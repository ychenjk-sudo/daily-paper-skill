import json
import re
import os

def parse_markdown(filepath):
    with open(filepath, 'r') as f:
        content = f.read()
        
    data = {
        "date_range": "2026-02-17 ~ 2026-02-23",
        "summary": "",
        "papers": [],
        "trends": [],
        "links": []
    }
    
    # Extract Summary
    # Match until the first subheading (###) or next main heading (##)
    summary_match = re.search(r'## 本周摘要\n(.*?)\n###', content, re.DOTALL)
    if not summary_match:
        summary_match = re.search(r'## 本周摘要\n(.*?)\n##', content, re.DOTALL)
        
    if summary_match:
        data['summary'] = summary_match.group(1).strip()
        
    # Extract Papers
    # Pattern: #### Title\n- **机构**: Org\n- **作者**: Authors\n- **摘要**: Desc
    # Note: The regex needs to be careful about newlines and formatting
    paper_pattern = re.compile(r'#### (.*?)\n- \*\*机构\*\*: (.*?)\n- \*\*作者\*\*: (.*?)\n- \*\*摘要\*\*: (.*?)\n', re.DOTALL)
    
    # We need to iterate through the content to find papers
    # But the content has multiple sections.
    # Let's extract papers from the whole text.
    # The pattern assumes specific formatting.
    
    papers = []
    for match in paper_pattern.finditer(content):
        papers.append({
            "name": match.group(1).strip(),
            "org": match.group(2).strip(),
            "desc": match.group(4).strip()
        })
    data['papers'] = papers
        
    # Extract Trends
    # Pattern: ### 趋势 \d+: Title\nContent
    # The content might span multiple lines.
    # It ends at the next ### or ## or end of string.
    trend_pattern = re.compile(r'### 趋势 \d+: (.*?)\n(.*?)(?=\n###|\n##|$)', re.DOTALL)
    
    trends = []
    # We only want trends from the "Crossing Trend" section
    trend_section_match = re.search(r'## Crossing Trend\n(.*)', content, re.DOTALL)
    if trend_section_match:
        trend_section = trend_section_match.group(1)
        for match in trend_pattern.finditer(trend_section):
            trends.append({
                "title": match.group(1).strip(),
                "content": match.group(2).strip()
            })
    data['trends'] = trends
        
    # Add Link
    # I need the doc_id from the previous step. I'll hardcode it or pass it as arg.
    # For now, I'll use the one I got: UGpidgTYcomcS4xgRjVcsa4qn3e
    doc_url = "https://chj.feishu.cn/docx/UGpidgTYcomcS4xgRjVcsa4qn3e"
    data['links'].append({
        "name": "完整报告",
        "url": doc_url
    })
    
    return data

if __name__ == "__main__":
    md_path = "/workspace/daily-papers/weekly-2026-02-17-to-2026-02-23.md"
    output_path = "/workspace/data/weekly-paper-2026-02-23.json"
    
    data = parse_markdown(md_path)
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        
    print(f"Card data generated: {output_path}")
