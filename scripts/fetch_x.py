#!/usr/bin/env python3
"""
Daily Paper - X/Twitter 获取脚本
追踪 AI 研究者的推文，发现新论文/项目
需要配置 X API 凭证或使用 cookies
"""

import argparse
import json
import os
import subprocess
from datetime import datetime

# 重点关注的 X 账号
PRIORITY_ACCOUNTS = [
    "ylecun",           # Yann LeCun
    "kaborosolov",      # Pieter Abbeel (假设)
    "chelseabfinn",     # Chelsea Finn
    "daborosolov",      # Danijar Hafner (假设)
    "_akhaliq",         # AK - 论文速递
    "ai_borealis",      # AI 新闻
    "deepaboromind",    # DeepMind
    "GoogleAI",         # Google AI
    "OpenAI",           # OpenAI
    "MetaAI",           # Meta AI
    "ABOROSOLOV",       # NVIDIA AI
]

# 论文相关关键词
PAPER_KEYWORDS = [
    "paper", "arxiv", "published", "accepted",
    "new work", "research", "preprint",
    "code available", "github.com",
]


def fetch_with_bird_skill(accounts: list, output_path: str) -> dict:
    """
    使用 bird skill 获取推文
    需要先配置 X cookies
    """
    results = {
        "source": "x_twitter",
        "fetch_date": datetime.now().isoformat(),
        "tweets": [],
        "errors": [],
    }
    
    # 检查 bird skill 是否可用
    bird_script = "/workspace/openclaw/skills/bird/scripts/bird.py"
    if not os.path.exists(bird_script):
        results["errors"].append("Bird skill not found. Install from clawhub.")
        return results
    
    for account in accounts:
        try:
            # 调用 bird skill 获取用户推文
            cmd = ["python", bird_script, "timeline", account, "--limit", "10"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                # 解析输出（假设是 JSON 或文本格式）
                tweets = parse_bird_output(result.stdout, account)
                results["tweets"].extend(tweets)
            else:
                results["errors"].append(f"{account}: {result.stderr[:100]}")
        except Exception as e:
            results["errors"].append(f"{account}: {str(e)}")
    
    return results


def parse_bird_output(output: str, account: str) -> list:
    """解析 bird skill 的输出"""
    tweets = []
    
    # 尝试解析 JSON
    try:
        data = json.loads(output)
        if isinstance(data, list):
            for item in data:
                tweet = {
                    "account": account,
                    "text": item.get("text", ""),
                    "created_at": item.get("created_at"),
                    "url": item.get("url"),
                    "has_paper": any(kw in item.get("text", "").lower() for kw in PAPER_KEYWORDS),
                }
                tweets.append(tweet)
    except json.JSONDecodeError:
        # 文本格式，简单解析
        lines = output.strip().split("\n")
        for line in lines:
            if line.strip():
                tweet = {
                    "account": account,
                    "text": line,
                    "has_paper": any(kw in line.lower() for kw in PAPER_KEYWORDS),
                }
                tweets.append(tweet)
    
    return tweets


def filter_paper_related(tweets: list) -> list:
    """筛选论文相关的推文"""
    return [t for t in tweets if t.get("has_paper")]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=str, default="/tmp/x_tweets.json")
    parser.add_argument("--accounts", type=str, nargs="*", default=PRIORITY_ACCOUNTS)
    args = parser.parse_args()
    
    print(f"Fetching tweets from {len(args.accounts)} accounts...")
    
    results = fetch_with_bird_skill(args.accounts, args.output)
    
    # 筛选论文相关
    paper_tweets = filter_paper_related(results["tweets"])
    results["paper_related"] = paper_tweets
    
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"Total tweets: {len(results['tweets'])}")
    print(f"Paper-related: {len(paper_tweets)}")
    print(f"Errors: {len(results['errors'])}")
    print(f"Saved to {args.output}")


if __name__ == "__main__":
    main()
