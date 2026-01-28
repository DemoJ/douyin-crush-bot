import asyncio
import os
import sys
import random
import json
import base64
import datetime
from playwright.async_api import async_playwright
from openai import AsyncOpenAI
from dotenv import load_dotenv

# 强制设置标准输出编码为 UTF-8，解决 Windows 控制台乱码
sys.stdout.reconfigure(encoding='utf-8')

# 加载环境变量
load_dotenv()

# 配置 OpenAI 客户端
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
OPENAI_MODEL_NAME = os.getenv("OPENAI_MODEL_NAME", "gpt-4o")

def log(msg):
    """带时间戳的日志输出"""
    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {msg}")

class DouyinBot:
    def __init__(self, threshold=8.0, gender="全部", max_videos=100, action="all", headless=False):
        self.threshold = threshold
        self.gender = gender
        self.max_videos = max_videos
        self.action = action  # like, follow, all
        self.headless = headless
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        self.auth_path = os.path.join(os.path.dirname(self.current_dir), "auth.json")
        
        if OPENAI_API_KEY:
            self.client = AsyncOpenAI(
                api_key=OPENAI_API_KEY,
                base_url=OPENAI_BASE_URL
            )
        else:
            self.client = None
            log("警告: 未配置 OPENAI_API_KEY，视觉打分功能将不可用。")

    async def get_beauty_score(self, image_bytes):
        """调用兼容 OpenAI 格式的视觉模型进行打分"""
        if not self.client:
            return 5.0, "未知"
        
        try:
            # 将图片转换为 Base64
            base64_image = base64.b64encode(image_bytes).decode('utf-8')
            
            prompt = (
                "你是一个审美专家。请分析这张图片中的主要人物，如果有多人，分析最突出的那一个。\n"
                "请评估其颜值并给出评分，分值范围为 0.0 到 10.0 。\n"
                "\n"
                "请严格遵守以下规则：\n"
                "1. 必须且只能返回合法的 JSON 格式数据。\n"
                "2. 不要包含 Markdown 格式标记（如 ```json ... ```）。\n"
                "3. 如果图片中没有人物或无法识别，请返回 {\"gender\": \"未知\", \"score\": 0.0}。\n"
                "JSON 格式示例：\n"
                "{\n"
                "  \"gender\": \"男\" 或 \"女\",\n"
                "  \"score\": 8.5\n"
                "}"
            )

            log("正在请求视觉模型 API...")
            response = await self.client.chat.completions.create(
                model=OPENAI_MODEL_NAME,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=3000,
                timeout=60.0 
            )

            # 增强容错处理
            if not response.choices or not response.choices[0].message:
                log("API 返回结构异常: choices 为空")
                return 0, "错误"

            content = response.choices[0].message.content
            
            if content is None:
                log(f"API 返回了空内容 (content is None)。结束原因: {response.choices[0].finish_reason}")
                # 尝试打印完整 response 以供调试
                # log(f"完整响应: {response}") 
                return 0, "错误"

            content = content.strip()
            log("API 响应成功")
            
            # 清理可能存在的 Markdown 代码块标记
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            
            content = content.strip()
            
            data = json.loads(content)
            return float(data.get("score", 0)), data.get("gender", "未知")
            
        except json.JSONDecodeError:
            log(f"解析模型响应失败，原始响应: {content}")
            return 0, "错误"
        except Exception as e:
            log(f"视觉分析请求失败: {e}")
            return 0, "错误"

    async def process_one_video(self, page):
        """处理单个视频的完整逻辑，包含超时控制"""
        # 1. 稍微移动鼠标保活
        await page.mouse.move(random.randint(100, 500), random.randint(100, 500))
        
        # 2. 定位视频容器
        # 常见选择器: [data-e2e="feed-active-video"] 或 xg-video-container
        video_container = page.locator('[data-e2e="feed-active-video"]')
        
        if await video_container.count() == 0:
            video_container = page.locator('video').first
        
        if await video_container.count() == 0:
            log("未找到视频元素")
            return

        # 3. 截图
        log("准备截图...")
        # 确保元素可见且稳定
        await video_container.scroll_into_view_if_needed(timeout=2000)
        screenshot = await video_container.screenshot(type='jpeg', quality=80, timeout=3000)
        
        # 4. 打分
        score, gender = await self.get_beauty_score(screenshot)
        log(f"分析结果: 性别={gender}, 颜值={score}")
        
        # 5. 决策
        target_gender_match = (self.gender == "全部") or (self.gender == gender)
        
        if score >= self.threshold and target_gender_match:
            log(f"[MATCH] 符合心动要求 (>{self.threshold})! 正在执行互动...")
            
            # 使用快捷键进行互动 (Z: 点赞, G: 关注)
            try:
                # 触发点赞 (如果 action 是 like 或 all)
                if self.action in ["like", "all"]:
                    await page.keyboard.press("z")
                    log("已发送点赞快捷键 [Z]")
                    await asyncio.sleep(0.5)
                
                # 触发关注 (如果 action 是 follow 或 all)
                if self.action in ["follow", "all"]:
                    await page.keyboard.press("g") 
                    log("已发送关注快捷键 [G]")
                    await asyncio.sleep(0.5)
            except Exception as e:
                log(f"快捷键操作失败: {e}")
        else:
            log("[SKIP] 不符合心动要求，跳过。")


    async def run(self):
        # 自动检测登录状态
        if not os.path.exists(self.auth_path):
            log(f"未检测到登录状态文件 ({self.auth_path})，即将启动登录流程...")
            log("请在弹出的浏览器中扫码登录，登录成功后脚本将自动继续。")
            
            login_script = os.path.join(self.current_dir, "login.py")
            try:
                # 使用当前相同的 Python 解释器调用登录脚本
                import subprocess
                subprocess.run([sys.executable, login_script], check=True)
                
                # 重新检查
                if not os.path.exists(self.auth_path):
                    log("错误: 登录流程未完成或未保存状态文件，程序退出。")
                    return
                log("登录成功！继续执行自动化任务...")
                
            except Exception as e:
                log(f"启动登录脚本失败: {e}")
                return

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.headless)
            try:
                context = await browser.new_context(storage_state=self.auth_path)
            except Exception as e:
                log(f"加载登录状态失败: {e}")
                log("尝试启动无状态模式（可能需要重新登录）...")
                context = await browser.new_context()

            page = await context.new_page()
            
            # 设置视口大小
            await page.set_viewport_size({"width": 1280, "height": 800})
            
            log("正在打开抖音...")
            # 放宽等待策略
            await page.goto("https://www.douyin.com/", wait_until="domcontentloaded", timeout=60000)
            
            log("页面已加载，等待弹窗处理...")
            await asyncio.sleep(5)

            # 尝试关闭各种常见弹窗
            popups = [
                '[class*="dy-account-close"]',       
                '.dy-account-close',                 
                '[data-e2e="close-icon"]',           
                '.login-close',                      
                '#login-pannel-close',               
            ]
            
            for selector in popups:
                try:
                    close_btn = page.locator(selector).first
                    if await close_btn.count() > 0 and await close_btn.is_visible():
                        log(f"检测到弹窗 ({selector})，正在关闭...")
                        await close_btn.click()
                        await asyncio.sleep(1)
                except Exception as e:
                    pass
            
            # 专门处理“我知道了”引导弹窗 (通过文本定位)
            try:
                guide_btn = page.get_by_role("button", name="我知道了").first
                if await guide_btn.count() > 0 and await guide_btn.is_visible():
                    log("检测到新手引导弹窗，点击'我知道了'...")
                    await guide_btn.click()
                    await asyncio.sleep(1)
            except Exception as e:
                pass

            count = 0
            while count < self.max_videos:
                count += 1
                log(f"\n--- 正在查看第 {count}/{self.max_videos} 个视频 ---")
                
                try:
                    # 随机等待视频播放
                    wait_time = random.uniform(2, 5)
                    await asyncio.sleep(wait_time)

                    # 设置单次循环的最大超时时间为 90 秒，防止死锁
                    await asyncio.wait_for(self.process_one_video(page), timeout=90.0)

                except asyncio.TimeoutError:
                    log("⚠️ 本次处理超时 (可能是API卡顿或元素未找到)，强制跳过...")
                except Exception as e:
                    log(f"⚠️ 处理过程发生未捕获错误: {e}")
                finally:
                    # 无论成功失败，必须翻页
                    log("切换到下一个视频...")
                    await page.keyboard.press("ArrowDown")
                
                # 休息策略
                if count % 10 == 0:
                    sleep_break = random.randint(5, 10)
                    log(f"已刷 10 个视频，休息 {sleep_break} 秒...")
                    await asyncio.sleep(sleep_break)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--threshold", type=float, default=8.0)
    parser.add_argument("--gender", type=str, default="全部")
    parser.add_argument("--max-videos", type=int, default=100)
    parser.add_argument("--action", type=str, default="all", choices=["like", "follow", "all"], help="互动行为: like, follow, all")
    args = parser.parse_args()

    bot = DouyinBot(threshold=args.threshold, gender=args.gender, max_videos=args.max_videos, action=args.action)
    asyncio.run(bot.run())
    