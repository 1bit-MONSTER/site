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
tags: release, v2026.44, lemonade, hrx, npu, 1bit-os, strix-halo, ryzen-ai-max-395
title: v2026.44: one binary, boot a stick
summary: The first published release of the 1bit engine. A signed live USB that brings up the GPU, the NPU and Lemonade Server on a Ryzen AI MAX+ 395, or one tarball for an Ubuntu that already runs ROCm. What ships, how it was tested on the hardware, and what is not in it.

# v2026.44, the first release

The engine has its first published release. It is one binary with no Python in it, and the
same binary is the whole operating system when you want it to be.

## Two ways to run it

- **Boot a stick.** `1bit-os-v2026.44.img.zst` is a live USB image, Secure Boot signed. Write it
  to a stick of 8 GB or more, boot a Ryzen AI MAX+ 395 machine from it, and Lemonade Server is up
  with the engine behind it: the GPU through HRX and our HIP kernels, the NPU through our own
  runtime. `1bit-install <disk> --yes` puts the same system on a disk.
- **Add it to an Ubuntu that already runs ROCm.** `lemonade-onebit-v2026.44-linux-x86_64.tar.zst`
  is Lemonade Server from our fork with the `onebit` backend and the engine in `1bit/`.

Both talk the OpenAI API on a port, and the Lemonade web app is in the box.

## What is in the box

| component | version |
|---|---|
| engine | the release commit on [Releases](../docs/releases.md) |
| HRX (llama.cpp fork, ggml-hrx) | the pinned fork commit, listed in the release notes |
| hrx-system | `82804197bcbe` |
| Lemonade Server | our fork of the current Lemonade release, `onebit` recipe |
| kernel in the image | `7.3.0-rc4-1bit-perfopt`, MOK-signed |
| NPU kernel sets | sealed and signed sets |

Models in the release gate: the Qwen3.8 family (27B with MTP, Flash-Next), DeepSeek-V4.1,
GLM 5.x, ZAYA1, Bonsai-2 on the NPU, and any GGUF the fork loads. The DwarfStar route is not in
this release; its models are served on HRX.

## How it was tested, all on the hardware

Every candidate goes through the same gate before a tag is cut, and the tag is cut only after the
last candidate has booted from the stick on a real Max+ 395:

- build, `ctest`, package
- the hardware gate at the shipped pins: every kernel op against the reference, known answers,
  KLD against the release pin, long-prompt needles at 7,000 tokens, placement checks
- the NPU route through the sealed kernel sets: oracle, greedy, prefill and reproducibility
- image checks (sealed sets, licences, release identity) and the VM release tests
- QEMU: live boot, run, install to a disk, boot from the installed disk
- the release stick: written and read back byte for byte
- **live USB boot on the board with Secure Boot on**, and `1bit-release-check` run on the live
  stick: `RESULT: PASS (19 checks, no failures)`, read off the stick's own `/data/release-check.log`
- an **installed system** -- live boot, install to a disk, boot from the installed disk -- run in
  **QEMU**, not on the board: `RESULT: PASS (19 checks, no failures)` and `VMTEST-RELEASE PASS (10
  PASS, 9 SKIP, 0 FAIL)`. The install on the hardware is the next release's gate, not this one's

One candidate was pulled back from publication last week because the stick test had not been run
on that exact build. The rule stands: the whole gate, on the hardware, on the bytes that ship.

## What is not in it, said plainly

- The installed appliance is the live image on disk. The next release makes it a full headless OS
  ([#712](https://github.com/1bit-MONSTER/engine/issues/712)).
- No firmware boot entry is written by the installer on this kernel; remove the stick or pick the
  disk in the firmware ([#709](https://github.com/1bit-MONSTER/engine/issues/709)).
- Single-stream decode on Qwen3.8 is behind the fastest Strix Halo engines today. The numbers we
  publish are the ones we measured, on the [leaderboard](../docs/npu-leaderboard.md) and the
  [wiki](https://github.com/1bit-MONSTER/engine/wiki), with the command that produced each.

## License

Source is Apache-2.0. The release binaries also contain two proprietary components compiled in,
the 1bit NPU runtime and the 1bit HIP kernels for HRX, under the 1bit Binary License, free to use.

Thank you to Osmantic / ODS, to the Lemonade team and to AMD's developers.
