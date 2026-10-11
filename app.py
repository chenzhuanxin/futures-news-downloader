# -*- coding: utf-8 -*-
"""
期货品种资讯下载器 · Flask 后端

功能：
  · 展示全部品种（来自公众号导航页）
  · 预览 / 批量下载（全部或单个品种）最近三天（今天/昨天/前天）的资讯
  · 数据源可选：东方财富 / 新浪财经 / 两者合并
  · 导出 Word（标题黑体三号加粗居中，正文仿宋三号两端对齐首行缩进2字符，
    原文配图按原文位置插入对应资讯正文中）

启动：python app.py   然后浏览器打开 http://127.0.0.1:8899
"""
import os
import re
import sys
import json
import time
import uuid
import shutil
import zipfile
import tempfile
import threading
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

from flask import Flask, jsonify, request, send_file, abort

from core import varieties as V
from core import sources
from core import docx_builder as DB


# --------------------------------------------------------------------------
# 路径处理：兼容「源码运行」与「PyInstaller 打包 exe」两种模式
#   · BUNDLE_DIR —— 静态资源所在目录（打包后为解压出来的临时目录）
#   · APP_DIR    —— 可写目录（输出 Word 放这里，打包后即 exe 所在目录）
# --------------------------------------------------------------------------
def _is_frozen():
    return getattr(sys, "frozen", False)


if _is_frozen():
    BUNDLE_DIR = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(sys.executable)))
    APP_DIR = os.path.dirname(os.path.abspath(sys.executable))
else:
    BUNDLE_DIR = os.path.dirname(os.path.abspath(__file__))
    APP_DIR = BUNDLE_DIR

STATIC_DIR = os.path.join(BUNDLE_DIR, "static")
OUTPUT_DIR = os.path.join(APP_DIR, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

app = Flask(__name__, static_folder=STATIC_DIR, static_url_path="/static")

JOBS = {}
JOBS_LOCK = threading.Lock()

SEARCH_WORKERS = 8
FETCH_WORKERS = 10

MAX_PARAS_PER_ART = 60      # 单篇最多保留段落（超出截断并标注）
MAX_IMGS_PER_ART = 12       # 单篇最多保留配图


# --------------------------------------------------------------------------
# 基础接口
# --------------------------------------------------------------------------
@app.route("/")
def index():
    return app.send_static_file("index.html")


@app.route("/api/varieties")
def api_varieties():
    ex = V.EXCHANGES
    groups = {}
    for v in V.VARIETIES:
        item = dict(v)
        item["ex_short"] = ex[v["ex"]]["short"]
        item["ex_name"] = ex[v["ex"]]["name"]
        item["ex_color"] = ex[v["ex"]]["color"]
        groups.setdefault(v["ex"], []).append(item)
    return jsonify({
        "exchanges": [{"key": k, **ex[k], "items": groups.get(k, [])}
                      for k in ex if k in groups],
        "total": len(V.VARIETIES),
        "dates": sources.get_date_window(3),
    })


def _resolve_varieties(codes):
    if not codes or codes == ["*"] or codes == "all":
        return list(V.VARIETIES)
    out = []
    for c in codes:
        v = V.get_variety(c)
        if v:
            ex = V.EXCHANGES[v["ex"]]
            vv = dict(v)
            vv["ex_name"] = ex["name"]
            vv["ex_short"] = ex["short"]
            out.append(vv)
    return out


# --------------------------------------------------------------------------
# 预览：只做搜索，快速返回每个品种在窗口期内的资讯条数
# --------------------------------------------------------------------------
@app.route("/api/preview", methods=["POST"])
def api_preview():
    data = request.get_json(force=True) or {}
    codes = data.get("codes") or ["*"]
    days = int(data.get("days", 3))
    src = data.get("src") or "em"
    dates = sources.get_date_window(days)
    vs = _resolve_varieties(codes)

    results = []

    def work(v):
        items = sources.fetch_variety_news(v, dates, max_items=60, src=src)
        return v, items

    with ThreadPoolExecutor(max_workers=SEARCH_WORKERS) as pool:
        futs = [pool.submit(work, v) for v in vs]
        for f in as_completed(futs):
            v, items = f.result()
            results.append({
                "code": v["code"], "name": v["name"],
                "ex_short": v.get("ex_short", ""),
                "count": len(items),
                "items": [{"title": it["title"], "date": it["date"],
                           "source": it["source"],
                           "src_label": sources.SRC_LABEL.get(it.get("src"), ""),
                           "url": it["url"]}
                          for it in items[:10]],
            })
    order = {v["code"]: i for i, v in enumerate(vs)}
    results.sort(key=lambda x: order.get(x["code"], 999))
    total = sum(r["count"] for r in results)
    return jsonify({"dates": dates, "varieties": results,
                    "total_count": total, "variety_count": len(results),
                    "src": src})


# --------------------------------------------------------------------------
# 导出：后台任务
# --------------------------------------------------------------------------
@app.route("/api/export", methods=["POST"])
def api_export():
    data = request.get_json(force=True) or {}
    codes = data.get("codes") or ["*"]
    days = int(data.get("days", 3))
    mode = data.get("mode", "merge")            # merge | split
    max_items = int(data.get("max_items", 15))
    save_images = bool(data.get("save_images", True))
    src = data.get("src") or "em"               # em | sina | both

    job_id = uuid.uuid4().hex[:12]
    with JOBS_LOCK:
        JOBS[job_id] = {"status": "pending", "progress": 0, "total": 1,
                        "message": "任务已创建", "file": None, "error": None,
                        "created": time.time(), "result": None}
    t = threading.Thread(target=_run_export, args=(job_id, codes, days, mode,
                                                   max_items, save_images, src),
                         daemon=True)
    t.start()
    return jsonify({"job_id": job_id})


def _set(job_id, **kw):
    with JOBS_LOCK:
        JOBS[job_id].update(kw)


def _run_export(job_id, codes, days, mode, max_items, save_images, src="em"):
    # 图片只作中转：下载到临时目录 -> 内嵌进 Word -> 删除，成品目录不放 images
    tmp_img_root = tempfile.mkdtemp(prefix="fnd_img_") if save_images else None
    try:
        dates = sources.get_date_window(days)
        vs = _resolve_varieties(codes)
        if not vs:
            _set(job_id, status="error", error="未选择任何品种")
            return

        src_label = sources.SRC_LABEL.get(src, "东方财富") if src != "both" else "东方财富 + 新浪财经"

        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        label = vs[0]["name"] if len(vs) == 1 else f"共{len(vs)}个品种"
        job_dir = os.path.join(OUTPUT_DIR, f"{ts}_{label}")
        os.makedirs(job_dir, exist_ok=True)
        img_root = tmp_img_root or os.path.join(tempfile.gettempdir(), "fnd_img_noop")

        # ---------- 阶段 1：检索 ----------
        _set(job_id, status="running", message="正在检索各品种资讯…",
             progress=0, total=len(vs) + 1)
        found = {}          # code -> [items]

        def search_one(v):
            return v, sources.fetch_variety_news(v, dates, max_items=max_items, src=src)

        done = 0
        with ThreadPoolExecutor(max_workers=SEARCH_WORKERS) as pool:
            futs = [pool.submit(search_one, v) for v in vs]
            for f in as_completed(futs):
                v, items = f.result()
                found[v["code"]] = items
                done += 1
                _set(job_id, progress=done,
                     message=f"已检索 {done}/{len(vs)} 个品种（{v['name']}：{len(items)} 条）")

        all_arts = [(v, it) for v in vs for it in found.get(v["code"], [])]
        total_arts = len(all_arts)

        # ---------- 阶段 2：抓正文 + 图片 ----------
        _set(job_id, message=f"共 {total_arts} 条资讯，正在抓取正文与图片…",
             progress=len(vs), total=len(vs) + total_arts + 2)

        image_map = {}      # url -> local filename
        art_cache = {}

        def fetch_one(v, it):
            art = sources.fetch_article(it["url"])
            art["date"] = it["date"] or art.get("date")
            art["source"] = art.get("source") or it.get("source")
            art["title"] = art.get("title") or it["title"]
            art["summary"] = it.get("summary", "")
            art["url"] = it["url"]
            art["src"] = it.get("src", "em")
            art["src_label"] = sources.SRC_LABEL.get(it.get("src"), "东方财富")
            # 超长正文截断（如每日宏观综述），避免文档失衡
            paras = art.get("paragraphs") or []
            if len(paras) > MAX_PARAS_PER_ART:
                art["paragraphs"] = paras[:MAX_PARAS_PER_ART] + \
                    [f"……（原文较长，此处节选前 {MAX_PARAS_PER_ART} 段，"
                     f"全文见来源链接）"]
            # 同步裁剪 blocks
            blocks = art.get("blocks") or []
            if blocks:
                kept, np_ = [], 0
                for b in blocks:
                    if b.get("type") == "p":
                        np_ += 1
                        if np_ > MAX_PARAS_PER_ART:
                            continue
                    kept.append(b)
                if np_ > MAX_PARAS_PER_ART:
                    kept.append({"type": "p",
                                 "text": f"……（原文较长，此处节选前 {MAX_PARAS_PER_ART} 段，"
                                         f"全文见来源链接）"})
                art["blocks"] = kept

            imgs_local = {}
            if save_images:
                for iu in art.get("images", [])[:MAX_IMGS_PER_ART]:
                    fn = sources.download_image(iu, img_root, referer=it["url"])
                    if fn:
                        imgs_local[iu] = fn
            art["_img_local"] = imgs_local
            return (v["code"], it["url"]), art

        d2 = 0
        with ThreadPoolExecutor(max_workers=FETCH_WORKERS) as pool:
            futs = [pool.submit(fetch_one, v, it) for v, it in all_arts]
            for f in as_completed(futs):
                key, art = f.result()
                art_cache[key] = art
                d2 += 1
                if d2 % 3 == 0 or d2 == total_arts:
                    _set(job_id, progress=len(vs) + d2,
                         message=f"已抓取正文 {d2}/{total_arts} 条…")
            for art in art_cache.values():
                image_map.update(art.get("_img_local", {}))

        # ---------- 阶段 3：生成 Word ----------
        _set(job_id, message="正在生成 Word 文档…",
             progress=len(vs) + total_arts, total=len(vs) + total_arts + 2)

        date_label = f"{dates[-1]}至{dates[0]}"
        produced = []
        img_count = 0

        def arts_of(v):
            out = []
            for it in found.get(v["code"], []):
                a = art_cache.get((v["code"], it["url"]))
                if a:
                    a = dict(a)
                    imgs = [iu for iu in a.get("images", []) if iu in image_map]
                    a["images"] = imgs
                    # blocks 里只保留成功下载的图
                    if a.get("blocks"):
                        a["blocks"] = [b for b in a["blocks"]
                                       if b.get("type") != "img" or b.get("url") in image_map]
                    out.append(a)
            return out

        if mode == "merge":
            title = f"期货品种资讯汇编（{date_label}）"
            if len(vs) == 1:
                title = f"{vs[0]['name']} 资讯汇编（{date_label}）"
            fname = f"期货品种资讯汇编_{dates[-1]}_{dates[0]}.docx"
            if len(vs) == 1:
                fname = f"{vs[0]['name']}_资讯汇编_{dates[-1]}_{dates[0]}.docx"
            fpath = os.path.join(job_dir, fname)

            doc = DB.setup_document()
            DB.add_title(doc, title)
            DB.add_meta(doc, f"资讯来源：{src_label}　|　日期范围：{date_label}　|　"
                             f"品种数：{len(vs)}　|　整理时间："
                             f"{datetime.now().strftime('%Y-%m-%d %H:%M')}")
            DB.add_body(doc, f"本文档由「期货品种资讯下载器」自动生成，汇编了 {date_label} "
                             f"期间共 {len(vs)} 个品种的 {total_arts} 条资讯。"
                             f"标题采用黑体三号加粗居中，正文采用仿宋三号两端对齐、"
                             f"首行缩进2字符，原文配图按原文位置插入对应资讯正文中。")
            for v in vs:
                DB.add_page_break(doc)
                DB.render_variety_section(doc, v, arts_of(v),
                                          img_dir=img_root, image_map=image_map)
            DB.add_credit(doc)
            doc.save(fpath)
            produced.append(fpath)
            result_file = fpath
            download_name = fname
        else:
            for v in vs:
                art_list = arts_of(v)
                title = f"{v['name']}（{v['code']}）资讯汇编（{date_label}）"
                fname = f"{v['name']}_{v['code']}_资讯_{dates[-1]}_{dates[0]}.docx"
                fpath = os.path.join(job_dir, fname)
                doc = DB.setup_document()
                DB.add_title(doc, title)
                DB.add_meta(doc, f"{v.get('ex_name','')}　|　{date_label}　|　"
                                 f"来源：{src_label}　|　共 {len(art_list)} 条　|　"
                                 f"{datetime.now().strftime('%Y-%m-%d %H:%M')}")
                DB.render_variety_section(doc, v, art_list,
                                          img_dir=img_root, image_map=image_map)
                DB.add_credit(doc)
                doc.save(fpath)
                produced.append(fpath)
            # 打包 zip（只含 Word，图片已内嵌在文档中）
            zname = f"期货品种资讯_{date_label}_{len(vs)}品种.zip"
            zpath = os.path.join(job_dir, zname)
            with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
                for p in produced:
                    z.write(p, os.path.basename(p))
            result_file = zpath
            download_name = zname

        img_count = len(image_map)

        # ---------- 完成 ----------
        summary = {
            "dates": dates,
            "date_label": date_label,
            "src": src,
            "src_label": src_label,
            "variety_count": len(vs),
            "article_count": total_arts,
            "image_count": img_count,
            "mode": mode,
            "dir": job_dir,
            "per_variety": [{"name": v["name"], "code": v["code"],
                             "count": len(found.get(v["code"], []))} for v in vs],
        }
        _set(job_id, status="done", progress=len(vs) + total_arts + 2,
             total=len(vs) + total_arts + 2,
             message="生成完成！", file=result_file,
             download_name=download_name, result=summary)
    except Exception as e:
        import traceback
        traceback.print_exc()
        _set(job_id, status="error", error=f"{type(e).__name__}: {e}")
    finally:
        if tmp_img_root:
            shutil.rmtree(tmp_img_root, ignore_errors=True)


@app.route("/api/progress/<job_id>")
def api_progress(job_id):
    with JOBS_LOCK:
        job = JOBS.get(job_id)
        if not job:
            abort(404)
        out = {k: v for k, v in job.items() if k != "file"}
        out["has_file"] = bool(job.get("file"))
        out["download_name"] = job.get("download_name")
        if job.get("file") and os.path.exists(job["file"]):
            out["size"] = os.path.getsize(job["file"])
        return jsonify(out)


@app.route("/api/download/<job_id>")
def api_download(job_id):
    with JOBS_LOCK:
        job = JOBS.get(job_id)
        if not job or not job.get("file"):
            abort(404)
        path = job["file"]
        name = job.get("download_name") or os.path.basename(path)
    if not os.path.exists(path):
        abort(404)
    return send_file(path, as_attachment=True, download_name=name)


@app.route("/api/open_folder/<job_id>", methods=["POST"])
def api_open_folder(job_id):
    with JOBS_LOCK:
        job = JOBS.get(job_id)
    if not job or not job.get("result"):
        abort(404)
    d = job["result"]["dir"]
    try:
        if os.name == "nt":
            os.startfile(d)  # noqa
        else:
            import subprocess
            subprocess.Popen(["open" if os.uname().sysname == "Darwin" else "xdg-open", d])
        return jsonify({"ok": True, "dir": d})
    except Exception as e:
        return jsonify({"ok": False, "dir": d, "error": str(e)})


if __name__ == "__main__":
    import socket

    def pick_port(prefer=8899):
        for p in [prefer, 8899, 8000, 9000, 8800, 7860, 6060, 7788, 5000]:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                s.bind(("127.0.0.1", p))
                return p
            except Exception:
                continue
            finally:
                s.close()
        return prefer

    port = int(os.environ.get("PORT", 0)) or pick_port()
    url = f"http://127.0.0.1:{port}"
    print("=" * 58)
    print("  期货品种资讯下载器 已启动")
    print(f"  请在浏览器打开： {url}")
    print(f"  导出文件保存位置： {OUTPUT_DIR}")
    print("  （关闭本窗口即可停止服务）")
    print("=" * 58)

    # 打包成 exe 后自动打开浏览器（可设 NO_BROWSER=1 关闭）
    if _is_frozen() and not os.environ.get("NO_BROWSER"):
        def _open():
            time.sleep(1.2)
            try:
                import webbrowser
                webbrowser.open(url)
            except Exception:
                pass
        threading.Thread(target=_open, daemon=True).start()

    app.run(host="127.0.0.1", port=port, debug=False, threaded=True)

