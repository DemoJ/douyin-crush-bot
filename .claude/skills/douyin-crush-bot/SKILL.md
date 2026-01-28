---
name: douyin-crush-bot
description: 抖音自动化助手。用于自动刷抖音视频、对博主颜值进行 AI 打分、自动点赞或关注高颜值博主。当用户提到“刷抖音”、“找美女/帅哥”、“自动点赞抖音”时使用。
argument-hint: [--threshold 8.0] [--gender 女] [--action all] [--max-videos 100] [--login]
allowed-tools: Bash, Read, Write
---

# 抖音颜值心动机器人 (Douyin Crush Bot)

此技能通过 Playwright 控制抖音网页版，并结合视觉 AI 实现自动化审美筛选。

## 运行环境规范

在执行任何 Python 脚本时，**必须**优先检查并使用项目根目录下的虚拟环境解释器，严禁直接使用系统全局 Python，除非虚拟环境不存在。
- **Windows**: 使用 `.\.venv\Scripts\python.exe`
- **Linux/macOS**: 使用 `./.venv/bin/python`

**命令示例**:
`.\.venv\Scripts\python.exe .claude/skills/douyin-crush-bot/scripts/bot.py --threshold 9.0`

## 核心操作流程

1. **环境准备**：
   - 检查并确保安装了 `requirements.txt` 中的依赖。
   - 确保 Playwright 浏览器已安装 (`playwright install chromium`)。

2. **登录管理**：
   - 若未登录，运行 `/douyin-crush-bot --login`。
   - 脚本 `scripts/login.py` 会启动浏览器供用户手动扫码，登录后 Cookies 将保存至 `auth.json`。

3. **自动化运行**：
   - 执行 `scripts/bot.py`，加载 `auth.json` 状态。
   - 循环逻辑：截图 -> 视觉 AI 打分 -> 决策（点赞/关注） -> 下一个视频。

## 参数说明

- `--threshold`: 颜值打分阈值 (0.0 - 10.0)，默认 8.0。
- `--gender`: 目标性别 (男/女/全部)，默认 全部。
- `--action`: 互动行为 (like:仅点赞, follow:仅关注, all:全部)，默认 all。
- `--max-videos`: 本次运行最大浏览视频数，默认 100。
- `--login`: 启动登录模式，手动扫码后保存状态。

## 提示

- 运行前请确保在脚本中配置好你的视觉模型 API Key。
- 建议使用有界面模式运行，以便观察自动化过程。
