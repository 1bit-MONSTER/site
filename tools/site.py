#!/usr/bin/env python3
# Copyright 2026 bong-water-water-bong
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# site.py <out-dir>
#
# Builds the 1bit engine site (GitHub Pages, .github/workflows/pages.yml) in the
# 1bit.MONSTER site template (site/template.html, site/style.css, site/theme.js):
#
#   index.html     the home page: hero, the latest post, a card for every page
#   overview.html  README.md, "Meet the engine"
#   docs.html      the docs index; docs/<name>.md becomes <name>.html, with the docs sidebar
#                  (every doc is published; the ones NAV does not place land under "More")
#   blog.html      posts in blog/YYYY-MM-DD-<slug>.md, newest first; each becomes
#                  blog-<slug>.html, and feed.xml carries them as an Atom feed
#   404.html       sends old 1bit.MONSTER addresses to the archived old site
#
# A post may start with "tags: a, b" lines, a "summary: one line", an "image: card.png" (its own
# 1200x630 link-preview card in site/assets), a "title: short search title" (its <title> without
# the " · 1bit engine" suffix, 46 characters at most; unset, the heading is cut to fit) and
# "draft: true" (kept in blog/, not built) before its "# Title"; its first paragraph is its lead.
# A dated "> **Update (YYYY-MM-DD):** ..." blockquote after the lead is how a post records a claim
# that later changed; the post itself is not rewritten.
#
# The Lemonade pin is never written into a page by hand: lemonade_pin() reads it from the engine
# checkout (the third_party/lemonade gitlink and its bump commit) at build time. The summary (the lead when there is none) is the
# post's meta description and its feed.xml summary, which the Discord blog mirror posts. Links to
# other docs become page links; links to other files in the repository go to them on GitHub.
#
# Doc pages take their <title> and meta description from PAGE_META below (the docs live in the
# engine repository, so the page's search text is kept here); a doc PAGE_META does not name gets
# its heading and its first paragraph. The build stops on a title over TITLE_MAX or a description
# over DESCRIPTION_MAX in PAGE_META, and on a page with other than one <h1>.
#
# Visitor counts: with GOATCOUNTER set to a GoatCounter site code (pages.yml passes the
# repository variable of that name), every page loads GoatCounter's counter, which sets
# no cookies. Unset, as in a local preview, the pages carry no analytics at all.
#
# Docs chat: with CONTEXT7_LIBRARY set to the engine's Context7 library id (pages.yml passes
# the repository variable of that name), every page carries Context7's chat widget, which
# answers from the docs Context7 indexed (see context7.json). Context7 only serves it once the
# library is claimed and 1bit.gg is on the widget's allowed domains; unset, no widget.
#
# Search engines and link previews: every page carries its canonical 1bit.gg address, Open
# Graph and Twitter card tags with site/assets/og-card.png, and JSON-LD: the home page carries
# the Organization, the WebSite and the engine as a SoftwareApplication; each doc page is a
# TechArticle, each post a BlogPosting (published = the date in its file name, modified = its last
# commit), and the two indexes are a CollectionPage and a Blog. robots.txt and sitemap.xml list
# every page; a page's lastmod is its source file's last commit (pages.yml checks out the full
# history for that).
#
# Needs python-markdown (pip install markdown).
import datetime
import html
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys

import markdown

REPO = "https://github.com/1bit-MONSTER/engine"
WIKI = REPO + "/wiki"
SITE = "https://1bit.gg/"
# the old 1bit.MONSTER site, kept on GitHub Pages under its repository's own address
OLD_SITE = "https://1bit-monster.github.io/1bit-MONSTER/"
ROOT = pathlib.Path(__file__).resolve().parent.parent
# The engine's README.md and docs/ live in 1bit-MONSTER/engine; the site workflow checks it out and
# points ONEBIT_ENGINE_DIR at it. Unset, the engine is this checkout (the old single-repo layout).
ENGINE = pathlib.Path(os.environ.get("ONEBIT_ENGINE_DIR") or ROOT).resolve()
SITE_REPO = "https://github.com/1bit-MONSTER/site"

RELEASES = REPO + "/releases"
LEMONADE = "https://github.com/lemonade-sdk/lemonade"
DISCORD = "https://discord.gg/fa5m4Vawpa"

TAGLINE = ("Local LLM inference on the AMD Ryzen AI MAX+ 395 (Strix Halo), inside AMD's Lemonade Server: "
           "HRX with our own HIP kernels on the Radeon 8060S iGPU, and our own NPU runtime on the XDNA 2 NPU, "
           "behind an OpenAI-compatible API.")
# The home page's search title (without the " · 1bit engine" suffix) and description. Keep the
# description <= DESCRIPTION_MAX characters and update it with each milestone (README.md, docs/hrx.md).
HOME_TITLE = "Local LLM inference on AMD Ryzen AI MAX+ 395"
HOME_DESCRIPTION = ("1bit engine: local LLM inference on the AMD Ryzen AI MAX+ 395 (Strix Halo) inside Lemonade Server, "
                    "on the Radeon 8060S iGPU through HRX and on the XDNA 2 NPU.")
HOME_KEYWORDS = ("LLM inference, AMD Ryzen AI MAX+ 395, Strix Halo, gfx1151, Radeon 8060S, HRX, HIP kernels, XDNA 2 NPU, "
                 "Lemonade Server, OpenAI-compatible API, GGUF, Qwen3.8, Zyphra ZAYA1, BitNet b1.58, ternary, "
                 "Ternary-Bonsai, gpt-oss-20b, MXFP4, NVFP4, MTP, speculative decoding, 1bit OS, local AI")

# The landing page stays short: what the engine is, how it ships, where the docs are. Measured
# numbers live in the docs (engine docs/models.md -> models.html).

# Doc pages: name -> (search title without the " · 1bit engine" suffix, meta description).
# The docs themselves live in the engine repository; this is where their search text is kept.
PAGE_META = {
    'models': ('Models measured on a Ryzen AI MAX+ 395',
     'Models the 1bit engine is checked against, with the number each measured on Strix Halo: Qwen3.8-27B, Flash-Next, ZAYA1-8B, Bonsai, BitNet, gpt-oss-20b.'),
    'overview': ('What the 1bit engine is and what runs where',
     "The engine's README: HRX with our HIP kernels on the Radeon 8060S iGPU, our NPU runtime on the XDNA 2 NPU, the hybrid route, and how it installs via Lemonade."),
    'docs': ('Documentation: serve, HRX, NPU, Lemonade',
     'Documentation for the 1bit engine: 1bit serve and its OpenAI-compatible API, Lemonade, releases, HRX, the NPU engine, DwarfStar, Laya and the model registry.'),
    'blog': ('Blog: build notes and measured results',
     'Notes from building the 1bit engine on AMD Strix Halo: measured results on HRX and our HIP kernels, the NPU engine, speculative decoding and quantization.'),
    'serve': ('1bit serve: the OpenAI-compatible API',
     '1bit serve runs the engine behind one OpenAI-compatible API inside Lemonade: devices, model loading, strict GPU placement, --parallel, --mtp, --dflash, --laya.'),
    'lemonade': ('Lemonade: the onebit backend',
     "How the 1bit engine runs inside AMD's Lemonade Server as the onebit backend: the recipe, one HTTP hop for GGUF models, the pinned fork and the Ubuntu 26.04 PPA."),
    'releases': ('Releases: packages, 1bit OS, checklist',
     "The 1bit engine's releases: the Linux tarball, the Lemonade+onebit package and the 1bit OS live image, the pins each is built from, and the release checklist."),
    'bench': ('How the numbers are measured',
     "How the engine's serve numbers are taken: tools/bench.py A/B-measures 1bit serve configurations in the same run, and a recipe earns its place by that measure."),
    'recipes': ('Recipes: tuned backend settings',
     'Recipes are tuned backend settings kept as data in config/recipes.json: which flags each model and route gets, why, and how a recipe is measured before landing.'),
    'hw-gate': ('HRX hardware gate on Strix Halo',
     'The hardware gate runs every HRX pin change and hw-gate PR on a Strix Halo box before merge: kernel tests, known answers, KLD against the release pin.'),
    'hrx': ('HRX on the Radeon 8060S iGPU',
     "HRX, AMD's HIP Runtime Extended, with our own HIP kernels on the Radeon 8060S iGPU: pinned sources, quant coverage, MTP and DFlash2, ternary Bonsai, BitNet."),
    'npu': ('NPU engine on the XDNA 2 NPU',
     "The engine's NPU route on the Ryzen AI MAX+ 395's XDNA 2 NPU: our own runtime with full-ELF kernel sets, what matches the reference today, and measured numbers."),
    'hybrid': ('Hybrid: NPU prefill, HRX decode',
     '1bit serve --device hybrid processes the prompt on one device and generates on another: a prefill provider fills the KV cache, the HRX llama-server decodes.'),
    'kernel': ('Linux kernel for the Strix Halo box',
     'The kernel the Strix Halo box runs: Linux v7.3-rc4 with the IOMMU PerfOpt backports, built from our config, MOK-signed for Secure Boot, and the next-tag steps.'),
    'onnx': ('ONNX Runtime GenAI models',
     '1bit serve --device onnx serves ONNX Runtime GenAI model directories (genai_config.json, model.onnx and the tokenizer) behind the same OpenAI-compatible API.'),
    'dwarfstar': ('DwarfStar: large MoE models with SSD experts',
     'DwarfStar (antirez/ds4) in the 1bit engine: DeepSeek V4 Flash, GLM 5.x and Qwen3.8-Flash-Next in their own GGUFs, with expert streaming from the SSD.'),
    'laya': ('Laya router: where each request runs',
     'Laya, opt-in with 1bit serve --laya, sorts each conversation into code, prose, short answer or long document (95.5% right) and picks the backend and settings.'),
    'pm': ('Project Manager: ZAYA1-8B delegates',
     "1bit serve --pm makes the served model the engine's Project Manager: ZAYA1-8B routes every request and delegates to expert models over the same OpenAI API."),
    'registry': ('Model registry and Hugging Face census',
     "Which Hugging Face model architectures the 1bit engine runs: a registry built from the pinned backends' own code, and a daily census of the models people use."),
    'arch-gaps': ('Architecture gaps in the registry',
     'Model architectures the registry does not map yet, with the upstream commits that add them and what each needs before the engine serves it.'),
    'moe-streaming': ('MoE expert streaming from NVMe',
     "Running mixture-of-experts models larger than Strix Halo's 128 GB: only the experts a token routes to are read, through an expert cache and --moe-slots."),
    'tokenizers': ('Hugging Face tokenizers in the engine',
     "The engine reads any model's tokenizer.json through Hugging Face tokenizers, the Rust library, behind a C ABI: byte-exact tokens for every model it serves."),
    'PORTING': ('Porting map: private tree to public engine',
     'How the working 1bit-MONSTER engine is ported into this public repository without its history: the steps, what is done, and what stays private.'),
    'npu-leaderboard': ('NPU engine leaderboard: measured runs',
     "One row per measured run of the engine's NPU and HRX routes on the Strix Halo box, each with its instrument, repeat count and timestamp."),
}

# top bar: (label, page name or absolute URL)
TOP = [("Engine", "overview"), ("Docs", "docs"), ("Blog", "blog"), ("Benchmarks", WIKI)]

# docs sidebar groups: (title, [(doc name, label)])
NAV = [
    ("Start", [("serve", "1bit serve"), ("models", "Models measured"), ("lemonade", "Lemonade"), ("releases", "Releases"),
               ("bench", "How we measure"), ("recipes", "Recipes"), ("hw-gate", "Hardware gate")]),
    ("Devices", [("hrx", "HRX"), ("npu", "NPU engine"), ("onnx", "ONNX Runtime"), ("dwarfstar", "DwarfStar")]),
    ("Components", [("laya", "Laya router"), ("pm", "Project Manager"), ("registry", "Model registry"),
                    ("arch-gaps", "Architecture gaps"), ("moe-streaming", "MoE streaming"), ("tokenizers", "Tokenizers")]),
    ("Project", [("PORTING", "Porting map")]),
]


def docs_sources():
    return {p.stem: p for p in sorted((ENGINE / "docs").glob("*.md"))}


def posts():
    """[(date, slug, path)], newest first."""
    out = []
    for p in (ROOT / "blog").glob("*.md"):
        m = re.fullmatch(r"(\d{4}-\d{2}-\d{2})-([a-z0-9-]+)", p.stem)
        if not m:
            sys.exit(f"blog post names are YYYY-MM-DD-<slug>.md: {p.name}")
        if not is_draft(p):
            out.append((m.group(1), m.group(2), p))
    return sorted(out, reverse=True)


def strip_notice(text):
    # the copyright notice at the top of every doc is an HTML comment
    return re.sub(r"\A\s*<!--.*?-->\s*", "", text, count=1, flags=re.S)


def title_of(text):
    m = re.search(r"^# (.+)$", strip_notice(text), flags=re.M)
    return re.sub(r"[`*]", "", m.group(1)).strip() if m else "1bit engine"


def rewrite_links(text, src, docs, labels):
    """Doc links -> page links; other repository paths -> GitHub; anything absolute unchanged."""
    here = src.parent

    def fix(m):
        label, target = m.group(1), m.group(2)
        # a label that is just the file name reads better as the page's name
        path_label = re.fullmatch(r"(?:docs/)?([A-Za-z0-9_-]+)\.md", label.strip("`"))
        # GitHub keeps "--" where a heading had "(`--x`)"; python-markdown's toc collapses it to "-"
        if target.startswith("#"):
            return f"[{label}]({re.sub(r'-{2,}', '-', target)})"
        if re.match(r"^[a-z]+:|^/", target):
            return m.group(0)
        path, _, frag = target.partition("#")
        raw_frag = "#" + frag if frag else ""
        frag = "#" + re.sub(r"-{2,}", "-", frag) if frag else ""
        resolved = (here / path).resolve()
        try:
            rel = resolved.relative_to(ENGINE if resolved.is_relative_to(ENGINE) else ROOT).as_posix()
        except ValueError:
            return m.group(0)
        if rel == "README.md":
            return f"[{'Meet the engine' if path_label else label}](overview.html{frag})"
        post = re.fullmatch(r"blog/\d{4}-\d{2}-\d{2}-([a-z0-9-]+)\.md", rel)
        if post:
            return f"[{label}](blog-{post.group(1)}.html{frag})"
        if rel.startswith("docs/") and rel.endswith(".md") and resolved.stem in docs:
            if path_label:
                label = labels.get(resolved.stem) or title_of(docs[resolved.stem].read_text())
            return f"[{label}]({resolved.stem}.html{frag})"
        kind = "tree" if resolved.is_dir() else "blob"
        return f"[{label}]({REPO}/{kind}/main/{rel}{raw_frag})"

    return re.sub(r"\[([^\]]*)\]\(([^)\s]+)\)", fix, text)


def nest_lists(text):
    """GitHub nests a list under 2 spaces, python-markdown needs 4: double list-marker indents outside code."""
    out, fenced = [], False
    for line in text.split("\n"):
        if line.lstrip().startswith("```"):
            fenced = not fenced
        m = None if fenced else re.match(r"^( +)([-*+]|\d+\.) ", line)
        out.append(" " * (2 * len(m.group(1))) + line[len(m.group(1)):] if m else line)
    return "\n".join(out)


def escape_issue_numbers(text):
    """python-markdown makes any line that starts with "#" a heading, even "#572 reads ..." in the
    middle of a paragraph (GitHub does not): escape the "#" of such lines outside code blocks."""
    out, fenced = [], False
    for line in text.split("\n"):
        if line.lstrip().startswith("```"):
            fenced = not fenced
        out.append(re.sub(r"^#(?=\d)", r"\\#", line) if not fenced else line)
    return "\n".join(out)


def render(text):
    text = escape_issue_numbers(nest_lists(text))
    md = markdown.Markdown(extensions=["tables", "fenced_code", "toc", "sane_lists", "footnotes"],
                           extension_configs={"toc": {"permalink": "#", "permalink_class": "anchor"}})
    body = md.convert(text)
    # wide tables scroll on their own instead of the page
    body = body.replace("<table>", '<div class="table"><table>').replace("</table>", "</table></div>")
    return body


def analytics():
    out = []
    code = os.environ.get("GOATCOUNTER", "").strip()
    if code:
        if not re.fullmatch(r"[a-z0-9-]+", code):
            sys.exit(f"GOATCOUNTER must be a GoatCounter site code (letters, digits, dashes), not {code!r}")
        out.append(f'<script data-goatcounter="https://{code}.goatcounter.com/count" async src="https://gc.zgo.at/count.js"></script>')
    # Docs7 (Context7's docs analytics): the site id from the Docs7 dashboard
    site = os.environ.get("DOCS7_SITE", "").strip()
    if site:
        if not re.fullmatch(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", site):
            sys.exit(f"DOCS7_SITE must be the Docs7 site id (a UUID), not {site!r}")
        out.append(f'<script defer src="https://context7.com/docs7-analytics.js" data-site="{site}"></script>')
    return "\n".join(out)


def chat_widget():
    library = os.environ.get("CONTEXT7_LIBRARY", "").strip()
    if not library:
        return ""
    if not re.fullmatch(r"/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", library):
        sys.exit(f"CONTEXT7_LIBRARY must be a Context7 library id like /owner/repo, not {library!r}")
    return (f'<script src="https://context7.com/widget.js" data-library="{library}" '
            'data-color="#1779e1" data-position="bottom-right" '
            'data-placeholder="Ask about the 1bit engine docs..." '
            'data-welcome-message="Ask anything about the 1bit engine: install, serving, HRX, HIP kernels, the NPU, Lemonade." '
            'async></script>')


OG_IMAGE = SITE + "assets/og-card.png"
AUTHOR = {"@type": "Person", "name": "bong-water-water-bong", "url": "https://github.com/bong-water-water-bong"}
ORG_ID, WEBSITE_ID, SOFTWARE_ID = SITE + "#organization", SITE + "#website", SITE + "#software"
ORG = {"@type": "Organization", "@id": ORG_ID, "name": "1bit engine", "url": SITE,
       "logo": {"@type": "ImageObject", "url": SITE + "assets/apple-touch-icon.png", "width": 180, "height": 180},
       "sameAs": [REPO, "https://github.com/1bit-MONSTER", DISCORD]}


def jsonld_graph(*nodes):
    return {"@context": "https://schema.org", "@graph": list(nodes)}


def website_node():
    return {"@type": "WebSite", "@id": WEBSITE_ID, "name": "1bit engine", "url": SITE,
            "description": HOME_DESCRIPTION, "inLanguage": "en", "publisher": {"@id": ORG_ID}}


def software_node():
    return {"@type": "SoftwareApplication", "@id": SOFTWARE_ID, "name": "1bit engine", "url": SITE,
            "description": TAGLINE, "applicationCategory": "DeveloperApplication",
            "applicationSubCategory": "LLM inference engine", "operatingSystem": "Linux",
            "downloadUrl": RELEASES, "installUrl": SITE + "lemonade.html",
            "softwareRequirements": f"AMD Ryzen AI MAX+ 395 (Strix Halo); Lemonade Server, {lemonade_pin_text(lemonade_pin())}",
            "license": "https://www.apache.org/licenses/LICENSE-2.0",
            "isAccessibleForFree": True,
            "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD", "availability": "https://schema.org/InStock"},
            "author": {"@id": ORG_ID}, "publisher": {"@id": ORG_ID}, "sameAs": [REPO], "keywords": HOME_KEYWORDS}


def article_node(kind, name, title, description, published, modified, image=None, keywords=None):
    node = {"@type": kind, "@id": page_url(name) + "#article", "headline": title, "description": description,
            "url": page_url(name), "mainEntityOfPage": page_url(name), "image": image or OG_IMAGE,
            "datePublished": published, "dateModified": modified, "inLanguage": "en",
            "author": AUTHOR, "publisher": {"@id": ORG_ID}, "isPartOf": {"@id": WEBSITE_ID}}
    if keywords:
        node["keywords"] = keywords
    return node


def source_url(src):
    """The page source's GitHub URL: engine files in the engine repo, the rest in the site repo."""
    src = pathlib.Path(src).resolve()
    if src.is_relative_to(ENGINE):
        return f"{REPO}/blob/main/{src.relative_to(ENGINE).as_posix()}"
    return f"{SITE_REPO}/blob/main/{src.relative_to(ROOT).as_posix()}"


def last_commit_date(path):
    """The source file's last commit date (YYYY-MM-DD); today when git cannot say."""
    try:
        d = subprocess.run(["git", "-C", str(pathlib.Path(path).resolve().parent), "log", "-1", "--format=%cs", "--", str(path)],
                           capture_output=True, text=True, timeout=30).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        d = ""
    return d or datetime.date.today().isoformat()


def lemonade_pin():
    """The Lemonade the engine is pinned to, from the engine checkout alone (the site workflow checks
    out no submodules): the gitlink of third_party/lemonade and the subject of the commit that last
    moved it, which the bump-lemonade workflow writes as
    "Bump Lemonade: 1bit-MONSTER/lemonade <sha> (upstream vYYYY.WW.N)". A checked-out submodule, when
    there is one, must agree with the gitlink. -> {"short", "date", "upstream"} or {} when git cannot say."""
    try:
        tree = subprocess.run(["git", "-C", str(ENGINE), "ls-tree", "HEAD", "third_party/lemonade"],
                              capture_output=True, text=True, timeout=30).stdout.split()
        if len(tree) < 3 or tree[1] != "commit":
            return {}
        sha = tree[2]
        log = subprocess.run(["git", "-C", str(ENGINE), "log", "-1", "--format=%cs%n%s", "--", "third_party/lemonade"],
                             capture_output=True, text=True, timeout=30).stdout.splitlines()
        sub = ENGINE / "third_party" / "lemonade"
        if (sub / ".git").exists():
            head = subprocess.run(["git", "-C", str(sub), "rev-parse", "HEAD"], capture_output=True, text=True, timeout=30).stdout.strip()
            if head and head != sha:
                sys.exit(f"third_party/lemonade is checked out at {head[:12]} but the engine pins {sha[:12]}")
    except (OSError, subprocess.SubprocessError):
        return {}
    m = re.search(r"upstream (v\d{4}\.\d{1,2}\.\d+)", log[1]) if len(log) > 1 else None
    return {"short": sha[:12], "date": log[0] if log else "", "upstream": m.group(1) if m else ""}


def lemonade_pin_text(pin):
    """"the weekly Lemonade pin (fork commit <sha>, bumped <date>, upstream vX)" for the pages."""
    if not pin:
        return "the weekly Lemonade pin"
    parts = [f"fork commit {pin['short']}"] + ([f"bumped {pin['date']}"] if pin["date"] else []) + \
            ([f"upstream {pin['upstream']}"] if pin["upstream"] else [])
    return "the weekly Lemonade pin (" + ", ".join(parts) + ")"


def first_commit_date(path):
    """The source file's first commit date (YYYY-MM-DD); its last commit date when git cannot say."""
    try:
        d = subprocess.run(["git", "-C", str(pathlib.Path(path).resolve().parent), "log", "--format=%cs",
                            "--diff-filter=A", "--follow", "--", str(path)],
                           capture_output=True, text=True, timeout=30).stdout.split()
    except (OSError, subprocess.SubprocessError):
        d = []
    return d[-1] if d else last_commit_date(path)


def page_url(name):
    return SITE if name == "index" else f"{SITE}{name}.html"


def seo_head(name, title, description, og_type, jsonld, noindex, image=None, image_alt=None, dates=None):
    """dates: (published, modified) for an article page; they become article:*_time tags."""
    esc = lambda s: html.escape(s, quote=True)
    if noindex:
        return '<meta name="robots" content="noindex">'
    url = page_url(name)
    image = image or OG_IMAGE
    image_alt = image_alt or "1bit engine: local LLM inference on the AMD Ryzen AI MAX+ 395 inside Lemonade Server"
    tags = [f'<link rel="canonical" href="{url}">',
            f'<meta property="og:url" content="{url}">',
            f'<meta property="og:type" content="{og_type}">',
            '<meta property="og:locale" content="en_US">',
            f'<meta property="og:image" content="{image}">',
            '<meta property="og:image:width" content="1200">',
            '<meta property="og:image:height" content="630">',
            f'<meta property="og:image:alt" content="{esc(image_alt)}">',
            '<meta name="twitter:card" content="summary_large_image">',
            f'<meta name="twitter:title" content="{esc(title)}">',
            f'<meta name="twitter:description" content="{esc(description)}">',
            f'<meta name="twitter:image" content="{image}">',
            f'<meta name="twitter:image:alt" content="{esc(image_alt)}">']
    if dates:
        tags += [f'<meta property="article:published_time" content="{dates[0]}">',
                 f'<meta property="article:modified_time" content="{dates[1]}">',
                 '<meta property="article:author" content="bong-water-water-bong">']
    if jsonld:
        # "</" cannot appear inside a script element
        tags.append('<script type="application/ld+json">' + json.dumps(jsonld, ensure_ascii=False).replace("</", "<\\/") + "</script>")
    return "\n".join(tags)


def plain(markdown_text):
    """One paragraph of markdown as plain text."""
    text = re.sub(r"\s*\(\[[^\]]*\.md\]\([^)]*\)\)", "", markdown_text)  # "(docs/x.md)" asides
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    return re.sub(r"[`*_]", "", " ".join(text.split()))


def post_image(text):
    """A post's own link-preview card: an optional "image: file.png" line (site/assets, 1200x630)."""
    m = re.search(r"^image:\s*(\S+)\s*$", strip_notice(text).split("\n# ", 1)[0], re.M)
    return SITE + "assets/" + m.group(1) if m else None


def split_post(text):
    """-> (tags, title, lead, the rest, summary or "", search title or "", draft) of a post. A post that
    starts with "draft: true" is kept in blog/ but not built (no page, no feed entry, no sitemap line)."""
    text = strip_notice(text)
    tags, summary, seo_title, draft = [], "", "", False
    while True:
        m = re.match(r"\s*(tags|summary|image|title|draft):\s*(.+)\n", text)
        if not m:
            break
        if m.group(1) == "draft":
            draft = m.group(2).strip().lower() in ("true", "yes", "1")
        elif m.group(1) == "tags":
            tags += [t.strip() for t in m.group(2).split(",") if t.strip()]
        elif m.group(1) == "summary":
            summary = m.group(2).strip()
        elif m.group(1) == "title":
            seo_title = m.group(2).strip()
        text = text[m.end():]
    m = re.match(r"\s*# (.+)\n", text)
    if not m:
        sys.exit("a post starts with its '# Title'")
    rest = text[m.end():].strip()
    lead, _, body = rest.partition("\n\n")
    return tags, re.sub(r"[`*]", "", m.group(1)).strip(), lead.strip(), body, summary, seo_title, draft


def is_draft(path):
    return split_post(path.read_text())[6]


def first_paragraph(text):
    for para in re.split(r"\n\s*\n", strip_notice(text)):
        para = para.strip()
        if para and not para.startswith(("#", ">", "|", "-", "```", "<", "[")):  # "[" = a badge line
            return plain(para)
    return ""


# what search results show: about 160 characters of description and 60 of title
DESCRIPTION_MAX, TITLE_MAX, SUFFIX = 160, 60, " · 1bit engine"


def meta_description(text):
    """Whole sentences up to DESCRIPTION_MAX; else (too long, or too short to say much) the
    text cut at a clause."""
    text = " ".join(text.split())
    if len(text) <= DESCRIPTION_MAX:
        return text
    out = ""
    for sentence in re.split(r"(?<=[.!?])\s+(?=[A-Z0-9`\"(])", text):
        if len(out) + len(sentence) + 1 > DESCRIPTION_MAX:
            break
        out = f"{out} {sentence}".strip()
    if len(out) >= 70 or out == text:
        return out
    cut = text[:DESCRIPTION_MAX - 1]
    for mark in ("; ", ": ", ", ", " "):
        i = cut.rfind(mark)
        if i > DESCRIPTION_MAX // 2:
            return cut[:i].rstrip(",;:") + "…"
    return cut + "…"


def meta_title(title):
    """"<title> · 1bit engine", at most TITLE_MAX characters with the brand always last: a long
    title is cut at the longest clause that fits, else at a word."""
    base = title.removesuffix(SUFFIX).strip()
    room = TITLE_MAX - len(SUFFIX)
    if len(base) <= room:
        return base + SUFFIX
    best = ""
    for mark in (": ", " — ", " - ", ", ", "; "):
        i = base.rfind(mark, 0, room + 1)
        if i > len(best):
            best = base[:i]
    return (best if len(best) >= 20 else clip(base, room - 1)) + SUFFIX


def clip(text, n=150):
    return text if len(text) <= n else text[:n].rsplit(" ", 1)[0] + "…"


def nav_groups(docs):
    placed = {name for _, items in NAV for name, _ in items}
    groups = [(t, [(n, l) for n, l in items if n in docs]) for t, items in NAV]
    extra = [(n, title_of(docs[n].read_text())) for n in docs if n not in placed]
    if extra:
        groups.append(("More", extra))
    return [(t, items) for t, items in groups if items]


class Site:
    def __init__(self, out):
        self.out = out
        self.template = strip_notice((ROOT / "site" / "template.html").read_text())
        self.docs = docs_sources()
        self.groups = nav_groups(self.docs)
        self.order = [n for _, items in self.groups for n, _ in items]
        self.labels = {n: l for _, items in self.groups for n, l in items}
        self.posts = posts()
        self.pages = []  # (url, lastmod) for sitemap.xml
        # rewrite_links resolves README.md to the overview page and docs to their pages
        self.link_docs = dict(self.docs)

    def posts_modified(self):
        """The newest post date or post commit: the lastmod of the pages that list the posts."""
        return max((max(d, last_commit_date(p)) for d, _, p in self.posts), default=datetime.date.today().isoformat())

    def top_nav(self, current):
        out = []
        for label, target in TOP:
            href = target if target.startswith("http") else f"{target}.html"
            cur = ' aria-current="page"' if target == current else ""
            out.append(f'      <a href="{href}"{cur}>{html.escape(label)}</a>')
        return "\n".join(out)

    def write(self, name, title, main, kind, section, description=TAGLINE, extra_head="",
              og_type="website", jsonld=None, lastmod=None, noindex=False, image=None, image_alt=None, dates=None):
        if not noindex:
            self.pages.append((page_url(name), lastmod or datetime.date.today().isoformat()))
        title, description = meta_title(title), meta_description(description)
        if len(title) > TITLE_MAX or len(description) > DESCRIPTION_MAX:
            sys.exit(f"{name}.html: title {len(title)} > {TITLE_MAX} or description {len(description)} > {DESCRIPTION_MAX} characters")
        page = (self.template
                .replace("{{seo}}", seo_head(name, title, description, og_type, jsonld, noindex, image, image_alt, dates))
                .replace("{{title}}", html.escape(title))
                .replace("{{description}}", html.escape(description, quote=True))
                .replace("{{kind}}", kind)
                .replace("{{nav}}", self.top_nav(section))
                .replace("{{main}}", main)
                .replace("{{analytics}}", analytics())
                .replace("{{chat}}", chat_widget())
                .replace("{{repo}}", REPO))
        if extra_head:
            page = page.replace("<head>", "<head>\n" + extra_head, 1)
        # one h1 per page (SEO): a line starting "#36 ..." in a doc renders as a stray h1
        h1 = len(re.findall(r"<h1[\s>]", page, re.I))
        if h1 != 1:
            sys.exit(f"{name}.html has {h1} <h1> elements; start no doc line with '#<number>'")
        (self.out / f"{name}.html").write_text(page)

    def md(self, text, src):
        return render(rewrite_links(text, src, self.link_docs, self.labels))

    # ── docs ──────────────────────────────────────────────────────────
    def sidebar(self, current):
        out = ['<details class="docs-side" open><summary>Contents</summary><nav aria-label="Documentation">']
        for title, items in [("Overview", [("docs", "All docs"), ("overview", "Meet the engine")])] + self.groups:
            out.append(f'<p class="group">{html.escape(title)}</p><ul>')
            for name, label in items:
                cur = ' aria-current="page"' if name == current else ""
                out.append(f'<li><a href="{name}.html"{cur}>{html.escape(label)}</a></li>')
            out.append("</ul>")
        out.append("</nav></details>")
        return "\n".join(out)

    def pager(self, name):
        if name not in self.order:
            return ""
        i = self.order.index(name)
        prev = (f'<a class="prev" href="{self.order[i - 1]}.html"><span>Previous</span>{html.escape(self.labels[self.order[i - 1]])}</a>'
                if i > 0 else "<span></span>")
        nxt = (f'<a class="next" href="{self.order[i + 1]}.html"><span>Next</span>{html.escape(self.labels[self.order[i + 1]])}</a>'
               if i + 1 < len(self.order) else "<span></span>")
        return f'<nav class="pager">{prev}{nxt}</nav>'

    def doc_page(self, name, src, section="docs"):
        text = strip_notice(src.read_text())
        if name == "overview":
            # the README's link to this site is redundant on the site itself
            text = re.sub(r"^\*\*Documentation:\*\*.*\n+", "", text, count=1, flags=re.M)
            text = re.sub(r"^\*\*Site:\*\*.*\n+", "", text, count=1, flags=re.M)
        main = (f'<div class="container docs">\n{self.sidebar(name)}\n<article class="docs-page prose">\n'
                f'{self.md(text, src)}\n{self.pager(name)}\n'
                f'<p class="source meta"><a href="{source_url(src)}">View this page\'s source on GitHub ↗</a></p>\n'
                "</article>\n</div>")
        heading = title_of(text)
        page_title, description = PAGE_META.get(name) or (heading, first_paragraph(text) or TAGLINE)
        if name in PAGE_META and (len(page_title) + len(SUFFIX) > TITLE_MAX or len(description) > DESCRIPTION_MAX):
            sys.exit(f"PAGE_META[{name!r}]: title over {TITLE_MAX - len(SUFFIX)} or description over {DESCRIPTION_MAX} characters")
        published, modified = first_commit_date(src), last_commit_date(src)
        article = article_node("TechArticle", name, heading, meta_description(description), published, modified)
        if name == "overview":
            article["about"] = {"@id": SOFTWARE_ID}
        self.write(name, page_title + SUFFIX, main, "doc", section, description, og_type="article",
                   lastmod=modified, dates=(published, modified), jsonld=jsonld_graph(article))

    def docs_index(self):
        rows = []
        for title, items in self.groups:
            rows.append(f"<h2>{html.escape(title)}</h2>\n<div class=\"table\"><table><thead><tr><th>Page</th><th>What it covers</th></tr></thead><tbody>")
            for name, label in items:
                desc = clip(first_paragraph(self.docs[name].read_text()), 180)
                rows.append(f'<tr><td><a href="{name}.html">{html.escape(label)}</a></td><td>{html.escape(desc)}</td></tr>')
            rows.append("</tbody></table></div>")
        main = (f'<div class="container docs">\n{self.sidebar("docs")}\n<article class="docs-page prose">\n'
                "<h1>Documentation</h1>\n"
                f'<p class="lead">How to run the engine, what each device does, and how the pieces fit. '
                f'Measured numbers are on the <a href="{WIKI}">wiki</a>.</p>\n' + "\n".join(rows) +
                "\n</article>\n</div>")
        title, description = PAGE_META["docs"]
        self.write("docs", title + SUFFIX, main, "doc", "docs", description,
                   lastmod=max(last_commit_date(p) for p in self.docs.values()), jsonld=jsonld_graph(
            {"@type": "CollectionPage", "@id": page_url("docs") + "#page", "name": "1bit engine documentation",
             "url": page_url("docs"), "description": description, "inLanguage": "en",
             "isPartOf": {"@id": WEBSITE_ID}, "about": {"@id": SOFTWARE_ID},
             "hasPart": [{"@type": "TechArticle", "name": l, "url": page_url(n)} for _, items in self.groups for n, l in items]}))

    # ── blog ──────────────────────────────────────────────────────────
    def blog(self):
        if not self.posts:
            return []
        rows = []
        for i, (date, slug, src) in enumerate(self.posts):
            tags, title, lead, body, summary, seo_title, _ = split_post(src.read_text())
            summary = summary or plain(lead)
            if seo_title and len(seo_title) + len(SUFFIX) > TITLE_MAX:
                sys.exit(f"{src.name}: title: line over {TITLE_MAX - len(SUFFIX)} characters")
            image = post_image(src.read_text())
            name = f"blog-{slug}"
            tag_html = "".join(f'<span class="tag">{html.escape(t)}</span>' for t in tags)
            newer = self.posts[i - 1] if i > 0 else None
            older = self.posts[i + 1] if i + 1 < len(self.posts) else None

            def link(p, cls, word):
                if not p:
                    return "<span></span>"
                return f'<a class="{cls}" href="blog-{p[1]}.html"><span>{word}</span>{html.escape(split_post(p[2].read_text())[1])}</a>'
            main = (f'<article class="art"><div class="container">\n'
                    f'<a class="back" href="blog.html">← all posts</a>\n'
                    f'<div class="art-meta"><time datetime="{date}">{date}</time>{tag_html}</div>\n'
                    f"<h1>{html.escape(title)}</h1>\n"
                    f'<p class="lead">{self.md(lead, src)[3:-4]}</p>\n'
                    f'<div class="prose">\n{self.md(body, src)}\n</div>\n'
                    f'<nav class="pager">{link(newer, "prev", "Newer")}{link(older, "next", "Older")}</nav>\n'
                    "</div></article>")
            modified = max(date, last_commit_date(src))
            self.write(name, (seo_title or title) + SUFFIX, main, "post", "blog", summary, og_type="article",
                       lastmod=modified, image=image, image_alt=title, dates=(date, modified),
                       jsonld=jsonld_graph(article_node("BlogPosting", name, title, meta_description(summary), date, modified,
                                                        image, ", ".join(tags))))
            rows.append((date, name, title, plain(lead), tags, self.md(lead + "\n\n" + body, src), summary))

        log = "\n".join(
            f'<a class="log-row" href="{n}.html"><span class="log-date">{d}</span><div class="log-body">'
            f"<h3>{html.escape(t)}</h3><p>{html.escape(clip(s, 320))}</p></div></a>" for d, n, t, s, _, _, _ in rows)
        main = ('<section class="section"><div class="container hero-center hero-narrow">\n'
                '<p class="eyebrow">Blog · field notes</p>\n'
                "<h1>How the engine actually gets built.</h1>\n"
                '<p class="lead">Notes on the work: what we port, what we measure, what we ship.</p>\n'
                "</div></section>\n"
                '<section class="section"><div class="container">\n'
                '<div class="row-between log-head"><div><p class="eyebrow">Serial · 2026</p><h2>Notes, in order.</h2></div>'
                f'<div class="links"><a class="btn btn-ghost" href="feed.xml">Atom feed&nbsp;→</a>'
                f'<a class="btn btn-ghost" href="{OLD_SITE}1bit-blog.html">1bit.MONSTER archive&nbsp;→</a></div></div>\n'
                f"{log}\n</div></section>\n{self.archive()}")
        title, description = PAGE_META["blog"]
        self.write("blog", title + SUFFIX, main, "blog", "blog", description, lastmod=self.posts_modified(), jsonld=jsonld_graph(
            {"@type": "Blog", "@id": page_url("blog") + "#blog", "name": "1bit engine blog", "url": page_url("blog"),
             "description": description, "inLanguage": "en", "publisher": {"@id": ORG_ID}, "isPartOf": {"@id": WEBSITE_ID},
             "blogPost": [{"@type": "BlogPosting", "headline": t, "url": page_url(n), "datePublished": d}
                          for d, n, t, _, _, _, _ in rows]}))

        def stamp(d):
            return d + "T00:00:00Z"
        entries = "".join(
            f"<entry><title>{html.escape(t)}</title><link href=\"{SITE}{n}.html\"/><id>{SITE}{n}.html</id>"
            f"<updated>{stamp(d)}</updated><summary>{html.escape(sm)}</summary>"
            + "".join(f'<category term="{html.escape(x, quote=True)}"/>' for x in tags) +
            f"<content type=\"html\">{html.escape(b)}</content></entry>" for d, n, t, s, tags, b, sm in rows)
        (self.out / "feed.xml").write_text(
            '<?xml version="1.0" encoding="utf-8"?>\n<feed xmlns="http://www.w3.org/2005/Atom">'
            f'<title>1bit engine</title><link href="{SITE}"/><link rel="self" href="{SITE}feed.xml"/><id>{SITE}</id>'
            f"<updated>{stamp(rows[0][0])}</updated><author><name>bong-water-water-bong</name></author>{entries}</feed>\n")
        return rows

    def archive(self):
        """blog/archive.tsv: date, title, page of the old 1bit.MONSTER blog worth keeping."""
        src = ROOT / "blog" / "archive.tsv"
        if not src.exists():
            return ""
        rows = [line.split("\t") for line in src.read_text().splitlines() if line.strip()]
        log = "\n".join(
            f'<a class="log-row" href="{OLD_SITE}{f}"><span class="log-date">{d}</span><div class="log-body">'
            f"<h3>{html.escape(t)}&nbsp;↗</h3></div></a>" for d, t, f in rows)
        return ('<section class="section"><div class="container">\n'
                '<div class="log-head"><p class="eyebrow">Archive · 1bit.MONSTER</p><h2>From the 1bit.MONSTER years.</h2>\n'
                '<p class="lead archive-note">The posts from before the clean repository, as they were written. '
                "They describe the old monorepo; the engine's current numbers are on the wiki.</p></div>\n"
                f"{log}\n</div></section>")

    # ── home ──────────────────────────────────────────────────────────
    def home(self, rows):
        latest = ""
        if rows:
            d, n, t, s, _, _, _ = rows[0]
            latest = (f'<a class="latest-link" href="{n}.html"><span class="latest-badge"><span class="dot"></span>latest · {d}</span>'
                      f'<span class="latest-title"><strong>{html.escape(t)}.</strong> {html.escape(clip(s, 260))}</span>'
                      '<span class="latest-more">read the post <span class="ar">→</span></span></a>')

        def card(href, title, desc, path):
            return (f'<a class="site-card" href="{href}"><span class="site-title">{html.escape(title)} <span class="ar">→</span></span>'
                    f'<p class="site-desc">{html.escape(desc)}</p><span class="site-path">{html.escape(path)}</span></a>')
        cards = [card("overview.html", "Engine", "What the engine is, what runs where, and who it is built on.", "engine"),
                 card("docs.html", "Docs", "Every device, every component, and how to run them.", "docs"),
                 card("blog.html", "Blog", "The build log: what moved over, what got faster, what broke.", "blog"),
                 card(WIKI, "Benchmarks", "Measured, not projected. Every number with how it was taken.", "wiki")]
        cards += [card(f"{n}.html", l, clip(first_paragraph(self.docs[n].read_text()), 120), n)
                  for _, items in self.groups for n, l in items]
        mark = ('<svg class="mark" viewBox="0 0 24 24" fill="none" aria-hidden="true"><rect class="relay r1" x="2" y="2" width="9" height="9" rx="2"/>'
                '<rect class="relay r2" x="13" y="2" width="9" height="9" rx="2"/><rect class="relay r3" x="2" y="13" width="9" height="9" rx="2"/>'
                '<rect class="relay r4" x="13" y="13" width="9" height="9" rx="2"/></svg>')
        main = ('<section class="section hero-center"><div class="container">\n'
                f"<h1>{mark}1bit engine</h1>\n"
                f'<p class="lead">{html.escape(TAGLINE)}</p>\n'
                '<div class="cta-row"><a class="btn btn-primary" href="serve.html">Get started&nbsp;→</a>'
                '<a class="btn btn-ghost" href="overview.html">Meet the engine&nbsp;→</a></div>\n'
                f"{latest}\n</div></section>\n"
                '<section class="section"><div class="container">\n'
                '<span class="site-badge"><span class="dot"></span>site index</span>\n'
                f'<div class="site-grid">{"".join(cards)}</div>\n</div></section>')
        self.write("index", HOME_TITLE + SUFFIX, main, "home", "", description=HOME_DESCRIPTION,
                   lastmod=max(last_commit_date(ROOT / "tools" / "site.py"), self.posts_modified()),
                   jsonld=jsonld_graph(ORG, website_node(), software_node()))

    # ── 404 ───────────────────────────────────────────────────────────
    def not_found(self):
        """GitHub serves 404.html at any depth, so it pins its links to the site root. An old
        1bit.MONSTER address (1bit-*.html) links to its copy on the archived old site."""
        main = ('<section class="section hero-center"><div class="container hero-narrow">\n'
                '<p class="eyebrow">404</p><h1>Page not found</h1>\n'
                '<p class="lead">1bit.MONSTER is now 1bit engine. Pages from the old site are kept in the '
                f'<a id="old" href="{OLD_SITE}"><u>1bit.MONSTER archive</u></a>.</p>\n'
                '<div class="cta-row"><a class="btn btn-primary" href="index.html">Home&nbsp;→</a>'
                '<a class="btn btn-ghost" href="docs.html">Docs&nbsp;→</a></div>\n'
                "<script>\n"
                "  // an old 1bit.MONSTER address: point straight at its archived copy\n"
                r'  var m = location.pathname.match(/\/(1bit-[a-z0-9-]+\.html)$/);' "\n"
                f'  if (m && m[1] !== "1bit-jarvis.html") document.getElementById("old").href = "{OLD_SITE}" + m[1];\n'
                "</script>\n</div></section>")
        self.write("404", "Page not found · 1bit engine", main, "doc", "",
                   "This address is not on 1bit.gg. Pages of the old 1bit.MONSTER site are kept in its archive.",
                   extra_head=f'<base href="{SITE}">', noindex=True)

    def build(self):
        readme = ENGINE / "README.md"
        for name, src in self.docs.items():
            self.doc_page(name, src)
        self.doc_page("overview", readme, section="overview")
        self.docs_index()
        rows = self.blog()
        self.home(rows)
        self.not_found()
        for f in ("style.css", "theme.js"):
            shutil.copy(ROOT / "site" / f, self.out / f)
        shutil.copytree(ROOT / "site" / "assets", self.out / "assets")
        (self.out / ".nojekyll").write_text("")
        # IndexNow (Bing, Yandex, Seznam, Naver): pages.yml sets INDEXNOW_KEY (public by design), the
        # site serves it at /<key>.txt, and the deploy job submits the sitemap's URLs.
        key = os.environ.get("INDEXNOW_KEY", "").strip()
        if key:
            if not re.fullmatch(r"[0-9a-f]{8,128}", key):
                sys.exit(f"INDEXNOW_KEY must be 8-128 hex digits, not {key!r}")
            (self.out / f"{key}.txt").write_text(key)
        (self.out / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {SITE}sitemap.xml\n")
        urls = "".join(f"<url><loc>{u}</loc><lastmod>{d}</lastmod></url>" for u, d in sorted(self.pages))
        (self.out / "sitemap.xml").write_text('<?xml version="1.0" encoding="utf-8"?>\n'
                                              f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n')
        return len(list(self.out.glob("*.html")))


def main():
    out = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "_site")
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    print(f"{Site(out).build()} pages -> {out}")


if __name__ == "__main__":
    main()
