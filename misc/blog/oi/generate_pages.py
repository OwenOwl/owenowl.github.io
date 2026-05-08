from __future__ import annotations

import argparse
import html
import os
from pathlib import Path


def render_markdown(markdown_text: str) -> tuple[str, str]:
    lines = markdown_text.splitlines()
    blocks: list[str] = []
    paragraph_lines: list[str] = []
    page_title = "Untitled"

    def flush_paragraph() -> None:
        if not paragraph_lines:
            return
        paragraph = " ".join(line.strip() for line in paragraph_lines)
        blocks.append(f"<p>{html.escape(paragraph)}</p>")
        paragraph_lines.clear()

    for raw_line in lines:
        stripped = raw_line.strip()
        if not stripped:
            flush_paragraph()
            continue

        heading_marks, _, heading_text = stripped.partition(" ")
        if heading_marks and set(heading_marks) == {"#"} and 1 <= len(heading_marks) <= 6 and heading_text:
            flush_paragraph()
            escaped_text = html.escape(heading_text.strip())
            level = len(heading_marks)
            blocks.append(f"<h{level}>{escaped_text}</h{level}>")
            if level == 1 and page_title == "Untitled":
                page_title = heading_text.strip()
            continue

        paragraph_lines.append(raw_line)

    flush_paragraph()
    return page_title, "\n".join(blocks)


def build_page(title: str, body: str, stylesheet_href: str, back_href: str) -> str:
    escaped_title = html.escape(title)
    return f"""<!DOCTYPE html>
<html lang=\"zh-CN\">
<head>
  <meta charset=\"utf-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
  <title>{escaped_title}</title>
    <link rel=\"stylesheet\" href=\"{html.escape(stylesheet_href, quote=True)}\">
</head>
<body>
<a class=\"back-link\" href=\"{html.escape(back_href, quote=True)}\">返回</a>
<main class=\"article-shell\">\n{body}\n</main>
</body>
</html>
"""


def generate_pages(base_dir: Path, list_file: Path, src_dir: Path, output_dir: Path, stylesheet: Path) -> list[Path]:
    filenames = [line.strip() for line in list_file.read_text(encoding="utf-8").splitlines() if line.strip()]
    output_dir.mkdir(parents=True, exist_ok=True)
    stylesheet_path = stylesheet.resolve()
    index_path = (base_dir / "index.html").resolve()

    written_files: list[Path] = []
    for filename in filenames:
        source_path = src_dir / filename
        if not source_path.exists():
            raise FileNotFoundError(f"Missing source markdown file: {source_path}")

        title, body = render_markdown(source_path.read_text(encoding="utf-8"))
        output_path = output_dir / f"{source_path.stem}.html"
        stylesheet_href = os.path.relpath(stylesheet_path, output_path.parent)
        back_href = os.path.relpath(index_path, output_path.parent)
        output_path.write_text(build_page(title, body, stylesheet_href, back_href), encoding="utf-8")
        written_files.append(output_path)

    return written_files


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate HTML pages from listed Markdown files.")
    parser.add_argument("--base-dir", default=".", help="Base directory containing list.txt, src, and pages.")
    parser.add_argument("--list-file", default="list.txt", help="File listing Markdown filenames in order.")
    parser.add_argument("--src-dir", default="src", help="Directory containing Markdown source files.")
    parser.add_argument("--output-dir", default="pages", help="Directory to write generated HTML files.")
    parser.add_argument("--stylesheet", default="../../../static/css/misc.css", help="Stylesheet path used by generated pages.")
    args = parser.parse_args()

    base_dir = Path(args.base_dir).resolve()
    list_file = (base_dir / args.list_file).resolve()
    src_dir = (base_dir / args.src_dir).resolve()
    output_dir = (base_dir / args.output_dir).resolve()
    stylesheet = (base_dir / args.stylesheet).resolve()

    written_files = generate_pages(base_dir, list_file, src_dir, output_dir, stylesheet)
    print(f"Generated {len(written_files)} HTML files:")
    for path in written_files:
        print(path.name)


if __name__ == "__main__":
    main()