"""
多轮对话测试数据
定义各种对话场景和预期行为
"""

from typing import List, Optional, Literal
from dataclasses import dataclass


@dataclass
class ContextCheck:
    """上下文检查配置"""
    should_reference: List[str]
    mode: Literal['any', 'all'] = 'any'


@dataclass
class QualityCheck:
    """质量检查配置"""
    min_length: Optional[int] = None
    min_words: Optional[int] = None
    forbidden_phrases: Optional[List[str]] = None


@dataclass
class ConversationTurn:
    """对话轮次"""
    user_message: str
    expected_keywords: Optional[List[str]] = None
    context_check: Optional[ContextCheck] = None
    quality_check: Optional[QualityCheck] = None


@dataclass
class ConversationScenario:
    """对话场景"""
    name: str
    description: str
    turns: List[ConversationTurn]


# 上下文连续性测试场景
CONTEXT_CONTINUITY_SCENARIOS = [
    ConversationScenario(
        name='代词引用测试',
        description='测试AI是否能理解代词引用之前提到的内容',
        turns=[
            ConversationTurn(
                user_message='list all my projects',
                expected_keywords=['project', 'Projects Associated'],
                quality_check=QualityCheck(min_length=100)
            ),
            ConversationTurn(
                user_message='copy the first one',
                expected_keywords=['copy', 'duplicate', 'clone'],
                context_check=ContextCheck(
                    should_reference=['project'],
                    mode='any'
                )
            ),
            ConversationTurn(
                user_message='what is its status?',
                expected_keywords=['status'],
                context_check=ContextCheck(
                    should_reference=['project'],
                    mode='any'
                )
            )
        ]
    ),
    ConversationScenario(
        name='跨多轮状态记忆',
        description='测试AI是否能记住3轮以上的对话上下文',
        turns=[
            ConversationTurn(
                user_message='create a new project called Marketing Campaign 2024',
                expected_keywords=['marketing', 'campaign', '2024']
            ),
            ConversationTurn(
                user_message='add a task named Design Review',
                expected_keywords=['task', 'design', 'review'],
                context_check=ContextCheck(
                    should_reference=['marketing'],
                    mode='any'
                )
            ),
            ConversationTurn(
                user_message='set the priority to high',
                expected_keywords=['priority', 'high'],
                context_check=ContextCheck(
                    should_reference=['task', 'design'],
                    mode='any'
                )
            ),
            ConversationTurn(
                user_message='assign it to John',
                expected_keywords=['assign', 'john'],
                context_check=ContextCheck(
                    should_reference=['task', 'design'],
                    mode='any'
                )
            ),
            ConversationTurn(
                user_message='when is the deadline for this task?',
                expected_keywords=['deadline', 'date'],
                context_check=ContextCheck(
                    should_reference=['design', 'review'],
                    mode='any'
                )
            )
        ]
    )
]


# 逻辑一致性测试场景
LOGIC_CONSISTENCY_SCENARIOS = [
    ConversationScenario(
        name='信息不矛盾测试',
        description='测试AI前后回答的一致性',
        turns=[
            ConversationTurn(
                user_message='create a project named Alpha',
                expected_keywords=['alpha', 'project', 'create']
            ),
            ConversationTurn(
                user_message='what projects do I have?',
                expected_keywords=['alpha'],
                context_check=ContextCheck(
                    should_reference=['alpha'],
                    mode='any'
                )
            ),
            ConversationTurn(
                user_message='tell me about project Alpha',
                expected_keywords=['alpha'],
                context_check=ContextCheck(
                    should_reference=['project'],
                    mode='any'
                )
            )
        ]
    ),
    ConversationScenario(
        name='状态变化追踪',
        description='测试AI是否能追踪实体状态的变化',
        turns=[
            ConversationTurn(
                user_message='create a task called Update Documentation',
                expected_keywords=['task', 'documentation', 'update']
            ),
            ConversationTurn(
                user_message='what is the status of this task?',
                expected_keywords=['status'],
                context_check=ContextCheck(
                    should_reference=['task', 'documentation'],
                    mode='any'
                )
            ),
            ConversationTurn(
                user_message='mark it as completed',
                expected_keywords=['complet', 'done', 'finish'],
                context_check=ContextCheck(
                    should_reference=['task'],
                    mode='any'
                )
            ),
            ConversationTurn(
                user_message='check the status again',
                expected_keywords=['status', 'complet'],
                context_check=ContextCheck(
                    should_reference=['task'],
                    mode='any'
                )
            )
        ]
    )
]


# 上下文切换测试场景
CONTEXT_SWITCHING_SCENARIOS = [
    ConversationScenario(
        name='话题转换测试',
        description='测试AI在切换话题后是否能正确处理新上下文',
        turns=[
            ConversationTurn(
                user_message='tell me about my projects',
                expected_keywords=['project']
            ),
            ConversationTurn(
                user_message='actually, I want to check my tasks instead',
                expected_keywords=['task'],
                context_check=ContextCheck(
                    should_reference=[],  # 不应该过多引用项目
                    mode='any'
                )
            ),
            ConversationTurn(
                user_message='show me the high priority ones',
                expected_keywords=['priority', 'high', 'task'],
                context_check=ContextCheck(
                    should_reference=['task'],
                    mode='any'
                )
            )
        ]
    ),
    ConversationScenario(
        name='多主题并行',
        description='测试AI在多个主题间切换的能力',
        turns=[
            ConversationTurn(
                user_message='I have a project called Website Redesign',
                expected_keywords=['website', 'redesign', 'project']
            ),
            ConversationTurn(
                user_message='I also have a task to review the budget',
                expected_keywords=['task', 'budget', 'review']
            ),
            ConversationTurn(
                user_message='tell me about the website project',
                expected_keywords=['website', 'redesign'],
                context_check=ContextCheck(
                    should_reference=['website', 'redesign'],
                    mode='any'
                )
            ),
            ConversationTurn(
                user_message='now tell me about the budget task',
                expected_keywords=['budget', 'task'],
                context_check=ContextCheck(
                    should_reference=['budget', 'task'],
                    mode='any'
                )
            )
        ]
    )
]


# 错误恢复测试场景
ERROR_RECOVERY_SCENARIOS = [
    ConversationScenario(
        name='无效输入后恢复',
        description='测试AI在收到无效输入后能否继续正常对话',
        turns=[
            ConversationTurn(
                user_message='list my projects',
                expected_keywords=['project']
            ),
            ConversationTurn(
                user_message='xyzabc123invalid456',
                expected_keywords=[],  # 无效输入
                quality_check=QualityCheck(
                    forbidden_phrases=[]  # 不应该崩溃
                )
            ),
            ConversationTurn(
                user_message='copy the first project',
                expected_keywords=['copy', 'project'],
                context_check=ContextCheck(
                    should_reference=['project'],
                    mode='any'
                )
            )
        ]
    ),
    ConversationScenario(
        name='澄清请求测试',
        description='测试AI在信息不明确时的处理',
        turns=[
            ConversationTurn(
                user_message='create a project',
                expected_keywords=['project', 'name']  # 应该询问项目名
            ),
            ConversationTurn(
                user_message='the name is Mobile App Development',
                expected_keywords=['mobile', 'app', 'development'],
                context_check=ContextCheck(
                    should_reference=['project'],
                    mode='any'
                )
            ),
            ConversationTurn(
                user_message='confirm the details',
                expected_keywords=['mobile', 'app', 'development'],
                context_check=ContextCheck(
                    should_reference=['mobile', 'app'],
                    mode='any'
                )
            )
        ]
    )
]


# 复杂对话流程测试场景
COMPLEX_CONVERSATION_SCENARIOS = [
    ConversationScenario(
        name='完整项目管理流程',
        description='模拟真实的项目管理对话流程',
        turns=[
            ConversationTurn(
                user_message='I want to start a new marketing project',
                expected_keywords=['marketing', 'project']
            ),
            ConversationTurn(
                user_message='add three tasks: content creation, design, and review',
                expected_keywords=['task', 'content', 'design', 'review'],
                context_check=ContextCheck(
                    should_reference=['project', 'marketing'],
                    mode='any'
                )
            ),
            ConversationTurn(
                user_message='set content creation as high priority',
                expected_keywords=['content', 'priority', 'high'],
                context_check=ContextCheck(
                    should_reference=['task'],
                    mode='any'
                )
            ),
            ConversationTurn(
                user_message='what tasks do I have in the marketing project?',
                expected_keywords=['task', 'marketing', 'content', 'design', 'review'],
                context_check=ContextCheck(
                    should_reference=['marketing', 'project'],
                    mode='all'
                )
            ),
            ConversationTurn(
                user_message='mark the design task as in progress',
                expected_keywords=['design', 'progress'],
                context_check=ContextCheck(
                    should_reference=['task'],
                    mode='any'
                )
            )
        ]
    )
]


# 所有场景的集合
ALL_CONVERSATION_SCENARIOS = {
    'context_continuity': CONTEXT_CONTINUITY_SCENARIOS,
    'logic_consistency': LOGIC_CONSISTENCY_SCENARIOS,
    'context_switching': CONTEXT_SWITCHING_SCENARIOS,
    'error_recovery': ERROR_RECOVERY_SCENARIOS,
    'complex': COMPLEX_CONVERSATION_SCENARIOS
}
