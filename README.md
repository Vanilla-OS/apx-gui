<div align="center">
    <img src="data/icons/hicolor/scalable/apps/org.vanillaos.ApxGUI.svg" height="64">
    <h1>Apx GUI</h1>
    <p>A frontend in GTK 4 and Libadwaita for Apx.</p>
    <br />

[![Translation Status][weblate-image]][weblate-url]

<img src="data/screenshot.png">
</div>

[weblate-url]: <https://hosted.weblate.org/engage/vanilla-os/>
[weblate-image]: <https://hosted.weblate.org/widgets/vanilla-os/-/apx-gui/svg-badge.svg>

### Dependencies

#### Build Dependencies

```bash
apt install -y build-essential meson libadwaita-1-dev \
               desktop-file-utils pkg-config libglib2.0-dev
```

#### Runtime Dependencies

```bash
apt install -y python3 python3-gi \
               gir1.2-gtk-4.0 libadwaita-1-0 \
               gir1.2-vte-3.91 python3-yaml \
               python3-requests gettext
```

**APX version 2.0+ required.**

### Build

```bash
meson setup build
ninja -C build
```

### Install

```bash
sudo ninja -C build install
```

## Run

```bash
apx-gui
```
