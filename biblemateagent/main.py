import asyncio, argparse
from agentmake import SUPPORTED_AI_BACKENDS, DEFAULT_AI_BACKEND
from biblemateagent.agent import bible_agent

parser = argparse.ArgumentParser(description = f"""BibleMate AI Agent""")
parser.add_argument("default", nargs="*", default=None, help="user request")
parser.add_argument("-l", "--language", action="store", dest="language", choices=["eng", "tc", "sc"], help="language option")
parser.add_argument("-b", "--backend", action="store", dest="backend", choices=SUPPORTED_AI_BACKENDS, help="AI backend option")
parser.add_argument("-m", "--model", action="store", dest="model", help="AI model option")
parser.add_argument("-k", "--api_key", action="store", dest="api_key", help="API key option")
parser.add_argument("-e", "--api_endpoint", action="store", dest="api_endpoint", help="API endpoint option")
parser.add_argument("-mt", "--max_tokens", action="store", dest="max_tokens", type=int, help="max tokens option")
parser.add_argument("-cw", "--context_window", action="store", dest="context_window", type=int, help="context window option")
parser.add_argument("-t", "--temperature", action="store", dest="temperature", type=float, help="temperature option")
parser.add_argument("-p", "--improve_prompt", action="store_true", dest="improve_prompt", help="improve user prompt")
parser.add_argument("-d", "--developer", action="store_true", dest="developer", help="developer mode")
parser.add_argument("-md", "--md_export", action="store_true", dest="md_export", help="export outputs in markdown format")
parser.add_argument("-docx", "--docx_export", action="store_true", dest="docx_export", help="export outputs in docx format")
parser.add_argument("-o", "--output_directory", action="store", dest="output_directory", help="output directory")
args = parser.parse_args()

async def main_async():
    print("Starting BibleMate AI Agent...")
    kwargs = {}
    kwargs["backend"] = args.backend if args.backend else DEFAULT_AI_BACKEND
    kwargs["model"] = args.model if args.model else None
    kwargs["api_key"] = args.api_key if args.api_key else None
    kwargs["api_endpoint"] = args.api_endpoint if args.api_endpoint else None
    kwargs["max_tokens"] = args.max_tokens if args.max_tokens else None
    kwargs["context_window"] = args.context_window if args.context_window else None
    kwargs["temperature"] = args.temperature if args.temperature else None
    
    await bible_agent(
        request=" ".join(args.default),
        language=args.language if args.language else "eng",
        improve_prompt=args.improve_prompt if args.improve_prompt else False,
        md_export=args.md_export if args.md_export else False,
        docx_export=args.docx_export if args.docx_export else False,
        output_directory=args.output_directory if args.output_directory else "",
        developer=args.developer if args.developer else False,
        **kwargs,
    )
    print("Finished")

def main():
    asyncio.run(main_async())

if __name__ == "__main__":
    main()
