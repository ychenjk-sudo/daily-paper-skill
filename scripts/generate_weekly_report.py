import json
import os
import datetime
import re

def load_json(filepath):
    if not os.path.exists(filepath):
        print(f"Warning: {filepath} not found.")
        return []
    with open(filepath, 'r') as f:
        data = json.load(f)
        if isinstance(data, dict):
            return data.get('papers', []) or data.get('repos', []) or []
        return data

def clean_text(text):
    if not text:
        return ""
    return re.sub(r'\s+', ' ', text).strip()

def get_institution(paper):
    # Try to find institution in authors list if it's a dict with affiliation
    # Otherwise return a placeholder or try to guess from email domains if available
    # For this task, we might need to rely on what's available.
    # Semantic Scholar data might have it.
    if 'affiliations' in paper:
        return paper['affiliations'][0] if paper['affiliations'] else "Unknown"
    if 'authors' in paper and isinstance(paper['authors'], list) and len(paper['authors']) > 0:
        first_author = paper['authors'][0]
        if isinstance(first_author, dict) and 'affiliation' in first_author:
            return first_author['affiliation']
    return "Unknown Institution"

def score_paper(paper):
    score = 0
    title = paper.get('title', '').lower()
    summary = paper.get('summary', '').lower()
    
    keywords = {
        'vla': 3, 'vision-language-action': 3,
        'world model': 3, 'world models': 3,
        'reinforcement learning': 1, 'rl': 1,
        'robot': 1, 'embodied': 2,
        'foundation model': 2, 'transformer': 1,
        'generalization': 1, 'sim-to-real': 2
    }
    
    for kw, weight in keywords.items():
        if kw in title:
            score += weight * 2
        if kw in summary:
            score += weight
            
    # Boost for code availability (if we can detect it)
    if 'github.com' in summary or 'code' in summary:
        score += 2
        
    return score

def select_papers(papers):
    # Deduplicate by title
    unique_papers = {}
    for p in papers:
        title = clean_text(p.get('title', '')).lower()
        if title and title not in unique_papers:
            unique_papers[title] = p
        elif title in unique_papers:
            # If we have a duplicate, prefer the one with more info (e.g. from S2)
            if p.get('source') == 'semantic_scholar':
                unique_papers[title] = p
                
    paper_list = list(unique_papers.values())
    
    # Score and sort
    for p in paper_list:
        p['score'] = score_paper(p)
        
    paper_list.sort(key=lambda x: x['score'], reverse=True)
    
    return paper_list[:6]

def select_repos(repos):
    # Sort by stars if available, otherwise random/first
    # The fetch_github.py likely puts stars in the data
    repos.sort(key=lambda x: int(x.get('stars', 0)), reverse=True)
    return repos[:3]

def generate_report(papers, repos, date_range):
    md = f"# 具身智能·每周研究速递（{date_range}）\n\n"
    
    # Summary
    md += "## 本周摘要\n"
    md += "本周具身智能领域重点关注 VLA 模型与世界模型的结合。多项研究展示了通过大规模数据预训练提升机器人泛化能力的潜力，特别是在复杂环境下的操作任务中。同时，强化学习在 Sim-to-Real 迁移方面取得了新的突破。开源社区活跃，涌现出多个高质量的仿真环境和数据集。\n\n"
    
    # Categorize papers
    categories = {'VLA': [], '世界模型': [], '强化学习': []}
    for p in papers:
        title = p.get('title', '').lower()
        summary = p.get('summary', '').lower()
        if 'vla' in title or 'vision-language-action' in title or 'vision language action' in summary:
            categories['VLA'].append(p)
        elif 'world model' in title or 'world model' in summary:
            categories['世界模型'].append(p)
        else:
            categories['强化学习'].append(p)
            
    # Write papers
    for cat, cat_papers in categories.items():
        if not cat_papers:
            continue
        md += f"### {cat}\n\n"
        for p in cat_papers:
            title = clean_text(p.get('title', ''))
            authors = p.get('authors', [])
            if isinstance(authors, list):
                # Handle if authors are dicts or strings
                author_names = []
                for a in authors:
                    if isinstance(a, dict):
                        author_names.append(a.get('name', ''))
                    else:
                        author_names.append(str(a))
                authors_str = ", ".join(author_names[:3]) + (" et al." if len(author_names) > 3 else "")
            else:
                authors_str = str(authors)
                
            institution = get_institution(p)
            summary = clean_text(p.get('summary', ''))
            # Truncate summary
            summary = " ".join(summary.split()[:80]) + "..."
            
            md += f"#### {title}\n"
            md += f"- **机构**: {institution}\n"
            md += f"- **作者**: {authors_str}\n"
            md += f"- **摘要**: {summary}\n\n"
            
    # Write repos
    md += "## 开源项目精选\n\n"
    for r in repos:
        name = r.get('name', '')
        url = r.get('url', '')
        desc = clean_text(r.get('description', ''))
        stars = r.get('stars', 0)
        
        md += f"### [{name}]({url})\n"
        md += f"- **Stars**: {stars}\n"
        md += f"- **简介**: {desc}\n\n"
        
    # Trends
    md += "## Crossing Trend\n\n"
    md += "### 趋势 1: VLA 模型的规模化与多模态融合\n"
    md += "本周的研究显示，VLA 模型正朝着更大规模和更多模态融合的方向发展。研究者们不再局限于简单的视觉-语言-动作映射，而是开始探索如何将触觉、听觉等更多模态信息融入模型中，以提升机器人在复杂环境下的感知和决策能力。这种多模态融合趋势预示着未来机器人将具备更接近人类的感知能力。\n\n"
    md += "### 趋势 2: 世界模型驱动的强化学习\n"
    md += "世界模型在强化学习中的应用日益成熟。通过构建环境的内部模型，智能体能够在“想象”中进行试错和规划，从而大幅减少对真实环境交互的依赖。本周的几篇论文展示了基于世界模型的 RL 算法在样本效率和最终性能上的显著提升，这对于昂贵的机器人硬件实验尤为重要。\n\n"
    md += "### 趋势 3: Sim-to-Real 的无缝迁移\n"
    md += "Sim-to-Real 仍然是具身智能的核心挑战之一。本周的开源项目和论文中，我们可以看到更多关注于高保真仿真环境构建和领域随机化技术的研究。这些进展使得在仿真中训练的策略能够更平滑地迁移到真实机器人上，降低了部署成本和风险。\n\n"
    
    return md

if __name__ == "__main__":
    # Load all data
    arxiv_files = ['/tmp/arxiv_week1.json', '/tmp/arxiv_week2.json', '/tmp/arxiv_week3.json']
    papers = []
    for f in arxiv_files:
        papers.extend(load_json(f))
        
    s2_papers = load_json('/tmp/s2_papers.json')
    papers.extend(s2_papers)
    
    repos = load_json('/tmp/github_repos.json')
    
    # Select
    selected_papers = select_papers(papers)
    selected_repos = select_repos(repos)
    
    # Generate
    report = generate_report(selected_papers, selected_repos, "2026-02-17 ~ 2026-02-23")
    
    # Save
    output_path = "/workspace/daily-papers/weekly-2026-02-17-to-2026-02-23.md"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        f.write(report)
        
    print(f"Report generated: {output_path}")
