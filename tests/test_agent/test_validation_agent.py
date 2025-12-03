"""
验证智能体单元测试

测试 ValidationAgent 类的基本功能
注意：这些是单元测试，不涉及浏览器操作
"""

import pytest
import allure
from ai_enhanced.validation_agent import ValidationAgent, ValidationScore


@allure.feature("AI智能体")
@allure.story("验证智能体")
@pytest.mark.unit
class TestValidationAgent:
    """ValidationAgent 单元测试"""

    @pytest.fixture
    def validator(self):
        """创建验证智能体实例（Mock模式）"""
        return ValidationAgent(pass_threshold=6.0, mock_mode=True)

    @allure.title("测试智能体初始化")
    @pytest.mark.agent
    def test_initialization(self, validator):
        """测试智能体正确初始化"""
        assert validator.name == "ValidationAgent"
        assert validator.pass_threshold == 6.0
        assert validator.mock_mode is True

    @allure.title("测试Mock模式评估")
    @pytest.mark.agent
    def test_mock_evaluation(self, validator):
        """测试Mock模式的基本评估功能"""
        result = validator.validate_single_response(
            user_message="什么是Python？",
            ai_response="Python是一种高级编程语言，广泛用于Web开发、数据科学和人工智能。"
        )

        assert isinstance(result, ValidationScore)
        assert 0 <= result.overall <= 10
        assert hasattr(result, 'passed')
        print(f"\n评估结果: overall={result.overall}, passed={result.passed}")

    @allure.title("测试高质量响应")
    @pytest.mark.agent
    def test_good_response(self, validator):
        """高质量响应应该得高分"""
        result = validator.validate_single_response(
            user_message="Python是什么？",
            ai_response="Python是一种高级、解释型、通用的编程语言。"
                       "它由Guido van Rossum于1991年创建，以代码可读性著称。"
                       "Python支持多种编程范式，广泛应用于Web开发、数据科学、AI等领域。"
        )

        # 长响应应该有较高的完整性评分
        assert result.completeness >= 7

    @allure.title("测试低质量响应")
    @pytest.mark.agent
    def test_poor_response(self, validator):
        """低质量响应应该得低分"""
        result = validator.validate_single_response(
            user_message="如何实现排序算法？",
            ai_response="好的。"
        )

        # 过短响应应该有较低的完整性评分
        assert result.completeness <= 5

    @allure.title("测试ValidationScore数据结构")
    @pytest.mark.agent
    def test_validation_score_structure(self):
        """测试ValidationScore的属性和方法"""
        score = ValidationScore(
            accuracy=8,
            relevance=9,
            completeness=8,
            fluency=9,
            context_awareness=8,
            overall=8.4,
            suggestions=["建议更详细"],
            passed=True
        )

        assert score.accuracy == 8
        assert score.overall == 8.4
        assert score.passed is True

        # 测试 to_dict 方法
        score_dict = score.to_dict()
        assert "accuracy" in score_dict
        assert "overall" in score_dict
