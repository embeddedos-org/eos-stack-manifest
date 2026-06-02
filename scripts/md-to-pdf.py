#!/usr/bin/env python3
"""Convert a Markdown file to PDF using weasyprint, with fallback to .md copy."""
import sys
import os
import shutil

def convert(md_path, out_path):
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    try:
        import markdown
        import weasyprint
        with open(md_path) as f:
            md = f.read()
        css = """
        body { font-family: sans-serif; margin: 2cm; line-height: 1.6; }
        h1, h2, h3 { color: #1a1a2e; }
        table { border-collapse: collapse; width: 100%; margin: 1em 0; }
        td, th { border: 1px solid #ccc; padding: 8px; text-align: left; }
        th { background: #f4f4f4; }
        code { background: #f0f0f0; padding: 2px 4px; border-radius: 3px; font-family: monospace; }
        pre { background: #f0f0f0; padding: 1em; border-radius: 4px; overflow-x: auto; }
        """
        html = f"""<!DOCTYPE html>
<html><head>
<meta charset="utf-8">
<style>{css}</style>
</head><body>
{markdown.markdown(md, extensions=['tables', 'fenced_code', 'toc'])}
</body></html>"""
        weasyprint.HTML(string=html).write_pdf(out_path)
        print(f"PDF generated: {out_path}")
    except ImportError as e:
        # Fallback: copy markdown
        fallback = out_path.replace(".pdf", ".md")
        shutil.copy(md_path, fallback)
        print(f"Fallback (missing {e.name}): copied to {fallback}")
    except Exception as e:
        fallback = out_path.replace(".pdf", ".md")
        shutil.copy(md_path, fallback)
        print(f"Fallback ({e}): copied to {fallback}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: md-to-pdf.py <input.md> <output.pdf>")
        sys.exit(1)
    convert(sys.argv[1], sys.argv[2])
