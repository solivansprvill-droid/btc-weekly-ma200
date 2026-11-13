# 比特币周线 MA200 K 线图

一个纯静态网页，展示比特币从 2011 年 8 月（Bitstamp 开始交易）到现在的周线 K 线，叠加周线 MA200 和 MA50。

## 功能
- 周线蜡烛图（周一 00:00 UTC 开盘），默认对数坐标，可切换
- MA200（黄线）和 MA50（蓝线）
- 顶部卡片：最新收盘价、MA200、距 MA200 的百分比、MA50、MA200 近四周斜率
- 可切换显示全部、近 5 年、近 2 年；鼠标悬停显示 OHLC

## 目录
```
index.html                     页面（图表库为 lightweight-charts，经 jsDelivr CDN 加载）
data/btc_weekly.json           周线数据
scripts/fetch_data.py          从 Bitstamp 拉日线并聚合成周线，只用 Python 标准库
.github/workflows/update-data.yml  每周一、周四自动更新数据并提交
```

## 本地运行
```bash
python3 scripts/fetch_data.py      # 更新数据
python3 -m http.server 8000        # 打开 http://localhost:8000
```
直接双击打开 index.html 无法读取 JSON，需要像上面这样起一个本地服务。

## 部署
- 私有仓库可以部署到 Vercel、Netlify 或 Cloudflare Pages（导入仓库，构建命令留空，输出目录为根目录）。
- 私有仓库开启 GitHub Pages 需要付费套餐。

## 说明
- MA200 = 最近 200 根周线收盘价的简单平均。
- 最新一根周线可能还没收盘，数值会变动。
- 仅供学习参考，不构成投资建议。
