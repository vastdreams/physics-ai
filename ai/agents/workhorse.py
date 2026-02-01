"""
PATH: ai/agents/workhorse.py
PURPOSE: Layer B Workhorse Agent (Qwen 2.5 7B)

ROLE:
- Data mapping and transformation
- Tool calling for deterministic pipelines
- Schema generation
- Analysis plan creation
- Code generation for calculations

WHY: Best value for moderate complexity tasks. Handles ~30% of
     requests that need more capability than gatekeeper.
"""

import json
from typing import Any, Callable, Dict, List, Optional

from ai.llm.config import ModelTier
from ai.llm.provider import Message, Tool
from .base import BaseAgent, AgentResponse, AgentStatus, Artefact, PROVENANCE_PROMPT


class WorkhorseAgent(BaseAgent):
    """
    Layer B: Workhorse Agent
    
    Uses Qwen 2.5 7B for:
    - Data extraction and mapping
    - Tool calling
    - Schema generation
    - Analysis planning
    - Code generation
    """
    
    def __init__(self, manager=None):
        super().__init__(manager)
        self._tools: Dict[str, Callable] = {}
    
    @property
    def name(self) -> str:
        return "Workhorse"
    
    @property
    def tier(self) -> ModelTier:
        return ModelTier.WORKHORSE
    
    @property
    def system_prompt(self) -> str:
        return """You are a capable workhorse agent for a physics AI system.

Your responsibilities:
1. EXTRACT structured data from unstructured content
2. MAP data between schemas and formats
3. CALL tools for deterministic computations
4. GENERATE schemas and analysis plans
5. WRITE code for physics calculations

Key principles:
- When you need a calculation, call the appropriate tool
- Never make up numeric values - use tools and cite artefacts
- If a task requires multi-step orchestration, escalate
- Produce structured, machine-readable outputs when appropriate

""" + PROVENANCE_PROMPT
    
    def register_tool(self, name: str, func: Callable, description: str, parameters: Dict):
        """Register a tool for the agent to use."""
        self._tools[name] = {
            "func": func,
            "tool": Tool(name=name, description=description, parameters=parameters)
        }
    
    async def process(self, input_data: Dict[str, Any]) -> AgentResponse:
        """
        Process a workhorse request.
        
        Input data should have:
        - action: extract, map, analyze, generate_code, tool_call
        - content: The content to process
        - options: Action-specific options
        """
        action = input_data.get("action", "analyze")
        content = input_data.get("content", "")
        options = input_data.get("options", {})
        
        handlers = {
            "extract": self._extract,
            "map": self._map_data,
            "analyze": self._analyze,
            "generate_code": self._generate_code,
            "generate_schema": self._generate_schema,
            "tool_call": self._tool_call,
            "summarize": self._summarize,
        }
        
        handler = handlers.get(action, self._analyze)
        return await handler(content, options)
    
    async def _extract(
        self,
        content: str,
        options: Dict[str, Any]
    ) -> AgentResponse:
        """Extract structured data from content."""
        target_schema = options.get("schema", {})
        context = options.get("context", "")
        
        prompt = f"""Extract structured data from the following content.

Content:
{content}

"""
        if target_schema:
            prompt += f"Target schema:\n{json.dumps(target_schema, indent=2)}\n\n"
        if context:
            prompt += f"Additional context: {context}\n\n"
        
        prompt += """Respond with JSON matching the schema.
For numeric values that require calculation, use null and note "requires_calculation": true
If extraction requires complex reasoning across multiple sources, set "escalate": true"""

        response = await self._generate(prompt, json_mode=True)
        result = response.parse_json()
        should_escalate = result.get("escalate", False) if result else False
        
        # Create artefact for extracted data
        if result and not should_escalate:
            artefact = Artefact.create("extraction", result, source="content")
            self.register_artefact(artefact)
            return self._build_response(
                response,
                artefacts=[artefact],
                should_escalate=should_escalate
            )
        
        return self._build_response(response, should_escalate=should_escalate)
    
    async def _map_data(
        self,
        content: str,
        options: Dict[str, Any]
    ) -> AgentResponse:
        """Map data from one schema to another."""
        source_schema = options.get("source_schema", {})
        target_schema = options.get("target_schema", {})
        
        prompt = f"""Map the following data to the target schema.

Source data:
{content}

Source schema: {json.dumps(source_schema, indent=2) if source_schema else "infer from data"}

Target schema:
{json.dumps(target_schema, indent=2)}

Respond with:
1. The mapped data in JSON format
2. A mapping explanation showing source -> target field mappings
3. Any fields that couldn't be mapped"""

        response = await self._generate(prompt)
        
        return self._build_response(response)
    
    async def _analyze(
        self,
        content: str,
        options: Dict[str, Any]
    ) -> AgentResponse:
        """Analyze content and produce structured analysis."""
        analysis_type = options.get("type", "general")
        focus = options.get("focus", [])
        artefact_ids = options.get("artefact_ids", [])
        
        prompt = f"""Perform a {analysis_type} analysis of the following.

Content:
{content}

"""
        if focus:
            prompt += f"Focus areas: {', '.join(focus)}\n\n"
        
        prompt += """Structure your analysis as:
1. Summary (2-3 sentences)
2. Key findings (bullet points)
3. Detailed analysis
4. Recommendations or next steps

When referencing any data or numbers, cite the artefact ID.
If the analysis requires complex multi-step reasoning, set escalate=true at the end."""

        response = await self._generate(prompt, artefact_ids=artefact_ids)
        
        # Check for escalation markers
        should_escalate = "escalate=true" in response.content.lower()
        
        return self._build_response(
            response,
            should_escalate=should_escalate,
            escalation_reason="Complex analysis requires orchestrator" if should_escalate else None
        )
    
    async def _generate_code(
        self,
        content: str,
        options: Dict[str, Any]
    ) -> AgentResponse:
        """Generate code for physics calculations."""
        language = options.get("language", "python")
        purpose = options.get("purpose", "calculation")
        constraints = options.get("constraints", [])
        
        prompt = f"""Generate {language} code for the following physics task.

Task: {content}

Purpose: {purpose}

"""
        if constraints:
            prompt += f"Constraints:\n" + "\n".join(f"- {c}" for c in constraints)
        
        prompt += """

Requirements:
1. Code must be self-contained and runnable
2. Include docstrings and comments
3. Handle edge cases
4. Return structured results (dict/dataclass)
5. All numeric outputs must be captured as artefacts

Respond with:
```python
# code here
```

Followed by explanation of the approach."""

        response = await self._generate(prompt)
        
        # Extract code block
        code = ""
        if "```python" in response.content:
            start = response.content.index("```python") + 9
            end = response.content.index("```", start)
            code = response.content[start:end].strip()
        
        if code:
            artefact = Artefact.create("code", code, language=language, purpose=purpose)
            self.register_artefact(artefact)
            return self._build_response(response, artefacts=[artefact])
        
        return self._build_response(response)
    
    async def _generate_schema(
        self,
        content: str,
        options: Dict[str, Any]
    ) -> AgentResponse:
        """Generate a schema from content or description."""
        format_type = options.get("format", "json_schema")
        
        prompt = f"""Generate a {format_type} schema for the following.

Description/Example:
{content}

Requirements:
1. Include all relevant fields
2. Add descriptions for each field
3. Specify types and constraints
4. Mark required vs optional fields

Respond with the schema in {format_type} format."""

        response = await self._generate(prompt, json_mode=True)
        result = response.parse_json()
        
        if result:
            artefact = Artefact.create("schema", result, format=format_type)
            self.register_artefact(artefact)
            return self._build_response(response, artefacts=[artefact])
        
        return self._build_response(response)
    
    async def _tool_call(
        self,
        content: str,
        options: Dict[str, Any]
    ) -> AgentResponse:
        """Call a registered tool."""
        tool_name = options.get("tool")
        tool_args = options.get("args", {})
        
        if tool_name not in self._tools:
            return AgentResponse(
                status=AgentStatus.ERROR,
                content=f"Unknown tool: {tool_name}",
                agent_name=self.name,
                tier=self.tier
            )
        
        tool_info = self._tools[tool_name]
        
        try:
            # Execute tool
            result = tool_info["func"](**tool_args)
            
            # Create artefact for result
            artefact = Artefact.create(
                "tool_result",
                result,
                tool=tool_name,
                args=tool_args
            )
            self.register_artefact(artefact)
            
            return AgentResponse(
                status=AgentStatus.SUCCESS,
                content=f"Tool {tool_name} executed successfully. Result: [{artefact.id}]",
                artefacts=[artefact],
                artefact_references=[artefact.id],
                agent_name=self.name,
                tier=self.tier
            )
            
        except Exception as e:
            return AgentResponse(
                status=AgentStatus.ERROR,
                content=f"Tool execution failed: {str(e)}",
                agent_name=self.name,
                tier=self.tier
            )
    
    async def _summarize(
        self,
        content: str,
        options: Dict[str, Any]
    ) -> AgentResponse:
        """Summarize content."""
        max_length = options.get("max_length", 500)
        style = options.get("style", "technical")
        
        prompt = f"""Summarize the following content in a {style} style.

Content:
{content}

Requirements:
- Maximum {max_length} characters
- Preserve key technical details
- Cite any specific numbers or data with artefact IDs"""

        response = await self._generate(prompt)
        return self._build_response(response)
    
    # Physics-specific methods
    
    async def solve_equation(
        self,
        equation: str,
        solve_for: str,
        known_values: Dict[str, float] = None
    ) -> AgentResponse:
        """Solve a physics equation."""
        return await self.process({
            "action": "generate_code",
            "content": f"Solve the equation: {equation} for {solve_for}",
            "options": {
                "language": "python",
                "purpose": "equation_solve",
                "constraints": [
                    f"Known values: {known_values or {}}",
                    "Use sympy for symbolic manipulation",
                    "Return both symbolic and numeric solutions"
                ]
            }
        })
    
    async def create_simulation_plan(
        self,
        description: str,
        parameters: Dict[str, Any] = None
    ) -> AgentResponse:
        """Create a plan for a physics simulation."""
        return await self.process({
            "action": "analyze",
            "content": f"""Create a detailed simulation plan for:

{description}

Parameters: {json.dumps(parameters or {}, indent=2)}""",
            "options": {
                "type": "simulation_planning",
                "focus": [
                    "physical model",
                    "numerical method",
                    "parameters and constraints",
                    "expected outputs",
                    "validation approach"
                ]
            }
        })
