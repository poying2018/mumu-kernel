#!/bin/bash
# Write the Kbuild and Kconfig fragments for the built-in vaddress driver.
#
# The driver object comes from the emulator's own module; these two files tell
# the kernel build to link it in.
set -eu

KDIR="$1"
cd "$KDIR"

# The module object is linked in directly, so the Makefile names it rather
# than adding a subdirectory.
cat > drivers/vaddress/Makefile <<'MAKEEOF'
obj-$(CONFIG_VADDRESS) += vaddress.o
MAKEEOF

cat > drivers/vaddress/Kconfig <<'KCONFEOF'
config VADDRESS
	bool "MuMu virtual address device"
	depends on PCI
	default y
	help
	  The emulator exposes a private PCI device that carries the
	  channel between the guest and the host. Without a driver for
	  it the guest cannot finish booting.
KCONFEOF

grep -q "drivers/vaddress/Kconfig" drivers/Kconfig || \
    sed -i '/^endmenu/i source "drivers/vaddress/Kconfig"' drivers/Kconfig

grep -q "vaddress" drivers/Makefile || \
    printf "\nobj-\$(CONFIG_VADDRESS) += vaddress/\n" >> drivers/Makefile

scripts/config --file .config -e VADDRESS
make olddefconfig
grep -E "^CONFIG_VADDRESS" .config

# The module was built with modversions and carries a __versions section the
# kernel build has no use for; drop it so the link does not complain.
if command -v objcopy >/dev/null 2>&1; then
    objcopy --remove-section=__versions \
            --remove-section=.modinfo \
            --remove-section=.gnu.linkonce.this_module \
            drivers/vaddress/vaddress.o 2>/dev/null || true
fi
