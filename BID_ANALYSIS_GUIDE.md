# 招标文件分析功能 - 使用指南

## 🎯 功能概述

已实现招标文件分析功能，支持：
- ✅ 文件上传（PDF、DOCX、TXT）
- ✅ 文件内容自动提取
- ✅ AI 智能分析（使用 OpenAI）
- ✅ 结构化分析报告
- ✅ 分析历史记录

---

## 📚 API 端点

### 1. 上传招标文件

```bash
POST /api/v1/bid-documents/upload
```

**参数：**
- `file`: 文件（multipart/form-data）
- `project_name`: 项目名称（可选）
- `bidder_name`: 投标单位（可选）

**示例：**
```bash
curl -X POST http://localhost:8000/api/v1/bid-documents/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@tender.pdf" \
  -F "project_name=XX项目招标"
```

**返回：**
```json
{
  "id": "uuid",
  "filename": "stored_filename.pdf",
  "original_filename": "tender.pdf",
  "file_size": 12345,
  "file_type": "application/pdf",
  "project_name": "XX项目招标",
  "analysis_status": "pending",
  "uploaded_at": "2026-02-07T16:00:00Z"
}
```

### 2. 分析招标文件

```bash
POST /api/v1/bid-documents/{doc_id}/analyze
```

**示例：**
```bash
curl -X POST http://localhost:8000/api/v1/bid-documents/{doc_id}/analyze \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**返回：**
```json
{
  "id": "uuid",
  "analysis_status": "completed",
  "analysis_result": {
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
    "risk_level": "medium",
    "recommendations": ["建议1", "建议2"],
    "summary": "项目总结"
  },
  "analyzed_at": "2026-02-07T16:00:00Z"
}
```

### 3. 查看文档列表

```bash
GET /api/v1/bid-documents?skip=0&limit=100
```

### 4. 查看单个文档

```bash
GET /api/v1/bid-documents/{doc_id}
```

### 5. 删除文档

```bash
DELETE /api/v1/bid-documents/{doc_id}
```

---

## 🔧 配置要求

### 环境变量配置

编辑 `backend/.env` 文件：

```bash
# OpenAI API Key（必需）
OPENAI_API_KEY=your-openai-api-key-here

# AI 模型配置
AI_MODEL=gpt-4o-mini
AI_TEMPERATURE=0.7
```

**获取 OpenAI API Key：**
1. 访问：https://platform.openai.com/api-keys
2. 创建新 API Key
3. 复制到 `backend/.env` 文件
4. 重启服务：`bid-system restart`

---

## 🧪 快速测试

### 1. 创建测试用户并登录

```bash
# 注册
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test123!@#",
    "full_name": "测试用户"
  }'

# 登录
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test123!@#"
  }'

# 返回的 access_token 用于后续请求
```

### 2. 上传测试文件

创建一个简单的测试文件 `test_tender.txt`：

```txt
XX市公共资源交易中心
关于XX项目的招标公告

项目名称：XX市XX道路建设工程
项目编号：XX-2026-001
招标单位：XX市公共资源交易中心
预算金额：500万元
开标时间：2026年2月20日 14:00
投标截止时间：2026年2月19日 17:00
投标保证金：10万元

资格要求：
1. 具备市政公用工程施工总承包一级资质
2. 项目经理具备一级建造师资质
3. 近三年内完成过类似项目业绩

技术要求：
1. 工期要求：180日历天
2. 质量标准：合格

商务要求：
1. 投标保证金需在开标前3天缴纳
```

上传文件：

```bash
TOKEN="your_access_token"

curl -X POST http://localhost:8000/api/v1/bid-documents/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@test_tender.txt" \
  -F "project_name=XX道路建设工程"
```

### 3. 分析文件

```bash
DOC_ID="document_id_from_upload_response"

curl -X POST http://localhost:8000/api/v1/bid-documents/$DOC_ID/analyze \
  -H "Authorization: Bearer $TOKEN"
```

### 4. 查看分析结果

```bash
curl http://localhost:8000/api/v1/bid-documents/$DOC_ID \
  -H "Authorization: Bearer $TOKEN" | jq .
```

---

## 📊 AI 分析内容

AI 会从招标文件中提取：

### 1. 项目基本信息
- 项目名称
- 项目编号
- 招标单位
- 预算金额
- 开标时间
- 投标截止时间
- 投标保证金

### 2. 资格要求
- 企业资质要求
- 人员要求
- 业绩要求
- 其他资格要求

### 3. 技术要求
- 技术标准
- 工期要求
- 质量标准

### 4. 商务要求
- 保证金缴纳方式
- 投标文件要求
- 其他商务条款

### 5. 评分标准
- 技术评分
- 商务评分
- 价格评分

### 6. 风险点分析
- 潜在风险点
- 风险等级（low/medium/high）

### 7. 投标建议
- 投标策略建议
- 需要特别注意的事项

---

## 🛠️ 故障排查

### 分析失败

**错误信息：**
```
"OPENAI_API_KEY not configured"
```

**解决方法：**
1. 检查 `backend/.env` 文件中 `OPENAI_API_KEY` 是否配置
2. 确认 API Key 有效
3. 重启服务：`bid-system restart`

### 文件提取失败

**支持的文件格式：**
- `.pdf` - PDF 文档
- `.docx` - Word 文档
- `.txt` - 纯文本

**不支持：**
- `.doc` - 旧版 Word 格式（请转换为 .docx）

### 服务状态检查

```bash
bid-system status
bid-system health
```

---

## 📝 下一步优化方向

- [ ] 添加文件格式验证
- [ ] 支持更多文件格式（.doc）
- [ ] 添加分析进度跟踪
- [ ] 支持批量上传和分析
- [ ] 添加分析报告导出（PDF/Excel）
- [ ] 添加投标建议模板
- [ ] 添加历史数据分析

---

**最后更新：** 2026-02-07
