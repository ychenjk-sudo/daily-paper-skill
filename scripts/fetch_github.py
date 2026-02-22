#!/usr/bin/env python3
"""
Daily Paper - GitHub Trending 获取脚本
获取 AI/ML/Robotics 相关的热门新项目
"""

import argparse
import json
import urllib.request
from datetime import datetime, timedelta
import re

# GitHub API
GITHUB_API = "https://api.github.com"

# 相关 topic 标签
TOPICS = [
    "reinforcement-learning",
    "robot-learning",
    "robotics",
    "world-model",
    "vision-language",
    "imitation-learning",
]

# 相关关键词
KEYWORDS = [
    "VLA", "vision-language-action",
    "world model", "dreamer",
    "robot", "manipulation",
    "reinforcement learning", "RL",
]


def search_repos(query: str, days: int = 7, limit: int = 30) -> list:
    """搜索最近创建/更新的仓库"""
    repos = []
    
    cutoff_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    
    # 搜索最近推送的仓库
    search_query = f"{query} pushed:>={cutoff_date}"
    url = f"{GITHUB_API}/search/repositories"
    params = f"?q={urllib.parse.quote(search_query)}&sort=stars&order=desc&per_page={limit}"
    
    try:
        req = urllib.request.Request(
            url + params,
            headers={
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": "DailyPaper/1.0"
            }
        )
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode('utf-8'))
    except Exception as e:
        print(f"Error searching GitHub: {e}")
        return []
    
    for item in data.get("items", []):
        try:
            repo = {
                "source": "github",
                "name": item.get("full_name"),
                "description": item.get("description", ""),
                "url": item.get("html_url"),
                "stars": item.get("stargazers_count", 0),
                "forks": item.get("forks_count", 0),
                "language": item.get("language"),
                "topics": item.get("topics", []),
                "created_at": item.get("created_at"),
                "updated_at": item.get("updated_at"),
                "is_new": False,
            }
            
            # 检查是否是最近创建的新项目
            created = item.get("created_at")
            if created:
                created_dt = datetime.strptime(created[:10], "%Y-%m-%d")
                if (datetime.now() - created_dt).days <= days:
                    repo["is_new"] = True
            
            repos.append(repo)
        except:
            continue
    
    return repos


def fetch_trending_topics() -> list:
    """获取相关 topic 下的热门仓库"""
    all_repos = []
    
    for topic in TOPICS:
        repos = search_repos(f"topic:{topic}", days=7, limit=20)
        for r in repos:
            r["matched_topic"] = topic
        all_repos.extend(repos)
        print(f"  Topic '{topic}': {len(repos)} repos")
    
    return all_repos


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--days", type=int, default=7)
    parser.add_argument("--output", type=str, default="/tmp/github_repos.json")
    args = parser.parse_args()
    
    all_repos = []
    
    # 按 topic 搜索
    print("Fetching from topics...")
    all_repos.extend(fetch_trending_topics())
    
    # 按关键词搜索
    print("Fetching from keywords...")
    for kw in KEYWORDS[:5]:  # 限制请求数
        repos = search_repos(kw, args.days, limit=20)
        all_repos.extend(repos)
        print(f"  Keyword '{kw}': {len(repos)} repos")
    
    # 去重并按 stars 排序
    seen = set()
    unique_repos = []
    for r in all_repos:
        if r["name"] not in seen:
            seen.add(r["name"])
            unique_repos.append(r)
    
    unique_repos.sort(key=lambda x: x["stars"], reverse=True)
    
    # 筛选：只保留有意义的项目（有描述、有一定 stars）
    filtered = [r for r in unique_repos if r.get("description") and r.get("stars", 0) >= 10]
    
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump({
            "source": "github",
            "fetch_date": datetime.now().isoformat(),
            "repos": filtered[:50]
        }, f, ensure_ascii=False, indent=2)
    
    print(f"Saved {len(filtered[:50])} repos to {args.output}")


if __name__ == "__main__":
    main()
