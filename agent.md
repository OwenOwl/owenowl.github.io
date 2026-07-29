# Agent Handoff Notes

This file is for future coding agents working in this repository. It summarizes the repo state and workflows so a new turn does not need to reread every file from scratch.

## Repo Shape

This is a static GitHub Pages personal site. There is no package manager, build system, or app framework at the repo root. Most pages can be opened directly in a browser.

Important top-level paths:

- `index.html`: main personal homepage for Lixing Fang.
- `static/`: root homepage and misc shared CSS/JS/images.
- `misc/index.html`: miscellaneous hub page linking to Opus Magnum, OI articles, and Gallery.
- `misc/blog/oi/`: Chinese OI travelogue/blog source and generated pages.
- `misc/game/opus/`: Opus Magnum optimal-solution showcase with GIFs and generated index.
- `misc/gallery/index.html`: hand-authored gallery page with embedded CSS/JS and photo metadata.
- `extremcontrol/`: sub-repository/submodule boundary. Treat it as an external repo and do not rely on or summarize its internal files from this root-repo handoff.

The root repo is asset-heavy. Large root-owned binaries are mainly `misc/game/opus/gif/*.gif` and images under `static/images` and `misc/gallery/src`. Sub-repositories may contain their own assets, but treat those folders as external/empty unless the user explicitly asks to work inside them.

## Current Content

Main homepage (`index.html`):

- Personal bio for Lixing Fang, 2nd-year Ph.D. student at UMass Amherst CICS, supervised by Chuang Gan.
- Research focus: human motion and humanoid robots.
- Publications listed: SPOT, ExtremControl, Virtual Community, CFC, unbounded soft environments, CAMS.
- Experience: Genesis AI intern in 2026, UCSD research intern in 2023, Shanghai Qi Zhi Institute intern in 2022.
- Education: UMass Amherst PhD, Tsinghua IIIS/Yao Class bachelor.
- Teaching: COMPSCI 230 TA in Fall 2024, Summer 2025, Fall 2025.
- Uses Bulma plus `static/css/index.css`; imports jQuery, Bulma carousel/slider, FontAwesome, Academicons.

Root styling/scripts:

- `static/css/index.css`: clean white/light-blue card style for the homepage. It overrides Bulma sections into bordered card-like blocks. Uses CSS variables `--bg`, `--ink`, `--muted`, `--line`, `--panel`, `--accent`, `--shadow`.
- `static/js/index.js`: leftover NeRFies-style carousel/interpolation helper. It preloads `./static/interpolation/stacked/*.jpg`, but that directory is not present in the repo. The homepage currently does not appear to use those interpolation elements.
- `static/css/misc.css`: shared style for misc pages, OI generated pages, and Opus page. Contains `.back-link`, `.article-shell`, `.article-list`, `.index-quote`, `.opus-wrap`, `.page-head`, `.chapter`, `.metric-card`, `.gif-slot`, and mobile media queries.

Misc hub (`misc/index.html`):

- Chinese-language page titled `Miscellaneous`.
- Links to `./game/opus/index.html`, `./blog/oi/index.html`, and `./gallery/index.html`.
- Has three placeholder cards with empty titles and `href="#"`.
- Inline styles rely on variables from `../static/css/misc.css`.

Gallery (`misc/gallery/index.html`):

- Self-contained page with inline CSS and JS.
- Uses `../../static/css/misc.css` for shared variables/back button.
- Data is in the embedded `galleryData` array. Categories are `Baseball`, `HIMEHINA`, and `Live`.
- Images live in `misc/gallery/src/*.jpg`.
- It implements category tabs, left/right navigation buttons, arrow-key navigation, animated image transitions, captions, and SVG placeholder generation when an activity has no `image`.
- To add an entry, edit `galleryData` and add the photo under `misc/gallery/src`.

OI blog (`misc/blog/oi/`):

- Source of truth is `src/*.md`, `list.txt`, `content.txt`, and the generator scripts.
- Generated outputs are `pages/*.html` and `index.html`.
- `list.txt` stores markdown filenames in original order. `generate_index.py` reverses this order so newest/last-listed appears first.
- `content.txt` currently contains:
  - `标题：OI 游记`
  - `内容：高中时期写下的文字。`
- Markdown renderer in `generate_pages.py` is intentionally minimal:
  - headings beginning with `#` through `######` become headings
  - blank lines split paragraphs
  - paragraph text is HTML-escaped
  - no lists, links, code blocks, images, or Markdown extensions are supported
- Blog titles currently present: NOIP 2017, THUWC 2018, SCOI 2018, CTSC/APIO 2018, THUSC 2018, NOI 2018, NOIP 2018, WC 2019, SCOI 2019, THUPC 2019, CTS 2019, APIO 2019, NOI 2019, 4th Metropolis, PKU 2019.

OI generation commands, from `misc/blog/oi`:

```sh
python generate_pages.py
python generate_index.py
```

Opus Magnum (`misc/game/opus/`):

- Source of truth is `content.txt`, `generate_index.py`, and GIF filenames under `gif/`.
- Generated output is `index.html`.
- `content.txt` uses Chinese labels and a strict custom format:
  - metadata: `游戏名：`, `标签页：`, `标题：`, `内容：`
  - chapters: `章节：...`
  - levels: `- level name`
  - best metrics line: `cost/cycles/area`
  - optional metric notes: `费用：`, `周期：`, `区域：`
  - indented continuation lines after `内容：` are supported.
- GIF names are parsed with this exact pattern:
  - `Opus Magnum - LEVEL_NAME (COSTG, CYCLES, AREA, TIMESTAMP).gif`
- A GIF is matched to a metric card when its level name and selected best value match the content file. Missing GIFs render as `未解决`.
- Metrics are Chinese: `费用`, `周期`, `区域`; any best metric value of `0` is skipped.

Opus generation command, from `misc/game/opus`:

```sh
python generate_index.py
```

Sub-repositories:

- `extremcontrol/` is declared in `.gitmodules` as a submodule. For root-repo work, treat it as an external empty folder. Do not inspect, summarize, validate, or edit inside it unless the user explicitly scopes the task to that sub-repository.

## File/Asset Conventions

- Keep generated files in sync when editing OI Markdown/content or Opus content.
- Preserve Chinese text encoding as UTF-8.
- Asset paths are relative and are meant for static hosting; avoid root-relative paths unless the existing page already uses them.
- The repo contains `.DS_Store` files in several folders despite `.gitignore` ignoring `.DS_Store`.
- `.vscode/settings.json` is ignored by `.gitignore` but exists locally with Python conda defaults.
- `.gitignore` ignores `.DS_Store` and `.vscode`.

## Validation

There are no automated tests. Practical validation is:

- For root/misc pages: open the relevant HTML file directly in a browser.
- For generated OI pages: run both OI generator commands and inspect `misc/blog/oi/index.html` plus one generated `pages/*.html`.
- For Opus: run its generator and inspect `misc/game/opus/index.html`; confirm GIF filenames still match parsed metric values.
- For sub-repositories: no root-repo validation is expected. Validate them only when the user explicitly asks to work inside one.

## Agent Notes

- Use `rg --files` for inventory. Avoid reading binary assets byte-for-byte; inventory them by path/name/size unless image/video inspection is directly relevant.
- Prefer editing source files over generated outputs when a generator exists:
  - OI article body: edit `misc/blog/oi/src/*.md`, then regenerate pages and index.
  - OI ordering/title/quote: edit `list.txt` or `content.txt`, then regenerate index.
  - Opus data: edit `misc/game/opus/content.txt` or add/rename GIFs, then regenerate `index.html`.
- The site currently has no dependency install step.
- Be careful with sub-repository boundaries. Changes inside them are not ordinary root-repo file updates.
