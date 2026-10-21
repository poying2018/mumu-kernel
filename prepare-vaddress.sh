#!/bin/bash
# Prepare the emulator's private PCI driver for linking into the kernel.
#
# MuMu exposes a private PCI device (vendor 0x1c87, device 0x1074) that
# carries the channel between the guest and the host. The stock kernel has no
# driver for it, so the guest cannot finish booting. The driver ships as
# /system/lib64/vaddress.ko, an out-of-tree module; unpacking it lets its
# objects be linked into the kernel image.
set -eu

KDIR="$1"
cd "$KDIR"

mkdir -p drivers/vaddress

curl -sL -o /tmp/vaddress.ko \
    "https://github.com/poying2018/mumu-kernel/releases/download/plain-kernel-test/vaddress.ko"
ls -la /tmp/vaddress.ko

rm -rf /tmp/vaddress-unpack
mkdir -p /tmp/vaddress-unpack
cd /tmp/vaddress-unpack
ar x /tmp/vaddress.ko
ls -la

cp ./*.o "$KDIR/drivers/vaddress/"
ls -la "$KDIR/drivers/vaddress/"
