"""
PATH: api/v1/agents.py
PURPOSE: REST API endpoints for the DREAM-style agent system

ENDPOINTS:
- POST /agents/chat          - Chat with physics AI (auto-routes to appropriate agent)
- POST /agents/classify      - Classify a query (Layer A)
- POST /agents/extract       - Extract data (Layer B)
- POST /agents/analyze       - Analyze content (Layer B)
- POST /agents/orchestrate   - Complex orchestration (Layer C)
- GET  /agents/status        - Get agent system status
- GET  /agents/stats         - Get usage statistics
- POST /agents/setup         - Setup/pull local models
"""

from flask import Blueprint, jsonify, request
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ai.llm.config import ModelTier, get_config
from ai.llm.provider import Message
from ai.llm.manager import LLMManager
from ai.llm.local_provider import OllamaProvider, setup_dream_models
from ai.agents.gatekeeper import GatekeeperAgent
from ai.agents.workhorse import WorkhorseAgent
from ai.agents.orchestrator import OrchestratorAgent
from ai.rubric.quality_gate import QualityGate, GateVerdict, get_quality_gate

agents_bp = Blueprint('agents', __name__, url_prefix='/agents')

# Global instances (initialized lazily)
_manager = None
_gatekeeper = None
_workhorse = None
_orchestrator = None


def get_manager():
    global _manager
    if _manager is None:
        _manager = LLMManager()
    return _manager


def get_gatekeeper():
    global _gatekeeper
    if _gatekeeper is None:
        _gatekeeper = GatekeeperAgent(get_manager())
    return _gatekeeper


def get_workhorse():
    global _workhorse
    if _workhorse is None:
        _workhorse = WorkhorseAgent(get_manager())
    return _workhorse


def get_orchestrator():
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = OrchestratorAgent(get_manager())
    return _orchestrator


def run_async(coro):
    """Run an async function from sync context."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)


@agents_bp.route('/status', methods=['GET'])
def get_status():
    """Get agent system status."""
    manager = get_manager()
    config = get_config()
    
    # Check providers
    ollama_status = run_async(manager.local_provider.health_check())
    deepseek_available = manager.api_provider.is_available
    
    return jsonify({
        'success': True,
        'status': {
            'providers': {
                'ollama': {
                    'available': ollama_status,
                    'host': config.ollama_host,
                    'models': run_async(manager.local_provider.list_models()) if ollama_status else []
                },
                'deepseek': {
                    'available': deepseek_available,
                    'is_fallback': True
                }
            },
            'agents': {
                'gatekeeper': {
                    'name': 'Phi 3.5 Mini',
                    'tier': 'A',
                    'model': config.models[ModelTier.GATEKEEPER].ollama_model
                },
                'workhorse': {
                    'name': 'Qwen 2.5 7B',
                    'tier': 'B',
                    'model': config.models[ModelTier.WORKHORSE].ollama_model
                },
                'orchestrator': {
                    'name': 'Ministral 8B',
                    'tier': 'C',
                    'model': config.models[ModelTier.ORCHESTRATOR].ollama_model
                }
            },
            'config': {
                'prefer_local': config.prefer_local,
                'fallback_to_api': config.fallback_to_api,
                'auto_escalate': config.auto_escalate
            }
        }
    })


@agents_bp.route('/stats', methods=['GET'])
def get_stats():
    """Get usage statistics."""
    manager = get_manager()
    return jsonify({
        'success': True,
        'stats': manager.get_stats()
    })


@agents_bp.route('/setup', methods=['POST'])
def setup_models():
    """Setup/pull local models for DREAM stack."""
    manager = get_manager()
    
    # Check if Ollama is running
    ollama_healthy = run_async(manager.local_provider.health_check())
    if not ollama_healthy:
        return jsonify({
            'success': False,
            'error': 'Ollama is not running. Please start Ollama first.'
        }), 503
    
    # Pull models
    results = run_async(setup_dream_models(manager.local_provider))
    
    return jsonify({
        'success': True,
        'models': results,
        'message': 'Model setup initiated. Large models may take time to download.'
    })


import re as _re

# ── Physics-aware system prompt ──────────────────────────────────────────
_SYSTEM_PROMPT = """You are Beyond Frontier, a computational physics AI engine.

CRITICAL RULES FOR CODE GENERATION:
1. When asked to simulate, compute, or visualize anything, you MUST produce
   executable Python code that runs in the browser via Pyodide.
2. For visualizations and simulations, use ONLY matplotlib (with inline
   backend). NEVER use pygame, tkinter, turtle, or any GUI framework.
3. Always call plt.show() at the end of plots — the system captures them
   automatically.
4. Use numpy for numerical computation. sympy is available for symbolic math.
5. For animations / time-evolving simulations, produce a multi-frame figure
   or a series of plots — do NOT use FuncAnimation or real-time loops.
6. Wrap simulation code in a single ```python code fence.
7. Always include print() statements to show key results numerically
   alongside any plots.
8. Available packages: numpy, sympy, matplotlib, scipy (on demand).

RESPONSE FORMAT:
- Start with a brief explanation of the physics.
- Then provide the complete executable code block.
- After the code block, summarize what the user will see when it runs.

Example for "simulate gravity":
```python
import numpy as np
import matplotlib.pyplot as plt

# N-body gravitational simulation
G = 6.674e-11
...
plt.show()
```
"""


def _extract_code_blocks(text: str):
    """Extract fenced code blocks from markdown text.

    Returns a list of dicts: [{"language": "python", "code": "..."}]
    """
    pattern = _re.compile(r"```(\w*)\s*\n(.*?)```", _re.DOTALL)
    blocks = []
    for m in pattern.finditer(text):
        lang = m.group(1).lower() or "python"
        code = m.group(2).strip()
        if code:
            blocks.append({"language": lang, "code": code})
    return blocks


def _detect_simulation(message: str) -> bool:
    """Return True if the user message looks like a simulation / visualization request."""
    keywords = [
        "simulat", "visuali", "plot", "graph", "animat", "render",
        "show me", "draw", "chart", "demonstrate", "run",
    ]
    lower = message.lower()
    return any(kw in lower for kw in keywords)


@agents_bp.route('/chat', methods=['POST'])
def chat():
    """
    Chat with physics AI - auto-routes to appropriate agent.
    
    Body:
    - message: User message (required)
    - context: Additional context (optional)
    - force_tier: Force specific tier (optional: gatekeeper, workhorse, orchestrator)
    """
    data = request.get_json() or {}
    message = data.get('message', '')
    context = data.get('context', '')
    force_tier = data.get('force_tier')
    
    if not message:
        return jsonify({
            'success': False,
            'error': 'Message is required'
        }), 400
    
    manager = get_manager()
    
    # Build messages — always include the physics system prompt
    messages = [Message.system(_SYSTEM_PROMPT)]
    if context:
        messages.append(Message.system(f"Conversation context:\n{context}"))

    # For simulation requests, add an extra nudge
    if _detect_simulation(message):
        messages.append(Message.system(
            "The user is requesting a simulation or visualization. "
            "You MUST include a complete, runnable ```python code block "
            "using matplotlib for visualization. Do NOT use pygame."
        ))

    messages.append(Message.user(message))
    
    # Determine tier
    tier = None
    if force_tier:
        tier_map = {
            'gatekeeper': ModelTier.GATEKEEPER,
            'workhorse': ModelTier.WORKHORSE,
            'orchestrator': ModelTier.ORCHESTRATOR,
            'a': ModelTier.GATEKEEPER,
            'b': ModelTier.WORKHORSE,
            'c': ModelTier.ORCHESTRATOR,
        }
        tier = tier_map.get(force_tier.lower())
    
    # Generate response
    response = run_async(manager.generate(
        messages=messages,
        force_tier=tier,
        auto_escalate=not force_tier  # Don't auto-escalate if tier is forced
    ))
    
    # Extract code blocks from the response content
    code_blocks = _extract_code_blocks(response.content or "")
    # Primary code = first python block, if any
    primary_code = None
    code_language = "python"
    for block in code_blocks:
        if block["language"] in ("python", "sympy", "py"):
            primary_code = block["code"]
            code_language = block["language"]
            break
    if not primary_code and code_blocks:
        primary_code = code_blocks[0]["code"]
        code_language = code_blocks[0]["language"]

    # Run through Quality Gate (rubric-based evaluation)
    quality_report = None
    try:
        gate = get_quality_gate()
        gate_decision = gate.evaluate(
            content=response.content or "",
            query=message,
            domain="general",
        )
        quality_report = gate_decision.to_dict()
    except Exception as e:
        # Quality gate failure should not block the response
        quality_report = {"error": str(e), "verdict": "skip"}
    
    return jsonify({
        'success': not response.is_error,
        'response': {
            'content': response.content,
            'model': response.model,
            'provider': response.provider,
            'is_fallback': response.is_fallback,
            'latency_ms': response.latency_ms,
            'usage': {
                'prompt_tokens': response.usage.prompt_tokens,
                'completion_tokens': response.usage.completion_tokens,
                'total_tokens': response.usage.total_tokens
            }
        },
        'code': primary_code,
        'code_language': code_language,
        'code_blocks': code_blocks,
        'auto_execute': primary_code is not None and _detect_simulation(message),
        'quality': quality_report,
        'error': response.error
    })


@agents_bp.route('/classify', methods=['POST'])
def classify():
    """
    Classify a query using Gatekeeper (Layer A).
    
    Body:
    - content: Content to classify (required)
    - categories: List of categories (optional)
    """
    data = request.get_json() or {}
    content = data.get('content', '')
    categories = data.get('categories')
    
    if not content:
        return jsonify({
            'success': False,
            'error': 'Content is required'
        }), 400
    
    gatekeeper = get_gatekeeper()
    
    response = run_async(gatekeeper.process({
        'action': 'classify',
        'content': content,
        'options': {'categories': categories} if categories else {}
    }))
    
    return jsonify({
        'success': response.status.value in ['success', 'escalated'],
        'result': response.to_dict()
    })


@agents_bp.route('/validate', methods=['POST'])
def validate():
    """
    Validate data using Gatekeeper (Layer A).
    
    Body:
    - content: Content to validate (required)
    - schema: Schema to validate against (optional)
    - rules: Validation rules (optional)
    """
    data = request.get_json() or {}
    content = data.get('content', '')
    schema = data.get('schema', {})
    rules = data.get('rules', [])
    
    if not content:
        return jsonify({
            'success': False,
            'error': 'Content is required'
        }), 400
    
    gatekeeper = get_gatekeeper()
    
    response = run_async(gatekeeper.process({
        'action': 'validate',
        'content': content,
        'options': {'schema': schema, 'rules': rules}
    }))
    
    return jsonify({
        'success': response.status.value in ['success', 'escalated'],
        'result': response.to_dict()
    })


@agents_bp.route('/extract', methods=['POST'])
def extract():
    """
    Extract structured data using Workhorse (Layer B).
    
    Body:
    - content: Content to extract from (required)
    - schema: Target schema (optional)
    """
    data = request.get_json() or {}
    content = data.get('content', '')
    schema = data.get('schema', {})
    
    if not content:
        return jsonify({
            'success': False,
            'error': 'Content is required'
        }), 400
    
    workhorse = get_workhorse()
    
    response = run_async(workhorse.process({
        'action': 'extract',
        'content': content,
        'options': {'schema': schema}
    }))
    
    return jsonify({
        'success': response.status.value in ['success', 'escalated'],
        'result': response.to_dict()
    })


@agents_bp.route('/analyze', methods=['POST'])
def analyze():
    """
    Analyze content using Workhorse (Layer B).
    
    Body:
    - content: Content to analyze (required)
    - type: Analysis type (optional)
    - focus: Focus areas (optional)
    """
    data = request.get_json() or {}
    content = data.get('content', '')
    analysis_type = data.get('type', 'general')
    focus = data.get('focus', [])
    
    if not content:
        return jsonify({
            'success': False,
            'error': 'Content is required'
        }), 400
    
    workhorse = get_workhorse()
    
    response = run_async(workhorse.process({
        'action': 'analyze',
        'content': content,
        'options': {'type': analysis_type, 'focus': focus}
    }))
    
    return jsonify({
        'success': response.status.value in ['success', 'escalated'],
        'result': response.to_dict()
    })


@agents_bp.route('/generate-code', methods=['POST'])
def generate_code():
    """
    Generate code using Workhorse (Layer B).
    
    Body:
    - task: Code generation task (required)
    - language: Programming language (default: python)
    - purpose: Purpose of the code (optional)
    """
    data = request.get_json() or {}
    task = data.get('task', '')
    language = data.get('language', 'python')
    purpose = data.get('purpose', 'calculation')
    
    if not task:
        return jsonify({
            'success': False,
            'error': 'Task is required'
        }), 400
    
    workhorse = get_workhorse()
    
    response = run_async(workhorse.process({
        'action': 'generate_code',
        'content': task,
        'options': {'language': language, 'purpose': purpose}
    }))
    
    return jsonify({
        'success': response.status.value in ['success', 'escalated'],
        'result': response.to_dict()
    })


@agents_bp.route('/orchestrate', methods=['POST'])
def orchestrate():
    """
    Complex orchestration using Orchestrator (Layer C).
    
    Body:
    - task: Complex task to orchestrate (required)
    - context: Additional context (optional)
    """
    data = request.get_json() or {}
    task = data.get('task', '')
    context = data.get('context', '')
    
    if not task:
        return jsonify({
            'success': False,
            'error': 'Task is required'
        }), 400
    
    orchestrator = get_orchestrator()
    
    response = run_async(orchestrator.process({
        'action': 'orchestrate',
        'content': task,
        'options': {'context': context}
    }))
    
    return jsonify({
        'success': response.status.value in ['success', 'escalated'],
        'result': response.to_dict()
    })


@agents_bp.route('/reason', methods=['POST'])
def reason():
    """
    Deep reasoning using Orchestrator (Layer C).
    
    Body:
    - question: Question to reason about (required)
    - type: Reasoning type (deductive, inductive, abductive)
    """
    data = request.get_json() or {}
    question = data.get('question', '')
    reasoning_type = data.get('type', 'deductive')
    
    if not question:
        return jsonify({
            'success': False,
            'error': 'Question is required'
        }), 400
    
    orchestrator = get_orchestrator()
    
    response = run_async(orchestrator.process({
        'action': 'reason',
        'content': question,
        'options': {'type': reasoning_type}
    }))
    
    return jsonify({
        'success': response.status.value in ['success', 'escalated'],
        'result': response.to_dict()
    })


@agents_bp.route('/quality/evaluate', methods=['POST'])
def evaluate_quality():
    """
    Evaluate content quality using the Rubric Quality Gate system.
    
    Body:
    - content: Content to evaluate (required)
    - query: Original query that prompted this content (optional)
    - code: Any code in the response (optional)
    - domain: Physics domain (optional, default: general)
    """
    data = request.get_json() or {}
    content = data.get('content', '')
    query = data.get('query', '')
    code = data.get('code')
    domain = data.get('domain', 'general')
    
    if not content:
        return jsonify({
            'success': False,
            'error': 'Content is required'
        }), 400
    
    try:
        gate = get_quality_gate()
        decision = gate.evaluate(
            content=content,
            query=query,
            code=code,
            domain=domain,
        )
        
        return jsonify({
            'success': True,
            'quality': decision.to_dict()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@agents_bp.route('/quality/stats', methods=['GET'])
def quality_stats():
    """Get quality gate statistics."""
    try:
        gate = get_quality_gate()
        return jsonify({
            'success': True,
            'stats': gate.get_stats()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@agents_bp.route('/derive', methods=['POST'])
def derive():
    """
    Derive from first principles using Orchestrator (Layer C).
    
    Body:
    - target: What to derive (required)
    - starting_point: Where to start (optional)
    """
    data = request.get_json() or {}
    target = data.get('target', '')
    starting_point = data.get('starting_point', 'fundamental laws')
    
    if not target:
        return jsonify({
            'success': False,
            'error': 'Target is required'
        }), 400
    
    orchestrator = get_orchestrator()
    
    response = run_async(orchestrator.process({
        'action': 'derive',
        'content': target,
        'options': {'starting_point': starting_point}
    }))
    
    return jsonify({
        'success': response.status.value in ['success', 'escalated'],
        'result': response.to_dict()
    })
