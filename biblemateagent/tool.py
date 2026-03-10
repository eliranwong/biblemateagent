import asyncio
import traceback
import os
import re
from copy import deepcopy

from biblemateagent.stream import stream_output
from biblemateweb import get_translation, chapter2verses, DEFAULT_MESSAGES, BIBLEMATEWEB_APP_DIR
from biblemateweb.mcp_tools.elements import TOOL_ELEMENTS
from biblemateweb.mcp_tools.tools import TOOLS
from biblemateweb.api.api import get_api_content
from biblemate.core.systems import get_system_tool_instruction, get_system_generate_title
from biblemateagent import do_export
from agentmake import agentmake, readTextFile, getCurrentDateTime, DEFAULT_AI_BACKEND

async def run_single_tool(
    selected_tool,
    request,
    MESSAGES=None,
    language="eng",
    prompt_refinement=False,
    md_export=False,
    docx_export=False,
    output_directory="",
    developer=False,
    cancel_event=None,
    **kwargs
):
    """
    Run a single tool using the provided request and tool name.
    Extracts the workflow from agent.py for single tool execution.
    """

    if not request or not request.strip():
        print("Please provide a request.")
        return None

    original_user_request = request

    SYSTEM_TOOL_SELECTION = readTextFile(os.path.join(BIBLEMATEWEB_APP_DIR, "mcp_tools", "system_tool_selection_lite.md"))

    TOOL_INSTRUCTION_PROMPT = """Please transform the following suggestions into clear, precise, and actionable instructions."""
    TOOL_INSTRUCTION_SUFFIX = """

# Remember

* Provide me with the instructions directly.
* Do not start your response, like, 'Here are the insturctions ...'
* Do not ask me if I want to execute the instruction."""

    if not output_directory:
        output_directory = os.getcwd()
    output_directory = os.path.abspath(output_directory)

    # generate title
    generated_title = ""
    generated_title_output = agentmake(
        request,
        system=get_system_generate_title(),
        backend=kwargs.get("backend", DEFAULT_AI_BACKEND),
        model=kwargs.get("model", None),
        api_key=kwargs.get("api_key", None),
        api_endpoint=kwargs.get("api_endpoint", None),
        max_tokens=kwargs.get("max_tokens", None),
        context_window=kwargs.get("context_window", None),
        temperature=kwargs.get("temperature", None),
        print_on_terminal=False,
        **{"think": kwargs.get("think")} if "think" in kwargs else {},
    )
    timestamp = getCurrentDateTime()
    if generated_title_output:
        generated_title = generated_title_output[-1].get("content", "").strip().replace("Title: ", "")
        if not generated_title == "[NO_CONTENT]":
            print(f"\n[TITLE] {generated_title}\n")
            sanitized_title = re.sub(r"[^a-zA-Z0-9_\u4e00-\u9fff\s\-\.]+", "_", generated_title)
            study_directory = f"{timestamp}_{sanitized_title}"
            output_directory = os.path.join(output_directory, study_directory)
        else:
            study_directory = f"{timestamp}_biblemate_study"
            output_directory = os.path.join(output_directory, study_directory)
    else:
        study_directory = f"{timestamp}_biblemate_study"
        output_directory = os.path.join(output_directory, study_directory)

    print(f"\n[REQUEST] {request}\n")

    if MESSAGES is None:
        MESSAGES = deepcopy(DEFAULT_MESSAGES)

    if prompt_refinement:
        print("\n--- Refining Your Request ---\n")
        user_request = await stream_output(
            MESSAGES, request+"\n\n# Remember\n\nYour role is to refine the request given above, not to answer the request.", cancel_event, system="improve_prompt_2", **kwargs
        )
        if user_request and user_request.strip() != "[NO_CONTENT]":
            if "```" in user_request:
                request = re.sub(r"^.*?(```improved_prompt|```)(.+?)```.*?$", r"\2", user_request, flags=re.DOTALL).strip()
            else:
                request = user_request.strip()
            print(f"\n[IMPROVED REQUEST] {request}\n")

    if selected_tool == "auto":
        # tool selection
        print("\n--- Tool Selection ---\n")
        suggested_tools = await stream_output(DEFAULT_MESSAGES, request, cancel_event, system=SYSTEM_TOOL_SELECTION, **kwargs)
        
        if not suggested_tools or suggested_tools.strip() == "[NO_CONTENT]":
            suggested_tools_list = ["get_direct_text_response"]
        else:
            try:
                suggested_tools_str = re.sub(r"^.*?(\[.*?\]).*?$", r"\1", suggested_tools, flags=re.DOTALL)
                suggested_tools_list = eval(suggested_tools_str.replace("`", "'")) if suggested_tools_str.startswith("[") and suggested_tools_str.endswith("]") else ["get_direct_text_response"]
            except:
                suggested_tools_list = ["get_direct_text_response"]

        selected_tool = suggested_tools_list[0] if suggested_tools_list else "get_direct_text_response"
        if not selected_tool in TOOLS:
            selected_tool = "get_direct_text_response"

    print(f"\n[Selected Tool: {selected_tool}]\n")

    # tool instruction
    print("\n--- Tool Instruction ---\n")
    selected_tool_description = TOOLS.get(selected_tool, "No description available.")
    tool_instruction_draft = TOOL_INSTRUCTION_PROMPT + "\n\n# Request\n\n"+request+f"\n\n# Tool Description of `{selected_tool}`\n\n"+selected_tool_description+TOOL_INSTRUCTION_SUFFIX
    system_tool_instruction = get_system_tool_instruction(selected_tool, selected_tool_description)
    
    user_request = await stream_output(MESSAGES, tool_instruction_draft, cancel_event, system=system_tool_instruction, **kwargs)
    
    if not user_request or user_request.strip() == "[NO_CONTENT]":
        print("\n[No tool instruction generated. Stopping.]\n")
        return None, None

    print("\n--- Agent Execution ---\n")
    answers = None
    try:
        if selected_tool == "get_direct_text_response":
            answers = await stream_output(MESSAGES, user_request, cancel_event, system="auto", **kwargs)
        else:
            element = TOOL_ELEMENTS.get(selected_tool)
            if isinstance(element, str):
                print(f"Loading {selected_tool}...")
                if not selected_tool.startswith("search_"):
                    user_req = chapter2verses(user_request)
                else:
                    user_req = user_request
                api_query = f"{element}{user_req}"
                answers = await asyncio.to_thread(get_api_content, api_query, language)
                if answers:
                    print(answers)
                else:
                    answers = "[NO_CONTENT]"
                    print(answers)
            elif isinstance(element, dict):
                element_copy = element.copy()
                system = element_copy.pop("system") if "system" in element_copy else None
                answers = await stream_output(MESSAGES, user_request, cancel_event, system=system, **element_copy, **kwargs)
                
    except Exception as e:
        answers = f"[{get_translation('Error')}: {str(e)}]"
        print(f"\n{answers}\n")
        if developer:
            traceback.print_exc()

    if md_export or docx_export:
        filename = selected_tool
        content = f"# Title\n\n{generated_title}\n\n" if generated_title else ""
        if original_user_request == request:
            content += f"# Request\n\n{request}\n\n# Selected Tool\n\n{selected_tool}\n\n# Tool Instruction\n\n{user_request}\n\n# Tool Response\n\n{answers}"
        else:
            original_user_request = original_user_request.strip()
            content += f"# Original Request\n\n{original_user_request}\n\n# Refined Request\n\n{request}\n\n# Selected Tool\n\n{selected_tool}\n\n# Tool Instruction\n\n{user_request}\n\n# Tool Response\n\n{answers}"
        do_export(content, filename, md_export, docx_export, output_directory)

    MESSAGES += [
        {"role": "user", "content": user_request},
        {"role": "assistant", "content": f"[TOOL] {selected_tool}\n\n[RESPONSE]\n\n{answers}"},
    ]
    return MESSAGES
