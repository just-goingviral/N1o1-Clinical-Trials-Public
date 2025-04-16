/**
 * Preload script for Electron app
 * Exposes specific Node.js APIs to the renderer process
 * Author: Dustin Salinas
 * License: MIT
 */

const { contextBridge, ipcRenderer } = require('electron');
const os = require('os');

// Define the API that will be exposed to the renderer process
contextBridge.exposeInMainWorld('nodeDynamics', {
  // Application info
  appInfo: {
    getVersion: () => ipcRenderer.invoke('app:getVersion'),
    getPlatform: () => process.platform,
    getOsInfo: () => ({
      platform: os.platform(),
      release: os.release(),
      arch: os.arch(),
      cpus: os.cpus().length,
      memory: Math.round(os.totalmem() / (1024 * 1024 * 1024)) // Total memory in GB
    })
  },
  
  // File operations
  files: {
    saveFile: (options) => ipcRenderer.invoke('app:saveFile', options),
    openFile: (options) => ipcRenderer.invoke('app:openFile', options),
    
    // Helper function to save CSV data
    saveCsv: async (csvData, defaultFilename = 'simulation_results.csv') => {
      const result = await ipcRenderer.invoke('app:saveFile', {
        data: csvData,
        defaultPath: defaultFilename,
        filters: [
          { name: 'CSV Files', extensions: ['csv'] },
          { name: 'All Files', extensions: ['*'] }
        ]
      });
      
      return result;
    },
    
    // Helper function to save an image
    saveImage: async (imgData, defaultFilename = 'plot.png') => {
      // Convert base64 image to binary
      const base64Data = imgData.replace(/^data:image\/\w+;base64,/, '');
      const binaryData = Buffer.from(base64Data, 'base64');
      
      const result = await ipcRenderer.invoke('app:saveFile', {
        data: binaryData,
        defaultPath: defaultFilename,
        filters: [
          { name: 'PNG Image', extensions: ['png'] },
          { name: 'All Files', extensions: ['*'] }
        ]
      });
      
      return result;
    },
    
    // Helper function to open and parse CSV
    openCsv: async () => {
      const result = await ipcRenderer.invoke('app:openFile', {
        filters: [
          { name: 'CSV Files', extensions: ['csv'] },
          { name: 'All Files', extensions: ['*'] }
        ]
      });
      
      return result;
    }
  }
});

// Notify the main process when the page has loaded
window.addEventListener('DOMContentLoaded', () => {
  // Add desktop-specific classes to the body
  document.body.classList.add('electron-app');
  
  // Add platform-specific classes
  document.body.classList.add(`platform-${process.platform}`);
  
  // Initialize electron-specific features when app.js loads
  const initDesktopFeatures = () => {
    // Replace file download links with desktop file save dialogs
    const downloadCsvBtn = document.getElementById('downloadCsv');
    if (downloadCsvBtn) {
      const originalClickHandler = downloadCsvBtn.onclick;
      downloadCsvBtn.onclick = (e) => {
        e.preventDefault();
        
        // Get CSV data from the server
        fetch('/api/export-csv')
          .then(response => response.blob())
          .then(blob => {
            const reader = new FileReader();
            reader.onload = () => {
              window.nodeDynamics.files.saveCsv(reader.result, 'nitrite_simulation_results.csv')
                .then(filePath => {
                  if (filePath) {
                    // Show success message
                    const toastFn = window.showToast || console.log;
                    toastFn(`File saved to: ${filePath}`, 'success');
                  }
                });
            };
            reader.readAsText(blob);
          })
          .catch(err => {
            const toastFn = window.showToast || console.error;
            toastFn(`Error exporting CSV: ${err.message}`, 'danger');
          });
      };
    }
    
    // Add app version to footer
    window.nodeDynamics.appInfo.getVersion().then(version => {
      const footerEl = document.querySelector('footer .text-muted');
      if (footerEl) {
        footerEl.innerHTML += ` | v${version}`;
      }
    });
  };
  
  // Wait for app.js to load and then initialize desktop features
  const checkForAppJs = setInterval(() => {
    if (window.showToast) {
      clearInterval(checkForAppJs);
      initDesktopFeatures();
    }
  }, 100);
});
