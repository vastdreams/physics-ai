"""
PATH: ai/agents/orchestrator.py
PURPOSE: Layer C Orchestrator Agent (Ministral/Mistral 8B)

ROLE:
- End-to-end task orchestration
- Multi-step planning and execution
- Narrative synthesis with provenance
- Cross-checking outputs against computed results
- Complex reasoning and theory work

WHY: Most capable local model, handles complex ~10% of requests
     that require deep reasoning and orchestration.
"""

import json
from typing import Any, Dict, List, Optional
from datetime import datetime

from ai.llm.config import ModelTier
from ai.llm.provider import Message, Tool
from .base import BaseAgent, AgentResponse, AgentStatus, Artefact, PROVENANCE_PROMPT


class OrchestratorAgent(BaseAgent):
    """
    Layer C: Orchestrator Agent
    
    Uses Ministral/Mistral 8B for:
    - Complex multi-step orchestration
    - Narrative generation with provenance
    - Theory derivation and synthesis
    - Cross-validation of results
    - Research-grade outputs
    """
    
    @property
    def name(self) -> str:
        return "Orchestrator"
    
    @property
    def tier(self) -> ModelTier:
        return ModelTier.ORCHESTRATOR
    
    @property
    def system_prompt(self) -> str:
        return """You are the orchestrator agent for a physics AI research system.

Your role is to handle complex, multi-step tasks that require:
1. Deep REASONING about physics concepts
2. PLANNING multi-step analysis or derivations
3. ORCHESTRATING calls to other tools and agents
4. SYNTHESIZING results into coherent narratives
5. CROSS-CHECKING outputs for consistency

Key principles:
- You are the "senior researcher" that coordinates the work
- Always maintain scientific rigor
- Never claim numeric results without citing artefact IDs
- Structure your reasoning explicitly (show your work)
- When writing narratives, use [art_XXXXXXXX] citations

Output format for research tasks:
1. UNDERSTANDING: What is being asked
2. APPROACH: How you will tackle it
3. EXECUTION: Step-by-step work
4. RESULTS: Findings with citations
5. DISCUSSION: Implications and limitations
6. NEXT STEPS: What could be done further

""" + PROVENANCE_PROMPT
    
    async def process(self, input_data: Dict[str, Any]) -> AgentResponse:
        """
        Process an orchestration request.
        
        Input data should have:
        - action: orchestrate, plan, reason, synthesize, cross_check
        - content: The content to process
        - options: Action-specific options
        """
        action = input_data.get("action", "orchestrate")
        content = input_data.get("content", "")
        options = input_data.get("options", {})
        
        handlers = {
            "orchestrate": self._orchestrate,
            "plan": self._plan,
            "reason": self._reason,
            "synthesize": self._synthesize,
            "cross_check": self._cross_check,
            "derive": self._derive,
            "narrative": self._write_narrative,
        }
        
        handler = handlers.get(action, self._orchestrate)
        return await handler(content, options)
    
    async def _orchestrate(
        self,
        content: str,
        options: Dict[str, Any]
    ) -> AgentResponse:
        """Orchestrate a complex multi-step task."""
        context = options.get("context", "")
        artefact_ids = options.get("artefact_ids", [])
        tools_available = options.get("tools", [])
        
        prompt = f"""Orchestrate the following complex task.

Task:
{content}

"""
        if context:
            prompt += f"Context:\n{context}\n\n"
        
        if tools_available:
            prompt += f"Available tools: {', '.join(tools_available)}\n\n"
        
        prompt += """Structure your orchestration as:

1. TASK DECOMPOSITION
   - Break down into subtasks
   - Identify dependencies

2. EXECUTION PLAN
   - Order of operations
   - Which tools/agents for each step

3. EXECUTION
   - For each step, show:
     * Input
     * Action taken
     * Output (with artefact citations)

4. INTEGRATION
   - Combine results
   - Verify consistency

5. FINAL OUTPUT
   - Complete answer/deliverable
   - Provenance summary"""

        response = await self._generate(prompt, artefact_ids=artefact_ids)
        return self._build_response(response)
    
    async def _plan(
        self,
        content: str,
        options: Dict[str, Any]
    ) -> AgentResponse:
        """Create a detailed execution plan."""
        constraints = options.get("constraints", [])
        resources = options.get("resources", [])
        
        prompt = f"""Create a detailed execution plan for:

{content}

"""
        if constraints:
            prompt += f"Constraints:\n" + "\n".join(f"- {c}" for c in constraints) + "\n\n"
        if resources:
            prompt += f"Available resources:\n" + "\n".join(f"- {r}" for r in resources) + "\n\n"
        
        prompt += """Create a plan with:

1. OBJECTIVE
   - Clear goal statement
   - Success criteria

2. PREREQUISITES
   - What must be in place before starting
   - Data or information needed

3. STEPS
   For each step:
   - Description
   - Expected inputs
   - Expected outputs
   - Potential issues and mitigations
   - Estimated complexity (simple/moderate/complex)

4. VERIFICATION
   - How to verify each step succeeded
   - Final validation approach

5. CONTINGENCIES
   - What if key steps fail
   - Alternative approaches"""

        response = await self._generate(prompt)
        return self._build_response(response)
    
    async def _reason(
        self,
        content: str,
        options: Dict[str, Any]
    ) -> AgentResponse:
        """Deep reasoning about a physics question."""
        artefact_ids = options.get("artefact_ids", [])
        reasoning_type = options.get("type", "deductive")
        
        prompt = f"""Engage in {reasoning_type} reasoning about:

{content}

Structure your reasoning:

1. PREMISES
   - State known facts and assumptions
   - Cite artefacts for any data

2. LOGICAL CHAIN
   - Step-by-step reasoning
   - Each step justified
   - Mark uncertain inferences

3. CONCLUSION
   - What follows from the reasoning
   - Confidence level
   - Limitations

4. ALTERNATIVE VIEWS
   - Other interpretations
   - Counter-arguments
   - Conditions where conclusion might not hold"""

        response = await self._generate(prompt, artefact_ids=artefact_ids)
        return self._build_response(response)
    
    async def _synthesize(
        self,
        content: str,
        options: Dict[str, Any]
    ) -> AgentResponse:
        """Synthesize multiple sources/results into unified output."""
        sources = options.get("sources", [])
        artefact_ids = options.get("artefact_ids", [])
        output_format = options.get("format", "narrative")
        
        prompt = f"""Synthesize the following into a coherent {output_format}.

Content to synthesize:
{content}

"""
        if sources:
            prompt += f"Sources:\n" + "\n".join(f"- {s}" for s in sources) + "\n\n"
        
        prompt += """Your synthesis should:

1. INTEGRATE key points from all sources
2. RESOLVE any conflicts or inconsistencies
3. HIGHLIGHT areas of agreement
4. NOTE gaps or uncertainties
5. CITE artefacts for all factual claims

Maintain a unified, coherent narrative while preserving nuance."""

        response = await self._generate(prompt, artefact_ids=artefact_ids)
        return self._build_response(response)
    
    async def _cross_check(
        self,
        content: str,
        options: Dict[str, Any]
    ) -> AgentResponse:
        """Cross-check outputs against computed results."""
        computed_results = options.get("computed_results", {})
        artefact_ids = options.get("artefact_ids", [])
        
        prompt = f"""Cross-check the following narrative against computed results.

NARRATIVE:
{content}

COMPUTED RESULTS:
{json.dumps(computed_results, indent=2)}

For each claim in the narrative:
1. Identify the claim
2. Find supporting computed result (cite artefact ID)
3. Verify match or flag discrepancy

Output format:
{{
  "claims_checked": [
    {{
      "claim": "...",
      "artefact_reference": "art_XXXXXXXX",
      "status": "verified|unverified|discrepancy",
      "details": "..."
    }}
  ],
  "overall_status": "pass|fail|partial",
  "issues_found": ["..."]
}}"""

        response = await self._generate(prompt, artefact_ids=artefact_ids, json_mode=True)
        
        result = response.parse_json()
        if result:
            artefact = Artefact.create("cross_check", result)
            self.register_artefact(artefact)
            return self._build_response(response, artefacts=[artefact])
        
        return self._build_response(response)
    
    async def _derive(
        self,
        content: str,
        options: Dict[str, Any]
    ) -> AgentResponse:
        """Derive a result from first principles."""
        starting_point = options.get("starting_point", "fundamental laws")
        target = options.get("target", "")
        
        prompt = f"""Derive the following from first principles.

DERIVATION TARGET:
{content}

Starting from: {starting_point}
"""
        if target:
            prompt += f"Target form: {target}\n"
        
        prompt += """

Structure your derivation:

1. STARTING POINT
   - State initial principles/equations
   - List assumptions made

2. DERIVATION STEPS
   For each step:
   - Mathematical operation
   - Physical justification
   - Intermediate result

3. FINAL RESULT
   - Derived expression/equation
   - Physical interpretation

4. VERIFICATION
   - Dimensional analysis
   - Limiting cases
   - Comparison with known results

5. APPLICABILITY
   - When this result holds
   - Limitations and caveats"""

        response = await self._generate(prompt)
        return self._build_response(response)
    
    async def _write_narrative(
        self,
        content: str,
        options: Dict[str, Any]
    ) -> AgentResponse:
        """Write a research-grade narrative with provenance."""
        artefact_ids = options.get("artefact_ids", [])
        section = options.get("section", "results")
        style = options.get("style", "academic")
        
        prompt = f"""Write a {style} {section} section based on:

{content}

Requirements:
1. Every numeric claim MUST cite its artefact: [art_XXXXXXXX]
2. Use precise scientific language
3. Maintain objectivity
4. Acknowledge limitations
5. Connect findings to broader context

Structure for {section}:
"""
        
        section_guides = {
            "results": """
- Present findings in logical order
- Lead with most important results
- Include statistical significance where relevant
- Use figures/tables references""",
            "discussion": """
- Interpret findings in context
- Compare with prior work
- Discuss implications
- Address limitations
- Suggest future directions""",
            "methods": """
- Describe approach clearly
- Justify methodological choices
- Enable reproducibility
- Note any modifications""",
            "introduction": """
- Establish context and importance
- Review relevant background
- State objectives clearly
- Preview structure"""
        }
        
        prompt += section_guides.get(section, section_guides["results"])
        
        response = await self._generate(prompt, artefact_ids=artefact_ids)
        return self._build_response(response)
    
    # High-level physics research methods
    
    async def investigate_phenomenon(
        self,
        phenomenon: str,
        known_data: Dict[str, Any] = None
    ) -> AgentResponse:
        """Investigate a physics phenomenon comprehensively."""
        return await self.process({
            "action": "orchestrate",
            "content": f"""Investigate: {phenomenon}

Conduct a comprehensive investigation including:
1. Current understanding
2. Relevant equations and theories
3. Key experiments and observations
4. Open questions
5. Potential new insights""",
            "options": {
                "context": json.dumps(known_data) if known_data else "",
            }
        })
    
    async def compare_theories(
        self,
        theories: List[str],
        context: str = ""
    ) -> AgentResponse:
        """Compare multiple physics theories."""
        return await self.process({
            "action": "synthesize",
            "content": f"""Compare these theories:
{chr(10).join(f'- {t}' for t in theories)}

Compare:
1. Core assumptions
2. Predictions
3. Experimental support
4. Limitations
5. Domains of applicability
6. Potential for unification""",
            "options": {
                "format": "comparative_analysis",
                "sources": theories
            }
        })
    
    async def propose_experiment(
        self,
        hypothesis: str,
        constraints: List[str] = None
    ) -> AgentResponse:
        """Propose an experiment to test a hypothesis."""
        return await self.process({
            "action": "plan",
            "content": f"""Design an experiment to test:

Hypothesis: {hypothesis}

The experiment should:
1. Directly test the hypothesis
2. Control for confounding variables
3. Produce measurable outcomes
4. Be feasible with current technology""",
            "options": {
                "constraints": constraints or []
            }
        })
