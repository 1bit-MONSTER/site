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
tags: npu, xdna2, ternary, bonsai, ryzen-ai, work-in-progress
title: Ternary Bonsai-2-27B on the Ryzen AI NPU
summary: PrismML's Ternary-Bonsai-2-27B now answers correctly on the XDNA 2 NPU (device cosine 0.9908, argmax identical to the engine) and decodes at 8.87 s/token, from 11.5; the per-role kernel design is at its measured ceiling, and a fused per-layer design is the next step.

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

## Where the ceiling is

Measured end to end, the per-role kernel design (one kernel per role: projection, attention,
gate, and so on, each a separate dispatch over the whole array) moves 2.85 to 3.1 GB/s of
weights. A 27B ternary file at that rate is seconds per token, which is what the number above
is. The design has reached what it can do; the next step is a fused per-layer kernel, one
dispatch per layer that keeps the activations on the array between roles. The reference figure
for that design is 24 GB/s. It is not built yet, and until it is, the Bonsai row for the NPU
stays a correctness result, not a speed.

The NPU route and its current state are on [NPU engine](../docs/npu.md); the model's HRX numbers
(43.3 tok/s with MTP in PQ2_0) are in [Models measured](../docs/models.md).

Sources: [engine #661](https://github.com/1bit-MONSTER/engine/pull/661), [docs/npu.md](../docs/npu.md).
