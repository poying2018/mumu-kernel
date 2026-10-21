#!/bin/bash
# Prepare the emulator's private PCI driver for linking into the kernel.
#
# MuMu exposes a private PCI device (vendor 0x1c87, device 0x1074) that
# carries the channel between the guest and the host. The stock kernel has no
# driver for it, so the guest cannot finish booting. The driver ships as
# /system/lib64/vaddress.ko, an out-of-tree module.
#
# A kernel module is itself a relocatable ELF object, so it is used directly
# as vaddress.o rather than being unpacked with ar.
set -eu

KDIR="$1"
cd "$KDIR"

mkdir -p drivers/vaddress

curl -sL -o /tmp/vaddress.ko \
    "https://github.com/poying2018/mumu-kernel/releases/download/plain-kernel-test/vaddress.ko"
ls -la /tmp/vaddress.ko
file /tmp/vaddress.ko || true

cp /tmp/vaddress.ko "$KDIR/drivers/vaddress/vaddress.o"
ls -la "$KDIR/drivers/vaddress/"
