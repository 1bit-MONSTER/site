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
tags: bitnet, ternary, hrx, strix-halo, local-llm, quantization, amd-gpu, radeon-8060s
title: BitNet b1.58 runs on HRX
summary: Microsoft's BitNet b1.58 2B-4T in its TQ2_0 ternary GGUF (1.11 GiB) runs end to end on the Radeon 8060S through HRX, perplexity 102.42 against 102.56 on the CPU, and decodes at 123.4 tok/s.

# BitNet b1.58 runs on HRX

Microsoft's BitNet b1.58 2B-4T, in the TQ2_0 ternary GGUF (1.11 GiB, 2.06 bits per weight), now
runs end to end on the Radeon 8060S through HRX. Every node of the graph is on the GPU; nothing
falls back to the CPU. Perplexity on HRX is 102.42 against 102.56 on the CPU for the same file, and
decode is 123.4 tok/s.

## What was measured

| check | result |
|---|---|
| placement | every graph node on HRX0, no CPU fallback |
| perplexity, same file | 102.42 on HRX, 102.56 on the CPU |
| decode, tg128, before the repack | 101.6 tok/s |
| decode, tg128, after the repack | 123.4 tok/s (same binary) |

The TQ1_0 and TQ2_0 ternary formats were already full `mul_mat` formats on HRX. What changed is a
load-time step: a TQ2_0 file is repacked once, as it loads, onto the packed-ternary layout our
decode kernel reads ([llama.cpp fork #147](https://github.com/1bit-MONSTER/llama.cpp/pull/147)).
The same kernel already decodes the packed-ternary Bonsai files; BitNet's weights now take the
same path, which is where the 101.6 to 123.4 tok/s comes from. The binary is the same before and
after; the file is the one Microsoft publishes.

Microsoft's own runtime for these models, bitnet.cpp, ships no AMD GPU path, so this is a way to
run the model on this GPU.

How to run it is the usual: `1bit serve -m <bitnet>.gguf` picks HRX for the file. The formats the
route covers are listed in [HRX on the Radeon 8060S iGPU](../docs/hrx.md), and the number sits
with the other models in [Models measured](../docs/models.md).

Sources: [1bit-MONSTER/llama.cpp #147](https://github.com/1bit-MONSTER/llama.cpp/pull/147), [docs/hrx.md](../docs/hrx.md), [docs/models.md](../docs/models.md).
