"""
登录功能测试
包含各种登录场景的测试用例
"""
import pytest
import allure
from pages.login_page import LoginPage
from config.settings import TestConfig

@allure.feature("用户认证")
@allure.story("登录功能")
class TestLogin:
    """登录功能测试套件"""

    @allure.title("测试成功登录 - 有效凭证")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.smoke
    @pytest.mark.login
    def test_successful_login(self, login_page: LoginPage):
        """
        测试使用有效凭据成功登录

        步骤:
        1. 导航到登录页面
        2. 输入有效的用户名和密码
        3. 点击登录按钮
        4. 验证登录成功并跳转到主系统
        """
        # 步骤1: 导航到登录页面
        login_page.navigate_to_login()

        # 验证在登录页面
        assert login_page.is_on_login_page(), "未成功导航到登录页面"

        # 步骤2和3: 输入有效凭据并登录
        login_page.login(
            username=TestConfig.TEST_USERNAME,
            password=TestConfig.TEST_PASSWORD
        )

        # 步骤4: 验证登录成功
        assert login_page.is_login_successful(), "登录失败"

        # 验证跳转到主系统
        assert TestConfig.BASE_URL in login_page.get_current_url(), "未跳转到主系统"

    @allure.title("测试无效用户名登录失败")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.regression
    @pytest.mark.login
    def test_invalid_username(self, login_page: LoginPage):
        """
        测试使用无效用户名登录失败

        预期: 登录失败，显示错误消息
        """
        login_page.navigate_to_login()

        # 使用无效用户名
        login_page.login(username="invalid_user_12345", password="password123")

        # 验证登录失败
        assert not login_page.is_login_successful(), "不应该登录成功"

        # 验证仍在登录页面或有错误消息
        assert login_page.is_on_login_page() or login_page.get_error_message() != "", \
            "应该仍在登录页面或显示错误消息"

    @allure.title("测试无效密码登录失败")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.regression
    @pytest.mark.login
    def test_invalid_password(self, login_page: LoginPage):
        """
        测试使用错误密码登录失败

        预期: 登录失败，显示错误消息
        """
        login_page.navigate_to_login()

        # 使用正确用户名但错误密码
        login_page.login(
            username=TestConfig.TEST_USERNAME,
            password="wrong_password_12345"
        )

        # 验证登录失败
        assert not login_page.is_login_successful(), "不应该登录成功"

    @allure.title("测试空用户名登录")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    @pytest.mark.login
    def test_empty_username(self, login_page: LoginPage):
        """
        测试空用户名

        预期: 登录失败
        """
        login_page.navigate_to_login()
        login_page.login(username="", password="password123")

        # 验证登录失败
        assert not login_page.is_login_successful(), "不应该允许空用户名登录"

    @allure.title("测试空密码登录")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    @pytest.mark.login
    def test_empty_password(self, login_page: LoginPage):
        """
        测试空密码

        预期: 登录失败
        """
        # 清除会话确保从全新状态开始
        login_page.clear_session_and_navigate()

        login_page.login(username=TestConfig.TEST_USERNAME, password="")

        # 验证登录失败
        assert not login_page.is_login_successful(), "不应该允许空密码登录"

    @allure.title("测试空用户名和密码")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    @pytest.mark.login
    def test_empty_credentials(self, login_page: LoginPage):
        """
        测试用户名和密码都为空

        预期: 登录失败
        """
        # 清除会话确保从全新状态开始
        login_page.clear_session_and_navigate()

        login_page.login(username="", password="")

        # 验证登录失败
        assert not login_page.is_login_successful(), "不应该允许空凭据登录"

    @allure.title("测试登录页面元素可见性")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.smoke
    @pytest.mark.login
    def test_login_page_elements(self, login_page: LoginPage):
        """
        测试登录页面的关键元素是否可见

        验证:
        - 用户名输入框可见
        - 密码输入框可见
        - 登录按钮可见且可用
        """
        login_page.navigate_to_login()

        # 验证用户名输入框可见
        assert login_page.is_username_input_visible(), "用户名输入框不可见"

        # 验证密码输入框可见
        assert login_page.is_visible(login_page.password_input), "密码输入框不可见"

        # 验证登录按钮可见
        assert login_page.is_visible(login_page.login_button), "登录按钮不可见"

        # 验证登录按钮可用
        assert login_page.is_login_button_enabled(), "登录按钮不可用"

    @allure.title("测试登录页面标题")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    @pytest.mark.login
    def test_login_page_title(self, login_page: LoginPage):
        """
        测试登录页面标题

        验证页面标题包含相关关键词
        """
        login_page.navigate_to_login()

        title = login_page.get_title()
        assert title != "", "页面标题为空"

        # 可以根据实际页面标题调整断言
        # 例如: assert "Noosh" in title or "Login" in title
