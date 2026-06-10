# TVBox 聚合源

自动聚合 TVBox 影视源，每小时 GitHub Actions 自动更新。

## 使用方法（填入影视仓/丰米）

### 简洁版（10个最快采集站，播放测速排序）

| 渠道 | 地址 |
|------|------|
| GitHub Raw | `https://raw.githubusercontent.com/shifeiquan520/shifeiquan1/main/tvbox.json` |
| ghproxy 加速 | `https://ghproxy.net/https://raw.githubusercontent.com/shifeiquan520/shifeiquan1/main/tvbox.json` |
| jsDelivr CDN | `https://cdn.jsdelivr.net/gh/shifeiquan520/shifeiquan1@main/tvbox.json` |

### 全量版（全部站点合并，带 spider JAR）

| 渠道 | 地址 |
|------|------|
| GitHub Raw | `https://raw.githubusercontent.com/shifeiquan520/shifeiquan1/main/tvbox_full.json` |
| ghproxy 加速 | `https://ghproxy.net/https://raw.githubusercontent.com/shifeiquan520/shifeiquan1/main/tvbox_full.json` |
| jsDelivr CDN | `https://cdn.jsdelivr.net/gh/shifeiquan520/shifeiquan1@main/tvbox_full.json` |

### 多仓版（多仓库独立保留）

| 渠道 | 地址 |
|------|------|
| GitHub Raw | `https://raw.githubusercontent.com/shifeiquan520/shifeiquan1/main/tvbox_multi.json` |
| ghproxy 加速 | `https://ghproxy.net/https://raw.githubusercontent.com/shifeiquan520/shifeiquan1/main/tvbox_multi.json` |
| jsDelivr CDN | `https://cdn.jsdelivr.net/gh/shifeiquan520/shifeiquan1@main/tvbox_multi.json` |

> **推荐**：国内用户优先使用 ghproxy 或 jsDelivr 地址，速度更快。
>
> **多仓配置方式**：影视仓 → 首页 → 配置 → 多仓地址

## 客户端下载

| 客户端 | 多仓 | 仓库地址 |
|--------|:----:|---------|
| TVBox 原版 | ❌ | [GitHub Releases](https://github.com/o0HalfLife0o/TVBoxOSC/releases) |
| 影视仓 | ✅ | [GitHub 仓库](https://github.com/q215613905/TVBoxOSC) |
| FongMi（丰米）| ✅ | [GitHub 仓库](https://github.com/FongMi/Release) |
| TVBox 合集下载 | - | [网盘下载](https://pan.wpcoder.cn/?dir=tvbox) |

## 说明

- 数据来源：[tvbox.clbug.com](https://tvbox.clbug.com/user.php)
- 每小时自动更新：测速 → 抓取 → 合并 → 推送
- 播放测速流程：获取视频 → 下载 m3u8 主列表 → 解析媒体列表 → 下载 ts 分片 → 计算持续速度
- 置顶规则：索尼、360 固定排在前两位，其他按播放速度/延迟排序
- GitHub Actions 通过 CF Tunnel + 本地代理（国内IP）测速，突破采集站 IP 封锁
- 不可用源自动清洗，恢复后自动加回

## 更新频率

每小时整点（UTC `0 * * * *`），GitHub Actions 自动执行。
