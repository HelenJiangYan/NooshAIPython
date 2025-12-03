"""
AI智能体测试演示 - 作为pytest测试运行

运行方式：
    pytest tests/demo_agent_test.py -v -s

这个演示展示什么是"智能体测试"：
- 传统测试：人工编写固定的测试步骤
- 智能体测试：AI自主决定如何测试，能理解和验证对话质量
"""

import time
import pytest


def print_banner(text: str):
    """打印横幅"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


def print_step(step: int, text: str):
    """打印步骤"""
    print(f"\n[步骤 {step}] {text}")


def print_agent_thought(thought: str):
    """打印智能体思考过程"""
    print(f"   [思考] {thought}")


def print_agent_action(action: str):
    """打印智能体行动"""
    print(f"   [行动] {action}")


def print_result(label: str, value: str):
    """打印结果"""
    print(f"   [结果] {label}: {value}")


class SimpleTestAgent:
    """
    简单的测试智能体演示

    这个智能体可以：
    1. 控制浏览器执行操作
    2. 发送消息给AI聊天机器人
    3. 分析和验证AI的响应
    4. 自主决定测试是否通过
    """

    def __init__(self, chatbot_page):
        self.chatbot = chatbot_page
        self.conversation = []

    def think(self, situation: str) -> str:
        """智能体的思考过程（模拟）"""
        thoughts = {
            "start": "我需要测试这个AI聊天机器人。让我先发送一个问候语看看它的反应。",
            "greeting_sent": "消息已发送，让我等待AI的响应...",
            "analyzing": "让我分析AI的响应质量：是否礼貌？是否相关？是否有帮助？",
            "follow_up": "第一轮对话成功。让我问一个更具体的问题，测试AI的专业能力。",
            "final": "测试完成。让我总结整体对话质量。"
        }
        return thoughts.get(situation, "让我思考下一步...")

    def send_message(self, message: str) -> str:
        """发送消息并获取响应"""
        self.chatbot.send_message(message)
        self.conversation.append({"role": "user", "content": message})

        ai_response = self.chatbot.get_last_ai_message()
        self.conversation.append({"role": "assistant", "content": ai_response})

        return ai_response

    def validate_response(self, user_msg: str, ai_response: str) -> dict:
        """验证AI响应质量（简单规则模拟）"""
        score = {
            "relevance": 0,
            "helpfulness": 0,
            "politeness": 0,
            "overall": 0,
            "passed": False,
            "reason": ""
        }

        response_lower = ai_response.lower()

        # 礼貌性检查
        polite_words = ["你好", "您好", "请", "谢谢", "帮助", "help", "hi", "hello", "glad", "happy"]
        score["politeness"] = min(10, sum(3 for w in polite_words if w in response_lower))

        # 相关性检查
        if len(ai_response) > 20:
            score["relevance"] = 7
        if len(ai_response) > 100:
            score["relevance"] = 9

        # 有用性检查
        if "?" in ai_response or "吗" in ai_response:
            score["helpfulness"] += 3
        if len(ai_response) > 50:
            score["helpfulness"] += 4

        score["helpfulness"] = min(10, score["helpfulness"])

        # 综合评分
        score["overall"] = (score["relevance"] + score["helpfulness"] + score["politeness"]) / 3
        score["passed"] = score["overall"] >= 5

        score["reason"] = "AI响应质量良好" if score["passed"] else "AI响应质量不足"

        return score

    def run_test(self, test_messages: list) -> dict:
        """执行测试场景"""
        results = []

        for i, msg in enumerate(test_messages, 1):
            print_step(i, f"发送消息: '{msg}'")

            # 思考
            thought = self.think("start") if i == 1 else self.think("follow_up")
            print_agent_thought(thought)

            # 行动
            print_agent_action("输入消息并发送")
            ai_response = self.send_message(msg)
            print_result("AI响应", ai_response[:100] + "..." if len(ai_response) > 100 else ai_response)

            # 分析
            print_agent_thought(self.think("analyzing"))
            score = self.validate_response(msg, ai_response)
            print_result("响应评分", f"{score['overall']:.1f}/10")
            print_result("测试结果", "PASS" if score["passed"] else "FAIL")

            results.append({
                "user_message": msg,
                "ai_response": ai_response,
                "score": score
            })

            time.sleep(1)

        return {
            "total": len(results),
            "passed": sum(1 for r in results if r["score"]["passed"]),
            "details": results
        }


@pytest.mark.agent
@pytest.mark.integration
class TestAgentDemo:
    """AI智能体测试演示"""

    def test_agent_demo(self, authenticated_page):
        """
        智能体测试演示

        使用 authenticated_page fixture (已登录并导航到AI Assistant)
        """
        chatbot_page = authenticated_page  # authenticated_page 返回的就是 ChatbotPage

        print_banner("AI智能体测试演示")

        print("""
    什么是智能体测试？

    传统自动化测试：
    - 固定的测试步骤
    - 硬编码的断言 (assert response == "预期文本")
    - 无法理解语义

    智能体测试：
    - AI自主决定测试策略
    - 能理解对话内容和质量
    - 可以进行语义验证
    - 能适应不同的AI响应
        """)

        # 创建智能体
        print_banner("创建测试智能体")
        agent = SimpleTestAgent(chatbot_page)
        print("   [Agent] 智能体已就绪")
        print("   [能力] 发送消息、分析响应、验证质量")

        time.sleep(2)

        # 执行测试
        print_banner("智能体执行测试")
        test_messages = [
            "你好，请介绍一下你自己",
            "你能帮我做什么？",
        ]
        results = agent.run_test(test_messages)

        # 报告
        print_banner("测试报告")
        print(f"""
    总测试数: {results['total']}
    通过数量: {results['passed']}
    通过率: {results['passed']/results['total']*100:.0f}%
        """)

        print("\n对话记录:")
        for i, d in enumerate(results['details'], 1):
            print(f"\n   轮次 {i}:")
            print(f"   [用户] {d['user_message']}")
            response_preview = d['ai_response'][:80] + "..." if len(d['ai_response']) > 80 else d['ai_response']
            print(f"   [AI] {response_preview}")
            print(f"   [评分] {d['score']['overall']:.1f}/10 - {d['score']['reason']}")

        print_banner("演示结束")
        print("""
    总结 - 智能体测试的优势:

    1. 自主性：智能体自己决定如何测试
    2. 理解能力：能理解对话语义，不只是文本匹配
    3. 适应性：能处理各种不同的AI响应
    4. 质量评估：能从多个维度评估响应质量

    在实际项目中，ValidationAgent 使用 Claude API:
    - 深度理解对话语义
    - 评估响应准确性、相关性、完整性
    - 提供改进建议
        """)

        # 断言至少有一个测试通过
        assert results['passed'] >= 1, "至少应有一个测试通过"
