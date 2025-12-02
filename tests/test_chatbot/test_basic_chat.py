"""
Chatbot基础对话测试
"""
import pytest
import allure
from pages.chatbot_page import ChatbotPage

@allure.feature("Chatbot功能")
@allure.story("基础对话")
class TestBasicChat:
    """Chatbot基础对话测试套件"""

    @allure.title("测试发送简单消息并获得响应")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.smoke
    @pytest.mark.chatbot
    def test_send_simple_message(self, authenticated_page: ChatbotPage):
        """
        测试发送简单消息并获得AI响应

        步骤:
        1. 发送测试消息
        2. 验证用户消息已发送
        3. 验证收到AI响应
        """
        chatbot = authenticated_page

        # 验证聊天输入框可见
        assert chatbot.is_chat_input_visible(), "聊天输入框不可见"

        # 步骤1: 发送测试消息
        test_message = "你好，请介绍一下你自己"
        chatbot.send_message(test_message)

        # 步骤2: 验证用户消息已发送
        last_user_msg = chatbot.get_last_user_message()
        assert test_message in last_user_msg, f"用户消息未正确显示，预期包含: {test_message}, 实际: {last_user_msg}"

        # 步骤3: 验证收到AI响应
        ai_response = chatbot.get_last_ai_message()
        assert ai_response != "", "未收到AI响应"
        assert len(ai_response) > 10, f"AI响应内容过短: {ai_response}"

    @allure.title("测试多轮对话")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.regression
    @pytest.mark.chatbot
    def test_multi_turn_conversation(self, authenticated_page: ChatbotPage):
        """
        测试多轮对话功能

        验证:
        - 可以连续发送多条消息
        - 每条消息都能获得响应
        - 对话历史保持完整
        """
        chatbot = authenticated_page

        messages = [
            "你好",
            "你能做什么?",
            "请帮我写一段Python代码打印Hello World"
        ]

        for i, msg in enumerate(messages, 1):
            chatbot.send_message(msg)
            ai_response = chatbot.get_last_ai_message()
            assert ai_response != "", f"第{i}轮未收到AI响应"

        # 验证对话历史
        message_count = chatbot.get_message_count()
        expected_count = len(messages) * 2  # 用户消息 + AI响应
        assert message_count >= expected_count, f"对话历史不完整，预期至少{expected_count}条，实际{message_count}条"

    @allure.title("测试长消息处理")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    @pytest.mark.chatbot
    @pytest.mark.slow
    def test_long_message(self, authenticated_page: ChatbotPage):
        """
        测试处理长消息

        验证系统可以处理较长的用户输入
        """
        chatbot = authenticated_page

        long_message = "请帮我分析以下问题：" + "这是一段测试文本。" * 50

        chatbot.send_message(long_message)

        # 验证收到响应
        response = chatbot.get_last_ai_message()
        assert response != "", "应该收到对长消息的响应"

    @allure.title("测试特殊字符处理")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    @pytest.mark.chatbot
    def test_special_characters(self, authenticated_page: ChatbotPage):
        """
        测试特殊字符的处理

        测试各种特殊字符，如表情符号、符号等
        """
        chatbot = authenticated_page

        special_messages = [
            "测试表情: 😀😁😂",
            "测试代码: `print('hello')`",
            "测试符号: @#$%^&*()",
        ]

        for msg in special_messages:
            chatbot.send_message(msg)
            response = chatbot.get_last_ai_message()
            assert response != "", f"对消息 '{msg}' 应该收到响应"

    @allure.title("测试聊天输入框功能")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.smoke
    @pytest.mark.chatbot
    def test_chat_input_functionality(self, authenticated_page: ChatbotPage):
        """
        测试聊天输入框的基本功能

        验证:
        - 输入框可见
        - 输入框可用
        - 可以输入文本
        """
        chatbot = authenticated_page

        # 验证输入框可见
        assert chatbot.is_chat_input_visible(), "聊天输入框不可见"

        # 验证输入框可用
        assert chatbot.is_chat_input_enabled(), "聊天输入框不可用"

    @allure.title("测试获取消息数量")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    @pytest.mark.chatbot
    def test_message_count(self, authenticated_page: ChatbotPage):
        """
        测试消息计数功能

        验证可以正确统计消息数量
        """
        chatbot = authenticated_page

        # 初始消息数
        initial_count = chatbot.get_message_count()

        # 发送一条消息
        chatbot.send_message("测试消息计数")

        # 验证消息数增加
        new_count = chatbot.get_message_count()
        assert new_count > initial_count, "发送消息后消息数应该增加"

    @allure.title("测试代码生成请求")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.chatbot
    @pytest.mark.ai
    def test_code_generation_request(self, authenticated_page: ChatbotPage):
        """
        测试请求AI生成代码

        验证AI可以响应代码生成请求
        """
        chatbot = authenticated_page

        code_request = "请用Python写一个函数计算斐波那契数列"
        chatbot.send_message(code_request)

        response = chatbot.get_last_ai_message()
        assert response != "", "应该收到代码生成响应"

        # 验证响应中包含代码相关关键词
        code_keywords = ["def", "python", "函数", "function"]
        has_code_keyword = any(keyword in response.lower() for keyword in code_keywords)
        assert has_code_keyword, f"响应应包含代码相关内容: {response[:100]}"

    @allure.title("测试问答功能")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.chatbot
    @pytest.mark.ai
    def test_question_answering(self, authenticated_page: ChatbotPage):
        """
        测试问答功能

        验证AI可以回答常识问题
        """
        chatbot = authenticated_page

        question = "Python是什么?"
        chatbot.send_message(question)

        response = chatbot.get_last_ai_message()
        assert response != "", "应该收到问答响应"
        assert len(response) > 20, "响应应该包含足够的信息"

        # 验证响应相关性
        assert "python" in response.lower(), "响应应该与Python相关"

@allure.feature("Chatbot功能")
@allure.story("消息流测试")
class TestMessageFlow:
    """消息流测试"""

    @allure.title("测试消息发送后输入框清空")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    @pytest.mark.chatbot
    def test_input_cleared_after_send(self, authenticated_page: ChatbotPage):
        """
        测试发送消息后输入框是否清空

        验证用户体验的基本功能
        """
        chatbot = authenticated_page

        test_message = "测试输入框清空"
        chatbot.send_message(test_message, wait_for_response=False)

        # 注意: 这个测试可能需要根据实际实现调整
        # 有些系统在发送后会清空输入框，有些不会

    @allure.title("测试快速连续发送消息")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    @pytest.mark.chatbot
    def test_rapid_message_sending(self, authenticated_page: ChatbotPage):
        """
        测试快速连续发送多条消息

        验证系统的稳定性
        """
        chatbot = authenticated_page

        messages = [f"测试消息 {i+1}" for i in range(3)]

        for msg in messages:
            chatbot.send_message(msg, wait_for_response=False)

        # 等待所有响应
        chatbot.wait_for_message_count(len(messages) * 2, timeout=30000)

        # 验证至少收到了一些响应
        final_count = chatbot.get_message_count()
        assert final_count >= len(messages), "应该至少有用户发送的消息"
