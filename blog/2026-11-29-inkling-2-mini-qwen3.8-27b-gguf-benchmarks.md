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
tags: inkling, inkling-2-mini, qwen3.8, qwen3.8-27b, gguf, gguf-benchmark, quantization, unsloth, unsloth-dynamic, ud-quants, ud-q4_k_xl, imatrix, bartowski, ggml-org, lmstudio, kld, kl-divergence, perplexity, gsm8k, tokens-per-second, benchmarks, leaderboard, nvfp4, mxfp8, native-fp4, loom, hrx, mtp, speculative-decoding, dflash, strix-halo, ryzen-ai-max-395, ryzen-ai-max-plus-395, amd-ryzen-ai, radeon-8060s, gfx1151, local-llm, local-ai, on-device-ai, self-hosted-ai, open-weights, lemonade, lemonade-server, llama-cpp, linux-ai, ai-pc, mini-pc
title: Inkling-2-Mini and Qwen3.8-27B GGUF benchmarks
summary: Every Inkling-2-Mini and Qwen3.8-27B GGUF quant measured on one AMD Strix Halo: KL divergence, top-1, tok/s, GSM8K, and which quant to pick per memory size.
dataset: inkling-2-mini-gguf-leaderboard
dataset: qwen3.8-27b-gguf-leaderboard

# Inkling-2-Mini and Qwen3.8-27B GGUF quants, measured on Strix Halo

Which GGUF of Inkling-2-Mini or Qwen3.8-27B should you download for an AMD Ryzen AI MAX+ 395? We measured
every quant the main publishers ship (Unsloth Dynamic, ggml-org, bartowski, LM Studio and ours) on one
Strix Halo machine, with one engine build, and put the numbers in two tables you can sort and download.

<!-- TODO(cl-lb): "Which quant should I pick" summary per memory size, from the measured rows only. -->

## How we measured

- **Hardware:** one AMD Ryzen AI MAX+ 395 with 128 GB of unified memory (Radeon 8060S iGPU, gfx1151), running
  1bit OS. One engine build for every row: v2026.49-rc1 <!-- TODO: engine commit + llama.cpp build -->.
- **Accuracy (KL divergence, top-1):** each file's next-token distribution is compared with a reference over a
  fixed text. Inkling-2-Mini's reference is the original Thinking Machines checkpoint; Qwen3.8-27B's is the
  BF16 GGUF. Lower KL divergence means closer to the original; "same top-1" is how often both pick the same
  most likely token. For a fine-tune, KL divergence measures how far it moved from the base model, not its
  quality.
- **Speed:** prompt tokens per second at 512 and about 6,000 tokens, and decode tokens per second, greedy,
  through the route the engine serves the file on (Loom or llama.cpp), with and without a draft model.
- **GSM8K:** the first 40 problems of a fixed 200-problem sample, greedy, thinking off (Inkling-2-Mini also
  with thinking on).
- **Peak GPU memory** while serving at 16K context.

## Inkling-2-Mini

<!-- TODO(cl-lb): headline row = our native NVFP4 + MXFP8 Loom route (no repo link), then the table:
     site/assets/data/inkling-2-mini-gguf-leaderboard.table.html. -->

## Qwen3.8-27B

<!-- TODO(cl-lb): table site/assets/data/qwen3.8-27b-gguf-leaderboard.table.html, the top-25 HF rows,
     not-runnable rows with their reason. -->

## Download the data

Both tables as CSV and JSON: <!-- TODO links to assets/data/*.csv|json -->

## Frequently asked questions

### Which Inkling-2-Mini GGUF should I use on Strix Halo?

<!-- TODO from measured rows -->

### Which Qwen3.8-27B GGUF should I use on Strix Halo?

<!-- TODO from measured rows -->
