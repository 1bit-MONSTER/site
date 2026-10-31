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
tags: weekly, release, lemonade, hrx, npu, 1bit-os, strix-halo, ryzen-ai-max-395
title: This week in the engine
summary: This week's Lemonade release is the pin, the 1bit OS live image passes 17 of 17 checks on the board with Secure Boot on, the HRX pin carries the DeepSeek-V4.1 port, ONNX Runtime runs in-process with our own execution provider, and the README is simple again.d the two-engine NPU stand.

# This week in the engine

The engine is pinned to this week's Lemonade release, the release candidate's checks are green,
and two measurements this week say plainly where two slow things stand.

## The release candidate

- **Lemonade:** the pin moved to this week's Lemonade release
  ([#641](https://github.com/1bit-MONSTER/engine/pull/641)); the fork sync now ports a release onto
  the fork's main instead of checking out the tag ([#642](https://github.com/1bit-MONSTER/engine/pull/642)).
- **1bit OS:** the live image passes 17 of 17 checks on the board with Secure Boot on. The image
  build now refuses an image whose kernel modules were selected for another kernel
  ([#638](https://github.com/1bit-MONSTER/engine/pull/638)), and the weekly run signs the sealed
  NPU kernel sets between build and package ([#648](https://github.com/1bit-MONSTER/engine/pull/648)).
- **Hardware gate:** fully green at the shipping pin, after the HRX bump to llama.cpp
  d8d2f5b39f22 and hrx-system 82804197bcbe ([#659](https://github.com/1bit-MONSTER/engine/pull/659)).

The tag and the packages are the owner's; the checklist is on [Releases](../docs/releases.md).

## Two measurements, stated as they are

**Flash-Next prefill.** Qwen3.8-Flash-Next prefills at 287 tok/s on HRX. A prefill forward takes
about 1.8 s, of which about 1.0 s is host time between dispatches, not device time. Measured on
the file itself, that gap is a `GET_ROWS` the HRX backend declines, so the operation runs on the
host and the device waits ([#572](https://github.com/1bit-MONSTER/engine/issues/572), written up in
[#646](https://github.com/1bit-MONSTER/engine/pull/646) and on [HRX](../docs/hrx.md)). The fix is a
kernel, not a setting.

**Two engines on the NPU.** `--npu-streams 2` runs a second resident engine on the NPU
([#640](https://github.com/1bit-MONSTER/engine/pull/640)). With both engines on whole-array
kernels, the aggregate throughput is 0.41x of one engine: they contend for the same array, and
each waits for the other. Two engines need kernel sets partitioned to disjoint halves of the
array, one column partition per engine, which is
[#656](https://github.com/1bit-MONSTER/engine/issues/656). Until then the second engine is opt-in
and costs more than it gives.

## Later the same day

- **The HRX pin moved again**, to a fork head that carries six commits: the host-gap profiler,
  the KV cache zero-padding repair, the DeepSeek-V4.1-Flash port, and the `GET_ROWS` fix that
  lets Flash-Next's 320-million-row token table gather on the GPU instead of the CPU
  ([#672](https://github.com/1bit-MONSTER/engine/pull/672), fork
  [#156](https://github.com/1bit-MONSTER/llama.cpp/pull/156),
  [#159](https://github.com/1bit-MONSTER/llama.cpp/pull/159)). Every pin move passes the hardware
  gate on the board first; the recipe for a hand-raised bump is now written down
  ([#675](https://github.com/1bit-MONSTER/engine/pull/675)).
- **ONNX Runtime runs inside the engine**, behind a build flag, with our own execution provider.
  Its first proof is a MatMul on the NPU through an ORT session, repeatable, within 0.5 % of the
  CPU provider's result; a Quark-quantised A8W8 graph runs on it unchanged. The first whole model
  through it is not right yet, and the write-up says so
  ([#647](https://github.com/1bit-MONSTER/engine/pull/647), [ONNX Runtime](../docs/onnx.md)).
- **The NPU and the GPU run at the same time.** A reported hazard said they could not; forty
  measured reps say they can, at a cost of about 13 % of the NPU's weight stream while the GPU is
  busy. The numbers are in [Hybrid](../docs/hybrid.md).
- **The README is simple again**: boot a stick, try it, install it; the technical map moved to
  [How the engine is built](../docs/architecture.md)
  ([#676](https://github.com/1bit-MONSTER/engine/pull/676)).
- The engine became a workload for AMD's Hyperloom tuner
  ([#660](https://github.com/1bit-MONSTER/engine/pull/660)), the daily census and bump workflows
  now report their failures instead of failing silently
  ([#664](https://github.com/1bit-MONSTER/engine/pull/664),
  [#665](https://github.com/1bit-MONSTER/engine/pull/665)), and the kernel arena that scores NPU
  kernels against a byte-exact oracle has its public half in the tree
  ([#668](https://github.com/1bit-MONSTER/engine/pull/668)).

## Merged on 30 October

- [#659](https://github.com/1bit-MONSTER/engine/pull/659) Bump HRX: llama.cpp d8d2f5b39f22 + hrx-system 82804197bcbe
- [#658](https://github.com/1bit-MONSTER/engine/pull/658) q4nx: cross-check our packer against the official converter (#587)
- [#655](https://github.com/1bit-MONSTER/engine/pull/655) Census 2026-10-30
- [#654](https://github.com/1bit-MONSTER/engine/pull/654) census-watch: pin the Q4NX converter and the d3 source, and watch both
- [#649](https://github.com/1bit-MONSTER/engine/pull/649) census-watch: a Q4NX pack for a family with no NPU route is an alert
- [#648](https://github.com/1bit-MONSTER/engine/pull/648) weekly: sign the sealed NPU kernel sets between build and package
- [#646](https://github.com/1bit-MONSTER/engine/pull/646) docs: where a Flash-Next prefill forward's 1.8 s goes, and the ~1.0 s that is not HRX (engine #572)
- [#645](https://github.com/1bit-MONSTER/engine/pull/645) tools: one entry point for the engine#612 demo
- [#644](https://github.com/1bit-MONSTER/engine/pull/644) docs: what the hybrid route costs at this pin, and why its row is not here (engine#612 item 3)
- [#643](https://github.com/1bit-MONSTER/engine/pull/643) bench: HRX batched decode on Qwen3-Coder-30B-A3B at the current pin (engine#612 item 2)
- [#642](https://github.com/1bit-MONSTER/engine/pull/642) sync-lemonade-fork: port the release onto main, never check out the tag
- [#641](https://github.com/1bit-MONSTER/engine/pull/641) Bump Lemonade: 1bit-MONSTER/lemonade ef0f3b490a27 (upstream release)
- [#640](https://github.com/1bit-MONSTER/engine/pull/640) npu: --npu-streams N, the opt-in second engine, mechanism and its measured cost (engine#612)
- [#638](https://github.com/1bit-MONSTER/engine/pull/638) mkimage: refuse an image whose modules were selected for another kernel
- [#637](https://github.com/1bit-MONSTER/engine/pull/637) npu: cache the dense FFN tail for GDN models by default (#587)
- [#636](https://github.com/1bit-MONSTER/engine/pull/636) weekly: bound the bump CI wait and do not wait on a queued pr_agent

Sources: [#641](https://github.com/1bit-MONSTER/engine/pull/641), [#642](https://github.com/1bit-MONSTER/engine/pull/642), [#638](https://github.com/1bit-MONSTER/engine/pull/638), [#648](https://github.com/1bit-MONSTER/engine/pull/648), [#659](https://github.com/1bit-MONSTER/engine/pull/659), [#572](https://github.com/1bit-MONSTER/engine/issues/572), [#646](https://github.com/1bit-MONSTER/engine/pull/646), [#640](https://github.com/1bit-MONSTER/engine/pull/640), [#656](https://github.com/1bit-MONSTER/engine/issues/656), [docs/releases.md](../docs/releases.md).
