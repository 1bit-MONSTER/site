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
tags: 1bit-os, live-usb, lemonade, strix-halo, ryzen-ai-max-395, local-llm, getting-started
title: Boot a stick
summary: The simplest way to run local LLMs on a Ryzen AI MAX+ 395: write the 1bit OS image to a USB stick, boot it with Secure Boot on, and Lemonade is serving on the GPU and the NPU. One command installs it to the disk.

# Boot a stick

The feedback we hear most is "keep it simple". So here is the whole setup for local LLMs on a
Ryzen AI MAX+ 395 (Strix Halo) machine:

1. Download the 1bit OS image from the [releases page](https://github.com/1bit-MONSTER/engine/releases).
2. Write it to a USB stick of 8 GB or more.
3. Boot the machine from the stick. Secure Boot stays on; the image is signed.
4. Lemonade comes up with its catalog and its web UI. Pick a model and talk to it.

If you like it, one command from the live session installs the 1bit appliance to the disk:
`1bit-install <disk> --yes`. It refuses to write anything until it has printed the disk it is
about to use and waited, so a typo cannot cost you a drive. Reboot without the stick and the
machine is the same appliance, now permanent.

## What is on the stick

A Lemonade Server with the 1bit engine embedded as its `onebit` backend. Lemonade is the server
you talk to: its model catalog, its downloads, its router, its UI, its OpenAI-compatible API.
For the models it hands to the engine, the Radeon 8060S iGPU runs them through HRX with our own
HIP kernels and the XDNA 2 NPU runs them through our own NPU runtime. Nothing to configure,
nothing to compile, no driver to install: the kernel on the stick is ours, built and signed for
this hardware.

The same engine is also a package for a Lemonade you already run on Ubuntu, from the same
releases page ([Lemonade](../docs/lemonade.md)).

## Where it stands

The current candidate image passes 17 of 17 checks on the board, booted from the stick with
Secure Boot on. The release itself goes out when every item on the checklist is done; the
checklist and the candidate's pins are public ([Releases](../docs/releases.md)). The models the
image is checked against, with the number each one measured on this hardware, are one page
([Models measured](../docs/models.md)).

Sources: [README](https://github.com/1bit-MONSTER/engine#readme), [docs/releases.md](../docs/releases.md), [os/v2/README.md](https://github.com/1bit-MONSTER/engine/blob/main/os/v2/README.md).
