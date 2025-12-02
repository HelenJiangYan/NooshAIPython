"""
Pytest全局配置和Fixtures

提供浏览器、页面对象、认证等全局fixture
"""
import pytest
from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page, Playwright
from pathlib import Path
from datetime import datetime
import json
from typing import Generator

from config.settings import TestConfig, PlaywrightConfig
from pages.login_page import LoginPage
from pages.chatbot_page import ChatbotPage
from utils.logger import test_logger as logger

# ============ Playwright Fixtures ============

@pytest.fixture(scope="session")
def playwright() -> Generator[Playwright, None, None]:
    """
    Playwright实例 (session级别)

    整个测试会话共享一个Playwright实例
    """
    with sync_playwright() as p:
        yield p

@pytest.fixture(scope="session")
def browser_type_launch_args() -> dict:
    """
    浏览器启动参数

    Returns:
        dict: 浏览器启动配置
    """
    return {
        "headless": TestConfig.HEADLESS,
        "slow_mo": TestConfig.SLOW_MO,
        "args": PlaywrightConfig.BROWSER_ARGS,
    }

@pytest.fixture(scope="session")
def browser_context_args() -> dict:
    """
    浏览器上下文参数

    Returns:
        dict: 浏览器上下文配置
    """
    return PlaywrightConfig.CONTEXT_OPTIONS

@pytest.fixture(scope="session")
def browser(playwright: Playwright, browser_type_launch_args: dict) -> Generator[Browser, None, None]:
    """
    浏览器实例 (session级别)

    整个测试会话共享一个浏览器实例，提高执行效率

    Args:
        playwright: Playwright实例
        browser_type_launch_args: 浏览器启动参数

    Yields:
        Browser: 浏览器实例
    """
    logger.info(f"启动浏览器: {TestConfig.BROWSER}")
    browser_type = getattr(playwright, TestConfig.BROWSER)
    browser = browser_type.launch(**browser_type_launch_args)
    yield browser
    logger.info("关闭浏览器")
    browser.close()

@pytest.fixture(scope="function")
def context(browser: Browser, browser_context_args: dict) -> Generator[BrowserContext, None, None]:
    """
    浏览器上下文 (function级别)

    每个测试函数都有独立的浏览器上下文，确保测试隔离

    Args:
        browser: 浏览器实例
        browser_context_args: 上下文参数

    Yields:
        BrowserContext: 浏览器上下文
    """
    # 禁用浏览器自动填充,确保测试隔离
    context_args = browser_context_args.copy()
    context_args['ignore_https_errors'] = True

    context = browser.new_context(**context_args)

    # 启用trace（失败时保存）
    if TestConfig.TRACE_ON_FAILURE:
        context.tracing.start(screenshots=True, snapshots=True, sources=True)

    yield context

    # 保存trace
    if TestConfig.TRACE_ON_FAILURE:
        trace_path = TestConfig.TRACES_DIR / f"trace_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        trace_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            context.tracing.stop(path=str(trace_path))
        except Exception as e:
            logger.warning(f"保存trace失败: {e}")

    context.close()

@pytest.fixture(scope="function")
def page(context: BrowserContext) -> Generator[Page, None, None]:
    """
    页面实例 (function级别)

    每个测试函数都有独立的页面实例

    Args:
        context: 浏览器上下文

    Yields:
        Page: 页面实例
    """
    page = context.new_page()

    # 设置默认超时
    page.set_default_timeout(TestConfig.DEFAULT_TIMEOUT)

    # 设置页面加载超时
    page.set_default_navigation_timeout(TestConfig.PAGE_LOAD_TIMEOUT)

    logger.info("创建新页面实例")
    yield page

    logger.info("关闭页面实例")
    page.close()

# ============ 页面对象 Fixtures ============

@pytest.fixture(scope="function")
def login_page(page: Page) -> LoginPage:
    """
    登录页面对象

    Args:
        page: 页面实例

    Returns:
        LoginPage: 登录页面对象
    """
    return LoginPage(page)

@pytest.fixture(scope="function")
def chatbot_page(page: Page) -> ChatbotPage:
    """
    Chatbot页面对象

    Args:
        page: 页面实例

    Returns:
        ChatbotPage: Chatbot页面对象
    """
    return ChatbotPage(page)

# ============ 认证 Fixtures ============

@pytest.fixture(scope="function")
def authenticated_page(page: Page, login_page: LoginPage, chatbot_page: ChatbotPage) -> ChatbotPage:
    """
    已认证的页面 (自动登录)

    自动完成登录流程，返回已登录的ChatbotPage对象
    适用于需要登录后才能测试的场景

    Args:
        page: 页面实例
        login_page: 登录页面对象
        chatbot_page: Chatbot页面对象

    Returns:
        ChatbotPage: 已登录的Chatbot页面对象
    """
    logger.info("执行自动登录...")

    # 导航到登录页
    login_page.navigate_to_login()

    # 执行登录
    login_page.login()

    # 验证登录成功
    if not login_page.is_login_successful():
        # 截图保存失败状态
        screenshot_path = TestConfig.SCREENSHOTS_DIR / f"login_failed_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        page.screenshot(path=str(screenshot_path))
        pytest.fail(f"自动登录失败，截图已保存: {screenshot_path}")

    logger.info("✅ 登录成功，现在导航到 AI Assistant...")

    # 从Dashboard导航到AI Assistant页面
    try:
        chatbot_page.navigate_to_ai_assistant_from_dashboard()
    except Exception as e:
        logger.error(f"导航到 AI Assistant 失败: {e}")
        # 截图保存失败状态
        screenshot_path = TestConfig.SCREENSHOTS_DIR / f"nav_to_ai_assistant_failed_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        page.screenshot(path=str(screenshot_path))
        pytest.fail(f"导航到 AI Assistant 失败，截图已保存: {screenshot_path}\n错误: {e}")

    logger.info("✅ 已成功导航到 AI Assistant 页面")
    return chatbot_page

# ============ 测试数据 Fixtures ============

@pytest.fixture(scope="session")
def test_messages() -> dict:
    """
    加载测试消息数据

    Returns:
        dict: 测试消息数据
    """
    data_file = TestConfig.BASE_DIR / "data" / "test_messages.json"

    if data_file.exists():
        with open(data_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    # 默认测试消息
    return {
        "basic": [
            "你好",
            "今天天气怎么样?",
            "帮我写一段Python代码"
        ],
        "mcp": [
            "帮我读取文件",
            "列出当前目录",
            "执行命令ls"
        ],
        "complex": [
            "分析这段代码的性能问题",
            "设计一个用户认证系统"
        ]
    }

@pytest.fixture(scope="session")
def mcp_test_cases() -> list:
    """
    加载MCP测试用例

    Returns:
        list: MCP测试用例列表
    """
    data_file = TestConfig.BASE_DIR / "data" / "mcp_test_cases.json"

    if data_file.exists():
        with open(data_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    return []

# ============ AI增强 Fixtures ============

@pytest.fixture(scope="session")
def llm_validator():
    """
    LLM验证器 (用于验证AI响应质量)

    仅在启用LLM验证时返回验证器实例

    Returns:
        LLMValidator or None: LLM验证器
    """
    if TestConfig.ENABLE_LLM_VALIDATION and TestConfig.LLM_API_KEY:
        try:
            from ai_enhanced.llm_validator import LLMValidator
            return LLMValidator(
                provider=TestConfig.LLM_PROVIDER,
                model=TestConfig.LLM_MODEL,
                api_key=TestConfig.LLM_API_KEY
            )
        except Exception as e:
            logger.warning(f"初始化LLM验证器失败: {e}")
            return None
    return None

# ============ 钩子函数 ============

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    测试报告钩子 - 失败时自动截图

    在测试失败时自动截取页面截图并保存

    Args:
        item: 测试项
        call: 测试调用信息
    """
    outcome = yield
    report = outcome.get_result()

    # 只在测试执行阶段(call)且失败时处理
    if report.when == "call" and report.failed:
        # 尝试获取page fixture
        page = None
        for fixture_name in item.funcargs:
            if "page" in fixture_name.lower():
                potential_page = item.funcargs[fixture_name]
                # 检查是否是Page对象
                if hasattr(potential_page, 'screenshot'):
                    page = potential_page
                    break

        if page and TestConfig.SCREENSHOT_ON_FAILURE:
            # 生成截图文件名
            test_name = item.nodeid.replace("::", "_").replace("/", "_")
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            screenshot_name = f"FAILED_{test_name}_{timestamp}"
            screenshot_path = TestConfig.SCREENSHOTS_DIR / f"{screenshot_name}.png"

            try:
                page.screenshot(path=str(screenshot_path), full_page=True)
                logger.error(f"测试失败截图: {screenshot_path}")

                # 附加到Allure报告
                try:
                    import allure
                    allure.attach.file(
                        str(screenshot_path),
                        name=f"失败截图_{timestamp}",
                        attachment_type=allure.attachment_type.PNG
                    )
                except ImportError:
                    pass

            except Exception as e:
                logger.error(f"截图失败: {e}")

def pytest_configure(config):
    """
    Pytest配置钩子

    在测试运行前执行的配置操作

    Args:
        config: Pytest配置对象
    """
    # 创建必要的目录
    TestConfig.REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    TestConfig.SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    TestConfig.VIDEOS_DIR.mkdir(parents=True, exist_ok=True)
    TestConfig.ALLURE_DIR.mkdir(parents=True, exist_ok=True)
    TestConfig.LOGS_DIR.mkdir(parents=True, exist_ok=True)
    TestConfig.TRACES_DIR.mkdir(parents=True, exist_ok=True)

    # 注册自定义标记（已在pytest.ini中定义，这里是补充）
    logger.info("Pytest配置完成")

def pytest_collection_modifyitems(config, items):
    """
    修改收集到的测试项

    可以在这里添加标记、修改测试顺序等

    Args:
        config: Pytest配置对象
        items: 收集到的测试项列表
    """
    for item in items:
        # 为包含"login"的测试自动添加login标记
        if "login" in item.nodeid.lower():
            item.add_marker(pytest.mark.login)

        # 为包含"chatbot"的测试自动添加chatbot标记
        if "chatbot" in item.nodeid.lower():
            item.add_marker(pytest.mark.chatbot)

        # 为包含"mcp"的测试自动添加mcp标记
        if "mcp" in item.nodeid.lower():
            item.add_marker(pytest.mark.mcp)

def pytest_sessionstart(session):
    """
    测试会话开始时执行

    Args:
        session: Pytest会话对象
    """
    logger.info("=" * 60)
    logger.info("NooshAI 自动化测试开始")
    logger.info(f"测试环境: {TestConfig.BASE_URL}")
    logger.info(f"浏览器: {TestConfig.BROWSER}")
    logger.info(f"Headless模式: {TestConfig.HEADLESS}")
    logger.info("=" * 60)

def pytest_sessionfinish(session, exitstatus):
    """
    测试会话结束时执行

    Args:
        session: Pytest会话对象
        exitstatus: 退出状态码
    """
    logger.info("=" * 60)
    logger.info("NooshAI 自动化测试完成")
    logger.info(f"退出状态: {exitstatus}")
    logger.info(f"报告目录: {TestConfig.REPORTS_DIR}")
    logger.info("=" * 60)
