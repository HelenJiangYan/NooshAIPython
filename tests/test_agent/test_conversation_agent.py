"""
对话智能体测试

测试 ConversationAgent 的对话执行和验证能力
"""

import pytest
import allure
from ai_enhanced.conversation_agent import (
    ConversationAgent,
    TestScenario,
    TestStep,
    TestStatus,
    ConversationTestResult
)
from ai_enhanced.validation_agent import ValidationAgent, ValidationScore


@allure.feature("AI智能体")
@allure.story("对话智能体")
class TestConversationAgent:
    """对话智能体测试套件"""

    @pytest.fixture
    def agent(self):
        """创建对话智能体实例（Mock模式）"""
        return ConversationAgent(mock_mode=True)

    @pytest.fixture
    def sample_scenario(self):
        """创建示例测试场景"""
        return TestScenario(
            name="greeting_test",
            description="测试基本问候功能",
            steps=[
                TestStep(
                    action="send_message",
                    params={"message": "你好"},
                    expected="包含问候语"
                ),
                TestStep(
                    action="send_message",
                    params={"message": "今天天气怎么样？"},
                    expected="关于天气的回复"
                )
            ]
        )

    @allure.title("测试对话智能体初始化")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.agent
    def test_agent_initialization(self, agent):
        """测试智能体正确初始化"""
        assert agent.name == "ConversationAgent"
        assert agent.mock_mode is True
        assert agent.validator is not None
        assert len(agent.conversation_history) == 0

    @allure.title("测试Mock模式执行场景")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.agent
    def test_mock_execute_scenario(self, agent, sample_scenario):
        """测试Mock模式下执行测试场景"""
        result = agent.execute(sample_scenario)

        assert isinstance(result, ConversationTestResult)
        assert result.scenario_name == "greeting_test"
        assert len(result.conversation_history) == 4  # 2条用户消息 + 2条AI响应
        assert len(result.validation_scores) == 2
        print(f"\n测试结果: {result.summary}")

    @allure.title("测试简单对话执行")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.agent
    def test_run_simple_conversation(self, agent):
        """测试简单对话执行方法"""
        messages = [
            "你好，我是测试用户",
            "请帮我查询订单状态"
        ]

        result = agent.run_simple_conversation(messages, validate=True)

        assert isinstance(result, ConversationTestResult)
        assert result.scenario_name == "simple_conversation"
        assert len(result.conversation_history) == 4
        print(f"\n对话历史: {result.conversation_history}")

    @allure.title("测试对话验证功能")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.agent
    def test_validate_conversation(self, agent):
        """测试已有对话的验证"""
        conversation = [
            {"role": "user", "content": "什么是人工智能？"},
            {"role": "assistant", "content": "人工智能(AI)是计算机科学的一个分支，"
             "致力于创建能够执行通常需要人类智能的任务的系统。"
             "这包括学习、推理、问题解决、感知和语言理解等能力。"}
        ]

        score = agent.validate_conversation(conversation)

        assert isinstance(score, ValidationScore)
        assert score.completeness >= 7  # 响应足够详细
        print(f"\n验证结果: {score.to_dict()}")

    @allure.title("测试步骤状态跟踪")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.agent
    def test_step_status_tracking(self, agent, sample_scenario):
        """测试步骤状态正确跟踪"""
        result = agent.execute(sample_scenario)

        # 检查所有步骤都已完成
        for step in sample_scenario.steps:
            assert step.status == TestStatus.PASSED
            assert step.result is not None

    @allure.title("测试空场景处理")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.agent
    def test_empty_scenario(self, agent):
        """测试空场景的处理"""
        empty_scenario = TestScenario(
            name="empty_test",
            description="空测试场景",
            steps=[]
        )

        result = agent.execute(empty_scenario)

        assert isinstance(result, ConversationTestResult)
        assert result.success is True  # 空场景应该成功
        assert len(result.conversation_history) == 0

    @allure.title("测试多轮对话场景")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.agent
    def test_multi_turn_scenario(self, agent):
        """测试多轮对话场景"""
        scenario = TestScenario(
            name="multi_turn_test",
            description="测试多轮对话上下文理解",
            steps=[
                TestStep(
                    action="send_message",
                    params={"message": "我想创建一个新项目"},
                    expected="询问项目信息"
                ),
                TestStep(
                    action="send_message",
                    params={"message": "项目名称是测试项目2024"},
                    expected="确认项目名称"
                ),
                TestStep(
                    action="send_message",
                    params={"message": "添加一个设计评审任务"},
                    expected="确认添加任务"
                )
            ]
        )

        result = agent.execute(scenario)

        assert isinstance(result, ConversationTestResult)
        assert len(result.conversation_history) == 6  # 3条用户 + 3条AI
        assert len(result.validation_scores) == 3

        # 检查上下文理解评分
        last_score = result.validation_scores[-1]
        assert last_score.context_awareness >= 6, "多轮对话应有良好的上下文理解"

        print(f"\n多轮对话测试结果:")
        print(f"  成功: {result.success}")
        print(f"  平均评分: {sum(s.overall for s in result.validation_scores) / len(result.validation_scores):.2f}")


@allure.feature("AI智能体")
@allure.story("对话智能体工具")
class TestConversationAgentTools:
    """对话智能体工具测试"""

    @pytest.fixture
    def agent(self):
        """创建对话智能体实例（Mock模式）"""
        return ConversationAgent(mock_mode=True)

    @allure.title("测试问题报告功能")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.agent
    def test_report_issue(self, agent):
        """测试问题报告工具"""
        result = agent._tool_report_issue({
            "issue_type": "bug",
            "description": "AI响应与预期不符",
            "severity": "medium"
        })

        assert result["reported"] is True
        assert len(agent.issues) == 1
        assert agent.issues[0]["type"] == "bug"

    @allure.title("测试日志记录功能")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.agent
    def test_log_info(self, agent):
        """测试日志记录工具"""
        result = agent._execute_tool("log_info", {
            "message": "测试日志消息",
            "level": "info"
        })

        assert result["logged"] is True

    @allure.title("测试验证响应工具")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.agent
    def test_validate_response_tool(self, agent):
        """测试验证响应工具"""
        result = agent._tool_validate_response({
            "user_message": "你好",
            "ai_response": "你好！有什么可以帮助你的吗？"
        })

        assert "validation" in result
        assert "passed" in result
        assert isinstance(result["validation"], dict)

    @allure.title("测试完成测试工具")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.agent
    def test_complete_test_tool(self, agent):
        """测试完成测试工具"""
        result = agent._tool_complete_test({
            "success": True,
            "summary": "所有测试通过"
        })

        assert result["success"] is True
        assert result["summary"] == "所有测试通过"


@allure.feature("AI智能体")
@allure.story("对话智能体数据结构")
class TestConversationAgentDataStructures:
    """对话智能体数据结构测试"""

    @allure.title("测试TestStep数据结构")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.agent
    def test_test_step_structure(self):
        """测试TestStep数据结构"""
        step = TestStep(
            action="send_message",
            params={"message": "测试"},
            expected="响应"
        )

        assert step.action == "send_message"
        assert step.params["message"] == "测试"
        assert step.expected == "响应"
        assert step.result is None
        assert step.status == TestStatus.PENDING

    @allure.title("测试TestScenario数据结构")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.agent
    def test_test_scenario_structure(self):
        """测试TestScenario数据结构"""
        scenario = TestScenario(
            name="test_scenario",
            description="测试描述",
            steps=[
                TestStep(action="send_message", params={"message": "hi"})
            ]
        )

        assert scenario.name == "test_scenario"
        assert scenario.description == "测试描述"
        assert len(scenario.steps) == 1
        assert scenario.status == TestStatus.PENDING
        assert len(scenario.issues) == 0

    @allure.title("测试ConversationTestResult数据结构")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.agent
    def test_conversation_test_result_structure(self):
        """测试ConversationTestResult数据结构"""
        result = ConversationTestResult(
            scenario_name="test",
            success=True,
            summary="测试通过",
            conversation_history=[],
            validation_scores=[],
            issues=[],
            duration_seconds=1.5
        )

        assert result.scenario_name == "test"
        assert result.success is True
        assert result.duration_seconds == 1.5


@allure.feature("AI智能体")
@allure.story("对话智能体浏览器集成")
class TestConversationAgentBrowser:
    """对话智能体浏览器集成测试 - 真正打开浏览器"""

    @allure.title("智能体控制浏览器执行对话")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.agent
    @pytest.mark.integration
    def test_agent_with_real_browser(self, authenticated_page):
        """
        测试智能体控制真实浏览器执行对话

        使用 authenticated_page fixture（已登录并导航到AI Assistant）
        """
        chatbot_page = authenticated_page

        # 创建智能体，传入真实的 chatbot_page
        agent = ConversationAgent(
            chatbot_page=chatbot_page,
            mock_mode=True  # 验证逻辑用Mock，避免API调用
        )

        # 执行简单对话
        result = agent.run_simple_conversation(
            messages=["你好", "帮我介绍一下你自己"],
            validate=True
        )

        assert isinstance(result, ConversationTestResult)
        assert len(result.conversation_history) >= 2

        print(f"\n浏览器对话测试结果:")
        print(f"  成功: {result.success}")
        print(f"  对话轮数: {len(result.conversation_history) // 2}")
        for msg in result.conversation_history:
            role = "用户" if msg["role"] == "user" else "AI"
            print(f"  [{role}]: {msg['content'][:50]}...")

    @allure.title("智能体执行多轮对话场景")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.agent
    @pytest.mark.integration
    def test_agent_multi_turn_browser(self, authenticated_page):
        """测试智能体在真实浏览器中执行多轮对话"""
        chatbot_page = authenticated_page

        agent = ConversationAgent(chatbot_page=chatbot_page, mock_mode=True)

        # 创建多轮对话场景
        scenario = TestScenario(
            name="browser_multi_turn",
            description="浏览器多轮对话测试",
            steps=[
                TestStep(action="send_message", params={"message": "你好"}),
                TestStep(action="send_message", params={"message": "你能做什么？"}),
            ]
        )

        result = agent.execute(scenario)

        assert isinstance(result, ConversationTestResult)
        assert len(result.conversation_history) == 4

        print(f"\n多轮对话结果: {result.summary}")
