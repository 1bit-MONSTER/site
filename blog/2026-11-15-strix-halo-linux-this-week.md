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
tags: weekly, strix-halo, ryzen-ai-max, linux, npu, hrx, bosgame
title: Strix Halo Linux LLM engine: 31 Oct to 15 Nov
summary: Two weeks of the 1bit engine, the local LLM inference engine for Strix Halo Linux: open issues from 30 to 6, an MTP crash fixed, new CI gates, Bosgame M5 USB.

# This week in the engine

For two weeks the 1bit engine, the local LLM inference engine for the AMD Ryzen AI Max+ 395 (Strix Halo)
on Linux, fixed open issues before building anything new: from 30 open engine issues to 6. Along the way
a crash in the MTP drafter was found and fixed, the CI gained checks that catch whole classes of mistakes
before review, and the Bosgame M5's dead USB-C ports turned out to have a one-line fix.

> **Update (2026-11-22):** v2026.47 is the first published release of the engine. What ships, how it was measured on the hardware and how to get it: [the v2026.47 release post](2026-11-22-v2026.47-release.md).

## Why fix every issue first?

The release is held until every issue is fixed. So from 31 October the work went to open issues first,
oldest first, with new features after. Between 31 October and 15 November, 1,220 pull requests were
merged into the engine, 1,764 in all since the repository started. Each one went through review and the
merge loop, and every pin change also went through the hardware gate on a Strix Halo board.

## What broke, and what fixed it?

**The MTP drafter crashed** on the first request to any GGUF that carries its own MTP head, on the GPU
route. The crash was found by serving such a file on engine main, and the fix came in with the llama.cpp
pin ([#2433](https://github.com/1bit-MONSTER/engine/issues/2433), fixed by
[#2431](https://github.com/1bit-MONSTER/engine/pull/2431)).

**The Lemonade fork sync failed on a cherry-pick that had become empty**, because upstream already had
the change. An empty cherry-pick now counts as a skip, not a failed port
([#2454](https://github.com/1bit-MONSTER/engine/pull/2454)).

## What do the new CI gates check?

Each of these answers one question about a branch before a reviewer has to:

- **pre-pr-checks** runs the repository's own checks on a branch, including the stale-branch and
  registry-loss checks, and says when the tree is dirty
  ([#2396](https://github.com/1bit-MONSTER/engine/pull/2396),
  [#2401](https://github.com/1bit-MONSTER/engine/pull/2401)).
- **branch_stale_check** names the files a branch that is behind main would write back over newer work
  ([#2398](https://github.com/1bit-MONSTER/engine/pull/2398)).
- **guard_loss_check** reports a refusing or asserting condition that a change deleted
  ([#2429](https://github.com/1bit-MONSTER/engine/pull/2429)).
- **tests_referenced** now requires every test script to be invoked by a registered test, not just
  mentioned somewhere ([#2460](https://github.com/1bit-MONSTER/engine/pull/2460)).

## What moved on the GPU route?

The GPU route runs the Radeon 8060S through HRX with our own HIP kernels ([HRX](../docs/hrx.md)). Its two
pins moved forward, each through the hardware gate:

- the gpu-kernels pin moved twice, once for the prefill route on the 27B Q4_K model and once for decode
  ([#2449](https://github.com/1bit-MONSTER/engine/pull/2449),
  [#2453](https://github.com/1bit-MONSTER/engine/pull/2453));
- the llama.cpp pin now reads the recurrent state of gated delta-net models in place during decode,
  instead of copying it each step ([#2461](https://github.com/1bit-MONSTER/engine/pull/2461)).

The NPU route, our own runtime for the XDNA 2 NPU, is described on [NPU](../docs/npu.md).

## Do the Bosgame M5's USB-C ports work on Linux now?

Yes. On the Bosgame M5 (board `AXB35-02`), three of the four USB controllers sleep in `D3cold` under
Linux, so only the front USB-A port worked. A one-line udev rule keeps them awake, and with it every
external port enumerated in a plug test on the hardware on 14 November (BIOS 1.10). USB4 devices are
not tested yet. The rule, the check and the per-port table are in
[Bosgame M5 USB-C not working on Linux: the fix](2026-11-15-bosgame-m5-usb-c-linux-fix.md), and the
full record is on [AXB35 USB ports](../docs/axb35-usb-ports.md).

The previous update is [This week in the engine, 30 October](2026-10-30-this-week-in-the-engine.md).
The code is in the [1bit engine repository](https://github.com/1bit-MONSTER/engine), and to run it
from a USB stick, see [Install](../docs/install.md).

## Frequently asked questions

### What is the 1bit engine?

A model-agnostic local LLM inference engine for the AMD Ryzen AI Max+ 395 (Strix Halo) on Linux. It serves GGUF models on the Radeon 8060S through HRX and models on the XDNA 2 NPU, as a backend of Lemonade Server.

### Is the release out?

No. The release is held until every open engine issue is fixed.

### Does the engine use the AMD NPU on Linux?

Yes. It has its own NPU runtime for the XDNA 2 NPU, next to the GPU route through HRX.
