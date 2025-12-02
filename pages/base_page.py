"""
基础页面对象类
所有页面对象的父类，提供通用的页面操作方法
"""
from playwright.sync_api import Page, Locator
from typing import Optional, List, Any, Literal, Union
from pathlib import Path
from config.settings import TestConfig
from utils.logger import test_logger as logger
import re

class BasePage:
    """
    基础页面类

    所有页面对象都应继承此类
    提供通用的页面操作方法和等待策略

    设计原则:
    - 基础操作方法(click, fill等)只接受Locator,保持简单高效
    - 各页面通过@property返回Locator对象,在页面层处理定位逻辑
    - 提供Locator构建辅助方法(get_by_role, get_by_text等)
    """

    def __init__(self, page: Page):
        """
        初始化页面对象

        Args:
            page: Playwright Page对象
        """
        self.page = page
        self.timeout = TestConfig.DEFAULT_TIMEOUT

    # ========== Locator 构建方法 (用于页面层) ==========

    def get_by_role(self, role: str, **kwargs) -> Locator:
        """
        通过 ARIA role 获取元素 (最推荐)

        Args:
            role: ARIA role (button, textbox, link, etc.)
            **kwargs: 其他选项 (name, exact, disabled, etc.)

        Returns:
            Locator: 元素定位器

        Examples:
            @property
            def login_button(self):
                return self.get_by_role("button", name="Login")
        """
        return self.page.get_by_role(role, **kwargs)

    def get_by_text(self, text: Union[str, re.Pattern], **kwargs) -> Locator:
        """
        通过可见文本获取元素

        Args:
            text: 文本内容或正则表达式
            **kwargs: 其他选项 (exact=True/False)

        Returns:
            Locator: 元素定位器
        """
        return self.page.get_by_text(text, **kwargs)

    def get_by_label(self, text: Union[str, re.Pattern], **kwargs) -> Locator:
        """
        通过 label 文本获取关联的表单元素

        Args:
            text: label 文本或正则表达式
            **kwargs: 其他选项

        Returns:
            Locator: 元素定位器
        """
        return self.page.get_by_label(text, **kwargs)

    def get_by_placeholder(self, text: Union[str, re.Pattern], **kwargs) -> Locator:
        """
        通过 placeholder 获取输入框

        Args:
            text: placeholder 文本或正则表达式
            **kwargs: 其他选项

        Returns:
            Locator: 元素定位器
        """
        return self.page.get_by_placeholder(text, **kwargs)

    def get_by_alt_text(self, text: Union[str, re.Pattern], **kwargs) -> Locator:
        """
        通过 alt 属性获取图片

        Args:
            text: alt 文本或正则表达式
            **kwargs: 其他选项

        Returns:
            Locator: 元素定位器
        """
        return self.page.get_by_alt_text(text, **kwargs)

    def get_by_title(self, text: Union[str, re.Pattern], **kwargs) -> Locator:
        """
        通过 title 属性获取元素

        Args:
            text: title 文本或正则表达式
            **kwargs: 其他选项

        Returns:
            Locator: 元素定位器
        """
        return self.page.get_by_title(text, **kwargs)

    def get_by_test_id(self, test_id: str) -> Locator:
        """
        通过 data-testid 获取元素

        Args:
            test_id: test id 值

        Returns:
            Locator: 元素定位器
        """
        return self.page.get_by_test_id(test_id)

    def locator(self, selector: str, **kwargs) -> Locator:
        """
        通过 CSS selector 获取元素

        Args:
            selector: CSS 选择器
            **kwargs: 其他选项

        Returns:
            Locator: 元素定位器

        Examples:
            @property
            def username_input(self):
                return self.locator("input[name='username']")
        """
        return self.page.locator(selector, **kwargs)

    # ========== 基础操作方法 (只接受 Locator) ==========

    def navigate(self, url: str):
        """
        导航到指定URL

        Args:
            url: 目标URL
        """
        logger.info(f"导航到: {url}")
        self.page.goto(url, wait_until="domcontentloaded")

    def click(self, locator: Locator, **kwargs):
        """
        点击元素

        Args:
            locator: Locator 对象
            **kwargs: Playwright click 选项

        Examples:
            self.click(self.login_button)
            self.click(self.submit_btn, force=True)
        """
        if 'delay' not in kwargs:
            kwargs['delay'] = 0

        logger.info("点击元素 (Locator)")
        locator.click(**kwargs)

    def fill(self, locator: Locator, value: str, **kwargs):
        """
        填充输入框

        Args:
            locator: Locator 对象
            value: 要填充的值
            **kwargs: Playwright fill 选项 (force, timeout, no_wait_after)

        Examples:
            self.fill(self.username_input, "admin")
            self.fill(self.password_input, "secret", force=True)
        """
        # 默认不等待后续操作完成，提高速度
        if 'no_wait_after' not in kwargs:
            kwargs['no_wait_after'] = True

        logger.info(f"填充 (Locator): {value}")
        locator.fill(value, **kwargs)

    def type_text(self, locator: Locator, text: str, delay: float = 0, **kwargs):
        """
        逐字输入文本（模拟真实打字）

        Args:
            locator: Locator 对象
            text: 要输入的文本
            delay: 每个字符之间的延迟(毫秒)，0表示无延迟
            **kwargs: Playwright type 选项

        Examples:
            self.type_text(self.search_input, "hello", delay=100)
        """
        logger.info(f"输入文本: {text}")
        locator.type(text, delay=delay, **kwargs)

    def clear(self, locator: Locator):
        """
        清除输入框

        Args:
            locator: Locator 对象

        Examples:
            self.clear(self.username_input)
        """
        logger.info("清除输入框")
        locator.clear()

    def get_text(self, locator: Locator) -> str:
        """
        获取元素文本内容

        Args:
            locator: Locator 对象

        Returns:
            str: 元素文本

        Examples:
            text = self.get_text(self.error_message)
        """
        return locator.text_content(timeout=self.timeout) or ""

    def get_value(self, locator: Locator) -> str:
        """
        获取输入框的值

        Args:
            locator: Locator 对象

        Returns:
            str: 输入框的值
        """
        return locator.input_value(timeout=self.timeout)

    def is_visible(self, locator: Locator, timeout: int = 5000) -> bool:
        """
        检查元素是否可见

        Args:
            locator: Locator 对象
            timeout: 超时时间(毫秒)

        Returns:
            bool: 元素可见返回True

        Examples:
            if self.is_visible(self.error_message):
                print("发现错误消息")
        """
        try:
            return locator.is_visible(timeout=timeout)
        except:
            return False

    def is_enabled(self, locator: Locator, timeout: int = 5000) -> bool:
        """
        检查元素是否可用

        Args:
            locator: Locator 对象
            timeout: 超时时间(毫秒)

        Returns:
            bool: 元素可用返回True
        """
        try:
            return locator.is_enabled(timeout=timeout)
        except:
            return False

    def is_checked(self, locator: Locator) -> bool:
        """
        检查复选框/单选框是否选中

        Args:
            locator: Locator 对象

        Returns:
            bool: 选中返回True
        """
        try:
            return locator.is_checked(timeout=5000)
        except:
            return False

    def wait_for_locator(
        self,
        locator: Locator,
        state: Literal["attached", "detached", "visible", "hidden"] = "visible",
        timeout: Optional[int] = None
    ):
        """
        等待 Locator 元素达到指定状态

        Args:
            locator: Locator 对象
            state: 等待状态 (visible, hidden, attached, detached)
            timeout: 超时时间(毫秒)

        Examples:
            self.wait_for_locator(self.loading_spinner, state="hidden")
            self.wait_for_locator(self.submit_button, state="visible")
        """
        timeout = timeout or self.timeout
        logger.info(f"等待 Locator 元素 (状态: {state})")
        locator.wait_for(state=state, timeout=timeout)

    def get_all(self, locator: Locator) -> List[Locator]:
        """
        获取所有匹配的元素

        Args:
            locator: Locator 对象

        Returns:
            List[Locator]: 元素列表

        Examples:
            messages = self.get_all(self.message_items)
            for msg in messages:
                print(self.get_text(msg))
        """
        return locator.all()

    def get_count(self, locator: Locator) -> int:
        """
        获取匹配元素的数量

        Args:
            locator: Locator 对象

        Returns:
            int: 元素数量

        Examples:
            count = self.get_count(self.error_messages)
        """
        return locator.count()

    def press_key(self, locator: Locator, key: str):
        """
        在元素上按键

        Args:
            locator: Locator 对象
            key: 按键名称 (Enter, Tab, Escape等)

        Examples:
            self.press_key(self.search_input, "Enter")
        """
        logger.info(f"按键: {key}")
        locator.press(key)

    def hover(self, locator: Locator, **kwargs):
        """
        鼠标悬停在元素上

        Args:
            locator: Locator 对象
            **kwargs: Playwright hover 选项
        """
        logger.info("鼠标悬停")
        locator.hover(**kwargs)

    def select_option(self, locator: Locator, value: Union[str, List[str]], **kwargs):
        """
        选择下拉框选项

        Args:
            locator: Locator 对象(select元素)
            value: 选项值或值列表
            **kwargs: Playwright select_option 选项

        Examples:
            self.select_option(self.country_select, "USA")
            self.select_option(self.languages_select, ["en", "zh"])
        """
        logger.info(f"选择选项: {value}")
        locator.select_option(value, **kwargs)

    def check(self, locator: Locator, **kwargs):
        """
        勾选复选框

        Args:
            locator: Locator 对象(checkbox)
            **kwargs: Playwright check 选项
        """
        logger.info("勾选复选框")
        locator.check(**kwargs)

    def uncheck(self, locator: Locator, **kwargs):
        """
        取消勾选复选框

        Args:
            locator: Locator 对象(checkbox)
            **kwargs: Playwright uncheck 选项
        """
        logger.info("取消勾选复选框")
        locator.uncheck(**kwargs)

    def get_attribute(self, locator: Locator, name: str) -> Optional[str]:
        """
        获取元素属性值

        Args:
            locator: Locator 对象
            name: 属性名

        Returns:
            Optional[str]: 属性值
        """
        return locator.get_attribute(name, timeout=self.timeout)

    # ========== 页面级操作方法 ==========

    def wait_for_url(self, url_pattern: str, timeout: Optional[int] = None):
        """
        等待URL变化

        Args:
            url_pattern: URL模式(支持glob或正则)
            timeout: 超时时间(毫秒)
        """
        timeout = timeout or self.timeout
        logger.info(f"等待URL匹配: {url_pattern}")
        self.page.wait_for_url(url_pattern, timeout=timeout)

    def wait_for_load_state(
        self,
        state: Literal["load", "domcontentloaded", "networkidle"] = "networkidle",
        timeout: Optional[int] = None
    ):
        """
        等待页面加载状态

        Args:
            state: 加载状态 (load, domcontentloaded, networkidle)
            timeout: 超时时间(毫秒)
        """
        timeout = timeout or TestConfig.PAGE_LOAD_TIMEOUT
        logger.info(f"等待页面加载状态: {state}")
        self.page.wait_for_load_state(state, timeout=timeout)

    def take_screenshot(self, name: str, full_page: bool = True) -> Path:
        """
        截图

        Args:
            name: 截图文件名
            full_page: 是否全页面截图

        Returns:
            Path: 截图文件路径
        """
        screenshot_path = TestConfig.SCREENSHOTS_DIR / f"{name}.png"
        screenshot_path.parent.mkdir(parents=True, exist_ok=True)
        self.page.screenshot(path=str(screenshot_path), full_page=full_page)
        logger.info(f"截图保存至: {screenshot_path}")
        return screenshot_path

    def get_current_url(self) -> str:
        """
        获取当前URL

        Returns:
            str: 当前页面URL
        """
        return self.page.url

    def get_title(self) -> str:
        """
        获取页面标题

        Returns:
            str: 页面标题
        """
        return self.page.title()

    def reload(self):
        """刷新页面"""
        logger.info("刷新页面")
        self.page.reload()

    def go_back(self):
        """返回上一页"""
        logger.info("返回上一页")
        self.page.go_back()

    # ========== JavaScript 执行 ==========

    def execute_script(self, script: str, *args: Any) -> Any:
        """
        执行JavaScript代码

        Args:
            script: JavaScript代码
            *args: 传递给JavaScript的参数

        Returns:
            Any: JavaScript执行结果
        """
        return self.page.evaluate(script, *args)

    def scroll_to_element(self, locator: Locator):
        """
        滚动到元素位置

        Args:
            locator: Locator 对象
        """
        logger.info("滚动到元素")
        locator.scroll_into_view_if_needed()

    # ========== Local Storage 操作 ==========

    def get_local_storage(self, key: str) -> Optional[str]:
        """
        获取localStorage值

        Args:
            key: localStorage键名

        Returns:
            Optional[str]: localStorage值
        """
        result = self.page.evaluate(f"localStorage.getItem('{key}')")
        return str(result) if result is not None else None

    def set_local_storage(self, key: str, value: str):
        """
        设置localStorage值

        Args:
            key: localStorage键名
            value: 要设置的值
        """
        self.page.evaluate(f"localStorage.setItem('{key}', '{value}')")

    def clear_local_storage(self):
        """清除localStorage"""
        self.page.evaluate("localStorage.clear()")
        logger.info("已清除localStorage")
