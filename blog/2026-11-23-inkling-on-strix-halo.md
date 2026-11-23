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
draft: true
tags: inkling, thinking-machines, strix-halo, ryzen-ai-max-395, local-llm, lemonade, hrx, loom, nvfp4, npu, xdna2, long-context, moe
title: Inkling-2-Mini on Strix Halo: 80 tok/s on the GPU, 128K context
summary: Thinking Machines' Inkling-2-Mini runs on the AMD Ryzen AI MAX+ 395 through the 1bit engine's Loom route: 79.9 tok/s code decode, 2,258 tok/s prefill at 16.8k tokens, needle recall at 128K.

# Inkling-2-Mini on Strix Halo, measured

Thinking Machines released the Inkling family this week, and the question we heard most was whether
Inkling-2-Mini runs on a Strix Halo machine. It does. This post is what we measured on one AMD Ryzen AI
MAX+ 395 (128 GB), how we measured it, and how to try it.

## How it runs

The GPU route is Loom. We run Inkling-2-Mini from the
[loom-fun Inkling-2-Mini card](https://huggingface.co/loom-fun/unsloth-Inkling-2-Mini-loom) by Jeremy Fowers and Daniel Holanda on
`hrx-loom`, with the model's mixture-of-experts weights read in their published NVFP4 format. Multi-token
prediction drafts three tokens ahead (d=3). Before a model is routed to Loom in a release, it passes our
gate: its answers are compared against the CPU on the same prompts, and its speed against the fallback
route.

## Speed

Arun Babu Neelicattu published a Strix Halo report for Inkling-2-Mini on Loom with a fixed set of
prompts. We ran the same prompts on our box, three runs each, and report the median in tokens per
second. His numbers are from his report; ours are measured.

| d=3 (MTP) | code | reasoning | 16.8k-token prefill | decode after 16.8k |
|---|---|---|---|---|
| Arun's report | 59.7 | 67.9 | 2,067 | 50.4 |
| ours, balanced power mode | 74.6 | 65.8 | 2,022 | 46.4 |
| ours, performance power mode | **79.9** | **73.9** | **2,258** | **51.7** |

Performance mode lifts every row by 7 to 12 percent over balanced, at a higher power draw (median 93 W
for the whole run, peaks of about 150 W). Balanced mode is the 1bit OS default.

## Long context

Balanced mode, the needle found in every run (18 of 18):

| prompt | prefill tok/s | decode tok/s |
|---|---|---|
| 32K tokens | 1,769 | 66.4 |
| 63K tokens | 1,363 | 41.8 |
| 128K tokens | 912 | 30.7 |

Loading takes 15 s from cold to the first token, 9 s warm.

## Accuracy

Speed is only worth reporting if the answers hold. Every run checks a needle in the long prompts and a
known answer (17 x 23 = 391), and both held on every run. The NVFP4 build we ship by default keeps the
published weights as they are; a faster variant that also re-quantizes attention is measured (decode
+14 to 20 percent) but costs accuracy (top-1 agreement down 2.9 points), so it will be opt-in, labelled
with that cost.

## The NPU

We also ran Inkling on the Ryzen AI NPU, with the native NVFP4 weights: 3.0 to 4.7 tok/s for
Inkling-2-Mini and 3.7 to 4.8 tok/s for TML-d24, whose answers matched the CPU token for token on all
eight test prompts. That is correct but far slower than the GPU, so it stays a research route.

## Try it

Inkling-2-Mini ships in the next 1bit engine test build, as a Loom-routed model in the Lemonade
catalogue. The release page will link here.

Thanks to Thinking Machines for the models, to Jeremy Fowers and Daniel Holanda for the loom-fun card,
and to Arun Babu Neelicattu for publishing his numbers and his method.
