#!/bin/bash
# Extract the uncompressed vmlinux from a bzImage.
set -eu
IMG="$1"
OUT="$2"

# The kernel source ships the extractor, which knows the payload layout.
curl -sL -o /tmp/extract-vmlinux \
  "https://raw.githubusercontent.com/torvalds/linux/v6.1/scripts/extract-vmlinux"
chmod +x /tmp/extract-vmlinux

# extract-vmlinux needs the lz4 tool for the LZ4 payload.
if ! command -v lz4 >/dev/null 2>&1; then
    sudo apt-get update >/dev/null
    sudo apt-get install -y liblz4-tool >/dev/null
fi

/tmp/extract-vmlinux "$IMG" > "$OUT" || {
    echo "extract-vmlinux failed" >&2
    exit 1
}
ls -la "$OUT"
