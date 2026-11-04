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
# Share kit: drafts for Reddit and Hacker News

Drafts for the maintainer to post by hand. **Nothing here is posted automatically, and nothing
should be posted by an agent.** Every number below is on a doc page or in a post on 1bit.gg, with
the link next to it; if a number on the site changes, change it here before posting.

## Before posting anywhere

- **Say who you are.** "I build this" in the first line or the first comment. Most of these
  communities allow a maker's own post when it is disclosed and the poster takes part in the thread.
- **Read the community's rules on the day.** Self-promotion ratios, flair, and "no blog links"
  rules change; some want a text post with the link inside rather than a link post.
- **One community a day**, each with its own angle below; do not cross-post the same text.
- **Answer with numbers and the command that produced them**, and link the page that has them.
  Plain and factual, no comparisons we have not measured, and nothing negative about anyone's
  project or company.
- **What not to discuss** in threads: how the NPU kernels or the NPU runtime work inside, kernel
  performance internals, and any reverse-engineering. The honest answer is "the NPU runtime and the
  HIP kernels ship as compiled binaries under the 1bit Binary License; the rest is Apache-2.0".
- **The release is not published yet** (v2026.44 is a draft, [Releases](https://1bit.gg/releases.html)).
  Drafts marked **HOLD** need the published release; post them only after it is out.

## Canonical links

| use | link |
|---|---|
| home | https://1bit.gg/ |
| Strix Halo guide | https://1bit.gg/strix-halo.html |
| FAQ | https://1bit.gg/faq.html |
| measured numbers | https://1bit.gg/models.html |
| GPU route (HRX) | https://1bit.gg/hrx.html |
| NPU on Linux | https://1bit.gg/npu.html |
| Lemonade backend | https://1bit.gg/lemonade.html |
| how we measure | https://1bit.gg/bench.html |
| source | https://github.com/1bit-MONSTER/engine |
| models | https://huggingface.co/1bit-MONSTER |
| chat | https://discord.gg/fa5m4Vawpa |

The site counts referrers on its own (GoatCounter), so the links need no tracking parameters; use
them as they are, so every share points at the canonical address.

## r/LocalLLaMA

Angle: measured numbers on one popular machine, and how they were taken.

**Title:** Strix Halo (Ryzen AI MAX+ 395): Qwen3.8-27B at 36 tok/s with MTP, 56.6 with DFlash2, all on the iGPU, in an open-source engine inside Lemonade

> I build the 1bit engine, an Apache-2.0 inference engine for the Ryzen AI MAX+ 395 that runs as a
> backend of AMD's Lemonade Server. On the Radeon 8060S through HRX and our own HIP kernels,
> Qwen3.8-27B (UD-Q4_K_XL) decodes at 36.0 tok/s with MTP on code prompts and 56.6 tok/s with the
> DFlash2 drafter, ZAYA1-8B (Q4_K_M) at 157 tok/s and BitNet b1.58 2B-4T at 123.4 tok/s, with every
> graph node on the GPU (43 of 43 configurations, 0 nodes on the CPU). Every number is on one page
> with how it was taken: https://1bit.gg/models.html

## r/StrixHalo

Angle: a practical guide for owners of the machine.

**Title:** A guide to local LLMs on the Ryzen AI MAX+ 395 on Linux: the GPU, the NPU and Lemonade, with measured numbers

> I put together what we have measured while building the 1bit engine on Strix Halo: what runs on
> the Radeon 8060S (`gfx1151`) through HRX, what runs on the XDNA 2 NPU, and how both sit behind
> Lemonade Server's OpenAI-compatible API. Every ggml weight type runs on HRX, including NVFP4,
> MXFP4 and the ternary formats, so any GGUF quantization loads. The guide links each number to the
> page that measured it: https://1bit.gg/strix-halo.html

## r/AMD

Angle: AMD's own pieces (Lemonade, HRX, the XDNA 2 NPU) working together on Linux.

**Title:** Running LLMs on the Radeon 8060S and the XDNA 2 NPU at the same time on Linux: forty runs, no hang, no corruption

> On a Ryzen AI MAX+ 395 we measured the iGPU and the NPU working at the same time: forty
> repetitions, twenty of them with the GPU busy, and 160 byte-exact checks, all passing; a busy GPU
> costs the NPU about 13 % of its stream. That settles it for the hybrid route of the 1bit engine,
> which puts the prompt on one device and the tokens on the other, inside AMD's Lemonade Server. The
> write-up, with the method: https://1bit.gg/blog-gpu-and-npu-at-the-same-time.html

## r/ROCm

Angle: HIP on `gfx1151`, correctness first.

**Title:** gfx1151: every graph node of 43 LLM configurations on the GPU through HRX and HIP kernels, with a hardware gate on every pin change

> The 1bit engine runs local LLMs on the Radeon 8060S through HRX, AMD's ggml-hrx with its Loom
> kernels, plus our own HIP kernels. In the 2026-10-20 census, 43 of 43 configurations ran with 0
> nodes on the CPU, and every ggml weight type runs, including NVFP4, Q2_0, MXFP4 and the ternary
> TQ, PTQ and PQ formats. Every HRX pin change passes a hardware gate on a Strix Halo box before it
> merges (kernel tests, known answers, KLD against the release pin): https://1bit.gg/hrx.html

## r/linux

Angle: the NPU and the GPU used for LLMs on plain Linux, with Secure Boot on.

**Title:** Local LLMs on an AMD NPU and iGPU under Linux, with Secure Boot on: the 1bit engine

> The 1bit engine serves local LLMs on the Ryzen AI MAX+ 395 under Linux: the Radeon 8060S iGPU
> through HRX, and the XDNA 2 NPU through our own runtime on the `amdxdna` driver. The
> machine runs Linux v7.3-rc4 with the IOMMU PerfOpt backports, MOK-signed so Secure Boot stays on,
> and the kernel config is documented. The source is Apache-2.0, and every upstream the engine
> builds on is credited in its NOTICE: https://1bit.gg/kernel.html

## r/selfhosted

Angle: an OpenAI-compatible LLM server on your own box. Post the Lemonade-backend version now; the
USB-stick version is **HOLD** until the release is published.

**Title:** A self-hosted, OpenAI-compatible LLM server on a Ryzen AI MAX+ 395: Lemonade Server with the 1bit engine behind it

> Lemonade Server gives you a model catalog, downloads, a web UI and an OpenAI-compatible API; the
> 1bit engine plugs into it as the `onebit` backend and runs the models on the machine's GPU and NPU.
> The recipe passes Lemonade's own LLM test suite on HRX, 29 of 29 tests, and on Ubuntu 26.04 it
> works with the stock `lemond` from Lemonade's PPA. How to set it up:
> https://1bit.gg/lemonade.html

## r/puppylinux (HOLD)

Post only after the release is published **and** the 1bit OS docs (engine#859) are merged; the
facts below are from that pull request.

**Title:** 1bit OS: a Puppy Linux appliance (ResolutePup64) that boots straight into a local LLM server

> 1bit OS is built with woof-CE as ResolutePup64 on the Ubuntu 26.04 base, with Lemonade Server and
> the 1bit engine inside, for the AMD Ryzen AI MAX+ 395. It boots headless by default, with a second
> boot entry for Puppy's desktop, `apt` works, and models and settings persist on a `1BIT-DATA`
> partition. Write it to a stick, boot with Secure Boot on, and the LLM server is up:
> https://1bit.gg/os-v3.html

## Hacker News: Show HN (HOLD)

Post after the release is published, on a weekday morning US Eastern time. The link is the
repository; the text goes in the first comment.

**Title:** Show HN: 1bit engine – local LLMs on AMD Strix Halo's GPU and NPU, boots from a USB stick

> First comment: I build the 1bit engine, one model-agnostic binary that serves local LLMs on the
> AMD Ryzen AI MAX+ 395 (Strix Halo), as a backend of AMD's Lemonade Server: the Radeon 8060S
> through HRX with our own HIP kernels, and the XDNA 2 NPU through our own runtime on Linux.
> Measured on the machine: Qwen3.8-27B at 36.0 tok/s with MTP and 56.6 tok/s with DFlash2,
> ZAYA1-8B at 157 tok/s, and BitNet b1.58 2B-4T at 123.4 tok/s, each with how it was taken
> (https://1bit.gg/models.html). The source is Apache-2.0; the NPU runtime and our HIP kernels ship
> compiled in the release under a free-to-use binary license, and the FAQ says exactly what is
> open: https://1bit.gg/faq.html

## Questions to expect, and the page that answers each

| question | answer in one line | page |
|---|---|---|
| Is it open source? | Source Apache-2.0; the NPU runtime and our HIP kernels ship compiled under the 1bit Binary License, free to use | https://1bit.gg/faq.html |
| Does it need ROCm or Vulkan? | One GPU backend, ggml-hrx, plus our HIP kernels; what HRX does not run, Lemonade serves with its own backends | https://1bit.gg/hrx.html |
| Is the NPU actually used? | Yes, on Linux, in progress: Qwen3-0.6B decodes at 88.6 tok/s in the release gate | https://1bit.gg/npu.html |
| How were the numbers taken? | Same-run A/B with `tools/bench.py`, and a hardware gate on every HRX pin | https://1bit.gg/bench.html |
| Which models? | Any GGUF the HRX build loads; the checked list with numbers is one page | https://1bit.gg/models.html |
| Windows? | The engine runs on Linux | https://1bit.gg/faq.html |
