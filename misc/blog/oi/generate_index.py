from __future__ import annotations

import argparse
import html
import os
import re
from pathlib import Path

H1_RE = re.compile(r"^#\s+(.*\S)\s*$", re.MULTILINE)


def read_title(markdown_path: Path) -> str:
    text = markdown_path.read_text(encoding="utf-8")
    match = H1_RE.search(text)
    if match:
        return match.group(1).strip()
    return markdown_path.stem


def read_index_meta(content_file: Path) -> tuple[str | None, str | None]:
    if not content_file.exists():
        return None, None

    title_value: str | None = None
    quote_value: str | None = None

    for raw_line in content_file.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line:
            continue

        if line.startswith("标题："):
            value = line.split("：", 1)[1].strip()
            if value:
                title_value = value
            continue

        if line.startswith("引语：") or line.startswith("内容："):
            value = line.split("：", 1)[1].strip()
            if value:
                quote_value = value

    return title_value, quote_value


def build_index_page(title: str, quote: str | None, stylesheet_href: str, back_href: str, items_html: str) -> str:
    escaped_title = html.escape(title)
    escaped_stylesheet = html.escape(stylesheet_href, quote=True)
    escaped_back = html.escape(back_href, quote=True)
    quote_block = f"    <p class=\"index-quote\">{html.escape(quote)}</p>\n" if quote else ""
    return f"""<!DOCTYPE html>
<html lang=\"zh-CN\">
<head>
  <meta charset=\"utf-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
  <title>{escaped_title}</title>
  <link rel=\"stylesheet\" href=\"{escaped_stylesheet}\">
</head>
<body>
  <a class=\"back-link\" href=\"{escaped_back}\">返回</a>
  <main class=\"article-shell\">
    <h1>{escaped_title}</h1>
{quote_block}    <ul class=\"article-list\">
{items_html}
    </ul>
  </main>
</body>
</html>
"""


def generate_index(
    base_dir: Path,
    list_file: Path,
    src_dir: Path,
    pages_dir: Path,
    output_file: Path,
    stylesheet: Path,
    back_href: str,
    page_title: str,
    page_quote: str | None,
) -> Path:
    filenames = [line.strip() for line in list_file.read_text(encoding="utf-8").splitlines() if line.strip()]
    filenames.reverse()

    item_lines: list[str] = []
    for filename in filenames:
        source_md = src_dir / filename
        if not source_md.exists():
            raise FileNotFoundError(f"Missing source markdown file: {source_md}")

        target_html = pages_dir / f"{source_md.stem}.html"
        if not target_html.exists():
            raise FileNotFoundError(f"Missing generated article page: {target_html}")

        title = read_title(source_md)
        href = os.path.relpath(target_html, output_file.parent)
        item_lines.append(f"      <li><a href=\"{html.escape(href, quote=True)}\">{html.escape(title)}</a></li>")

    stylesheet_href = os.path.relpath(stylesheet, output_file.parent)
    page = build_index_page(page_title, page_quote, stylesheet_href, back_href, "\n".join(item_lines))
    output_file.write_text(page, encoding="utf-8")
    return output_file


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate oi index page from list.txt in reverse order.")
    parser.add_argument("--base-dir", default=".", help="Base directory containing list.txt, src, pages, and repo-global misc.css.")
    parser.add_argument("--list-file", default="list.txt", help="File listing markdown filenames in original order.")
    parser.add_argument("--src-dir", default="src", help="Markdown source directory.")
    parser.add_argument("--pages-dir", default="pages", help="Generated article pages directory.")
    parser.add_argument("--output", default="index.html", help="Output index html file.")
    parser.add_argument("--stylesheet", default="../../../static/css/misc.css", help="Stylesheet path used by index.html.")
    parser.add_argument("--back-href", default="../../index.html", help="Back button target URL.")
    parser.add_argument("--content-file", default="content.txt", help="Meta file for index title and quote.")
    parser.add_argument("--title", default="OI Articles", help="Index page title and H1 text.")
    parser.add_argument("--quote", default="", help="Index quote text. If empty, read from content file.")
    args = parser.parse_args()

    base_dir = Path(args.base_dir).resolve()
    output_file = (base_dir / args.output).resolve()
    content_file = (base_dir / args.content_file).resolve()

    file_title, file_quote = read_index_meta(content_file)
    final_title = file_title or args.title
    final_quote = args.quote.strip() or file_quote

    generated = generate_index(
        base_dir=base_dir,
        list_file=(base_dir / args.list_file).resolve(),
        src_dir=(base_dir / args.src_dir).resolve(),
        pages_dir=(base_dir / args.pages_dir).resolve(),
        output_file=output_file,
        stylesheet=(base_dir / args.stylesheet).resolve(),
        back_href=args.back_href,
        page_title=final_title,
        page_quote=final_quote,
    )
    print(f"Generated index: {generated}")


if __name__ == "__main__":
    main()
