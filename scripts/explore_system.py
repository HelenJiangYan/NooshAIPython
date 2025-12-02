"""
NooshAI系统探索脚本

自动登录并分析系统结构，识别页面元素，为测试框架提供元素定位器
"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from config.settings import TestConfig
import json
import time

def explore_nooshai_system():
    """
    探索NooshAI系统并记录发现

    步骤:
    1. 访问登录页并分析元素
    2. 执行登录
    3. 分析Chatbot主页面
    4. 测试发送消息
    5. 查找MCP相关功能
    6. 生成元素定位器报告
    """

    findings = {
        "url": TestConfig.BASE_URL,
        "auth_url": TestConfig.AUTH_URL,
        "elements": {},
        "features": [],
        "mcp_capabilities": [],
        "screenshots": []
    }

    print("=" * 60)
    print("NooshAI系统探索工具")
    print("=" * 60)

    with sync_playwright() as p:
        # 启动浏览器
        browser = p.chromium.launch(headless=False, slow_mo=1000)
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = context.new_page()

        try:
            # ========== 步骤1: 访问登录页 ==========
            print("\n[步骤1] 访问登录页...")
            page.goto(TestConfig.AUTH_URL, timeout=60000)
            time.sleep(2)

            screenshot_path = TestConfig.SCREENSHOTS_DIR / "01_login_page.png"
            page.screenshot(path=str(screenshot_path), full_page=True)
            findings["screenshots"].append(str(screenshot_path))
            print(f"[OK] 截图保存: {screenshot_path}")

            # 查找用户名输入框
            print("\n查找用户名输入框...")
            username_selectors = [
                "input[name='username']",
                "input[type='text']",
                "input[id*='username']",
                "input[placeholder*='username' i]",
                "input[placeholder*='用户' i]"
            ]

            for selector in username_selectors:
                try:
                    if page.is_visible(selector, timeout=2000):
                        print(f"✓ 找到用户名输入框: {selector}")
                        findings["elements"]["username_input"] = selector
                        page.fill(selector, TestConfig.TEST_USERNAME)
                        break
                except:
                    continue

            # 查找密码输入框
            print("查找密码输入框...")
            password_selectors = [
                "input[name='password']",
                "input[type='password']",
                "input[id*='password']"
            ]

            for selector in password_selectors:
                try:
                    if page.is_visible(selector, timeout=2000):
                        print(f"✓ 找到密码输入框: {selector}")
                        findings["elements"]["password_input"] = selector
                        page.fill(selector, TestConfig.TEST_PASSWORD)
                        break
                except:
                    continue

            # 查找登录按钮
            print("查找登录按钮...")
            login_button_selectors = [
                "button[type='submit']",
                "button:has-text('登录')",
                "button:has-text('Login')",
                "button:has-text('Sign In')",
                "input[type='submit']"
            ]

            for selector in login_button_selectors:
                try:
                    if page.is_visible(selector, timeout=2000):
                        print(f"✓ 找到登录按钮: {selector}")
                        findings["elements"]["login_button"] = selector
                        break
                except:
                    continue

            # ========== 步骤2: 执行登录 ==========
            print("\n[步骤2] 执行登录...")
            if "login_button" in findings["elements"]:
                page.click(findings["elements"]["login_button"])
                print("[OK] 已点击登录按钮")
            else:
                print("[WARN] 未找到登录按钮,尝试按Enter键")
                page.press(findings["elements"].get("password_input", "input[type='password']"), "Enter")

            # 等待登录完成
            print("等待登录完成...")
            time.sleep(5)

            screenshot_path = TestConfig.SCREENSHOTS_DIR / "02_after_login.png"
            page.screenshot(path=str(screenshot_path), full_page=True)
            findings["screenshots"].append(str(screenshot_path))

            current_url = page.url
            print(f"当前URL: {current_url}")
            findings["current_url_after_login"] = current_url

            if TestConfig.BASE_URL in current_url:
                print("[OK] 登录成功，已跳转到主系统")
                findings["features"].append("login_successful")
            else:
                print(f"[WARN] 可能未成功跳转，当前URL: {current_url}")

            # ========== 步骤3: 分析Chatbot主页面 ==========
            print("\n[步骤3] 分析Chatbot主页面...")

            # 查找聊天输入框
            print("查找聊天输入框...")
            chat_input_selectors = [
                "textarea[placeholder*='消息']",
                "textarea[placeholder*='message' i]",
                "input[type='text']",
                "textarea",
                "[contenteditable='true']",
                "textarea[placeholder*='type' i]"
            ]

            for selector in chat_input_selectors:
                try:
                    if page.is_visible(selector, timeout=3000):
                        print(f"✓ 找到聊天输入框: {selector}")
                        findings["elements"]["chat_input"] = selector
                        findings["features"].append("chat_input_found")
                        break
                except:
                    continue

            # 查找发送按钮
            print("查找发送按钮...")
            send_button_selectors = [
                "button[type='submit']",
                "button:has-text('发送')",
                "button:has-text('Send')",
                "[aria-label*='send' i]",
                "button svg",  # 可能是图标按钮
            ]

            for selector in send_button_selectors:
                try:
                    if page.is_visible(selector, timeout=2000):
                        print(f"✓ 找到发送按钮: {selector}")
                        findings["elements"]["send_button"] = selector
                        break
                except:
                    continue

            # 查找消息容器
            print("查找消息容器...")
            message_container_selectors = [
                ".messages",
                ".chat-messages",
                "[role='log']",
                ".conversation",
                ".message-list",
                "[class*='message']",
                "[class*='chat']"
            ]

            for selector in message_container_selectors:
                try:
                    if page.is_visible(selector, timeout=2000):
                        print(f"✓ 找到消息容器: {selector}")
                        findings["elements"]["message_container"] = selector
                        break
                except:
                    continue

            screenshot_path = TestConfig.SCREENSHOTS_DIR / "03_chatbot_page.png"
            page.screenshot(path=str(screenshot_path), full_page=True)
            findings["screenshots"].append(str(screenshot_path))

            # ========== 步骤4: 测试发送消息 ==========
            if "chat_input" in findings["elements"]:
                print("\n[步骤4] 测试发送消息...")

                try:
                    test_message = "你好，请介绍一下你自己"
                    page.fill(findings["elements"]["chat_input"], test_message)
                    print(f"✓ 已输入消息: {test_message}")

                    time.sleep(1)

                    if "send_button" in findings["elements"]:
                        page.click(findings["elements"]["send_button"])
                        print("✓ 已点击发送按钮")
                    else:
                        page.press(findings["elements"]["chat_input"], "Enter")
                        print("✓ 已按Enter键发送")

                    time.sleep(3)

                    screenshot_path = TestConfig.SCREENSHOTS_DIR / "04_message_sent.png"
                    page.screenshot(path=str(screenshot_path), full_page=True)
                    findings["screenshots"].append(str(screenshot_path))

                    # 等待AI响应
                    print("等待AI响应...")
                    time.sleep(10)

                    screenshot_path = TestConfig.SCREENSHOTS_DIR / "05_ai_response.png"
                    page.screenshot(path=str(screenshot_path), full_page=True)
                    findings["screenshots"].append(str(screenshot_path))

                    # 查找用户消息和AI响应元素
                    print("分析消息元素...")
                    user_message_selectors = [
                        ".user-message",
                        ".message.user",
                        "[data-role='user']",
                        "[class*='user']"
                    ]

                    for selector in user_message_selectors:
                        try:
                            count = page.locator(selector).count()
                            if count > 0:
                                print(f"✓ 找到用户消息元素: {selector} (数量: {count})")
                                findings["elements"]["user_message"] = selector
                                break
                        except:
                            continue

                    ai_message_selectors = [
                        ".ai-message",
                        ".assistant-message",
                        "[data-role='assistant']",
                        ".bot-message",
                        "[class*='assistant']",
                        "[class*='bot']"
                    ]

                    for selector in ai_message_selectors:
                        try:
                            count = page.locator(selector).count()
                            if count > 0:
                                print(f"✓ 找到AI消息元素: {selector} (数量: {count})")
                                findings["elements"]["ai_message"] = selector
                                findings["features"].append("ai_response_received")
                                break
                        except:
                            continue

                except Exception as e:
                    print(f"[WARN] 发送消息时出错: {e}")

            # ========== 步骤5: 查找MCP相关功能 ==========
            print("\n[步骤5] 查找MCP功能...")

            mcp_indicators = [
                "[data-panel='tools']",
                ".tools-panel",
                ".mcp-tools",
                "[aria-label*='tools' i]",
                "[class*='tool']",
                "[class*='mcp']"
            ]

            for selector in mcp_indicators:
                try:
                    if page.is_visible(selector, timeout=2000):
                        print(f"✓ 找到MCP相关元素: {selector}")
                        findings["mcp_capabilities"].append(selector)
                except:
                    continue

            # 检查页面文本内容
            try:
                page_text = page.inner_text("body")
                if "tool" in page_text.lower():
                    print("✓ 页面内容包含'tool'关键词")
                    findings["features"].append("tool_keyword_found")
                if "mcp" in page_text.lower():
                    print("✓ 页面内容包含'mcp'关键词")
                    findings["features"].append("mcp_keyword_found")
            except Exception as e:
                print(f"[WARN] 分析页面文本时出错: {e}")

            # 获取页面信息
            findings["page_title"] = page.title()
            findings["final_url"] = page.url

            print(f"\n页面标题: {findings['page_title']}")
            print(f"最终URL: {findings['final_url']}")

        except Exception as e:
            print(f"\n[ERROR] 探索过程中出错: {e}")
            screenshot_path = TestConfig.SCREENSHOTS_DIR / "error.png"
            page.screenshot(path=str(screenshot_path), full_page=True)
            findings["error"] = str(e)

        finally:
            browser.close()

    # ========== 保存探索结果 ==========
    output_file = TestConfig.REPORTS_DIR / "system_exploration.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(findings, f, indent=2, ensure_ascii=False)

    # ========== 打印总结 ==========
    print("\n" + "=" * 60)
    print("探索完成！")
    print("=" * 60)

    print(f"\n[FILE] 报告保存至: {output_file}")

    print(f"\n[SCREENSHOT] 截图保存至: {TestConfig.SCREENSHOTS_DIR}")
    for screenshot in findings["screenshots"]:
        print(f"   - {Path(screenshot).name}")

    print(f"\n[SEARCH] 发现的页面元素:")
    for key, value in findings["elements"].items():
        print(f"   {key:25} → {value}")

    print(f"\n[DONE] 发现的功能:")
    for feature in findings["features"]:
        print(f"   ✓ {feature}")

    if findings["mcp_capabilities"]:
        print(f"\n[TOOL] MCP功能指标:")
        for indicator in findings["mcp_capabilities"]:
            print(f"   ✓ {indicator}")
    else:
        print(f"\n[WARN] 未发现明显的MCP功能元素(可能需要发送特定消息触发)")

    print("\n" + "=" * 60)
    print("💡 下一步:")
    print("1. 查看截图确认页面结构")
    print("2. 根据发现的元素更新页面对象类")
    print("3. 创建.env文件(复制.env.example)")
    print("4. 运行第一个测试: pytest tests/test_authentication/test_login.py -v")
    print("=" * 60)

    return findings

if __name__ == "__main__":
    explore_nooshai_system()
