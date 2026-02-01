"""
PATH: ai/agents/gatekeeper.py
PURPOSE: Layer A Gatekeeper Agent (Phi 3.5 Mini)

ROLE:
- Input classification and routing
- Quick validation and sanity checks
- Schema enforcement
- PII detection
- Deciding when to escalate

WHY: Cheapest model, handles ~60% of requests that don't need
     full reasoning capability.
"""

import json
from typing import Any, Dict, List, Optional
import re

from ai.llm.config import ModelTier
from ai.llm.provider import Message
from .base import BaseAgent, AgentResponse, AgentStatus, Artefact, PROVENANCE_PROMPT


class GatekeeperAgent(BaseAgent):
    """
    Layer A: Gatekeeper Agent
    
    Uses Phi 3.5 Mini (3.8B) for:
    - Input classification
    - Routing decisions
    - Quick validations
    - Schema checks
    - Simple extractions
    """
    
    @property
    def name(self) -> str:
        return "Gatekeeper"
    
    @property
    def tier(self) -> ModelTier:
        return ModelTier.GATEKEEPER
    
    @property
    def system_prompt(self) -> str:
        return """You are a fast, efficient gatekeeper agent for a physics AI system.

Your responsibilities:
1. CLASSIFY inputs into categories
2. VALIDATE data against schemas
3. ROUTE requests to appropriate handlers
4. DETECT issues (PII, malformed data, etc.)
5. QUICK CHECKS for simple queries

Response guidelines:
- Be concise and direct
- Use structured formats (JSON) when appropriate
- Flag anything suspicious or complex for escalation
- Never attempt complex reasoning - escalate instead

""" + PROVENANCE_PROMPT
    
    async def process(self, input_data: Dict[str, Any]) -> AgentResponse:
        """
        Process a gatekeeper request.
        
        Input data should have:
        - action: classify, validate, route, check, extract
        - content: The content to process
        - options: Action-specific options
        """
        action = input_data.get("action", "classify")
        content = input_data.get("content", "")
        options = input_data.get("options", {})
        
        handlers = {
            "classify": self._classify,
            "validate": self._validate,
            "route": self._route,
            "check": self._check,
            "extract": self._simple_extract,
        }
        
        handler = handlers.get(action, self._classify)
        return await handler(content, options)
    
    async def _classify(
        self,
        content: str,
        options: Dict[str, Any]
    ) -> AgentResponse:
        """Classify content into categories."""
        categories = options.get("categories", [
            "question", "calculation", "simulation", "lookup", "explanation", "other"
        ])
        
        prompt = f"""Classify this input into exactly ONE category.

Categories: {', '.join(categories)}

Input: {content}

Respond with JSON: {{"category": "...", "confidence": 0.0-1.0, "escalate": true/false}}

Rules:
- escalate=true if the task is complex or ambiguous
- confidence should reflect certainty"""

        response = await self._generate(prompt, json_mode=True)
        
        # Parse response
        result = response.parse_json()
        should_escalate = result.get("escalate", False) if result else False
        
        return self._build_response(
            response,
            should_escalate=should_escalate,
            escalation_reason="Complex classification" if should_escalate else None
        )
    
    async def _validate(
        self,
        content: str,
        options: Dict[str, Any]
    ) -> AgentResponse:
        """Validate content against schema or rules."""
        schema = options.get("schema", {})
        rules = options.get("rules", [])
        
        prompt = f"""Validate this content.

Content: {content}

"""
        if schema:
            prompt += f"Schema: {json.dumps(schema)}\n"
        if rules:
            prompt += f"Rules: {json.dumps(rules)}\n"
        
        prompt += """
Respond with JSON:
{
  "valid": true/false,
  "errors": ["list of errors"],
  "warnings": ["list of warnings"],
  "escalate": true/false
}"""

        response = await self._generate(prompt, json_mode=True)
        result = response.parse_json()
        should_escalate = result.get("escalate", False) if result else False
        
        return self._build_response(
            response,
            should_escalate=should_escalate,
            escalation_reason="Validation requires deeper analysis" if should_escalate else None
        )
    
    async def _route(
        self,
        content: str,
        options: Dict[str, Any]
    ) -> AgentResponse:
        """Route request to appropriate handler."""
        routes = options.get("routes", {
            "workhorse": "Data extraction, calculations, tool calling",
            "orchestrator": "Complex reasoning, multi-step tasks, synthesis",
            "direct": "Simple lookups, yes/no questions",
        })
        
        prompt = f"""Determine the best route for this request.

Request: {content}

Available routes:
{json.dumps(routes, indent=2)}

Respond with JSON:
{{
  "route": "route_name",
  "confidence": 0.0-1.0,
  "reason": "brief explanation"
}}"""

        response = await self._generate(prompt, json_mode=True)
        result = response.parse_json()
        
        # Escalate if routed to orchestrator
        should_escalate = result.get("route") == "orchestrator" if result else False
        
        return self._build_response(
            response,
            should_escalate=should_escalate,
            escalation_reason="Complex task requires orchestrator" if should_escalate else None
        )
    
    async def _check(
        self,
        content: str,
        options: Dict[str, Any]
    ) -> AgentResponse:
        """Quick sanity check on content."""
        check_type = options.get("type", "general")
        
        prompts = {
            "general": f"Check this for any issues or concerns:\n{content}",
            "pii": f"Check for PII (names, emails, addresses, etc):\n{content}",
            "physics": f"Check if this is a valid physics question/statement:\n{content}",
            "code": f"Check this code for obvious issues:\n{content}",
        }
        
        prompt = prompts.get(check_type, prompts["general"])
        prompt += """

Respond with JSON:
{
  "passed": true/false,
  "issues": ["list of issues found"],
  "suggestions": ["list of suggestions"],
  "escalate": true/false
}"""

        response = await self._generate(prompt, json_mode=True)
        result = response.parse_json()
        should_escalate = result.get("escalate", False) if result else False
        
        return self._build_response(
            response,
            should_escalate=should_escalate
        )
    
    async def _simple_extract(
        self,
        content: str,
        options: Dict[str, Any]
    ) -> AgentResponse:
        """Simple data extraction."""
        fields = options.get("fields", ["key_info"])
        
        prompt = f"""Extract the following fields from the content.

Fields to extract: {', '.join(fields)}

Content: {content}

Respond with JSON containing the extracted fields.
If a field cannot be extracted, use null.
If extraction requires complex reasoning, set "escalate": true"""

        response = await self._generate(prompt, json_mode=True)
        result = response.parse_json()
        should_escalate = result.get("escalate", False) if result else False
        
        return self._build_response(
            response,
            should_escalate=should_escalate,
            escalation_reason="Extraction requires complex reasoning" if should_escalate else None
        )
    
    # Convenience methods
    
    async def classify_physics_query(self, query: str) -> Dict[str, Any]:
        """Classify a physics query."""
        response = await self.process({
            "action": "classify",
            "content": query,
            "options": {
                "categories": [
                    "equation_solve",      # Solve an equation
                    "simulation",          # Run a simulation
                    "lookup",              # Look up constant/equation
                    "derivation",          # Derive something
                    "explanation",         # Explain a concept
                    "calculation",         # Numerical calculation
                    "comparison",          # Compare theories/models
                    "validation",          # Validate a claim
                    "other"
                ]
            }
        })
        
        return response.llm_response.parse_json() if response.llm_response else {}
    
    async def check_numeric_provenance(self, text: str) -> Dict[str, Any]:
        """Check if numeric claims have proper provenance."""
        # Find all numbers in text
        numbers = re.findall(r'\b\d+\.?\d*(?:e[+-]?\d+)?\b', text)
        refs = re.findall(r'\[art_[a-f0-9]{8}\]', text)
        
        if not numbers:
            return {"valid": True, "reason": "No numeric claims found"}
        
        if not refs:
            return {
                "valid": False,
                "reason": f"Found {len(numbers)} numbers but no artefact references",
                "numbers": numbers
            }
        
        return {
            "valid": True,
            "numbers_found": len(numbers),
            "references_found": len(refs)
        }
