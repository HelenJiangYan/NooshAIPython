"""
登录页面对象 - 使用 User-facing Locators
"""
from pages.base_page import BasePage
from config.settings import TestConfig
from utils.logger import test_logger as logger
from playwright.sync_api import Locator
import re

class LoginPage(BasePage):
    """
    登录页面对象

    封装登录页面的所有交互操作
    使用 Playwright 推荐的 User-facing locators 优先定位元素
    """

    def __init__(self, page):
        """
        初始化登录页面对象

        Args:
            page: Playwright Page对象
        """
        super().__init__(page)
        self.url = TestConfig.AUTH_URL

    # ========== User-facing Locators (推荐) ==========

    @property
    def username_input(self) -> Locator:
        """用户名输入框 - 使用 placeholder 或 label (实际是 User ID)"""
        return (
            self.get_by_placeholder(re.compile(r"user id|username|用户名", re.I))
            .or_(self.get_by_label(re.compile(r"user id|username|用户名", re.I)))
            .or_(self.locator("input[placeholder*='User ID' i]"))
            .first
        )

    @property
    def password_input(self) -> Locator:
        """密码输入框 - 使用 placeholder 或 label"""
        return (
            self.get_by_placeholder(re.compile(r"password|密码", re.I))
            .or_(self.get_by_label(re.compile(r"password|密码", re.I)))
            .or_(self.locator("input[type='password']"))
            .first
        )

    @property
    def login_button(self) -> Locator:
        """登录按钮 - 使用 role 和文本"""
        return (
            self.get_by_role("button", name=re.compile(r"登录|login|sign in", re.I))
            .or_(self.get_by_text(re.compile(r"^(登录|Login|Sign In)$", re.I)))
            .or_(self.locator("button[type='submit']"))
            .first
        )

    @property
    def error_message(self) -> Locator:
        """错误消息 - 使用 role='alert'"""
        return self.get_by_role("alert").or_(self.locator(".error-message, .alert-danger"))

    @property
    def forgot_password_link(self) -> Locator:
        """忘记密码链接 - 使用 role='link' 和文本"""
        return self.get_by_role("link", name=re.compile(r"忘记密码|forgot password", re.I))

    @property
    def remember_me_checkbox(self) -> Locator:
        """记住我复选框 - 使用 role='checkbox'"""
        return self.get_by_role("checkbox", name=re.compile(r"remember", re.I))

    @property
    def cookie_accept_button(self) -> Locator:
        """Cookie 同意按钮 - 使用文本"""
        return self.get_by_text(re.compile(r"Accept All|Accept|同意", re.I)).and_(self.get_by_role("button"))

    @property
    def cookie_banner(self) -> Locator:
        """Cookie 横幅 - 使用 role='dialog'"""
        return self.get_by_role("dialog").or_(self.get_by_text(re.compile(r"cookie|privacy", re.I)))

    def navigate_to_login(self):
        """导航到登录页面"""
        logger.info("导航到登录页面")
        self.navigate(self.url)

        # 等待登录表单可见（减少超时时间）
        self.wait_for_locator(self.username_input, timeout=5000)
        logger.info("登录表单已就绪")

        # 处理Cookie同意弹窗
        self.handle_cookie_consent()

    def handle_cookie_consent(self):
        """处理Cookie同意弹窗"""
        try:
            if self.is_visible(self.cookie_accept_button, timeout=1000):
                logger.info("发现Cookie同意弹窗,点击接受")
                self.click(self.cookie_accept_button)
                # 等待弹窗消失
                try:
                    self.wait_for_locator(self.cookie_accept_button, state="hidden", timeout=1000)
                    logger.info("Cookie弹窗已关闭")
                except:
                    logger.debug("Cookie弹窗可能已关闭")
        except Exception as e:
            logger.debug(f"没有Cookie弹窗或已处理: {str(e)}")

    def login(self, username: str | None = None, password: str | None = None, remember_me: bool = False):
        """
        执行登录操作

        Args:
            username: 用户名 (默认使用配置中的测试账号)
            password: 密码 (默认使用配置中的测试密码)
            remember_me: 是否记住密码
        """
        actual_username = username if username is not None else TestConfig.TEST_USERNAME
        actual_password = password if password is not None else TestConfig.TEST_PASSWORD

        logger.info(f"使用账号登录: {actual_username}")

        # 快速填写用户名 - fill() 会自动清除旧值
        self.fill(self.username_input, actual_username, force=True)

        # 快速填写密码 - fill() 会自动清除旧值
        self.fill(self.password_input, actual_password, force=True)

        # 记住密码选项
        if remember_me and self.is_visible(self.remember_me_checkbox, timeout=2000):
            self.click(self.remember_me_checkbox)

        # 点击登录按钮
        self.click(self.login_button)

        logger.info("已提交登录表单，等待响应...")

    def is_login_successful(self, timeout: int = 30000) -> bool:
        """
        检查登录是否成功

        Args:
            timeout: 超时时间(毫秒)

        Returns:
            bool: 登录成功返回True
        """
        try:
            logger.info("等待登录处理和页面跳转...")

            # 方法1: 等待URL变化离开登录页面
            try:
                # 等待URL变化,不再包含 'login'
                logger.info("等待URL变化...")
                self.page.wait_for_url(lambda url: "login" not in url.lower(), timeout=timeout)
                logger.info(f"URL已变化,当前URL: {self.page.url}")
            except Exception as url_wait_error:
                logger.warning(f"等待URL变化超时: {str(url_wait_error)}")
                # URL没有变化,可能仍在登录页面
                current_url = self.page.url
                logger.info(f"当前URL: {current_url}")

                if "login" in current_url.lower():
                    logger.error(f"登录失败 - 仍在登录页面: {current_url}")
                    # 检查是否有错误消息
                    if self.is_visible(self.ERROR_MESSAGE, timeout=2000):
                        error_msg = self.get_error_message()
                        logger.error(f"登录错误消息: {error_msg}")
                    return False

            # 方法2: 等待页面基本加载即可,不需要等待networkidle
            logger.info("等待页面加载完成...")
            try:
                self.page.wait_for_load_state("domcontentloaded", timeout=5000)
                logger.info("页面加载完成(domcontentloaded)")
            except:
                logger.warning("等待页面加载超时,继续验证")

            # 检查最终URL
            final_url = self.page.url
            logger.info(f"登录后最终URL: {final_url}")

            # 如果不在登录页面,说明登录成功
            if "login" not in final_url.lower():
                logger.info(f"[OK] 登录成功 - 已离开登录页面: {final_url}")

                # 如果不在目标页面,尝试导航到目标页面
                if TestConfig.BASE_URL not in final_url:
                    logger.info(f"尝试导航到目标页面: {TestConfig.BASE_URL}")
                    try:
                        self.page.goto(TestConfig.BASE_URL, wait_until="load", timeout=30000)
                        logger.info(f"导航后URL: {self.page.url}")
                    except Exception as nav_error:
                        logger.warning(f"导航到目标页面失败: {str(nav_error)}")

                return True
            else:
                logger.error(f"登录失败 - 仍在登录页面: {final_url}")
                return False

        except Exception as e:
            logger.error(f"[ERROR] 登录验证失败: {str(e)}")
            return False

    def get_error_message(self) -> str:
        """
        获取错误消息

        Returns:
            str: 错误消息文本
        """
        if self.is_visible(self.error_message, timeout=2000):
            error_text = self.get_text(self.error_message)
            logger.warning(f"发现错误消息: {error_text}")
            return error_text
        return ""

    def is_on_login_page(self) -> bool:
        """
        检查是否在登录页面

        Returns:
            bool: 在登录页面返回True
        """
        current_url = self.get_current_url()
        is_on_page = self.url in current_url
        logger.info(f"当前URL: {current_url}, 是否在登录页: {is_on_page}")
        return is_on_page

    def is_username_input_visible(self) -> bool:
        """
        检查用户名输入框是否可见

        Returns:
            bool: 可见返回True
        """
        return self.is_visible(self.username_input, timeout=5000)

    def is_login_button_enabled(self) -> bool:
        """
        检查登录按钮是否可用

        Returns:
            bool: 可用返回True
        """
        return self.is_enabled(self.login_button)

    def click_forgot_password(self):
        """点击忘记密码链接"""
        if self.is_visible(self.forgot_password_link, timeout=2000):
            logger.info("点击忘记密码链接")
            self.click(self.forgot_password_link)
        else:
            logger.warning("未找到忘记密码链接")

    def clear_form(self):
        """清空登录表单"""
        logger.info("清空登录表单")
        self.fill(self.username_input, "")
        self.fill(self.password_input, "")

    def clear_session_and_navigate(self):
        """
        清除所有会话状态并导航到登录页

        用于确保测试从全新状态开始
        """
        logger.info("清除浏览器会话状态...")

        # 清除所有cookies
        try:
            self.page.context.clear_cookies()
            logger.info("✓ 已清除所有cookies")
        except Exception as e:
            logger.warning(f"清除cookies失败: {e}")

        # 清除本地存储和会话存储
        try:
            self.page.evaluate("() => { localStorage.clear(); sessionStorage.clear(); }")
            logger.info("✓ 已清除本地存储和会话存储")
        except Exception as e:
            logger.warning(f"清除存储失败: {e}")

        # 导航到登录页
        self.navigate_to_login()
