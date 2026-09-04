/* 生活流水账 Service Worker
 *
 * BUILD 由 build.py 自动写入（index.html 的内容哈希）。内容一变缓存名就变，
 * 旧缓存在 activate 时清掉——所以不需要手工维护版本号，也就忘不掉。
 * 这是缓存优先策略最经典的翻车点：忘了改版本号，用户会永远停在旧版本上。
 */
const BUILD = "b43080471531";
const CACHE = "daily-tracker-" + BUILD;

const SHELL = [
  "./", "./index.html", "./manifest.json",
  "./icon-180.png", "./icon-192.png", "./icon-512.png"
];

/* 字体来自 Google Fonts。不缓存的话，离线时会退回系统字体，样子和在线不一样。
   运行时缓存一次之后，离线和在线长得完全一致。 */
const FONT_HOSTS = ["https://fonts.googleapis.com", "https://fonts.gstatic.com"];

self.addEventListener("install", function(e){
  e.waitUntil(
    caches.open(CACHE)
      .then(function(c){ return c.addAll(SHELL); })
      .then(function(){ return self.skipWaiting(); })
  );
});

self.addEventListener("activate", function(e){
  e.waitUntil(
    caches.keys()
      .then(function(keys){
        return Promise.all(keys.filter(function(k){ return k !== CACHE; })
                               .map(function(k){ return caches.delete(k); }));
      })
      .then(function(){ return self.clients.claim(); })
  );
});

self.addEventListener("fetch", function(e){
  var req = e.request;
  if(req.method !== "GET") return;

  var url = new URL(req.url);
  var isFont = FONT_HOSTS.indexOf(url.origin) >= 0;
  if(url.origin !== self.location.origin && !isFont) return;

  e.respondWith(
    caches.match(req).then(function(hit){
      if(hit) return hit;
      return fetch(req).then(function(res){
        if(isFont && (res.ok || res.type === "opaque")){
          var copy = res.clone();
          caches.open(CACHE).then(function(c){ c.put(req, copy); });
        }
        return res;
      })["catch"](function(){
        /* 离线且没缓存：导航请求退回应用外壳，其余放弃 */
        if(req.mode === "navigate") return caches.match("./index.html");
        return Response.error();
      });
    })
  );
});
