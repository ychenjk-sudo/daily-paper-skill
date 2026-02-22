#!/usr/bin/env python3
"""
Daily Paper - 飞书文档写入脚本
用法: python daily_paper_feishu.py --input /path/to/report.md --doc-id <feishu_doc_id>
"""

import argparse
import requests
import json
import re
from typing import List, Dict

# 飞书应用凭证
FEISHU_APP_ID = "cli_a99c1819e3f4900b"
FEISHU_APP_SECRET = "qvYVoPKbRyicpoPXYcBG9bn6AIoKmezw"


def get_tenant_token() -> str:
    """获取飞书 tenant_access_token"""
    resp = requests.post(
        "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
        json={"app_id": FEISHU_APP_ID, "app_secret": FEISHU_APP_SECRET}
    )
    data = resp.json()
    if data.get("code") != 0:
        raise Exception(f"Failed to get token: {data}")
    return data["tenant_access_token"]


def parse_text_with_styles(text: str) -> List[Dict]:
    """解析文本中的 markdown 格式，返回飞书 elements 数组"""
    elements = []
    pos = 0
    
    # 匹配加粗 **text**
    for match in re.finditer(r'\*\*([^*]+)\*\*', text):
        # 添加匹配前的普通文本
        if match.start() > pos:
            plain = text[pos:match.start()]
            if plain:
                elements.append({"text_run": {"content": plain}})
        
        # 添加加粗文本
        bold_text = match.group(1)
        elements.append({
            "text_run": {
                "content": bold_text,
                "text_element_style": {"bold": True}
            }
        })
        pos = match.end()
    
    # 添加剩余的普通文本
    if pos < len(text):
        remaining = text[pos:]
        if remaining:
            elements.append({"text_run": {"content": remaining}})
    
    # 如果没有任何格式，返回原文本
    if not elements:
        elements = [{"text_run": {"content": text}}]
    
    return elements


def make_text_block(text: str) -> Dict:
    """创建文本块"""
    elements = parse_text_with_styles(text)
    return {
        "block_type": 2,
        "text": {"elements": elements}
    }


def make_bullet_block(text: str) -> Dict:
    """创建无序列表块"""
    clean_text = text.lstrip('- ').strip()
    elements = parse_text_with_styles(clean_text)
    return {
        "block_type": 12,
        "bullet": {"elements": elements}
    }


def make_numbered_block(text: str) -> Dict:
    """创建有序列表块"""
    clean_text = re.sub(r'^\d+\.\s*', '', text).strip()
    elements = parse_text_with_styles(clean_text)
    return {
        "block_type": 13,
        "ordered": {"elements": elements}
    }


def make_heading_block(level: int, text: str) -> Dict:
    """创建标题块"""
    block_types = {1: 3, 2: 4, 3: 5, 4: 6}
    heading_keys = {1: "heading1", 2: "heading2", 3: "heading3", 4: "heading4"}
    elements = parse_text_with_styles(text)
    return {
        "block_type": block_types[level],
        heading_keys[level]: {"elements": elements}
    }


def make_divider() -> Dict:
    """创建分隔线"""
    return {"block_type": 22, "divider": {}}


def parse_markdown_to_blocks(content: str) -> List[Dict]:
    """将 Markdown 转换为飞书文档块"""
    children = []
    lines = content.split('\n')
    
    for line in lines:
        if line.startswith('# '):
            children.append(make_heading_block(1, line[2:]))
        elif line.startswith('## '):
            children.append(make_heading_block(2, line[3:]))
        elif line.startswith('### '):
            children.append(make_heading_block(3, line[4:]))
        elif line.startswith('#### '):
            children.append(make_heading_block(4, line[5:]))
        elif line.startswith('---'):
            children.append(make_divider())
        elif line.strip().startswith('- '):
            children.append(make_bullet_block(line.strip()))
        elif re.match(r'^\d+\.\s+', line.strip()):
            children.append(make_numbered_block(line.strip()))
        elif line.strip():
            children.append(make_text_block(line.strip()))
    
    return children


def write_to_feishu_doc(doc_id: str, blocks: List[Dict], token: str, append: bool = True) -> bool:
    """将内容块写入飞书文档"""
    
    if not append:
        # 清除现有内容
        blocks_resp = requests.get(
            f"https://open.feishu.cn/open-apis/docx/v1/documents/{doc_id}/blocks/{doc_id}/children",
            headers={"Authorization": f"Bearer {token}"}
        )
        existing_blocks = blocks_resp.json().get("data", {}).get("items", [])
        
        for block in existing_blocks:
            block_id = block.get("block_id")
            requests.delete(
                f"https://open.feishu.cn/open-apis/docx/v1/documents/{doc_id}/blocks/{block_id}",
                headers={"Authorization": f"Bearer {token}"}
            )
        print(f"Cleared {len(existing_blocks)} existing blocks")
    else:
        # 追加模式：先添加分隔线
        blocks = [make_divider()] + blocks
    
    # 批量创建块
    batch_size = 30
    success_count = 0
    
    for i in range(0, len(blocks), batch_size):
        batch = blocks[i:i+batch_size]
        resp = requests.post(
            f"https://open.feishu.cn/open-apis/docx/v1/documents/{doc_id}/blocks/{doc_id}/children",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            json={"children": batch}
        )
        result = resp.json()
        if result.get("code") == 0:
            success_count += len(batch)
            print(f"Batch {i//batch_size + 1}: Added {len(batch)} blocks")
        else:
            print(f"Batch {i//batch_size + 1} error: {result.get('msg')}")
    
    print(f"Total blocks added: {success_count}/{len(blocks)}")
    return success_count == len(blocks)


def main():
    parser = argparse.ArgumentParser(description="Write Daily Paper to Feishu Doc")
    parser.add_argument("--input", type=str, required=True, help="Input markdown file")
    parser.add_argument("--doc-id", type=str, required=True, help="Feishu document ID")
    parser.add_argument("--replace", action="store_true", help="Replace instead of append")
    args = parser.parse_args()
    
    # 读取 markdown 文件
    with open(args.input, "r", encoding="utf-8") as f:
        content = f.read()
    
    print(f"Read {len(content)} characters from {args.input}")
    
    # 转换为飞书块
    blocks = parse_markdown_to_blocks(content)
    print(f"Parsed {len(blocks)} blocks")
    
    # 获取 token
    token = get_tenant_token()
    
    # 写入飞书
    success = write_to_feishu_doc(args.doc_id, blocks, token, append=not args.replace)
    
    if success:
        print(f"Successfully wrote to https://chj.feishu.cn/docx/{args.doc_id}")
    else:
        print("Some blocks failed to write")
    
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
