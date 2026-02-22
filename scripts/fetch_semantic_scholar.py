#!/usr/bin/env python3
"""
Daily Paper - Semantic Scholar 获取脚本
追踪特定作者的最新论文
"""

import argparse
import json
import urllib.request
import urllib.parse
from datetime import datetime, timedelta
import time

# Semantic Scholar API (免费，有速率限制)
S2_API = "https://api.semanticscholar.org/graph/v1"

# 重点作者 Semantic Scholar IDs
# 可通过搜索 https://www.semanticscholar.org/search 获取
PRIORITY_AUTHORS = {
    "Yann LeCun": "1688882",
    "Pieter Abbeel": "1736370",
    "Sergey Levine": "2691021",
    "Chelsea Finn": "2065960",
    "Danijar Hafner": "2059290",
    "Kaiming He": "2164085",
    "Ilya Sutskever": "1695689",
    # NVIDIA Robotics / DreamZero / DreamDojo
    "Jim Fan (Linxi Fan)": "3275727",
}


def fetch_author_papers(author_id: str, author_name: str, days: int = 7) -> list:
    """获取作者最近的论文"""
    papers = []
    
    url = f"{S2_API}/author/{author_id}/papers"
    params = {
        "fields": "title,abstract,authors,year,publicationDate,url,openAccessPdf,citationCount",
        "limit": 20,
    }
    full_url = f"{url}?{urllib.parse.urlencode(params)}"
    
    try:
        req = urllib.request.Request(full_url)
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode('utf-8'))
    except Exception as e:
        print(f"Error fetching author {author_name}: {e}")
        return []
    
    cutoff_date = datetime.now() - timedelta(days=days)
    
    for item in data.get("data", []):
        try:
            pub_date = item.get("publicationDate")
            if pub_date:
                pub_dt = datetime.strptime(pub_date, "%Y-%m-%d")
                if pub_dt < cutoff_date:
                    continue
            
            paper = {
                "source": "semantic_scholar",
                "title": item.get("title"),
                "abstract": item.get("abstract", ""),
                "authors": [a.get("name") for a in item.get("authors", [])],
                "published": pub_date,
                "url": item.get("url"),
                "pdf_url": item.get("openAccessPdf", {}).get("url") if item.get("openAccessPdf") else None,
                "citations": item.get("citationCount", 0),
                "tracked_author": author_name,
            }
            papers.append(paper)
        except Exception as e:
            continue
    
    return papers


def search_papers(query: str, days: int = 1, limit: int = 50) -> list:
    """搜索论文"""
    papers = []
    
    url = f"{S2_API}/paper/search"
    params = {
        "query": query,
        "fields": "title,abstract,authors,year,publicationDate,url,openAccessPdf,citationCount",
        "limit": limit,
    }
    full_url = f"{url}?{urllib.parse.urlencode(params)}"
    
    try:
        req = urllib.request.Request(full_url)
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode('utf-8'))
    except Exception as e:
        print(f"Error searching: {e}")
        return []
    
    cutoff_date = datetime.now() - timedelta(days=days + 1)
    
    for item in data.get("data", []):
        try:
            pub_date = item.get("publicationDate")
            if pub_date:
                pub_dt = datetime.strptime(pub_date, "%Y-%m-%d")
                if pub_dt < cutoff_date:
                    continue
            
            paper = {
                "source": "semantic_scholar",
                "title": item.get("title"),
                "abstract": item.get("abstract", ""),
                "authors": [a.get("name") for a in item.get("authors", [])],
                "published": pub_date,
                "url": item.get("url"),
                "pdf_url": item.get("openAccessPdf", {}).get("url") if item.get("openAccessPdf") else None,
                "citations": item.get("citationCount", 0),
            }
            papers.append(paper)
        except:
            continue
    
    return papers


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--days", type=int, default=7)
    parser.add_argument("--output", type=str, default="/tmp/s2_papers.json")
    parser.add_argument("--authors-only", action="store_true", help="只获取重点作者")
    args = parser.parse_args()
    
    all_papers = []
    
    # 获取重点作者的论文
    print("Fetching papers from priority authors...")
    for name, author_id in PRIORITY_AUTHORS.items():
        papers = fetch_author_papers(author_id, name, args.days)
        all_papers.extend(papers)
        print(f"  {name}: {len(papers)} papers")
        time.sleep(1)  # 速率限制
    
    if not args.authors_only:
        # 搜索相关主题
        queries = [
            "vision language action robot",
            "world model reinforcement learning",
            "robot imitation learning",
        ]
        for query in queries:
            papers = search_papers(query, args.days)
            all_papers.extend(papers)
            print(f"  Query '{query}': {len(papers)} papers")
            time.sleep(1)
    
    # 去重
    seen = set()
    unique_papers = []
    for p in all_papers:
        key = p.get("title", "").lower()
        if key not in seen:
            seen.add(key)
            unique_papers.append(p)
    
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump({"source": "semantic_scholar", "papers": unique_papers}, f, ensure_ascii=False, indent=2)
    
    print(f"Saved {len(unique_papers)} unique papers to {args.output}")


if __name__ == "__main__":
    main()
