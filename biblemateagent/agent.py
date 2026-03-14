import asyncio
import re
import os
import traceback
from copy import deepcopy

from biblemateagent.stream import stream_output
from biblemateweb import BIBLEMATEWEB_APP_DIR, DEFAULT_MESSAGES, chapter2verses
from biblemateweb.api.api import get_api_content
from biblemate.core.systems import get_system_tool_instruction, get_system_master_plan, get_system_make_suggestion, get_system_progress, get_system_generate_title
from agentmake import agentmake, readTextFile, getCurrentDateTime, DEFAULT_AI_BACKEND
from agentmake.tools.search.ollamacloud import ollama_web_search
from biblemateagent import do_export, TOOLS, TOOL_ELEMENTS

async def bible_agent(
    request="",
    language="eng",
    prompt_refinement=False,
    md_export=False,
    docx_export=False,
    output_directory="",
    developer=False,
    cancel_event=None,
    **kwargs
):

    if not request or not request.strip():
        print("Please provide a request.")
        return None

    MESSAGES = None
    MASTER_PLAN = None
    PROGRESS_STATUS = None
    ROUND = 1
    MASTER_USER_REQUEST = request

    SYSTEM_TOOL_SELECTION = readTextFile(os.path.join(BIBLEMATEWEB_APP_DIR, "mcp_tools", "system_tool_selection_mini_web.md" if os.getenv("OLLAMACLOUD_API_KEY") else "system_tool_selection_mini.md"))

    TOOL_INSTRUCTION_PROMPT = """Please transform the following suggestions into clear, precise, and actionable instructions."""
    TOOL_INSTRUCTION_SUFFIX = """

# Remember

* Provide me with the instructions directly.
* Do not start your response, like, 'Here are the insturctions ...'
* Do not ask me if I want to execute the instruction."""

    MASTER_PLAN_PROMPT_TEMPLATE = """Provide me with the `Preliminary Action Plan` and the `Measurable Outcome` for resolving `My Request`.
    
# Available Tools

Available tools are: {available_tools}.

{tool_descriptions}

# My Request

{user_request}"""

    FINAL_INSTRUCTION = """# Instruction
Please provide a comprehensive response that resolves my original request, ensuring all previously completed milestones and data points are fully integrated.

# Original Request
"""

    if not output_directory:
        output_directory = os.getcwd()
    output_directory = os.path.abspath(output_directory)

    # generate title
    generated_title = ""
    generated_title_output = agentmake(
        MASTER_USER_REQUEST,
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

    print(f"\n[REQUEST] {MASTER_USER_REQUEST}\n")

    MESSAGES = deepcopy(DEFAULT_MESSAGES)

    original_user_request = MASTER_USER_REQUEST
    if prompt_refinement:
        print("\n--- Refining Your Request ---\n")
        user_request = await stream_output(
            MESSAGES, MASTER_USER_REQUEST+"\n\n# Remember\n\nYour role is to refine the request given above, not to answer the request.", cancel_event, system="improve_prompt_2", **kwargs
        )
        if user_request and user_request.strip() != "[NO_CONTENT]":
            if "```" in user_request:
                MASTER_USER_REQUEST = re.sub(r"^.*?(```improved_prompt|```)(.+?)```.*?$", r"\2", user_request, flags=re.DOTALL).strip()
            else:
                MASTER_USER_REQUEST = user_request.strip()
            print(f"\n[IMPROVED REQUEST] {MASTER_USER_REQUEST}\n")

    MESSAGES += [
        {"role": "user", "content": MASTER_USER_REQUEST},
        {"role": "assistant", "content": "Let's begin!"},
    ]

    # Generate master plan
    print("\n--- Generating Study Plan ---\n")
    available_tools = list(TOOL_ELEMENTS.keys())
    available_tools_desciption = "\n\n".join([f'# TOOL DESCRIPTION: `{i}`\n'+TOOLS.get(i) for i in TOOL_ELEMENTS])
    master_plan_prompt = MASTER_PLAN_PROMPT_TEMPLATE.format(
        available_tools=available_tools, 
        tool_descriptions=available_tools_desciption, 
        user_request=MASTER_USER_REQUEST
    )
    
    MASTER_PLAN = await stream_output(
        MESSAGES, master_plan_prompt, cancel_event, system=get_system_master_plan(), **kwargs
    )
    
    if not MASTER_PLAN or MASTER_PLAN.strip() == "[NO_CONTENT]":
        print("Failed to generate master plan.")
        return None

    if md_export or docx_export:
        filename = f"00_request_and_master_plan"
        content = f"# Title\n\n{generated_title}\n\n" if generated_title else ""
        if original_user_request == MASTER_USER_REQUEST:
            content += f"---\n\n# Request\n\n---\n\n{MASTER_USER_REQUEST}\n\n---\n\n# Master Plan\n\n---\n\n{MASTER_PLAN}"
        else:
            original_user_request = original_user_request.strip()
            content += f"---\n\n# Original Request\n\n---\n\n{original_user_request}\n\n---\n\n# Refined Request\n\n---\n\n{MASTER_USER_REQUEST}\n\n---\n\n# Master Plan\n\n---\n\n{MASTER_PLAN}"
        do_export(content, filename, md_export, docx_export, output_directory)

    PROGRESS_STATUS = "START"
    print("\n--- Finished generating study plan. Beginning rounds. ---\n")

    try:
        while PROGRESS_STATUS is None or not ("STOP" in PROGRESS_STATUS or re.sub("^[^A-Za-z]*?([A-Za-z]+?)[^A-Za-z]*?$", r"\1", PROGRESS_STATUS).upper() == "STOP"):
            if cancel_event and cancel_event.is_set():
                break

            print(f"\n### Round {ROUND} ###\n")

            # suggestion
            print("\n--- Suggestion ---\n")
            system_make_suggestion = get_system_make_suggestion(master_plan=MASTER_PLAN)
            follow_up_prompt = "Please provide me with the next step suggestion, based on the action plan."
            
            suggestion = await stream_output(MESSAGES, follow_up_prompt, cancel_event, system=system_make_suggestion, **kwargs)
            
            if not suggestion or suggestion.strip() == "[NO_CONTENT]":
                print("\n[No suggestion generated. Stopping.]\n")
                break

            # tool selection
            print("\n--- Tool Selection ---\n")
            suggested_tools = await stream_output(DEFAULT_MESSAGES, suggestion, cancel_event, system=SYSTEM_TOOL_SELECTION, **kwargs)
            
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
            tool_instruction_draft = TOOL_INSTRUCTION_PROMPT + "\n\n# Suggestions\n\n"+suggestion+f"\n\n# Tool Description of `{selected_tool}`\n\n"+selected_tool_description+TOOL_INSTRUCTION_SUFFIX
            system_tool_instruction = get_system_tool_instruction(selected_tool, selected_tool_description)
            
            user_request = await stream_output(MESSAGES, tool_instruction_draft, cancel_event, system=system_tool_instruction, **kwargs)
            
            if not user_request or user_request.strip() == "[NO_CONTENT]":
                print("\n[No tool instruction generated. Stopping.]\n")
                break

            print("\n--- Agent Execution ---\n")
            answers = None
            try:
                if selected_tool == "get_direct_text_response":
                    answers = await stream_output(MESSAGES, user_request, cancel_event, system="auto", **kwargs)
                elif selected_tool == "search_the_internet":
                    answers = await asyncio.to_thread(ollama_web_search, user_request)
                    print(answers)
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
                        system = element.pop("system") if "system" in element else None
                        answers = await stream_output(MESSAGES, user_request, cancel_event, system=system, **element, **kwargs)
                        
            except Exception as e:
                answers = f"[Error: {str(e)}]"
                print(f"\n{answers}\n")
                if developer:
                    traceback.print_exc()

            if answers and not (answers.strip() == "[NO_CONTENT]" or answers.startswith("[Error:")):
                if md_export or docx_export:
                    round_str = f"{ROUND:02}"
                    filename = f"{round_str}_{selected_tool}"
                    export_content = f"""---

{user_request}

---

{answers}

---"""
                    do_export(export_content, filename, md_export, docx_export, output_directory)
                MESSAGES += [
                    {"role": "user", "content": f"[ROUND {ROUND}]\n\n{user_request}"},
                    {"role": "assistant", "content": f"[TOOL] {selected_tool}\n\n[RESPONSE]\n\n{answers}"},
                ]

            # check progress
            print("\n--- Progress Check ---\n")
            system_progress = get_system_progress(master_plan=MASTER_PLAN)
            follow_up_prompt="Please decide either to `CONTINUE` or `STOP` the process."
            PROGRESS_STATUS = await stream_output(MESSAGES, follow_up_prompt, cancel_event, system=system_progress, **kwargs)
            
            if not PROGRESS_STATUS or PROGRESS_STATUS.strip() == "[NO_CONTENT]":
                MESSAGES = MESSAGES[:-2]
                break
                
            ROUND += 1

        print("\n---\n")
        print("\nWrapping up...\n")
        print("\n--- Final Report ---\n")
        system_report = "write_final_answer"
        follow_up_prompt=f"""{FINAL_INSTRUCTION}{MASTER_USER_REQUEST}"""
        report = await stream_output(MESSAGES, follow_up_prompt, cancel_event, system=system_report, **kwargs)

        if report and report.strip() != "[NO_CONTENT]":
            if md_export or docx_export:
                round_str = f"{ROUND:02}"
                filename = f"{round_str}_final_report"
                do_export(report, filename, md_export, docx_export, output_directory)
            MESSAGES += [
                {"role": "user", "content": "[FINAL] Please provide a comprehensive response that resolves my original request, ensuring all previously completed milestones and data points are fully integrated."},
                {"role": "assistant", "content": f"[REPORT]\n\n{report}"},
            ]
            print("\n--- Finished successfully ---\n")
            
        return MESSAGES
        
    except Exception as e:
        print(f"\nError: {e}\n")
        # traceback.print_exc()
        return None
