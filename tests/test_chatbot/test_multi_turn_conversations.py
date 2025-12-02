"""
多轮对话测试
基于data/conversation_test_data.py中的测试场景
"""
import pytest
import allure
from pages.chatbot_page import ChatbotPage
from data.conversation_test_data import (
    CONTEXT_CONTINUITY_SCENARIOS,
    LOGIC_CONSISTENCY_SCENARIOS,
    CONTEXT_SWITCHING_SCENARIOS,
    ERROR_RECOVERY_SCENARIOS,
    COMPLEX_CONVERSATION_SCENARIOS,
    ConversationScenario,
    ConversationTurn
)
from typing import List


@allure.feature("AI Assistant - 多轮对话")
@allure.story("上下文连续性")
class TestContextContinuity:
    """测试AI在多轮对话中的上下文理解和连续性"""

    @pytest.mark.parametrize("scenario", CONTEXT_CONTINUITY_SCENARIOS, ids=lambda s: s.name)
    @allure.title("上下文连续性测试: {scenario.name}")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.chatbot
    @pytest.mark.multi_turn
    def test_context_continuity(self, authenticated_page: ChatbotPage, scenario: ConversationScenario):
        """
        测试AI的上下文连续性理解能力

        验证AI是否能:
        - 理解代词引用
        - 保持多轮对话的上下文记忆
        - 正确关联前后对话内容
        """
        chatbot = authenticated_page

        allure.dynamic.description(scenario.description)

        # 执行对话场景的每一轮
        for turn_index, turn in enumerate(scenario.turns, 1):
            with allure.step(f"第 {turn_index} 轮: {turn.user_message}"):
                # 发送消息
                chatbot.send_message(turn.user_message)

                # 获取AI响应
                ai_response = chatbot.get_last_ai_message()
                assert ai_response, f"第 {turn_index} 轮未收到AI响应"

                # 验证关键词
                if turn.expected_keywords:
                    self._verify_keywords(ai_response, turn.expected_keywords, turn_index)

                # 验证上下文引用
                if turn.context_check:
                    self._verify_context_reference(
                        ai_response,
                        turn.context_check.should_reference,
                        turn.context_check.mode,
                        turn_index
                    )

                # 验证质量检查
                if turn.quality_check:
                    self._verify_quality(ai_response, turn.quality_check, turn_index)

                # 记录响应到报告
                allure.attach(
                    ai_response,
                    name=f"第 {turn_index} 轮 AI 响应",
                    attachment_type=allure.attachment_type.TEXT
                )

    def _verify_keywords(self, response: str, keywords: List[str], turn_index: int):
        """验证响应中包含预期关键词"""
        response_lower = response.lower()
        found_keywords = [kw for kw in keywords if kw.lower() in response_lower]

        with allure.step(f"验证关键词: {keywords}"):
            assert found_keywords, (
                f"第 {turn_index} 轮响应中未找到预期关键词。"
                f"预期: {keywords}, 响应: {response[:200]}"
            )
            allure.attach(
                f"找到的关键词: {found_keywords}",
                name="关键词验证结果",
                attachment_type=allure.attachment_type.TEXT
            )

    def _verify_context_reference(self, response: str, should_reference: List[str], mode: str, turn_index: int):
        """验证响应中的上下文引用"""
        if not should_reference:
            return

        response_lower = response.lower()
        found_references = [ref for ref in should_reference if ref.lower() in response_lower]

        with allure.step(f"验证上下文引用 (模式: {mode}): {should_reference}"):
            if mode == 'all':
                assert len(found_references) == len(should_reference), (
                    f"第 {turn_index} 轮响应应包含所有上下文引用。"
                    f"预期: {should_reference}, 找到: {found_references}"
                )
            else:  # mode == 'any'
                assert found_references, (
                    f"第 {turn_index} 轮响应应包含至少一个上下文引用。"
                    f"预期: {should_reference}, 响应: {response[:200]}"
                )

            allure.attach(
                f"找到的上下文引用: {found_references}",
                name="上下文引用验证结果",
                attachment_type=allure.attachment_type.TEXT
            )

    def _verify_quality(self, response: str, quality_check, turn_index: int):
        """验证响应质量"""
        with allure.step("验证响应质量"):
            if quality_check.min_length:
                assert len(response) >= quality_check.min_length, (
                    f"第 {turn_index} 轮响应长度不足。"
                    f"最小长度: {quality_check.min_length}, 实际: {len(response)}"
                )

            if quality_check.min_words:
                word_count = len(response.split())
                assert word_count >= quality_check.min_words, (
                    f"第 {turn_index} 轮响应词数不足。"
                    f"最小词数: {quality_check.min_words}, 实际: {word_count}"
                )

            if quality_check.forbidden_phrases:
                for phrase in quality_check.forbidden_phrases:
                    assert phrase.lower() not in response.lower(), (
                        f"第 {turn_index} 轮响应包含禁用短语: {phrase}"
                    )


@allure.feature("AI Assistant - 多轮对话")
@allure.story("逻辑一致性")
class TestLogicConsistency:
    """测试AI回答的逻辑一致性"""

    @pytest.mark.parametrize("scenario", LOGIC_CONSISTENCY_SCENARIOS, ids=lambda s: s.name)
    @allure.title("逻辑一致性测试: {scenario.name}")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.chatbot
    @pytest.mark.multi_turn
    def test_logic_consistency(self, authenticated_page: ChatbotPage, scenario: ConversationScenario):
        """
        测试AI回答的逻辑一致性

        验证AI是否能:
        - 保持前后信息一致
        - 追踪实体状态变化
        - 不产生矛盾的回答
        """
        chatbot = authenticated_page

        allure.dynamic.description(scenario.description)

        # 执行对话场景的每一轮
        for turn_index, turn in enumerate(scenario.turns, 1):
            with allure.step(f"第 {turn_index} 轮: {turn.user_message}"):
                # 发送消息
                chatbot.send_message(turn.user_message)

                # 获取AI响应
                ai_response = chatbot.get_last_ai_message()
                assert ai_response, f"第 {turn_index} 轮未收到AI响应"

                # 验证关键词
                if turn.expected_keywords:
                    self._verify_keywords(ai_response, turn.expected_keywords, turn_index)

                # 验证上下文引用
                if turn.context_check:
                    self._verify_context_reference(
                        ai_response,
                        turn.context_check.should_reference,
                        turn.context_check.mode,
                        turn_index
                    )

                # 记录响应到报告
                allure.attach(
                    ai_response,
                    name=f"第 {turn_index} 轮 AI 响应",
                    attachment_type=allure.attachment_type.TEXT
                )

    def _verify_keywords(self, response: str, keywords: List[str], turn_index: int):
        """验证响应中包含预期关键词"""
        response_lower = response.lower()
        found_keywords = [kw for kw in keywords if kw.lower() in response_lower]

        with allure.step(f"验证关键词: {keywords}"):
            assert found_keywords, (
                f"第 {turn_index} 轮响应中未找到预期关键词。"
                f"预期: {keywords}, 响应: {response[:200]}"
            )

    def _verify_context_reference(self, response: str, should_reference: List[str], mode: str, turn_index: int):
        """验证响应中的上下文引用"""
        if not should_reference:
            return

        response_lower = response.lower()
        found_references = [ref for ref in should_reference if ref.lower() in response_lower]

        with allure.step(f"验证上下文引用: {should_reference}"):
            if mode == 'all':
                assert len(found_references) == len(should_reference), (
                    f"第 {turn_index} 轮响应应包含所有上下文引用。"
                    f"预期: {should_reference}, 找到: {found_references}"
                )
            else:
                assert found_references, (
                    f"第 {turn_index} 轮响应应包含至少一个上下文引用。"
                    f"预期: {should_reference}"
                )


@allure.feature("AI Assistant - 多轮对话")
@allure.story("上下文切换")
class TestContextSwitching:
    """测试AI处理话题切换的能力"""

    @pytest.mark.parametrize("scenario", CONTEXT_SWITCHING_SCENARIOS, ids=lambda s: s.name)
    @allure.title("上下文切换测试: {scenario.name}")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.chatbot
    @pytest.mark.multi_turn
    def test_context_switching(self, authenticated_page: ChatbotPage, scenario: ConversationScenario):
        """
        测试AI处理话题切换的能力

        验证AI是否能:
        - 正确识别话题转换
        - 在多个话题间切换
        - 不混淆不同话题的上下文
        """
        chatbot = authenticated_page

        allure.dynamic.description(scenario.description)

        # 执行对话场景的每一轮
        for turn_index, turn in enumerate(scenario.turns, 1):
            with allure.step(f"第 {turn_index} 轮: {turn.user_message}"):
                # 发送消息
                chatbot.send_message(turn.user_message)

                # 获取AI响应
                ai_response = chatbot.get_last_ai_message()
                assert ai_response, f"第 {turn_index} 轮未收到AI响应"

                # 验证关键词
                if turn.expected_keywords:
                    self._verify_keywords(ai_response, turn.expected_keywords, turn_index)

                # 验证上下文引用
                if turn.context_check:
                    self._verify_context_reference(
                        ai_response,
                        turn.context_check.should_reference,
                        turn.context_check.mode,
                        turn_index
                    )

                # 记录响应到报告
                allure.attach(
                    ai_response,
                    name=f"第 {turn_index} 轮 AI 响应",
                    attachment_type=allure.attachment_type.TEXT
                )

    def _verify_keywords(self, response: str, keywords: List[str], turn_index: int):
        """验证响应中包含预期关键词"""
        response_lower = response.lower()
        found_keywords = [kw for kw in keywords if kw.lower() in response_lower]

        with allure.step(f"验证关键词: {keywords}"):
            assert found_keywords, (
                f"第 {turn_index} 轮响应中未找到预期关键词。"
                f"预期: {keywords}, 响应: {response[:200]}"
            )

    def _verify_context_reference(self, response: str, should_reference: List[str], mode: str, turn_index: int):
        """验证响应中的上下文引用"""
        if not should_reference:
            return

        response_lower = response.lower()
        found_references = [ref for ref in should_reference if ref.lower() in response_lower]

        with allure.step(f"验证上下文引用: {should_reference}"):
            if mode == 'all':
                assert len(found_references) == len(should_reference), (
                    f"第 {turn_index} 轮响应应包含所有上下文引用。"
                    f"预期: {should_reference}, 找到: {found_references}"
                )
            else:
                assert found_references, (
                    f"第 {turn_index} 轮响应应包含至少一个上下文引用。"
                    f"预期: {should_reference}"
                )


@allure.feature("AI Assistant - 多轮对话")
@allure.story("错误恢复")
class TestErrorRecovery:
    """测试AI的错误恢复能力"""

    @pytest.mark.parametrize("scenario", ERROR_RECOVERY_SCENARIOS, ids=lambda s: s.name)
    @allure.title("错误恢复测试: {scenario.name}")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.chatbot
    @pytest.mark.multi_turn
    def test_error_recovery(self, authenticated_page: ChatbotPage, scenario: ConversationScenario):
        """
        测试AI的错误恢复能力

        验证AI是否能:
        - 处理无效输入
        - 从错误中恢复
        - 在信息不明确时请求澄清
        """
        chatbot = authenticated_page

        allure.dynamic.description(scenario.description)

        # 执行对话场景的每一轮
        for turn_index, turn in enumerate(scenario.turns, 1):
            with allure.step(f"第 {turn_index} 轮: {turn.user_message}"):
                # 发送消息
                chatbot.send_message(turn.user_message)

                # 获取AI响应
                ai_response = chatbot.get_last_ai_message()
                assert ai_response, f"第 {turn_index} 轮未收到AI响应"

                # 验证关键词
                if turn.expected_keywords:
                    self._verify_keywords(ai_response, turn.expected_keywords, turn_index)

                # 验证上下文引用
                if turn.context_check:
                    self._verify_context_reference(
                        ai_response,
                        turn.context_check.should_reference,
                        turn.context_check.mode,
                        turn_index
                    )

                # 验证质量检查
                if turn.quality_check:
                    self._verify_quality(ai_response, turn.quality_check, turn_index)

                # 记录响应到报告
                allure.attach(
                    ai_response,
                    name=f"第 {turn_index} 轮 AI 响应",
                    attachment_type=allure.attachment_type.TEXT
                )

    def _verify_keywords(self, response: str, keywords: List[str], turn_index: int):
        """验证响应中包含预期关键词"""
        if not keywords:  # 无效输入的情况
            return

        response_lower = response.lower()
        found_keywords = [kw for kw in keywords if kw.lower() in response_lower]

        with allure.step(f"验证关键词: {keywords}"):
            assert found_keywords, (
                f"第 {turn_index} 轮响应中未找到预期关键词。"
                f"预期: {keywords}, 响应: {response[:200]}"
            )

    def _verify_context_reference(self, response: str, should_reference: List[str], mode: str, turn_index: int):
        """验证响应中的上下文引用"""
        if not should_reference:
            return

        response_lower = response.lower()
        found_references = [ref for ref in should_reference if ref.lower() in response_lower]

        with allure.step(f"验证上下文引用: {should_reference}"):
            if mode == 'all':
                assert len(found_references) == len(should_reference), (
                    f"第 {turn_index} 轮响应应包含所有上下文引用。"
                    f"预期: {should_reference}, 找到: {found_references}"
                )
            else:
                assert found_references, (
                    f"第 {turn_index} 轮响应应包含至少一个上下文引用。"
                    f"预期: {should_reference}"
                )

    def _verify_quality(self, response: str, quality_check, turn_index: int):
        """验证响应质量"""
        with allure.step("验证响应质量"):
            if quality_check.min_length:
                assert len(response) >= quality_check.min_length, (
                    f"第 {turn_index} 轮响应长度不足。"
                    f"最小长度: {quality_check.min_length}, 实际: {len(response)}"
                )

            if quality_check.min_words:
                word_count = len(response.split())
                assert word_count >= quality_check.min_words, (
                    f"第 {turn_index} 轮响应词数不足。"
                    f"最小词数: {quality_check.min_words}, 实际: {word_count}"
                )


@allure.feature("AI Assistant - 多轮对话")
@allure.story("复杂对话流程")
class TestComplexConversation:
    """测试复杂的真实对话流程"""

    @pytest.mark.parametrize("scenario", COMPLEX_CONVERSATION_SCENARIOS, ids=lambda s: s.name)
    @allure.title("复杂对话流程测试: {scenario.name}")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.chatbot
    @pytest.mark.multi_turn
    @pytest.mark.slow
    def test_complex_conversation(self, authenticated_page: ChatbotPage, scenario: ConversationScenario):
        """
        测试复杂的真实对话流程

        验证AI是否能:
        - 处理完整的业务流程
        - 管理多步骤的任务
        - 保持长对话的上下文连贯性
        """
        chatbot = authenticated_page

        allure.dynamic.description(scenario.description)

        # 执行对话场景的每一轮
        for turn_index, turn in enumerate(scenario.turns, 1):
            with allure.step(f"第 {turn_index} 轮: {turn.user_message}"):
                # 发送消息
                chatbot.send_message(turn.user_message)

                # 获取AI响应
                ai_response = chatbot.get_last_ai_message()
                assert ai_response, f"第 {turn_index} 轮未收到AI响应"

                # 验证关键词
                if turn.expected_keywords:
                    self._verify_keywords(ai_response, turn.expected_keywords, turn_index)

                # 验证上下文引用
                if turn.context_check:
                    self._verify_context_reference(
                        ai_response,
                        turn.context_check.should_reference,
                        turn.context_check.mode,
                        turn_index
                    )

                # 记录响应到报告
                allure.attach(
                    ai_response,
                    name=f"第 {turn_index} 轮 AI 响应",
                    attachment_type=allure.attachment_type.TEXT
                )

    def _verify_keywords(self, response: str, keywords: List[str], turn_index: int):
        """验证响应中包含预期关键词"""
        response_lower = response.lower()
        found_keywords = [kw for kw in keywords if kw.lower() in response_lower]

        with allure.step(f"验证关键词: {keywords}"):
            assert found_keywords, (
                f"第 {turn_index} 轮响应中未找到预期关键词。"
                f"预期: {keywords}, 响应: {response[:200]}"
            )

    def _verify_context_reference(self, response: str, should_reference: List[str], mode: str, turn_index: int):
        """验证响应中的上下文引用"""
        if not should_reference:
            return

        response_lower = response.lower()
        found_references = [ref for ref in should_reference if ref.lower() in response_lower]

        with allure.step(f"验证上下文引用: {should_reference}"):
            if mode == 'all':
                assert len(found_references) == len(should_reference), (
                    f"第 {turn_index} 轮响应应包含所有上下文引用。"
                    f"预期: {should_reference}, 找到: {found_references}"
                )
            else:
                assert found_references, (
                    f"第 {turn_index} 轮响应应包含至少一个上下文引用。"
                    f"预期: {should_reference}"
                )
