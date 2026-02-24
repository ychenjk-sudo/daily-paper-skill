#!/usr/bin/env python3
"""
Daily Paper - arXiv 论文获取脚本
用法: python daily_paper_fetch.py [--date YYYY-MM-DD] [--output /path/to/output.json]
"""

import argparse
import json
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import re

# 重点关注机构
PRIORITY_AFFILIATIONS = [
    "DeepMind", "Google DeepMind",
    "Berkeley", "BAIR", "UC Berkeley",
    "NVIDIA",
    "1X", "1X Technologies",
    "Figure", "Figure AI",
    "Stanford",
    "MIT", "Massachusetts Institute of Technology",
    "OpenAI",
    "Anthropic",
    "Tesla", "Tesla AI", "Optimus",
    "Physical Intelligence",
    "Covariant",
    "Meta", "FAIR", "Facebook AI",
    "Yann LeCun", "LeCun",
]

# 重点论文系列关键词
PRIORITY_SERIES = [
    "Dreamer", "DreamerV2", "DreamerV3", "DreamDojo", "DreamZero",
    "RT-1", "RT-2", "RT-X", "Robotics Transformer",
    "OpenVLA", "Octo",
    "ALOHA",
    "JEPA", "I-JEPA", "V-JEPA",
]

# 筛选主题关键词
TOPIC_KEYWORDS = {
    "VLA": [
        "vision-language-action", "VLA", "vision language action",
        "multimodal robot", "language-conditioned", "instruction following robot",
        "vision-language model robot", "VLM robot",
    ],
    "World Model": [
        "world model", "world modeling", "predictive model", 
        "dynamics model", "latent dynamics", "imagination",
        "model-based planning", "dreamer", "world simulator",
    ],
    "RL": [
        "reinforcement learning", "offline RL", "model-based RL",
        "reward learning", "imitation learning", "policy learning",
        "actor-critic", "PPO", "SAC", "TD3", "RLHF",
        "inverse reinforcement", "demonstration learning",
    ],
}

def fetch_arxiv_papers(date_str: str, categories: list = None) -> list:
    """
    从 arXiv API 获取指定日期的论文
    """
    if categories is None:
        categories = ["cs.RO", "cs.LG", "cs.CV", "cs.AI"]
    
    # 构建查询
    cat_query = " OR ".join([f"cat:{cat}" for cat in categories])
    
    # arXiv API URL
    base_url = "http://export.arxiv.org/api/query"
    
    # 查询参数 - 获取最近的论文
    params = {
        "search_query": cat_query,
        "sortBy": "submittedDate",
        "sortOrder": "descending",
        "max_results": 300,
    }
    
    url = f"{base_url}?{urllib.parse.urlencode(params)}"
    
    print(f"Fetching from arXiv: {url[:100]}...")
    
    try:
        with urllib.request.urlopen(url, timeout=60) as response:
            xml_data = response.read().decode('utf-8')
    except Exception as e:
        print(f"Error fetching arXiv: {e}")
        return []
    
    # 解析 XML
    root = ET.fromstring(xml_data)
    ns = {"atom": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}
    
    papers = []
    target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    
    for entry in root.findall("atom:entry", ns):
        try:
            # 获取发布日期
            published = entry.find("atom:published", ns).text
            pub_date = datetime.fromisoformat(published.replace("Z", "+00:00")).date()
            
            # 只保留目标日期前后 3 天的论文（考虑时区差异）
            date_diff = abs((pub_date - target_date).days)
            if date_diff > 3:
                continue
            
            # 提取信息
            paper = {
                "id": entry.find("atom:id", ns).text.split("/abs/")[-1],
                "title": entry.find("atom:title", ns).text.strip().replace("\n", " "),
                "summary": entry.find("atom:summary", ns).text.strip().replace("\n", " "),
                "authors": [author.find("atom:name", ns).text for author in entry.findall("atom:author", ns)],
                "published": published,
                "link": entry.find("atom:id", ns).text,
                "pdf_link": None,
                "categories": [],
            }
            
            # PDF 链接
            for link in entry.findall("atom:link", ns):
                if link.get("title") == "pdf":
                    paper["pdf_link"] = link.get("href")
                    break
            
            # 分类
            for cat in entry.findall("arxiv:primary_category", ns):
                paper["categories"].append(cat.get("term"))
            for cat in entry.findall("atom:category", ns):
                term = cat.get("term")
                if term and term not in paper["categories"]:
                    paper["categories"].append(term)
            
            papers.append(paper)
            
        except Exception as e:
            continue
    
    print(f"Fetched {len(papers)} papers from arXiv")
    return papers


def check_topic_relevance(paper: dict) -> dict:
    """
    检查论文与主题的相关性
    """
    text = (paper["title"] + " " + paper["summary"]).lower()
    
    relevance = {"VLA": 0, "World Model": 0, "RL": 0}
    
    for topic, keywords in TOPIC_KEYWORDS.items():
        for kw in keywords:
            if kw.lower() in text:
                relevance[topic] += 1
    
    paper["topic_relevance"] = relevance
    paper["primary_topic"] = max(relevance, key=relevance.get) if max(relevance.values()) > 0 else None
    paper["is_relevant"] = max(relevance.values()) > 0
    
    return paper


def check_priority(paper: dict) -> dict:
    """
    检查是否来自重点机构或属于重点系列
    """
    text = paper["title"] + " " + paper["summary"] + " " + " ".join(paper["authors"])
    
    # 检查重点机构（使用单词边界匹配，避免 "submit" 匹配到 "MIT"）
    paper["priority_affiliation"] = None
    for aff in PRIORITY_AFFILIATIONS:
        # 对于短缩写（如 MIT, FAIR），使用单词边界匹配
        if len(aff) <= 4:
            pattern = r'\b' + re.escape(aff) + r'\b'
            if re.search(pattern, text, re.IGNORECASE):
                paper["priority_affiliation"] = aff
                break
        else:
            if aff.lower() in text.lower():
                paper["priority_affiliation"] = aff
                break
    
    # 检查重点系列
    paper["priority_series"] = None
    for series in PRIORITY_SERIES:
        if series.lower() in text.lower():
            paper["priority_series"] = series
            break
    
    paper["is_priority"] = paper["priority_affiliation"] is not None or paper["priority_series"] is not None
    
    return paper


def filter_and_rank_papers(papers: list) -> list:
    """
    筛选和排序论文
    """
    # 添加相关性和优先级信息
    for paper in papers:
        check_topic_relevance(paper)
        check_priority(paper)
    
    # 只保留相关论文
    relevant_papers = [p for p in papers if p["is_relevant"]]
    
    print(f"Relevant papers: {len(relevant_papers)}")
    
    # 排序：优先级 > 相关性分数
    def sort_key(p):
        priority_score = 10 if p["is_priority"] else 0
        relevance_score = sum(p["topic_relevance"].values())
        return (priority_score, relevance_score)
    
    relevant_papers.sort(key=sort_key, reverse=True)
    
    return relevant_papers


def main():
    parser = argparse.ArgumentParser(description="Fetch arXiv papers for Daily Paper")
    parser.add_argument("--date", type=str, default=None, help="Target date (YYYY-MM-DD)")
    parser.add_argument("--output", type=str, default="/tmp/arxiv_papers.json", help="Output JSON file")
    args = parser.parse_args()
    
    # 默认获取昨天的论文
    if args.date is None:
        target_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    else:
        target_date = args.date
    
    print(f"Fetching papers for date: {target_date}")
    
    # 获取论文
    papers = fetch_arxiv_papers(target_date)
    
    # 筛选和排序
    filtered_papers = filter_and_rank_papers(papers)
    
    # 输出结果
    result = {
        "date": target_date,
        "fetch_time": datetime.now().isoformat(),
        "total_fetched": len(papers),
        "total_relevant": len(filtered_papers),
        "papers": filtered_papers[:80],  # 最多 80 篇候选
    }
    
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"Saved {len(filtered_papers[:80])} papers to {args.output}")
    
    # 打印统计
    by_topic = {"VLA": 0, "World Model": 0, "RL": 0}
    priority_count = 0
    for p in filtered_papers[:80]:
        if p["primary_topic"]:
            by_topic[p["primary_topic"]] += 1
        if p["is_priority"]:
            priority_count += 1
    
    print(f"\nStatistics:")
    print(f"  By topic: {by_topic}")
    print(f"  Priority papers: {priority_count}")


if __name__ == "__main__":
    main()
