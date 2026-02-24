# Daily Paper 📚

具身智能论文速递 - 自动化学术调研工具

自动从 arXiv 获取具身智能领域最新论文，智能筛选高质量研究，生成结构化中文报告。

## 功能特性

- 🔍 **多源数据采集**：arXiv、Semantic Scholar、GitHub Trending、Hugging Face
- 🎯 **智能筛选**：按新颖性、影响力、工程价值评分
- 📊 **结构化输出**：每篇论文包含技术细节、SOTA对比、落地分析
- 🔄 **多渠道发布**：飞书文档/卡片、Markdown 文件

## 研究方向

| 方向 | 关键词 |
|------|--------|
| VLA / 多模态机器人 | Vision-Language-Action、多模态指令控制 |
| 世界模型 | 视频预测、物理模拟、生成式世界模型 |
| 强化学习 | Robot RL、Imitation Learning、Offline RL |
| 仿真 | Sim2Real、物理仿真、可微仿真 |
| 自动驾驶 | 端到端驾驶、BEV、占用网络 |

## 快速开始

### 1. 获取论文数据

```bash
# arXiv
python scripts/fetch.py --output /tmp/arxiv_papers.json

# Semantic Scholar (重点作者)
python scripts/fetch_semantic_scholar.py --days 7 --output /tmp/s2_papers.json

# GitHub Trending
python scripts/fetch_github.py --output /tmp/github_repos.json
```

### 2. 生成报告

```bash
python scripts/generate_report.py --input /tmp/arxiv_papers.json --output daily-report.md
```

### 3. 发布

**飞书渠道**：
```bash
# 创建新文档
python scripts/feishu.py --input daily-report.md --create --title "论文速递 2026-02-24"

# 写入已有文档
python scripts/feishu.py --input daily-report.md --doc-id <YOUR_DOC_ID>
```

**非飞书渠道**：
直接输出 Markdown 文件内容即可。

## 输出格式

```markdown
# 具身智能论文速递 (2026-02-24)

## 📌 摘要
今日精选 4 篇论文...

## 🔮 Crossing Trend
- 本周证据：...
- 技术迁移：...

## 📚 论文详情

### [论文标题](arXiv链接)
- **一句话摘要**：50字内核心贡献
- **解决的工程/算法瓶颈**：技术细节
- **SOTA 改进点**：带数据支撑
- **工程落地潜力**：硬件/数据需求
- **风险与局限**：具体失效场景
- **应用启示**：可迁移洞见
```

## 作为 OpenClaw Skill 使用

```bash
# 复制到 skills 目录
cp -r . ~/.openclaw/skills/daily-paper

# 或直接在对话中使用
"帮我做今日论文速递"
"本周具身智能领域有什么新论文"
```

## 定时任务

```json
{
  "name": "Daily Paper",
  "schedule": {"kind": "cron", "expr": "0 9 * * *", "tz": "Asia/Shanghai"},
  "sessionTarget": "isolated",
  "payload": {
    "kind": "agentTurn",
    "model": "gemini",
    "message": "执行今日论文速递"
  }
}
```

## 重点关注

**机构**：NVIDIA, DeepMind, Berkeley, Stanford, MIT, Tesla AI, Physical Intelligence

**作者**：Jim Fan, Pieter Abbeel, Sergey Levine, Chelsea Finn, Danijar Hafner

**论文系列**：Dreamer, RT, OpenVLA, ALOHA, JEPA

## License

MIT
