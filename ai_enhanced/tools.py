"""
智能体工具定义

定义 ConversationAgent 可以调用的工具
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum


class ToolCategory(Enum):
    """工具类别"""
    CHAT = "chat"
    NAVIGATION = "nav"
    VALIDATION = "validate"
    UTILITY = "util"


def _param(type_: str, desc: str, **kwargs) -> Dict[str, Any]:
    """创建参数定义"""
    p = {"type": type_, "description": desc}
    p.update(kwargs)
    return p


@dataclass
class ToolDefinition:
    """工具定义"""
    name: str
    description: str
    category: ToolCategory
    parameters: Dict[str, Any] = field(default_factory=dict)
    required: List[str] = field(default_factory=list)

    def to_claude_tool(self) -> Dict[str, Any]:
        """转换为 Claude API 格式"""
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": {
                "type": "object",
                "properties": self.parameters,
                "required": self.required
            }
        }


# 工具定义
ALL_TOOLS: List[ToolDefinition] = [
    # 聊天工具
    ToolDefinition("send_message", "向 Chatbot 发送消息", ToolCategory.CHAT,
                   {"message": _param("string", "消息内容")}, ["message"]),

    ToolDefinition("wait_for_response", "等待 AI 响应完成", ToolCategory.CHAT,
                   {"timeout": _param("integer", "超时时间(秒)", default=60)}),

    ToolDefinition("get_conversation_history", "获取对话历史", ToolCategory.CHAT),

    ToolDefinition("clear_conversation", "清空对话", ToolCategory.CHAT),

    # 导航工具
    ToolDefinition("navigate_to_chat", "导航到 Chatbot 页面", ToolCategory.NAVIGATION),

    ToolDefinition("login", "登录系统", ToolCategory.NAVIGATION,
                   {"username": _param("string", "用户名"),
                    "password": _param("string", "密码")},
                   ["username", "password"]),

    ToolDefinition("take_screenshot", "截取屏幕截图", ToolCategory.NAVIGATION,
                   {"name": _param("string", "截图名称", default="screenshot")}),

    # 验证工具
    ToolDefinition("validate_response", "验证 AI 响应质量", ToolCategory.VALIDATION,
                   {"user_message": _param("string", "用户消息"),
                    "ai_response": _param("string", "AI 响应"),
                    "context": _param("array", "对话上下文", items={"type": "object"})},
                   ["user_message", "ai_response"]),

    ToolDefinition("check_element_exists", "检查页面元素是否存在", ToolCategory.VALIDATION,
                   {"selector": _param("string", "CSS 选择器")}, ["selector"]),

    # 辅助工具
    ToolDefinition("report_issue", "报告问题", ToolCategory.UTILITY,
                   {"issue_type": _param("string", "问题类型",
                                         enum=["bug", "unexpected_behavior", "performance", "ui_issue"]),
                    "description": _param("string", "问题描述"),
                    "severity": _param("string", "严重程度", enum=["low", "medium", "high", "critical"])},
                   ["issue_type", "description", "severity"]),

    ToolDefinition("log_info", "记录日志", ToolCategory.UTILITY,
                   {"message": _param("string", "日志消息"),
                    "level": _param("string", "日志级别", enum=["debug", "info", "warning", "error"], default="info")},
                   ["message"]),

    ToolDefinition("complete_test", "标记测试完成", ToolCategory.UTILITY,
                   {"success": _param("boolean", "是否成功"),
                    "summary": _param("string", "结果摘要"),
                    "issues": _param("array", "问题列表", items={"type": "object"})},
                   ["success", "summary"]),
]

# 工具名称映射（便于快速查找）
_TOOLS_BY_NAME = {tool.name: tool for tool in ALL_TOOLS}


def get_claude_tools() -> List[Dict[str, Any]]:
    """获取 Claude API 格式的工具列表"""
    return [tool.to_claude_tool() for tool in ALL_TOOLS]


def get_tools_by_category(category: ToolCategory) -> List[ToolDefinition]:
    """按类别获取工具"""
    return [tool for tool in ALL_TOOLS if tool.category == category]


def get_tool_by_name(name: str) -> Optional[ToolDefinition]:
    """按名称获取工具"""
    return _TOOLS_BY_NAME.get(name)
