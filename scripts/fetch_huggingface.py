#!/usr/bin/env python3
"""
Daily Paper - Hugging Face 获取脚本
获取最新模型、数据集和 Spaces
"""

import argparse
import json
import urllib.request
import urllib.parse
from datetime import datetime, timedelta

# Hugging Face API
HF_API = "https://huggingface.co/api"

# 相关标签
MODEL_TAGS = [
    "robotics",
    "reinforcement-learning", 
    "world-model",
    "vision-language",
    "multimodal",
    "text-to-action",
]

# 重点组织/作者
PRIORITY_ORGS = [
    "google",
    "meta-llama",
    "openai",
    "microsoft",
    "nvidia",
    "deepmind",
    "berkeley-nest",
    "openvla",
]


def fetch_models(tags: list = None, limit: int = 50, days: int = 7) -> list:
    """获取最新模型"""
    models = []
    
    # 基础 URL
    url = f"{HF_API}/models"
    params = {
        "sort": "lastModified",
        "direction": "-1",
        "limit": limit,
    }
    
    if tags:
        params["filter"] = ",".join(tags)
    
    full_url = f"{url}?{urllib.parse.urlencode(params)}"
    
    try:
        req = urllib.request.Request(full_url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode('utf-8'))
    except Exception as e:
        print(f"Error fetching HF models: {e}")
        return []
    
    cutoff_date = datetime.now() - timedelta(days=days)
    
    for item in data:
        try:
            # 检查更新时间
            last_modified = item.get("lastModified")
            if last_modified:
                mod_dt = datetime.fromisoformat(last_modified.replace("Z", "+00:00"))
                if mod_dt.replace(tzinfo=None) < cutoff_date:
                    continue
            
            model = {
                "source": "huggingface",
                "type": "model",
                "id": item.get("id"),
                "name": item.get("modelId") or item.get("id"),
                "author": item.get("author"),
                "description": item.get("description", ""),
                "tags": item.get("tags", []),
                "downloads": item.get("downloads", 0),
                "likes": item.get("likes", 0),
                "last_modified": last_modified,
                "url": f"https://huggingface.co/{item.get('id')}",
                "is_priority": any(org in str(item.get("author", "")).lower() for org in PRIORITY_ORGS),
            }
            models.append(model)
        except Exception as e:
            continue
    
    return models


def fetch_datasets(tags: list = None, limit: int = 30, days: int = 7) -> list:
    """获取最新数据集"""
    datasets = []
    
    url = f"{HF_API}/datasets"
    params = {
        "sort": "lastModified",
        "direction": "-1",
        "limit": limit,
    }
    
    if tags:
        params["filter"] = ",".join(tags)
    
    full_url = f"{url}?{urllib.parse.urlencode(params)}"
    
    try:
        req = urllib.request.Request(full_url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode('utf-8'))
    except Exception as e:
        print(f"Error fetching HF datasets: {e}")
        return []
    
    cutoff_date = datetime.now() - timedelta(days=days)
    
    for item in data:
        try:
            last_modified = item.get("lastModified")
            if last_modified:
                mod_dt = datetime.fromisoformat(last_modified.replace("Z", "+00:00"))
                if mod_dt.replace(tzinfo=None) < cutoff_date:
                    continue
            
            dataset = {
                "source": "huggingface",
                "type": "dataset",
                "id": item.get("id"),
                "name": item.get("id"),
                "author": item.get("author"),
                "description": item.get("description", ""),
                "tags": item.get("tags", []),
                "downloads": item.get("downloads", 0),
                "likes": item.get("likes", 0),
                "last_modified": last_modified,
                "url": f"https://huggingface.co/datasets/{item.get('id')}",
                "is_priority": any(org in str(item.get("author", "")).lower() for org in PRIORITY_ORGS),
            }
            datasets.append(dataset)
        except:
            continue
    
    return datasets


def fetch_spaces(limit: int = 30, days: int = 7) -> list:
    """获取热门 Spaces"""
    spaces = []
    
    url = f"{HF_API}/spaces"
    params = {
        "sort": "likes",
        "direction": "-1",
        "limit": limit,
    }
    
    full_url = f"{url}?{urllib.parse.urlencode(params)}"
    
    try:
        req = urllib.request.Request(full_url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode('utf-8'))
    except Exception as e:
        print(f"Error fetching HF spaces: {e}")
        return []
    
    cutoff_date = datetime.now() - timedelta(days=days)
    
    for item in data:
        try:
            last_modified = item.get("lastModified")
            if last_modified:
                mod_dt = datetime.fromisoformat(last_modified.replace("Z", "+00:00"))
                if mod_dt.replace(tzinfo=None) < cutoff_date:
                    continue
            
            space = {
                "source": "huggingface",
                "type": "space",
                "id": item.get("id"),
                "name": item.get("id"),
                "author": item.get("author"),
                "sdk": item.get("sdk"),
                "likes": item.get("likes", 0),
                "last_modified": last_modified,
                "url": f"https://huggingface.co/spaces/{item.get('id')}",
                "is_priority": any(org in str(item.get("author", "")).lower() for org in PRIORITY_ORGS),
            }
            spaces.append(space)
        except:
            continue
    
    return spaces


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--days", type=int, default=7)
    parser.add_argument("--output", type=str, default="/tmp/huggingface.json")
    args = parser.parse_args()
    
    all_items = []
    
    # 获取相关标签的模型
    print("Fetching models...")
    for tag in MODEL_TAGS:
        models = fetch_models(tags=[tag], limit=20, days=args.days)
        all_items.extend(models)
        print(f"  Tag '{tag}': {len(models)} models")
    
    # 获取数据集
    print("Fetching datasets...")
    datasets = fetch_datasets(tags=["robotics", "reinforcement-learning"], limit=30, days=args.days)
    all_items.extend(datasets)
    print(f"  Datasets: {len(datasets)}")
    
    # 获取 Spaces
    print("Fetching spaces...")
    spaces = fetch_spaces(limit=30, days=args.days)
    all_items.extend(spaces)
    print(f"  Spaces: {len(spaces)}")
    
    # 去重
    seen = set()
    unique_items = []
    for item in all_items:
        if item["id"] not in seen:
            seen.add(item["id"])
            unique_items.append(item)
    
    # 按 likes/downloads 排序
    unique_items.sort(key=lambda x: x.get("likes", 0) + x.get("downloads", 0), reverse=True)
    
    result = {
        "source": "huggingface",
        "fetch_date": datetime.now().isoformat(),
        "items": unique_items[:100],
        "stats": {
            "models": len([i for i in unique_items if i["type"] == "model"]),
            "datasets": len([i for i in unique_items if i["type"] == "dataset"]),
            "spaces": len([i for i in unique_items if i["type"] == "space"]),
        }
    }
    
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"\nSaved {len(unique_items[:100])} items to {args.output}")
    print(f"Stats: {result['stats']}")


if __name__ == "__main__":
    main()
