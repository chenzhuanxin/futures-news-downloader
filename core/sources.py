# -*- coding: utf-8 -*-
"""
资讯抓取模块（双数据源）

东方财富：
  · 搜索接口  https://search-api-web.eastmoney.com/search/jsonp
  · 文章页    div#ContentBody

新浪财经：
  · 搜索接口  https://interface.sina.cn/homepage/search.d.json
  · 文章页    div#artibody / div#article / .article-content

统一输出条目：{title, date, source, url, code, summary, src}
文章正文解析为「顺序块」blocks：[{type:'p',text:...}, {type:'img',url:...}, ...]
以便 Word 里图片落在原文对应的位置。
"""
import re
import os
import json
import time
import html as _html
import hashlib
from datetime import datetime, timedelta
from urllib.parse import quote

import requests
from bs4 import BeautifulSoup

# --------------------------------------------------------------------------
# 常量
# --------------------------------------------------------------------------
SRC_LABEL = {"em": "东方财富", "sina": "新浪财经"}

EM_SEARCH_API = "https://search-api-web.eastmoney.com/search/jsonp"
SINA_SEARCH_API = "https://interface.sina.cn/homepage/search.d.json"

BASE_HEADERS = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                   "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"),
    "Accept-Language": "zh-CN,zh;q=0.9",
}

EM_HEADERS = dict(BASE_HEADERS, Referer="https://so.eastmoney.com/")
SINA_HEADERS = dict(BASE_HEADERS, Referer="https://finance.sina.com.cn/",
                    **{"X-Requested-With": "XMLHttpRequest"})

EM_SESSION = requests.Session()
EM_SESSION.headers.update(EM_HEADERS)
SINA_SESSION = requests.Session()
SINA_SESSION.headers.update(SINA_HEADERS)

# 图片最小尺寸（像素），过滤站点图标/广告小图
MIN_IMG_W = 200
MIN_IMG_H = 120

# 明显不是正文配图的 URL 片段
IMG_URL_BLACKLIST = (
    "sina_logo", "push_qrcode", "thumb_default", "sinaimg.cn/default",
    "i.sso.sina.com.cn", "icon", "avatar", "logo", "qrcode", "share_",
    "/blank.", "spacer.", "transparent.",
)

_TAG_RE = re.compile(r"<[^>]+>")

# 新浪搜索对个别品种用更精准的关键词（覆盖导航页自带的关键词）
SINA_KW_OVERRIDE = {
    "TS": "2年期国债",
    "TF": "5年期国债",
    "T": "10年期国债",
    "TL": "30年期国债",
}

# 正文中需要剔除的垃圾段
_JUNK_STARTS = (
    "（文章来源", "（文章来", "郑重声明", "特别声明", "责任编辑", "扫描二维码",
    "更多精彩", "海量资讯", "点击查看", "查看更多", "返回搜狐", "新浪声明",
    "风险提示：本文", "免责声明", "以上内容仅代表", "特别提醒", "广告",
    "原标题：", "本文来源：", "海量数据",
)
_JUNK_CONTAINS = ("新浪财经公众号", "24小时滚动播报", "点击进入专题", "下载新浪财经")


def _strip_tags(s):
    if not s:
        return ""
    # 去掉东财搜索接口返回的高亮标记控制符
    s = s.replace("\u0001", "").replace("\u0002", "")
    return _html.unescape(_TAG_RE.sub("", s)).strip()


def _is_junk(text):
    if not text:
        return True
    t = text.strip()
    if len(t) <= 2:
        return True
    if t.startswith(_JUNK_STARTS):
        return True
    if any(k in t for k in _JUNK_CONTAINS):
        return True
    return False


def get_date_window(days=3):
    """返回 [今天, 昨天, 前天]（可配置天数），格式 YYYY-MM-DD"""
    today = datetime.now().date()
    return [(today - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(days)]


# ==========================================================================
# 一、东方财富
# ==========================================================================
def search_news_em(keyword, page_size=40, page_index=1, sort="time"):
    """东财搜索接口，返回 [{title,date,source,url,code,summary}]"""
    param = {
        "uid": "",
        "keyword": keyword,
        "type": ["cmsArticleWebOld"],
        "client": "web",
        "clientType": "web",
        "clientVersion": "curr",
        "param": {
            "cmsArticleWebOld": {
                "searchScope": "default",
                "sort": sort,
                "pageIndex": page_index,
                "pageSize": page_size,
                "preTag": "\u0001",
                "postTag": "\u0002",
            }
        },
    }
    url = EM_SEARCH_API + "?cb=cb&param=" + quote(json.dumps(param, ensure_ascii=False))
    try:
        r = EM_SESSION.get(url, timeout=15)
        r.raise_for_status()
        text = r.text
        m = re.search(r"^[^(]*\((.*)\)\s*;?\s*$", text, re.S)
        payload = json.loads(m.group(1) if m else text)
    except Exception as e:
        print(f"[em-search] {keyword} 失败: {e}")
        return []

    result = (payload.get("result") or {}).get("cmsArticleWebOld") or []
    out = []
    for it in result:
        title = _strip_tags(it.get("title", ""))
        if not title:
            continue
        out.append({
            "title": title,
            "date": (it.get("date") or "").strip(),
            "source": (it.get("mediaName") or "").strip(),
            "url": it.get("url") or "",
            "code": str(it.get("code") or ""),
            "summary": _strip_tags(it.get("content", "")),
            "src": "em",
        })
    return out


def fetch_article_em(url):
    """东财文章正文：div#ContentBody"""
    out = {"title": "", "paragraphs": [], "images": [], "blocks": [],
           "source": "", "date": ""}
    url = _normalize_em_url(url)
    try:
        r = EM_SESSION.get(url, timeout=20, headers={"Referer": "https://futures.eastmoney.com/"})
        r.raise_for_status()
        r.encoding = r.apparent_encoding or "utf-8"
        soup = BeautifulSoup(r.text, "lxml")

        t = soup.find("title")
        if t:
            out["title"] = _strip_tags(t.get_text()).split("_")[0].strip()

        tm = soup.find("div", class_="time")
        if tm:
            out["date"] = tm.get_text(strip=True)
        if not out["date"]:
            m = re.search(r'class="time">\s*([\d\-\s:]+)', r.text)
            if m:
                out["date"] = m.group(1).strip()

        sb = soup.find("div", class_="sourcebox")
        if sb:
            m = re.search(r"文章来源[：:]\s*([^\s]+)", sb.get_text(" ", strip=True))
            if m:
                out["source"] = m.group(1)

        body = soup.find("div", id="ContentBody")
        if not body:
            return out
        for sel in body.select(".ad_context1, .ad_context3, .em_media, script, style, .zwothers"):
            sel.decompose()
        _fill_from_body(out, body)
    except Exception as e:
        print(f"[em-article] {url} 失败: {e}")
        out["error"] = str(e)
    return out


def _normalize_em_url(url):
    if url and url.startswith("http://"):
        return "https://" + url[len("http://"):]
    return url


# ==========================================================================
# 二、新浪财经
# ==========================================================================
def search_news_sina(keyword, num=20, page=1):
    """新浪财经搜索接口，返回 [{title,date,source,url,code,summary}]"""
    url = f"{SINA_SEARCH_API}?q={quote(keyword)}&num={num}&page={page}"
    try:
        r = SINA_SESSION.get(url, timeout=15)
        r.raise_for_status()
        payload = json.loads(r.text)
    except Exception as e:
        print(f"[sina-search] {keyword} p{page} 失败: {e}")
        return []

    lst = ((payload.get("result") or {}).get("list")) or []
    out = []
    for it in lst:
        title = _strip_tags(it.get("title") or it.get("origin_title") or "")
        if not title:
            continue
        u = it.get("url") or ""
        if "video.sina.com.cn" in u:      # 视频页无正文，跳过
            continue
        out.append({
            "title": title,
            "date": (it.get("datetime") or "").strip(),
            "source": (it.get("media") or "").strip(),
            "url": u,
            "code": str(it.get("id") or ""),
            "summary": _strip_tags(it.get("intro") or ""),
            "src": "sina",
        })
    return out


def fetch_article_sina(url):
    """新浪文章正文：div#artibody / div#article / .article-content"""
    out = {"title": "", "paragraphs": [], "images": [], "blocks": [],
           "source": "", "date": ""}
    try:
        r = SINA_SESSION.get(url, timeout=20, headers={"Referer": "https://finance.sina.com.cn/"})
        r.raise_for_status()
        r.encoding = r.apparent_encoding or "utf-8"
        soup = BeautifulSoup(r.text, "lxml")

        og = soup.find("meta", attrs={"property": "og:title"})
        if og and og.get("content"):
            out["title"] = _strip_tags(og["content"])
        if not out["title"]:
            h1 = soup.find("h1")
            if h1:
                out["title"] = h1.get_text(strip=True)
        if not out["title"]:
            t = soup.find("title")
            if t:
                out["title"] = _strip_tags(t.get_text()).split("_")[0].strip()

        d = soup.find("span", class_="date") or soup.find("div", class_="date")
        if d:
            out["date"] = d.get_text(strip=True)
        if not out["date"]:
            ogt = soup.find("meta", attrs={"property": "article:published_time"})
            if ogt and ogt.get("content"):
                out["date"] = ogt["content"].replace("T", " ")[:19]

        body = None
        for css in ["#artibody", "div#article", "div.article-content",
                    "div.article-content-left", "div.article"]:
            body = soup.select_one(css)
            if body:
                break
        if not body:
            return out
        for sel in body.select(".article-notice, .article-bottom, .fengniao-container, "
                               "script, style, .appendQr_wrap, .article-editor"):
            sel.decompose()
        _fill_from_body(out, body)
    except Exception as e:
        print(f"[sina-article] {url} 失败: {e}")
        out["error"] = str(e)
    return out


# ==========================================================================
# 三、正文顺序块（图文按原顺序）
# ==========================================================================
def _abs_url(src, base="https://futures.eastmoney.com/"):
    if not src:
        return ""
    src = src.strip()
    if src.startswith("//"):
        return "https:" + src
    if src.startswith("/"):
        return "https://finance.sina.com.cn" + src if base.startswith("https://finance") \
            else "https://futures.eastmoney.com" + src
    if src.startswith("http"):
        return src
    return base + src


def _fill_from_body(out, body):
    """按文档顺序把正文与配图填进 out（paragraphs / images / blocks）"""
    blocks, paras, imgs = [], [], []
    for el in body.find_all(["p", "img", "h3", "h4", "blockquote"]):
        if el.name == "img":
            src = el.get("src") or el.get("data-src") or el.get("data-original") or ""
            src = _abs_url(src)
            if not src or any(b in src.lower() for b in IMG_URL_BLACKLIST):
                continue
            w = el.get("width") or el.get("data-w")
            h = el.get("height") or el.get("data-h")
            try:
                w = int(str(w)) if w else None
                h = int(str(h)) if h else None
            except Exception:
                w = h = None
            if w and h and (w < MIN_IMG_W or h < MIN_IMG_H):
                continue
            if blocks and blocks[-1]["type"] == "img" and blocks[-1]["url"] == src:
                continue
            blocks.append({"type": "img", "url": src})
            imgs.append(src)
        else:
            txt = el.get_text("\u200b", strip=True).replace("\u200b", "").strip()
            if _is_junk(txt):
                continue
            if blocks and blocks[-1]["type"] == "p" and blocks[-1]["text"] == txt:
                continue
            blocks.append({"type": "p", "text": txt})
            paras.append(txt)

    # 段落为空时兜底：直接取纯文本
    if not paras:
        txt = body.get_text("\n", strip=True)
        for line in (x.strip() for x in txt.split("\n")):
            if not _is_junk(line):
                blocks.append({"type": "p", "text": line})
                paras.append(line)

    out["blocks"] = blocks
    out["paragraphs"] = paras
    out["images"] = imgs


def fetch_article(url):
    """自动按域名分派到对应解析器"""
    if not url:
        return {"title": "", "paragraphs": [], "images": [], "blocks": [],
                "source": "", "date": ""}
    if "sina.com" in url:
        return fetch_article_sina(url)
    return fetch_article_em(url)


# ==========================================================================
# 四、按品种检索（支持多源合并）
# ==========================================================================
def _in_window(date_str, dset):
    return bool(date_str) and date_str[:10] in dset


def _variety_kw(variety):
    return SINA_KW_OVERRIDE.get(variety.get("code")) or variety.get("kw") or variety["name"]


def _em_variety(variety, dates, max_items):
    dset = set(dates)
    dmin = min(dset)
    kw = variety.get("kw") or variety["name"]
    seen, picked = set(), []
    for page in (1, 2):
        items = search_news_em(kw, page_size=40, page_index=page)
        if not items:
            break
        stop = False
        for it in items:
            d = it["date"][:10] if it["date"] else ""
            if d in dset:
                key = it["code"] or it["url"]
                if key and key not in seen:
                    seen.add(key)
                    picked.append(it)
                    if len(picked) >= max_items:
                        stop = True
                        break
            elif d and d < dmin:
                stop = True
                break
        if stop:
            break
        time.sleep(0.08)
    return picked


def _sina_variety(variety, dates, max_items, max_pages=4):
    dset = set(dates)
    dmin = min(dset)
    kw = _variety_kw(variety)
    seen, picked = set(), []
    for page in range(1, max_pages + 1):
        items = search_news_sina(kw, num=20, page=page)
        if not items:
            break
        page_dates = [it["date"][:10] for it in items if it["date"]]
        for it in items:
            d = it["date"][:10] if it["date"] else ""
            if d in dset:
                key = it["url"] or it["code"]
                if key and key not in seen:
                    seen.add(key)
                    picked.append(it)
        # 本页最早时间已早于窗口 —— 视为已翻过窗口
        if page_dates and max(page_dates) < dmin:
            break
        if len(picked) >= max_items * 2:
            break
        time.sleep(0.08)
    return picked


def _norm_title(t):
    return re.sub(r"[\s\W_]+", "", t or "")[:26]


def fetch_variety_news(variety, dates, max_items=15, src="em"):
    """抓取单个品种在窗口期内的资讯（按时间倒序）。
    src: 'em' | 'sina' | 'both'
    """
    picked = []
    if src in ("em", "both"):
        picked += _em_variety(variety, dates, max_items)
    if src in ("sina", "both"):
        picked += _sina_variety(variety, dates, max_items)

    # 跨源去重（同一篇稿子两边都有时只留一条）
    uniq, seen_titles = [], set()
    for it in picked:
        k = _norm_title(it["title"])
        if k in seen_titles:
            continue
        seen_titles.add(k)
        it["variety"] = variety["name"]
        it["variety_code"] = variety["code"]
        uniq.append(it)

    uniq.sort(key=lambda x: x["date"], reverse=True)
    return uniq[:max_items]


# ==========================================================================
# 五、图片下载
# ==========================================================================
def download_image(url, out_dir, referer="", min_w=MIN_IMG_W, min_h=140):
    """下载图片到 out_dir，返回本地文件名；失败或过小返回 None"""
    try:
        hdr = dict(BASE_HEADERS)
        if referer:
            hdr["Referer"] = referer
        r = requests.get(url, headers=hdr, timeout=25)
        r.raise_for_status()
        ctype = r.headers.get("Content-Type", "")
        ext = ".jpg"
        if "png" in ctype:
            ext = ".png"
        elif "gif" in ctype:
            ext = ".gif"
        elif "webp" in ctype:
            ext = ".webp"
        elif "jpeg" in ctype or "jpg" in ctype:
            ext = ".jpg"
        else:
            m = re.search(r"\.(jpg|jpeg|png|gif|webp)", url, re.I)
            if m:
                ext = "." + m.group(1).lower()
        name = hashlib.md5(url.encode("utf-8")).hexdigest()[:16] + ext
        os.makedirs(out_dir, exist_ok=True)
        path = os.path.join(out_dir, name)
        with open(path, "wb") as f:
            f.write(r.content)
        if len(r.content) < 2048:          # 过小，视为无效
            _rm(path)
            return None
        try:
            from PIL import Image
            with Image.open(path) as im:
                w, h = im.size
            if w < min_w or h < min_h:     # 按真实像素过滤图标 / 窄横幅
                _rm(path)
                return None
        except Exception:
            pass
        return name
    except Exception as e:
        print(f"[image] {url} 失败: {e}")
        return None


def _rm(path):
    try:
        os.remove(path)
    except Exception:
        pass
