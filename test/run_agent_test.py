import asyncio
import os
import shutil
from biblemateagent.agent import bible_agent

async def run_test():
    test_dir = "test_agent_export"
    if os.path.isdir(test_dir):
        shutil.rmtree(test_dir)
    os.makedirs(test_dir)
    
    # We will mock agentmake to run much faster and produce predictable outputs
    # But for a quick test, we can just call bible_agent with a simple request.
    print("Testing bible_agent export...")
    await bible_agent(
        request="What is John 3:16?",
        md_export=True,
        docx_export=False,
        output_directory=test_dir,
        backend="google",
        model="gemini-1.5-flash"
    )

if __name__ == "__main__":
    asyncio.run(run_test())
