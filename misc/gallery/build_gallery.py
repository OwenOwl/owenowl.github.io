#!/usr/bin/env python3
"""Build gallery-data.js from src/<activity>/index.md and numbered images."""
from __future__ import annotations
import html, json, re
from datetime import date
from pathlib import Path

ROOT=Path(__file__).resolve().parent
SOURCE=ROOT/"src"
OUTPUT=ROOT/"gallery-data.js"
IMAGE_SUFFIXES={".jpg",".jpeg",".png",".webp",".gif",".avif"}

def read_entry(path):
    text=path.read_text(encoding="utf-8")
    match=re.match(r"^---\s*\n(.*?)\n---\s*(?:\n|$)(.*)$",text,re.S)
    if not match: raise ValueError(f"{path}: 缺少 YAML 风格的头部信息")
    meta={}
    for line in match.group(1).splitlines():
        if not line.strip() or line.lstrip().startswith("#"): continue
        key,sep,value=line.partition(":")
        if not sep: raise ValueError(f"{path}: 无法解析头部行 {line!r}")
        meta[key.strip()]=value.strip().strip('"\'')
    missing={"title","date","category"}-meta.keys()
    if missing: raise ValueError(f"{path}: 缺少字段 {', '.join(sorted(missing))}")
    date.fromisoformat(meta["date"])
    if meta.get("date_end"): date.fromisoformat(meta["date_end"])
    return meta,match.group(2).strip()

def markdown_to_html(source):
    if not source: return ""
    blocks,paragraph=[],[]
    def flush():
        if paragraph: blocks.append(f"<p>{'<br>'.join(paragraph)}</p>"); paragraph.clear()
    for raw in source.splitlines():
        line=html.escape(raw.strip())
        if not line: flush()
        elif line.startswith("### "): flush(); blocks.append(f"<h4>{line[4:]}</h4>")
        elif line.startswith("## "): flush(); blocks.append(f"<h3>{line[3:]}</h3>")
        elif line.startswith("# "): flush(); blocks.append(f"<h3>{line[2:]}</h3>")
        else: paragraph.append(line)
    flush(); return "\n".join(blocks)

def make_excerpt(source,length=54):
    plain=re.sub(r"[#*_>`~\[\]()]","",source)
    plain=re.sub(r"\s+"," ",plain).strip()
    return plain if len(plain)<=length else plain[:length].rstrip()+"…"

def image_number(path):
    if not path.stem.isdigit(): raise ValueError(f"{path}: 图片必须命名为 1、2、3……")
    return int(path.stem)

def build():
    entries=[]
    for md_path in sorted(SOURCE.glob("*/index.md")):
        meta,body=read_entry(md_path)
        images=sorted((p for p in md_path.parent.iterdir() if p.suffix.lower() in IMAGE_SUFFIXES),key=image_number)
        if len(images)!=1 or image_number(images[0])!=1: raise ValueError(f"{md_path.parent}: 必须且只能包含一张命名为 1 的图片")
        entries.append({"title":meta["title"],"date":meta["date"],"dateDisplay":meta.get("date_display",meta["date"]),"category":meta["category"],"excerpt":make_excerpt(body),"contentHtml":markdown_to_html(body),"image":f"./{images[0].relative_to(ROOT).as_posix()}","_sort":meta.get("date_end",meta["date"])})
    entries.sort(key=lambda x:(x["_sort"],x["date"]),reverse=True)
    for entry in entries: del entry["_sort"]
    payload=json.dumps(entries,ensure_ascii=False,indent=2)
    OUTPUT.write_text(f"// 由 build_gallery.py 自动生成，请勿手动编辑。\nwindow.GALLERY_DATA = {payload};\n",encoding="utf-8")
    print(f"Built {len(entries)} entries -> {OUTPUT.relative_to(ROOT)}")

if __name__=="__main__": build()
