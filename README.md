# 🌊 Ebb&Flow // Oceanic Tide Reconnaissance

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platforms](https://img.shields.io/badge/Platforms-Android%20%7C%20Linux%20%7C%20Windows%20%7C%20macOS-blue.svg)](#supported-platforms)
[![Tech Stack](https://img.shields.io/badge/Tech-Kotlin%20%7C%20Leaflet%20%7C%20WebAudio%20%7C%20Python-orange.svg)](#architecture)
[![Interface](https://img.shields.io/badge/Interface-Oceanic%20Glassmorphism-00f5d4.svg)](#features)

*A global marine tide, tidal currents, and lunar/solunar reconnaissance platform indexing 32,013 coastal stations worldwide across North & Central America, South America, Asia, Africa, Oceania, and Europe.*

</div>

---

## 🌊 Overview

**Ebb&Flow** is a tactical oceanic surveillance and coastal telemetry application designed for mariners, anglers, surfers, and coastal observers. Styled with an **Oceanic Deep Water Glassmorphism** aesthetic (deep abyss navy, bioluminescent teal accents, frosted translucent glass panels, and live canvas wave fluid animations), it tracks astronomical tides, water elevations, tidal tendencies, lunar phases, and solunar coefficients without requiring manual refreshing.

---

## ✨ Key Features

- **🌐 Global Tide Station Coverage (32,013 Stations)**:
  - Compiled directly from [tides4fishing.com](https://tides4fishing.com) across 6 continents:
    - **North & Central America** (`/am`)
    - **South America** (`/su`)
    - **Asia** (`/as`)
    - **Africa** (`/af`)
    - **Oceania** (`/oc`)
    - **Europe** (`/eu`)
  - Instant offline fuzzy search across stations, coastal regions, and countries.
- **⏱️ 100% Real-Time Telemetry (Zero Reloads)**:
  - Continuous second-by-second water elevation calculation and tidal tendency tracking (`FLOODING (RISING) ▲` vs `EBBING (FALLING) ▼`).
  - Next High Tide and Next Low Tide countdown timer ticking live.
  - Interactive Dynamic Waveform Canvas: 24-hour harmonic tide curve with fluid wave oscillation and glowing real-time cursor.
- **📍 Location Persistence & Sticky Behavior**:
  - The app always re-opens to the last chosen location and firmly maintains that position across sessions until explicitly changed.
- **🏠 Home Base & Quick Access with Customizable Nicknames**:
  - 1-tap Home Base designation with direct top HUD jump button.
  - Quick Access bookmarked list allowing personalized custom nicknames (e.g., *"My Secret Surf Break"*, *"Weekend Fishing Pier"*, *"Home Marina"*).
- **🌕 Lunar & Solunar Activity Tracking**:
  - Real-time lunar phase calculation (illumination percentage, lunar age in days).
  - Maritime tidal coefficient (20 - 118 scale) and solunar feeding activity classification.
- **↗️ One-Touch Deep Link Telemetry**:
  - Direct deep-link launching full historical tables, solunar charts, and barometric data on Tides4Fishing.
- **📱 Native Hardware Integration**:
  - Android native client with edge-to-edge dark theme, hardware-accelerated WebView, SharedPreferences persistence bridge, and haptic feedback.
  - Custom launcher icons generated from `/home/prime3vil/Pictures/Ebb&Flow.jpg`.

---

## 🏗️ Architecture

```
Ebb&Flow/
├── app/                              # Android Native Client (Kotlin + AndroidX + WebKit)
│   ├── src/main/java/com/ebbflow/app/
│   │   ├── MainActivity.kt          # Activity lifecycle, edge-to-edge display
│   │   └── EbbFlowBridge.kt         # Native SharedPreferences & haptic bridge
│   ├── src/main/assets/map/         # Core Oceanic Map & UI Engine
│   │   ├── index.html               # Main map HUD & sliding telemetry drawer
│   │   ├── oceanic.css              # Deep Water Glassmorphism stylesheet
│   │   ├── tide_engine.js           # Real-time harmonic tide & solunar calculation
│   │   ├── quick_access.js          # Persistent storage & nickname manager
│   │   ├── tides_data.js            # 32,013 compiled stations database
│   │   └── leaflet/                 # Hardware-accelerated Leaflet & MarkerCluster
│   └── src/main/res/                # Mipmap launcher icons & themes
├── scripts/
│   ├── compile_tides4fishing.py     # High-concurrency 6-continent scraper
│   └── generate_app_icons.py        # Icon generator from source image
├── tide_stations.json               # Full JSON station database (7.4 MB)
└── Ebb&Flow.apk                     # Standalone installable Android APK (5.6 MB)
```

---

## 🚀 Building & Running

### Android Release APK
To compile the standalone release APK:
```bash
./gradlew assembleRelease
```
The compiled package will be placed at `Ebb&Flow.apk` in the root directory.

### Ingesting / Updating Station Data
To refresh station data from tides4fishing:
```bash
python3 scripts/compile_tides4fishing.py
```

---

## 📦 Pre-Built Cross-Platform Packages

Ready-to-use release binaries are available under [Releases](https://github.com/Prime3vil/Ebb-Flow/releases):

| Platform | Package File | Architecture | Format |
|---|---|---|---|
| **Android** | `Ebb&Flow.apk` | Universal | Standalone Installable APK (v2) |
| **Linux (x64)** | `Ebb&Flow-Linux-x64.zip` | x86_64 | Portable Standalone Binary |
| **Windows (x64)**| `Ebb&Flow-Windows-x64.zip` | x86_64 | Portable `.zip` (`Ebb&Flow.exe`) |
| **macOS (Apple Silicon)**| `Ebb&Flow-Mac-AppleSilicon-arm64.zip` | Apple Silicon (M1-M4) | Standalone `.app` bundle |
| **macOS (Intel)**| `Ebb&Flow-Mac-Intel-x64.zip` | Intel x64 | Standalone `.app` bundle |

---

## 🖱️ GUI Installation Guide (Pre-Built Apps)

Follow the simple visual instructions below to install and launch Ebb&Flow through your operating system's graphical interface:

### 🤖 Android (`Ebb&Flow.apk`)
1. Download **`Ebb&Flow.apk`** from [Releases](https://github.com/Prime3vil/Ebb-Flow/releases) directly on your device (or download to PC and transfer via USB).
2. Open your device's **Files** or **Downloads** app and tap **`Ebb&Flow.apk`**.
3. If Android displays *"For your security, your phone is not allowed to install unknown apps from this source"*:
   - Tap **Settings** in the prompt.
   - Toggle **"Allow from this source"** to **ON**.
   - Tap the back arrow.
4. Tap **Install** and wait for the installer to finish.
5. Tap **Open** to launch Ebb&Flow, or tap the **Ebb&Flow** icon in your app drawer.

---

### 🪟 Windows (`Ebb&Flow-Windows-x64.zip`)
1. Download **`Ebb&Flow-Windows-x64.zip`** from [Releases](https://github.com/Prime3vil/Ebb-Flow/releases).
2. Locate the file in **Windows File Explorer** (in your `Downloads` folder).
3. Right-click **`Ebb&Flow-Windows-x64.zip`** -> select **Extract All...** -> click **Extract**.
4. Open the extracted **`Ebb&Flow-win32-x64`** folder.
5. Double-click **`Ebb&Flow.exe`** to launch the console.
6. *(First Launch / SmartScreen)*: If Windows SmartScreen displays *"Windows protected your PC"*:
   - Click **"More info"**.
   - Click **"Run anyway"**.
7. *(Optional Desktop Shortcut)*: Right-click **`Ebb&Flow.exe`** -> **Show more options** -> **Send to** -> **Desktop (create shortcut)**.

---

### 🍎 macOS (`Ebb&Flow-Mac-AppleSilicon-arm64.zip` / `Ebb&Flow-Mac-Intel-x64.zip`)
1. Download the archive matching your Mac's processor from [Releases](https://github.com/Prime3vil/Ebb-Flow/releases):
   - **`Ebb&Flow-Mac-AppleSilicon-arm64.zip`**: For Apple Silicon (M1, M2, M3, M4) Macs.
   - **`Ebb&Flow-Mac-Intel-x64.zip`**: For Intel-based Macs.
2. In **Finder**, double-click the `.zip` file to extract it.
3. Open the extracted folder and drag **`Ebb&Flow.app`** into your **Applications** folder (`/Applications`).
4. Launch **`Ebb&Flow`** from your Applications folder, Launchpad, or Spotlight (`Cmd + Space`).
5. *(First Launch / Gatekeeper Approval)*:
   - If macOS displays *"Ebb&Flow cannot be opened because the developer cannot be verified"*:
     - **Option 1**: Right-click (or Control-click) `Ebb&Flow.app` in Finder -> choose **Open** -> click **Open** in the confirmation dialog.
     - **Option 2**: Go to **System Settings** -> **Privacy & Security**, scroll down to the **Security** section, and click **"Open Anyway"**.

---

### 🐧 Linux Desktop (`Ebb&Flow-Linux-x64.zip`)
1. Download **`Ebb&Flow-Linux-x64.zip`** from [Releases](https://github.com/Prime3vil/Ebb-Flow/releases).
2. Open your desktop file manager (**Dolphin** in KDE, **Nautilus** / **Files** in GNOME) and right-click the `.zip` file -> choose **Extract Here** (or **Extract Archive**).
3. Open the extracted **`Ebb&Flow-linux-x64`** folder.
4. Enable executable permission:
   - Right-click the **`Ebb&Flow`** binary -> select **Properties**.
   - Navigate to the **Permissions** tab.
   - Check the box **"Is executable"** (KDE) or **"Allow executing file as program"** (GNOME).
   - Click **OK**.
5. Double-click **`Ebb&Flow`** to launch!
6. *(Optional System Menu Integration)*: If cloning the repository, you can run `./install.sh` inside `Linux app` to automatically install icons, application menu launchers, and the `ebb-flow` CLI command.

---

## 💻 CLI Installation & Terminal Launch Guide

For developers and power users who prefer using the command line:

### 🤖 Android (via ADB)
With USB debugging enabled on your phone:
```bash
adb install -r "Ebb&Flow.apk"
```

### 🐧 Linux Terminal
```bash
# 1. Download & extract archive:
unzip "Ebb&Flow-Linux-x64.zip" -d EbbFlow

# 2. Grant execution permission:
chmod +x "EbbFlow/Ebb&Flow-linux-x64/Ebb&Flow"

# 3. Launch application:
"./EbbFlow/Ebb&Flow-linux-x64/Ebb&Flow"
```

### 🪟 Windows (PowerShell)
```powershell
# 1. Extract archive:
Expand-Archive -Path ".\Ebb&Flow-Windows-x64.zip" -DestinationPath ".\EbbFlow"

# 2. Launch:
& ".\EbbFlow\Ebb&Flow-win32-x64\Ebb&Flow.exe"
```

### 🍎 macOS (Terminal)
```bash
# 1. Extract to Applications:
unzip "Ebb&Flow-Mac-AppleSilicon-arm64.zip" -d /Applications/

# 2. Clear quarantine attribute (Gatekeeper bypass):
xattr -cr "/Applications/Ebb&Flow-darwin-arm64/Ebb&Flow.app"

# 3. Launch:
open "/Applications/Ebb&Flow-darwin-arm64/Ebb&Flow.app"
```

---

## 📜 License

Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for details.

---

<div align="center">

Maintained with 🌊 by **[Prime3vil](https://github.com/Prime3vil)**

</div>


