# NooshAI Chatbot 自动化测试框架

基于 **Python + Pytest + Playwright + LLM/RAG** 的智能化自动化测试框架，专门为 NooshAI Chatbot 系统设计。

## 🎯 项目特点

- ✅ **现代化技术栈**: Python 3.11+ + Pytest + Playwright
- ✅ **POM设计模式**: 清晰的页面对象模型，易于维护
- ✅ **AI增强功能**: 集成LLM进行响应验证和测试生成
- ✅ **RAG知识库**: 智能存储和检索测试知识
- ✅ **完整报告**: Allure精美报告 + HTML报告
- ✅ **并行执行**: 支持多进程并行运行，提升效率
- ✅ **自动截图**: 失败时自动截图和录像
- ✅ **CI/CD就绪**: 可轻松集成到CI/CD流水线

## 📁 项目结构

```
intelligent-test-framework/
├── config/                    # 配置文件
│   ├── settings.py           # 全局配置
│   └── __init__.py
├── pages/                     # 页面对象模型 (POM)
│   ├── base_page.py          # 基础页面类
│   ├── login_page.py         # 登录页面
│   ├── chatbot_page.py       # Chatbot主页面
│   └── __init__.py
├── tests/                     # 测试用例
│   ├── test_authentication/  # 认证测试
│   │   └── test_login.py
│   ├── test_chatbot/         # Chatbot测试
│   │   └── test_basic_chat.py
│   ├── test_mcp/            # MCP功能测试
│   ├── test_integration/     # 集成测试
│   └── test_performance/     # 性能测试
├── utils/                     # 工具类
│   ├── logger.py             # 日志工具
│   └── __init__.py
├── ai_enhanced/              # AI增强功能
│   ├── llm_validator.py      # LLM响应验证
│   ├── test_generator.py     # AI测试生成
│   └── knowledge_rag.py      # RAG知识库
├── rag/                      # RAG数据
│   └── data/                 # 知识库数据
├── scripts/                  # 辅助脚本
│   └── explore_system.py     # 系统探索脚本
├── reports/                  # 测试报告
│   ├── screenshots/          # 截图
│   ├── videos/               # 录像
│   ├── allure-results/       # Allure报告
│   └── logs/                 # 日志
├── data/                     # 测试数据
├── venv/                     # Python虚拟环境 (已配置)
├── conftest.py              # Pytest全局配置
├── pytest.ini               # Pytest配置文件
├── requirements.txt         # 依赖包
├── .env.example            # 环境变量示例
├── .gitignore              # Git忽略文件
├── activate.bat            # 激活虚拟环境脚本 (Windows)
└── README.md               # 项目文档
```

## 🚀 快速开始

### 1. 环境准备

**前置条件:**
- Python 3.11 或更高版本
- pip 包管理器

### 2. 激活虚拟环境

项目已配置好虚拟环境，直接激活即可：

```bash
# Windows - 使用便捷脚本
activate.bat

# 或手动激活
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

激活后，命令行前面会显示 `(venv)`，表示虚拟环境已激活。

### 3. 安装依赖

```bash
# 安装Python依赖包
pip install -r requirements.txt

# 安装Playwright浏览器
playwright install chromium

# (可选) 安装Firefox和WebKit
playwright install firefox webkit
```

> **注意**: 如果虚拟环境不存在，可以创建新的：
> ```bash
> python -m venv venv
> ```

### 4. 配置环境

```bash
# 复制环境变量示例文件
copy .env.example .env

# 编辑.env文件，填入实际配置
# - 测试环境URL
# - 测试账号密码
# - API密钥(如果需要AI功能)
```

**.env 文件配置示例:**
```ini
# 测试环境
BASE_URL=https://nooshchat.qa2.noosh.com
AUTH_URL=https://nooshauth.qa2.noosh.com/login

# 测试账号
TEST_USERNAME=your_username
TEST_PASSWORD=your_password

# 浏览器配置
BROWSER=chromium
HEADLESS=False

# AI功能 (可选)
ANTHROPIC_API_KEY=your_api_key_here
```

### 5. 探索系统

首次使用时，运行系统探索脚本来识别页面元素：

```bash
python scripts/explore_system.py
```

这个脚本会:
- 自动登录系统
- 分析页面结构
- 识别元素定位器
- 生成截图和报告
- 保存结果到 `reports/system_exploration.json`

### 6. 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_authentication/test_login.py -v

# 运行冒烟测试
pytest -m smoke -v

# 运行回归测试
pytest -m regression -v

# 并行执行测试 (加速)
pytest -n auto

# 生成Allure报告
pytest --alluredir=reports/allure-results
allure serve reports/allure-results
```

### 7. VSCode 调试 (推荐)

本项目已配置完整的 VSCode 调试支持，可以直接在代码上打断点调试！

**快速开始:**
1. 打开测试文件 (如 `test_login.py`)
2. 在代码行号左侧点击，添加红色断点 ⭕
3. 按 **F5** 键
4. 选择 `Pytest: 调试当前文件`

**详细文档:**
- 📖 [完整调试指南](DEBUG_GUIDE.md) - 详细的调试教程和技巧
- 🚀 [快速参考卡片](QUICK_DEBUG.md) - 常用调试快捷键

**可用的调试配置:**
- `Pytest: 调试当前文件` - 调试打开的测试文件
- `Pytest: 调试登录测试` - 快速调试登录测试
- `Pytest: 有界面调试` - 显示浏览器窗口，可视化执行
- `Pytest: 调试失败的测试` - 只调试上次失败的测试

## 📊 测试报告

### HTML报告

测试完成后，HTML报告自动生成在 `reports/html/report.html`

### Allure报告

```bash
# 生成并查看Allure报告
allure serve reports/allure-results
```

## 🎨 编写测试用例

### 基础测试示例

```python
import pytest
from pages.chatbot_page import ChatbotPage

def test_send_message(authenticated_page):
    """测试发送消息"""
    chatbot = authenticated_page

    # 发送消息
    chatbot.send_message("你好")

    # 验证收到响应
    response = chatbot.get_last_ai_message()
    assert response != "", "应该收到AI响应"
```

### 使用Allure标记

```python
import allure

@allure.feature("Chatbot功能")
@allure.story("基础对话")
@allure.severity(allure.severity_level.CRITICAL)
def test_conversation(authenticated_page):
    with allure.step("发送消息"):
        authenticated_page.send_message("测试")

    with allure.step("验证响应"):
        response = authenticated_page.get_last_ai_message()
        assert response != ""
```

## 🧪 测试分类

使用 Pytest 标记来分类和选择测试:

- `@pytest.mark.smoke` - 冒烟测试 (核心功能)
- `@pytest.mark.regression` - 回归测试 (全面测试)
- `@pytest.mark.mcp` - MCP功能测试
- `@pytest.mark.ai` - AI增强测试
- `@pytest.mark.slow` - 慢速测试
- `@pytest.mark.login` - 登录相关测试
- `@pytest.mark.chatbot` - Chatbot功能测试

运行特定标记的测试:

```bash
pytest -m "smoke and not slow" -v
pytest -m chatbot -v
```

## 🔧 配置选项

### 浏览器配置

在 `.env` 文件中配置:

```ini
# 浏览器类型: chromium, firefox, webkit
BROWSER=chromium

# 无头模式: True 或 False
HEADLESS=False

# 慢动作模式 (毫秒)，调试时有用
SLOW_MO=100
```

### 超时配置

在 `config/settings.py` 中调整超时时间:

```python
DEFAULT_TIMEOUT = 30000  # 30秒
PAGE_LOAD_TIMEOUT = 60000  # 60秒
AI_RESPONSE_TIMEOUT = 120000  # 120秒
```

## 🤖 AI增强功能

### LLM响应验证

自动验证AI响应质量 (需要配置API密钥):

```python
def test_with_llm_validation(authenticated_page, llm_validator):
    chatbot = authenticated_page
    chatbot.send_message("Python是什么?")
    response = chatbot.get_last_ai_message()

    # AI验证响应质量
    if llm_validator:
        result = llm_validator.validate_response_quality(
            "Python是什么?",
            response
        )
        assert result["passed"], "响应质量不达标"
```

### RAG知识库

存储测试场景和预期行为，用于智能推荐测试用例。

## 📝 最佳实践

### 1. 测试隔离

每个测试应该独立运行，不依赖其他测试:

```python
# ✅ 好的做法
def test_login(login_page):
    login_page.navigate_to_login()
    login_page.login()
    assert login_page.is_login_successful()

# ❌ 不好的做法
def test_after_login():  # 依赖前一个测试的状态
    # ...
```

### 2. 使用Fixtures

使用fixtures管理测试数据和状态:

```python
@pytest.fixture
def test_data():
    return {"username": "test", "password": "pass"}

def test_with_data(test_data):
    # 使用test_data
```

### 3. 明确的断言消息

```python
# ✅ 好的做法
assert user_count > 0, f"用户数应该大于0，实际: {user_count}"

# ❌ 不好的做法
assert user_count > 0
```

### 4. 合理使用等待

```python
# ✅ 好的做法 - 智能等待
page.wait_for_selector(".message")

# ❌ 不好的做法 - 硬编码等待
time.sleep(5)
```

## 🐛 故障排查

### 测试失败时查看截图

失败的测试会自动截图，保存在 `reports/screenshots/`

### 查看详细日志

日志文件在 `reports/logs/`:
- `test_YYYY-MM-DD.log` - 所有日志
- `error_YYYY-MM-DD.log` - 仅错误日志

### 使用调试模式

```bash
# 使用-s显示print输出
pytest -s tests/test_login.py

# 使用--pdb在失败时进入调试器
pytest --pdb tests/test_login.py
```

### 查看浏览器操作

设置 `HEADLESS=False` 并调整慢动作:

```ini
HEADLESS=False
SLOW_MO=500  # 每个操作延迟500ms
```

## 📦 CI/CD集成

### GitHub Actions示例

创建 `.github/workflows/test.yml`:

```yaml
name: Automated Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          playwright install chromium --with-deps

      - name: Run tests
        env:
          TEST_USERNAME: ${{ secrets.TEST_USERNAME }}
          TEST_PASSWORD: ${{ secrets.TEST_PASSWORD }}
        run: pytest -m smoke --alluredir=allure-results

      - name: Upload Allure Report
        uses: actions/upload-artifact@v3
        with:
          name: allure-report
          path: allure-results/
```

## 📚 更多文档

- [Playwright Documentation](https://playwright.dev/python/)
- [Pytest Documentation](https://docs.pytest.org/)
- [Allure Report](https://docs.qameta.io/allure/)

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

## 📄 许可证

本项目仅供内部测试使用。

## 🙋 支持

如有问题或建议，请联系测试团队。

---

**Happy Testing! 🎉**
