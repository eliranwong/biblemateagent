import re
import os
import shutil
import pydoc

def do_export(content, filename, md_export=True, docx_export=False, output_directory=None):

    # sanitize filename, but accept chinese characters
    filename = re.sub(r"[^a-zA-Z0-9_\u4e00-\u9fff]+", "_", filename)

    if not os.path.isdir(output_directory):
        os.makedirs(output_directory)
    
    if md_export:
        md_filepath = os.path.join(output_directory, f"{filename}.md")
        try:
            with open(md_filepath, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"\n\n---\n\nExported to: {md_filepath}\n\n---\n")
        except Exception as e:
            print(f"Error exporting to MD: {e}")
    
    if docx_export:
        if not shutil.which("pandoc"):
            print("Pandoc is not installed. Skipping DOCX export.")
            return
        try:
            docx_filepath = os.path.join(output_directory, f"{filename}.docx")
            docx_filepath.replace('"', "_")
            pydoc.pipepager(content, cmd=f'''pandoc -f markdown -t docx -o "{docx_filepath}"''')
            print(f"\n\n---\n\nExported to: {docx_filepath}\n\n---\n")
        except Exception as e:
            print(f"Error exporting to DOCX: {e}")