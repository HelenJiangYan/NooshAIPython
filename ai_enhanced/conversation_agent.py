"""
对话测试智能体

自主控制 Playwright 执行对话测试，并使用 ValidationAgent 验证响应质量
"""

import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum

from .base_agent import BaseAgent, AgentConfig
from .validation_agent import ValidationAgent, ValidationScore
from .tools import get_claude_tools, get_tool_by_name
from utils.logger import test_logger as logger


class ScenarioStatus(Enum):
    """场景状态"""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    ERROR = "error"


# 保持向后兼容
TestStatus = ScenarioStatus


@dataclass
class ScenarioStep:
    """场景步骤"""
    action: str
    params: Dict[str, Any]
    expected: Optional[str] = None
    result: Optional[str] = None
    status: ScenarioStatus = ScenarioStatus.PENDING


# 保持向后兼容
TestStep = ScenarioStep


@dataclass
class ConversationScenario:
    """对话测试场景"""
    name: str
    description: str
    steps: List[ScenarioStep] = field(default_factory=list)
    status: ScenarioStatus = ScenarioStatus.PENDING
    issues: List[Dict[str, Any]] = field(default_factory=list)
    validation_scores: List[ValidationScore] = field(default_factory=list)


# 保持向后兼容
TestScenario = ConversationScenario


@dataclass
class ConversationTestResult:
    """对话测试结果"""
    scenario_name: str
    success: bool
    summary: str
    conversation_history: List[Dict[str, str]]
    validation_scores: List[ValidationScore]
    issues: List[Dict[str, Any]]
    duration_seconds: float


class ConversationAgent(BaseAgent):
    """
    对话测试智能体

    自主控制 Playwright 与 NooshAI Chatbot 交互，执行多轮对话测试
    """

    SYSTEM_PROMPT = """你是一个专业的AI测试智能体，负责测试Chatbot系统的对话功能。

你的任务是：
1. 执行给定的测试场景，发送用户消息并验证AI响应
2. 使用提供的工具与Chatbot页面交互
3. 评估AI响应的质量和准确性
4. 报告发现的任何问题

执行测试时请遵循以下原则：
- 按顺序执行测试步骤，确保每一步都成功后再继续
- 如果遇到错误，尝试恢复或记录问题后继续
- 对每个AI响应调用validate_response进行质量评估
- 完成所有测试步骤后，调用complete_test汇报结果

工具使用说明：
- send_message: 向Chatbot发送消息
- wait_for_response: 等待并获取AI响应
- validate_response: 验证AI响应质量
- take_screenshot: 在关键步骤或出错时截图
- report_issue: 报告发现的问题
- complete_test: 标记测试完成

请用中文与我交流，并在执行过程中提供清晰的状态更新。
"""

    def __init__(
        self,
        chatbot_page=None,
        validator: Optional[ValidationAgent] = None,
        mock_mode: bool = False
    ):
        """
        初始化对话测试智能体

        Args:
            chatbot_page: ChatbotPage 实例，用于页面交互
            validator: ValidationAgent 实例，用于验证响应
            mock_mode: 是否使用模拟模式（不调用 API）
        """
        self.mock_mode = mock_mode
        self.chatbot_page = chatbot_page
        self.validator = validator or ValidationAgent(mock_mode=mock_mode)
        self.conversation_history: List[Dict[str, str]] = []
        self.current_scenario: Optional[TestScenario] = None
        self.issues: List[Dict[str, Any]] = []

        if not mock_mode:
            config = AgentConfig(
                model="claude-sonnet-4-5-20250929",
                max_tokens=4096,
                temperature=0.5
            )
            super().__init__(
                name="ConversationAgent",
                system_prompt=self.SYSTEM_PROMPT,
                config=config
            )
        else:
            self.name = "ConversationAgent"
            logger.info(f"智能体 [{self.name}] 以 Mock 模式初始化")

    def set_chatbot_page(self, chatbot_page):
        """设置 ChatbotPage 实例"""
        self.chatbot_page = chatbot_page

    def execute(self, scenario: TestScenario) -> ConversationTestResult:
        """
        执行测试场景

        Args:
            scenario: 测试场景

        Returns:
            ConversationTestResult: 测试结果
        """
        import time
        start_time = time.time()

        self.current_scenario = scenario
        self.conversation_history = []
        self.issues = []

        logger.info(f"🚀 开始执行测试场景: {scenario.name}")
        logger.info(f"   描述: {scenario.description}")

        if self.mock_mode:
            # Mock 模式：模拟执行测试
            result = self._mock_execute_scenario(scenario)
        else:
            # 真实模式：使用 Claude 智能执行
            result = self._execute_with_agent(scenario)

        duration = time.time() - start_time
        result.duration_seconds = duration

        logger.info(f"✅ 测试场景完成: {scenario.name}")
        logger.info(f"   结果: {'通过' if result.success else '失败'}")
        logger.info(f"   耗时: {duration:.2f}秒")

        return result

    def _mock_execute_scenario(self, scenario: TestScenario) -> ConversationTestResult:
        """Mock 模式执行测试场景"""
        validation_scores = []

        for step in scenario.steps:
            logger.info(f"  [Mock] 执行步骤: {step.action}")

            if step.action == "send_message":
                message = step.params.get("message", "")
                self.conversation_history.append({
                    "role": "user",
                    "content": message
                })

                # 模拟 AI 响应
                if self.chatbot_page:
                    try:
                        self.chatbot_page.send_message(message)
                        ai_response = self.chatbot_page.get_last_ai_message()
                    except Exception as e:
                        ai_response = f"[Mock Response] 收到消息: {message}"
                        logger.warning(f"使用 Mock 响应: {e}")
                else:
                    ai_response = f"[Mock Response] 收到消息: {message}"

                self.conversation_history.append({
                    "role": "assistant",
                    "content": ai_response
                })

                # 验证响应
                score = self.validator.validate_single_response(
                    user_message=message,
                    ai_response=ai_response,
                    context=self.conversation_history[:-2] if len(self.conversation_history) > 2 else None
                )
                validation_scores.append(score)

                step.result = ai_response
                step.status = TestStatus.PASSED

            elif step.action == "validate":
                # 验证已在发送消息时完成
                step.status = TestStatus.PASSED

            else:
                logger.warning(f"  [Mock] 未知步骤: {step.action}")
                step.status = TestStatus.PASSED

        # 计算总体结果
        all_passed = all(s.passed for s in validation_scores) if validation_scores else True
        avg_score = sum(s.overall for s in validation_scores) / len(validation_scores) if validation_scores else 0

        return ConversationTestResult(
            scenario_name=scenario.name,
            success=all_passed,
            summary=f"Mock执行完成，共{len(scenario.steps)}个步骤，平均评分{avg_score:.2f}",
            conversation_history=self.conversation_history,
            validation_scores=validation_scores,
            issues=self.issues,
            duration_seconds=0
        )

    def _execute_with_agent(self, scenario: TestScenario) -> ConversationTestResult:
        """使用 Claude 智能体执行测试场景"""
        # 构建任务描述
        task_prompt = self._build_task_prompt(scenario)

        # 调用 Claude 并处理工具调用
        response = self._run_agent_loop(task_prompt)

        # 解析结果
        return self._parse_agent_result(scenario, response)

    def _build_task_prompt(self, scenario: TestScenario) -> str:
        """构建任务提示"""
        steps_desc = []
        for i, step in enumerate(scenario.steps, 1):
            step_text = f"{i}. {step.action}"
            if step.params:
                step_text += f": {json.dumps(step.params, ensure_ascii=False)}"
            if step.expected:
                step_text += f" (预期: {step.expected})"
            steps_desc.append(step_text)

        return f"""
请执行以下测试场景：

**场景名称**: {scenario.name}
**描述**: {scenario.description}

**测试步骤**:
{chr(10).join(steps_desc)}

请按顺序执行每个步骤，并在完成后调用 complete_test 工具汇报结果。
"""

    def _run_agent_loop(self, task_prompt: str) -> Dict[str, Any]:
        """运行智能体循环，处理工具调用"""
        messages = [{"role": "user", "content": task_prompt}]
        tools = get_claude_tools()

        max_iterations = 20
        iteration = 0
        final_result = None

        while iteration < max_iterations:
            iteration += 1
            logger.info(f"  智能体迭代 {iteration}/{max_iterations}")

            # 调用 Claude
            response = self.client.messages.create(
                model=self.config.model,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                system=self.system_prompt,
                messages=messages,
                tools=tools
            )

            # 处理响应
            assistant_content = []
            tool_results = []

            for block in response.content:
                if block.type == "text":
                    assistant_content.append({"type": "text", "text": block.text})
                    logger.info(f"  智能体: {block.text[:100]}...")

                elif block.type == "tool_use":
                    tool_name = block.name
                    tool_input = block.input

                    logger.info(f"  调用工具: {tool_name}")
                    logger.debug(f"  参数: {tool_input}")

                    # 执行工具
                    tool_result = self._execute_tool(tool_name, tool_input)

                    assistant_content.append({
                        "type": "tool_use",
                        "id": block.id,
                        "name": tool_name,
                        "input": tool_input
                    })

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": json.dumps(tool_result, ensure_ascii=False)
                    })

                    # 检查是否完成测试
                    if tool_name == "complete_test":
                        final_result = tool_result
                        break

            # 添加助手消息
            messages.append({"role": "assistant", "content": assistant_content})

            # 如果有工具调用，添加工具结果
            if tool_results:
                messages.append({"role": "user", "content": tool_results})

            # 如果测试完成或没有更多工具调用，退出
            if final_result or response.stop_reason == "end_turn":
                break

        return final_result or {"success": False, "summary": "智能体未正常完成测试"}

    def _execute_tool(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """执行工具调用"""
        try:
            if tool_name == "send_message":
                return self._tool_send_message(params)

            elif tool_name == "wait_for_response":
                return self._tool_wait_for_response(params)

            elif tool_name == "get_conversation_history":
                return {"history": self.conversation_history}

            elif tool_name == "validate_response":
                return self._tool_validate_response(params)

            elif tool_name == "take_screenshot":
                return self._tool_take_screenshot(params)

            elif tool_name == "report_issue":
                return self._tool_report_issue(params)

            elif tool_name == "complete_test":
                return self._tool_complete_test(params)

            elif tool_name == "log_info":
                level = params.get("level", "info")
                message = params.get("message", "")
                getattr(logger, level)(f"[Agent] {message}")
                return {"logged": True}

            else:
                return {"error": f"未知工具: {tool_name}"}

        except Exception as e:
            logger.error(f"工具执行失败 {tool_name}: {e}")
            return {"error": str(e)}

    def _tool_send_message(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """发送消息工具"""
        message = params.get("message", "")

        if not self.chatbot_page:
            return {"error": "ChatbotPage 未初始化"}

        try:
            self.chatbot_page.send_message(message, wait_for_response=False)
            self.conversation_history.append({
                "role": "user",
                "content": message
            })
            return {"success": True, "message_sent": message}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _tool_wait_for_response(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """等待响应工具"""
        timeout = params.get("timeout", 60) * 1000

        if not self.chatbot_page:
            return {"error": "ChatbotPage 未初始化"}

        try:
            self.chatbot_page.wait_for_ai_response(timeout=timeout)
            response = self.chatbot_page.get_last_ai_message()
            self.conversation_history.append({
                "role": "assistant",
                "content": response
            })
            return {"success": True, "response": response}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _tool_validate_response(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """验证响应工具"""
        user_message = params.get("user_message", "")
        ai_response = params.get("ai_response", "")
        context = params.get("context", None)

        score = self.validator.validate_single_response(
            user_message=user_message,
            ai_response=ai_response,
            context=context
        )

        return {
            "validation": score.to_dict(),
            "passed": score.passed
        }

    def _tool_take_screenshot(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """截图工具"""
        name = params.get("name", "screenshot")

        if not self.chatbot_page:
            return {"error": "ChatbotPage 未初始化"}

        try:
            path = self.chatbot_page.take_screenshot(name)
            return {"success": True, "path": str(path)}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _tool_report_issue(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """报告问题工具"""
        issue = {
            "type": params.get("issue_type", "unknown"),
            "description": params.get("description", ""),
            "severity": params.get("severity", "medium")
        }
        self.issues.append(issue)
        logger.warning(f"发现问题: [{issue['severity']}] {issue['type']} - {issue['description']}")
        return {"reported": True, "issue": issue}

    def _tool_complete_test(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """完成测试工具"""
        return {
            "success": params.get("success", False),
            "summary": params.get("summary", ""),
            "issues": params.get("issues", self.issues)
        }

    def _parse_agent_result(
        self,
        scenario: TestScenario,
        result: Dict[str, Any]
    ) -> ConversationTestResult:
        """解析智能体执行结果"""
        return ConversationTestResult(
            scenario_name=scenario.name,
            success=result.get("success", False),
            summary=result.get("summary", ""),
            conversation_history=self.conversation_history,
            validation_scores=scenario.validation_scores,
            issues=result.get("issues", self.issues),
            duration_seconds=0
        )

    # ============== 便捷方法 ==============

    def run_simple_conversation(
        self,
        messages: List[str],
        validate: bool = True
    ) -> ConversationTestResult:
        """执行简单的多轮对话测试"""
        steps = [TestStep(action="send_message", params={"message": msg}) for msg in messages]
        scenario = TestScenario(
            name="simple_conversation",
            description=f"简单对话测试: {len(messages)}条消息",
            steps=steps
        )
        return self.execute(scenario)

    def validate_conversation(
        self,
        conversation: List[Dict[str, str]]
    ) -> ValidationScore:
        """
        验证已有的对话历史

        Args:
            conversation: 对话历史

        Returns:
            ValidationScore: 验证结果
        """
        return self.validator.execute(conversation)
