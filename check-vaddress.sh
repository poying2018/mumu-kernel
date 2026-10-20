#!/bin/bash
# Check the emulator's vaddress module against a freshly built kernel.
#
# The emulator loads /system/lib64/vaddress.ko during boot; it provides the
# binder channel the Android framework needs. Its symbol CRCs have to match
# the running kernel or the module loader rejects it.
#
# Usage: check-vaddress.sh <kernel dir>
set -eu

KDIR="$1"
cd "$KDIR"

if [ ! -f vmlinux ]; then
    echo "no vmlinux in $KDIR"
    exit 1
fi

WORK=$(mktemp -d)
trap 'rm -rf "$WORK"' EXIT
cd "$WORK"

curl -sL -o vaddress.ko \
    "https://github.com/poying2018/mumu-kernel/releases/download/plain-kernel-test/vaddress.ko"
if [ ! -s vaddress.ko ]; then
    echo "the vaddress module could not be downloaded"
    exit 1
fi
ls -la vaddress.ko

# A fully built-in kernel produces no Module.symvers; the CRC of every
# exported symbol lives in the vmlinux as __crc_<name>.
nm "$KDIR/vmlinux" 2>/dev/null \
    | grep -E " __crc_[A-Za-z0-9_]+$" \
    | awk '{print $3, $2}' | sed "s/^__crc_//" > crcs.txt
echo "kernel CRC symbols: $(wc -l < crcs.txt)"

python3 "$GITHUB_WORKSPACE/helper/check-ko-crc.py" crcs.txt vaddress.ko
