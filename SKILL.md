---
name: daily-paper
description: |
  每日论文速递 - 自动化学术调研工具
  
  自动从 arXiv 获取 VLA、World Model、RL 领域的最新论文，智能筛选高质量研究，生成结构化中文报告并发布到飞书文档。
  
  使用场景：
  - 收到 YouTube 学术论文推荐链接时
  - 用户要求"今日论文"、"论文速递"、"学术调研"
  - 需要追踪 AI/机器人/自动驾驶领域最新研究
  - 定时任务自动执行每日调研
---

# Daily Paper - 每日论文速递

自动化学术调研工具，专注于 AI + Robotics 领域。

## 功能

- **多数据源获取**：
  - arXiv（cs.RO, cs.LG, cs.CV, cs.AI）
  - Papers With Code（带代码的论文）
  - Semantic Scholar（追踪特定作者）
  - GitHub Trending（新开源项目）
  - X/Twitter（研究者动态）
- 智能筛选与主题相关的高质量论文
- 重点关注顶级机构和重要论文系列
- 生成结构化中文报告
- 自动发布到飞书文档

## 执行流程

### 步骤 1：获取数据（多数据源）

**1.1 arXiv（主要来源）**
```bash
python scripts/fetch.py --output /tmp/arxiv_papers.json
```

**1.2 Papers With Code（带代码的论文）**
```bash
python scripts/fetch_pwc.py --output /tmp/pwc_papers.json
```

**1.3 Semantic Scholar（追踪重点作者）**
```bash
python scripts/fetch_semantic_scholar.py --output /tmp/s2_papers.json
```

**1.4 GitHub Trending（新项目）**
```bash
python scripts/fetch_github.py --output /tmp/github_repos.json
```

**1.5 X/Twitter（研究者动态）**
```bash
python scripts/fetch_x.py --output /tmp/x_tweets.json
```
需要配置 bird skill 的 X cookies。

输出 JSON 包含：
- `papers`: 候选论文列表（最多 80 篇）
- `is_priority`: 是否来自重点机构/系列
- `topic_relevance`: 各主题相关性分数
- `primary_topic`: 主要分类（VLA/World Model/RL）

### 步骤 2：筛选论文

从候选中选出 6-12 篇，评分维度：
- Novelty（新颖性）
- Impact（潜在影响力）
- Technical Soundness（技术可信度）
- Reproducibility（可复现性）
- Engineering Value（工程价值）

`is_priority=true` 的论文同等质量下优先。

### 步骤 3：生成报告

保存到 `/workspace/daily-papers/YYYY-MM-DD-cn.md`

报告结构见 [references/report-template.md](references/report-template.md)

### 步骤 4：发布到飞书

```bash
python scripts/feishu.py --input /workspace/daily-papers/YYYY-MM-DD-cn.md --doc-id <DOC_ID>
```

## 配置

### 重点关注机构

```
DeepMind, UC Berkeley/BAIR, NVIDIA, 1X Technologies, Figure AI,
Stanford, MIT, OpenAI, Anthropic, Tesla AI, Physical Intelligence,
Covariant, Meta AI/FAIR, Yann LeCun
```

### 重点论文系列

```
Dreamer 系列, RT 系列, OpenVLA/Octo, ALOHA, JEPA 系列
```

### 筛选主题

- **VLA**: Vision-Language-Action, multimodal robot, instruction following
- **World Model**: world modeling, dynamics model, latent dynamics, dreamer
- **RL**: reinforcement learning, offline RL, model-based RL, imitation learning

## 定时任务配置

```json
{
  "name": "Daily Paper",
  "schedule": {"kind": "cron", "expr": "0 9 * * *", "tz": "Asia/Shanghai"},
  "sessionTarget": "isolated",
  "payload": {
    "kind": "agentTurn",
    "model": "gemini"
  }
}
```

## 输出格式

论文标题格式：`英文原标题（保留关键词的中文翻译）`

示例：
> Dreaming to Assist: Learning to Align with Human Goals via World Models（Dreaming to Assist：通过世界模型学习与人类目标对齐）

每篇论文输出：
- 一句话摘要
- 解决的工程/算法瓶颈
- 核心改进点（≤3条）
- 工程落地潜力
- 风险与局限
- 对自动驾驶/机器人的启示
- 应用场景
- 论文链接（含代码）
