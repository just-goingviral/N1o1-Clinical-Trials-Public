/**
 * Electron main process for NO Dynamics Simulator
 * Author: Dustin Salinas
 * License: MIT
 */

const { app, BrowserWindow, ipcMain, dialog, shell, Menu } = require('electron');
const path = require('path');
const fs = require('fs');
const { spawn } = require('child_process');
const axios = require('axios');
const portfinder = require('portfinder');
const url = require('url');
const os = require('os');

// Set app name
app.name = 'NO Dynamics Simulator';

// Flask server process
let flaskProcess = null;
let flaskPort = 5000;
let mainWindow = null;
let splashWindow = null;
let serverReady = false;

// Handle creating/removing shortcuts on Windows when installing/uninstalling
if (require('electron-squirrel-startup')) {
  app.quit();
}

// Determine the Python executable path
function getPythonExecutable() {
  const platform = process.platform;
  const appPath = app.getAppPath();
  
  if (platform === 'win32') {
    return path.join(appPath, 'python', 'python.exe');
  } else if (platform === 'darwin') {
    return path.join(appPath, 'python', 'bin', 'python');
  } else {
    return path.join(appPath, 'python', 'bin', 'python');
  }
}

// Start Flask server
async function startFlaskServer() {
  return new Promise(async (resolve, reject) => {
    try {
      // Find an available port
      flaskPort = await portfinder.getPortPromise({ port: 5000 });
      
      const pythonPath = getPythonExecutable();
      const appPath = app.getAppPath();
      const flaskAppPath = path.join(appPath, 'app.py');
      
      // Spawn Flask process
      flaskProcess = spawn(pythonPath, [flaskAppPath], {
        env: {
          ...process.env,
          FLASK_APP: flaskAppPath,
          FLASK_ENV: 'production',
          FLASK_RUN_PORT: flaskPort.toString(),
          FLASK_RUN_HOST: '127.0.0.1'
        },
        cwd: appPath
      });
      
      let serverStarted = false;
      
      // Handle stdout
      flaskProcess.stdout.on('data', (data) => {
        const output = data.toString();
        console.log(`Flask: ${output}`);
        
        if (output.includes('Running on') && !serverStarted) {
          serverStarted = true;
          serverReady = true;
          resolve(flaskPort);
        }
      });
      
      // Handle stderr
      flaskProcess.stderr.on('data', (data) => {
        const error = data.toString();
        console.error(`Flask error: ${error}`);
        
        if (error.includes('Running on') && !serverStarted) {
          serverStarted = true;
          serverReady = true;
          resolve(flaskPort);
        }
      });
      
      // Handle process exit
      flaskProcess.on('close', (code) => {
        console.log(`Flask server process exited with code ${code}`);
        flaskProcess = null;
        
        if (!serverStarted) {
          reject(new Error(`Flask server failed to start (exit code ${code})`));
        }
      });
      
      // Set timeout for server start
      setTimeout(() => {
        if (!serverStarted) {
          reject(new Error('Flask server failed to start (timeout)'));
        }
      }, 30000);
    } catch (error) {
      reject(error);
    }
  });
}

// Create splash screen window
function createSplashWindow() {
  splashWindow = new BrowserWindow({
    width: 500,
    height: 300,
    frame: false,
    transparent: true,
    resizable: false,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false
    }
  });
  
  splashWindow.loadFile(path.join(__dirname, 'splash.html'));
  
  // Show splash window in the center of the screen
  splashWindow.center();
  
  // Close event
  splashWindow.on('closed', () => {
    splashWindow = null;
  });
}

// Create main application window
function createMainWindow(port) {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    minWidth: 800,
    minHeight: 600,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false
    },
    show: false,
    backgroundColor: '#212529',
    icon: path.join(__dirname, 'icons', process.platform === 'win32' ? 'icon.ico' : 'icon.png')
  });
  
  // Load the Flask app URL
  mainWindow.loadURL(`http://localhost:${port}/`);
  
  // Once the main window is ready, hide splash and show main
  mainWindow.once('ready-to-show', () => {
    if (splashWindow) {
      splashWindow.close();
    }
    mainWindow.show();
  });
  
  // Handle window closed event
  mainWindow.on('closed', () => {
    mainWindow = null;
  });
  
  // Create application menu
  const template = [
    {
      label: 'File',
      submenu: [
        {
          label: 'Export Results',
          accelerator: 'CmdOrCtrl+E',
          click: () => {
            mainWindow.webContents.executeJavaScript(`
              document.getElementById('downloadCsv').click();
            `);
          }
        },
        {
          label: 'Save Plot',
          accelerator: 'CmdOrCtrl+S',
          click: () => {
            mainWindow.webContents.executeJavaScript(`
              const plotImg = document.getElementById('staticPlot').src;
              if(plotImg) {
                downloadImage(plotImg, 'nitrite_simulation.png');
              } else {
                showToast('No plot to save', 'warning');
              }
            `);
          }
        },
        { type: 'separator' },
        {
          label: 'Exit',
          accelerator: process.platform === 'darwin' ? 'Cmd+Q' : 'Alt+F4',
          click: () => {
            app.quit();
          }
        }
      ]
    },
    {
      label: 'Edit',
      submenu: [
        { role: 'undo' },
        { role: 'redo' },
        { type: 'separator' },
        { role: 'cut' },
        { role: 'copy' },
        { role: 'paste' },
        { role: 'delete' },
        { type: 'separator' },
        { role: 'selectAll' }
      ]
    },
    {
      label: 'View',
      submenu: [
        { role: 'reload' },
        { role: 'forceReload' },
        { role: 'toggleDevTools' },
        { type: 'separator' },
        { role: 'resetZoom' },
        { role: 'zoomIn' },
        { role: 'zoomOut' },
        { type: 'separator' },
        { role: 'togglefullscreen' }
      ]
    },
    {
      label: 'Simulation',
      submenu: [
        {
          label: 'Run Simulation',
          accelerator: 'CmdOrCtrl+R',
          click: () => {
            mainWindow.webContents.executeJavaScript(`
              document.getElementById('runSimulation').click();
            `);
          }
        },
        { type: 'separator' },
        {
          label: 'Standard Protocol',
          click: () => {
            mainWindow.webContents.executeJavaScript(`
              document.querySelector('[data-preset="standard"]').click();
            `);
          }
        },
        {
          label: 'High Dose',
          click: () => {
            mainWindow.webContents.executeJavaScript(`
              document.querySelector('[data-preset="high-dose"]').click();
            `);
          }
        },
        {
          label: 'Reduced Renal Function',
          click: () => {
            mainWindow.webContents.executeJavaScript(`
              document.querySelector('[data-preset="reduced-function"]').click();
            `);
          }
        },
        {
          label: 'Extended Duration',
          click: () => {
            mainWindow.webContents.executeJavaScript(`
              document.querySelector('[data-preset="extended"]').click();
            `);
          }
        }
      ]
    },
    {
      role: 'help',
      submenu: [
        {
          label: 'About',
          click: () => {
            mainWindow.loadURL(`http://localhost:${flaskPort}/about`);
          }
        },
        {
          label: 'Documentation',
          click: async () => {
            await shell.openExternal('https://github.com/JustGoingViral/n1o1clinicaltrials');
          }
        }
      ]
    }
  ];
  
  const menu = Menu.buildFromTemplate(template);
  Menu.setApplicationMenu(menu);
  
  // Open external links in browser
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url);
    return { action: 'deny' };
  });
}

// App ready event
app.on('ready', async () => {
  // Create splash window
  createSplashWindow();
  
  try {
    // Start Flask server
    const port = await startFlaskServer();
    
    // Wait a moment to ensure Flask is fully initialized
    setTimeout(() => {
      // Create main window
      createMainWindow(port);
    }, 2000);
  } catch (error) {
    console.error('Failed to start Flask server:', error);
    
    if (splashWindow) {
      splashWindow.webContents.executeJavaScript(`
        document.getElementById('loadingText').textContent = 'Error: Failed to start server';
        document.getElementById('loadingSpinner').style.display = 'none';
        document.getElementById('errorMessage').textContent = '${error.message}';
        document.getElementById('errorContainer').style.display = 'block';
      `);
    }
    
    // Show error dialog
    dialog.showErrorBox(
      'Server Error',
      `Failed to start the simulation server: ${error.message}\n\nThe application will now close.`
    );
    
    // Wait a moment before quitting
    setTimeout(() => {
      app.quit();
    }, 5000);
  }
});

// Quit when all windows are closed
app.on('window-all-closed', () => {
  // On macOS it is common for applications to stay open until explicitly quit
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  // On macOS it's common to re-create a window when the dock icon is clicked
  if (BrowserWindow.getAllWindows().length === 0) {
    if (serverReady) {
      createMainWindow(flaskPort);
    } else {
      createSplashWindow();
    }
  }
});

// Clean up Flask process on app quit
app.on('before-quit', () => {
  if (flaskProcess) {
    flaskProcess.kill();
    flaskProcess = null;
  }
});

// IPC event handlers
ipcMain.handle('app:getVersion', () => {
  return app.getVersion();
});

ipcMain.handle('app:saveFile', async (event, { data, defaultPath, filters }) => {
  const { canceled, filePath } = await dialog.showSaveDialog({
    defaultPath,
    filters: filters || [
      { name: 'CSV Files', extensions: ['csv'] },
      { name: 'All Files', extensions: ['*'] }
    ]
  });
  
  if (!canceled && filePath) {
    fs.writeFileSync(filePath, data);
    return filePath;
  }
  
  return null;
});

ipcMain.handle('app:openFile', async (event, { filters }) => {
  const { canceled, filePaths } = await dialog.showOpenDialog({
    properties: ['openFile'],
    filters: filters || [
      { name: 'CSV Files', extensions: ['csv'] },
      { name: 'All Files', extensions: ['*'] }
    ]
  });
  
  if (!canceled && filePaths.length > 0) {
    const filePath = filePaths[0];
    const data = fs.readFileSync(filePath, 'utf8');
    return { filePath, data };
  }
  
  return null;
});
