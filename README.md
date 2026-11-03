<!--
Copyright 2026 bong-water-water-bong
SPDX-License-Identifier: Apache-2.0

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
-->
# 1bit.gg: the 1bit engine site

This repository builds [https://1bit.gg/](https://1bit.gg/), the site of the
[1bit engine](https://github.com/1bit-MONSTER/engine): local LLM inference on the AMD Ryzen AI
MAX+ 395 (Strix Halo) inside AMD's Lemonade Server, on the Radeon 8060S iGPU through HRX and on
the XDNA 2 NPU.

- `tools/site.py` renders the engine's `README.md` and `docs/*.md` (checked out from
  `1bit-MONSTER/engine`) and this repository's `blog/*.md` with `site/template.html`,
  `site/style.css` and `site/theme.js`.
- `.github/workflows/pages.yml` builds the site on every pull request, deploys `main` to GitHub
  Pages, and rebuilds every three hours so engine doc changes reach the site.
- `site/pages/*.md` are the site's own landing pages (the Strix Halo guide, the FAQ): short hubs
  for the searches mapped in `SEO-KEYWORDS.md`, with facts only from the engine docs and the posts.
- Every page carries its canonical address, Open Graph and Twitter card tags and JSON-LD
  (breadcrumbs, and FAQPage where a page has an FAQ); the build writes `sitemap.xml` (lastmod from
  git), `robots.txt`, `llms.txt` and the Atom feed `feed.xml`.
- `SHARE-KIT.md` holds drafts for sharing the project (Reddit, Hacker News) for the maintainer to
  post; nothing is posted from this repository.

Build locally:

```sh
python3 -m pip install markdown==3.10.3
git clone https://github.com/1bit-MONSTER/engine ../engine
ONEBIT_ENGINE_DIR=../engine python3 tools/site.py _site
```

Apache-2.0, see [LICENSE](https://github.com/1bit-MONSTER/engine/blob/main/LICENSE) in the engine
repository; the same notice heads every file here.
