#!/usr/bin/env python3
"""
Daily Paper - X/Twitter 获取脚本
追踪 AI 研究者的推文，发现新论文/项目
使用 bird CLI + cookies 认证
"""

import argparse
import json
import os
import subprocess
from datetime import datetime

# X credentials 配置路径
X_CREDENTIALS_PATH = "/workspace/ai-masters-quotes/config/x_credentials.json"

# 重点关注的 X 账号
PRIORITY_ACCOUNTS = [
    "ylecun",           # Yann LeCun
    "PieterAbbeel",     # Pieter Abbeel
    "chelseabfinn",     # Chelsea Finn
    "daborosolov",      # Danijar Hafner
    "_akhaliq",         # AK - 论文速递
    "GoogleDeepMind",   # DeepMind
    "GoogleAI",         # Google AI
    "OpenAI",           # OpenAI
    "AIatMeta",         # Meta AI
    "ABOROSOLOV",       # NVIDIA AI
    "DrJimFan",         # Jim Fan (NVIDIA)
    "AndrewYNg",        # Andrew Ng
    "kaborosolov",      # Andrej Karpathy
]

# 论文相关关键词
PAPER_KEYWORDS = [
    "paper", "arxiv", "published", "accepted",
    "new work", "research", "preprint",
    "code available", "github.com",
]


def load_credentials() -> tuple:
    """从配置文件加载 X credentials"""
    try:
        with open(X_CREDENTIALS_PATH, "r") as f:
            creds = json.load(f)
            return creds.get("auth_token"), creds.get("ct0")
    except:
        return None, None


def fetch_with_bird_cli(accounts: list, output_path: str) -> dict:
    """
    使用 bird CLI 获取推文
    """
    results = {
        "source": "x_twitter",
        "fetch_date": datetime.now().isoformat(),
        "tweets": [],
        "errors": [],
    }
    
    # 加载 credentials
    auth_token, ct0 = load_credentials()
    if not auth_token or not ct0:
        results["errors"].append("X credentials not found. Check " + X_CREDENTIALS_PATH)
        return results
    
    env = os.environ.copy()
    env["AUTH_TOKEN"] = auth_token
    env["CT0"] = ct0
    
    for account in accounts:
        try:
            # 使用 bird CLI 获取用户推文
            cmd = ["bird", "user-tweets", f"@{account}", "-n", "10", "--json"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30, env=env)
            
            if result.returncode == 0:
                tweets = parse_bird_output(result.stdout, account)
                results["tweets"].extend(tweets)
                print(f"  @{account}: {len(tweets)} tweets")
            else:
                error_msg = result.stderr[:100] if result.stderr else "Unknown error"
                results["errors"].append(f"@{account}: {error_msg}")
        except subprocess.TimeoutExpired:
            results["errors"].append(f"@{account}: timeout")
        except Exception as e:
            results["errors"].append(f"@{account}: {str(e)}")
    
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
    
    results = fetch_with_bird_cli(args.accounts, args.output)
    
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
