# 抖音颜值心动机器人 (Douyin Crush Bot)

> [!CAUTION]
> **风险警示**：本程序涉及自动化操作抖音网页端，属于抖音官方禁止的行为。频繁使用可能导致账号被风控（如：功能受限、强制下线、甚至封号）。**强烈建议使用小号进行测试和运行，由此产生的所有账号安全问题及法律责任由使用者自行承担。**

这是一个集成在 Claude CLI 中的技能，通过 Playwright 自动化控制抖音网页版，并结合 OpenAI 兼容格式的视觉大模型对视频博主进行颜值评分。

## 核心功能

- **自动化刷视频**：模拟人类行为，自动翻页浏览。
- **视觉 AI 审美**：实时截取视频画面并调用视觉模型打分。
- **精准互动**：根据设定的颜值阈值、性别偏好，自动执行点赞和关注。
- **防风控策略**：支持随机观看时长、自动处理引导弹窗、使用官方快捷键操作。

## 快速开始

### 1. 环境准备

确保你的电脑已安装 Python 3.8+。

```bash
# 安装依赖 (建议在虚拟环境中运行)
pip install -r .claude/skills/douyin-crush-bot/requirements.txt

# 安装 Playwright 浏览器
playwright install chromium
```

### 2. 配置 API 密钥

将 `.claude/skills/douyin-crush-bot/.env.example` 复制为 `.claude/skills/douyin-crush-bot/.env`，并填入你的 API 配置。

### 3. 登录抖音

运行登录命令，在弹出的窗口中完成扫码：

```bash
/douyin-crush-bot --login
```

## 使用方法

### 1. 命令行调用 (斜杠命令)
直接输入 `/douyin-crush-bot` 并带上参数。

### 2. 自然语言调用
由于已配置 `description`，你可以直接对 Claude 说：
- “帮我刷一会儿抖音，点赞 8 分以上的妹子”
- “启动抖音机器人，刷 20 个视频，关注并点赞帅哥”

Claude 会自动解析你的意图并转换为带参数的命令执行。

### 3. 如何关闭自然语言调用
如果你不希望 Claude 在对话中自动触发此技能，只需修改 `.claude/skills/douyin-crush-bot/SKILL.md` 文件：

在顶部的 YAML 元数据中添加 `disable-model-invocation: true`：

```yaml
---
name: douyin-crush-bot
description: ...
disable-model-invocation: true  # 添加这一行
---
```
保存后，该技能将只能通过 `/douyin-crush-bot` 手动触发。

## 参数说明

| 参数 | 说明 | 默认值 | 可选值 |
| :--- | :--- | :--- | :--- |
| `--threshold` | 颜值评分阈值 | 8.0 | 0.0 - 10.0 |
| `--gender` | 目标性别筛选 | 全部 | 男, 女, 全部 |
| `--action` | 匹配后的动作 | all | like, follow, all |
| `--max-videos` | 本次运行最大浏览数| 100 | 任意正整数 |
| `--login` | 启动登录模式 | - | - |

## 注意事项

1. **API 消耗**：建议先用较小的 `--max-videos` 进行测试。
2. **账号安全**：虽然脚本模拟了人类行为，但建议不要长时间高频运行。
3. **分辨率限制**：运行期间请勿随意拉伸 Playwright 浏览器窗口。
4. **控制台编码**：已针对 Windows 优化，建议使用现代终端。