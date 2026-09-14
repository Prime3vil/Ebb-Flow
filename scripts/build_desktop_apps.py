import os
import shutil
import subprocess
import json
import zipfile
import tarfile

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAP_SRC = os.path.join(BASE_DIR, "app", "src", "main", "assets", "map")
ICON_PNG = os.path.join(BASE_DIR, "scripts", "icon_512.png")
ICON_ICO = os.path.join(BASE_DIR, "scripts", "icon.ico")
ICON_ICNS = os.path.join(BASE_DIR, "scripts", "icon.icns")

PKG_JSON = {
    "name": "ebbflow",
    "productName": "Ebb&Flow",
    "version": "1.0.0",
    "description": "Ebb&Flow - Global Oceanic Tide Reconnaissance & Solunar Ephemeris",
    "main": "main.js",
    "author": "Ebb&Flow Dev Team",
    "license": "ISC"
}

PRELOAD_JS_TEMPLATE = """const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('desktopBridge', {
  platform: '__PLATFORM__',
  minimize: () => ipcRenderer.send('window-minimize'),
  maximize: () => ipcRenderer.send('window-maximize'),
  close: () => ipcRenderer.send('window-close'),
  toggleFullscreen: () => ipcRenderer.send('window-fullscreen'),
  isMaximized: () => ipcRenderer.invoke('window-is-maximized'),
  onMaximizedState: (callback) => ipcRenderer.on('window-maximized-state', (_, state) => callback(state)),
  onFullscreenState: (callback) => ipcRenderer.on('window-fullscreen-state', (_, state) => callback(state))
});
"""

MAIN_JS_WIN = """const { app, BrowserWindow, ipcMain, session } = require('electron');
const path = require('path');

app.setName('Ebb&Flow');

let mainWindow = null;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1440,
    height: 920,
    minWidth: 1024,
    minHeight: 700,
    frame: true,
    backgroundColor: '#020813',
    icon: path.join(__dirname, 'icon.ico'),
    show: false,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: false,
      contextIsolation: true,
      webSecurity: false,
      allowRunningInsecureContent: true
    }
  });

  session.defaultSession.webRequest.onBeforeSendHeaders((details, callback) => {
    const requestHeaders = Object.assign({}, details.requestHeaders);
    requestHeaders['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36';
    callback({ requestHeaders });
  });

  session.defaultSession.webRequest.onHeadersReceived((details, callback) => {
    const responseHeaders = Object.assign({}, details.responseHeaders);
    for (const key of Object.keys(responseHeaders)) {
      const lower = key.toLowerCase();
      if (lower === 'x-frame-options' || lower === 'content-security-policy') {
        delete responseHeaders[key];
      }
    }
    callback({ responseHeaders });
  });

  mainWindow.loadFile(path.join(__dirname, 'src', 'index.html'));

  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
  });

  mainWindow.on('maximize', () => {
    if (mainWindow && mainWindow.webContents) {
      mainWindow.webContents.send('window-maximized-state', true);
    }
  });

  mainWindow.on('unmaximize', () => {
    if (mainWindow && mainWindow.webContents) {
      mainWindow.webContents.send('window-maximized-state', false);
    }
  });

  mainWindow.on('enter-full-screen', () => {
    if (mainWindow && mainWindow.webContents) {
      mainWindow.webContents.send('window-fullscreen-state', true);
    }
  });

  mainWindow.on('leave-full-screen', () => {
    if (mainWindow && mainWindow.webContents) {
      mainWindow.webContents.send('window-fullscreen-state', false);
    }
  });

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

ipcMain.on('window-minimize', () => {
  if (mainWindow) mainWindow.minimize();
});

ipcMain.on('window-maximize', () => {
  if (!mainWindow) return;
  if (mainWindow.isMaximized()) {
    mainWindow.unmaximize();
  } else {
    mainWindow.maximize();
  }
});

ipcMain.on('window-close', () => {
  if (mainWindow) mainWindow.close();
});

ipcMain.on('window-fullscreen', () => {
  if (mainWindow) {
    mainWindow.setFullScreen(!mainWindow.isFullScreen());
  }
});

ipcMain.handle('window-is-maximized', () => {
  return mainWindow ? mainWindow.isMaximized() : false;
});

app.whenReady().then(() => {
  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', () => {
  app.quit();
});
"""

MAIN_JS_MAC = """const { app, BrowserWindow, ipcMain, session } = require('electron');
const path = require('path');

app.setName('Ebb&Flow');

let mainWindow = null;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1440,
    height: 920,
    minWidth: 1024,
    minHeight: 700,
    frame: true,
    titleBarStyle: 'hiddenInset',
    backgroundColor: '#020813',
    icon: path.join(__dirname, 'icon.icns'),
    show: false,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: false,
      contextIsolation: true,
      webSecurity: false,
      allowRunningInsecureContent: true
    }
  });

  session.defaultSession.webRequest.onBeforeSendHeaders((details, callback) => {
    const requestHeaders = Object.assign({}, details.requestHeaders);
    requestHeaders['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36';
    callback({ requestHeaders });
  });

  session.defaultSession.webRequest.onHeadersReceived((details, callback) => {
    const responseHeaders = Object.assign({}, details.responseHeaders);
    for (const key of Object.keys(responseHeaders)) {
      const lower = key.toLowerCase();
      if (lower === 'x-frame-options' || lower === 'content-security-policy') {
        delete responseHeaders[key];
      }
    }
    callback({ responseHeaders });
  });

  mainWindow.loadFile(path.join(__dirname, 'src', 'index.html'));

  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
  });

  mainWindow.on('maximize', () => {
    if (mainWindow && mainWindow.webContents) {
      mainWindow.webContents.send('window-maximized-state', true);
    }
  });

  mainWindow.on('unmaximize', () => {
    if (mainWindow && mainWindow.webContents) {
      mainWindow.webContents.send('window-maximized-state', false);
    }
  });

  mainWindow.on('enter-full-screen', () => {
    if (mainWindow && mainWindow.webContents) {
      mainWindow.webContents.send('window-fullscreen-state', true);
    }
  });

  mainWindow.on('leave-full-screen', () => {
    if (mainWindow && mainWindow.webContents) {
      mainWindow.webContents.send('window-fullscreen-state', false);
    }
  });

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

ipcMain.on('window-minimize', () => {
  if (mainWindow) mainWindow.minimize();
});

ipcMain.on('window-maximize', () => {
  if (!mainWindow) return;
  if (mainWindow.isMaximized()) {
    mainWindow.unmaximize();
  } else {
    mainWindow.maximize();
  }
});

ipcMain.on('window-close', () => {
  if (mainWindow) mainWindow.close();
});

ipcMain.on('window-fullscreen', () => {
  if (mainWindow) {
    mainWindow.setFullScreen(!mainWindow.isFullScreen());
  }
});

ipcMain.handle('window-is-maximized', () => {
  return mainWindow ? mainWindow.isMaximized() : false;
});

app.whenReady().then(() => {
  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', () => {
  app.quit();
});
"""

def copy_tree(src, dst):
    if os.path.exists(dst):
        shutil.rmtree(dst)
    shutil.copytree(src, dst)

def zip_folder(folder_path, output_zip_path):
    print(f"Creating zip archive: {output_zip_path} ...")
    with zipfile.ZipFile(output_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        base_name = os.path.basename(folder_path)
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, os.path.dirname(folder_path))
                zipf.write(full_path, rel_path)
    print(f"✓ Zip ready: {output_zip_path} ({os.path.getsize(output_zip_path)} bytes)")

def build_windows():
    print("\n==========================================")
    print("BUILDING WINDOWS DESKTOP APP")
    print("==========================================")
    app_dir = os.path.join(BASE_DIR, "Windows app")
    os.makedirs(app_dir, exist_ok=True)
    
    copy_tree(MAP_SRC, os.path.join(app_dir, "src"))
    shutil.copyfile(ICON_PNG, os.path.join(app_dir, "icon.png"))
    shutil.copyfile(ICON_ICO, os.path.join(app_dir, "icon.ico"))
    
    with open(os.path.join(app_dir, "package.json"), "w") as f:
        json.dump(PKG_JSON, f, indent=2)
        
    with open(os.path.join(app_dir, "preload.js"), "w") as f:
        f.write(PRELOAD_JS_TEMPLATE.replace("__PLATFORM__", "win32"))
        
    with open(os.path.join(app_dir, "main.js"), "w") as f:
        f.write(MAIN_JS_WIN)

    # Note: omit --icon on Linux for win32 to avoid requiring wine64 for rcedit
    cmd = [
        "npx", "--yes", "electron-packager", ".", "Ebb&Flow",
        "--platform=win32", "--arch=x64",
        "--electron-version=34.3.0",
        "--out=dist",
        "--overwrite", "--prune=true", "--asar"
    ]
    print("Running:", " ".join(cmd))
    subprocess.check_call(cmd, cwd=app_dir)
    
    dist_dir = os.path.join(app_dir, "dist")
    out_app_folder = os.path.join(dist_dir, "Ebb&Flow-win32-x64")
    # Also place icon.ico in root of the output folder for Windows shortcut convenience
    shutil.copyfile(ICON_ICO, os.path.join(out_app_folder, "icon.ico"))
    zip_folder(out_app_folder, os.path.join(dist_dir, "Ebb&Flow-Windows-x64.zip"))
    print("✓ Windows App Build Complete!")

def build_mac():
    print("\n==========================================")
    print("BUILDING MAC DESKTOP APPS (Apple Silicon & Intel)")
    print("==========================================")
    app_dir = os.path.join(BASE_DIR, "Mac app")
    os.makedirs(app_dir, exist_ok=True)
    
    copy_tree(MAP_SRC, os.path.join(app_dir, "src"))
    shutil.copyfile(ICON_PNG, os.path.join(app_dir, "icon.png"))
    shutil.copyfile(ICON_ICNS, os.path.join(app_dir, "icon.icns"))
    
    with open(os.path.join(app_dir, "package.json"), "w") as f:
        json.dump(PKG_JSON, f, indent=2)
        
    with open(os.path.join(app_dir, "preload.js"), "w") as f:
        f.write(PRELOAD_JS_TEMPLATE.replace("__PLATFORM__", "darwin"))
        
    with open(os.path.join(app_dir, "main.js"), "w") as f:
        f.write(MAIN_JS_MAC)

    cmd = [
        "npx", "--yes", "electron-packager", ".", "Ebb&Flow",
        "--platform=darwin", "--arch=x64,arm64",
        "--electron-version=34.3.0",
        "--out=dist", "--icon=icon.icns",
        "--overwrite", "--prune=true", "--asar"
    ]
    print("Running:", " ".join(cmd))
    subprocess.check_call(cmd, cwd=app_dir)
    
    dist_dir = os.path.join(app_dir, "dist")
    arm_folder = os.path.join(dist_dir, "Ebb&Flow-darwin-arm64")
    x64_folder = os.path.join(dist_dir, "Ebb&Flow-darwin-x64")
    
    if os.path.exists(arm_folder):
        zip_folder(arm_folder, os.path.join(dist_dir, "Ebb&Flow-Mac-AppleSilicon-arm64.zip"))
    if os.path.exists(x64_folder):
        zip_folder(x64_folder, os.path.join(dist_dir, "Ebb&Flow-Mac-Intel-x64.zip"))
    print("✓ Mac App Build Complete!")

if __name__ == "__main__":
    build_windows()
    build_mac()
    print("\n🎉 WINDOWS AND MAC BUILDS COMPLETED!")
