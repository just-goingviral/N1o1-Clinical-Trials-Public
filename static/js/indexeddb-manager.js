/**
 * N1O1 Clinical Trials - IndexedDB Manager
 * Low-level IndexedDB operations for offline data storage
 */

// Create a global namespace
window.IndexedDBManager = (function() {
  // Configuration
  const DB_NAME = 'n1o1_clinical_db';
  const DB_VERSION = 1;
  const OBJECT_STORES = [
    {
      name: 'patients',
      keyPath: 'id',
      indexes: [
        { name: 'name', keyPath: 'name', options: { unique: false } },
        { name: 'updated_at', keyPath: 'updated_at', options: { unique: false } }
      ]
    },
    {
      name: 'simulations',
      keyPath: 'id',
      indexes: [
        { name: 'patient_id', keyPath: 'patient_id', options: { unique: false } },
        { name: 'model_type', keyPath: 'model_type', options: { unique: false } },
        { name: 'created_at', keyPath: 'created_at', options: { unique: false } }
      ]
    },
    {
      name: 'no2_levels',
      keyPath: 'id',
      indexes: [
        { name: 'patient_id', keyPath: 'patient_id', options: { unique: false } },
        { name: 'measured_at', keyPath: 'measured_at', options: { unique: false } }
      ]
    },
    {
      name: 'supplement_doses',
      keyPath: 'id',
      indexes: [
        { name: 'patient_id', keyPath: 'patient_id', options: { unique: false } },
        { name: 'time_given', keyPath: 'time_given', options: { unique: false } }
      ]
    },
    {
      name: 'clinical_notes',
      keyPath: 'id',
      indexes: [
        { name: 'user_id', keyPath: 'user_id', options: { unique: false } },
        { name: 'patient_id', keyPath: 'patient_id', options: { unique: false } },
        { name: 'created_at', keyPath: 'created_at', options: { unique: false } }
      ]
    },
    {
      name: 'sync_queue',
      keyPath: 'id',
      autoIncrement: true,
      indexes: [
        { name: 'url', keyPath: 'url', options: { unique: false } },
        { name: 'timestamp', keyPath: 'timestamp', options: { unique: false } }
      ]
    }
  ];
  
  // Internal variable to hold the database instance
  let db = null;
  
  /**
   * Open the database
   * @returns {Promise} Promise resolving to the database instance
   */
  function openDatabase() {
    return new Promise((resolve, reject) => {
      if (db) {
        resolve(db);
        return;
      }
      
      if (!window.indexedDB) {
        reject(new Error('IndexedDB is not supported by your browser'));
        return;
      }
      
      const request = window.indexedDB.open(DB_NAME, DB_VERSION);
      
      request.onerror = (event) => {
        console.error('Error opening IndexedDB:', event.target.error);
        reject(event.target.error);
      };
      
      request.onsuccess = (event) => {
        db = event.target.result;
        console.log('IndexedDB opened successfully');
        resolve(db);
      };
      
      request.onupgradeneeded = (event) => {
        const db = event.target.result;
        
        // Create object stores and indexes
        OBJECT_STORES.forEach(store => {
          if (!db.objectStoreNames.contains(store.name)) {
            const options = {};
            
            // Set keyPath
            if (store.keyPath) {
              options.keyPath = store.keyPath;
            }
            
            // Set autoIncrement if specified
            if (store.autoIncrement) {
              options.autoIncrement = true;
            }
            
            // Create the object store
            const objectStore = db.createObjectStore(store.name, options);
            
            // Create indexes if defined
            if (store.indexes && Array.isArray(store.indexes)) {
              store.indexes.forEach(index => {
                objectStore.createIndex(index.name, index.keyPath, index.options || {});
              });
            }
            
            console.log(`Created object store: ${store.name}`);
          }
        });
      };
    });
  }
  
  /**
   * Close the database
   */
  function closeDatabase() {
    if (db) {
      db.close();
      db = null;
      console.log('IndexedDB closed');
    }
  }
  
  /**
   * Get one or more items from an object store
   * @param {string} storeName - Name of the object store
   * @param {string|number|null} key - Key of the item to get, or null to get all items
   * @returns {Promise} Promise resolving to the item(s)
   */
  function get(storeName, key = null) {
    return openDatabase().then(db => {
      return new Promise((resolve, reject) => {
        try {
          const transaction = db.transaction(storeName, 'readonly');
          const store = transaction.objectStore(storeName);
          
          let request;
          if (key !== null) {
            // Get a specific item
            request = store.get(key);
          } else {
            // Get all items
            request = store.getAll();
          }
          
          request.onsuccess = (event) => {
            resolve(event.target.result);
          };
          
          request.onerror = (event) => {
            console.error(`Error getting item(s) from ${storeName}:`, event.target.error);
            reject(event.target.error);
          };
        } catch (error) {
          console.error(`Error in get operation on ${storeName}:`, error);
          reject(error);
        }
      });
    });
  }
  
  /**
   * Get items by an index value
   * @param {string} storeName - Name of the object store
   * @param {string} indexName - Name of the index
   * @param {*} indexValue - Value to search for
   * @returns {Promise} Promise resolving to the matching items
   */
  function getByIndex(storeName, indexName, indexValue) {
    return openDatabase().then(db => {
      return new Promise((resolve, reject) => {
        try {
          const transaction = db.transaction(storeName, 'readonly');
          const store = transaction.objectStore(storeName);
          const index = store.index(indexName);
          
          const request = index.getAll(indexValue);
          
          request.onsuccess = (event) => {
            resolve(event.target.result);
          };
          
          request.onerror = (event) => {
            console.error(`Error getting items by index from ${storeName}:`, event.target.error);
            reject(event.target.error);
          };
        } catch (error) {
          console.error(`Error in getByIndex operation on ${storeName}:`, error);
          reject(error);
        }
      });
    });
  }
  
  /**
   * Add an item to an object store
   * @param {string} storeName - Name of the object store
   * @param {Object} item - Item to add
   * @returns {Promise} Promise resolving to the key of the added item
   */
  function add(storeName, item) {
    return openDatabase().then(db => {
      return new Promise((resolve, reject) => {
        try {
          const transaction = db.transaction(storeName, 'readwrite');
          const store = transaction.objectStore(storeName);
          
          // Add timestamp for syncing
          if (!item._createdOffline) {
            item._createdOffline = new Date().toISOString();
          }
          
          const request = store.add(item);
          
          request.onsuccess = (event) => {
            resolve(event.target.result);
          };
          
          request.onerror = (event) => {
            console.error(`Error adding item to ${storeName}:`, event.target.error);
            reject(event.target.error);
          };
        } catch (error) {
          console.error(`Error in add operation on ${storeName}:`, error);
          reject(error);
        }
      });
    });
  }
  
  /**
   * Put (add or update) an item in an object store
   * @param {string} storeName - Name of the object store
   * @param {Object} item - Item to put
   * @returns {Promise} Promise resolving to the key of the added/updated item
   */
  function put(storeName, item) {
    return openDatabase().then(db => {
      return new Promise((resolve, reject) => {
        try {
          const transaction = db.transaction(storeName, 'readwrite');
          const store = transaction.objectStore(storeName);
          
          // Add timestamp for syncing
          item._updatedOffline = new Date().toISOString();
          
          const request = store.put(item);
          
          request.onsuccess = (event) => {
            resolve(event.target.result);
          };
          
          request.onerror = (event) => {
            console.error(`Error putting item to ${storeName}:`, event.target.error);
            reject(event.target.error);
          };
        } catch (error) {
          console.error(`Error in put operation on ${storeName}:`, error);
          reject(error);
        }
      });
    });
  }
  
  /**
   * Delete an item from an object store
   * @param {string} storeName - Name of the object store
   * @param {string|number} key - Key of the item to delete
   * @returns {Promise} Promise resolving when the item is deleted
   */
  function remove(storeName, key) {
    return openDatabase().then(db => {
      return new Promise((resolve, reject) => {
        try {
          const transaction = db.transaction(storeName, 'readwrite');
          const store = transaction.objectStore(storeName);
          
          const request = store.delete(key);
          
          request.onsuccess = () => {
            resolve(true);
          };
          
          request.onerror = (event) => {
            console.error(`Error deleting item from ${storeName}:`, event.target.error);
            reject(event.target.error);
          };
        } catch (error) {
          console.error(`Error in remove operation on ${storeName}:`, error);
          reject(error);
        }
      });
    });
  }
  
  /**
   * Clear all items from an object store
   * @param {string} storeName - Name of the object store
   * @returns {Promise} Promise resolving when the store is cleared
   */
  function clear(storeName) {
    return openDatabase().then(db => {
      return new Promise((resolve, reject) => {
        try {
          const transaction = db.transaction(storeName, 'readwrite');
          const store = transaction.objectStore(storeName);
          
          const request = store.clear();
          
          request.onsuccess = () => {
            resolve(true);
          };
          
          request.onerror = (event) => {
            console.error(`Error clearing ${storeName}:`, event.target.error);
            reject(event.target.error);
          };
        } catch (error) {
          console.error(`Error in clear operation on ${storeName}:`, error);
          reject(error);
        }
      });
    });
  }
  
  /**
   * Count items in an object store
   * @param {string} storeName - Name of the object store
   * @returns {Promise} Promise resolving to the count
   */
  function count(storeName) {
    return openDatabase().then(db => {
      return new Promise((resolve, reject) => {
        try {
          const transaction = db.transaction(storeName, 'readonly');
          const store = transaction.objectStore(storeName);
          
          const request = store.count();
          
          request.onsuccess = (event) => {
            resolve(event.target.result);
          };
          
          request.onerror = (event) => {
            console.error(`Error counting items in ${storeName}:`, event.target.error);
            reject(event.target.error);
          };
        } catch (error) {
          console.error(`Error in count operation on ${storeName}:`, error);
          reject(error);
        }
      });
    });
  }
  
  /**
   * Get all object store names
   * @returns {Promise} Promise resolving to an array of store names
   */
  function getObjectStoreNames() {
    return openDatabase().then(db => {
      return Array.from(db.objectStoreNames);
    });
  }
  
  /**
   * Check if IndexedDB is supported by the browser
   * @returns {boolean} Whether IndexedDB is supported
   */
  function isSupported() {
    return !!window.indexedDB;
  }
  
  /**
   * Get database information
   * @returns {Object} Database information
   */
  function getDatabaseInfo() {
    return {
      name: DB_NAME,
      version: DB_VERSION,
      objectStores: OBJECT_STORES.map(store => store.name)
    };
  }
  
  // Initialize the database when the script loads
  openDatabase().catch(error => {
    console.error('Failed to initialize IndexedDB:', error);
  });
  
  // Return public methods
  return {
    openDatabase,
    closeDatabase,
    get,
    getByIndex,
    add,
    put,
    remove,
    clear,
    count,
    getObjectStoreNames,
    isSupported,
    getDatabaseInfo
  };
})();