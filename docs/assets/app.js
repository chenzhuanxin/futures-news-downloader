/* 文档站脚本：目录高亮 + 平滑滚动 + 代码块复制 */
(function () {
  'use strict';

  // 1. 侧栏目录滚动高亮
  var toc = document.querySelector('.toc');
  if (toc) {
    var links = [].slice.call(toc.querySelectorAll('a[href^="#"]'));
    var targets = links.map(function (a) {
      return document.getElementById(a.getAttribute('href').slice(1));
    }).filter(Boolean);

    function spy() {
      var y = window.scrollY + 110;
      var cur = null;
      targets.forEach(function (t) {
        if (t.offsetTop <= y) cur = t.id;
      });
      links.forEach(function (a) {
        a.classList.toggle('on', a.getAttribute('href') === '#' + cur);
      });
    }
    var ticking = false;
    window.addEventListener('scroll', function () {
      if (!ticking) {
        ticking = true;
        requestAnimationFrame(function () { spy(); ticking = false; });
      }
    }, { passive: true });
    spy();
  }

  // 2. 代码块悬浮复制按钮
  [].slice.call(document.querySelectorAll('pre')).forEach(function (pre) {
    var btn = document.createElement('button');
    btn.textContent = '复制';
    btn.style.cssText = 'position:absolute;top:9px;right:10px;padding:4px 10px;' +
      'font-size:12px;border-radius:7px;border:1px solid #334155;background:#1e293b;' +
      'color:#cbd5e1;cursor:pointer;opacity:0;transition:.18s';
    pre.style.position = 'relative';
    pre.appendChild(btn);
    pre.addEventListener('mouseenter', function () { btn.style.opacity = '1'; });
    pre.addEventListener('mouseleave', function () { btn.style.opacity = '0'; });
    btn.addEventListener('click', function () {
      var code = pre.querySelector('code');
      var text = (code || pre).innerText;
      navigator.clipboard.writeText(text).then(function () {
        btn.textContent = '已复制 ✓';
        setTimeout(function () { btn.textContent = '复制'; }, 1400);
      });
    });
  });
})();
