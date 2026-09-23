(function () {
  // Mobile navigation
  var toggle = document.querySelector('.nav-toggle');
  var nav = document.getElementById('site-nav');
  if (toggle && nav) {
    toggle.addEventListener('click', function () {
      var open = nav.classList.toggle('open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  }

  // Dark / light theme toggle (remembers the choice per browser)
  var themeBtn = document.querySelector('.theme-toggle');
  if (themeBtn) {
    themeBtn.addEventListener('click', function () {
      var root = document.documentElement;
      var current = root.getAttribute('data-theme') ||
        (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
      var next = current === 'dark' ? 'light' : 'dark';
      root.setAttribute('data-theme', next);
      try { localStorage.setItem('theme', next); } catch (e) {}
    });
  }

  // Publication filtering
  var list = document.getElementById('pubs');
  if (!list) return;
  var search = document.getElementById('pub-search');
  var typeSel = document.getElementById('pub-type');
  var yearSel = document.getElementById('pub-year');
  var count = document.getElementById('pub-count');
  var empty = document.getElementById('pub-empty');
  var items = Array.prototype.slice.call(list.querySelectorAll('.pub'));
  var groups = Array.prototype.slice.call(list.querySelectorAll('.pub-group'));

  // Pre-select the type from the URL hash, e.g. /publications/#Journal%20Articles
  var hash = decodeURIComponent(location.hash.slice(1));
  if (hash) {
    for (var i = 0; i < typeSel.options.length; i++) {
      if (typeSel.options[i].value === hash) typeSel.value = hash;
    }
  }

  function apply() {
    var q = search.value.trim().toLowerCase();
    var t = typeSel.value;
    var y = yearSel.value;
    var shown = 0;
    items.forEach(function (el) {
      var ok = (!t || el.dataset.type === t) &&
               (!y || el.dataset.year === y) &&
               (!q || el.dataset.search.indexOf(q) !== -1);
      el.hidden = !ok;
      if (ok) shown++;
    });
    groups.forEach(function (g) {
      g.hidden = !g.querySelector('.pub:not([hidden])');
    });
    count.textContent = shown + (shown === 1 ? ' publication' : ' publications');
    empty.hidden = shown !== 0;
  }

  search.addEventListener('input', apply);
  typeSel.addEventListener('change', apply);
  yearSel.addEventListener('change', apply);
  apply();
})();
