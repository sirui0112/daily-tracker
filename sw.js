/* 生活流水账 Service Worker
 *
 * BUILD 由 build.py 自动写入（index.html 的内容哈希）。内容一变缓存名就变，
 * 旧缓存在 activate 时清掉——所以不需要手工维护版本号，也就忘不掉。
 * 这是缓存优先策略最经典的翻车点：忘了改版本号，用户会永远停在旧版本上。
 */
const BUILD = "819197dc09c7";
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

/* 页面本体走网络优先。缓存优先会让你在联网时仍然看到旧版本、必须刷两次才更新——
   HTML 才 70KB，为这点速度换来"改了却看不到"的困惑不值得。
   断网时自动退回缓存，离线可用不受影响。 */
function networkFirst(req){
  var timeout = new Promise(function(res){ setTimeout(function(){ res(null); }, 3500); });
  var net = fetch(req).then(function(r){
    var copy = r.clone();
    caches.open(CACHE).then(function(c){ c.put(req, copy); });
    return r;
  })["catch"](function(){ return null; });
  return Promise.race([net, timeout]).then(function(r){
    if(r) return r;
    return caches.match(req).then(function(hit){ return hit || caches.match("./index.html"); });
  });
}

function cacheFirst(req, isFont){
  return caches.match(req).then(function(hit){
    if(hit) return hit;
    return fetch(req).then(function(res){
      if(isFont && (res.ok || res.type === "opaque")){
        var copy = res.clone();
        caches.open(CACHE).then(function(c){ c.put(req, copy); });
      }
      return res;
    })["catch"](function(){ return Response.error(); });
  });
}

self.addEventListener("fetch", function(e){
  var req = e.request;
  if(req.method !== "GET") return;

  var url = new URL(req.url);
  var isFont = FONT_HOSTS.indexOf(url.origin) >= 0;
  if(url.origin !== self.location.origin && !isFont) return;

  if(req.mode === "navigate" || url.pathname.slice(-5) === ".html"){
    e.respondWith(networkFirst(req));      /* 页面：最新优先 */
  } else {
    e.respondWith(cacheFirst(req, isFont)); /* 图标和字体：缓存优先，它们几乎不变 */
  }
});
