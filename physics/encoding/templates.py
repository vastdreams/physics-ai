# PATH: physics/encoding/templates.py
# PURPOSE:
#   - Define template strings for physics problems, following DeepSeek's template patterns
#   - Provides structured formats for system, problem, solution, and tool calling
#
# ROLE IN ARCHITECTURE:
#   - Encoding layer: Template definitions for physics problem representation
#
# MAIN EXPORTS:
#   - Template strings for different physics problem types
#   - Special tokens for physics problem markup
#
# NON-RESPONSIBILITIES:
#   - This file does NOT handle:
#     - Actual template rendering (handled by encoding_physics.py)
#     - Problem solving (handled by inference layer)
#
# NOTES FOR FUTURE AI:
#   - Follows DeepSeek's template patterns from encoding_dsv32.py
#   - PPML (Physics Problem Markup Language) mirrors DSML structure
#   - Special tokens follow DeepSeek's token naming conventions

from typing import Any, Dict, List, Union

# Special tokens (inspired by DeepSeek's token system)
bos_token: str = "<|physics_begin|>"
eos_token: str = "<|physics_end|>"
reasoning_start_token: str = "<|reasoning|>"
reasoning_end_token: str = "</|reasoning|>"
ppml_token: str = "｜PPML｜"  # Physics Problem Markup Language (similar to DSML)

# Template strings (following DeepSeek's template patterns)
system_template: str = "{content}"
problem_template: str = "<|physics_User|>{content}<|physics_Assistant|>"
solution_template: str = "{reasoning}{content}{tool_calls}<|physics_end|>"
reasoning_template: str = "{reasoning_content}"

# Response format template (like DeepSeek's response_format_template)
response_format_template: str = (
    "## Response Format:\n\nYou MUST strictly adhere to the following schema to reply:\n{schema}"
)

# Tool calling templates (following DeepSeek's DSML pattern)
TOOLS_SYSTEM_TEMPLATE = """## Physics Tools

You have access to a set of physics tools you can use to solve the problem.
You can invoke functions by writing a "<{ppml_token}function_calls>" block like the following as part of your reply:
<{ppml_token}function_calls>
<{ppml_token}invoke name="$FUNCTION_NAME">
<{ppml_token}parameter name="$PARAMETER_NAME" string="true|false">$PARAMETER_VALUE</{ppml_token}parameter>
...
</{ppml_token}invoke>
<{ppml_token}invoke name="$FUNCTION_NAME2">
...
</{ppml_token}invoke>
</{ppml_token}function_calls>

String and scalar parameters should be specified as is without any escaping or quotes, while lists and objects should use JSON format. The "string" attribute should be set to "true" for string type parameters and "false" for other types (numbers, booleans, arrays, objects).

If the reasoning_mode is enabled, then after function results you should strongly consider outputting a reasoning block. Here is an example:

<{ppml_token}function_calls>
...
</{ppml_token}function_calls>

<function_results>
...
</function_results>

{reasoning_start_token}...reasoning about results{reasoning_end_token}

Here are the functions available in JSONSchema format:
<functions>
{tool_schemas}
</functions>
"""

tool_call_template: str = (
    "<{ppml_token}invoke name=\"{name}\">\n{arguments}\n</{ppml_token}invoke>"
)

tool_calls_template = (
    "<{ppml_token}function_calls>\n{tool_calls}\n</{ppml_token}function_calls>"
)

tool_output_template: str = (
    "\n<result>{content}</result>"
)

# Physics-specific templates
PHYSICS_SYSTEM_TEMPLATE = """## Physics Domain

You are solving a physics problem. The problem may involve:
- Classical mechanics (Newtonian, Lagrangian, Hamiltonian)
- Quantum mechanics (Schrödinger equation, path integrals)
- Field theory (Electromagnetic, Gauge theory, General Relativity)
- Statistical mechanics (Thermodynamics, Ensemble theory, Phase transitions)

You must:
1. Identify the appropriate physics domain(s)
2. Apply relevant conservation laws and symmetries
3. Solve using appropriate mathematical methods
4. Validate results against physical constraints
5. Provide step-by-step reasoning

{content}
"""

PROBLEM_TEMPLATE = """## Physics Problem

**Domain**: {domain}
**Type**: {problem_type}

**Initial Conditions**:
{initial_conditions}

**Constraints**:
{constraints}

**Goal**: {goal}

**Problem Statement**:
{problem_statement}
"""

SOLUTION_TEMPLATE = """## Solution

**Selected Theory**: {theory}
**Method**: {method}

**Step-by-Step Solution**:
{steps}

**Final Answer**: {answer}

**Validation**:
{validation}
"""

TOOL_CALL_TEMPLATE = tool_call_template
TOOL_CALLS_TEMPLATE = tool_calls_template

