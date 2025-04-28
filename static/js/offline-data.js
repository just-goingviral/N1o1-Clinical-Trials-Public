/**
 * N1O1 Clinical Trials - Offline Data Manager
 * Manages offline data storage and synchronization using IndexedDB
 */

// Create a global OfflineData namespace
window.OfflineData = (function() {
  // IndexedDB database info
  const DB_NAME = 'n1o1_offline_db';
  const DB_VERSION = 1;
  let db = null;
  
  // Status information
  let isOnlineStatus = navigator.onLine;
  let hasPendingSyncItems = false;
  
  /**
   * Initialize the offline data system
   */
  function init() {
    console.log('Initializing offline data system');
    
    // Open/create the IndexedDB database
    openDatabase()
      .then(() => {
        console.log('Offline database initialized');
        updateOfflineStatus();
        hasPendingSync();
      })
      .catch(err => {
        console.error('Failed to initialize offline database:', err);
      });
    
    // Set up event listeners for online/offline events
    window.addEventListener('online', handleOnlineEvent);
    window.addEventListener('offline', handleOfflineEvent);
    
    // Check for pending sync items periodically
    setInterval(hasPendingSync, 60000); // Check every minute
    
    // Create or update the status indicator
    createStatusIndicator();
  }
  
  /**
   * Open the IndexedDB database
   */
  function openDatabase() {
    return new Promise((resolve, reject) => {
      if (!window.indexedDB) {
        reject(new Error('IndexedDB is not supported in this browser'));
        return;
      }
      
      const request = indexedDB.open(DB_NAME, DB_VERSION);
      
      request.onerror = function(event) {
        console.error('Error opening offline database:', event.target.error);
        reject(event.target.error);
      };
      
      request.onsuccess = function(event) {
        db = event.target.result;
        console.log('Database opened successfully');
        resolve(db);
      };
      
      request.onupgradeneeded = function(event) {
        const db = event.target.result;
        
        // Create object stores for different data types
        if (!db.objectStoreNames.contains('patients')) {
          const patientsStore = db.createObjectStore('patients', { keyPath: 'id' });
          patientsStore.createIndex('name', 'name', { unique: false });
        }
        
        if (!db.objectStoreNames.contains('simulations')) {
          const simulationsStore = db.createObjectStore('simulations', { keyPath: 'id' });
          simulationsStore.createIndex('patient_id', 'patient_id', { unique: false });
        }
        
        if (!db.objectStoreNames.contains('measurements')) {
          const measurementsStore = db.createObjectStore('measurements', { keyPath: 'id' });
          measurementsStore.createIndex('patient_id', 'patient_id', { unique: false });
        }
        
        if (!db.objectStoreNames.contains('notes')) {
          const notesStore = db.createObjectStore('notes', { keyPath: 'id' });
          notesStore.createIndex('patient_id', 'patient_id', { unique: false });
        }
        
        if (!db.objectStoreNames.contains('sync_queue')) {
          db.createObjectStore('sync_queue', { keyPath: 'id', autoIncrement: true });
        }
      };
    });
  }
  
  /**
   * Check if online
   */
  function isOnline() {
    return isOnlineStatus;
  }
  
  /**
   * Check if offline storage is available
   */
  function isOfflineStorageAvailable() {
    return !!window.indexedDB && db !== null;
  }
  
  /**
   * Enhanced fetch with offline support
   */
  function fetchWithOfflineSupport(url, options = {}) {
    const isGetRequest = !options.method || options.method === 'GET';
    
    // For GET requests, try network first, then fall back to cache
    if (isGetRequest) {
      return fetch(url, options)
        .then(response => {
          if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
          }
          return response.json();
        })
        .catch(error => {
          console.warn(`Network request failed for ${url}, trying offline data:`, error);
          
          // Extract entity type and ID from URL
          const urlParts = url.split('/');
          const type = urlParts[urlParts.length - 2];
          const id = urlParts[urlParts.length - 1];
          
          if (isEntityUrl(url)) {
            return getStoredData(type, id);
          } else if (isCollectionUrl(url)) {
            return getStoredData(type);
          } else {
            throw new Error('No offline data available for this request');
          }
        });
    }
    
    // For non-GET requests (POST, PUT, DELETE), queue them if offline
    if (!isOnline()) {
      // Add to sync queue
      return addToSyncQueue(url, options)
        .then(() => {
          hasPendingSyncItems = true;
          updateOfflineStatus();
          
          // If this is a POST/PUT, we can optimistically update local data
          if (options.body && (options.method === 'POST' || options.method === 'PUT')) {
            try {
              const data = JSON.parse(options.body);
              const type = getEntityTypeFromUrl(url);
              
              if (type && data) {
                // Generate a temporary ID for new items
                if (options.method === 'POST' && !data.id) {
                  data.id = `temp_${Date.now()}_${Math.floor(Math.random() * 1000)}`;
                  data._isLocalOnly = true;
                }
                
                return saveEntityData(type, data, data.id)
                  .then(() => {
                    return { ...data, _queued: true };
                  });
              }
            } catch (e) {
              console.error('Error parsing request body for offline queue:', e);
            }
          }
          
          return { _queued: true, message: 'Request queued for sync' };
        });
    }
    
    // If online, proceed with normal fetch
    return fetch(url, options).then(response => response.json());
  }
  
  /**
   * Get data from offline storage
   */
  function getStoredData(type, id = null) {
    return new Promise((resolve, reject) => {
      if (!db) {
        reject(new Error('Database not initialized'));
        return;
      }
      
      try {
        const transaction = db.transaction([type], 'readonly');
        const store = transaction.objectStore(type);
        
        if (id !== null) {
          // Get a single item
          const request = store.get(id);
          
          request.onsuccess = function(event) {
            resolve(event.target.result || null);
          };
          
          request.onerror = function(event) {
            reject(event.target.error);
          };
        } else {
          // Get all items
          const request = store.getAll();
          
          request.onsuccess = function(event) {
            resolve(event.target.result || []);
          };
          
          request.onerror = function(event) {
            reject(event.target.error);
          };
        }
      } catch (error) {
        reject(error);
      }
    });
  }
  
  /**
   * Save data to offline storage
   */
  function saveEntityData(type, data, id = null) {
    return new Promise((resolve, reject) => {
      if (!db) {
        reject(new Error('Database not initialized'));
        return;
      }
      
      try {
        const transaction = db.transaction([type], 'readwrite');
        const store = transaction.objectStore(type);
        
        // If no ID is provided, use the one in the data
        id = id || data.id;
        
        // Make sure data has the correct ID
        if (id && data.id !== id) {
          data.id = id;
        }
        
        // Add '_offlineUpdatedAt' timestamp
        data._offlineUpdatedAt = Date.now();
        
        const request = store.put(data);
        
        request.onsuccess = function(event) {
          resolve(data);
        };
        
        request.onerror = function(event) {
          reject(event.target.error);
        };
      } catch (error) {
        reject(error);
      }
    });
  }
  
  /**
   * Delete data from offline storage
   */
  function deleteEntityData(type, id) {
    return new Promise((resolve, reject) => {
      if (!db) {
        reject(new Error('Database not initialized'));
        return;
      }
      
      try {
        const transaction = db.transaction([type], 'readwrite');
        const store = transaction.objectStore(type);
        const request = store.delete(id);
        
        request.onsuccess = function(event) {
          resolve(true);
        };
        
        request.onerror = function(event) {
          reject(event.target.error);
        };
      } catch (error) {
        reject(error);
      }
    });
  }
  
  /**
   * Add a request to the sync queue
   */
  function addToSyncQueue(url, options) {
    return new Promise((resolve, reject) => {
      if (!db) {
        reject(new Error('Database not initialized'));
        return;
      }
      
      try {
        const transaction = db.transaction(['sync_queue'], 'readwrite');
        const store = transaction.objectStore('sync_queue');
        
        const queueItem = {
          url: url,
          options: options,
          timestamp: Date.now(),
          attempts: 0
        };
        
        const request = store.add(queueItem);
        
        request.onsuccess = function(event) {
          hasPendingSyncItems = true;
          updateOfflineStatus();
          resolve(true);
        };
        
        request.onerror = function(event) {
          reject(event.target.error);
        };
      } catch (error) {
        reject(error);
      }
    });
  }
  
  /**
   * Check if there are pending items in the sync queue
   */
  function hasPendingSync() {
    return new Promise((resolve, reject) => {
      if (!db) {
        reject(new Error('Database not initialized'));
        return;
      }
      
      try {
        const transaction = db.transaction(['sync_queue'], 'readonly');
        const store = transaction.objectStore('sync_queue');
        const countRequest = store.count();
        
        countRequest.onsuccess = function(event) {
          const count = event.target.result;
          hasPendingSyncItems = count > 0;
          updateOfflineStatus();
          resolve(hasPendingSyncItems);
        };
        
        countRequest.onerror = function(event) {
          reject(event.target.error);
        };
      } catch (error) {
        reject(error);
      }
    });
  }
  
  /**
   * Process sync queue when back online
   */
  function processQueue() {
    return new Promise((resolve, reject) => {
      if (!isOnline()) {
        reject(new Error('Cannot process queue while offline'));
        return;
      }
      
      if (!db) {
        reject(new Error('Database not initialized'));
        return;
      }
      
      try {
        const transaction = db.transaction(['sync_queue'], 'readonly');
        const store = transaction.objectStore('sync_queue');
        const request = store.getAll();
        
        request.onsuccess = function(event) {
          const items = event.target.result || [];
          
          if (items.length === 0) {
            hasPendingSyncItems = false;
            updateOfflineStatus();
            resolve({ processed: 0, success: true });
            return;
          }
          
          let processed = 0;
          let failed = 0;
          
          // Process each item sequentially
          function processNext(index) {
            if (index >= items.length) {
              hasPendingSync().then(() => {
                updateOfflineStatus();
                resolve({ processed, failed, success: failed === 0 });
              });
              return;
            }
            
            const item = items[index];
            
            // Send the actual request
            fetch(item.url, item.options)
              .then(response => {
                if (!response.ok) {
                  throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
              })
              .then(data => {
                // Remove from queue on success
                removeFromQueue(item.id).then(() => {
                  processed++;
                  processNext(index + 1);
                });
              })
              .catch(error => {
                console.error('Error processing queued request:', error);
                updateQueueItemAttempts(item.id).then(() => {
                  failed++;
                  processNext(index + 1);
                });
              });
          }
          
          // Start processing
          processNext(0);
          
        };
        
        request.onerror = function(event) {
          reject(event.target.error);
        };
      } catch (error) {
        reject(error);
      }
    });
  }
  
  /**
   * Remove an item from the sync queue
   */
  function removeFromQueue(id) {
    return new Promise((resolve, reject) => {
      if (!db) {
        reject(new Error('Database not initialized'));
        return;
      }
      
      try {
        const transaction = db.transaction(['sync_queue'], 'readwrite');
        const store = transaction.objectStore('sync_queue');
        const request = store.delete(id);
        
        request.onsuccess = function(event) {
          resolve(true);
        };
        
        request.onerror = function(event) {
          reject(event.target.error);
        };
      } catch (error) {
        reject(error);
      }
    });
  }
  
  /**
   * Update attempt count for a queue item
   */
  function updateQueueItemAttempts(id) {
    return new Promise((resolve, reject) => {
      if (!db) {
        reject(new Error('Database not initialized'));
        return;
      }
      
      try {
        const transaction = db.transaction(['sync_queue'], 'readwrite');
        const store = transaction.objectStore('sync_queue');
        const getRequest = store.get(id);
        
        getRequest.onsuccess = function(event) {
          const item = event.target.result;
          if (item) {
            item.attempts = (item.attempts || 0) + 1;
            item.lastAttempt = Date.now();
            
            const updateRequest = store.put(item);
            updateRequest.onsuccess = function() {
              resolve(true);
            };
            updateRequest.onerror = function(event) {
              reject(event.target.error);
            };
          } else {
            resolve(false);
          }
        };
        
        getRequest.onerror = function(event) {
          reject(event.target.error);
        };
      } catch (error) {
        reject(error);
      }
    });
  }
  
  /**
   * Create a status indicator in the UI
   */
  function createStatusIndicator() {
    let statusContainer = document.getElementById('offline-status-container');
    
    if (!statusContainer) {
      statusContainer = document.createElement('div');
      statusContainer.id = 'offline-status-container';
      statusContainer.style.position = 'fixed';
      statusContainer.style.bottom = '20px';
      statusContainer.style.right = '20px';
      statusContainer.style.zIndex = '1000';
      document.body.appendChild(statusContainer);
    }
    
    updateOfflineStatus();
  }
  
  /**
   * Update the offline status indicator
   */
  function updateOfflineStatus() {
    const statusContainer = document.getElementById('offline-status-container');
    if (!statusContainer) return;
    
    // Clear existing content
    statusContainer.innerHTML = '';
    
    if (!isOnline()) {
      // Offline indicator
      const offlineIndicator = document.createElement('div');
      offlineIndicator.className = 'offline-indicator';
      offlineIndicator.innerHTML = `
        <div class="toast show" role="alert" aria-live="assertive" aria-atomic="true">
          <div class="toast-header bg-danger text-white">
            <i class="bi bi-wifi-off me-2"></i>
            <strong class="me-auto">Offline Mode</strong>
            <small>Working with local data</small>
          </div>
          <div class="toast-body">
            You're currently offline. Data changes will be synchronized when you reconnect.
          </div>
        </div>
      `;
      statusContainer.appendChild(offlineIndicator);
    } else if (hasPendingSyncItems) {
      // Pending sync indicator
      const syncIndicator = document.createElement('div');
      syncIndicator.className = 'sync-indicator';
      syncIndicator.innerHTML = `
        <div class="toast show" role="alert" aria-live="assertive" aria-atomic="true">
          <div class="toast-header bg-warning text-dark">
            <i class="bi bi-arrow-repeat me-2"></i>
            <strong class="me-auto">Sync Pending</strong>
            <small>Online, syncing...</small>
          </div>
          <div class="toast-body">
            Synchronizing your offline changes...
            <button class="btn btn-sm btn-primary mt-2" id="force-sync-btn">
              Sync Now
            </button>
          </div>
        </div>
      `;
      statusContainer.appendChild(syncIndicator);
      
      // Add event listener to the sync button
      setTimeout(() => {
        const syncButton = document.getElementById('force-sync-btn');
        if (syncButton) {
          syncButton.addEventListener('click', function() {
            processQueue().then(() => {
              // Show success toast
              const toastEl = document.createElement('div');
              toastEl.className = 'toast align-items-center text-white bg-success border-0';
              toastEl.setAttribute('role', 'alert');
              toastEl.setAttribute('aria-live', 'assertive');
              toastEl.setAttribute('aria-atomic', 'true');
              toastEl.innerHTML = `
                <div class="d-flex">
                  <div class="toast-body">
                    Synchronization complete!
                  </div>
                  <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
                </div>
              `;
              document.body.appendChild(toastEl);
              const toast = new bootstrap.Toast(toastEl);
              toast.show();
              
              // Remove the toast after it's hidden
              toastEl.addEventListener('hidden.bs.toast', function() {
                toastEl.remove();
              });
            });
          });
        }
      }, 100);
    }
  }
  
  /**
   * Handle online event
   */
  function handleOnlineEvent() {
    console.log('Device is now online');
    isOnlineStatus = true;
    updateOfflineStatus();
    
    // Try to process the sync queue
    if (hasPendingSyncItems) {
      processQueue().then(result => {
        console.log('Sync queue processed:', result);
      }).catch(error => {
        console.error('Error processing sync queue:', error);
      });
    }
  }
  
  /**
   * Handle offline event
   */
  function handleOfflineEvent() {
    console.log('Device is now offline');
    isOnlineStatus = false;
    updateOfflineStatus();
  }
  
  /**
   * Check if a URL points to a single entity
   */
  function isEntityUrl(url) {
    const entityPatterns = [
      /\/api\/patients\/\d+$/,
      /\/api\/simulations\/\d+$/,
      /\/api\/measurements\/\d+$/,
      /\/api\/notes\/\d+$/
    ];
    
    return entityPatterns.some(pattern => pattern.test(url));
  }
  
  /**
   * Check if a URL points to a collection
   */
  function isCollectionUrl(url) {
    const collectionPatterns = [
      /\/api\/patients\/?(\?.*)?$/,
      /\/api\/simulations\/?(\?.*)?$/,
      /\/api\/measurements\/?(\?.*)?$/,
      /\/api\/notes\/?(\?.*)?$/
    ];
    
    return collectionPatterns.some(pattern => pattern.test(url));
  }
  
  /**
   * Extract entity type from URL
   */
  function getEntityTypeFromUrl(url) {
    const matches = url.match(/\/api\/([a-zA-Z]+)/);
    if (matches && matches[1]) {
      return matches[1];
    }
    return null;
  }
  
  // Initialize when the DOM is ready
  document.addEventListener('DOMContentLoaded', init);
  
  // Public API
  return {
    isOnline,
    isOfflineStorageAvailable,
    fetchWithOfflineSupport,
    getStoredData,
    saveEntityData,
    deleteEntityData,
    hasPendingSync,
    processQueue
  };
})();