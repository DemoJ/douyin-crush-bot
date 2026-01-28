---
name: douyin-crush-bot
description: 抖音网页版自动化工具。用于自动刷视频、对博主颜值进行打分、自动点赞或关注高颜值博主。当用户提到“刷抖音”、“找美女/帅哥”、“自动点赞抖音”时使用。
argument-hint: [--threshold 8.0] [--gender 女] [--action all] [--max-videos 100]
allowed-tools: Bash, Read, Write
---

# 执行准则 (CRITICAL)
1. **禁止闲聊**: 收到任务后，严禁回复任何“好的”、“没问题”、“正在为您启动”等废话。
2. **即刻执行**: 必须直接生成并调用对应的 `run_shell_command`。
3. **环境优先**: 必须先检查并准备 Python 虚拟环境。

# 运行环境检查
在执行任务前，**第一步**必须使用 `ls .venv` 检查虚拟环境是否存在。
- 如果不存在：
  - Windows: `python -m venv .venv && ".venv/Scripts/pip" install -r ".claude/skills/douyin-crush-bot/requirements.txt" && playwright install chromium`
  - Linux/macOS: `python3 -m venv .venv && ".venv/bin/pip" install -r ".claude/skills/douyin-crush-bot/requirements.txt" && playwright install chromium`
- 如果已存在：直接进行下一步。

# 参数提取
从用户意图中提取：
- `--threshold`: 颜值分 (默认 8.0)
- `--gender`: 性别 (女/男/全部，默认 全部)
- `--max-videos`: 数量 (默认 100)
- `--action`: 行为 (like/follow/all，默认 all)

# 最终命令构建
**注意：为了兼容 Git Bash 和 PowerShell，请统一使用正斜杠 `/` 并加上双引号。**

- **Windows 命令格式**: 
  `".venv/Scripts/python.exe" ".claude/skills/douyin-crush-bot/scripts/bot.py" [参数]`
- **Linux/macOS 命令格式**:
  `"./venv/bin/python" ".claude/skills/douyin-crush-bot/scripts/bot.py" [参数]`

# 示例意图响应
**用户**: "帮我刷10条抖音，点赞8分以上的妹子"
**你的唯一动作**: 调用 `run_shell_command` 执行 `".venv/Scripts/python.exe" ".claude/skills/douyin-crush-bot/scripts/bot.py" --max-videos 10 --threshold 8.0 --gender 女 --action like`
