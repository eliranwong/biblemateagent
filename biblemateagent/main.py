import asyncio, argparse, sys, os
from agentmake import SUPPORTED_AI_BACKENDS, DEFAULT_AI_BACKEND
from biblemateagent import TOOLS, TOOL_ELEMENTS
from biblemateagent.agent import bible_agent
from biblemateagent.tool import run_single_tool


parser = argparse.ArgumentParser(description = f"""BibleMate AI Agent""")
parser.add_argument("default", nargs="*", default=None, help="user request")
parser.add_argument("-p", "--prompt_refinement", action="store_true", dest="prompt_refinement", help="refine user request")
parser.add_argument("-l", "--language", action="store", dest="language", choices=["eng", "tc", "sc"], help="language option")
parser.add_argument("-b", "--backend", action="store", dest="backend", choices=SUPPORTED_AI_BACKENDS, help="AI backend option")
parser.add_argument("-m", "--model", action="store", dest="model", help="AI model option")
parser.add_argument("-k", "--api_key", action="store", dest="api_key", help="API key option")
parser.add_argument("-e", "--api_endpoint", action="store", dest="api_endpoint", help="API endpoint option")
parser.add_argument("-mt", "--max_tokens", action="store", dest="max_tokens", type=int, help="max tokens option")
parser.add_argument("-cw", "--context_window", action="store", dest="context_window", type=int, help="context window option")
parser.add_argument("-tp", "--temperature", action="store", dest="temperature", type=float, help="temperature option")
parser.add_argument("-tk", "--think", action="store", dest="think", choices=["low", "medium", "high"], help="think option")
parser.add_argument("-t", "--tool", action="store", dest="tool", choices=["auto", "get_direct_text_response"]+list(TOOL_ELEMENTS.keys()), help="run a single tool instead of orchestrating multiple tools; specify a specific tool or 'auto' to let the agent choose")
parser.add_argument("-td", "--tool_description", action="store_true", dest="tool_description", help="show tool description only; no execution")
parser.add_argument("-md", "--md_export", action="store_true", dest="md_export", help="export outputs in markdown format")
parser.add_argument("-docx", "--docx_export", action="store_true", dest="docx_export", help="export outputs in docx format")
parser.add_argument("-o", "--output_directory", action="store", dest="output_directory", help="output directory")
parser.add_argument("-d", "--developer", action="store_true", dest="developer", help="enable developer mode")
args = parser.parse_args()

async def main_async():

    if args.tool_description:
        print(f"\n[Tool: auto]\n")
        print("Let the BibleMate AI agent automatically select the appropriate tool for each request")
        print(f"\n[Tool: get_direct_text_response]\n")
        print("Receive a direct text response from the AI model")
        for tool in TOOL_ELEMENTS:
            print(f"\n[Tool: {tool}]\n")
            print(TOOLS.get(tool, "No description!"))
        print("\n")
        return

    print("Starting BibleMate AI Agent...")
    kwargs = {}
    kwargs["backend"] = args.backend if args.backend else DEFAULT_AI_BACKEND
    kwargs["model"] = args.model if args.model else None
    kwargs["api_key"] = args.api_key if args.api_key else None
    kwargs["api_endpoint"] = args.api_endpoint if args.api_endpoint else None
    kwargs["max_tokens"] = args.max_tokens if args.max_tokens else None
    kwargs["context_window"] = args.context_window if args.context_window else None
    kwargs["temperature"] = args.temperature if args.temperature else None
    if args.think:
        kwargs["think"] = args.think
    
    user_requests = []
    if args.default is not None:
        user_requests.append(" ".join(args.default))
    stdin_text = sys.stdin.read() if not sys.stdin.isatty() else ""
    if stdin_text:
        user_requests.append(stdin_text.strip())
    # user request
    user_request = "\n\n".join(user_requests) if user_requests else ""
    
    if args.tool:
        await run_single_tool(
            selected_tool=args.tool,
            request=user_request,
            language=args.language if args.language else "eng",
            prompt_refinement=args.prompt_refinement if args.prompt_refinement else False,
            md_export=args.md_export if args.md_export else False,
            docx_export=args.docx_export if args.docx_export else False,
            output_directory=args.output_directory if args.output_directory else "",
            developer=args.developer if args.developer else False,
            **kwargs
        )
    else:
        await bible_agent(
            request=user_request,
            language=args.language if args.language else "eng",
            prompt_refinement=args.prompt_refinement if args.prompt_refinement else False,
            md_export=args.md_export if args.md_export else False,
            docx_export=args.docx_export if args.docx_export else False,
            output_directory=args.output_directory if args.output_directory else "",
            developer=args.developer if args.developer else False,
            **kwargs,
        )
    print("\n--- Finished ---")

def main():
    asyncio.run(main_async())

if __name__ == "__main__":
    main()
