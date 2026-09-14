#!/usr/bin/env bash
set -e
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=== Installing Ebb&Flow for Fedora KDE Plasma ==="

mkdir -p "$HOME/.local/share/applications"
mkdir -p "$HOME/.local/share/icons/hicolor/256x256/apps"
mkdir -p "$HOME/.local/share/icons/hicolor/512x512/apps"
mkdir -p "$HOME/.local/share/pixmaps"
mkdir -p "$HOME/.local/bin"
mkdir -p "$HOME/Desktop"

chmod +x "$DIR/dist/Ebb&Flow-linux-x64/Ebb&Flow"
chmod +x "$DIR/run.sh"

cp "$DIR/icon.png" "$HOME/.local/share/icons/hicolor/512x512/apps/ebbflow.png"
cp "$DIR/icon.png" "$HOME/.local/share/icons/hicolor/256x256/apps/ebbflow.png"
cp "$DIR/icon.png" "$HOME/.local/share/pixmaps/ebbflow.png"
echo "✓ Installed application icons to hicolor and pixmaps"

cp "$DIR/ebbflow.desktop" "$HOME/.local/share/applications/ebbflow.desktop"
chmod +x "$HOME/.local/share/applications/ebbflow.desktop"
echo "✓ Installed desktop entry: $HOME/.local/share/applications/ebbflow.desktop"

cp "$DIR/ebbflow.desktop" "$HOME/Desktop/ebbflow.desktop"
chmod +x "$HOME/Desktop/ebbflow.desktop"
echo "✓ Created Desktop shortcut: $HOME/Desktop/ebbflow.desktop"

ln -sf "$DIR/dist/Ebb&Flow-linux-x64/Ebb&Flow" "$HOME/.local/bin/ebbflow"
echo "✓ Created terminal CLI symlink: $HOME/.local/bin/ebbflow"

if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database "$HOME/.local/share/applications" >/dev/null 2>&1 || true
fi
if command -v gtk-update-icon-cache >/dev/null 2>&1; then
    gtk-update-icon-cache -f -t "$HOME/.local/share/icons/hicolor" >/dev/null 2>&1 || true
fi
if command -v kbuildsycoca6 >/dev/null 2>&1; then
    kbuildsycoca6 --noincremental >/dev/null 2>&1 || true
fi

echo "=== Ebb&Flow Native Linux App installed successfully! ==="
