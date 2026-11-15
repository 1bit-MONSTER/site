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
tags: bosgame, strix-halo, ryzen-ai-max, linux, usb4
title: Bosgame M5 USB-C not working on Linux: the fix
summary: Bosgame M5 (AXB35-02) USB-C and rear USB not working on Linux? Three USB controllers sleep in D3cold. One udev rule wakes them, and every port works.

# Bosgame M5 / AXB35 USB-C and rear USB not working on Linux: the fix

On the Bosgame M5 (BeyondMax, board `AXB35-02`, Ryzen AI Max+ 395), Linux sees only the front USB-A port.
Three of the board's four USB controllers sleep in `D3cold` and never wake, so a drive in a USB-C or rear
port produces no kernel event at all. A one-line udev rule keeps the controllers awake. With it, every
external port worked in a plug test on the hardware on 14 November 2026 (BIOS 1.10).

## Why don't the USB-C and rear USB ports work on Linux?

The board has four xHCI USB controllers (PCI ids `1022:1587`, `1588`, `1589`, `158b`). On a stock Linux
boot, three of them autosuspend to `D3cold` and stay there. A port whose controller is asleep does not
report a plug, so the symptom looks electrical: no `dmesg` line, no device, and the port registers stay
in `RxDetect`. The one controller that stays awake carries the front USB-A port, which is why that port
works and nothing else does. The original report says every port works under Windows on the same box
([engine#823](https://github.com/1bit-MONSTER/engine/issues/823)); we have not tested Windows ourselves.

It is not a missing driver, and it is not a Type-C or UCSI problem. Writing `on` to each controller's
`power/control` moves it to `D0`, and its ports come alive.

## How do I fix it?

Install this rule as `/etc/udev/rules.d/91-1bit-xhci-keepawake.rules` (one line):

```
ACTION=="add|bind", SUBSYSTEM=="pci", DRIVER=="xhci_hcd", ATTR{[dmi/id]board_name}=="AXB35-02", ATTR{vendor}=="0x1022", ATTR{device}=="0x1587|0x1588|0x1589|0x158b", TEST=="power/control", ATTR{power/control}="on"
```

Then reboot. The rule only binds on a board whose DMI name is `AXB35-02`, and it only writes
`power/control = on` on those four controllers, so it does nothing on any other machine.

1bit OS ships this rule in its image. The same file is in the
[engine repository](https://github.com/1bit-MONSTER/engine/blob/main/os/v3/puppy/embed/etc/udev/rules.d/91-1bit-xhci-keepawake.rules).

## How do I check that it worked?

The engine repository has a read-only check, `tools/xhci_keepawake_check.sh`:

```sh
tools/xhci_keepawake_check.sh                    # DMI match, each controller's power state, a verdict
tools/xhci_keepawake_check.sh --require-awake    # exit 1 unless every matched controller is in D0
sudo tools/xhci_keepawake_check.sh --apply       # the rule's one write, without a reboot (--revert undoes it)
```

The verdict `all awake` means a plug into any port is a valid test. `N asleep` means the rule is not
installed or did not apply yet.

## Which port is on which controller?

Measured on the Bosgame M5 (AXB35-02), BIOS 1.10, kernel `7.4.0-rc1-1bit`, with the four controllers kept awake:

| physical port | xHCI controller | result |
|---|---|---|
| front USB-A | `c7:00.0` (`1588`) | works with or without the rule |
| front USB-C | `c7:00.3` (`1589`) | SuperSpeed 5 Gbps, USB storage |
| rear USB-C | `c7:00.4` (`158b`) | SuperSpeed 5 Gbps, USB storage |
| rear USB-A | `c7:00.0` (`1588`), port 4 | high-speed with a USB 2 stick (a USB 3 device not yet tried) |
| rear USB-A next to the power connector | `c5:00.4` (`1587`) | SuperSpeed 5 Gbps, USB storage |

One enclosure we tried, a Realtek RTL9210, enumerates at USB 2 speed on every port, including ports
where another drive reaches 5 Gbps. That limit is the enclosure or its cable, not the board.

## Does a BIOS update fix it?

No. The same three controllers sleep in `D3cold` on BIOS 1.09 and on BIOS 1.10 (11/04/2026). The rule
is needed on both.

## What about USB4 and Thunderbolt?

The Bosgame M5 uses the APU's native USB4: USB4 v1 at 40 Gbps, through two USB4 host routers. There is
no discrete USB4 v2 (80 Gbps) controller on this board. USB 2 and USB 3 devices on the USB-C ports go
through the xHCI controllers above, which is what the rule fixes. **A USB4 or Thunderbolt device has
not been tested yet**, and neither has a 1bit OS boot with the rule loaded from the image (the plug
test above ran on an Ubuntu host with the rule installed).

The full record, with the per-boot captures and the measurements behind each step, is on
[AXB35 USB ports](../docs/axb35-usb-ports.md). For booting 1bit OS from a stick on this board, see
[Install](../docs/install.md). The issue is
[engine#823](https://github.com/1bit-MONSTER/engine/issues/823). More from this week is in
[This week in the engine](2026-11-15-strix-halo-linux-this-week.md).

## Frequently asked questions

### Why does only the front USB-A port work on the Bosgame M5 under Linux?

Three of its four xHCI USB controllers autosuspend to D3cold and never wake. Only the controller behind the front USB-A port stays awake.

### Is there a fix for the Bosgame M5 USB-C ports on Linux?

Yes. A one-line udev rule sets power/control to on for the board's four xHCI controllers. With it, every external USB-A and USB-C port worked in a plug test on BIOS 1.10.

### Does the udev rule affect other computers?

No. It only binds when the DMI board name is AXB35-02, and only on the four AMD xHCI controller ids it names.

### Does the Bosgame M5 have USB4 v2 at 80 Gbps?

No. It uses the Ryzen AI Max+ 395's native USB4 v1 at 40 Gbps. USB4 and Thunderbolt devices have not been tested with the fix yet.
