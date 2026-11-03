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
tags: milestones, release, v2026.44, strix-halo, ryzen-ai-max-395, local-llm, lemonade, hrx, npu, xdna2, bitnet, ternary, 1bit-os, puppy-linux, amd-npu-linux
title: Strix Halo LLM engine: milestones to v2026.44
summary: Ten weeks of the 1bit engine, local LLMs on the Ryzen AI MAX+ 395 GPU and NPU inside Lemonade, from the first commit to the first release, v2026.44.

# From the first commit to the first release: the 1bit engine on Strix Halo

The 1bit engine runs local LLMs on the AMD Ryzen AI MAX+ 395 (Strix Halo): on the Radeon 8060S
iGPU through AMD's HRX runtime with our own HIP kernels, and on the XDNA 2 NPU through our own
runtime, all inside AMD's Lemonade Server. This post is the whole road from the clean repository
on 22 September 2026 to the first release, v2026.44, with every measured number linked to the
post or document it came from, and with a plain list of what was and was not tested.

The engine is Apache-2.0 and lives at
[github.com/1bit-MONSTER/engine](https://github.com/1bit-MONSTER/engine). It is model agnostic:
one binary serves Qwen3, Qwen3.8, ZAYA1, BitNet b1.58, ternary Bonsai-2, GLM and DeepSeek-V4.1
files behind the OpenAI-compatible API that Lemonade already gives you. The release ships as
**1bit OS**, a Puppy Linux appliance you boot from a USB stick, and as a package for a Lemonade
you already run on Ubuntu.

If you have a Strix Halo machine, the most useful thing you can do after reading this is to boot
it, run a model, and tell us what broke. The last two sections say how.

## What the 1bit engine is: Strix Halo LLM inference inside Lemonade Server

The pieces, in the order a request meets them:

- **Lemonade Server** is the server you talk to: its model catalog, its downloads, its router, its
  web UI and its OpenAI-compatible API. The engine is one of its backends, the `onebit` recipe, in
  the same shape as Lemonade's `llama-server` recipe ([the engine in Lemonade](../docs/lemonade.md)).
  The `onebit` recipe passes Lemonade's own LLM test suite on HRX: 29 of 29 tests run, all pass
  ([docs/lemonade.md](../docs/lemonade.md)).
- **The GPU route.** For a GGUF, Lemonade starts the engine's HRX `llama-server` directly, one
  HTTP hop ([#475](https://github.com/1bit-MONSTER/engine/pull/475)). HRX is AMD's HIP Runtime
  Extended behind llama.cpp's `HRX0` device; our llama.cpp fork follows AMD's tested pair, and our
  own HIP kernels are compiled into it ([HRX on the Radeon 8060S](../docs/hrx.md)).
- **The NPU route.** The XDNA 2 NPU runs models through our own NPU runtime and kernels, served by
  `1bit serve` behind the same API ([NPU engine](../docs/npu.md)).

The source in the repository is Apache-2.0. The release binaries also contain two proprietary
components, compiled in: the 1bit NPU runtime and the 1bit HIP kernels for HRX. They are closed
source and ship under the 1bit Binary License, free to use
([README](https://github.com/1bit-MONSTER/engine#license), [releases](../docs/releases.md#private-components)).

## September 2026: the clean repository and the first week of Ryzen AI MAX+ 395 local LLM work

**22 September.** The clean repository started. The engine came out of the older 1bit.MONSTER
monorepo, which was GPL-3.0; the engine is Apache-2.0, with a copyright notice on every file
enforced in CI and every upstream credited in its NOTICE
([1bit.MONSTER is now 1bit engine](2026-09-24-new-direction-from-1bit-monster.md)).

**23 September: inside Lemonade, not around it.** The first version ran Lemonade's server core
inside the `1bit` process. A review from geramyL, a moderator on Lemonade's Discord, pointed out
that the engine should be embedded into Lemonade instead, and on 23 September the vendored
Lemonade and every local delta were removed; `1bit serve` took over what the local recipes did
([docs/lemonade.md](../docs/lemonade.md#how-it-got-here)). Every later milestone sits on that
decision.

**24 September: the first week.** In three days the engine came up on every device it then
targeted, each step verified on the hardware before it merged
([The first week of 1bit engine](2026-09-24-first-week-milestones.md)):

- The XDNA 2 NPU ran Qwen3-0.6B end to end, served inside Lemonade
  ([#8](https://github.com/1bit-MONSTER/engine/pull/8), [#9](https://github.com/1bit-MONSTER/engine/pull/9)).
- Our patches made HRX correct on more models: `test-backend-ops` on `HRX0` went from about 1,150
  failures to 791 passing and 0 failing ([#29](https://github.com/1bit-MONSTER/engine/pull/29)).
- Hugging Face `tokenizers` v0.23.2 behind our C ABI reads any model's `tokenizer.json`,
  byte-exact on 18 models ([#19](https://github.com/1bit-MONSTER/engine/pull/19)).
- The Linux kernel was pinned to upstream v7.3-rc4 with `amdxdna` in-tree
  ([#17](https://github.com/1bit-MONSTER/engine/pull/17)).

The same day, HRX decoding past 256 tokens of KV cache was fixed (one missing bound in the
cooperative attention path), and we published which Unsloth Dynamic file to download for five
popular models: UD-Q4_K_XL is the lean pick on every model we measured (the smallest file that
stays within a KL divergence of 0.03), UD-Q5_K_XL the accurate one, and the 2-bit files cost
KL 0.11-0.23 at these sizes
([HRX long prompts and Unsloth sweet spots](2026-09-24-hrx-long-prompts-and-ud-sweet-spots.md)).
Measured against the same BF16 Qwen3.8-27B, UD-Q4_K_XL kept the top token the same 95.3% of the
time at KL 0.008, and PrismML's trained-ternary Bonsai-2-27B in PQ2_0 matched its own F16 to KL
0.00014 on the CPU ([Smaller files](2026-09-24-smaller-files-unsloth-rocmfpx-ternary.md)).

**24 September: speculative decoding, measured both ways.** Qwen3.8-27B's own MTP head took
decode to 2.3-2.9x on every prompt with the default draft length, and 3.4x on code with longer
drafts. On Qwen3-Coder-30B-A3B, a mixture of experts with 3B parameters active per token, every
draft model we tried was slower than no drafting. The rule we took from it: speculative decoding
pays on dense models that bring their own drafter, not on small-active MoE models
([Speculative decoding: where it pays](2026-09-24-speculative-decoding-where-it-pays.md)).

**25 September: the NPU drafts, the GPU checks.** Qwen3-0.6B on the NPU drafted for Qwen3-32B on
the GPU: 10.7 to 23.4 tok/s, 2.19x, at six drafted tokens per round
([The NPU drafts, the GPU checks](2026-09-25-the-npu-drafts-the-gpu-checks.md)). Drafting on the
GPU itself was still a little faster in that first version; what the NPU gave was the drafting
done on silicon that was otherwise idle.

**26 September: Zyphra's family and experts from the drive.** ZAYA1-8B, ZAYA1-74B-preview,
ZAYA1-VL-8B and the older Zamba and BlackMamba models ran end to end, each checked against
Zyphra's or transformers' reference; ZAYA1-VL-8B agreed with Zyphra's own FP32 code at 100 of 101
teacher-forced positions. The model registry reached 323 Hugging Face architectures mapped to a
backend
([Zyphra family, older architectures, experts from the drive](2026-09-26-zyphra-family-old-architectures-experts-from-the-drive.md)).

**27 September: the HRX decode race, solved.** HRX's split flash-attention decode kernel gave
different answers to identical requests and sometimes faulted the GPU. The cause was one barrier
that fenced shared memory but not global memory. After the fix, under forced queue evictions,
Qwen3-Coder-30B-A3B went from 1 correct run in 8 to 8 in 8, and greedy Qwen3-0.6B from 13-34
divergent answers per ~177 requests to none in 354
([Milestone: the HRX decode race is solved](2026-09-27-hrx-decode-race-solved.md)).

**28 September: routing and drafters.** The Laya router, a small decision model, now classifies
each conversation (code, prose, short answer, long document) instead of guessing a device, and is
right 95.5% of the time on 200 hand-labelled requests
([Laya routing](2026-09-28-laya-routes-by-request-class.md)). The DFlash2 drafter from z-lab and
Inco reached 45.7 tok/s on code for Qwen3.8-27B through `1bit serve --dflash`
([Qwen3.8-27B with DFlash2](2026-09-28-qwen38-27b-dflash2-and-hadamard.md)).

**29 September: the direction.** The engine set its course on HRX plus the NPU, with Vulkan kept
as the default only until HRX met the gates written down in
[RFC #213](https://github.com/1bit-MONSTER/engine/discussions/213). Laya's scorer moved to HRX at
15-16 ms a decision, against 538 ms on the CPU, at the same 95.5% accuracy
([Where the engine is going](2026-09-29-hrx-and-npu-direction.md)).

Several September numbers above were taken on Vulkan or ROCm builds that the engine no longer
ships. Each of those posts carries a dated update that says so; the measurements stand as
measured, on the route they were measured on.

## October 2026: HRX and our own HIP kernels on the Radeon 8060S

**4 October: one GPU route.** HRX met the gates of RFC #213, and the engine became HRX with our
HIP kernels plus the NPU engine, embedded in Lemonade. The Vulkan, ROCm and CUDA builds were
removed ([#306](https://github.com/1bit-MONSTER/engine/pull/306),
[README](https://github.com/1bit-MONSTER/engine#milestones)). Lemonade keeps serving those
devices with its own backends; the engine does the part Lemonade does not have.

**20 October: one hop, stock Lemonade.** Lemonade starts the engine's llama-server directly: one
HTTP hop instead of two, one process fewer, and a quarter of a second off each model load
([#475](https://github.com/1bit-MONSTER/engine/pull/475)). On Ubuntu 26.04 the stock `lemond` from
the Lemonade PPA can use the engine through a systemd drop-in, with no patch to Lemonade
([#483](https://github.com/1bit-MONSTER/engine/pull/483)).

**21 October: every node on the GPU.** We keep a census of the models people run and the modes
they run them in: short chat, long prompt, q8 KV cache, four parallel requests, MTP, embeddings
and reranking. The closing census: **43 of 43** configurations with 0 nodes off the GPU
([Every node on the GPU](2026-10-21-every-node-on-hrx.md)). Placement became strict by default:
if any node of a model would run on the CPU, the load stops with one line naming the node, its op
and its shape ([#482](https://github.com/1bit-MONSTER/engine/pull/482)). And every HRX pin change
now passes a hardware gate on a Strix Halo box before it merges
([the hardware gate](../docs/hw-gate.md)).

## Run Qwen3 27B locally on AMD: Qwen3.8-27B with MTP on HRX

The model we measure most is Qwen3.8-27B (Unsloth UD-Q4_K_XL). Without drafting it decodes at
12.2 tok/s on HRX, because every token reads the whole file. With its own MTP head, greedy
256-token chats ([Every node on the GPU](2026-10-21-every-node-on-hrx.md)):

| prompt | before the verify rework | after ([#487](https://github.com/1bit-MONSTER/engine/pull/487)) |
|---|---|---|
| code | 25.9 tok/s | **36.0 tok/s** |
| prose | 20.5 tok/s | **26.8 tok/s** |
| short | 21.9 tok/s | **29.9 tok/s** |

With the DFlash2 drafter it decodes at 56.6 tok/s on code prompts on HRX, and it reads a
4,096-token prompt at 560 to 585 tok/s depending on the batch size
([Models measured](../docs/models.md), [Every node on the GPU](2026-10-21-every-node-on-hrx.md)).

More October numbers from the same box, from the release notes of the 23 October candidate
([releases](../docs/releases.md)):

- **Long context on gated-attention models** ([#500](https://github.com/1bit-MONSTER/engine/pull/500)):
  Qwen3.5-4B at 32K decodes at 47.1 tok/s, from 23.7.
- **Qwen3.8-Flash-Next** ([#494](https://github.com/1bit-MONSTER/engine/pull/494)): its MoE formats
  on HRX took decode from 5.1 to 26 tok/s, 50 with MTP.
- **Many users at once**, aggregate at 8 concurrent requests (90 W cap): Qwen3.8-27B 50.7 tok/s,
  Qwen3-Coder-30B-A3B 138.1, Qwen3.5-4B 194.3.
- **A long-standing GPU fault, closed**: the CWSR soak behind engine issue 315 passed 37 arms over
  9 h 03 min with 0 faults ([#518](https://github.com/1bit-MONSTER/engine/pull/518)).

## BitNet b1.58 on an AMD GPU, and ternary Bonsai-2-27B on HRX

Ternary models store each weight as -1, 0 or +1. The ternary TQ1_0, TQ2_0, PTQ and PQ formats are
full matrix-multiply formats on HRX, and a TQ2_0 file is repacked once at load onto the
packed-ternary layout our decode kernel reads
([llama.cpp fork #147](https://github.com/1bit-MONSTER/llama.cpp/pull/147)).

- **Microsoft BitNet b1.58 2B-4T**, the TQ2_0 GGUF Microsoft publishes (1.11 GiB, 2.06 bits per
  weight), runs end to end on the Radeon 8060S with every node on HRX. Perplexity is 102.42 on HRX
  against 102.56 on the CPU for the same file, and decode is 123.4 tok/s, from 101.6 before the
  repack, on the same binary ([BitNet b1.58 on HRX](2026-10-30-bitnet-b158-on-hrx.md)).
- **PrismML Ternary-Bonsai-2-27B** in PQ2_0 (6.7 GiB, against 50 GiB in F16) decodes at 43.3 tok/s
  with MTP on HRX ([Models measured](../docs/models.md)).

A 27B model in under 7 GiB, at that speed, on an integrated GPU, is the clearest case for the
formats.

## XDNA 2 NPU LLM on Linux: what the NPU does today

The NPU work is the slowest-moving and the most often asked about, so here it is in one place.

- **Since the first week**, the NPU route has served Qwen3-0.6B inside Lemonade. The release
  package carries the NPU runtime compiled into `1bit` and sealed, signed kernel sets, and serves
  dense Qwen3 (0.6B, 1.7B and 4B) on the NPU ([releases](../docs/releases.md#the-npu-engine)).
- **Ternary Bonsai-2-27B answers correctly on the NPU** (30 October): cosine 0.9908 against the
  engine's reference, with the same argmax token. Its decode went from 11.5 to 8.87 seconds per
  token, then to 4.10-4.29 s/token from weight layout alone, bit-identical output. That is a
  correctness result with a dated speed, not a speed claim
  ([Ternary Bonsai-2-27B on the Ryzen AI NPU](2026-10-30-ternary-bonsai-on-the-npu.md)).
- **The GPU and the NPU run at the same time** (30 October). Forty measured reps, 160 byte-exact
  checks and zero GPU resets or ring timeouts in the kernel log say they can, with the fabric
  clock changing level mid-run. A busy GPU costs the NPU about 13% of its weight stream through
  shared memory bandwidth ([GPU and NPU at once](2026-10-30-gpu-and-npu-at-the-same-time.md),
  [#673](https://github.com/1bit-MONSTER/engine/pull/673)).
- **Two engines on one NPU do not pay yet**: with both on whole-array kernels the aggregate is
  0.41x of one engine, so the second engine stays opt-in
  ([#640](https://github.com/1bit-MONSTER/engine/pull/640),
  [This week in the engine](2026-10-30-this-week-in-the-engine.md)).
- **ONNX Runtime runs inside the engine** behind a build flag, with our own execution provider:
  a MatMul on the NPU through an ORT session, within 0.5% of the CPU provider's result; the first
  whole model through it is not right yet ([#647](https://github.com/1bit-MONSTER/engine/pull/647),
  [ONNX Runtime](../docs/onnx.md)).

Our NPU kernels and the NPU runtime are closed source. Everything else about the route, the model
directory format, `plan.json`, how `1bit serve` runs an NPU model, is in the open in
[docs/npu.md](../docs/npu.md).

## The week of 30 October: Lemonade release pin, DeepSeek-V4.1, Flash-Next

The engine is pinned to Lemonade's releases: the pin moves when Lemonade releases
([#641](https://github.com/1bit-MONSTER/engine/pull/641)), and the fork sync ports a release onto
the fork's main ([#642](https://github.com/1bit-MONSTER/engine/pull/642)). The HRX pin moved to a
fork head carrying the DeepSeek-V4.1-Flash port and a `GET_ROWS` fix that lets Flash-Next's large
token table gather on the GPU ([#672](https://github.com/1bit-MONSTER/engine/pull/672)).
Qwen3.8-Flash-Next prefills at 287 tok/s and decodes at 24.0 tok/s on HRX
([Models measured](../docs/models.md)); where the rest of its prefill time goes is written up in
[#646](https://github.com/1bit-MONSTER/engine/pull/646). The README went back to three steps:
boot a stick, try it, install it ([#676](https://github.com/1bit-MONSTER/engine/pull/676);
[This week in the engine](2026-10-30-this-week-in-the-engine.md)).

## November 2026: HIP kernels only, and the release gate

**1 November: HIP kernels only.** The DwarfStar route was taken out of the release, and out of the
tree on 2 November, because it is not our HIP kernels; DeepSeek V4.x, GLM 5.x and
Qwen3.8-Flash-Next run on HRX instead
([#770](https://github.com/1bit-MONSTER/engine/pull/770),
[#827](https://github.com/1bit-MONSTER/engine/pull/827), [releases](../docs/releases.md)).

**1 November: a candidate pulled back.** Release candidate 19 passed every software gate:
54 of 54 build tests, 1,959 of 1,959 kernel ops on the box's GPU with 0 ring timeouts, and the
QEMU run that boots the stick, installs to a disk and boots the installed disk. It was written to a
stick and never booted on the hardware, so it was pulled back to a draft
([releases](../docs/releases.md#v202644-1-nov-2026-the-first-release-a-draft)). The rule since
then: the whole gate, on the hardware, on the bytes that ship.

**2 November: the census.** The daily census counted 432,540 text-generation models on Hugging
Face, 342,299 with an architecture (2,974 architectures): 94.46% mapped to a backend, 63.68%
checked ([#815](https://github.com/1bit-MONSTER/engine/pull/815), [registry](../docs/registry.md)).

**2 November: candidate 20 on the board.** The engine build that becomes v2026.44 (engine commit
`a5271d92b287`) booted from a live USB stick on a Ryzen AI MAX+ 395 with Secure Boot on, and
`1bit-release-check` on the stick read `RESULT: PASS (19 checks, no failures)`.

**2 November: 1bit OS becomes the Puppy appliance.** The release image is a Puppy Linux
appliance with Lemonade and the engine inside, and the release waits until that appliance passes
its acceptance list on the hardware ([1bit OS on the wiki](https://github.com/1bit-MONSTER/engine/wiki/1bit-OS)).

## The first release: v2026.44

v2026.44 is the first published release of the 1bit engine. Releases are tagged
`v<ISO year>.<ISO week>`, like Lemonade's own versions ([releases](../docs/releases.md)). It comes
two ways:

- **`1bit-os-v2026.44.img.zst`: 1bit OS, a Puppy Linux AI appliance** (next section).
- **`lemonade-onebit-v2026.44-linux-x86_64.tar.zst`**: Lemonade Server from our fork with the
  `onebit` backend and the engine in `1bit/`, for an Ubuntu that already runs ROCm. Unpack it
  anywhere and start Lemonade through `lemond-onebit`, which points Lemonade's `onebit` backend at
  the packaged engine ([releases](../docs/releases.md#what-a-release-carries)).

Both serve the OpenAI API on a port, and both carry Lemonade's web app.

## Puppy Linux AI appliance: what 1bit OS is

1bit OS is `ResolutePup64`, built with woof-CE on the Ubuntu 26.04 "resolute" base, with Lemonade
Server and the engine embedded in it and our own MOK-signed `7.3.0-rc4-1bit-perfopt` kernel
underneath ([1bit OS](https://github.com/1bit-MONSTER/engine/wiki/1bit-OS)):

| | |
|---|---|
| Secure Boot | on: shim, our MOK-signed grub, our MOK-signed kernel, our signed modules |
| boot | **headless by default**: no X; a second boot entry, `1bit OS (desktop)`, starts Puppy's JWM desktop |
| console | a 1bit OS menu on tty1 with the machine's address and the Lemonade URL |
| userland | `bash`, `sudo`, `apt`, `sshd`: an ordinary Linux box |
| persistence | the `1BIT-DATA` partition, Puppy's save layer: models, Lemonade's config and cache, SSH keys |
| serves | Lemonade Server on port 13305 with its web app, its catalog and the engine as its `onebit` backend |

It boots headless because it is a server first: the desktop is in the image for anyone who
wants it, and is started only from its own boot entry. The same system goes onto a disk with
`1bit-install <disk> --yes`.

### How to boot the stick

1. Download `1bit-os-v2026.44.img.zst` from the
   [releases page](https://github.com/1bit-MONSTER/engine/releases) and check it against the
   release's `SHA256SUMS`.
2. Write it to a USB stick of 16 GB or more (the image is about 9 GB), for example with
   `zstd -dc 1bit-os-v2026.44.img.zst | sudo dd of=/dev/sdX bs=4M conv=fsync status=progress`,
   where `/dev/sdX` is the stick and nothing else.
3. Boot the Ryzen AI MAX+ 395 machine from the stick, with Secure Boot left on.
4. The console menu shows the machine's address and the Lemonade URL. Lemonade is up with the
   engine behind it: the GPU through HRX and our HIP kernels, the NPU through our own runtime.

### How clients connect to Lemonade

1bit OS is reached over the network; nothing has to run on the machine's own screen.

- **In a browser**: Lemonade's web app at `http://<address>:13305/`.
- **From any OpenAI client**: point it at Lemonade's API under `http://<address>:13305/api/v1`
  with the server's API key, which the console menu can show.
- **From a phone**: Lemonade Mobile connects to the same server.
- **Over SSH**: `sshd` is in the image, with your keys kept on `1BIT-DATA`.

## What was tested, where, and what was not

Every candidate goes through the same gate before a tag is cut ([releases](../docs/releases.md)):
build, `ctest` and package; the hardware gate at the shipped pins (every kernel op against the
reference, known answers, KLD against the release pin, long-prompt needles, placement); the NPU
route through the sealed kernel sets; image checks; the QEMU release tests; the stick written and
read back byte for byte; and `1bit-release-check` on the hardware.

What that gave for this release, stated as it stands:

- **Live USB on the hardware: done.** Candidate 20, engine `a5271d92b287`, booted from the stick on
  the board with Secure Boot on, and `1bit-release-check` passed 19 checks with no failures, read
  off the stick's own log.
- **The Puppy appliance on the hardware: booted.** It booted on the Max+ 395 with Secure Boot on,
  with Lemonade answering on port 13305 with its key and 0 `amdxdna` errors
  ([1bit OS](https://github.com/1bit-MONSTER/engine/wiki/1bit-OS)). In the latest board run of the
  appliance, `1bit-release-check` passed 19 checks with no failures, and it went from boot to
  serving in 52 s.
- **Install to disk: proven on the hardware at an earlier candidate, and in a VM for this one.**
  Candidate 18 (31 October) was installed to the internal NVMe of the board and booted from it with
  the stick out, with the release check at 18 checks and no failures both live and installed. For this release the install and
  the boot from the installed disk ran in QEMU: `VMTEST-RELEASE` 10 PASS, 9 SKIP (rows that need
  hardware a VM does not have), 0 FAIL ([releases](../docs/releases.md)). The install on the board's
  own disk has not been rerun for this candidate.
- **Secure Boot: on for every boot, with one open item.** The boot chain is signed end to end and
  the board boots it with Secure Boot on. The check that reads the Secure Boot state back from
  inside the running system is a known open item.
- **NPU speed: not quoted from this run.** The NPU chat row of the candidate's board run is not a
  number we quote; the NPU numbers that are measured under controlled conditions are on
  [NPU engine](../docs/npu.md) and in the posts linked above.

Single-stream decode on Qwen3.8 is behind the fastest Strix Halo engines today. The numbers we
publish are the ones we measured, with the command that produced each, on
[Models measured](../docs/models.md) and the [wiki](https://github.com/1bit-MONSTER/engine/wiki).

## Model agnostic: one binary for every model family

"One binary to rule them all" is the design goal: any Hugging Face architecture, any GGUF
quantization, Ryzen AI NPU packs and ONNX graphs, served by one Lemonade backend
([README](https://github.com/1bit-MONSTER/engine#what-it-is)). Every ggml weight type runs on HRX,
including NVFP4, Q2_0, MXFP4 and the ternary TQ, PTQ and PQ formats
([Models measured](../docs/models.md)). The families checked on this hardware:

| family | where it runs | measured, with the source |
|---|---|---|
| Qwen3 (0.6B, 4B, 8B) | HRX; dense Qwen3 also on the NPU | in the 43-of-43 GPU census ([post](2026-10-21-every-node-on-hrx.md)); NPU ([releases](../docs/releases.md#the-npu-engine)) |
| Qwen3.5-4B | HRX | 47.1 tok/s decode at 32K context ([releases](../docs/releases.md)) |
| Qwen3.8-27B | HRX | 36.0 tok/s with MTP, 56.6 with DFlash2, on code ([models](../docs/models.md)) |
| Qwen3.8-Flash-Next (MoE) | HRX | prefill 287, decode 24.0 tok/s ([models](../docs/models.md)) |
| Qwen3-Coder-30B-A3B (MoE) | HRX | 138.1 tok/s aggregate at 8 requests ([releases](../docs/releases.md)) |
| Zyphra ZAYA1-8B | HRX | 157 tok/s decode, Q4_K_M ([models](../docs/models.md)) |
| Microsoft BitNet b1.58 2B-4T | HRX | 123.4 tok/s, perplexity within 0.14 of the CPU ([post](2026-10-30-bitnet-b158-on-hrx.md)) |
| PrismML Ternary-Bonsai-2-27B | HRX; NPU (correctness) | 43.3 tok/s with MTP on HRX ([models](../docs/models.md)); cosine 0.9908 on the NPU ([post](2026-10-30-ternary-bonsai-on-the-npu.md)) |
| GLM (GLM-4.7-Flash, GLM 5.x) | HRX | GLM-4.7-Flash in the 43-of-43 census ([post](2026-10-21-every-node-on-hrx.md)); GLM 5.x in the release gate ([releases](../docs/releases.md)) |
| DeepSeek-V4.1-Flash | HRX | ported in the HRX pin ([#672](https://github.com/1bit-MONSTER/engine/pull/672)) |
| gpt-oss-20b | HRX | runs, MXFP4 ([models](../docs/models.md)) |
| LFM2, MiniCPM | HRX | in the 43-of-43 census ([post](2026-10-21-every-node-on-hrx.md)) |
| nomic, bge, jina (embeddings, reranking) | HRX | in the 43-of-43 census ([post](2026-10-21-every-node-on-hrx.md)) |

The registry maps 94.46% of the Hugging Face text-generation models that name an architecture to a
backend, and the daily census reports separately how many have been checked
([registry](../docs/registry.md)). "Mapped" means a backend's code accepts the architecture; it is
not a claim that every one of them has been run.

## How to test it and break it

We would rather hear about a failure from you than find it after a release. Concrete asks:

1. **Hardware reports.** Boot the stick on your Ryzen AI MAX+ 395 machine and open an issue with the
   make and model, the BIOS version, the memory size, whether Secure Boot stayed on, and the output
   of `1bit-release-check`. Machines other than the one we test on are exactly what we lack.
2. **Model coverage.** Load the GGUF you actually use. Placement is strict: if any node of a model
   would run on the CPU, the load stops with one line naming the node, its op and its shape
   ([#482](https://github.com/1bit-MONSTER/engine/pull/482)). That line, pasted into an issue, is
   the most useful bug report we can get.
3. **Bench numbers.** Measure with the repository's own tool, so numbers compare:

   ```sh
   tools/bench.py -m <model>.gguf --config base= --rounds 2 --json my-run.json
   ```

   It starts a fresh `1bit serve` per configuration, measures a long prompt and 256 greedy tokens
   on three chat prompts (code, prose, short), and interleaves rounds so drift hits every
   configuration alike ([how the numbers are measured](../docs/bench.md)). Attach the JSON.
4. **Wrong answers.** If a reply is wrong, run the same request twice and say whether it repeats.
   A known-answer prompt with the exact request body is worth more than a description.
5. **Lemonade clients.** Tell us which OpenAI client, editor plugin or Lemonade client you pointed
   at it, and what did not work.

Issues go to
[github.com/1bit-MONSTER/engine/issues](https://github.com/1bit-MONSTER/engine/issues); there is
also the [Discord](https://discord.gg/fa5m4Vawpa). If you write about what you measured, on Reddit
or anywhere else, include the command and the number, and link the issue if you filed one.

## FAQ

### Does the NPU run LLMs on Linux?

Yes. On the Ryzen AI MAX+ 395, the 1bit engine runs LLMs on the XDNA 2 NPU on Linux through our own
runtime and the upstream `amdxdna` driver. The release serves dense Qwen3 (0.6B, 1.7B, 4B) on the
NPU, and ternary Bonsai-2-27B answers correctly there as work in progress
([NPU engine](../docs/npu.md)).

### Can I run a 27B model on Strix Halo?

Yes. Qwen3.8-27B (UD-Q4_K_XL) decodes at 36.0 tok/s on code prompts with its MTP head on the
Radeon 8060S through HRX, and the ternary Bonsai-2-27B (6.7 GiB) at 43.3 tok/s with MTP
([Models measured](../docs/models.md)).

### Is the 1bit engine open source?

The engine's source is Apache-2.0 at
[github.com/1bit-MONSTER/engine](https://github.com/1bit-MONSTER/engine). The release binaries also
contain two closed-source components, the NPU runtime and our HIP kernels for HRX, under the 1bit
Binary License, free to use. A build from the repository without them runs HRX on the public
kernels only and has no NPU engine ([README](https://github.com/1bit-MONSTER/engine#license)).

### Does it work with Lemonade and OpenAI clients?

It is a Lemonade backend: Lemonade Server is what you connect to, with its web app and its
OpenAI-compatible API, and any OpenAI client works against it. The `onebit` recipe passes
Lemonade's LLM test suite on HRX, 29 of 29 ([the engine in Lemonade](../docs/lemonade.md)).

### Do I need to install Linux to try it?

No. Boot 1bit OS from a USB stick and the machine serves models; install it to a disk with
`1bit-install` only if you want to keep it. If you already run Lemonade on Ubuntu with ROCm, the
`lemonade-onebit` package adds the engine instead.

### Does it work with Secure Boot on?

Yes. The boot chain is shim, our MOK-signed grub, our MOK-signed kernel and signed modules, and the
board boots it with Secure Boot on. The in-system check that reads the Secure Boot state back is a
known open item in this release.

### Does it run BitNet b1.58 on an AMD GPU?

Yes. Microsoft's BitNet b1.58 2B-4T TQ2_0 GGUF runs end to end on the Radeon 8060S through HRX,
every node on the GPU, at 123.4 tok/s decode, with perplexity 102.42 against 102.56 on the CPU
([BitNet b1.58 on HRX](2026-10-30-bitnet-b158-on-hrx.md)).

### Can the GPU and the NPU work at the same time?

Yes. Forty measured reps show no hang and no corrupted NPU output with the GPU busy; a busy GPU
costs the NPU about 13% of its weight stream through shared memory bandwidth
([Hybrid](../docs/hybrid.md)).

### Which GGUF should I download?

For the models we measured, Unsloth's UD-Q4_K_XL is the lean pick and UD-Q5_K_XL the accurate one;
the 2-bit files lose too much at these sizes
([Unsloth sweet spots](2026-09-24-hrx-long-prompts-and-ud-sweet-spots.md)).

## Thank you

To the Lemonade team, whose server this engine lives inside, and to geramyL, whose review put it
there. To AMD's developers, for the XDNA driver and XRT, IRON and Peano, HRX and their tested
llama.cpp integration, which this engine is built on. To the Puppy Linux and woof-CE developers,
whose system 1bit OS is. And to Osmantic / ODS, where all of this started
([README](https://github.com/1bit-MONSTER/engine#thank-you)).
