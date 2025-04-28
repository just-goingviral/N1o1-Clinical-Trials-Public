/**
 * N1O1 Clinical Trials - Sync Manager
 * Handles synchronization of offline data with the server
 */

// Create a global SyncManager namespace
window.SyncManager = (function() {
  // Configuration
  const SYNC_INTERVAL = 60000; // 1 minute in milliseconds
  const MAX_SYNC_ATTEMPTS = 3; // Maximum number of sync attempts
  
  // State
  let isSyncing = false;
  let lastSyncTime = 0;
  let syncIntervalId = null;
  let registeredSyncListeners = [];
  
  /**
   * Initialize the sync manager
   */
  function init() {
    console.log('Initializing sync manager');
    
    // Register for online/offline events
    window.addEventListener('online', handleOnlineEvent);
    window.addEventListener('offline', handleOfflineEvent);
    
    // Check if service worker supports background sync
    if ('serviceWorker' in navigator && 'SyncManager' in window) {
      console.log('Background Sync API is supported');
      setupPeriodicSync();
    } else {
      console.log('Background Sync API is not supported, using interval-based sync');
      setupIntervalSync();
    }
    
    // Set up event listeners
    setupEventListeners();
    
    // Create sync indicator UI
    createSyncIndicator();
    
    // Check for pending changes on startup
    setTimeout(checkPendingChanges, 2000);
  }
  
  /**
   * Set up periodic background sync using the Background Sync API
   */
  function setupPeriodicSync() {
    navigator.serviceWorker.ready.then(registration => {
      // Try to register for periodic sync if available
      if ('periodicSync' in registration) {
        const syncTag = 'sync-data';
        
        // Check if already registered
        registration.periodicSync.getTags().then(tags => {
          if (!tags.includes(syncTag)) {
            try {
              registration.periodicSync.register(syncTag, {
                minInterval: SYNC_INTERVAL
              }).then(() => {
                console.log('Periodic background sync registered');
              }).catch(err => {
                console.error('Error registering periodic sync:', err);
                // Fall back to interval-based sync
                setupIntervalSync();
              });
            } catch (error) {
              console.error('Error setting up periodic sync:', error);
              setupIntervalSync();
            }
          } else {
            console.log('Periodic background sync already registered');
          }
        });
      } else {
        // If periodic sync is not available, use one-time background sync
        console.log('Periodic background sync not supported, using one-time sync');
        registration.sync.register('sync-data').then(() => {
          console.log('One-time background sync registered');
        }).catch(err => {
          console.error('Error registering one-time sync:', err);
          setupIntervalSync();
        });
      }
    }).catch(err => {
      console.error('Error accessing service worker:', err);
      setupIntervalSync();
    });
  }
  
  /**
   * Set up interval-based synchronization
   */
  function setupIntervalSync() {
    if (syncIntervalId) {
      clearInterval(syncIntervalId);
    }
    
    syncIntervalId = setInterval(() => {
      if (navigator.onLine) {
        syncIfNeeded();
      }
    }, SYNC_INTERVAL);
    
    console.log('Interval-based sync set up');
  }
  
  /**
   * Set up event listeners
   */
  function setupEventListeners() {
    // Listen for sync completion messages from service worker
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.addEventListener('message', event => {
        if (event.data && event.data.type === 'sync_status') {
          handleSyncComplete(event.data.status === 'complete', event.data.message);
        }
      });
    }
    
    // Listen for storage events (in case sync is triggered from another tab)
    window.addEventListener('storage', event => {
      if (event.key === 'n1o1_last_sync') {
        lastSyncTime = parseInt(event.newValue, 10) || 0;
      }
    });
  }
  
  /**
   * Handle online event
   */
  function handleOnlineEvent() {
    console.log('Device is now online');
    
    // Add a slight delay to ensure connection is stable
    setTimeout(() => {
      // Check if we need to sync
      checkPendingChanges().then(hasPending => {
        if (hasPending) {
          showPendingChanges();
          
          // If it's been a while since the last sync, do it automatically
          if (isSyncStale()) {
            syncIfNeeded();
          }
        }
      });
    }, 2000);
  }
  
  /**
   * Handle offline event
   */
  function handleOfflineEvent() {
    console.log('Device is now offline');
    
    // Update any UI elements that need to reflect offline status
    const syncIndicator = document.getElementById('sync-status-indicator');
    if (syncIndicator) {
      syncIndicator.innerHTML = `
        <span class="badge bg-danger">
          <i class="bi bi-wifi-off"></i> Offline
        </span>
      `;
    }
  }
  
  /**
   * Create a sync indicator element
   */
  function createSyncIndicator() {
    let indicator = document.getElementById('sync-status-indicator');
    
    if (!indicator) {
      indicator = document.createElement('div');
      indicator.id = 'sync-status-indicator';
      indicator.className = 'sync-status-indicator';
      
      // Add it to the page if there's a suitable container
      const container = document.querySelector('.sync-status-container') || 
                        document.querySelector('header') ||
                        document.querySelector('nav') ||
                        document.querySelector('body');
      
      if (container) {
        container.appendChild(indicator);
      }
    }
    
    // Initial status
    updateSyncIndicator(navigator.onLine ? 'online' : 'offline');
  }
  
  /**
   * Update the sync indicator with current status
   * @param {string} status - Current sync status
   * @param {Object} details - Additional details
   */
  function updateSyncIndicator(status, details = {}) {
    const indicator = document.getElementById('sync-status-indicator');
    if (!indicator) return;
    
    switch (status) {
      case 'offline':
        indicator.innerHTML = `
          <span class="badge bg-danger">
            <i class="bi bi-wifi-off"></i> Offline
          </span>
        `;
        break;
      
      case 'syncing':
        indicator.innerHTML = `
          <span class="badge bg-warning text-dark">
            <i class="bi bi-arrow-repeat"></i> Syncing...
          </span>
        `;
        break;
      
      case 'pending':
        indicator.innerHTML = `
          <span class="badge bg-warning text-dark">
            <i class="bi bi-cloud-arrow-up"></i> Changes Pending
          </span>
        `;
        break;
      
      case 'complete':
        indicator.innerHTML = `
          <span class="badge bg-success">
            <i class="bi bi-check2"></i> Synced
          </span>
        `;
        
        // Automatically revert to online after a few seconds
        setTimeout(() => {
          updateSyncIndicator('online');
        }, 3000);
        break;
      
      case 'error':
        indicator.innerHTML = `
          <span class="badge bg-danger">
            <i class="bi bi-exclamation-triangle"></i> Sync Failed
          </span>
        `;
        break;
      
      case 'online':
      default:
        indicator.innerHTML = `
          <span class="badge bg-success">
            <i class="bi bi-wifi"></i> Online
          </span>
        `;
        break;
    }
  }
  
  /**
   * Show pending changes indicator
   */
  function showPendingChanges() {
    updateSyncIndicator('pending');
    
    // Show a sync button or notification if appropriate
    const syncButtonContainer = document.getElementById('sync-button-container');
    if (syncButtonContainer) {
      syncButtonContainer.innerHTML = `
        <button id="manual-sync-button" class="btn btn-sm btn-warning">
          <i class="bi bi-arrow-repeat"></i> Sync Changes
        </button>
      `;
      
      document.getElementById('manual-sync-button').addEventListener('click', forceSync);
    }
  }
  
  /**
   * Check if pending changes exist
   */
  function checkPendingChanges() {
    // Use the OfflineData API to check for pending sync items
    if (window.OfflineData && typeof window.OfflineData.hasPendingSync === 'function') {
      return window.OfflineData.hasPendingSync();
    }
    
    return Promise.resolve(false);
  }
  
  /**
   * Check if a sync is needed and perform it
   */
  function syncIfNeeded() {
    if (isSyncing || !navigator.onLine) {
      return Promise.resolve(false);
    }
    
    return checkPendingChanges().then(hasPending => {
      if (hasPending) {
        return performSync();
      }
      return false;
    });
  }
  
  /**
   * Perform the actual synchronization
   */
  function performSync() {
    if (isSyncing) {
      return Promise.resolve(false);
    }
    
    isSyncing = true;
    updateSyncIndicator('syncing');
    
    console.log('Starting data synchronization');
    
    // Notify any listeners that sync is starting
    registeredSyncListeners.forEach(listener => {
      if (typeof listener.onSyncStart === 'function') {
        try {
          listener.onSyncStart();
        } catch (e) {
          console.error('Error in sync start listener:', e);
        }
      }
    });
    
    // Use the OfflineData API to process the sync queue
    let syncPromise;
    
    if (window.OfflineData && typeof window.OfflineData.processQueue === 'function') {
      syncPromise = window.OfflineData.processQueue();
    } else {
      // If OfflineData API is not available, try service worker sync
      if ('serviceWorker' in navigator && 'SyncManager' in window) {
        syncPromise = navigator.serviceWorker.ready
          .then(registration => {
            return registration.sync.register('sync-data')
              .then(() => {
                // This doesn't actually wait for the sync to complete,
                // that will be handled via the message event listener
                return { success: true, inProgress: true };
              });
          })
          .catch(error => {
            console.error('Error registering sync:', error);
            return { success: false, error: error.message };
          });
      } else {
        // If no sync method is available, just return success
        syncPromise = Promise.resolve({ success: true, noSyncNeeded: true });
      }
    }
    
    return syncPromise
      .then(result => {
        if (result.inProgress) {
          // The sync is still in progress, it will complete async
          console.log('Sync operation in progress');
          return true;
        }
        
        console.log('Sync completed:', result);
        
        lastSyncTime = Date.now();
        localStorage.setItem('n1o1_last_sync', lastSyncTime.toString());
        
        isSyncing = false;
        updateSyncIndicator('complete');
        
        // Notify any listeners that sync is complete
        registeredSyncListeners.forEach(listener => {
          if (typeof listener.onSyncComplete === 'function') {
            try {
              listener.onSyncComplete(result);
            } catch (e) {
              console.error('Error in sync complete listener:', e);
            }
          }
        });
        
        return result.success;
      })
      .catch(error => {
        handleSyncFailure(error);
        return false;
      });
  }
  
  /**
   * Handle a sync failure
   * @param {Error|string} error - Error that occurred
   */
  function handleSyncFailure(error) {
    console.error('Sync failed:', error);
    
    isSyncing = false;
    updateSyncIndicator('error');
    
    // Notify any listeners that sync failed
    registeredSyncListeners.forEach(listener => {
      if (typeof listener.onSyncError === 'function') {
        try {
          listener.onSyncError(error);
        } catch (e) {
          console.error('Error in sync error listener:', e);
        }
      }
    });
  }
  
  /**
   * Check if a sync operation is stale
   * @returns {boolean} Whether the sync is stale
   */
  function isSyncStale() {
    const now = Date.now();
    const lastSync = lastSyncTime || parseInt(localStorage.getItem('n1o1_last_sync'), 10) || 0;
    
    // Consider sync stale if it's been more than the sync interval
    return (now - lastSync) > SYNC_INTERVAL;
  }
  
  /**
   * Force a sync, even if there are no known pending actions
   */
  function forceSync() {
    return performSync();
  }
  
  /**
   * Handle sync complete event (from service worker)
   */
  function handleSyncComplete(success, message) {
    console.log('Sync complete:', success, message);
    
    isSyncing = false;
    lastSyncTime = Date.now();
    localStorage.setItem('n1o1_last_sync', lastSyncTime.toString());
    
    updateSyncIndicator(success ? 'complete' : 'error');
    
    // Notify any listeners
    registeredSyncListeners.forEach(listener => {
      const callback = success ? listener.onSyncComplete : listener.onSyncError;
      if (typeof callback === 'function') {
        try {
          callback(success ? { success: true, message } : new Error(message));
        } catch (e) {
          console.error('Error in sync listener:', e);
        }
      }
    });
    
    return success;
  }
  
  /**
   * Register a sync event listener
   * @param {Object} listener - Object with sync event callbacks
   */
  function registerSyncListener(listener) {
    if (typeof listener === 'object') {
      registeredSyncListeners.push(listener);
    }
  }
  
  /**
   * Unregister a sync event listener
   * @param {Object} listener - Previously registered listener object
   */
  function unregisterSyncListener(listener) {
    const index = registeredSyncListeners.indexOf(listener);
    if (index !== -1) {
      registeredSyncListeners.splice(index, 1);
    }
  }
  
  // Initialize when the DOM is ready
  document.addEventListener('DOMContentLoaded', init);
  
  // Public API
  return {
    forceSync,
    checkPendingChanges,
    registerSyncListener,
    unregisterSyncListener
  };
})();