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

# Install standalone app copy to ~/.local/share/ebbflow
mkdir -p "$HOME/.local/share/ebbflow"
cp -r "$DIR/dist/Ebb&Flow-linux-x64/." "$HOME/.local/share/ebbflow/"
cp "$DIR/icon.png" "$HOME/.local/share/ebbflow/icon.png"
chmod +x "$HOME/.local/share/ebbflow/Ebb&Flow"
echo "✓ Installed standalone Ebb&Flow application copy to $HOME/.local/share/ebbflow"

# Create CLI launcher
cat << 'EOF' > "$HOME/.local/bin/ebbflow"
#!/usr/bin/env bash
exec "$HOME/.local/share/ebbflow/Ebb&Flow" "$@"
EOF
chmod +x "$HOME/.local/bin/ebbflow"
echo "✓ Created terminal CLI launcher: $HOME/.local/bin/ebbflow"

cp "$DIR/icon.png" "$HOME/.local/share/pixmaps/ebbflow.png"
for size in 16 32 48 64 128 256 512; do
    mkdir -p "$HOME/.local/share/icons/hicolor/${size}x${size}/apps"
    if command -v magick >/dev/null 2>&1; then
        magick "$DIR/icon.png" -resize "${size}x${size}" "$HOME/.local/share/icons/hicolor/${size}x${size}/apps/ebbflow.png"
    elif command -v convert >/dev/null 2>&1; then
        convert "$DIR/icon.png" -resize "${size}x${size}" "$HOME/.local/share/icons/hicolor/${size}x${size}/apps/ebbflow.png"
    else
        cp "$DIR/icon.png" "$HOME/.local/share/icons/hicolor/${size}x${size}/apps/ebbflow.png"
    fi
done
echo "✓ Installed multi-resolution application icons to hicolor and pixmaps"

cp "$DIR/ebbflow.desktop" "$HOME/.local/share/applications/ebbflow.desktop"
chmod +x "$HOME/.local/share/applications/ebbflow.desktop"
echo "✓ Installed desktop entry: $HOME/.local/share/applications/ebbflow.desktop"

cp "$DIR/ebbflow.desktop" "$HOME/Desktop/ebbflow.desktop"
chmod +x "$HOME/Desktop/ebbflow.desktop"
echo "✓ Created Desktop shortcut: $HOME/Desktop/ebbflow.desktop"

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
