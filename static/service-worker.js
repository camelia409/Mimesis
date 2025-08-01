const CACHE_NAME = 'mimesis-v1.2';
const urlsToCache = [
    '/',
    '/static/css/styles.css',
    '/static/js/scripts.js',
    '/static/manifest.json',
    '/templates/base.html',
    '/templates/index.html',
    '/templates/results.html',
    '/templates/profile.html',
    '/templates/analytics.html',
    '/templates/popular.html'
];

// Install event - cache resources
self.addEventListener('install', (event) => {
    console.log('Service Worker: Installing...');
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then((cache) => {
                console.log('Service Worker: Caching files');
                return cache.addAll(urlsToCache);
            })
            .then(() => {
                console.log('Service Worker: Files cached successfully');
                return self.skipWaiting();
            })
            .catch((error) => {
                console.error('Service Worker: Error caching files', error);
            })
    );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
    console.log('Service Worker: Activating...');
    event.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames.map((cacheName) => {
                    if (cacheName !== CACHE_NAME) {
                        console.log('Service Worker: Deleting old cache', cacheName);
                        return caches.delete(cacheName);
                    }
                })
            );
        }).then(() => {
            console.log('Service Worker: Activated successfully');
            return self.clients.claim();
        })
    );
});

// Fetch event - serve from cache or network
self.addEventListener('fetch', (event) => {
    // Skip non-GET requests
    if (event.request.method !== 'GET') {
        return;
    }

    // Skip API calls and external resources
    if (event.request.url.includes('/api/') || 
        event.request.url.includes('googleapis.com') ||
        event.request.url.includes('gstatic.com') ||
        event.request.url.includes('cdn.jsdelivr.net')) {
        return;
    }

    event.respondWith(
        caches.match(event.request)
            .then((response) => {
                // Return cached version or fetch from network
                if (response) {
                    console.log('Service Worker: Serving from cache', event.request.url);
                    return response;
                }

                console.log('Service Worker: Fetching from network', event.request.url);
                return fetch(event.request)
                    .then((response) => {
                        // Check if we received a valid response
                        if (!response || response.status !== 200 || response.type !== 'basic') {
                            return response;
                        }

                        // Clone the response
                        const responseToCache = response.clone();

                        // Cache the fetched resource
                        caches.open(CACHE_NAME)
                            .then((cache) => {
                                cache.put(event.request, responseToCache);
                            });

                        return response;
                    })
                    .catch(() => {
                        // Return offline page for navigation requests
                        if (event.request.destination === 'document') {
                            return caches.match('/templates/index.html');
                        }
                    });
            })
    );
});

// Background sync for offline actions
self.addEventListener('sync', (event) => {
    if (event.tag === 'background-sync') {
        console.log('Service Worker: Background sync triggered');
        event.waitUntil(doBackgroundSync());
    }
});

function doBackgroundSync() {
    // Handle any pending offline actions
    console.log('Service Worker: Processing background sync');
    return Promise.resolve();
}

// Push notification handling
self.addEventListener('push', (event) => {
    console.log('Service Worker: Push notification received');
    
    const options = {
        body: event.data ? event.data.text() : 'New style recommendation available!',
        icon: '/static/icon-192.png',
        badge: '/static/badge-72.png',
        vibrate: [100, 50, 100],
        data: {
            dateOfArrival: Date.now(),
            primaryKey: 1
        },
        actions: [
            {
                action: 'explore',
                title: 'Explore Styles',
                icon: '/static/icon-192.png'
            },
            {
                action: 'close',
                title: 'Close',
                icon: '/static/icon-192.png'
            }
        ]
    };

    event.waitUntil(
        self.registration.showNotification('Mimesis Style Update', options)
    );
});

// Notification click handling
self.addEventListener('notificationclick', (event) => {
    console.log('Service Worker: Notification clicked');
    
    event.notification.close();

    if (event.action === 'explore') {
        event.waitUntil(
            clients.openWindow('/')
        );
    }
}); 