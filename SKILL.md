---
name: daily-paper
description: |
  具身智能论文速递 - 自动化学术调研工具
  
  自动从 arXiv 获取具身智能领域最新论文，智能筛选高质量研究，生成结构化中文报告。
  
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

**每篇论文的固定输出结构**：

⚠️ **重要**：写每篇论文前，必须先用 web_fetch 读取论文的 arXiv HTML 版本（如 https://arxiv.org/html/2602.18224v1），理解技术细节后再写。只看 abstract 写出来的内容会很浅。

```
### [论文标题](arXiv链接)
- **一句话摘要**：50字以内概括核心贡献
- **解决的工程/算法瓶颈**：（50-100字）具体说明针对什么问题，为什么之前的方法解决不了，要有技术细节
- **相对 SOTA 的核心改进点**（≤3条）：每条要具体，最好有数据支撑（如「LIBERO 上 98.5% 成功率」）
  1. 改进点1（带具体数据/对比）
  2. 改进点2
  3. 改进点3
- **工程落地潜力与前置条件**：（50-100字）分「潜力」和「前置条件」两部分写，要具体到硬件要求、数据需求等
- **风险与局限**：（50-100字）不是泛泛而谈，要指出具体在什么场景/任务下会失效
- **对自动驾驶/机器人系统的启示**：（50-100字）不是复述论文，而是从工程师视角提炼可迁移的洞见，可以类比其他领域（如 LLM、自动驾驶）的经验
- **潜在应用场景**：具体应用方向
- **论文链接**：arXiv链接（有代码附上GitHub）
```

**Crossing Trend 格式**：
- 本周证据：哪些论文体现了这个趋势
- 技术迁移：哪项技术从哪个领域迁移过来
- 趋势判断：基于事实的客观判断

### 步骤 4：发布

**根据当前渠道自动选择输出方式**：

#### 飞书渠道
1. **创建或使用飞书文档**：
   - 如果用户未指定文档 ID，使用飞书 API 创建新文档
   - 如果用户指定了文档 ID/链接，写入该文档
   - 新内容插入文档顶部

```bash
# 创建新文档并写入
python scripts/feishu.py --input /workspace/daily-papers/YYYY-MM-DD-cn.md --create --title "论文速递 YYYY-MM-DD"

# 写入已有文档
python scripts/feishu.py --input /workspace/daily-papers/YYYY-MM-DD-cn.md --doc-id <用户提供的DOC_ID>
```

2. **发送飞书卡片**（可选）：
```bash
python /workspace/scripts/feishu_card.py --to <CHAT_ID> --template daily-paper --data <JSON_FILE>
```

#### 非飞书渠道（Telegram/Discord/终端等）
直接输出 Markdown 文档内容，或保存到本地文件：

```bash
# 保存到本地
cat /workspace/daily-papers/YYYY-MM-DD-cn.md

# 或直接在消息中输出 Markdown 格式的报告
```

**输出示例**（非飞书）：
```markdown
# 具身智能论文速递 (2026-02-24)

## 📌 摘要
今日精选 4 篇论文，覆盖 VLA、世界模型、强化学习领域...

## 🔮 Crossing Trend
...

## 📚 论文详情
### 🤖 VLA / 多模态
#### [论文标题](https://arxiv.org/abs/xxxx)
...
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

## 用户配置（可选）

用户可以在对话中指定：
- **飞书文档 ID**：`--doc-id WPmJdLKAvohbGaxBRmLc08MVn5f` 或直接粘贴文档链接
- **输出格式**：`--format md` 强制输出 Markdown
- **推送对象**：`--to <open_id>` 指定飞书消息接收人

如果未指定，根据当前会话渠道自动选择输出方式。

## Prompt 文件

- 日报卡片：`/workspace/prompts/daily-paper-card.md`
- 周报卡片：`/workspace/prompts/weekly-paper-card.md`

## 定时任务示例

```json
{
  "name": "Daily Paper",
  "schedule": {"kind": "cron", "expr": "0 9 * * *", "tz": "Asia/Shanghai"},
  "sessionTarget": "isolated",
  "payload": {
    "kind": "agentTurn",
    "model": "gemini",
    "message": "执行今日论文速递，输出到飞书文档",
    "deliver": true,
    "channel": "feishu",
    "to": "<your_open_id>"
  }
}
```
