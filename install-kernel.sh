#!/bin/bash
# Install the kernel into the emulator's boot filesystem.
#
# debugfs silently leaves a zero length file when a write fails, so the result
# is verified against the source size before the image is uploaded.
set -eu

IMG="$1"
SRC="$2"

debugfs -w -R "rm /kernel" "$IMG" 2>&1 | tail -1 || true

cat > /tmp/debugfs.cmd <<EOF
write $SRC /kernel
set_inode_field /kernel mode 0100644
set_inode_field /kernel uid 1000
set_inode_field /kernel gid 1000
EOF
debugfs -w -f /tmp/debugfs.cmd "$IMG" 2>&1 | tail -3

SIZE=$(debugfs -R "stat /kernel" "$IMG" 2>&1 | sed -n 's/.*Size: \([0-9]*\).*/\1/p' | head -1)
WANT=$(stat -c%s "$SRC")
echo "installed size: $SIZE, expected: $WANT"
if [ "$SIZE" != "$WANT" ]; then
    echo "ERROR: the kernel was not installed correctly"
    exit 1
fi

debugfs -R "ls -l /" "$IMG" 2>&1 | tail -6
echo "OK"
