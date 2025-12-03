"""
验证智能体

使用 LLM 评估 AI 响应质量，提供多维度打分和改进建议
"""

import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from .base_agent import BaseAgent, AgentConfig
from utils.logger import test_logger as logger


@dataclass
class ValidationScore:
    """验证评分结果"""
    relevance: int  # 相关性 (1-10)
    accuracy: int  # 准确性 (1-10)
    completeness: int  # 完整性 (1-10)
    fluency: int  # 流畅性 (1-10)
    context_awareness: int  # 上下文理解 (1-10)
    overall: float  # 综合评分
    suggestions: List[str]  # 改进建议
    passed: bool  # 是否通过验证

    def to_dict(self) -> Dict[str, Any]:
        return {
            "relevance": self.relevance,
            "accuracy": self.accuracy,
            "completeness": self.completeness,
            "fluency": self.fluency,
            "context_awareness": self.context_awareness,
            "overall": self.overall,
            "suggestions": self.suggestions,
            "passed": self.passed
        }


class ValidationAgent(BaseAgent):
    """
    验证智能体

    使用 Claude 评估 AI 聊天系统的响应质量
    支持 mock 模式用于测试（不调用 API）
    """

    SYSTEM_PROMPT = """你是一个专业的AI响应质量评估专家。

你的任务是评估AI聊天系统的响应质量，从以下5个维度进行打分(1-10分)：

1. **相关性 (relevance)**: 响应是否与用户问题直接相关
   - 10分: 完全切题，直接回答了用户问题
   - 5分: 部分相关，但有偏离
   - 1分: 完全不相关

2. **准确性 (accuracy)**: 提供的信息是否准确
   - 10分: 信息完全准确
   - 5分: 基本准确，有小错误
   - 1分: 存在严重错误

3. **完整性 (completeness)**: 是否完整回答了问题
   - 10分: 回答全面，覆盖所有要点
   - 5分: 回答了主要内容，但有遗漏
   - 1分: 回答过于简略或不完整

4. **流畅性 (fluency)**: 语言是否流畅自然
   - 10分: 语言流畅，表达清晰
   - 5分: 基本通顺，但有些生硬
   - 1分: 表达混乱，难以理解

5. **上下文理解 (context_awareness)**: 是否正确理解了对话上下文
   - 10分: 完全理解上下文，响应连贯
   - 5分: 部分理解上下文
   - 1分: 忽略上下文，响应不连贯

**输出格式要求**:
你必须以严格的JSON格式输出评估结果，不要包含任何其他文字：

```json
{
  "relevance": <1-10>,
  "accuracy": <1-10>,
  "completeness": <1-10>,
  "fluency": <1-10>,
  "context_awareness": <1-10>,
  "suggestions": ["建议1", "建议2"]
}
```

注意：
- 评分必须是1-10的整数
- suggestions是改进建议数组，如果没有建议可以为空数组
- 不要输出JSON以外的任何内容
"""

    def __init__(self, pass_threshold: float = 6.0, mock_mode: bool = False):
        """
        初始化验证智能体

        Args:
            pass_threshold: 通过阈值，综合评分>=此值视为通过
            mock_mode: 是否使用模拟模式（不调用 API，用于测试）
        """
        self.mock_mode = mock_mode
        self.pass_threshold = pass_threshold

        if not mock_mode:
            config = AgentConfig(
                model="claude-sonnet-4-5-20250929",
                max_tokens=2048,
                temperature=0.3  # 降低温度以获得更稳定的评分
            )
            super().__init__(
                name="ValidationAgent",
                system_prompt=self.SYSTEM_PROMPT,
                config=config
            )
        else:
            # Mock 模式：不初始化 API 客户端
            self.name = "ValidationAgent"
            self.conversation_history = []
            logger.info(f"智能体 [{self.name}] 以 Mock 模式初始化")

    def execute(self, conversation: List[Dict[str, str]]) -> ValidationScore:
        """
        评估对话质量

        Args:
            conversation: 对话历史，格式为 [{"role": "user/assistant", "content": "..."}]

        Returns:
            ValidationScore: 评估结果
        """
        # Mock 模式：返回基于简单规则的模拟评分
        if self.mock_mode:
            return self._mock_evaluate(conversation)

        # 重置对话历史，每次评估独立
        self.reset()

        # 构建评估请求
        conversation_text = self._format_conversation(conversation)
        prompt = f"请评估以下对话的AI响应质量：\n\n{conversation_text}"

        # 调用 LLM 进行评估
        response = self.think(prompt)

        # 解析响应
        return self._parse_response(response)

    def _mock_evaluate(self, conversation: List[Dict[str, str]]) -> ValidationScore:
        """
        Mock 模式评估：基于简单规则生成模拟评分

        用于测试时不消耗 API 额度
        """
        # 获取最后一个 AI 响应
        ai_responses = [m for m in conversation if m["role"] == "assistant"]
        user_messages = [m for m in conversation if m["role"] == "user"]

        if not ai_responses:
            return ValidationScore(5, 5, 5, 5, 5, 5.0, ["无AI响应"], False)

        last_response = ai_responses[-1]["content"]
        last_question = user_messages[-1]["content"] if user_messages else ""

        # 基于响应长度评估完整性
        response_len = len(last_response)
        if response_len < 10:
            completeness = 2
        elif response_len < 50:
            completeness = 5
        elif response_len < 200:
            completeness = 7
        else:
            completeness = 9

        # 基于关键词匹配评估相关性
        question_words = set(last_question.lower().split())
        response_words = set(last_response.lower().split())
        overlap = len(question_words & response_words)
        if overlap == 0:
            relevance = 3
        elif overlap < 3:
            relevance = 6
        else:
            relevance = 8

        # 其他维度给予中等分数
        accuracy = 7
        fluency = 8
        context_awareness = 7 if len(conversation) > 2 else 6

        overall = (relevance + accuracy + completeness + fluency + context_awareness) / 5

        suggestions = []
        if completeness < 5:
            suggestions.append("响应过于简短，建议提供更详细的信息")
        if relevance < 5:
            suggestions.append("响应与问题相关性较低")

        return ValidationScore(
            relevance=relevance,
            accuracy=accuracy,
            completeness=completeness,
            fluency=fluency,
            context_awareness=context_awareness,
            overall=round(overall, 2),
            suggestions=suggestions,
            passed=overall >= self.pass_threshold
        )

    def validate_single_response(
        self,
        user_message: str,
        ai_response: str,
        context: Optional[List[Dict[str, str]]] = None
    ) -> ValidationScore:
        """
        验证单个AI响应

        Args:
            user_message: 用户消息
            ai_response: AI响应
            context: 可选的上下文对话历史

        Returns:
            ValidationScore: 评估结果
        """
        conversation = context or []
        conversation.append({"role": "user", "content": user_message})
        conversation.append({"role": "assistant", "content": ai_response})

        return self.execute(conversation)

    def _format_conversation(self, conversation: List[Dict[str, str]]) -> str:
        """格式化对话为可读文本"""
        formatted = []
        for msg in conversation:
            role = "用户" if msg["role"] == "user" else "AI"
            formatted.append(f"[{role}]: {msg['content']}")
        return "\n".join(formatted)

    def _parse_response(self, response: str) -> ValidationScore:
        """解析 LLM 响应为 ValidationScore"""
        try:
            # 尝试提取 JSON
            json_str = response
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0]

            data = json.loads(json_str.strip())

            # 提取评分
            relevance = int(data.get("relevance", 5))
            accuracy = int(data.get("accuracy", 5))
            completeness = int(data.get("completeness", 5))
            fluency = int(data.get("fluency", 5))
            context_awareness = int(data.get("context_awareness", 5))
            suggestions = data.get("suggestions", [])

            # 计算综合评分
            overall = (relevance + accuracy + completeness + fluency + context_awareness) / 5

            return ValidationScore(
                relevance=relevance,
                accuracy=accuracy,
                completeness=completeness,
                fluency=fluency,
                context_awareness=context_awareness,
                overall=round(overall, 2),
                suggestions=suggestions,
                passed=overall >= self.pass_threshold
            )

        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.warning(f"解析评估响应失败: {e}, 原始响应: {response[:200]}")
            # 返回默认评分
            return ValidationScore(
                relevance=5,
                accuracy=5,
                completeness=5,
                fluency=5,
                context_awareness=5,
                overall=5.0,
                suggestions=["评估解析失败，使用默认评分"],
                passed=False
            )

    def batch_validate(
        self,
        conversations: List[List[Dict[str, str]]]
    ) -> List[ValidationScore]:
        """
        批量验证多个对话

        Args:
            conversations: 对话列表

        Returns:
            List[ValidationScore]: 评估结果列表
        """
        results = []
        for i, conv in enumerate(conversations):
            logger.info(f"验证对话 {i+1}/{len(conversations)}")
            result = self.execute(conv)
            results.append(result)
        return results

    def generate_report(self, scores: List[ValidationScore]) -> Dict[str, Any]:
        """
        生成验证报告

        Args:
            scores: 评分结果列表

        Returns:
            Dict: 验证报告
        """
        if not scores:
            return {"error": "没有评分数据"}

        # 计算统计数据
        total = len(scores)
        passed = sum(1 for s in scores if s.passed)
        avg_overall = sum(s.overall for s in scores) / total

        avg_scores = {
            "relevance": sum(s.relevance for s in scores) / total,
            "accuracy": sum(s.accuracy for s in scores) / total,
            "completeness": sum(s.completeness for s in scores) / total,
            "fluency": sum(s.fluency for s in scores) / total,
            "context_awareness": sum(s.context_awareness for s in scores) / total,
        }

        # 收集所有建议
        all_suggestions = []
        for s in scores:
            all_suggestions.extend(s.suggestions)

        return {
            "summary": {
                "total": total,
                "passed": passed,
                "failed": total - passed,
                "pass_rate": f"{(passed/total)*100:.1f}%",
                "average_score": round(avg_overall, 2)
            },
            "average_scores": {k: round(v, 2) for k, v in avg_scores.items()},
            "suggestions": list(set(all_suggestions)),  # 去重
            "details": [s.to_dict() for s in scores]
        }
