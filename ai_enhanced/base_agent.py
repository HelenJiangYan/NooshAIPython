"""
基础智能体类

提供智能体的核心功能：
- Claude API 调用封装
- 对话历史管理
- 工具调用支持
"""

import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv
from anthropic import Anthropic
from utils.logger import test_logger as logger

# 确保加载 .env 文件
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(env_path, override=True)


@dataclass
class AgentMessage:
    """智能体消息"""
    role: str  # "user", "assistant"
    content: str


@dataclass
class AgentConfig:
    """智能体配置"""
    model: str = "claude-sonnet-4-5-20250929"
    max_tokens: int = 4096
    temperature: float = 0.7


class BaseAgent(ABC):
    """
    基础智能体类

    所有智能体都应继承此类，提供：
    - Claude API 调用
    - 对话历史管理
    - 统一的思考接口
    """

    def __init__(
        self,
        name: str,
        system_prompt: str,
        config: Optional[AgentConfig] = None
    ):
        """
        初始化智能体

        Args:
            name: 智能体名称
            system_prompt: 系统提示词
            config: 智能体配置
        """
        self.name = name
        self.system_prompt = system_prompt
        self.config = config or AgentConfig()
        self.conversation_history: List[AgentMessage] = []

        # 初始化 Anthropic 客户端
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError(
                "未找到 ANTHROPIC_API_KEY，请在 .env 文件中配置"
            )

        self.client = Anthropic(api_key=api_key)
        logger.info(f"智能体 [{self.name}] 初始化完成")

    def think(self, user_input: str) -> str:
        """
        智能体思考并返回响应

        Args:
            user_input: 用户输入

        Returns:
            str: 智能体响应
        """
        # 添加用户消息到历史
        self.conversation_history.append(
            AgentMessage(role="user", content=user_input)
        )

        # 构建消息列表
        messages = [
            {"role": msg.role, "content": msg.content}
            for msg in self.conversation_history
        ]

        try:
            # 调用 Claude API
            response = self.client.messages.create(
                model=self.config.model,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                system=self.system_prompt,
                messages=messages
            )

            # 提取响应文本
            assistant_msg = response.content[0].text

            # 添加助手响应到历史
            self.conversation_history.append(
                AgentMessage(role="assistant", content=assistant_msg)
            )

            logger.debug(f"[{self.name}] 响应: {assistant_msg[:100]}...")
            return assistant_msg

        except Exception as e:
            logger.error(f"[{self.name}] API调用失败: {e}")
            raise

    def reset(self):
        """重置对话历史"""
        self.conversation_history = []
        logger.info(f"[{self.name}] 对话历史已重置")

    def get_history(self) -> List[Dict[str, str]]:
        """
        获取对话历史

        Returns:
            List[Dict]: 对话历史列表
        """
        return [
            {"role": msg.role, "content": msg.content}
            for msg in self.conversation_history
        ]

    @abstractmethod
    def execute(self, task: Any) -> Any:
        """
        执行具体任务

        子类必须实现此方法

        Args:
            task: 任务输入

        Returns:
            Any: 任务结果
        """
        pass

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name='{self.name}'>"
