#!/usr/bin/env python3
"""把 src/app.html 打包成可独立运行的 index.html。

Artifact 发布时平台会自动补上 <!doctype>/<head>/<body>，所以 src/app.html
里没有这些标签；部署到 Pages 就需要自己补。改完 src/app.html 后重跑本脚本。
"""
import io, json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
src = io.open(os.path.join(HERE, "src", "app.html"), encoding="utf-8").read()

# 初始项目配置：新设备第一次打开时用这套；之后以浏览器里存的为准
ITEMS = [
  {"id":"med","emoji":"💊","name":"吃药","color":"red","unit":"","presets":[{"label":"早","value":None},{"label":"晚","value":None}],"goal":2,"archived":False},
  {"id":"water","emoji":"💧","name":"喝水","color":"blue","unit":"ml","presets":[{"label":"200","value":200},{"label":"300","value":300}],"goal":2000,"archived":False},
  {"id":"cmtlblbfc","emoji":"🥛","name":"吸奶","color":"aqua","unit":"ml","presets":[{"label":"30","value":30}],"goal":None,"archived":False},
  {"id":"poop","emoji":"💩","name":"拉粑粑","color":"yellow","unit":"","presets":[{"label":"正常","value":None},{"label":"偏稀","value":None}],"goal":None,"archived":False},
  {"id":"buy","emoji":"🛒","name":"买菜","color":"green","unit":"SGD","presets":[{"label":"30","value":30},{"label":"60","value":60}],"goal":None,"archived":False},
  {"id":"move","emoji":"🏃","name":"散步","color":"orange","unit":"分钟","presets":[{"label":"30","value":30},{"label":"60","value":60}],"goal":None,"archived":False},
]
body = json.dumps(ITEMS, ensure_ascii=False)
src, n = re.subn(r"function defaultItems\(\)\{\s*return \[.*?\n  \];\n\}",
                 "function defaultItems(){\n  return " + body + ";\n}",
                 src, count=1, flags=re.S)
assert n == 1, "没能替换 defaultItems()，检查源文件是否改过结构"

head, sep, rest = src.partition("</style>")
assert sep, "没找到 </style>"

out = """<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<style>
/* 平台在 Artifact 里注入的基础重置，本地要自己补上 */
body{margin:0}
img{max-width:100%}
[hidden]{display:none !important}
</style>
""" + head + sep + """
</head>
<body>
""" + rest + """
</body>
</html>
"""
io.open(os.path.join(HERE, "index.html"), "w", encoding="utf-8").write(out)
print("index.html 已生成：%d 字节" % len(out))
