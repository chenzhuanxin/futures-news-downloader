/* ==========================================================================
   期货品种资讯下载器 · 前端逻辑
   ========================================================================== */
const $ = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => Array.from(r.querySelectorAll(s));

const state = {
  exchanges: [],
  selected: new Set(),
  filter: 'all',
  q: '',
  mode: 'merge',
  src: 'em',
  jobTimer: null,
};

const SRC_NAME = { em: '东方财富', sina: '新浪财经', both: '东方财富 + 新浪财经' };

const CHECK_SVG = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6L9 17l-5-5"/></svg>';

/* ------------------------------------------------------------------ 初始化 */
async function init() {
  try {
    const r = await fetch('/api/varieties');
    const data = await r.json();
    state.exchanges = data.exchanges;
    $('#statTotal').textContent = data.total;
    renderDates(data.dates);
    renderVarieties();
  } catch (e) {
    $('#varietyArea').innerHTML = '<div class="loading">加载失败：' + e.message + '</div>';
  }
  bindEvents();
}

function renderDates(dates) {
  const names = ['今天', '昨天', '前天'];
  $('#dateRow').innerHTML = dates.map((d, i) =>
    `<div class="dchip ${i === 0 ? 'today' : ''}">
       <span class="dot"></span>${names[i] || ''} <b>${d}</b>
     </div>`).join('');
  $('#statDays').textContent = dates.length;
}

/* ------------------------------------------------------------------ 渲染 */
function renderVarieties() {
  const area = $('#varietyArea');
  const q = state.q.trim().toLowerCase();
  let html = '';
  let shown = 0;

  state.exchanges.forEach(ex => {
    const items = ex.items.filter(v => {
      if (state.filter === 'night' && !v.night) return false;
      if (state.filter === 'new' && !v.isNew) return false;
      if (q && !(v.name.toLowerCase().includes(q) ||
                 v.code.toLowerCase().includes(q) ||
                 (v.py || '').toLowerCase().includes(q))) return false;
      return true;
    });
    if (!items.length) return;
    shown += items.length;

    html += `<div class="exch">
      <div class="exch-head">
        <span class="edot" style="background:${ex.color}"></span>
        <h3>${ex.name}</h3>
        <span class="ecode">${ex.en}</span>
        <span class="ecount">共 <b>${items.length}</b> 个品种</span>
      </div>
      <div class="vgrid">`;
    items.forEach(v => {
      const on = state.selected.has(v.code) ? 'on' : '';
      const flags = `${v.night ? '<span class="flag night">夜</span>' : ''}` +
                    `${v.isNew ? '<span class="flag new">新</span>' : ''}`;
      html += `<div class="vitem ${on}" data-code="${v.code}" data-ex="${v.ex}">
        <span class="cb">${CHECK_SVG}</span>
        <span class="vname">${v.name}</span>
        <span class="vcode">${v.code}</span>
        ${flags ? `<span class="flags">${flags}</span>` : ''}
      </div>`;
    });
    html += '</div></div>';
  });

  area.innerHTML = shown ? html : '<div class="loading">没有匹配的品种</div>';
  $$('.vitem', area).forEach(el => el.onclick = () => toggle(el.dataset.code));
  updateSelUI();
}

function toggle(code) {
  if (state.selected.has(code)) state.selected.delete(code);
  else state.selected.add(code);
  const el = $(`.vitem[data-code="${code}"]`);
  if (el) el.classList.toggle('on', state.selected.has(code));
  updateSelUI();
}

function updateSelUI() {
  const n = state.selected.size;
  $('#selCount').textContent = n;
  $('#statSel').textContent = n;
}

/* ------------------------------------------------------------------ 事件 */
function bindEvents() {
  $('#q').addEventListener('input', e => {
    state.q = e.target.value;
    $('#clr').style.display = state.q ? 'grid' : 'none';
    renderVarieties();
  });
  $('#clr').onclick = () => {
    $('#q').value = ''; state.q = ''; $('#clr').style.display = 'none';
    renderVarieties();
  };

  $$('#filterSeg button').forEach(b => b.onclick = () => {
    $$('#filterSeg button').forEach(x => x.classList.remove('on'));
    b.classList.add('on'); state.filter = b.dataset.f; renderVarieties();
  });

  $$('#modeSeg button').forEach(b => b.onclick = () => {
    $$('#modeSeg button').forEach(x => x.classList.remove('on'));
    b.classList.add('on'); state.mode = b.dataset.m;
  });

  $$('#srcSeg button').forEach(b => b.onclick = () => {
    $$('#srcSeg button').forEach(x => x.classList.remove('on'));
    b.classList.add('on'); state.src = b.dataset.s;
  });

  $('#btnAll').onclick = () => { visibleCodes().forEach(c => state.selected.add(c)); renderVarieties(); };
  $('#btnNone').onclick = () => { state.selected.clear(); renderVarieties(); };
  $('#btnNight').onclick = () => { state.selected.clear(); allItems().filter(v => v.night).forEach(v => state.selected.add(v.code)); renderVarieties(); };
  $('#btnMetal').onclick = () => { pick(['有色金属', '贵金属', '黑色金属', '新能源金属']); };
  $('#btnAgri').onclick = () => { pick(['农产品', '油脂油料', '软商品']); };

  $('#btnPreview').onclick = doPreview;
  $('#btnExport').onclick = doExport;
  $('#resPanel').addEventListener('click', e => {
    const a = e.target.closest('[data-act]');
    if (!a) return;
    if (a.dataset.act === 'folder') openFolder(a.dataset.job);
  });
  $('#pvPanel').addEventListener('click', e => {
    const h = e.target.closest('.pv-h');
    if (h) h.parentElement.classList.toggle('open');
  });
}

function pick(groups) {
  state.selected.clear();
  allItems().filter(v => groups.includes(v.group)).forEach(v => state.selected.add(v.code));
  renderVarieties();
}

function allItems() {
  return state.exchanges.flatMap(ex => ex.items);
}
function visibleCodes() {
  const q = state.q.trim().toLowerCase();
  return allItems().filter(v => {
    if (state.filter === 'night' && !v.night) return false;
    if (state.filter === 'new' && !v.isNew) return false;
    if (q && !(v.name.toLowerCase().includes(q) || v.code.toLowerCase().includes(q))) return false;
    return true;
  }).map(v => v.code);
}

function codesPayload() {
  return state.selected.size ? Array.from(state.selected) : ['*'];
}

/* ------------------------------------------------------------------ 预览 */
async function doPreview() {
  const btn = $('#btnPreview');
  btn.disabled = true; btn.textContent = '预览中…';
  const panel = $('#pvPanel');
  panel.style.display = 'block';
  panel.innerHTML = '<div class="loading">正在检索资讯，请稍候…</div>';
  panel.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  try {
    const r = await fetch('/api/preview', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ codes: codesPayload(), days: 3, src: state.src })
    });
    const data = await r.json();
    renderPreview(data);
  } catch (e) {
    panel.innerHTML = `<div class="res-head"><div class="res-ico err"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 8v5M12 16h.01"/><circle cx="12" cy="12" r="9"/></svg></div><div><h3>预览失败</h3><p>${e.message}</p></div></div>`;
  }
  btn.disabled = false; btn.textContent = '预览资讯';
}

function renderPreview(data) {
  const withNews = data.varieties.filter(v => v.count > 0);
  const empty = data.varieties.filter(v => v.count === 0);
  let html = `<div class="res-head">
    <div class="res-ico ok"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 5h16v14H4z"/><path d="M8 9h8M8 13h5"/></svg></div>
    <div><h3>资讯预览</h3>
    <p>日期范围 ${data.dates[data.dates.length-1]} ~ ${data.dates[0]} ·
       来源 ${SRC_NAME[data.src] || '东方财富'} ·
       ${data.variety_count} 个品种，共 <b style="color:var(--brand)">${data.total_count}</b> 条资讯</p></div>
  </div>`;

  if (!data.total_count) {
    html += '<div class="pv-empty">所选品种在最近三天暂无可用资讯，可稍后再试或更换品种。</div>';
  } else {
    withNews.forEach(v => {
      html += `<div class="pv-item open">
        <div class="pv-h">
          <span class="pv-name">${esc(v.name)}</span>
          <span class="vcode">${v.code}</span>
          <span class="pv-cnt">${v.count} 条</span>
        </div>
        <div class="pv-list">`;
      v.items.forEach(it => {
        html += `<div class="pv-art">
          <span class="d">${esc((it.date || '').slice(5, 16))}</span>
          <a href="${it.url}" target="_blank" rel="noopener">${esc(it.title)}</a>
          <span class="s">${esc(it.src_label ? it.src_label + ' · ' : '')}${esc(it.source || '')}</span>
        </div>`;
      });
      if (v.count > v.items.length)
        html += `<div class="pv-art" style="color:var(--text-3)">… 其余 ${v.count - v.items.length} 条将在导出的 Word 中呈现</div>`;
      html += '</div></div>';
    });
  }
  if (empty.length) {
    html += `<div class="per-variety" style="margin-top:14px">
      <span class="pv-tag" style="opacity:.75">以下 ${empty.length} 个品种近三日无资讯：</span>` +
      empty.map(v => `<span class="pv-tag">${v.name}</span>`).join('') + '</div>';
  }
  $('#pvPanel').innerHTML = html;
}

/* ------------------------------------------------------------------ 导出 */
async function doExport() {
  const btn = $('#btnExport');
  btn.disabled = true; btn.textContent = '正在生成…';
  $('#resPanel').style.display = 'none';
  const panel = $('#progPanel');
  panel.style.display = 'block';
  panel.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  setProgress(0, '正在创建任务…');

  try {
    const r = await fetch('/api/export', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        codes: codesPayload(),
        days: 3,
        mode: state.mode,
        src: state.src,
        max_items: parseInt($('#maxItems').value, 10),
        save_images: $('#saveImg').checked,
      })
    });
    const { job_id } = await r.json();
    pollJob(job_id);
  } catch (e) {
    setProgress(0, '创建任务失败：' + e.message);
    btn.disabled = false; btn.textContent = '生成并下载 Word';
  }
}

function setProgress(pct, msg) {
  $('#progBar').style.width = Math.max(0, Math.min(100, pct)) + '%';
  $('#progPct').textContent = Math.round(pct) + '%';
  if (msg !== undefined) $('#progMsg').textContent = msg;
}

function pollJob(jobId) {
  clearInterval(state.jobTimer);
  state.jobTimer = setInterval(async () => {
    try {
      const r = await fetch('/api/progress/' + jobId);
      if (!r.ok) throw new Error('任务不存在');
      const job = await r.json();
      const pct = job.total ? (job.progress / job.total) * 100 : 0;
      setProgress(pct, job.message || '');

      if (job.status === 'done') {
        clearInterval(state.jobTimer);
        setProgress(100, '完成');
        showResult(jobId, job);
        $('#btnExport').disabled = false;
        $('#btnExport').textContent = '生成并下载 Word';
      } else if (job.status === 'error') {
        clearInterval(state.jobTimer);
        showError(job.error || '未知错误');
        $('#btnExport').disabled = false;
        $('#btnExport').textContent = '生成并下载 Word';
      }
    } catch (e) {
      clearInterval(state.jobTimer);
      showError(e.message);
      $('#btnExport').disabled = false; $('#btnExport').textContent = '生成并下载 Word';
    }
  }, 700);
}

function showResult(jobId, job) {
  const s = job.result || {};
  const panel = $('#resPanel');
  panel.style.display = 'block';
  const isZip = (job.download_name || '').endsWith('.zip');
  panel.innerHTML = `
    <div class="res-head">
      <div class="res-ico ok"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6L9 17l-5-5"/></svg></div>
      <div><h3>生成完成</h3>
      <p>${isZip ? '已按品种分别生成 Word 并打包' : '已合并生成 Word 文档'} ·
         来源 ${esc(s.src_label || SRC_NAME[s.src] || '东方财富')} ·
         文件大小 ${fmtSize(job.size || 0)}</p></div>
    </div>
    <div class="res-stats">
      <div class="rstat"><b>${s.variety_count || 0}</b><span>品种</span></div>
      <div class="rstat"><b>${s.article_count || 0}</b><span>条资讯</span></div>
      <div class="rstat"><b>${s.image_count || 0}</b><span>张图片</span></div>
      <div class="rstat"><b>3</b><span>天范围</span></div>
    </div>
    <div class="res-actions">
      <button class="btn primary" onclick="location.href='/api/download/${jobId}'">
        ⬇ 下载 ${esc(job.download_name || '文件')}</button>
      <button class="btn ghost" data-act="folder" data-job="${jobId}">📂 打开所在文件夹</button>
    </div>
    <div class="per-variety">
      ${(s.per_variety || []).map(v => `<span class="pv-tag">${v.name} <b>${v.count}</b></span>`).join('')}
    </div>
    <div style="margin-top:12px;font-size:12px;color:var(--text-3)">
      保存位置：<span style="font-family:var(--mono)">${esc(s.dir || '')}</span>
      <br>提示：原文配图已直接插入每条资讯的正文中，不再单独输出 images 文件夹。
    </div>`;
  panel.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function showError(msg) {
  const panel = $('#resPanel');
  panel.style.display = 'block';
  panel.innerHTML = `<div class="res-head">
    <div class="res-ico err"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M12 8v5M12 16h.01"/><circle cx="12" cy="12" r="9"/></svg></div>
    <div><h3>生成失败</h3><p>${esc(msg)}</p></div></div>`;
}

async function openFolder(jobId) {
  try {
    const r = await fetch('/api/open_folder/' + jobId, { method: 'POST' });
    const d = await r.json();
    toast(d.ok ? '已打开文件夹' : ('请手动打开：' + d.dir));
  } catch (e) { toast('打开失败'); }
}

/* ------------------------------------------------------------------ 工具 */
function esc(s) {
  return String(s == null ? '' : s)
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}
function fmtSize(n) {
  if (n > 1048576) return (n / 1048576).toFixed(2) + ' MB';
  if (n > 1024) return (n / 1024).toFixed(0) + ' KB';
  return n + ' B';
}
let toastTimer;
function toast(msg) {
  const t = $('#toast');
  t.textContent = msg; t.classList.add('show');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => t.classList.remove('show'), 2600);
}

init();
