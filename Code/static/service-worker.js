const CACHE_NAME = "stylesurfer-cache-v1";
const urlsToCache = [
  "/", // your homepage
  "/static/icons/icon-512x512.png", // icon
  "/static/css/style.css", // your CSS file(s)
  "/static/js/main.js",   // your JS file(s)
  // add more static assets if needed
];

// Install service worker and cache files
self.addEventListener("install", event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      return cache.addAll(urlsToCache);
    })
  );
});

// Activate service worker
self.addEventListener("activate", event => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames
          .filter(name => name !== CACHE_NAME)
          .map(name => caches.delete(name))
      );
    })
  );
});

// Fetch files from cache if offline
self.addEventListener("fetch", event => {
  event.respondWith(
    caches.match(event.request).then(response => {
      return response || fetch(event.request);
    })
  );
});
