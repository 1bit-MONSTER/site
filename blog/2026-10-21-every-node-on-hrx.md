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
tags: milestone, strix-halo, local-llm, hrx, lemonade, qwen, speculative-decoding, release
image: og-every-node-on-hrx.png
summary: On AMD Strix Halo, all 43 local LLM configurations we test run fully on the GPU with HRX and our HIP kernels, and Qwen3.8-27B decodes at 36 tok/s.

# Every node on the GPU: local LLMs on Strix Halo in Lemonade

On a Ryzen AI Max+ 395 (Strix Halo), the 1bit engine now runs every graph node of every local LLM
and mode we test on the integrated Radeon 8060S GPU, through AMD's HRX runtime and our own HIP
kernels. Nothing falls back to the CPU. Here is what landed ahead of the first release, measured on
that machine.

## 43 of 43 configurations, all on the GPU with HRX

We keep a census of the models people run and the modes they run them in: a short chat, a long
prompt, a q8 KV cache, four requests in parallel, speculative decoding with MTP, embeddings and
reranking. The models are Qwen3 0.6B, 4B and 8B, Qwen3.8-27B, Qwen3-Coder-30B-A3B,
GLM-4.7-Flash, ZAYA1-8B, LFM2, MiniCPM, and the nomic, bge and jina embedding and reranking models.

On 20 October the census found 12 gaps, places where a node still ran on the CPU. All 12 are
closed. The closing census: 43 of 43 runnable configurations with 0 nodes off the GPU, one graph
split, and every request answered ([how HRX runs](../docs/hrx.md);
[#476](https://github.com/1bit-MONSTER/engine/pull/476),
[#480](https://github.com/1bit-MONSTER/engine/pull/480),
[#481](https://github.com/1bit-MONSTER/engine/pull/481)). Among them:

- a q8_0 KV cache, with K and V or K alone, now keeps flash attention on the GPU;
- four parallel requests work on LFM2, ZAYA1-8B and the Qwen3.5/3.8 family;
- Qwen3.8-27B with MTP answers an 8K-token prompt;
- jina-bert's attention, with its ALiBi bias, runs on the GPU.

## Qwen3.8-27B speed with MTP speculative decoding

Qwen3.8-27B (UD-Q4_K_XL) with MTP speculative decoding, greedy 256-token chats:

| prompt | before | now |
|---|---|---|
| code | 25.9 tok/s | **36.0 tok/s** |
| prose | 20.5 tok/s | **26.8 tok/s** |
| short | 21.9 tok/s | **29.9 tok/s** |

The verify step checks four tokens at once. New kernels for 2 to 8 tokens took it from 121 ms to
88 ms ([#487](https://github.com/1bit-MONSTER/engine/pull/487)). Decode without MTP is unchanged
at 12.2 tok/s. The same model reads a 4,096-token prompt at about 575 tok/s. How to run it:
[1bit serve](../docs/serve.md).

## Strict GPU placement by default

A node that quietly runs on the CPU is a slowdown nobody asked for. HRX placement is now strict by
default: if any node of a model would run on the CPU, the load stops with one line that names the
node, its op and its shape, and `--no-strict-device` turns the fallback back on
([#482](https://github.com/1bit-MONSTER/engine/pull/482)).

The hardware gate that every pin change passes now builds our kernels into the server, checks
that every graph of every gate model is on the GPU, adds q8 KV cache rows, and checks every kernel
registration against its compiled code at startup
([#478](https://github.com/1bit-MONSTER/engine/pull/478),
[#484](https://github.com/1bit-MONSTER/engine/pull/484)). That gate caught three bugs this week
before they reached main ([the hardware gate](../docs/hw-gate.md)).

The runtime also got safer: one memory budget for every buffer, coherent host reads, and after a
GPU fault the server refuses new work and exits cleanly, so Lemonade can restart the model
([#486](https://github.com/1bit-MONSTER/engine/pull/486)).

## Inside Lemonade, on Ubuntu 26.04 and as 1bit OS

Lemonade now starts the engine's llama-server directly: one HTTP hop instead of two, one process
fewer, and a quarter of a second off each model load
([#475](https://github.com/1bit-MONSTER/engine/pull/475)). On Ubuntu 26.04 the stock lemond from
the Lemonade PPA can use the engine through a systemd drop-in, with no patch to Lemonade
([#483](https://github.com/1bit-MONSTER/engine/pull/483)). The same build also ships as the 1bit OS
image, a bootable Lemonade appliance ([the engine in Lemonade](../docs/lemonade.md)).

## The NPU engine

The XDNA 2 NPU engine is coming along: correctness first, speed next
([NPU status](../docs/npu.md)). More in a later post.

## When it ships

The first release goes out when every item on our release checklist is done. Three full release
rehearsals this week (build, packages, the OS image booted in a VM, a clean build from the binary
drop) passed end to end ([releases](../docs/releases.md)).
