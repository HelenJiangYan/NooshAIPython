"""
Chatbot主页面对象 - 使用 User-facing Locators
"""
from pages.base_page import BasePage
from typing import List, Dict, Optional
from config.settings import TestConfig
from utils.logger import test_logger as logger
from playwright.sync_api import Locator
import time
import re

class ChatbotPage(BasePage):
    """
    Chatbot主页面对象

    封装Chatbot页面的所有交互操作，包括发送消息、接收响应、MCP工具调用等
    使用 Playwright 推荐的 User-facing locators 优先定位元素
    """

    def __init__(self, page):
        """
        初始化Chatbot页面对象

        Args:
            page: Playwright Page对象
        """
        super().__init__(page)
        self.url = TestConfig.BASE_URL

    # ========== User-facing Locators (推荐) ==========

    @property
    def chat_input(self) -> Locator:
        """聊天输入框 - 使用 placeholder 或 role='textbox'"""
        return (
            self.get_by_placeholder(re.compile(r"消息|message", re.I))
            .or_(self.get_by_role("textbox"))
            .or_(self.locator("textarea, input[type='text']"))
            .first
        )

    @property
    def send_button(self) -> Locator:
        """发送按钮 - 使用 role='button' 和文本"""
        return (
            self.get_by_role("button", name=re.compile(r"发送|send", re.I))
            .or_(self.get_by_text(re.compile(r"^(发送|Send)$", re.I)))
            .or_(self.locator("button[type='submit']"))
            .first
        )

    @property
    def message_container(self) -> Locator:
        """消息容器 - 使用 role='log' 或 role='list'"""
        return (
            self.get_by_role("log")
            .or_(self.get_by_role("list"))
            .or_(self.locator(".messages, .chat-messages"))
        )

    @property
    def user_messages(self) -> Locator:
        """
        用户消息列表

        实际DOM结构:
        <div class="group rounded-3xl px-5 py-3 shadow-sm bg-primary-100 dark:bg-primary-900/40 ...">
            <p>user message text</p>
        </div>
        """
        return self.locator("div.rounded-3xl.bg-primary-100, div.rounded-3xl[class*='bg-primary']")

    @property
    def ai_messages(self) -> Locator:
        """
        AI消息列表

        实际DOM结构:
        <div class="group w-full py-6 px-4 ...">
            <div class="max-w-5xl mx-auto">
                <div class="space-y-2">
                    <div class="text-gray-800 dark:text-gray-200">
                        <div class="markdown-content text-[15px] leading-7">
                            <p>AI message text</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        """
        return self.locator("div.markdown-content")

    @property
    def loading_indicator(self) -> Locator:
        """加载指示器 - 使用 role='status' 或 aria-label"""
        return (
            self.get_by_role("status")
            .or_(self.locator("[aria-label*='loading' i], [aria-label*='加载']"))
            .or_(self.locator(".loading, .typing-indicator, .spinner"))
        )

    @property
    def new_chat_button(self) -> Locator:
        """新对话按钮 - 使用 role='button' 和文本"""
        return self.get_by_role("button", name=re.compile(r"新对话|new chat|new conversation", re.I))

    @property
    def clear_chat_button(self) -> Locator:
        """清空按钮 - 使用 role='button' 和文本"""
        return self.get_by_role("button", name=re.compile(r"清空|clear", re.I))

    @property
    def chat_history(self) -> Locator:
        """聊天历史 - 使用 role='navigation'"""
        return (
            self.get_by_role("navigation")
            .or_(self.locator("[aria-label*='history' i]"))
            .or_(self.locator(".chat-history, .conversation-list"))
        )

    @property
    def mcp_tools_panel(self) -> Locator:
        """MCP工具面板 - 使用 role='region'"""
        return (
            self.get_by_role("region", name=re.compile(r"tools", re.I))
            .or_(self.locator("[data-panel='tools'], .tools-panel"))
        )

    @property
    def mcp_tool_items(self) -> Locator:
        """MCP工具项列表 - 使用 role='listitem'"""
        return (
            self.get_by_role("listitem")
            .or_(self.locator("[data-type='tool'], .tool-item"))
        )

    @property
    def tool_invocation_log(self) -> Locator:
        """工具调用日志 - 使用 role='log'"""
        return (
            self.get_by_role("log")
            .or_(self.locator("[aria-label*='tool output' i]"))
            .or_(self.locator(".tool-log, .mcp-log"))
        )

    def navigate_to_chatbot(self):
        """导航到Chatbot页面"""
        logger.info("导航到Chatbot页面")
        self.navigate(self.url)
        self.wait_for_load_state("domcontentloaded")

    def navigate_to_ai_assistant_from_dashboard(self):
        """
        从Dashboard导航到AI Assistant页面

        步骤:
        1. 等待Dashboard页面加载
        2. 点击左侧菜单的 "AI Assistant"
        """
        logger.info("从Dashboard导航到AI Assistant...")

        try:
            # 等待页面DOM加载完成 (不等待networkidle,因为AI Assistant有持续的WebSocket连接)
            self.wait_for_load_state("domcontentloaded", timeout=10000)

            # 等待侧边栏加载
            self.page.wait_for_timeout(1000)

            # 方法1: 使用href属性查找AI Assistant链接
            ai_assistant_link = self.page.locator("a[href='/workspace/chatbot']")

            if ai_assistant_link.count() > 0:
                logger.info(f"找到 {ai_assistant_link.count()} 个AI Assistant链接")
                # 优先选择可见的链接（桌面版侧边栏）
                visible_link = ai_assistant_link.first
                logger.info("点击 AI Assistant 链接...")
                visible_link.click()

                # 等待URL变化
                self.page.wait_for_url("**/workspace/chatbot", timeout=10000)
                logger.info("✅ 已导航到 AI Assistant 页面")

                # 等待连接完成
                self.wait_for_ai_connection()
                return

            # 方法2: 使用文本查找
            logger.info("尝试通过文本查找 AI Assistant 链接...")
            text_link = self.page.get_by_role("link").filter(has_text=re.compile(r"AI Assistant", re.I)).first

            if text_link.is_visible(timeout=5000):
                logger.info("找到 AI Assistant 文本链接，点击...")
                text_link.click()
                self.page.wait_for_url("**/workspace/chatbot", timeout=10000)
                logger.info("✅ 已导航到 AI Assistant 页面")
                self.wait_for_ai_connection()
                return

            # 方法3: 直接导航到 AI Assistant URL
            logger.warning("未找到 AI Assistant 菜单项，尝试直接导航...")
            self.navigate(self.url)
            self.page.wait_for_url("**/workspace/chatbot", timeout=10000)
            logger.info("✅ 已通过URL导航到 AI Assistant 页面")
            # 等待连接完成
            self.wait_for_ai_connection()

        except Exception as e:
            logger.error(f"导航到 AI Assistant 失败: {e}")
            raise

    def wait_for_ai_connection(self, timeout: int = 30000):
        """
        等待AI Assistant连接完成

        Args:
            timeout: 超时时间(毫秒)
        """
        logger.info("等待 AI Assistant 连接完成...")

        try:
            # 方法1: 等待 "Connecting..." 文本消失
            connecting_text = self.get_by_text(re.compile(r"Connecting", re.I))
            if self.is_visible(connecting_text, timeout=5000):
                logger.info("检测到 'Connecting...' 状态，等待连接完成...")
                self.wait_for_locator(connecting_text, state="hidden", timeout=timeout)
                logger.info("'Connecting...' 已消失")

            # 方法2: 等待输入框可用
            logger.info("等待聊天输入框可用...")
            start_time = time.time()
            while time.time() - start_time < timeout / 1000:
                if self.is_chat_input_enabled():
                    logger.info("✅ 聊天输入框已可用，连接完成")
                    return
                time.sleep(0.5)

            # 如果超时，记录警告但不抛出异常
            logger.warning(f"等待输入框可用超时 ({timeout}ms)，但将继续执行")

        except Exception as e:
            logger.warning(f"等待AI连接时出现异常: {e}，将继续执行")
            # 不抛出异常，让测试继续

    def send_message(self, message: str, wait_for_response: bool = True):
        """
        发送消息

        Args:
            message: 要发送的消息内容
            wait_for_response: 是否等待AI响应
        """
        logger.info(f"📤 发送消息: {message}")

        # 记录发送前的AI消息数量
        message_count_before = self.ai_messages.count()
        logger.info(f"发送前AI消息数量: {message_count_before}")

        # 等待输入框可用
        self.wait_for_locator(self.chat_input)

        # 输入消息
        self.fill(self.chat_input, message)

        # 点击发送按钮或按Enter键
        if self.is_visible(self.send_button, timeout=2000):
            self.click(self.send_button)
        else:
            # 如果没有发送按钮，尝试按Enter键
            self.press_key(self.chat_input, "Enter")

        # 短暂等待消息发送
        time.sleep(0.5)

        if wait_for_response:
            self.wait_for_ai_response(initial_count=message_count_before)

    def wait_for_ai_response(self, initial_count: int = 0, timeout: Optional[int] = None):
        """
        等待AI响应完成

        参考 TypeScript 版本实现：检测内容长度变化而不是消息数量

        Args:
            initial_count: 发送消息前的AI消息数量（保留兼容性）
            timeout: 超时时间(毫秒)，默认使用AI_RESPONSE_TIMEOUT
        """
        timeout = timeout or TestConfig.AI_RESPONSE_TIMEOUT
        logger.info("⏳ 等待AI响应...")

        try:
            # Step 1: 短暂等待消息发送
            time.sleep(1)

            # Step 2: 获取初始聊天区域内容
            chat_area = self.page.locator("main, [role='main'], .chat-area, .conversation-area").first
            initial_content = chat_area.text_content() or ""
            initial_length = len(initial_content)
            logger.info(f"📏 初始内容长度: {initial_length}")

            initial_message_count = self.ai_messages.count()
            logger.info(f"📝 初始消息数: {initial_message_count}")

            # Step 3: 循环检测加载指示器（最多5秒）
            logger.info("🔍 检查加载指示器...")
            dots_indicator = self.page.locator("text='...'")
            loading_detected = False
            loading_type = None

            check_interval = 0.3  # 每300ms检查一次
            max_checks = 17  # 约5秒

            for i in range(max_checks):
                dots_visible = self.is_visible(dots_indicator, timeout=100)
                spinner_visible = self.is_visible(self.loading_indicator, timeout=100)

                if dots_visible:
                    loading_detected = True
                    loading_type = "dots"
                    logger.info("✓ 检测到点状加载指示器")
                    break
                elif spinner_visible:
                    loading_detected = True
                    loading_type = "spinner"
                    logger.info("✓ 检测到旋转加载指示器")
                    break

                time.sleep(check_interval)

            # Step 4: 如果检测到加载指示器，等待其消失
            if loading_detected:
                indicator = dots_indicator if loading_type == "dots" else self.loading_indicator
                try:
                    self.wait_for_locator(indicator, state="hidden", timeout=int(timeout * 0.8))
                    logger.info(f"✓ {loading_type}加载指示器已消失")
                except:
                    logger.warning(f"⚠️  {loading_type}加载指示器未在超时内消失")
                # 额外等待内容渲染
                time.sleep(1)
            else:
                logger.info("ℹ️  未检测到加载指示器（可能响应很快）")

            # Step 5: 等待内容长度真正增加
            logger.info("⏳ 等待内容变化（新响应到达）...")
            start_time = time.time()
            max_wait_time = timeout / 1000
            content_changed = False

            while time.time() - start_time < max_wait_time:
                time.sleep(1.5)  # 每1.5秒检查一次

                current_content = chat_area.text_content() or ""
                current_length = len(current_content)
                current_message_count = self.ai_messages.count()

                # 检查内容是否显著增加（至少30个字符）
                length_increased = current_length > initial_length + 30
                message_count_increased = current_message_count > initial_message_count

                if length_increased or message_count_increased:
                    logger.info(f"✓ 检测到内容变化: {initial_length} → {current_length} (+{current_length - initial_length} 字符, 消息: {initial_message_count} → {current_message_count})")
                    content_changed = True
                    break

                elapsed = int(time.time() - start_time)
                logger.info(f"⏳ 继续等待... ({current_length} 字符, {current_message_count} 消息, {elapsed}s)")

            if not content_changed:
                logger.warning(f"⚠️  {int(max_wait_time)}秒内未检测到明显的内容变化")

            # Step 6: 额外等待确保内容稳定
            time.sleep(2)
            logger.info("✓ 响应等待完成")

        except Exception as e:
            logger.warning(f"⚠️  等待响应时出错: {e}")
            logger.info("使用备用等待策略...")
            time.sleep(10)

    def get_last_ai_message(self) -> str:
        """
        获取最后一条AI消息

        参考 TypeScript 版本：从整个聊天区域获取文本并过滤掉greeting消息

        Returns:
            str: AI消息内容
        """
        try:
            # 方法1: 从整个聊天区域获取文本（与TypeScript版本一致）
            chat_area = self.page.locator("main, [role='main'], .chat-area, .conversation-area").first
            all_text = chat_area.text_content() or ""

            if all_text and len(all_text) > 0:
                # 清理文本：移除UI文本和静态欢迎消息
                cleaned = all_text
                # 移除输入提示
                cleaned = cleaned.replace("Type your message...", "")
                cleaned = cleaned.replace("Press Enter to send", "")
                # 移除greeting消息
                cleaned = cleaned.replace("Welcome to Noosh AI! I'm here to assist you. How can I help you today?", "")
                # 移除时间戳
                cleaned = cleaned.replace("Just now", "|||")
                cleaned = cleaned.strip()

                logger.info(f"📨 获取最后AI消息（前200字符）: {cleaned[:200]}...")
                return cleaned

        except Exception as e:
            logger.warning(f"⚠️  从聊天区域获取消息失败: {e}")

        # 方法2: 回退到使用消息定位器
        try:
            messages = self.get_all(self.ai_messages)
            logger.info(f"发现 {len(messages)} 条AI消息")

            if messages:
                last_message = messages[-1]
                content = last_message.text_content() or ""
                logger.info(f"📨 获取最后AI消息: {content[:100]}...")
                return content
            else:
                logger.warning("未找到AI消息")
                return ""
        except Exception as e:
            logger.error(f"获取AI消息失败: {e}")
            return ""

    def get_last_user_message(self) -> str:
        """
        获取最后一条用户消息

        Returns:
            str: 用户消息内容
        """
        try:
            messages = self.get_all(self.user_messages)
            if messages:
                last_message = messages[-1]
                content = last_message.text_content() or ""
                logger.info(f"👤 获取最后用户消息: {content}")
                return content
            else:
                logger.warning("未找到用户消息")
                return ""
        except Exception as e:
            logger.error(f"获取用户消息失败: {e}")
            return ""

    def get_all_messages(self) -> List[Dict[str, str]]:
        """
        获取所有消息

        Returns:
            List[Dict]: 消息列表 [{"role": "user/assistant", "content": "..."}]
        """
        messages = []

        try:
            # 获取所有用户消息
            user_elements = self.get_all(self.user_messages)
            for elem in user_elements:
                messages.append({
                    "role": "user",
                    "content": elem.text_content() or ""
                })

            # 获取所有AI消息
            ai_elements = self.get_all(self.ai_messages)
            for elem in ai_elements:
                messages.append({
                    "role": "assistant",
                    "content": elem.text_content() or ""
                })

            logger.info(f"获取到 {len(messages)} 条消息")
        except Exception as e:
            logger.error(f"获取所有消息失败: {e}")

        return messages

    def get_message_count(self) -> int:
        """
        获取消息总数

        Returns:
            int: 消息总数
        """
        user_count = self.get_count(self.user_messages)
        ai_count = self.get_count(self.ai_messages)
        total = user_count + ai_count
        logger.info(f"消息总数: {total} (用户: {user_count}, AI: {ai_count})")
        return total

    def clear_chat(self):
        """清空当前对话"""
        logger.info("清空对话")

        if self.is_visible(self.clear_chat_button, timeout=2000):
            self.click(self.clear_chat_button)
        elif self.is_visible(self.new_chat_button, timeout=2000):
            self.click(self.new_chat_button)
        else:
            logger.warning("未找到清空/新对话按钮")

    def is_chat_input_enabled(self) -> bool:
        """
        检查输入框是否可用

        Returns:
            bool: 可用返回True
        """
        return self.is_enabled(self.chat_input)

    def is_chat_input_visible(self) -> bool:
        """
        检查输入框是否可见

        Returns:
            bool: 可见返回True
        """
        return self.is_visible(self.chat_input, timeout=5000)

    # ========== MCP相关方法 ==========

    def is_mcp_tools_panel_visible(self) -> bool:
        """
        检查MCP工具面板是否可见

        Returns:
            bool: 可见返回True
        """
        is_visible = self.is_visible(self.mcp_tools_panel, timeout=2000)
        logger.info(f"MCP工具面板可见性: {is_visible}")
        return is_visible

    def get_available_tools(self) -> List[str]:
        """
        获取可用的MCP工具列表

        Returns:
            List[str]: 工具名称列表
        """
        tools = []

        if self.is_mcp_tools_panel_visible():
            try:
                tool_elements = self.get_all(self.mcp_tool_items)
                for tool in tool_elements:
                    tool_name = tool.text_content() or ""
                    if tool_name:
                        tools.append(tool_name.strip())

                logger.info(f"发现 {len(tools)} 个MCP工具: {tools}")
            except Exception as e:
                logger.error(f"获取MCP工具列表失败: {e}")
        else:
            logger.warning("MCP工具面板不可见")

        return tools

    def check_tool_invocation(self, tool_name: str) -> bool:
        """
        检查工具是否被调用

        Args:
            tool_name: 工具名称

        Returns:
            bool: 工具被调用返回True
        """
        if self.is_visible(self.tool_invocation_log, timeout=2000):
            try:
                log_text = self.get_text(self.tool_invocation_log)
                is_invoked = tool_name in log_text
                logger.info(f"工具 {tool_name} 调用状态: {is_invoked}")
                return is_invoked
            except Exception as e:
                logger.error(f"检查工具调用失败: {e}")
                return False
        else:
            # 如果没有工具日志面板，检查AI响应中是否提到工具
            ai_response = self.get_last_ai_message()
            is_mentioned = tool_name in ai_response
            logger.info(f"AI响应中提到工具 {tool_name}: {is_mentioned}")
            return is_mentioned

    # ========== 辅助方法 ==========

    def wait_for_message_count(self, expected_count: int, timeout: int = 10000):
        """
        等待消息数量达到预期值

        Args:
            expected_count: 预期的消息数量
            timeout: 超时时间(毫秒)
        """
        logger.info(f"等待消息数量达到: {expected_count}")
        start_time = time.time()

        while time.time() - start_time < timeout / 1000:
            if self.get_message_count() >= expected_count:
                logger.info(f"✅ 消息数量已达到 {expected_count}")
                return
            time.sleep(0.5)

        logger.warning(f"⚠️ 超时: 消息数量未达到 {expected_count}")

    def get_chat_history_items(self) -> List[str]:
        """
        获取聊天历史列表

        Returns:
            List[str]: 历史会话列表
        """
        history_items = []

        if self.is_visible(self.chat_history, timeout=2000):
            try:
                # 获取历史面板中的所有子项
                items = self.chat_history.locator("> *").all()
                for item in items:
                    text = item.text_content() or ""
                    if text:
                        history_items.append(text.strip())

                logger.info(f"发现 {len(history_items)} 个历史会话")
            except Exception as e:
                logger.error(f"获取聊天历史失败: {e}")

        return history_items
