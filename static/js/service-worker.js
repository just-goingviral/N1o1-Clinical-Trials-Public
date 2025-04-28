/**
 * N1O1 Clinical Trials - Service Worker
 * Handles caching and offline functionality
 */

// Cache version - increment when updating resources
const CACHE_VERSION = 'v1';
const CACHE_NAME = `n1o1-cache-${CACHE_VERSION}`;

// Resources to pre-cache during installation
const PRECACHE_RESOURCES = [
  '/',
  '/offline',
  '/static/css/style.css',
  '/static/css/responsive.css',
  '/static/css/bootstrap-agent-dark-theme.min.css',
  '/static/js/app.js',
  '/static/js/offline-data.js',
  '/static/js/sync-manager.js',
  '/static/images/offline-graphic.svg',
  '/static/images/n1o1-favicon.svg',
  '/static/images/logo.png'
];

// Files to cache when requested
const DYNAMIC_CACHE_EXTENSIONS = [
  '.css',
  '.js',
  '.png',
  '.jpg',
  '.jpeg',
  '.svg',
  '.ico',
  '.woff',
  '.woff2',
  '.ttf'
];

// Install event - precache static resources
self.addEventListener('install', event => {
  console.log('[Service Worker] Installing Service Worker');
  
  // Skip waiting to activate immediately
  self.skipWaiting();
  
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      console.log('[Service Worker] Pre-caching offline resources');
      return cache.addAll(PRECACHE_RESOURCES);
    })
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', event => {
  console.log('[Service Worker] Activating Service Worker');
  
  // Clean up old caches
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== CACHE_NAME) {
            console.log('[Service Worker] Removing old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => {
      console.log('[Service Worker] Service Worker activated');
      // Claim clients to take control immediately
      return self.clients.claim();
    })
  );
});

// Fetch event - serve from cache or network, fallback to offline page
self.addEventListener('fetch', event => {
  // Skip non-GET requests
  if (event.request.method !== 'GET') return;
  
  // Skip browser extension requests and other non-http requests
  if (!event.request.url.startsWith('http')) return;
  
  // Handle API requests differently - network first, then cache
  if (event.request.url.includes('/api/')) {
    handleApiRequest(event);
    return;
  }
  
  // For static assets, use cache-first strategy
  const url = new URL(event.request.url);
  const extension = url.pathname.substring(url.pathname.lastIndexOf('.'));
  
  if (DYNAMIC_CACHE_EXTENSIONS.includes(extension)) {
    handleStaticAsset(event);
    return;
  }
  
  // For HTML pages, use network-first strategy
  handlePageRequest(event);
});

/**
 * Handle API requests with a network-first strategy
 */
function handleApiRequest(event) {
  event.respondWith(
    fetch(event.request)
      .then(response => {
        // Only cache successful responses
        if (!response || response.status !== 200) {
          return response;
        }
        
        // Clone the response to store in cache and return the original
        const responseToCache = response.clone();
        caches.open(CACHE_NAME).then(cache => {
          cache.put(event.request, responseToCache);
        });
        
        return response;
      })
      .catch(err => {
        console.log('[Service Worker] API fetch failed, trying cache', err);
        return caches.match(event.request)
          .then(cachedResponse => {
            if (cachedResponse) {
              // Add a custom header to indicate this is cached data
              const headers = new Headers(cachedResponse.headers);
              headers.append('X-N1O1-Cached', 'true');
              
              return new Response(cachedResponse.body, {
                status: cachedResponse.status,
                statusText: cachedResponse.statusText,
                headers: headers
              });
            }
            
            // If API data is not in cache and we're offline,
            // return a JSON response with error info
            return new Response(JSON.stringify({
              error: 'offline',
              message: 'You are currently offline and this data is not available locally'
            }), {
              status: 503,
              statusText: 'Service Unavailable',
              headers: {
                'Content-Type': 'application/json',
                'X-N1O1-Offline': 'true'
              }
            });
          });
      })
  );
}

/**
 * Handle static asset requests with a cache-first strategy
 */
function handleStaticAsset(event) {
  event.respondWith(
    caches.match(event.request)
      .then(cachedResponse => {
        if (cachedResponse) {
          return cachedResponse;
        }
        
        // If not in cache, fetch from network and cache
        return fetch(event.request)
          .then(response => {
            // Only cache successful responses
            if (!response || response.status !== 200) {
              return response;
            }
            
            // Clone the response to store in cache and return the original
            const responseToCache = response.clone();
            caches.open(CACHE_NAME).then(cache => {
              cache.put(event.request, responseToCache);
            });
            
            return response;
          })
          .catch(err => {
            console.log('[Service Worker] Static asset fetch failed', err);
            // For failed static assets, we don't have a good fallback
            // Just let the error propagate
          });
      })
  );
}

/**
 * Handle page requests with a network-first strategy and offline fallback
 */
function handlePageRequest(event) {
  event.respondWith(
    fetch(event.request)
      .then(response => {
        // Cache the latest version of the page
        const responseToCache = response.clone();
        caches.open(CACHE_NAME).then(cache => {
          cache.put(event.request, responseToCache);
        });
        
        return response;
      })
      .catch(err => {
        console.log('[Service Worker] Page fetch failed, trying cache', err);
        
        return caches.match(event.request)
          .then(cachedResponse => {
            // Return cached page if available
            if (cachedResponse) {
              return cachedResponse;
            }
            
            // If not in cache, redirect to offline page
            return caches.match('/offline')
              .then(offlineResponse => {
                return offlineResponse || Response.error();
              });
          });
      })
  );
}

/**
 * Listen for push notifications
 */
self.addEventListener('push', event => {
  console.log('[Service Worker] Push received:', event);
  
  let notificationData = {};
  
  if (event.data) {
    try {
      notificationData = event.data.json();
    } catch (e) {
      notificationData = {
        title: 'N1O1 Clinical Trials',
        body: event.data.text(),
        icon: '/static/images/n1o1-favicon.svg'
      };
    }
  } else {
    notificationData = {
      title: 'N1O1 Clinical Trials',
      body: 'New update available',
      icon: '/static/images/n1o1-favicon.svg'
    };
  }
  
  const title = notificationData.title || 'N1O1 Clinical Trials';
  const options = {
    body: notificationData.body || 'You have a new notification',
    icon: notificationData.icon || '/static/images/n1o1-favicon.svg',
    badge: '/static/images/n1o1-favicon.svg',
    data: notificationData.data || {},
    actions: notificationData.actions || [],
    vibrate: [100, 50, 100]
  };
  
  event.waitUntil(
    self.registration.showNotification(title, options)
  );
});

/**
 * Handle notification clicks
 */
self.addEventListener('notificationclick', event => {
  console.log('[Service Worker] Notification click received:', event);
  
  event.notification.close();
  
  // Get action and data from notification
  const action = event.action;
  const data = event.notification.data;
  
  // Default URL to open
  let url = '/';
  
  // If the notification has a specific URL, use that
  if (data && data.url) {
    url = data.url;
  }
  
  // Handle specific actions
  if (action === 'view_details' && data && data.detailsUrl) {
    url = data.detailsUrl;
  }
  
  // Open or focus the appropriate window
  event.waitUntil(
    clients.matchAll({
      type: 'window',
      includeUncontrolled: true
    })
    .then(windowClients => {
      // Check if a window is already open
      for (let client of windowClients) {
        if (client.url.includes(url) && 'focus' in client) {
          return client.focus();
        }
      }
      
      // If no window is open, open a new one
      if (clients.openWindow) {
        return clients.openWindow(url);
      }
    })
  );
});

/**
 * Handle background sync
 */
self.addEventListener('sync', event => {
  console.log('[Service Worker] Background Sync triggered:', event);
  
  if (event.tag === 'sync-data') {
    event.waitUntil(
      syncPendingData()
    );
  }
});

/**
 * Sync pending data stored in IndexedDB
 */
async function syncPendingData() {
  // This is just a skeleton - the actual sync logic would be implemented
  // in the sync-manager.js file which interacts with the service worker
  
  console.log('[Service Worker] Starting data sync process');
  
  try {
    // Notify clients about sync start
    const clients = await self.clients.matchAll();
    clients.forEach(client => {
      client.postMessage({
        type: 'sync_status',
        status: 'in_progress',
        message: 'Starting data synchronization'
      });
    });
    
    // Sync process would happen here, managed by the main application
    
    // Notify clients about sync completion
    clients.forEach(client => {
      client.postMessage({
        type: 'sync_status',
        status: 'complete',
        message: 'Data synchronized successfully'
      });
    });
    
    return true;
  } catch (error) {
    console.error('[Service Worker] Sync error:', error);
    
    // Notify clients about sync failure
    const clients = await self.clients.matchAll();
    clients.forEach(client => {
      client.postMessage({
        type: 'sync_status',
        status: 'error',
        message: 'Synchronization failed',
        error: error.message
      });
    });
    
    return false;
  }
}