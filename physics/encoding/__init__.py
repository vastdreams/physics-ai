# PATH: physics/encoding/__init__.py
# PURPOSE:
#   - Encoding package for physics problems, following DeepSeek's encoding patterns
#   - Handles problem formatting, encoding/decoding, and tool calling format
#
# ROLE IN ARCHITECTURE:
#   - Encoding layer: Separates problem representation from computation
#
# MAIN EXPORTS:
#   - encoding_physics: Main encoding/decoding functions
#   - templates: Template strings for physics problems
#
# NON-RESPONSIBILITIES:
#   - This package does NOT handle:
#     - Actual physics computation (handled by inference layer)
#     - Model training or inference (handled by inference layer)
#
# NOTES FOR FUTURE AI:
#   - Follows DeepSeek's encoding_dsv32.py patterns exactly
#   - Uses PPML (Physics Problem Markup Language) similar to DSML
#   - Template system mirrors DeepSeek's message rendering

from .encoding_physics import (
    encode_problem,
    decode_solution,
    render_problem,
    parse_tool_calls,
    encode_arguments_to_ppml,
    decode_ppml_to_arguments,
    encode_messages,
    parse_message_from_completion_text,
)

from .templates import (
    PHYSICS_SYSTEM_TEMPLATE,
    PROBLEM_TEMPLATE,
    SOLUTION_TEMPLATE,
    TOOL_CALL_TEMPLATE,
    TOOL_CALLS_TEMPLATE,
    bos_token,
    eos_token,
    reasoning_start_token,
    reasoning_end_token,
    ppml_token,
)

__all__ = [
    "encode_problem",
    "decode_solution",
    "render_problem",
    "parse_tool_calls",
    "encode_arguments_to_ppml",
    "decode_ppml_to_arguments",
    "encode_messages",
    "parse_message_from_completion_text",
    "PHYSICS_SYSTEM_TEMPLATE",
    "PROBLEM_TEMPLATE",
    "SOLUTION_TEMPLATE",
    "TOOL_CALL_TEMPLATE",
    "TOOL_CALLS_TEMPLATE",
    "bos_token",
    "eos_token",
    "reasoning_start_token",
    "reasoning_end_token",
    "ppml_token",
]

