# 生活流水账 · daily-tracker

一个记录日常小事的单页应用——吃药、喝水、拉粑粑、买菜这类。一键记录，可自定义项目，有每日目标和趋势图。

线上地址：https://sirui0112.github.io/daily-tracker/

## 数据存在哪

**记录只存在你当前这台设备的浏览器里**（`localStorage`，键名 `liushuizhang.v1`）。

- 换一台设备看不到这份数据
- 清掉浏览器数据 = 记录全没了
- 跨设备同步还没做

## 开发

只有一个源文件：`src/app.html`。单页、无依赖、无框架、无构建工具链，样式和脚本都内联在里面。

```bash
# 改完源文件后重新生成 index.html
python3 build.py

# 本地预览
python3 -m http.server 8000
# 然后打开 http://localhost:8000/
```

`build.py` 做三件事：把初始项目配置写进 `defaultItems()`；给 `src/app.html` 套上 `<!doctype html>` / `<head>` / `<body>` 外壳；把生成结果的内容哈希写进 `sw.js` 的缓存名。

最后一条是刻意的——Service Worker 用缓存优先策略，**版本号忘了改，所有人会永远停在旧版本上**，而且很难发现。让哈希自动跟着内容走，就忘不掉。

之所以需要套壳，是因为这个应用最早是作为 Claude Artifact 写的，那个平台会自动注入文档骨架，所以源文件里没有这些标签。同一份源码现在同时能在两个环境跑：

| 环境 | 判断依据 | 数据去向 |
|---|---|---|
| Claude Artifact | `window.claude` 存在 | 平台云端数据库，多设备同步 |
| GitHub Pages / 本地 | `window.claude` 不存在 | 浏览器 localStorage |

**`index.html` 是生成产物，不要直接改**，改了下次 `build.py` 会覆盖掉。

## 部署

GitHub Pages，从 `main` 分支根目录直接部署，没有 CI。`index.html` 提交进仓库，推上去就生效。

## PWA

已经是可安装的 PWA：手机浏览器打开 → 分享 → 添加到主屏幕，之后从图标启动是全屏的，**断网也能打开**（前提是联网打开过至少一次）。

- `manifest.json` — 应用名、图标、`display: standalone`
- `sw.js` — 缓存应用外壳和 Google Fonts；缓存名由 `build.py` 注入
- `tools/make-icons.py` — 纯 Python 生成图标，无第三方依赖，改了配色重跑即可

**iOS 注意**：主屏应用的存储空间和 Safari 可能是分开的，所以要装就一开始装，别先在 Safari 里记一堆再添加。

## 后续

- [ ] 跨设备同步
- [ ] 定时提醒（吃药这类）
