"""
AI Enhanced Testing Module

Provides LLM-based intelligent testing capabilities:
- ValidationAgent: Evaluates AI response quality
- ConversationAgent: Multi-turn conversation testing agent
- TestAgent: Autonomous test agent (planned)
"""

from .base_agent import BaseAgent, AgentConfig, AgentMessage
from .validation_agent import ValidationAgent, ValidationScore
from .conversation_agent import (
    ConversationAgent,
    ConversationScenario,
    ScenarioStep,
    ScenarioStatus,
    ConversationTestResult,
    # 向后兼容别名
    TestScenario,
    TestStep,
    TestStatus,
)
from .tools import (
    ToolDefinition,
    ToolCategory,
    get_claude_tools,
    get_tool_by_name,
    ALL_TOOLS
)

__all__ = [
    # Base
    "BaseAgent",
    "AgentConfig",
    "AgentMessage",
    # Validation
    "ValidationAgent",
    "ValidationScore",
    # Conversation
    "ConversationAgent",
    "ConversationScenario",
    "ScenarioStep",
    "ScenarioStatus",
    "ConversationTestResult",
    # 向后兼容
    "TestScenario",
    "TestStep",
    "TestStatus",
    # Tools
    "ToolDefinition",
    "ToolCategory",
    "get_claude_tools",
    "get_tool_by_name",
    "ALL_TOOLS",
]
