"""
PATH: physics/inference/generate.py
PURPOSE: Step-by-step physics solution generation pipeline

Follows DeepSeek's generate.py patterns:
- Temperature-based theory sampling (Gumbel trick)
- Iterative solution generation with constraint validation
- Batch processing support

FLOW:
┌─────────┐   ┌──────────────┐   ┌──────────┐   ┌──────────┐
│ Problem │ → │ Sample theory│ → │ Solve    │ → │ Validate │
└─────────┘   └──────────────┘   └──────────┘   └──────────┘

DEPENDENCIES:
- numpy: Numerical computation
- validators.data_validator: Input validation
- loggers.system_logger: Structured logging
"""

from typing import Any, Dict, List, Optional

import numpy as np

from loggers.system_logger import SystemLogger
from validators.data_validator import DataValidator

from .model import PhysicsModelArgs, PhysicsTransformer


def sample_theory(logits: np.ndarray, temperature: float = 1.0) -> int:
    """
    Sample a theory index from logits using temperature-scaled softmax.

    Uses the Gumbel-max trick for efficient categorical sampling:
        argmax_i [log(softmax(logits/T)) + Gumbel(0,1)]

    Args:
        logits: Logits array for theory predictions
        temperature: Temperature for scaling (0 = greedy argmax)

    Returns:
        Index of sampled theory
    """
    if temperature <= 0:
        return int(np.argmax(logits))

    logits = logits / max(temperature, 1e-5)
    probs = np.exp(logits - np.max(logits))  # Numerical stability
    probs = probs / np.sum(probs)

    gumbel = -np.log(-np.log(np.random.random()))
    return int(np.argmax(np.log(probs) + gumbel))


def validate_solution(solution: Dict[str, Any], constraints: Dict[str, Any]) -> bool:
    """
    Validate solution against physical constraints (energy, momentum conservation).

    Args:
        solution: Solution dictionary
        constraints: Physical constraints dictionary

    Returns:
        True if solution satisfies all constraints
    """
    validator = DataValidator()
    _logger = SystemLogger()

    if not validator.validate_dict(solution) or not validator.validate_dict(constraints):
        _logger.log("Invalid solution or constraints", level="ERROR")
        return False

    if "energy" in constraints:
        initial_energy = constraints["energy"].get("initial", 0.0)
        final_energy = solution.get("energy", 0.0)
        tolerance = constraints["energy"].get("tolerance", 1e-6)

        if abs(final_energy - initial_energy) > tolerance:
            _logger.log(f"Energy conservation violated: {abs(final_energy - initial_energy)}", level="WARNING")
            return False

    if "momentum" in constraints:
        initial_momentum = np.array(constraints["momentum"].get("initial", [0.0, 0.0, 0.0]))
        final_momentum = np.array(solution.get("momentum", [0.0, 0.0, 0.0]))
        tolerance = constraints["momentum"].get("tolerance", 1e-6)

        if np.linalg.norm(final_momentum - initial_momentum) > tolerance:
            _logger.log(f"Momentum conservation violated: {np.linalg.norm(final_momentum - initial_momentum)}", level="WARNING")
            return False

    _logger.log("Solution validation passed", level="DEBUG")
    return True


def generate_solution(
    model: PhysicsTransformer,
    problem: Dict[str, Any],
    max_steps: int = 100,
    temperature: float = 1.0,
    constraints: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Generate a physics solution step-by-step.

    At each step: select a theory via temperature sampling, apply the
    model forward pass, and accumulate results until completion or
    max_steps is reached.

    Args:
        model: Physics transformer model
        problem: Problem dictionary
        max_steps: Maximum number of solution steps
        temperature: Temperature for theory sampling
        constraints: Optional physical constraints

    Returns:
        Generated solution dictionary
    """
    validator = DataValidator()
    _logger = SystemLogger()

    if not validator.validate_dict(problem):
        _logger.log("Invalid problem provided", level="ERROR")
        raise ValueError("Invalid problem")

    _logger.log(f"Generating solution for problem (max_steps={max_steps})", level="INFO")

    solution: Dict[str, Any] = {
        "steps": [],
        "theories": [],
        "current_state": problem.get("initial_conditions", {}),
    }

    for step in range(max_steps):
        theory_logits = np.random.random(len(model.args.theory_types))
        theory_idx = sample_theory(theory_logits, temperature)
        theory = model.args.theory_types[theory_idx]

        step_problem = {
            **problem,
            "theory": theory,
            "current_state": solution["current_state"],
        }

        step_result = model.forward(step_problem)

        solution["steps"].append({
            "step": step,
            "theory": theory,
            "result": step_result,
        })
        solution["theories"].append(theory)

        if "solution" in step_result and "state" in step_result["solution"]:
            solution["current_state"] = step_result["solution"]["state"]

        if step_result.get("complete", False):
            _logger.log(f"Solution complete at step {step}", level="INFO")
            break

    if constraints:
        solution["valid"] = validate_solution(solution, constraints)
    else:
        solution["valid"] = True

    _logger.log("Solution generation completed", level="INFO")
    return solution


def generate_batch(
    model: PhysicsTransformer,
    problems: List[Dict[str, Any]],
    max_steps: int = 100,
    temperature: float = 1.0,
    constraints: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """
    Generate solutions for a batch of problems.

    Args:
        model: Physics transformer model
        problems: List of problem dictionaries
        max_steps: Maximum number of solution steps per problem
        temperature: Temperature for theory sampling
        constraints: Optional physical constraints

    Returns:
        List of generated solution dictionaries
    """
    _logger = SystemLogger()

    assert len(problems) <= model.args.max_batch_size, (
        f"Number of problems ({len(problems)}) exceeds maximum batch size ({model.args.max_batch_size})"
    )

    _logger.log(f"Generating solutions for batch of {len(problems)} problems", level="INFO")

    solutions = [
        generate_solution(model, problem, max_steps, temperature, constraints)
        for problem in problems
    ]

    _logger.log("Batch solution generation completed", level="INFO")
    return solutions
