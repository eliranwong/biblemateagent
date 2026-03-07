# Create a minimal script to test `do_export`
import os
import re

def do_export(content, filename, md_export=True, docx_export=False, output_directory=None):
    filename = re.sub(r"[^a-zA-Z0-9_\u4e00-\u9fff]+", "_", filename)
    if not os.path.isdir(output_directory):
        os.makedirs(output_directory)
    if md_export:
        md_filepath = os.path.join(output_directory, f"{filename}.md")
        with open(md_filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"\n\n---\n\nExported to: {md_filepath}\n\n---\n")

do_export("test", "01_test", True, False, "test_output")
