#!/usr/bin/env python3
"""
Daily Paper - Papers With Code 获取脚本
获取最新论文（带代码）
"""

import argparse
import json
import urllib.request
from datetime import datetime, timedelta

# Papers With Code API
PWC_API = "https://paperswithcode.com/api/v1"

def fetch_latest_papers(days: int = 1, limit: int = 50) -> list:
    """获取最近几天的论文"""
    papers = []
    
    # 获取最新论文
    url = f"{PWC_API}/papers/?ordering=-published&items_per_page={limit}"
    
    try:
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode('utf-8'))
    except Exception as e:
        print(f"Error fetching Papers With Code: {e}")
        return []
    
    cutoff_date = datetime.now() - timedelta(days=days + 1)
    
    for item in data.get("results", []):
        try:
            pub_date = item.get("published")
            if pub_date:
                pub_dt = datetime.strptime(pub_date, "%Y-%m-%d")
                if pub_dt < cutoff_date:
                    continue
            
            paper = {
                "source": "papers_with_code",
                "id": item.get("id"),
                "title": item.get("title"),
                "abstract": item.get("abstract", ""),
                "authors": item.get("authors", []),
                "published": pub_date,
                "url": item.get("url_abs"),
                "pdf_url": item.get("url_pdf"),
                "code_url": None,
                "stars": 0,
            }
            
            # 获取代码仓库
            paper_id = item.get("id")
            if paper_id:
                repo_url = f"{PWC_API}/papers/{paper_id}/repositories/"
                try:
                    req = urllib.request.Request(repo_url, headers={"Accept": "application/json"})
                    with urllib.request.urlopen(req, timeout=10) as resp:
                        repos = json.loads(resp.read().decode('utf-8'))
                        if repos.get("results"):
                            best_repo = max(repos["results"], key=lambda x: x.get("stars", 0))
                            paper["code_url"] = best_repo.get("url")
                            paper["stars"] = best_repo.get("stars", 0)
                except:
                    pass
            
            papers.append(paper)
        except Exception as e:
            continue
    
    print(f"Fetched {len(papers)} papers from Papers With Code")
    return papers


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--days", type=int, default=1)
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--output", type=str, default="/tmp/pwc_papers.json")
    args = parser.parse_args()
    
    papers = fetch_latest_papers(args.days, args.limit)
    
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump({"source": "papers_with_code", "papers": papers}, f, ensure_ascii=False, indent=2)
    
    print(f"Saved to {args.output}")


if __name__ == "__main__":
    main()
