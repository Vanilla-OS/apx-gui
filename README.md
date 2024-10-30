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

- build-essential
- meson
- libadwaita-1-dev
- gettext
- desktop-file-utils
- apx (2.0+)
- python3-yaml

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
