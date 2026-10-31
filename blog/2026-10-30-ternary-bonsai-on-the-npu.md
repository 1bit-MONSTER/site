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
tags: npu, xdna2, ternary, bonsai, ryzen-ai, work-in-progress, amd-npu-linux
title: Ternary Bonsai-2-27B on the Ryzen AI NPU
summary: PrismML's Ternary-Bonsai-2-27B answers correctly on the XDNA 2 NPU (cosine 0.9908, argmax identical); decode 13.3 to 4.1 s/token in a day, ceiling measured.

# Ternary Bonsai-2-27B on the Ryzen AI NPU

PrismML's Ternary-Bonsai-2-27B now answers correctly on the XDNA 2 NPU, and its decode went from
11.5 to 8.87 seconds per token. This is work in progress: the model runs and is right, and it is
slow, and the measurement says why.

## Correctness

The 27B's attention heads are stored interleaved per value head, and the same interleave shows up
in eight weight families of the model, including the gated delta net's swish gate. Once every
family is read with that interleave, the NPU's output agrees with the engine's: cosine 0.9908
against the engine's reference on the device, and the argmax token is identical. The same check
against FastFlowLM's reference container gives 0.9305, so the NPU route now reproduces the
engine's answer more closely than that container does.

## Decode: 11.5 to 8.87 s/token

Two changes, in [engine #661](https://github.com/1bit-MONSTER/engine/pull/661):

- the M=16 kernel twins: the decode kernels take 16 rows at a time instead of fewer, so a token
  makes fewer dispatches;
- no per-token re-dequant: the ternary weights are dequantized once at load, not again for every
  token.

Together: 8.87 s/token, from 11.5 on the same file and the same device.

## Decode again: 8.87 to 4.1 s/token, by weight layout alone

The same evening, one more change with no kernel edit: the weights are written to the container
in the order the kernel's tiles consume them, so every tile is one contiguous read instead of 64
short runs ([engine #667](https://github.com/1bit-MONSTER/engine/pull/667)). Bit-identical
output, and the decode step went from 8.87 to 4.10 to 4.29 s/token on the same device.

## Where the ceiling is, measured

A pass-through probe, the kernel's data path with the arithmetic removed, says the layout above is
at the limit of that data path: the device is bound by the number of tiles it moves per column, not
by the bytes in them. Two consequences, both measured the same day. First, the file is already
4-bit on disk, and streaming those bytes instead of dequantised 8-bit ones halves the work per
token; that kernel path is built and byte-exact in the private kernel tree and ships when all five
phases of the layer are through their gates. Second, the remaining distance to the stream rate our
small-model route already reaches on this silicon is in the data path itself, which is the next
piece of work. Until the five phases are in, the Bonsai row for the NPU stays a correctness result
with a dated speed, not a claim.

The NPU route and its current state are on [NPU engine](../docs/npu.md); the model's HRX numbers
(43.3 tok/s with MTP in PQ2_0) are in [Models measured](../docs/models.md).

Sources: [engine #661](https://github.com/1bit-MONSTER/engine/pull/661), [docs/npu.md](../docs/npu.md).
