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
    
    # Pattern for bold: **text**
    bold_pattern = re.compile(r'\*\*([^*]+)\*\*')
    # Pattern for link: [text](url)
    link_pattern = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
    
    while pos < len(text):
        # Find next bold
        bold_match = bold_pattern.search(text, pos)
        # Find next link
        link_match = link_pattern.search(text, pos)
        
        # Determine which comes first
        next_match = None
        match_type = None
        
        if bold_match and link_match:
            if bold_match.start() < link_match.start():
                next_match = bold_match
                match_type = 'bold'
            else:
                next_match = link_match
                match_type = 'link'
        elif bold_match:
            next_match = bold_match
            match_type = 'bold'
        elif link_match:
            next_match = link_match
            match_type = 'link'
            
        if next_match:
            # Add text before match
            if next_match.start() > pos:
                elements.append({"text_run": {"content": text[pos:next_match.start()]}})
            
            if match_type == 'bold':
                content = next_match.group(1)
                elements.append({
                    "text_run": {
                        "content": content,
                        "text_element_style": {"bold": True}
                    }
                })
            elif match_type == 'link':
                content = next_match.group(1)
                url = next_match.group(2)
                elements.append({
                    "text_run": {
                        "content": content,
                        "text_element_style": {
                            "link": {"url": url}
                        }
                    }
                })
            
            pos = next_match.end()
        else:
            # No more matches
            elements.append({"text_run": {"content": text[pos:]}})
            break
            
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


def get_indent_level(line: str) -> int:
    """计算行的缩进级别（每 2 个空格或 1 个 tab 为一级）"""
    indent = 0
    for char in line:
        if char == ' ':
            indent += 1
        elif char == '\t':
            indent += 2
        else:
            break
    return indent // 2


def parse_markdown_to_blocks(content: str) -> List[Dict]:
    """将 Markdown 转换为飞书文档块，支持嵌套列表"""
    children = []
    lines = content.split('\n')
    
    # 用于追踪列表嵌套的栈：[(indent_level, block_index)]
    list_stack = []
    
    for line in lines:
        stripped = line.strip()
        indent_level = get_indent_level(line)
        
        if line.startswith('# '):
            list_stack = []  # 标题重置列表栈
            children.append(make_heading_block(1, line[2:]))
        elif line.startswith('## '):
            list_stack = []
            children.append(make_heading_block(2, line[3:]))
        elif line.startswith('### '):
            list_stack = []
            children.append(make_heading_block(3, line[4:]))
        elif line.startswith('#### '):
            list_stack = []
            children.append(make_heading_block(4, line[5:]))
        elif line.startswith('---'):
            list_stack = []
            children.append(make_divider())
        elif stripped.startswith('- '):
            block = make_bullet_block(stripped)
            
            if indent_level == 0:
                # 顶级列表项
                list_stack = [(0, len(children))]
                children.append(block)
            else:
                # 嵌套列表项 - 作为独立块添加（飞书 API 不支持真正嵌套，用缩进文本代替）
                # 在文本前添加缩进标记
                indent_prefix = "　　" * indent_level  # 用全角空格缩进
                block = make_bullet_block(indent_prefix + stripped[2:])
                children.append(block)
                
        elif re.match(r'^\d+\.\s+', stripped):
            block = make_numbered_block(stripped)
            
            if indent_level == 0:
                list_stack = [(0, len(children))]
                children.append(block)
            else:
                # 嵌套有序列表项 - 用缩进文本代替
                indent_prefix = "　　" * indent_level
                clean_text = re.sub(r'^\d+\.\s*', '', stripped).strip()
                block = make_bullet_block(indent_prefix + clean_text)
                children.append(block)
                
        elif stripped.startswith('> '):
            # 引用块 - 转为斜体文本
            list_stack = []
            quote_text = stripped[2:]
            elements = parse_text_with_styles(quote_text)
            # 添加斜体样式
            for elem in elements:
                if "text_run" in elem:
                    if "text_element_style" not in elem["text_run"]:
                        elem["text_run"]["text_element_style"] = {}
                    elem["text_run"]["text_element_style"]["italic"] = True
            children.append({
                "block_type": 2,
                "text": {"elements": elements}
            })
        elif stripped:
            list_stack = []
            children.append(make_text_block(stripped))
    
    return children


def write_to_feishu_doc(doc_id: str, blocks: List[Dict], token: str, prepend: bool = True) -> bool:
    """将内容块写入飞书文档
    
    Args:
        doc_id: 飞书文档 ID
        blocks: 要写入的内容块
        token: 飞书 access token
        prepend: True=插入到顶部（时间倒序），False=追加到底部
    """
    
    # 获取文档现有块
    blocks_resp = requests.get(
        f"https://open.feishu.cn/open-apis/docx/v1/documents/{doc_id}/blocks/{doc_id}/children",
        headers={"Authorization": f"Bearer {token}"}
    )
    existing_blocks = blocks_resp.json().get("data", {}).get("items", [])
    
    # 在新内容后添加分隔线
    blocks = blocks + [make_divider()]
    
    # 确定插入位置
    if prepend and existing_blocks:
        # 插入到第一个块之前
        first_block_id = existing_blocks[0].get("block_id")
        index = 0
        print(f"Prepending before block: {first_block_id}")
    else:
        # 追加到末尾
        first_block_id = None
        index = -1
        print("Appending to end of document")
    
    # 批量创建块
    batch_size = 30
    success_count = 0
    
    for i in range(0, len(blocks), batch_size):
        batch = blocks[i:i+batch_size]
        
        # 构建请求
        payload = {"children": batch}
        if prepend and existing_blocks:
            payload["index"] = index
            # 每批次后更新 index（已插入的块数）
            index += len(batch)
        
        resp = requests.post(
            f"https://open.feishu.cn/open-apis/docx/v1/documents/{doc_id}/blocks/{doc_id}/children",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            json=payload
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
    parser.add_argument("--append", action="store_true", help="Append to end instead of prepend to top")
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
    
    # 写入飞书（默认 prepend=True，即新内容放顶部）
    success = write_to_feishu_doc(args.doc_id, blocks, token, prepend=not args.append)
    
    if success:
        print(f"Successfully wrote to https://chj.feishu.cn/docx/{args.doc_id}")
    else:
        print("Some blocks failed to write")
    
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
