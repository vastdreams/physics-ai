# PATH: physics/encoding/encoding_physics.py
# PURPOSE:
#   - Physics problem encoding/decoding following DeepSeek's encoding_dsv32.py patterns
#   - Template-based message rendering with special tokens
#   - PPML (Physics Problem Markup Language) for tool calling
#
# ROLE IN ARCHITECTURE:
#   - Encoding layer: Separates problem representation from computation
#
# MAIN EXPORTS:
#   - encode_problem(): Convert physics problem to structured format
#   - decode_solution(): Parse solution from structured format
#   - render_problem(): Format problem using templates
#   - parse_tool_calls(): Parse physics tool invocations
#
# NON-RESPONSIBILITIES:
#   - This file does NOT handle:
#     - Actual physics computation (handled by inference layer)
#     - Model training or inference (handled by inference layer)
#
# NOTES FOR FUTURE AI:
#   - Follows DeepSeek's encoding_dsv32.py patterns exactly
#   - Uses same function signatures and logic flow
#   - PPML mirrors DSML structure for tool calling

from typing import Any, Dict, List, Union, Optional, Tuple
import copy
import json
import re

from .templates import (
    bos_token,
    eos_token,
    reasoning_start_token,
    reasoning_end_token,
    ppml_token,
    system_template,
    problem_template,
    solution_template,
    reasoning_template,
    response_format_template,
    tool_call_template,
    tool_calls_template,
    tool_output_template,
    TOOLS_SYSTEM_TEMPLATE,
)


def to_json(value: Any) -> str:
    """
    Convert value to JSON string, following DeepSeek's pattern.
    
    Args:
        value: Value to convert to JSON
        
    Returns:
        JSON string representation
    """
    try:
        return json.dumps(value, ensure_ascii=False)
    except:
        return json.dumps(value, ensure_ascii=True)


def tools_from_openai_format(tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Convert tools from OpenAI format, following DeepSeek's pattern.
    
    Args:
        tools: Tools in OpenAI format
        
    Returns:
        Tools in simplified format
    """
    return [tool["function"] for tool in tools]


def tool_calls_from_openai_format(tool_calls: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    """
    Convert tool calls from OpenAI format, following DeepSeek's pattern.
    
    Args:
        tool_calls: Tool calls in OpenAI format
        
    Returns:
        Tool calls in simplified format
    """
    return [
        {
            "name": tool_call["function"]["name"],
            "arguments": tool_call["function"]["arguments"],
        }
        for tool_call in tool_calls
    ]


def tool_calls_to_openai_format(tool_calls: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    """
    Convert tool calls to OpenAI format, following DeepSeek's pattern.
    
    Args:
        tool_calls: Tool calls in simplified format
        
    Returns:
        Tool calls in OpenAI format
    """
    return [
        {
            "type": "function",
            "function": {
                "name": tool_call["name"],
                "arguments": tool_call["arguments"],
            }
        }
        for tool_call in tool_calls
    ]


def encode_arguments_to_ppml(tool_call: Dict[str, str]) -> str:
    """
    Encode tool call arguments to PPML format, following DeepSeek's DSML pattern.
    
    Args:
        tool_call: Tool call dictionary with name and arguments
        
    Returns:
        PPML-formatted parameter string
    """
    p_ppml_template = """<{ppml_token}parameter name="{key}" string="{is_str}">{value}</{ppml_token}parameter>"""
    P_ppml_strs = []

    arguments = json.loads(tool_call["arguments"])

    for k, v in arguments.items():
        p_ppml_str = p_ppml_template.format(
            ppml_token=ppml_token,
            key=k,
            is_str="true" if isinstance(v, str) else "false",
            value=v if isinstance(v, str) else to_json(v),
        )

        P_ppml_strs.append(p_ppml_str)

    return "\n".join(P_ppml_strs)


def decode_ppml_to_arguments(tool_name: str, tool_args: Dict[str, Tuple[str, str]]) -> Dict[str, str]:
    """
    Decode PPML format to tool call arguments, following DeepSeek's DSML pattern.
    
    Args:
        tool_name: Name of the tool
        tool_args: Dictionary mapping parameter names to (value, is_string) tuples
        
    Returns:
        Tool call dictionary with name and arguments
    """
    def _decode_value(key: str, value: str, string: str):
        if string == "true":
            value = to_json(value)
        return f"{to_json(key)}: {value}"

    tool_args_json = "{" + ", ".join([_decode_value(k, v, string=is_str) for k, (v, is_str) in tool_args.items()]) + "}"
    return dict(name=tool_name, arguments=tool_args_json)


def render_tools(tools: List[Dict[str, Union[str, Dict[str, Any]]]]) -> str:
    """
    Render tools in system template format, following DeepSeek's pattern.
    
    Args:
        tools: List of tool definitions
        
    Returns:
        Formatted tools string
    """
    tools_json = [to_json(t) for t in tools]

    return TOOLS_SYSTEM_TEMPLATE.format(
        tool_schemas="\n".join(tools_json),
        ppml_token=ppml_token,
        reasoning_start_token=reasoning_start_token,
        reasoning_end_token=reasoning_end_token,
    )


def find_last_user_index(messages: List[Dict[str, Any]]) -> int:
    """
    Find index of last user message, following DeepSeek's pattern.
    
    Args:
        messages: List of messages
        
    Returns:
        Index of last user message, or -1 if not found
    """
    last_user_index = -1
    for idx in range(len(messages)-1, -1, -1):
        if messages[idx].get("role") in ["user", "developer"]:
            last_user_index = idx
            break
    return last_user_index


def render_problem(index: int, messages: List[Dict[str, Any]], reasoning_mode: str) -> str:
    """
    Render a physics problem message, following DeepSeek's render_message pattern.
    
    Args:
        index: Index of message to render
        messages: List of all messages
        reasoning_mode: Mode for reasoning ("chat" or "thinking")
        
    Returns:
        Rendered prompt string
        
    Raises:
        AssertionError: If index is invalid or reasoning_mode is invalid
    """
    assert 0 <= index < len(messages)
    assert reasoning_mode in ["chat", "thinking"], f"Invalid reasoning_mode `{reasoning_mode}`"

    prompt = ""
    msg = messages[index]
    last_user_idx = find_last_user_index(messages)

    role = msg.get("role")
    content = msg.get("content")
    tools = msg.get("tools")
    response_format = msg.get("response_format")
    tool_calls = msg.get("tool_calls")
    reasoning_content = msg.get("reasoning_content")

    if tools:
        tools = tools_from_openai_format(tools)
    if tool_calls:
        tool_calls = tool_calls_from_openai_format(tool_calls)

    if role == "system":
        prompt += system_template.format(content=content or "")
        if tools:
            prompt += "\n\n" + render_tools(tools)

        if response_format:
            prompt += "\n\n" + response_format_template.format(schema=to_json(response_format))

    elif role == "developer":
        assert content, f"Invalid message for role `{role}`: {msg}"
        content_developer = ""
        if tools:
            content_developer += "\n\n" + render_tools(tools)

        if response_format:
            content_developer += "\n\n" + response_format_template.format(schema=to_json(response_format))

        content_developer += "\n\n# The user's message is: {}".format(content)

        prompt += problem_template.format(content=content_developer)
        if index == last_user_idx and reasoning_mode == "thinking":
            prompt += reasoning_start_token
        else:
            prompt += reasoning_end_token

    elif role == "user":
        prompt += problem_template.format(content=content)

        if index == last_user_idx and reasoning_mode == "thinking":
            prompt += reasoning_start_token
        else:
            prompt += reasoning_end_token

    elif role == "tool":
        prev_assistant_idx = index - 1
        assistant_msg = messages[prev_assistant_idx]
        while prev_assistant_idx >= 0 and assistant_msg.get("role") == "tool":
            prev_assistant_idx -= 1
            assistant_msg = messages[prev_assistant_idx]

        assert index == 0 or prev_assistant_idx >= 0 and assistant_msg.get("role") == "assistant", f"Invalid messages at {index}:\n{assistant_msg}"

        tool_call_order = index - prev_assistant_idx
        assistant_tool_calls = assistant_msg.get("tool_calls")
        assert assistant_tool_calls and len(assistant_tool_calls) >= tool_call_order, "No tool calls but found tool output"

        if tool_call_order == 1:
            prompt += "\n\n<function_results>"

        prompt += tool_output_template.format(content=content)

        if tool_call_order == len(assistant_tool_calls):
            prompt += "\n</function_results>"

            if index >= last_user_idx and reasoning_mode == "thinking":
                prompt += "\n\n" + reasoning_start_token
            else:
                prompt += "\n\n" + reasoning_end_token

    elif role == "assistant":
        prev_assistant_idx = index
        thinking_part = ""

        tool_calls_content = ""
        if tool_calls:
            tool_calls = [
                tool_call_template.format(
                    ppml_token=ppml_token,
                    name=tool_call.get("name"),
                    arguments=encode_arguments_to_ppml(tool_call)
                )
                for tool_call in tool_calls
            ]
            tool_calls_content += "\n\n" + tool_calls_template.format(
                ppml_token=ppml_token,
                tool_calls="\n".join(tool_calls)
            )

        summary_content = content or ""

        if reasoning_mode == "thinking" and index > last_user_idx:
            assert reasoning_content or tool_calls, f"ReasoningMode: {reasoning_mode}, invalid message without reasoning_content/tool_calls `{msg}` after last user message"
            thinking_part = reasoning_template.format(reasoning_content=reasoning_content or "") + reasoning_end_token

        prompt += solution_template.format(
            reasoning=thinking_part,
            content=summary_content,
            tool_calls=tool_calls_content,
        )
    else:
        raise NotImplementedError(f"Unknown role: {role}")

    return prompt


def drop_reasoning_messages(messages: List[Dict[str, Any]], last_user_idx: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Drop reasoning content from messages, following DeepSeek's pattern.
    
    Args:
        messages: List of messages
        last_user_idx: Index of last user message (computed if None)
        
    Returns:
        Messages without reasoning content
    """
    messages_wo_reasoning: List[Dict[str, Any]] = []
    last_user_idx = find_last_user_index(messages) if last_user_idx is None else last_user_idx
    for idx, msg in enumerate(messages):
        role = msg.get("role")
        if role in ["user", "system", "tool"] or idx >= last_user_idx:
            messages_wo_reasoning.append(msg)
            continue

        elif role == "assistant":
            msg_wo_reasoning = copy.copy(msg)
            msg_wo_reasoning.pop("reasoning_content", None)
            messages_wo_reasoning.append(msg_wo_reasoning)

    return messages_wo_reasoning


def encode_problem(messages: List[Dict[str, Any]], reasoning_mode: str, context: Optional[List[Dict[str, Any]]] = None, drop_reasoning: bool = True, add_default_bos_token: bool = True) -> str:
    """
    Encode physics problem messages to prompt string, following DeepSeek's encode_messages pattern.
    
    Args:
        messages: List of messages to encode
        reasoning_mode: Mode for reasoning ("chat" or "thinking")
        context: Optional context messages
        drop_reasoning: Whether to drop reasoning content
        add_default_bos_token: Whether to add beginning-of-sequence token
        
    Returns:
        Encoded prompt string
    """
    context = context if context else []
    full_messages = context + messages

    prompt = bos_token if add_default_bos_token and len(context) == 0 else ""

    if reasoning_mode == "thinking" and drop_reasoning:
        full_messages = drop_reasoning_messages(full_messages)

    for idx in range(len(messages)):
        prompt += render_problem(idx + len(context), full_messages, reasoning_mode=reasoning_mode)

    return prompt


def _read_until_stop(index: int, text: str, stop: List[str]) -> Tuple[int, str, Optional[str]]:
    """
    Read text until a stop token is found, following DeepSeek's pattern.
    
    Args:
        index: Starting index in text
        text: Text to search
        stop: List of stop tokens to search for
        
    Returns:
        Tuple of (new_index, content, matched_stop_token)
    """
    min_pos = len(text)
    matched_stop = None
    
    for s in stop:
        pos = text.find(s, index)
        if pos != -1 and pos < min_pos:
            min_pos = pos
            matched_stop = s
    
    if matched_stop:
        content = text[index:min_pos]
        return min_pos + len(matched_stop), content, matched_stop
    else:
        content = text[index:]
        return len(text), content, None


def parse_tool_calls(index: int, text: str) -> Tuple[int, Optional[str], List[Dict[str, Any]]]:
    """
    Parse tool calls from text, following DeepSeek's parse_tool_calls pattern.
    
    Args:
        index: Starting index in text
        text: Text to parse
        
    Returns:
        Tuple of (new_index, stop_token, tool_calls)
        
    Raises:
        AssertionError: If tool call format is invalid
    """
    tool_calls: List[Dict[str, Any]] = []
    stop_token = None
    tool_calls_end_token = f"</{ppml_token}function_calls>"

    while index < len(text):
        index, _, stop_token = _read_until_stop(index, text, [f"<{ppml_token}invoke", tool_calls_end_token])
        assert _ == ">\n", "Tool call format error"

        if stop_token == tool_calls_end_token:
            break

        assert stop_token is not None, "Missing special token"

        index, tool_name_content, stop_token = _read_until_stop(index, text, [f"<{ppml_token}parameter", f"</{ppml_token}invoke"])

        p_tool_name = re.findall(r'^\s*name="(.*?)">\n$', tool_name_content, flags=re.DOTALL)
        assert len(p_tool_name) == 1, "Tool name format error"
        tool_name = p_tool_name[0]

        tool_args: Dict[str, Tuple[str, str]] = {}
        while stop_token == f"<{ppml_token}parameter":
            index, param_content, stop_token = _read_until_stop(index, text, [f"/{ppml_token}parameter"])

            param_kv = re.findall(r'^ name="(.*?)" string="(true|false)">(.*?)<$', param_content, flags=re.DOTALL)
            assert len(param_kv) == 1, "Parameter format error"
            param_name, string, param_value = param_kv[0]

            assert param_name not in tool_args, "Duplicate parameter name"
            tool_args[param_name] = (param_value, string)

            index, content, stop_token = _read_until_stop(index, text, [f"<{ppml_token}parameter", f"</{ppml_token}invoke"])
            assert content == ">\n", "Parameter format error"

        tool_call = decode_ppml_to_arguments(tool_name=tool_name, tool_args=tool_args)
        tool_calls.append(tool_call)

    return index, stop_token, tool_calls


def parse_message_from_completion_text(text: str, reasoning_mode: str) -> Dict[str, Any]:
    """
    Parse message from completion text, following DeepSeek's parse_message_from_completion_text pattern.
    
    NOTE: This function is designed to parse only correctly formatted string and will not attempt to correct malformed output.
    
    Args:
        text: Completion text to parse
        reasoning_mode: Mode for reasoning ("chat" or "thinking")
        
    Returns:
        Parsed message dictionary
        
    Raises:
        AssertionError: If text format is invalid
    """
    summary_content, reasoning_content, tool_calls = "", "", []
    index, stop_token = 0, None
    tool_calls_start_token = f"\n\n<{ppml_token}function_calls"

    is_thinking, is_tool_calling = reasoning_mode == "thinking", False

    if is_thinking:
        index, content_delta, stop_token = _read_until_stop(index, text, [reasoning_end_token, tool_calls_start_token])
        reasoning_content = content_delta
        assert stop_token == reasoning_end_token, "Invalid reasoning format"

    index, content_delta, stop_token = _read_until_stop(index, text, [eos_token, tool_calls_start_token])
    summary_content = content_delta
    if stop_token == tool_calls_start_token:
        is_tool_calling = True
    else:
        assert stop_token == eos_token, "Invalid summary format"

    if is_tool_calling:
        index, stop_token, tool_calls = parse_tool_calls(index, text)

        index, tool_ends_text, stop_token = _read_until_stop(index, text, [eos_token])
        assert not tool_ends_text, "Unexpected content after tool calls"

    assert len(text) == index and stop_token in [eos_token, None], "Unexpected content at end"

    for sp_token in [bos_token, eos_token, reasoning_start_token, reasoning_end_token, ppml_token]:
        assert sp_token not in summary_content and sp_token not in reasoning_content, "Unexpected special token in content"

    return {
        "role": "assistant",
        "content": summary_content,
        "reasoning_content": reasoning_content,
        "tool_calls": tool_calls_to_openai_format(tool_calls)
    }


# Aliases for backward compatibility and clarity
encode_messages = encode_problem
decode_solution = parse_message_from_completion_text

