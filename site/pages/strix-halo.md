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
title: Local LLMs on Strix Halo: Ryzen AI MAX+ 395
description: Run local LLMs on AMD Strix Halo (Ryzen AI MAX+ 395) on Linux: the Radeon 8060S iGPU through HRX, the XDNA 2 NPU, Lemonade Server, and where to start.
label: Strix Halo guide
tags: strix-halo, ryzen-ai-max-395, local-llm, getting-started, hrx, npu, xdna2

# Local LLMs on AMD Strix Halo (Ryzen AI MAX+ 395) on Linux

The AMD Ryzen AI MAX+ 395, codenamed Strix Halo, puts a Radeon 8060S iGPU (`gfx1151`), an XDNA 2
NPU and 128 GB of memory shared between them in one machine. The 1bit engine is built for that one
chip: it serves local LLMs on its GPU and its NPU, on Linux, behind the OpenAI-compatible API of
AMD's [Lemonade Server](lemonade.html). This page gathers what the docs and the posts say about
running local LLMs on it, with a link to where each fact is measured.

## Start here

Three ways to get a model answering on this machine, all of them the same engine: one binary, model
agnostic, and the stick is the appliance.

- **Boot the stick.** 1bit OS is Lemonade Server with the engine inside, on a USB stick that boots a
  Ryzen AI MAX+ 395 with Secure Boot on; `1bit-install` from the live session puts the same system on an
  internal disk or another drive ([1bit OS](os-v3.html), [Boot a stick](blog-boot-a-stick.html)).
- **Add it to the Lemonade you already run.** The `lemonade-onebit` package adds the engine as a Lemonade
  backend and nothing else changes ([Lemonade](lemonade.html)).
- **Ask a model.** `1bit serve` exposes nothing but an OpenAI-compatible API, so any OpenAI client works
  ([1bit serve](serve.html)); the models checked on this box, and what each measured, are on
  [Models measured](models.html).

Whichever you pick, the first question is whether the model fits — that is the next section, and the
[FAQ](faq.html) answers it in two lines.

## What to expect

The 128 GB of memory is unified: the CPU, the Radeon 8060S and the XDNA 2 NPU share one pool, so a model
fits by its file size rather than by a copy per device, and the context you give it adds on top. The
measured rows include a 27B ternary model at 6.7 GiB and a 2B ternary model at 1.11 GiB, both running on
this iGPU ([Models measured](models.html)); every ggml weight type loads, from 2-bit ternary to 4-bit
and 8-bit quants. A mixture-of-experts model whose file is larger than memory can keep only the experts
a token routes to and read the rest from an NVMe drive ([MoE streaming](moe-streaming.html)).

What you should not expect: the NPU route is in progress — correctness first, speed next — so it is a
second device to try beside the GPU, not a replacement for it ([NPU engine](npu.html), [Hybrid](hybrid.html)).
Nothing here needs a cloud account, and nothing leaves the machine.

## The GPU: Radeon 8060S through HRX

The engine's one GPU route is HRX: AMD's ggml-hrx with its Loom kernels, plus our own HIP kernels,
in one llama.cpp build. HRX runs every graph node of every model and mode we test on the Strix Halo
GPU: 43 of 43 configurations in the 2026-10-20 census, with 0 nodes on the CPU
([HRX](hrx.html), [Every node on the GPU](blog-every-node-on-hrx.html)). Every ggml weight type runs
on it, including NVFP4, Q2_0, MXFP4 and the ternary TQ, PTQ and PQ formats, so any GGUF
quantization loads, from Unsloth's dynamic quants to [BitNet b1.58](blog-bitnet-b158-on-hrx.html).

## The NPU: XDNA 2 on Linux

The [NPU engine](npu.html) runs models on the XDNA 2 NPU on Linux, on our own runtime and kernels.
It is in progress, correctness first and speed next; Qwen3-0.6B decodes at 88.6 tok/s on it in the
release gate. The NPU and the GPU were measured running at the same time, forty repetitions with no
hang and no corruption ([the measurement](blog-gpu-and-npu-at-the-same-time.html)), and the
[hybrid route](hybrid.html) puts the prompt on one device and the generated tokens on the other.
PrismML's ternary Bonsai-2-27B already answers correctly on the NPU
([Ternary Bonsai on the NPU](blog-ternary-bonsai-on-the-npu.html)).

## Measured on the machine

Every number below was taken on a Ryzen AI MAX+ 395 at the current pins; the full table, and how
each number is taken, are on [Models measured](models.html) and [How we measure](bench.html).

| model | route | measured |
|---|---|---|
| Qwen3.8-27B, UD-Q4_K_XL | HRX | decode 36.0 tok/s with MTP on code prompts; 56.6 tok/s with the DFlash2 drafter |
| Qwen3.8-Flash-Next (MoE) | HRX | prefill 287 tok/s, decode 24.0 tok/s |
| Zyphra ZAYA1-8B, Q4_K_M | HRX | decode 157 tok/s |
| PrismML Ternary-Bonsai-2-27B, PQ2_0 | HRX | decode 43.3 tok/s with MTP |
| Microsoft BitNet b1.58 2B-4T, TQ2_0 | HRX | decode 123.4 tok/s |
| Qwen3-0.6B | NPU | decode 88.6 tok/s in the release gate |

Speculative decoding pays on the dense models: the model's own MTP head, or a separate drafter such
as DFlash2, guesses several tokens that the model checks in one pass. On Qwen3-Coder-30B-A3B, a MoE
already at 88 tok/s, every draft model we tried was slower
([Speculative decoding: where it pays](blog-speculative-decoding-where-it-pays.html)).

## Lemonade Server and the OpenAI API

The engine runs inside [Lemonade](lemonade.html) as its `onebit` backend, and that recipe passes
Lemonade's own LLM test suite on HRX: 31 of 31 tests run, all pass. Lemonade is what you talk to,
with its catalog, downloads, router and web UI; [1bit serve](serve.html) exposes nothing but an
OpenAI-compatible API, so any OpenAI client works with it. On Ubuntu 26.04 the engine plugs into the
stock `lemond` from Lemonade's PPA.

## Where it ships

The engine ships inside those packages once a release has passed its checklist ([Releases](releases.html)). The
source is Apache-2.0 on [GitHub](https://github.com/1bit-MONSTER/engine), and questions are answered in the
[FAQ](faq.html).
