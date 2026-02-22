---
name: daily-paper
description: |
  具身智能论文速递 - 自动化学术调研工具
  
  自动从 arXiv 获取具身智能领域最新论文，智能筛选高质量研究，生成结构化中文报告并发布到飞书文档+卡片。
  
  使用场景：
  - 用户要求"今日论文"、"论文速递"、"学术调研"
  - 需要追踪具身智能/自动驾驶领域最新研究
  - 定时任务自动执行每日/每周调研
---

# Daily Paper - 具身智能论文速递

自动化学术调研工具，专注于具身智能（Embodied AI）领域。

## 研究方向（按优先级排序）

1. **VLA / 多模态机器人** - Vision-Language-Action、多模态指令控制
2. **世界模型 (World Model)** - 视频预测、物理模拟、生成式世界模型
3. **强化学习 (RL)** - Robot RL、Imitation Learning、Offline RL
4. **仿真 (Simulation)** - Sim2Real、物理仿真、可微仿真
5. **自动驾驶** - 端到端驾驶、BEV、占用网络

**不收录**：开源工具/框架、效率优化、纯数据集、纯 LLM、纯视觉

## 数据源

- **arXiv**（主要）: cs.RO, cs.LG, cs.CV, cs.AI
- **Semantic Scholar**: 追踪重点作者（Jim Fan, Pieter Abbeel, Sergey Levine 等）
- **GitHub Trending**: 新开源项目
- **Hugging Face**: robotics、RL、world-model 标签

## 执行流程

### 步骤 1：获取数据

```bash
# arXiv
python scripts/fetch.py --output /tmp/arxiv_papers.json

# Semantic Scholar（重点作者）
python scripts/fetch_semantic_scholar.py --days 7 --output /tmp/s2_papers.json

# GitHub Trending
python scripts/fetch_github.py --output /tmp/github_repos.json

# Hugging Face
python scripts/fetch_huggingface.py --output /tmp/huggingface.json
```

### 步骤 2：筛选论文

日报：3-6 篇 | 周报：4-6 篇

评分维度：
- Novelty（新颖性）
- Impact（潜在影响力）
- Engineering Value（工程价值）

重点机构优先：NVIDIA, DeepMind, Berkeley, Stanford, MIT, Tesla AI, Physical Intelligence

### 步骤 3：生成报告

**报告结构**：
```
# 具身智能论文速递 (日期)
## 📌 摘要
## 🔮 Crossing Trend（基于当期论文的客观事实）
## 📚 论文分类详情
  ### 🤖 VLA / 多模态
  ### 🌍 世界模型
  ### 🎮 强化学习
  ### 🚗 自动驾驶
```

**Crossing Trend 格式**：
- 本周证据：哪些论文体现了这个趋势
- 技术迁移：哪项技术从哪个领域迁移过来
- 趋势判断：基于事实的客观判断

### 步骤 4：发布

```bash
# 发布到飞书文档（新内容在顶部）
python scripts/feishu.py --input /workspace/daily-papers/YYYY-MM-DD-cn.md --doc-id <DOC_ID>

# 发送飞书卡片
python /workspace/scripts/feishu_card.py --to <OPEN_ID> --template daily-paper --data <JSON_FILE>
```

## 配置

### 重点关注机构

```
NVIDIA, DeepMind, UC Berkeley/BAIR, Stanford, MIT, 
Tesla AI, Physical Intelligence, 1X Technologies, Figure AI,
OpenAI, Anthropic, Meta AI/FAIR, Covariant
```

### 重点作者（Semantic Scholar 追踪）

```
Jim Fan (Linxi Fan), Pieter Abbeel, Sergey Levine, Chelsea Finn,
Danijar Hafner, Yann LeCun, Kaiming He, Ilya Sutskever
```

### 重点论文系列

```
Dreamer 系列, DreamZero/DreamDojo, RT 系列, OpenVLA/Octo, ALOHA, JEPA 系列
```

## 飞书配置

- **文档 ID**: WPmJdLKAvohbGaxBRmLc08MVn5f
- **文档链接**: https://chj.feishu.cn/docx/WPmJdLKAvohbGaxBRmLc08MVn5f
- **推送对象**: ou_6d4bdf64620355814e6bc0cfd8763602

## Prompt 文件

- 日报卡片：`/workspace/prompts/daily-paper-card.md`
- 周报卡片：`/workspace/prompts/weekly-paper-card.md`

## 定时任务

```json
{
  "name": "Daily Paper",
  "schedule": {"kind": "cron", "expr": "0 9 * * *", "tz": "Asia/Shanghai"},
  "sessionTarget": "isolated",
  "payload": {
    "kind": "agentTurn",
    "model": "gemini",
    "deliver": true,
    "channel": "feishu",
    "to": "ou_6d4bdf64620355814e6bc0cfd8763602"
  }
}
```
