# 期货品种资讯下载器

把公众号图文 **[公歧收藏：商品品种资讯导航](https://mp.weixin.qq.com/s/Qh9bfpa41s_CN9v2-XdIeQ)**
里收录的全部期货品种，做成一个 **Python + HTML** 的本地小工具：

- 可 **批量下载全部品种**，也可以 **只下载单个品种** 的资讯；
- 只抓取 **今天 / 昨天 / 前天**（近 3 天）的资讯；
- 资讯来源可选：**东方财富 / 新浪财经 / 两家合并**；
- 导出为 **Word 文档**，规范排版，**原文配图直接插入对应资讯正文中**；
- 网页界面（UI）美观，支持搜索、多选、预览、进度条、一键下载。

> 📥 **直接下载 exe（免安装）**：
> [FuturesNewsDownloader.exe](https://github.com/chenzhuanxin/futures-news-downloader/releases/download/v1.0.0/FuturesNewsDownloader.exe)
> —— Windows 单文件版，约 22 MB，双击即用
>
> 📖 **在线文档**：
> [使用说明](https://chenzhuanxin.github.io/futures-news-downloader/usage.html) ·
> [数据源说明](https://chenzhuanxin.github.io/futures-news-downloader/data-source.html) ·
> [项目首页](https://chenzhuanxin.github.io/futures-news-downloader/)

---

## 一、快速开始

### 方式 0：直接用 exe（免安装，最省事）

从 [Releases](https://github.com/chenzhuanxin/futures-news-downloader/releases/latest)
下载 `FuturesNewsDownloader.exe`，**双击运行**即可，无需安装 Python。
启动后会自动打开浏览器，生成的文件保存在 **exe 同级目录的 `output/`** 下。

> 首次运行若被 Windows SmartScreen 拦截，点「更多信息」→「仍要运行」即可（未签名程序的正常提示）。

### 方式 A：双击启动（源码方式，推荐开发者）

双击项目根目录下的 **`启动.bat`**，会自动：
1. 启动本地服务（默认 `http://127.0.0.1:8899`）；
2. 自动打开浏览器。

用完直接关闭那个黑色命令行窗口即可。

### 方式 B：命令行启动

```bash
# 首次安装依赖（已装可跳过）
pip install -r requirements.txt

# 启动
python app.py
# 浏览器打开 http://127.0.0.1:8899
```

> 端口 8899 若被占用会自动切换到 8000 / 9000 / 8800 等，命令行会打印实际地址。
> 也可指定端口：`set PORT=9000 && python app.py`

---

## 二、使用步骤

1. **选品种**：在品种卡片上点击即可勾选（再点取消）。
   - 顶部搜索框可按名称 / 代码 / 拼音搜索，如 `沪铜`、`CU`；
   - 快捷按钮：`全选`、`清空`、`仅选夜盘`、`仅选金属`、`仅选农产`；
   - 不选任何品种直接点生成 = 全部品种。
2. **选资讯来源**：`东方财富` / `新浪财经` / `两家合并`（合并时同一篇稿子会自动去重）。
3. **选导出方式**：
   - `合并为一个 Word`：所有选中品种汇总到一个 docx（每个品种独立分页）；
   - `分品种打包 ZIP`：每个品种一个 docx，打包成 zip 下载。
4. **设置条数 / 配图**：可限制每个品种最多抓多少条、是否插入原文配图。
5. 点 **`预览资讯`** 可先看看近三天各品种有多少条、都是什么标题。
6. 点 **`生成并下载 Word`**，进度条走完后点下载按钮即可。

生成的文件同时保存在项目的 `output/` 目录下（图片已内嵌在 Word 里，
不会另外生成 images 文件夹），界面上也有「打开所在文件夹」按钮。

---

## 三、Word 排版规范

| 元素 | 字体 | 字号 | 其他 |
|------|------|------|------|
| 标题（文档名 / 品种名 / 每条资讯标题） | **黑体** | 三号(16pt) | 加粗、居中 |
| 正文 | **仿宋** | 三号(16pt) | 两端对齐、首行缩进 2 字符 |
| 来源 / 时间 / 原文链接 | 仿宋 | 五号 | 居中、灰色 |
| 图片 | — | — | 按原文位置插入对应资讯正文中，居中、等比缩放、全部展示 |
| 文档底部署名 | 黑体 | 小四 | 居中：设计：公歧子　微信：gongqizi0 |

页面 A4，左右页边距 2.5cm。

---

## 四、目录结构

```
futures-news-downloader/
├── app.py                 # Flask 后端：品种接口 / 预览 / 导出 / 进度 / 下载
├── requirements.txt
├── 启动.bat               # Windows 一键启动（源码方式）
├── build_exe.bat          # 一键打包为 exe（PyInstaller）
├── app.ico                # 应用图标
├── core/
│   ├── varieties.py       # 88 个品种数据（来自公众号导航页）
│   ├── sources.py         # 资讯检索 + 正文/图片抓取（东财 / 新浪）
│   └── docx_builder.py    # Word 排版生成
├── static/
│   ├── index.html         # 前端页面
│   ├── style.css          # 界面样式
│   └── app.js             # 前端交互逻辑
├── docs/                  # GitHub Pages 在线文档
│   ├── index.html         # 项目首页
│   ├── usage.html         # 使用说明
│   └── data-source.html   # 数据源说明
└── output/                # 生成结果（Word / zip）
```

---

## 五、数据来源与说明

- 品种数据：公众号图文内嵌的《期货品种资讯导航》页面（6 大交易所 / 88 个品种）。
- 资讯数据（仅以下两站，按品种关键词检索并按发布时间筛选近 3 天）：
  - **东方财富**：搜索接口 `search-api-web.eastmoney.com` + 文章页正文与配图；
  - **新浪财经**：搜索接口 `interface.sina.cn/homepage/search.d.json` + 文章页正文与配图。
- 原文配图在生成 Word 时内嵌到对应资讯的正文中，成品文件夹只保留 Word / zip，
  不再单独输出图片目录。
- 本工具仅供个人学习研究使用，抓取内容版权归原媒体所有，请勿用于商业用途。
- 抓取频率已做限速；如遇接口临时不可用，稍后重试即可。
