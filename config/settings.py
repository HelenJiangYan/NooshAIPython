"""
NooshAI测试框架全局配置
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent

# 测试环境配置
class TestConfig:
    """测试环境配置"""

    # 系统URL
    BASE_URL = os.getenv("BASE_URL", "https://nooshchat.qa2.noosh.com")
    AUTH_URL = os.getenv("AUTH_URL", "https://nooshauth.qa2.noosh.com/login")

    # 测试账号
    TEST_USERNAME = os.getenv("TEST_USERNAME", "dgo1g1mgr1")
    TEST_PASSWORD = os.getenv("TEST_PASSWORD", "noosh123")

    # 超时配置(毫秒)
    DEFAULT_TIMEOUT = int(os.getenv("DEFAULT_TIMEOUT", "30000"))
    PAGE_LOAD_TIMEOUT = int(os.getenv("PAGE_LOAD_TIMEOUT", "60000"))
    AI_RESPONSE_TIMEOUT = int(os.getenv("AI_RESPONSE_TIMEOUT", "120000"))

    # 浏览器配置
    BROWSER = os.getenv("BROWSER", "chromium")  # chromium, firefox, webkit
    HEADLESS = os.getenv("HEADLESS", "False").lower() == "true"
    SLOW_MO = int(os.getenv("SLOW_MO", "0"))  # 慢动作模式(ms)

    # 截图和录像配置
    SCREENSHOT_ON_FAILURE = os.getenv("SCREENSHOT_ON_FAILURE", "True").lower() == "true"
    VIDEO_ON_FAILURE = os.getenv("VIDEO_ON_FAILURE", "True").lower() == "true"
    TRACE_ON_FAILURE = os.getenv("TRACE_ON_FAILURE", "True").lower() == "true"

    # AI增强功能配置
    ENABLE_LLM_VALIDATION = os.getenv("ENABLE_LLM_VALIDATION", "True").lower() == "true"
    ENABLE_VISUAL_VALIDATION = os.getenv("ENABLE_VISUAL_VALIDATION", "True").lower() == "true"
    ENABLE_RAG = os.getenv("ENABLE_RAG", "True").lower() == "true"

    # LLM配置
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "anthropic")  # anthropic, openai
    LLM_MODEL = os.getenv("LLM_MODEL", "claude-sonnet-4-5-20250929")
    LLM_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

    # RAG配置
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    VECTOR_DB_PATH = BASE_DIR / "rag" / "vector_db"

    # 报告路径
    REPORTS_DIR = BASE_DIR / "reports"
    SCREENSHOTS_DIR = REPORTS_DIR / "screenshots"
    VIDEOS_DIR = REPORTS_DIR / "videos"
    ALLURE_DIR = REPORTS_DIR / "allure-results"
    LOGS_DIR = REPORTS_DIR / "logs"
    TRACES_DIR = REPORTS_DIR / "traces"
    HTML_DIR = REPORTS_DIR / "html"

class PlaywrightConfig:
    """Playwright浏览器配置"""

    # 浏览器启动参数
    BROWSER_ARGS = [
        "--disable-blink-features=AutomationControlled",
        "--disable-dev-shm-usage",
        "--no-sandbox",
        "--start-maximized",  # 最大化窗口
    ]

    # 浏览器上下文选项
    CONTEXT_OPTIONS = {
        "no_viewport": True,  # 禁用固定viewport，让浏览器窗口自适应
        "locale": "zh-CN",
        "timezone_id": "Asia/Shanghai",
        "permissions": ["clipboard-read", "clipboard-write"],
        "record_video_dir": str(TestConfig.VIDEOS_DIR) if TestConfig.VIDEO_ON_FAILURE else None,
    }

class MCPConfig:
    """MCP功能测试配置"""

    # 预期的MCP工具列表
    EXPECTED_TOOLS = [
        "read_file",
        "write_file",
        "list_directory",
        "search_files",
        "execute_command",
    ]

    # 预期的MCP资源类型
    EXPECTED_RESOURCES = [
        "file",
        "directory",
        "api",
    ]

    # MCP提示词模板
    PROMPTS_TO_TEST = [
        "code_review",
        "bug_analysis",
        "documentation",
    ]

# 创建必要的目录
def ensure_directories():
    """确保所有必要的目录存在"""
    directories = [
        TestConfig.REPORTS_DIR,
        TestConfig.SCREENSHOTS_DIR,
        TestConfig.VIDEOS_DIR,
        TestConfig.ALLURE_DIR,
        TestConfig.LOGS_DIR,
        TestConfig.TRACES_DIR,
        TestConfig.HTML_DIR,
        TestConfig.VECTOR_DB_PATH,
    ]

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)

# 初始化时创建目录
ensure_directories()
