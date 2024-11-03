const CacheKey = "v1";

const initCache = () => {
  return caches.open(CacheKey).then(
    (cache) => {
      return cache.addAll([
        "/",
        "/static/css/SPA.min.css",
        "/static/js/scripts/SPA.js"
      ]);
    },
    (error) => {
      console.log(error);
    }
  );
};

const tryNetwork = (req, timeout) => {
  // console.log(req);
  return new Promise((resolve, reject) => {
    const timeoutId = setTimeout(reject, timeout);
    fetch(req).then((res) => {
      clearTimeout(timeoutId);
      const responseClone = res.clone();
      caches.open(CacheKey).then((cache) => {
        if (res.ok) {
          if (req.url.startsWith("http") && req.url.startsWith("https")) {
            if (req.method === "GET") {
              cache.put(req, responseClone);
            }
          }
        }
      }).catch((error) => {
        // console.log(error);
      });
      resolve(res);
      // Reject also if network fetch rejects.
    }, reject);
  });
};

const getFromCache = async (req) => {
  // console.log("network is off so getting from cache...");
  const cache = await caches.open(CacheKey);
  const result = await cache.match(req);
  return result || Promise.reject("no-match");
};

self.addEventListener("install", (e) => {
  // console.log("Installed");
  e.waitUntil(initCache());
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys().then((keyList) => {
      return Promise.all(
        keyList.map((key) => {
          if (key !== CacheKey) {
            return caches.delete(key);
          }
        })
      );
    })
  );
});

self.addEventListener("fetch", (e) => {
  // console.log("Try network and store result or get data from cache");
  // Try network and if it fails, go for the cached copy.
  e.respondWith(
    tryNetwork(e.request, 300).catch(() => getFromCache(e.request))
  );
});
