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
title: FAQ: local LLMs on Strix Halo with 1bit engine
description: Answers about the 1bit engine: which AMD hardware it runs on, the NPU on Linux, Lemonade Server and the OpenAI API, which models, the license and 1bit OS.
label: FAQ
tags: getting-started, lemonade, 1bit-os, local-llm

# 1bit engine FAQ

Short answers to the questions people ask about the engine, each with the page that has the
details.

## Frequently asked questions

### What is the 1bit engine?

One binary to rule them all: a model-agnostic local LLM inference engine for the AMD Ryzen AI MAX+
395 (Strix Halo). It serves any Hugging Face architecture, any GGUF quantization, Ryzen AI NPU packs
and ONNX graphs as one backend of AMD's Lemonade Server, on the Radeon 8060S iGPU through HRX with
our own HIP kernels and on the XDNA 2 NPU through our own NPU runtime ([Meet the engine](overview.html)).

### Which hardware does it run on?

The AMD Ryzen AI MAX+ 395 (Strix Halo): its Radeon 8060S iGPU (`gfx1151`) and its XDNA 2 NPU, on
Linux. Every model is checked on that machine before it ships, and the measured numbers are on
[Models measured](models.html). The [Strix Halo guide](strix-halo.html) sums up what runs where.

### How much memory does a model need?

Its file size, plus the context you give it: the CPU, the GPU and the NPU share one 128 GB pool, so
there is no second copy for the second device. The measured rows include a 27B ternary model at
6.7 GiB and a 2B ternary model at 1.11 GiB ([Models measured](models.html)).

### Which models fit in 128 GB?

Anything whose file fits there, which covers every row of the measured table, up to 27B-class models
at 4-bit. A mixture-of-experts model larger than that keeps only the experts a prompt routes to and
streams the rest from an NVMe drive ([MoE streaming](moe-streaming.html)).

### Does it run on Windows?

No: the engine, its HRX llama.cpp build and its NPU route are built and measured on Linux, and there
is no Windows package ([Releases](releases.html)). Lemonade Server has its own Windows backends, so
on Windows you get Lemonade without the 1bit engine ([Lemonade](lemonade.html)).

### Does it work with the OpenAI API?

Yes. `1bit serve` exposes nothing but an OpenAI-compatible API, so any OpenAI client works with it,
and inside Lemonade it is a backend behind the OpenAI-compatible API Lemonade already gives you
([1bit serve](serve.html), [Lemonade](lemonade.html)).

### Does it use the AMD NPU on Linux?

Yes. The NPU engine runs models on the XDNA 2 NPU on Linux, on our own runtime and kernels. It is in
progress, correctness first and speed next, and Qwen3-0.6B decodes at 88.6 tok/s on it in the
release gate ([NPU engine](npu.html)). The GPU and the NPU can work at the same time; the hybrid
route puts the prompt on one and the generated tokens on the other ([Hybrid](hybrid.html)).

### Which models does it run?

Any GGUF the HRX llama.cpp build loads: every ggml weight type runs on HRX, including NVFP4, Q2_0,
MXFP4 and the ternary TQ, PTQ and PQ formats. The models checked on the hardware include Qwen3.8-27B,
Qwen3.8-Flash-Next, Zyphra ZAYA1-8B, PrismML Ternary-Bonsai-2-27B, Microsoft BitNet b1.58 2B-4T,
gpt-oss-20b and Qwen3-0.6B on the NPU ([Models measured](models.html), [Model registry](registry.html)).

### How fast is it?

Measured on a Ryzen AI MAX+ 395: Qwen3.8-27B (UD-Q4_K_XL) decodes at 36.0 tok/s with MTP on code
prompts and 56.6 tok/s with the DFlash2 drafter, ZAYA1-8B (Q4_K_M) at 157 tok/s and BitNet b1.58
2B-4T at 123.4 tok/s, all on HRX. Each number, and the standard it was taken in, is on
[Models measured](models.html) and [How we measure](bench.html).

### Does it use Vulkan or the ROCm backend?

No. The engine is one llama.cpp build with one GPU backend, ggml-hrx, plus our HIP kernels: no
Vulkan, ROCm backend, Metal or CUDA. What HRX does not run, Lemonade serves with its own backends
([HRX](hrx.html)).

### Can I add it to the Lemonade Server I already run?

Yes. The `lemonade-onebit` package adds the engine as a Lemonade backend and nothing else changes;
on Ubuntu 26.04 the engine plugs into the stock `lemond` from Lemonade's PPA ([Lemonade](lemonade.html)).

### What is 1bit OS?

The engine's appliance: Lemonade Server with the engine inside, on a USB stick that boots a Ryzen
AI MAX+ 395 with Secure Boot on. `1bit-install` from the live session puts the same system on a disk
([Install 1bit OS](install.html), [1bit OS](os-v3.html), [Boot a stick](blog-boot-a-stick.html),
[Releases](releases.html)).

### Is it free and open source?

The source code is Apache-2.0 on [GitHub](https://github.com/1bit-MONSTER/engine). The release
binaries also contain two proprietary components, compiled in: the 1bit NPU runtime and the 1bit HIP
kernels for HRX, under the 1bit Binary License, free to use for any purpose and to pass on
unmodified. A build from the source without them has no NPU engine and runs HRX on the public
kernels only ([Meet the engine](overview.html), [Releases](releases.html)).

### Where do the numbers come from?

Every number is measured on the Strix Halo box, with the command that produced it; nothing is
projected. Serve configurations are compared with `tools/bench.py` in the same run, and every HRX pin
change passes a hardware gate before it merges ([How we measure](bench.html),
[Hardware gate](hw-gate.html), [the wiki](https://github.com/1bit-MONSTER/engine/wiki)).

### Where do I ask a question or report a bug?

Bugs and requests go to the engine's
[GitHub issues](https://github.com/1bit-MONSTER/engine/issues); questions are welcome on
[Discord](https://discord.gg/fa5m4Vawpa). The [blog](blog.html) is the build log, with an
[Atom feed](feed.xml).
