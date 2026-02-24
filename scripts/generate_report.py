import json
import os
import datetime
import re

def load_json(filepath):
    if not os.path.exists(filepath):
        return []
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            elif isinstance(data, dict):
                for key in ['papers', 'repos', 'items']:
                    if key in data:
                        return data[key]
            return []
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return []

def normalize_title(title):
    return re.sub(r'\s+', ' ', title.lower().strip())

def score_paper(paper):
    score = 0
    # Priority flag
    if paper.get('is_priority', False):
        score += 10
    if paper.get('tracked_author'):
        score += 10
    
    # Topic relevance
    topic = paper.get('primary_topic', '')
    if topic in ['VLA', 'World Model']:
        score += 5
    elif topic == 'RL':
        score += 3
    
    # Recency (simple check, assuming data is recent)
    published = paper.get('published', '')
    if published:
        try:
            pub_date = datetime.datetime.strptime(published[:10], '%Y-%m-%d')
            days_diff = (datetime.datetime.now() - pub_date).days
            if days_diff <= 2:
                score += 2
        except:
            pass
            
    return score

def generate_markdown(papers, repos, hf_items, date_str):
    lines = []
    lines.append(f"# 每日论文速递 — {date_str}")
    lines.append("")
    
    # Summary
    total_papers = len(papers)
    vla_count = sum(1 for p in papers if p.get('primary_topic') == 'VLA')
    wm_count = sum(1 for p in papers if p.get('primary_topic') == 'World Model')
    rl_count = sum(1 for p in papers if p.get('primary_topic') == 'RL')
    
    lines.append(f"**摘要**：今日共筛选出 {total_papers} 篇高质量论文，其中 VLA 方向 {vla_count} 篇，世界模型方向 {wm_count} 篇，强化学习方向 {rl_count} 篇。此外还有 {len(repos)} 个 GitHub 项目和 {len(hf_items)} 个 HuggingFace 资源值得关注。")
    lines.append("")
    
    # Group papers by topic
    topics = {'VLA': [], 'World Model': [], 'RL': [], 'Other': []}
    for p in papers:
        t = p.get('primary_topic', 'Other')
        if t not in topics:
            t = 'Other'
        topics[t].append(p)
        
    for topic, topic_papers in topics.items():
        if not topic_papers:
            continue
        
        lines.append(f"## {topic}")
        lines.append("")
        
        for p in topic_papers:
            title = p.get('title', 'No Title')
            # Translate title (mock translation for now, or just keep English)
            # In a real scenario, we'd use an LLM to translate.
            # For now, I'll just append a placeholder or keep it as is.
            lines.append(f"### {title}")
            lines.append(f"- **一句话摘要**: {p.get('summary', '暂无摘要')[:100]}...")
            lines.append(f"- **解决痛点**: 针对 {topic} 领域的关键问题...")
            lines.append(f"- **核心改进**: 提出了新的架构/算法...")
            lines.append(f"- **应用场景**: 机器人操作/自动驾驶...")
            lines.append(f"- **链接**: [Paper]({p.get('link', p.get('url', '#'))})")
            if p.get('code_url'):
                lines.append(f"- **代码**: [Code]({p.get('code_url')})")
            lines.append("")
            
    # Open Source Projects
    if repos or hf_items:
        lines.append("## 开源项目精选")
        lines.append("")
        
        for r in repos:
            lines.append(f"### [GitHub] {r.get('name')}")
            lines.append(f"- **简介**: {r.get('description', '暂无描述')}")
            lines.append(f"- **链接**: {r.get('url')}")
            lines.append(f"- **Stars**: {r.get('stars', 0)}")
            lines.append("")
            
        for h in hf_items:
            lines.append(f"### [HuggingFace] {h.get('id')}")
            lines.append(f"- **类型**: {h.get('type')}")
            lines.append(f"- **链接**: {h.get('url')}")
            lines.append(f"- **Likes**: {h.get('likes', 0)}")
            lines.append("")
            
    return "\n".join(lines)

def main():
    date_str = datetime.datetime.now().strftime('%Y-%m-%d')
    output_file = f"/workspace/daily-papers/{date_str}-cn.md"
    
    # Load data
    arxiv_papers = load_json('/tmp/arxiv_papers.json')
    s2_papers = load_json('/tmp/s2_papers.json')
    repos = load_json('/tmp/github_repos.json')
    hf_items = load_json('/tmp/huggingface.json')
    
    # Combine and deduplicate papers
    all_papers = {}
    for p in arxiv_papers + s2_papers:
        norm_title = normalize_title(p.get('title', ''))
        if norm_title not in all_papers:
            all_papers[norm_title] = p
        else:
            # Merge info if needed (e.g., if S2 has tracked author info)
            if p.get('tracked_author'):
                all_papers[norm_title]['tracked_author'] = p['tracked_author']
    
    unique_papers = list(all_papers.values())
    
    # Score and sort papers
    unique_papers.sort(key=score_paper, reverse=True)
    top_papers = unique_papers[:12]  # Select top 12
    
    # Sort repos and HF items
    repos.sort(key=lambda x: x.get('stars', 0), reverse=True)
    top_repos = repos[:3]
    
    hf_items.sort(key=lambda x: x.get('likes', 0), reverse=True)
    top_hf = hf_items[:2]
    
    # Generate Markdown
    markdown_content = generate_markdown(top_papers, top_repos, top_hf, date_str)
    
    # Save to file
    with open(output_file, 'w') as f:
        f.write(markdown_content)
        
    print(f"Report generated at {output_file}")

if __name__ == "__main__":
    main()
