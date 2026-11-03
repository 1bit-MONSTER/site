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
tags: release, v2026.44, lemonade, hrx, npu, 1bit-os, puppy-linux, headless, strix-halo, ryzen-ai-max-395
title: v2026.44: one binary, boot a stick
summary: The first published release of the 1bit engine. 1bit OS is a Puppy Linux appliance - Lemonade Server and the engine inside it, headless by default, apt and a persistent data partition - or one tarball for an Ubuntu that already runs ROCm. What ships, how it was tested on the hardware, and what is not in it.

# v2026.44, the first release

The engine has its first published release. It is one binary with no Python in it, and the
same binary is the whole operating system when you want it to be.

## Two ways to run it

- **Boot a stick.** 1bit OS is a **Puppy Linux appliance**: `ResolutePup64`, built with woof-CE on
  the Ubuntu 26.04 "resolute" base, with Lemonade Server and the engine embedded in it and our own
  MOK-signed `7.3.0-rc4-1bit-perfopt` kernel underneath. Download `1bit-os-puppy.img.xz` (2.2 GB
  compressed, 9.1 GB written) and its `SHA256SUMS` from
  [Hugging Face](https://huggingface.co/1bit-MONSTER/1bit-OS) (the repository is private until this
  release is published, so from then on that link is the download) - the image is too big for a GitHub
  release asset, which is capped at 2 GiB - check the checksum, and write it to a stick
  of 16 GB or more (`xz -dc 1bit-os-puppy.img.xz | sudo dd of=/dev/sdX bs=4M conv=fsync status=progress`,
  or balenaEtcher/Rufus in DD mode, which take the `.xz` directly). Boot a Ryzen AI MAX+ 395 from it with Secure Boot on, and Lemonade comes up: the
  GPU through HRX and our HIP kernels, the NPU through our own runtime. It boots **headless** - a
  console login, no X - and the boot menu's `1bit OS (desktop)` entry brings up Puppy's desktop for
  anyone who wants one. `bash`, `sudo` and `apt` work; models, Lemonade's config and your SSH keys
  live on the `1BIT-DATA` partition and survive a reflash. `1bit-install <disk> --yes` puts the same
  system on a disk, firmware boot entry included.
- **Add it to an Ubuntu that already runs ROCm.** `lemonade-onebit-v2026.44-linux-x86_64.tar.zst`
  is Lemonade Server from our fork with the `onebit` backend and the engine in `1bit/`.

Both talk the OpenAI API on a port, and the Lemonade web app is in the box.

## What is in the box

| component | version |
|---|---|
| base | Puppy Linux `ResolutePup64` (woof-CE, Ubuntu 26.04 `resolute`), the same image live and installed |
| boot | headless by default (console login, no X); `1bit OS (desktop)` in the menu starts JWM |
| userland | `bash`, `sudo`, `apt`, `sshd`, `mokutil` |
| persistence | `1BIT-DATA`, which is Puppy's save layer: models, Lemonade's config and cache, SSH keys |
| engine | the release commit on [Releases](../docs/releases.md) |
| HRX (llama.cpp fork, ggml-hrx) | the pinned fork commit, listed in the release notes |
| hrx-system | `82804197bcbe` |
| Lemonade Server | our fork of the current Lemonade release, `onebit` recipe |
| kernel | `7.3.0-rc4-1bit-perfopt`, ours, MOK-signed |
| NPU kernel sets | sealed and signed sets |

Models in the release gate: the Qwen3.8 family (27B with MTP, Flash-Next), DeepSeek-V4.1,
GLM 5.x, ZAYA1, Bonsai-2 on the NPU, and any GGUF the fork loads. The DwarfStar route is not in
this release; its models are served on HRX.

## How it was tested, all on the hardware

Every candidate goes through the same gate before a tag is cut, and the tag is cut only after the
last candidate has booted the appliance on a real Max+ 395:

- build, `ctest`, package
- the hardware gate at the shipped pins: every kernel op against the reference, known answers,
  KLD against the release pin, long-prompt needles at 7,000 tokens, placement checks
- the NPU route through the sealed kernel sets: oracle, greedy, prefill and reproducibility
- the appliance's own gates, in QEMU: it boots on our kernel and layers its SFS (G2); `amdxdna` and
  `ec_su_axb35` are present, signed and verify against the enrolled MOK (G3); the save layer
  persists across a reboot on `1BIT-DATA` (G7); the init cannot exit, with the boot media pinned and
  with the pin deliberately broken; `vm-check` 19 PASS / 0 FAIL with Secure Boot on
- **the appliance booted on the board with Secure Boot on**: shim, our grub, our signed kernel, then
  the appliance; `puppy-check` 20 of 25 rows PASS, Lemonade answering on `:13305` with its key,
  chat 70.49 tok/s, TTFT 1.30 s, 0 `amdxdna` errors
- the release stick: written and read back byte for byte
- `1bit-release-check` in the appliance, which is the row a release has to pass with no failure
- an **installed system** - install to a disk, boot from it with no stick attached - run in **QEMU**;
  the install on the board's own disk is the gate the tag waits on

One candidate was pulled back from publication last week because the stick test had not been run
on that exact build. The rule stands: the whole gate, on the hardware, on the bytes that ship.

## What is not in it, said plainly

- The desktop is **in** the image but not started by default: Puppy's X packages are about 1 GB
  unpacked, and the appliance is a server unless you pick the `desktop` entry.
- The install to the board's internal disk has not run on the board yet; it has run in QEMU, live
  and installed, with the stick out.
- Single-stream decode on Qwen3.8 is behind the fastest Strix Halo engines today. The numbers we
  publish are the ones we measured, on the [leaderboard](../docs/npu-leaderboard.md) and the
  [wiki](https://github.com/1bit-MONSTER/engine/wiki), with the command that produced each.

## License

Source is Apache-2.0. The release binaries also contain two proprietary components compiled in,
the 1bit NPU runtime and the 1bit HIP kernels for HRX, under the 1bit Binary License, free to use.
The image carries Puppy's own tree under GPL-2.0-or-later, with every recipe's licences beside it.

Thank you to Osmantic / ODS, to the Lemonade team and to AMD's developers.
