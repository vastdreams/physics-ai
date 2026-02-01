# PATH: substrate/interface/chatbot.py
# PURPOSE:
#   - ChatGPT-style interface to the Physics AI substrate
#   - Translates natural language to physics problems
#   - Returns structured derivations and explanations
#
# ROLE IN ARCHITECTURE:
#   - Top layer - user-facing interface
#   - Uses graph, planner, executor, critics, and evolution under the hood
#
# MAIN EXPORTS:
#   - ChatbotInterface
#   - ChatMessage
#   - ChatSession
#
# NON-RESPONSIBILITIES:
#   - Does NOT do HTTP (api/ handles that)
#   - Does NOT plan/evolve outside provided components
#
# NOTES FOR FUTURE AI:
#   - Executor is the math path (SymPy/SciPy), not the LLM
#   - Keep traces rich; evolution uses them

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import uuid

from substrate.graph.formula import Formula
from substrate.graph.formula_graph import FormulaGraph
from substrate.planner.formula_planner import FormulaPlanner, DerivationPlan
from substrate.memory.reasoning_trace import (
    ReasoningTrace,
    TraceStep,
    TraceStepType,
    TraceStore,
)
from substrate.critics.local_llm import LocalLLMBackend
from substrate.critics.logic_critic import LogicCritic
from substrate.execution.executor import FormulaExecutor


@dataclass
class ChatMessage:
    """A message in a chat conversation."""

    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    role: str = "user"  # "user", "assistant", "system"
    content: str = ""

    physics_problem: Optional[Dict[str, Any]] = None
    derivation_plan: Optional[Dict[str, Any]] = None
    result: Optional[Dict[str, Any]] = None
    trace_id: Optional[str] = None

    timestamp: datetime = field(default_factory=datetime.now)
    confidence: float = 1.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "role": self.role,
            "content": self.content,
            "physics_problem": self.physics_problem,
            "derivation_plan": self.derivation_plan,
            "result": self.result,
            "trace_id": self.trace_id,
            "timestamp": self.timestamp.isoformat(),
            "confidence": self.confidence,
        }


@dataclass
class ChatSession:
    """A chat session with history."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    messages: List[ChatMessage] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)

    created_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)

    def add_message(self, message: ChatMessage):
        self.messages.append(message)
        self.last_activity = datetime.now()

    def get_history(self, n: int = 10) -> List[Dict[str, Any]]:
        return [m.to_dict() for m in self.messages[-n:]]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "messages": [m.to_dict() for m in self.messages],
            "context": self.context,
            "created_at": self.created_at.isoformat(),
            "last_activity": self.last_activity.isoformat(),
        }


class ChatbotInterface:
    """
    ChatGPT-style interface to the Physics AI.
    """

    def __init__(
        self,
        formula_graph: FormulaGraph,
        llm_backend: LocalLLMBackend,
        trace_store: TraceStore,
        planner: Optional[FormulaPlanner] = None,
        logic_critic: Optional[LogicCritic] = None,
        executor: Optional[FormulaExecutor] = None,
    ):
        self.graph = formula_graph
        self.llm = llm_backend
        self.trace_store = trace_store
        self.planner = planner or FormulaPlanner(formula_graph)
        self.logic_critic = logic_critic or LogicCritic(llm_backend, formula_graph)
        self.executor = executor or FormulaExecutor()

        self._sessions: Dict[str, ChatSession] = {}

    # -------------------------------------------------------------------------
    # Session management
    # -------------------------------------------------------------------------
    def create_session(self, context: Optional[Dict[str, Any]] = None) -> ChatSession:
        session = ChatSession(context=context or {})
        self._sessions[session.id] = session
        return session

    def get_session(self, session_id: str) -> Optional[ChatSession]:
        return self._sessions.get(session_id)

    def delete_session(self, session_id: str):
        self._sessions.pop(session_id, None)

    # -------------------------------------------------------------------------
    # Chat entrypoint
    # -------------------------------------------------------------------------
    def chat(
        self,
        message: str,
        session_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> ChatMessage:
        session = self.get_session(session_id) if session_id else None
        if not session:
            session = self.create_session(context)

        full_context = {**session.context, **(context or {})}

        user_message = ChatMessage(role="user", content=message)
        session.add_message(user_message)

        trace = ReasoningTrace(
            problem_text=message,
            context=full_context,
        )
        trace.add_step(
            TraceStepType.PROBLEM_RECEIVED,
            f"Received: {message[:100]}...",
        )

        try:
            physics_problem = self._parse_problem(message, full_context, trace)

            if not physics_problem:
                response = self._general_response(message, session, trace)
            else:
                plan = self._plan_derivation(physics_problem, trace)
                if plan:
                    result = self._execute_plan(plan, physics_problem, trace)
                    explanation = self._generate_explanation(plan, result, trace)
                    self._run_audit(trace)

                    response = ChatMessage(
                        role="assistant",
                        content=explanation,
                        physics_problem=physics_problem,
                        derivation_plan=plan.to_dict() if plan else None,
                        result=result,
                        trace_id=trace.id,
                        confidence=trace.overall_confidence,
                    )
                else:
                    response = self._no_plan_response(physics_problem, trace)

            trace.complete(result=response.result, success=True)
        except Exception as e:  # pylint: disable=broad-except
            trace.add_step(
                TraceStepType.ERROR,
                f"Error: {str(e)}",
                success=False,
                error_message=str(e),
            )
            trace.complete(success=False)
            response = ChatMessage(
                role="assistant",
                content=f"I encountered an error processing your request: {str(e)}. Please try rephrasing or providing more details.",
                trace_id=trace.id,
                confidence=0.0,
            )

        self.trace_store.store(trace)
        session.add_message(response)
        return response

    # -------------------------------------------------------------------------
    # Problem parsing
    # -------------------------------------------------------------------------
    def _parse_problem(
        self,
        message: str,
        context: Dict[str, Any],
        trace: ReasoningTrace,
    ) -> Optional[Dict[str, Any]]:
        prompt = f"""Analyze this message and extract a physics problem if present.

Message: "{message}"

Context: {json.dumps(context)}

If this is a physics problem, extract:
1. What quantities are given (inputs)
2. What needs to be calculated (outputs)
3. What domain applies (classical, quantum, relativistic, etc.)
4. Any constraints or conditions

Respond with JSON:
{{
    "is_physics_problem": true/false,
    "inputs": {{"variable_name": value_or_symbol, ...}},
    "outputs": ["variable_name", ...],
    "domain": "classical|quantum|relativistic|statistical|general",
    "conditions": ["condition 1", ...],
    "description": "brief problem description"
}}

If not a physics problem, return {{"is_physics_problem": false}}"""

        response = self.llm.generate(
            prompt,
            system_prompt="You are a physics problem parser. Extract structured physics problems from natural language.",
        )

        try:
            text = response.text.strip()
            if "```" in text:
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]

            data = json.loads(text)
            if not data.get("is_physics_problem"):
                trace.add_step(
                    TraceStepType.PROBLEM_PARSED,
                    "Not a physics problem",
                    data=data,
                )
                return None

            trace.add_step(
                TraceStepType.PROBLEM_PARSED,
                f"Parsed physics problem: {data.get('description', '')}",
                data=data,
            )
            trace.problem = data
            trace.domain = data.get("domain", "general")
            return data
        except (json.JSONDecodeError, KeyError):
            trace.add_step(
                TraceStepType.PROBLEM_PARSED,
                "Failed to parse problem",
                success=False,
            )
            return None

    # -------------------------------------------------------------------------
    # Planning
    # -------------------------------------------------------------------------
    def _plan_derivation(
        self,
        problem: Dict[str, Any],
        trace: ReasoningTrace,
    ) -> Optional[DerivationPlan]:
        trace.add_step(
            TraceStepType.PLAN_STARTED,
            "Starting derivation planning",
        )

        inputs = problem.get("inputs", {})
        outputs = problem.get("outputs", [])
        context = {
            "domain": problem.get("domain", "general"),
            **{c.replace(" ", "_"): True for c in problem.get("conditions", [])},
        }

        plans = self.planner.plan(
            inputs=inputs,
            outputs=outputs,
            context=context,
            max_plans=3,
        )

        if not plans:
            trace.add_step(
                TraceStepType.PLAN_INVALID,
                "No derivation plan found",
                success=False,
            )
            return None

        best_plan = plans[0]
        for step in best_plan.steps:
            trace.add_step(
                TraceStepType.FORMULA_SELECTED,
                f"Selected formula: {step.formula_name}",
                formula_id=step.formula_id,
                formula_name=step.formula_name,
            )

        trace.add_step(
            TraceStepType.PLAN_GENERATED,
            f"Generated plan with {len(best_plan.steps)} steps",
            data=best_plan.to_dict(),
        )

        is_valid, issues = self.planner.validate_plan(best_plan)
        if is_valid:
            trace.add_step(TraceStepType.PLAN_VALIDATED, "Plan validated")
        else:
            trace.add_step(
                TraceStepType.PLAN_INVALID,
                f"Plan validation issues: {issues}",
                success=False,
            )

        return best_plan

    # -------------------------------------------------------------------------
    # Execution
    # -------------------------------------------------------------------------
    def _execute_plan(
        self,
        plan: DerivationPlan,
        problem: Dict[str, Any],
        trace: ReasoningTrace,
    ) -> Dict[str, Any]:
        trace.add_step(
            TraceStepType.EXECUTION_STARTED,
            "Starting plan execution",
        )

        variables = dict(problem.get("inputs", {}))

        for step in sorted(plan.steps, key=lambda s: s.order):
            formula = self.graph.get_formula(step.formula_id)
            if not formula:
                trace.add_step(
                    TraceStepType.STEP_FAILED,
                    f"Formula not found: {step.formula_id}",
                    success=False,
                )
                continue

            step_result = self._execute_formula(formula, variables)
            if step_result:
                variables.update(step_result)
                trace.add_step(
                    TraceStepType.STEP_EXECUTED,
                    f"Executed: {formula.name}",
                    formula_id=formula.id,
                    formula_name=formula.name,
                    inputs={k: variables.get(k) for k in [v.symbol for v in formula.inputs]},
                    outputs=step_result,
                )
            else:
                trace.add_step(
                    TraceStepType.STEP_FAILED,
                    f"Failed to execute: {formula.name}",
                    formula_id=formula.id,
                    success=False,
                )

        result = {out: variables.get(out) for out in problem.get("outputs", [])}
        result["all_variables"] = variables

        trace.add_step(
            TraceStepType.RESULT_COMPUTED,
            "Computed result",
            outputs=result,
        )
        return result

    def _execute_formula(
        self,
        formula: Formula,
        variables: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """Execute a single formula using the executor (SymPy/SciPy-backed)."""
        return self.executor.evaluate_formula(formula, variables)

    # -------------------------------------------------------------------------
    # Explanation
    # -------------------------------------------------------------------------
    def _generate_explanation(
        self,
        plan: DerivationPlan,
        result: Dict[str, Any],
        trace: ReasoningTrace,
    ) -> str:
        steps_desc = []
        assumptions = set()
        regimes = set()
        for step in sorted(plan.steps, key=lambda s: s.order):
            formula = self.graph.get_formula(step.formula_id)
            if formula:
                steps_desc.append(f"- Applied {formula.name}: {formula.symbolic_form}")
                step_assumptions = getattr(step, "assumptions_used", []) or []
                step_regimes = getattr(step, "regime_conditions", []) or []
                if step_assumptions:
                    assumptions.update(step_assumptions)
                    steps_desc.append(f"  (Assumptions: {', '.join(step_assumptions)})")
                if step_regimes:
                    regimes.update(step_regimes)
        # Aggregate context details
        assumptions_list = sorted(assumptions)
        regimes_list = sorted(regimes)
        confidence = trace.compute_overall_confidence()

        prompt = f"""Generate a clear explanation of this physics derivation.

Problem: {trace.problem_text}

Derivation steps:
{chr(10).join(steps_desc)}

Result: {json.dumps(result.get('all_variables', result))}

Assumptions to respect: {assumptions_list if assumptions_list else "None explicitly stated"}
Regimes/conditions: {regimes_list if regimes_list else "Not specified"}
Current confidence (0-1): {confidence:.2f}

Write a clear, educational explanation that:
1. States what was calculated
2. Explains the physics principles used
3. Shows the key steps
4. States the final answer with units
5. Summarizes assumptions, regimes, and confidence explicitly at the end.

Keep it concise but informative."""

        response = self.llm.generate(
            prompt,
            system_prompt="You are a physics teacher explaining derivations clearly.",
        )

        explanation = response.text.strip()
        trace.add_step(
            TraceStepType.EXPLANATION_GENERATED,
            "Generated explanation",
        )
        # Append a compact summary to ensure users see the key guards
        summary = []
        if assumptions_list:
            summary.append(f"Assumptions: {', '.join(assumptions_list)}")
        if regimes_list:
            summary.append(f"Regimes/Conditions: {', '.join(regimes_list)}")
        summary.append(f"Confidence: {confidence:.2f}")
        if summary:
            explanation = explanation + "\n\n" + "\n".join(summary)
        return explanation

    # -------------------------------------------------------------------------
    # Audit
    # -------------------------------------------------------------------------
    def _run_audit(self, trace: ReasoningTrace):
        issues = self.logic_critic.analyze(trace, check_types={"derivation", "assumptions", "regime"})
        if issues:
            trace.add_step(
                TraceStepType.CRITIC_ANALYSIS,
                f"Critic found {len(issues)} issues",
                data={"issue_count": len(issues)},
            )
            for issue in issues[:3]:
                trace.add_step(
                    TraceStepType.CRITIC_ISSUE_FOUND,
                    f"[{issue.severity}] {issue.message}",
                )
        else:
            trace.add_step(
                TraceStepType.CRITIC_APPROVED,
                "Critic found no issues",
            )

    # -------------------------------------------------------------------------
    # Fallbacks
    # -------------------------------------------------------------------------
    def _general_response(
        self,
        message: str,
        session: ChatSession,
        trace: ReasoningTrace,
    ) -> ChatMessage:
        history = session.get_history(n=5)
        history_str = "\n".join([f"{m['role']}: {m['content'][:100]}" for m in history[:-1]])

        prompt = f"""You are a physics AI assistant. The user asked a question that isn't a specific physics problem.

Conversation history:
{history_str}

User: {message}

Respond helpfully. If the question is physics-related, explain concepts or suggest how to phrase it as a solvable problem.
If it's off-topic, politely redirect to physics topics."""

        response = self.llm.generate(
            prompt,
            system_prompt="You are a helpful physics AI. Stay focused on physics topics.",
        )

        trace.add_step(
            TraceStepType.EXPLANATION_GENERATED,
            "Generated general response",
        )

        return ChatMessage(
            role="assistant",
            content=response.text.strip(),
            trace_id=trace.id,
        )

    def _no_plan_response(
        self,
        problem: Dict[str, Any],
        trace: ReasoningTrace,
    ) -> ChatMessage:
        suggestions = self.planner.suggest_missing_formulas(
            inputs=problem.get("inputs", {}),
            outputs=problem.get("outputs", []),
            context={"domain": problem.get("domain", "general")},
        )

        suggestion_text = ""
        if suggestions:
            suggestion_text = "\n\nI identified these gaps in my knowledge:\n"
            for s in suggestions[:2]:
                suggestion_text += f"- {s.get('message', '')}\n"

        content = f"""I understand you're asking about: {problem.get('description', 'a physics problem')}

However, I couldn't find a complete derivation path with my current knowledge base.
{suggestion_text}
You could try:
1. Breaking the problem into smaller steps
2. Providing additional information or constraints
3. Specifying which formulas or principles to use

The system is continuously learning, so this gap may be addressed in future updates."""

        return ChatMessage(
            role="assistant",
            content=content,
            physics_problem=problem,
            trace_id=trace.id,
            confidence=0.3,
        )

    # -------------------------------------------------------------------------
    # Utilities
    # -------------------------------------------------------------------------
    def get_formula_info(self, formula_id: str) -> Optional[Dict[str, Any]]:
        formula = self.graph.get_formula(formula_id)
        if formula:
            return formula.to_dict()
        return None

    def search_formulas(
        self,
        query: str,
        domain: Optional[str] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        results = []
        query_lower = query.lower()

        for formula in self.graph.get_all_formulas():
            score = 0
            if query_lower in formula.name.lower():
                score += 10
            if formula.description and query_lower in formula.description.lower():
                score += 5
            if query_lower in formula.symbolic_form.lower():
                score += 3
            for tag in formula.tags:
                if query_lower in tag.lower():
                    score += 2

            if domain and formula.domain != domain:
                score = 0

            if score > 0:
                results.append((score, formula))

        results.sort(key=lambda x: -x[0])
        return [f.to_dict() for _, f in results[:limit]]

    def get_graph_stats(self) -> Dict[str, Any]:
        return self.graph.stats()

    def get_trace(self, trace_id: str) -> Optional[Dict[str, Any]]:
        trace = self.trace_store.get(trace_id)
        if trace:
            return trace.to_dict()
        return None

