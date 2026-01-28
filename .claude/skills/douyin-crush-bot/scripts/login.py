import asyncio
import os
import time
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        # 确保路径存在
        auth_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(auth_dir)
        auth_path = os.path.join(parent_dir, "auth.json")
        
        print("正在启动浏览器...")
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        
        page = await context.new_page()
        await page.goto("https://www.douyin.com/")
        
        print("\n" + "="*50)
        print("请在弹出的浏览器窗口中完成扫码登录。")
        print("脚本正在后台检测 Cookie 变化 (查找 sessionid)...")
        print("="*50 + "\n")
        
        # 轮询检测登录状态
        start_time = time.time()
        max_wait = 300  # 5分钟超时
        logged_in = False

        while time.time() - start_time < max_wait:
            cookies = await context.cookies()
            # 检查是否存在 sessionid，这是抖音登录的关键凭证
            session_cookie = next((c for c in cookies if c['name'] == 'sessionid'), None)
            
            if session_cookie:
                print(f"检测到 sessionid！登录成功。")
                print("等待 3 秒以确保状态完全加载...")
                await asyncio.sleep(3)
                
                # 保存 Storage State
                await context.storage_state(path=auth_path)
                print(f"✅ 状态已保存至: {auth_path}")
                logged_in = True
                break
            
            # 同时也尝试检测 UI (作为双重保障，或者给用户的视觉反馈)
            # 尝试查找通常只有登录后才有的元素，不做强阻塞
            try:
                # 比如“消息”图标，“个人头像”等
                # 注意：这里仅作尝试，不依赖它退出循环
                if await page.locator(".avatar-component-avatar-container").count() > 0:
                    pass 
            except:
                pass

            await asyncio.sleep(2)
        
        if not logged_in:
            print("❌ 登录超时，未检测到 sessionid。")

        print("正在关闭浏览器...")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())