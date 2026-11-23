/* Shared by every piece. Load it in <head>, after pieces.js and before the piece's own scripts.
   - Works out where the piece is running: the iPhone app, the Android app, or the website.
   - Adds a small "Collection" button that leads back to the collection.
   - Pauses all sound while the app is in the background, and brings it back afterwards.
   - On the website, paid pieces play a 60-second taste and then point to the apps.
   A piece can choose where the Collection button sits with <html data-home="tl|tc|tr|bl|br">. */
(function () {
  'use strict';
  var root = document.documentElement;
  var C = window.COLLECTION || {}, P = window.PIECES || [];
  var ios = !!(window.webkit && window.webkit.messageHandlers && window.webkit.messageHandlers.store);
  var android = !!window.StarSongAndroid;
  var app = ios || android;
  root.classList.add(app ? 'in-app' : 'on-web', ios ? 'ios' : android ? 'android' : 'web');

  var id = (location.pathname.match(/pieces\/([^\/]+)\//) || [])[1];
  var piece = P.filter(function (p) { return p.id === id; })[0];
  var taste = !app && piece && !piece.free;

  /* ---- keep track of every sound engine the piece makes ---- */
  var contexts = [], suspendedByUs = [], stopped = false, firstSound = null;
  var Native = window.AudioContext || window.webkitAudioContext;
  if (Native) {
    var Wrapped = function () {
      var c = new (Function.prototype.bind.apply(Native, [null].concat([].slice.call(arguments))))();
      contexts.push(c);
      if (stopped) silence(c);
      if (firstSound) { var f = firstSound; firstSound = null; f(); }
      return c;
    };
    Wrapped.prototype = Native.prototype;
    try { Object.setPrototypeOf(Wrapped, Native); } catch (e) {}
    window.AudioContext = Wrapped;
    if (window.webkitAudioContext) window.webkitAudioContext = Wrapped;
  }
  function silence(c) {
    try { c.suspend(); } catch (e) {}
    c.resume = function () { return Promise.resolve(); };
  }

  /* ---- background / foreground ---- */
  function setHidden(hidden) {
    if (stopped) return;
    if (hidden) {
      suspendedByUs = contexts.filter(function (c) { return c.state === 'running'; });
      suspendedByUs.forEach(function (c) { try { c.suspend(); } catch (e) {} });
    } else {
      suspendedByUs.forEach(function (c) { try { c.resume(); } catch (e) {} });
      suspendedByUs = [];
    }
  }
  window.__ssHidden = setHidden;              /* the Android app calls this */
  document.addEventListener('visibilitychange', function () { setHidden(document.hidden); });

  /* ---- buttons and the taste overlay ---- */
  var css =
    '.ss-home{position:fixed;z-index:2147483000;font:12px/1 "Cinzel","Times New Roman",serif;letter-spacing:.16em;text-transform:uppercase;' +
    'color:#f3ead2;background:rgba(6,10,24,.62);border:1px solid rgba(243,234,210,.35);border-radius:999px;padding:9px 14px 9px 11px;min-height:36px;' +
    '-webkit-backdrop-filter:blur(8px);backdrop-filter:blur(8px);-webkit-tap-highlight-color:transparent;cursor:pointer;transition:opacity 1s}' +
    '.ss-home:active{border-color:#f3ead2}' +
    'html[data-home=tl] .ss-home,html:not([data-home]) .ss-home{left:calc(12px + env(safe-area-inset-left,0px));top:calc(var(--ss-top,12px) + env(safe-area-inset-top,0px))}' +
    'html[data-home=tc] .ss-home{left:50%;transform:translateX(-50%);top:calc(var(--ss-top,10px) + env(safe-area-inset-top,0px))}' +
    'html[data-home=tr] .ss-home{right:calc(12px + env(safe-area-inset-right,0px));top:calc(var(--ss-top,12px) + env(safe-area-inset-top,0px))}' +
    'html[data-home=bl] .ss-home{left:calc(12px + env(safe-area-inset-left,0px));bottom:calc(12px + env(safe-area-inset-bottom,0px))}' +
    'html[data-home=br] .ss-home{right:calc(12px + env(safe-area-inset-right,0px));bottom:calc(12px + env(safe-area-inset-bottom,0px))}' +
    'body.idle .ss-home,body.ss-quiet .ss-home{opacity:0;pointer-events:none}' +
    '.ss-taste{position:fixed;z-index:2147483000;right:calc(12px + env(safe-area-inset-right,0px));top:calc(12px + env(safe-area-inset-top,0px));' +
    'font:11px/1 ui-monospace,Menlo,monospace;letter-spacing:.08em;color:#f3ead2;background:rgba(6,10,24,.62);border-radius:999px;padding:7px 10px;pointer-events:none}' +
    'html[data-home=tr] .ss-taste{top:calc(56px + env(safe-area-inset-top,0px))}' +
    '.ss-end{position:fixed;inset:0;z-index:2147483001;display:flex;align-items:center;justify-content:center;padding:24px;background:rgba(4,7,18,.78);' +
    '-webkit-backdrop-filter:blur(10px);backdrop-filter:blur(10px);opacity:0;transition:opacity 1.6s;color:#f3ead2;text-align:center;font:18px/1.45 "Cormorant Garamond",Georgia,serif}' +
    '.ss-end.on{opacity:1}' +
    '.ss-end h2{font:400 clamp(20px,4vw,28px)/1.2 "Cinzel","Times New Roman",serif;letter-spacing:.18em;text-transform:uppercase;color:#e3c170;margin:0 0 10px}' +
    '.ss-end p{margin:0 auto 18px;max-width:420px;font-style:italic}' +
    '.ss-end .row{display:flex;flex-wrap:wrap;gap:10px;justify-content:center}' +
    '.ss-end a,.ss-end button{font:500 16px/1 "Cormorant Garamond",Georgia,serif;color:#060d22;background:#e3c170;border:1px solid #e3c170;border-radius:2px;padding:12px 18px;text-decoration:none;cursor:pointer}' +
    '.ss-end .ghost{background:transparent;color:#f3ead2;border-color:rgba(243,234,210,.5)}';

  function el(tag, cls, text) { var e = document.createElement(tag); if (cls) e.className = cls; if (text) e.textContent = text; return e; }
  function stopEvents(b) {
    ['pointerdown', 'pointerup', 'touchstart', 'touchend', 'mousedown', 'mouseup', 'click', 'dblclick'].forEach(function (t) {
      b.addEventListener(t, function (e) { e.stopPropagation(); });
    });
  }
  function goHome() { location.href = '../../index.html?home=1'; }

  function storeLinks(row) {
    var any = false;
    if (C.appStoreUrl) { var a = el('a', '', 'App Store'); a.href = C.appStoreUrl; a.target = '_blank'; a.rel = 'noopener'; row.appendChild(a); any = true; }
    if (C.playStoreUrl) { var g = el('a', '', 'Google Play'); g.href = C.playStoreUrl; g.target = '_blank'; g.rel = 'noopener'; row.appendChild(g); any = true; }
    return any;
  }

  function endTaste() {
    stopped = true;
    contexts.forEach(silence);
    var o = el('div', 'ss-end'); o.setAttribute('role', 'dialog'); o.setAttribute('aria-label', 'End of the preview');
    var box = el('div');
    box.appendChild(el('h2', '', piece.title));
    var row = el('div', 'row');
    var hasLinks = storeLinks(row);
    box.appendChild(el('p', '', hasLinks
      ? 'That was a one-minute taste. The full piece plays for as long as you like in the ' + (C.title || 'app') + ' app, with all the other pieces in the collection.'
      : 'That was a one-minute taste. The full piece is coming soon in the ' + (C.title || '') + ' app for iPhone and Android.'));
    var back = el('button', 'ghost', 'Back to the collection'); back.type = 'button'; back.onclick = goHome; row.appendChild(back);
    box.appendChild(row); o.appendChild(box); stopEvents(o);
    document.body.appendChild(o);
    requestAnimationFrame(function () { o.classList.add('on'); });
  }

  function startTasteClock(badge) {
    var left = 60;
    badge.textContent = 'Preview 1:00';
    var t = setInterval(function () {
      left--;
      badge.textContent = 'Preview 0:' + (left < 10 ? '0' : '') + left;
      if (left <= 0) { clearInterval(t); badge.remove(); endTaste(); }
    }, 1000);
  }

  function build() {
    var s = el('style'); s.textContent = css; document.head.appendChild(s);
    var b = el('button', 'ss-home', '‹ Collection'); b.type = 'button';
    b.setAttribute('aria-label', 'Back to the collection');
    stopEvents(b); b.addEventListener('click', goHome);
    document.body.appendChild(b);
    if (taste) {
      var badge = el('div', 'ss-taste', 'Preview · 1 min'); document.body.appendChild(badge);
      /* the minute starts when the piece first makes sound */
      if (contexts.length) startTasteClock(badge); else firstSound = function () { startTasteClock(badge); };
    }
  }
  if (document.body) build(); else document.addEventListener('DOMContentLoaded', build);
})();
