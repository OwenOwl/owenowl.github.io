#!/usr/bin/env python3

from pathlib import Path
import html
import re
import sys
import os


def parse_content_file(raw_text: str):
    raw_lines = raw_text.splitlines()
    meta = {
        "game_name": "",
        "tab_title": "",
        "page_title": "",
        "subtitle": "",
    }
    chapters = []
    sections = []
    current_chapter = None
    current_level = None

    i = 0
    while i < len(raw_lines):
        raw_line = raw_lines[i]
        line = raw_line.strip()
        if not line:
            i += 1
            continue

        chapter_match = re.match(r"^章节[:：]\s*(.+)$", line)
        if chapter_match:
            current_chapter = {
                "name": chapter_match.group(1),
                "intro": "",
                "levels": [],
            }
            chapters.append(current_chapter)
            sections.append({"type": "chapter", "chapter": current_chapter})
            current_level = None
            i += 1
            continue

        bullet_match = re.match(r"^[-*•]\s*(.+)$", line)
        if bullet_match and current_chapter is not None:
            current_level = {
                "name": bullet_match.group(1),
                "best": {},
                "metric_notes": {},
                "general_notes": [],
            }
            current_chapter["levels"].append(current_level)
            i += 1
            continue

        kv_match = re.match(r"^(游戏名|标签页|标题|内容)[:：]\s*(.*)$", line)
        if kv_match:
            key = kv_match.group(1)
            value = kv_match.group(2)

            # Support multiline content by consuming following lines with 4-space indentation.
            if key == "内容":
                continuation_lines = []
                j = i + 1
                while j < len(raw_lines):
                    next_raw = raw_lines[j]
                    if next_raw.startswith("    ") and next_raw.strip():
                        continuation_lines.append(next_raw[4:])
                        j += 1
                        continue
                    break
                if continuation_lines:
                    value = value + "\n" + "\n".join(continuation_lines)
                i = j - 1

            if key == "内容" and current_chapter is None:
                meta["subtitle"] = value
            elif key == "内容" and current_chapter is not None and current_level is None and not current_chapter["intro"] and len(current_chapter["levels"]) == 0:
                current_chapter["intro"] = value
            elif key == "内容" and current_chapter is not None and len(current_chapter["levels"]) > 0:
                # Standalone content block between chapters.
                sections.append({"type": "interlude", "text": value})
            else:
                key_map = {
                    "游戏名": "game_name",
                    "标签页": "tab_title",
                    "标题": "page_title",
                    "内容": "subtitle",
                }
                if key in key_map:
                    meta[key_map[key]] = value
            i += 1
            continue

        if current_level is None:
            i += 1
            continue

        gca_match = re.match(r"^(\d+)\s*/\s*(\d+)\s*/\s*(\d+)$", line)
        if gca_match:
            current_level["best"] = {
                "费用": gca_match.group(1),
                "周期": gca_match.group(2),
                "区域": gca_match.group(3),
            }
            i += 1
            continue

        metric_note_match = re.match(r"^(费用|周期|区域)[:：]\s*(.+)$", line)
        if metric_note_match:
            current_level["metric_notes"][metric_note_match.group(1)] = metric_note_match.group(2)
            i += 1
            continue

        current_level["general_notes"].append(line)
        i += 1

    return meta, chapters, sections


def html_with_breaks(text: str) -> str:
    return html.escape(text).replace("\n", "<br />")


def build_gif_index(gif_dir: Path) -> dict:
    """Returns {level_name: [(cost, cycle, area, filename), ...]}"""
    pattern = re.compile(
        r"^Opus Magnum - (.+) \((\d+)G, (\d+), (\d+), .+\)\.gif$"
    )
    index: dict = {}
    if not gif_dir.is_dir():
        return index
    for f in gif_dir.iterdir():
        m = pattern.match(f.name)
        if not m:
            continue
        level_name = m.group(1)
        entry = (int(m.group(2)), int(m.group(3)), int(m.group(4)), f.name)
        index.setdefault(level_name, []).append(entry)
    return index


_METRIC_IDX = {"费用": 0, "周期": 1, "区域": 2}


def find_gif(gif_index: dict, level_name: str, metric_name: str, best_value: str) -> str:
    """Return relative path to gif, or empty string if not found."""
    if not best_value or metric_name not in _METRIC_IDX:
        return ""
    candidates = gif_index.get(level_name, [])
    idx = _METRIC_IDX[metric_name]
    target = int(best_value)
    matches = [entry for entry in candidates if entry[idx] == target]
    if not matches:
        return ""
    return f"./gif/{matches[0][3]}"


def render_metric_card(
    metric_name: str, best_value: str, metric_note: str, gif_path: str
) -> str:
    best_badge = f'<span class="metric-best">{html.escape(best_value)}</span>' if best_value else ""
    note_block = f'<p class="metric-note">{html.escape(metric_note)}</p>' if metric_note else ""
    if gif_path:
        # quote spaces and special chars in URL
        import urllib.parse
        encoded = urllib.parse.quote(gif_path, safe="./")
        slot_content = f'<img src="{encoded}" alt="{html.escape(metric_name)} GIF" loading="lazy" />'
    else:
        slot_content = "未解决"

    return f"""
                <article class="metric-card">
                  <div class="metric-head">
                    <h3>{html.escape(metric_name)}</h3>
                    {best_badge}
                  </div>
                  <div class="gif-slot">{slot_content}</div>
                  {note_block}
                </article>"""


def render_level(level: dict, gif_index: dict) -> str:
    safe_level_name = html.escape(level["name"])
    metrics = ["费用", "周期", "区域"]
    cards = []
    for metric in metrics:
        best_value = level["best"].get(metric, "")
        if best_value == "0":
            continue
        cards.append(
            render_metric_card(
                metric_name=metric,
                best_value=best_value,
                metric_note=level["metric_notes"].get(metric, ""),
                gif_path=find_gif(gif_index, level["name"], metric, best_value),
            )
        )

    general_note_block = ""
    if level["general_notes"]:
        joined_notes = "<br />".join(html.escape(note) for note in level["general_notes"])
        general_note_block = f'\n              <p class="level-note">{joined_notes}</p>'

    return f"""
                        <section class=\"level\">
                            <h3 class=\"level-title\">{safe_level_name}</h3>
              <div class=\"metric-stack\">
{"".join(cards)}
              </div>
{general_note_block}
                        </section>"""


def render_chapter(chapter: dict, gif_index: dict) -> str:
    safe_title = html.escape(chapter["name"])
    level_blocks = "\n".join(render_level(level, gif_index) for level in chapter["levels"])
    intro_block = ""
    if chapter.get("intro"):
        intro_block = f'\n          <p class="chapter-intro">{html_with_breaks(chapter["intro"])}</p>'

    return f"""
        <details class="chapter">
          <summary>{safe_title}</summary>
          <div class="level-list">
{intro_block}
{level_blocks}
          </div>
        </details>"""


def render_interlude(text: str) -> str:
    return f"""
        <section class=\"interlude-box\">
          <p class=\"interlude-text\">{html_with_breaks(text)}</p>
        </section>"""


def build_html(meta: dict, sections, gif_index: dict, stylesheet_href: str, back_href: str) -> str:
    rendered_sections = []
    for item in sections:
        if item["type"] == "chapter":
            rendered_sections.append(render_chapter(item["chapter"], gif_index))
        elif item["type"] == "interlude":
            rendered_sections.append(render_interlude(item["text"]))
    chapter_blocks = "\n".join(rendered_sections)
    safe_game_name = html.escape(meta["game_name"])
    safe_tab_title = html.escape(meta["tab_title"])
    safe_page_title = html.escape(meta["page_title"])
    safe_subtitle = html_with_breaks(meta["subtitle"])
    safe_stylesheet = html.escape(stylesheet_href, quote=True)
    safe_back_href = html.escape(back_href, quote=True)
    return f"""<!doctype html>
<html lang=\"zh-CN\">
  <head>
    <meta charset=\"UTF-8\" />
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />
    <title>{safe_tab_title}</title>
    <link rel=\"stylesheet\" href=\"{safe_stylesheet}\" />
  </head>
  <body>
        <a class=\"back-link\" href=\"{safe_back_href}\">返回</a>
    <div class=\"page-bg\"></div>
    <main class=\"opus-wrap\">
      <header class=\"page-head\">
        <p class=\"kicker\">{safe_game_name}</p>
        <h1>{safe_page_title}</h1>
        <p class=\"subtitle\">{safe_subtitle}</p>
      </header>

      <section class=\"chapter-list\">
{chapter_blocks}
      </section>
    </main>
  </body>
</html>
"""


def main():
    base_dir = Path(__file__).resolve().parent
    input_path = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else base_dir / "content.txt"
    output_path = Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else base_dir / "index.html"
    stylesheet_path = Path(sys.argv[3]).resolve() if len(sys.argv) > 3 else (base_dir / "../../../static/css/misc.css").resolve()
    back_href = sys.argv[4] if len(sys.argv) > 4 else "../../index.html"

    if not input_path.exists():
        raise FileNotFoundError(f"未找到输入文件: {input_path}")

    raw = input_path.read_text(encoding="utf-8")
    meta, chapters, sections = parse_content_file(raw)
    gif_index = build_gif_index(base_dir / "gif")

    missing_meta = [key for key, value in meta.items() if not value]
    if missing_meta:
        key_cn = {
            "game_name": "游戏名",
            "tab_title": "标签页",
            "page_title": "标题",
            "subtitle": "内容",
        }
        missing_text = "、".join(key_cn[key] for key in missing_meta)
        raise ValueError(f"content.txt 缺少字段: {missing_text}")

    if not chapters:
        raise ValueError("content.txt 中没有解析到章节，请检查格式。")

    if any(len(ch["levels"]) == 0 for ch in chapters):
        raise ValueError("存在没有关卡名的章节，请检查 content.txt 中每章的关卡列表。")

    stylesheet_href = os.path.relpath(stylesheet_path, output_path.parent)
    output_path.write_text(build_html(meta, sections, gif_index, stylesheet_href, back_href), encoding="utf-8")
    print(f"已生成: {output_path}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
