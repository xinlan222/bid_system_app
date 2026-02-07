"""AI Agent for analyzing bid documents."""

from pydantic_ai import Agent, RunContext

from app.db.models.bid_document import BidDocument


# Dependency injection for the agent
class BidAnalysisDeps:
    """Dependencies for bid analysis agent."""

    def __init__(
        self,
        document_id: str,
        filename: str,
    ) -> None:
        """Initialize dependencies.

        Args:
            document_id: Document ID
            filename: Document filename
        """
        self.document_id = document_id
        self.filename = filename


# Create the agent
bid_analysis_agent = Agent[BidAnalysisDeps, str](
    model="openai:gpt-4o-mini",
    system_prompt="""你是一个专业的招标文件分析专家。你的任务是分析招标文件并提取关键信息。

请从招标文件中提取以下信息：

1. **项目基本信息**：
   - 项目名称
   - 项目编号
   - 招标单位/招标代理
   - 招标预算金额
   - 开标时间
   - 投标截止时间
   - 投标保证金金额

2. **资格要求**：
   - 企业资质要求（如：建筑工程施工总承包一级）
   - 人员要求（如：项目经理、技术负责人）
   - 业绩要求（如：近三年类似项目业绩）
   - 其他资格要求（如：安全生产许可证、ISO认证等）

3. **技术要求**：
   - 技术标准要求
   - 工期要求
   - 质量标准
   - 其他技术要求

4. **商务要求**：
   - 投标保证金缴纳方式
   - 投标文件要求
   - 其他商务条款

5. **评分标准**：
   - 技术评分标准
   - 商务评分标准
   - 价格评分标准

6. **风险点分析**：
   - 潜在风险点（如：工期紧张、要求过高等）
   - 风险等级评估（low/medium/high）

7. **建议**：
   - 投标建议
   - 需要特别注意的事项

请以 JSON 格式返回分析结果，包含以上所有字段。如果某项信息在文件中未找到，请标注为 "未提及"。

JSON 格式示例：
```json
{
  "project_name": "项目名称",
  "project_number": "项目编号",
  "bidding_agency": "招标单位",
  "bid_budget": "预算金额",
  "bid_deadline": "开标时间",
  "submission_deadline": "投标截止时间",
  "bid_bond_amount": "保证金金额",
  "qualification_requirements": ["资质要求1", "资质要求2"],
  "technical_requirements": ["技术要求1", "技术要求2"],
  "business_requirements": ["商务要求1", "商务要求2"],
  "assessment_criteria": ["评分标准1", "评分标准2"],
  "risk_points": ["风险点1", "风险点2"],
  "risk_level": "low",
  "recommendations": ["建议1", "建议2"],
  "summary": "项目总结"
}
```

请确保返回完整的 JSON 格式，不要包含其他文字说明。""",
)
