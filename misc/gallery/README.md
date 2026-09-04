# Gallery 内容维护

页面使用按日期倒序的瀑布流展示活动。右上角的分类 checkbox 可以组合筛选 Baseball、HIMEHINA 和 Live；点击磁贴会打开单图详情，长正文可以独立滚动。页面本身不保存活动资料，所有内容均由本目录下的构建脚本从 `src` 生成。

每个活动对应 `src` 下的一个文件夹：

```text
src/2026-07-25-offkai-expo/
├── index.md
└── 1.jpg
```

每个活动必须且只能包含一张名为 `1` 的图片，扩展名可以是 jpg、jpeg、png、webp、gif 或 avif。`index.md` 的格式如下：

```md
---
title: 活动标题
date: 2026-07-25
category: Live
---

这里写完整正文，可以留空。
```

跨日活动可另加 `date_end` 和 `date_display`。正文支持段落和 `#`、`##`、`###` 标题。

字段说明：

- `title`：必填，磁贴及详情标题。
- `date`：必填，格式为 `YYYY-MM-DD`，也是单日活动的排序日期。
- `category`：必填，目前使用 `Baseball`、`HIMEHINA` 或 `Live`。
- `date_end`：跨日活动可选；填写后使用结束日期排序。
- `date_display`：可选，用于覆盖页面上显示的日期文字。
- Markdown 正文：可留空；有内容时，列表自动截取摘要，详情显示全文。

改完内容后执行：

```sh
conda run -n misc python misc/gallery/build_gallery.py
```

脚本会检查必填字段、ISO 日期和单张 `1.*` 图片，并按结束日期倒序生成 `gallery-data.js`。该文件是生成物，不应手动编辑。每次新增活动或修改 Markdown 后都需要重新运行构建命令，并将生成文件一同提交。
