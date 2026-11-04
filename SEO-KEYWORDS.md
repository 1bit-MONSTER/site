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
# Keyword map for 1bit.gg

Which searches each page of https://1bit.gg/ is meant to answer. One cluster is one intent; its
**primary** page is the one whose `<title>`, meta description and H1 carry the cluster's head term,
and the supporting pages link to it. A page answers one cluster as its primary, so two pages never
compete for the same search.

The queries are the ones people type about this hardware and this stack; there are no search
volumes here (no keyword tool was used), so the order inside a cluster is by how specific the query
is, not by traffic. Re-check the map when a page is added or renamed.

Rules that hold for every page (also enforced or helped by `tools/site.py`):

- `<title>` at most 60 characters with the " · 1bit engine" suffix; the head term first.
- Meta description 140-160 characters, unique, and every number in it from a doc or a post.
- One `<h1>`; the H2s name the sub-topics people search for (the build stops on a second H1).
- Every number on a landing page is already on a doc page or in a post; landing pages link to it.

## Clusters

| # | cluster | queries | primary page | supporting pages |
|---|---|---|---|---|
| 1 | Strix Halo local LLM | strix halo llm, ryzen ai max+ 395 llm, ryzen ai max 395 local llm linux, strix halo 128gb llm, best way to run llms on strix halo | [strix-halo.html](https://1bit.gg/strix-halo.html) (guide) | index.html, models.html, overview.html, blog-every-node-on-hrx.html |
| 2 | Radeon 8060S / gfx1151 on the GPU | radeon 8060s llama.cpp, gfx1151 rocm, gfx1151 llama.cpp, radeon 8060s llm tok/s, hip kernels strix halo, amd hrx | [hrx.html](https://1bit.gg/hrx.html) | blog-every-node-on-hrx.html, blog-hrx-decode-race-solved.html, hw-gate.html |
| 3 | AMD NPU on Linux | xdna 2 npu linux llm, amd npu llm linux, ryzen ai npu linux, amdxdna llm, npu inference linux | [npu.html](https://1bit.gg/npu.html) | faq.html, blog-gpu-and-npu-at-the-same-time.html, blog-ternary-bonsai-on-the-npu.html, npu-leaderboard.html |
| 4 | Lemonade Server | lemonade server, lemonade server backend, lemonade sdk strix halo, lemonade ubuntu ppa, lemonade onebit | [lemonade.html](https://1bit.gg/lemonade.html) | strix-halo.html, faq.html, blog-new-direction-from-1bit-monster.html |
| 5 | OpenAI-compatible local server on AMD | openai compatible local server amd, local openai api ryzen ai, self-hosted llm api amd | [serve.html](https://1bit.gg/serve.html) | faq.html, lemonade.html |
| 6 | Supported models, measured | supported models strix halo, which llm runs on ryzen ai max 395, qwen3 27b local amd, qwen3.8 27b strix halo tok/s, zaya1 8b amd, gpt-oss-20b strix halo | [models.html](https://1bit.gg/models.html) | registry.html, faq.html, blog-qwen38-27b-dflash2-and-hadamard.html |
| 7 | Ternary and BitNet | bitnet b1.58 amd, bitnet b1.58 amd gpu, tq2_0 gguf, ternary llm npu, ternary bonsai 27b | [blog-bitnet-b158-on-hrx.html](https://1bit.gg/blog-bitnet-b158-on-hrx.html) (GPU), [blog-ternary-bonsai-on-the-npu.html](https://1bit.gg/blog-ternary-bonsai-on-the-npu.html) (NPU) | models.html, blog-smaller-files-unsloth-rocmfpx-ternary.html |
| 8 | Speculative decoding on AMD | speculative decoding mtp amd, mtp llama.cpp amd, dflash2 qwen3.8, draft model strix halo, npu draft model | [blog-speculative-decoding-where-it-pays.html](https://1bit.gg/blog-speculative-decoding-where-it-pays.html) | blog-qwen38-27b-dflash2-and-hadamard.html, blog-the-npu-drafts-the-gpu-checks.html, serve.html |
| 9 | LLM appliance on a USB stick | local llm usb stick, bootable llm usb, offline ai appliance, puppy linux ai, 1bit os | [blog-boot-a-stick.html](https://1bit.gg/blog-boot-a-stick.html) now; the 1bit OS doc page once engine#859 and site#16 merge | releases.html, faq.html, strix-halo.html |
| 10 | Quantization choices | which unsloth quant, ud-q4_k_xl vs ud-q5_k_xl, nvfp4 amd gpu, mxfp4 strix halo, kld quant comparison | [blog-smaller-files-unsloth-rocmfpx-ternary.html](https://1bit.gg/blog-smaller-files-unsloth-rocmfpx-ternary.html) | blog-hrx-long-prompts-and-ud-sweet-spots.html, models.html, hrx.html |
| 11 | MoE bigger than memory | run moe larger than ram, moe expert streaming nvme, deepseek on strix halo | [moe-streaming.html](https://1bit.gg/moe-streaming.html) | blog-zyphra-family-old-architectures-experts-from-the-drive.html |
| 12 | GPU and NPU together | npu prefill gpu decode, heteromosaic strix halo, igpu npu split prefill | [hybrid.html](https://1bit.gg/hybrid.html) | hetero-prefill.html, blog-gpu-and-npu-at-the-same-time.html |
| 13 | Questions | is 1bit engine open source, does lemonade use the npu on linux, does it need vulkan or rocm | [faq.html](https://1bit.gg/faq.html) (FAQPage JSON-LD) | overview.html |
| 14 | Brand | 1bit engine, 1bit.gg, 1bit-MONSTER engine | [index.html](https://1bit.gg/) | overview.html, docs.html, blog.html |

## Gaps, and what fills them

| gap | why it is open | fill it with |
|---|---|---|
| A 1bit OS page for "puppy linux ai" and "offline ai appliance" | 1bit OS is described on engine#859 / site#16, not yet on main | the 1bit OS doc page (`os-v3.html`) once they merge; its PAGE_META in site#16 already carries "Puppy Linux appliance" |
| A release page for "1bit engine download" | v2026.44 is a draft; the release post is held (`draft: true`) | the held release post, published with the release |
| Windows searches (ryzen ai npu windows) | the engine is Linux; nothing to say that the docs say | none; Lemonade's own docs answer those |
| Search volumes | no keyword tool was used | Google Search Console (1bit.gg as a domain property) after a month of impressions |

## Off-site

- GitHub topics and description on `1bit-MONSTER/engine` and `1bit-MONSTER/site` carry clusters 1-7.
- `llms.txt` lists every page with its description, for AI assistants.
- Sharing drafts per community: `SHARE-KIT.md`.
