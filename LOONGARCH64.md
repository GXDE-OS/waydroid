# LoongArch64 host support

Waydroid's host manager must recognize the Linux `loongarch64` machine name
and preserve it as the Android container architecture. The mapping in
`tools/helpers/arch.py` provides that behavior.

The public Waydroid OTA service does not publish `waydroid_loongarch64`
images. Use preinstalled local images instead:

```text
/etc/waydroid-extra/images/system.img
/etc/waydroid-extra/images/vendor.img
```

With both images present, `sudo waydroid init -f` skips OTA discovery and
disables the online updater. `system.img` and `vendor.img` must be ext4
Android images built for LoongArch64; the vendor image also needs the
Waydroid container configuration and HAL integration. Do not use an arm64 or
x86_64 Waydroid OTA image on a LoongArch64 host.

Before initialization, confirm that the host kernel has Binder/binderfs,
namespaces, cgroup v2, overlayfs, and a usable DRM render node. Waydroid
mounts binderfs automatically during initialization.
