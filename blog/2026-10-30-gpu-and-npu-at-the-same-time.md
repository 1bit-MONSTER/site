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
tags: npu, xdna2, hrx, hybrid, strix-halo, measurement, amd-npu-linux
title: GPU and NPU at once on Strix Halo, measured
summary: Forty reps say the Radeon iGPU and the XDNA 2 NPU run together on Strix Halo with no hang and no corruption; a busy GPU costs the NPU about 13 % of its stream.

# The GPU and the NPU at the same time, measured

For four weeks the fleet that works on this engine ran every NPU job behind the GPU queue. The
reason was a report from another project's documentation: GPU and NPU work at the same time
could hang the machine, or corrupt NPU results, while the GPU's fabric clock (FCLK) changed level.
The suggested fix was to hold FCLK at its top level. We never reproduced it; we just avoided it.

The hybrid route (the prompt on the NPU, the tokens on the GPU) needs both devices busy at once,
so the question had to be settled by measurement.

## Method

The NPU side is the kernel arena's byte-exact oracle: one real decode kernel of the 27B ternary
model, five launches per cell, every output compared byte for byte against the frozen reference.
The GPU side is a looping `llama-bench` on HRX (prefill 512, decode 128) started before the NPU
runs and kept running through them. Four cells, GPU idle or busy times FCLK on auto or held at
the top level, run twice, with the live FCLK level sampled once a second and the kernel log
checked for GPU resets, MODE2 resets and ring timeouts after every cell. The hold cells ran
last, and the box was returned to `auto` and verified before the run was called done.

## Result

| cell | ms per launch, median | GB/s | FCLK levels seen | byte-exact | resets |
|---|---|---|---|---|---|
| GPU idle, FCLK auto | 10.79 | 8.26 | 5, 6 and 7, changing mid-run | 5 of 5 | 0 |
| GPU idle, FCLK held | 10.92 | 8.16 | 7 | 5 of 5 | 0 |
| GPU busy, FCLK auto | 12.04 | 7.40 | 6 and 7, changing mid-run | 5 of 5 | 0 |
| GPU busy, FCLK held | 12.01 | 7.42 | 7 | 5 of 5 | 0 |

Forty reps in total, twenty of them with the GPU busy, 160 byte-exact checks, all passing, and
zero reset or timeout lines in the kernel log in any cell, with the fabric clock demonstrably
changing level in the middle of NPU runs. Kernel 7.3.0-rc4 with the IOMMU PerfOpt backports, SMU
firmware 100.7.0, BIOS 1.09.

So: the hazard does not reproduce on this kernel and firmware. A busy GPU costs the NPU about 13 %
of its weight stream, through shared memory bandwidth, and nothing else. The first pass had
suggested that holding FCLK removes that cost; the second pass did not confirm it, so that claim
is retracted and the box stays on `auto`.

## What changed because of it

NPU jobs no longer queue behind GPU jobs on the development box; they take the NPU device lock
only. Every arena score now records whether the GPU was busy during the launch, so a 13 % dip is
never mistaken for a kernel regression. And the hybrid route is planned around a measured 13 %,
not around a hang. The full table is in [Hybrid](../docs/hybrid.md).

Sources: [engine #673](https://github.com/1bit-MONSTER/engine/pull/673), [docs/hybrid.md](../docs/hybrid.md).
