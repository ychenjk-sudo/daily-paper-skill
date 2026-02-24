import requests
import json

def create_doc():
    # Get token
    resp = requests.post(
        "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
        json={"app_id": "cli_a99c1819e3f4900b", "app_secret": "qvYVoPKbRyicpoPXYcBG9bn6AIoKmezw"}
    )
    if resp.status_code != 200:
        print(f"Error getting token: {resp.text}")
        return
        
    token = resp.json().get("tenant_access_token")
    if not token:
        print("No token received")
        return

    # Create doc
    resp = requests.post(
        "https://open.feishu.cn/open-apis/docx/v1/documents",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json={"title": "具身智能·每周研究速递（2026-02-17 ~ 2026-02-23）"}
    )
    
    if resp.status_code != 200:
        print(f"Error creating doc: {resp.text}")
        return

    doc_data = resp.json()
    if doc_data.get("code") != 0:
        print(f"API Error: {doc_data}")
        return
        
    doc_id = doc_data["data"]["document"]["document_id"]
    print(f"DOC_ID:{doc_id}")
    
    # Add permissions
    perm_resp = requests.post(
        f"https://open.feishu.cn/open-apis/drive/v1/permissions/{doc_id}/members?type=docx",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json={
            "member_type": "openid",
            "member_id": "ou_6d4bdf64620355814e6bc0cfd8763602",
            "perm": "full_access"
        }
    )
    
    if perm_resp.status_code != 200:
        print(f"Error adding permission: {perm_resp.text}")
    else:
        print("Permissions added successfully.")

if __name__ == "__main__":
    create_doc()
