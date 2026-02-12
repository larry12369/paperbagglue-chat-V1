#!/usr/bin/env python3
"""
飞书表格测试脚本
用于测试飞书 API 连接和基本操作
"""

import sys
from pathlib import Path

# 添加项目路径到系统路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from coze_workload_identity import Client
from cozeloop.decorator import observe
import requests


class FeishuBitable:
    """飞书多维表格客户端"""
    
    def __init__(self, base_url: str = "https://open.larkoffice.com/open-apis", timeout: int = 30):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.access_token = self._get_access_token()
    
    def _get_access_token(self) -> str:
        """获取访问令牌"""
        client = Client()
        return client.get_integration_credential("integration-feishu-base")
    
    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json; charset=utf-8",
        }
    
    @observe
    def _request(self, method: str, path: str, params: dict = None, json: dict = None) -> dict:
        """发送HTTP请求"""
        url = f"{self.base_url}{path}"
        resp = requests.request(method, url, headers=self._headers(), params=params, json=json, timeout=self.timeout)
        resp_data = resp.json()
        
        if resp_data.get("code") != 0:
            raise Exception(f"FeishuBitable API error: {resp_data}")
        
        return resp_data
    
    def list_tables(self, app_token: str) -> dict:
        """列出Base下所有数据表"""
        return self._request("GET", f"/bitable/v1/apps/{app_token}/tables")
    
    def search_base(self, query: str = "客户") -> dict:
        """搜索多维表格"""
        body = {
            "search_key": query,
            "count": 10,
            "offset": 0,
            "docs_types": ["bitable"]
        }
        return self._request("POST", "/suite/docs-api/search/object", json=body)
    
    def get_base_info(self, app_token: str) -> dict:
        """获取 Base 信息"""
        return self._request("GET", f"/bitable/v1/apps/{app_token}")


def main():
    """主函数"""
    print("=" * 60)
    print("飞书表格测试")
    print("=" * 60)
    
    try:
        client = FeishuBitable()
        
        # 测试搜索
        print("\n[1] 搜索现有表格...")
        result = client.search_base("客户")
        print(f"搜索结果: {result}")
        
        # 如果有表格，获取信息
        app_token = None
        if result.get("data", {}).get("docs_entities"):
            for file_info in result["data"]["docs_entities"]:
                if file_info.get("docs_type") == "bitable" and "客户聊天记录" in file_info.get("title", ""):
                    app_token = file_info.get("docs_token")
                    print(f"\n[2] 找到表格: {file_info.get('title')}")
                    print(f"  Token: {app_token}")
                    
                    # 获取表格详情
                    base_info = client.get_base_info(app_token)
                    print(f"  详情: {base_info}")
                    
                    # 列出所有数据表
                    tables = client.list_tables(app_token)
                    print(f"\n[3] 数据表列表:")
                    for table in tables.get("data", {}).get("items", []):
                        print(f"  - {table.get('name')} (ID: {table.get('table_id')})")
                    
                    if tables.get("data", {}).get("items"):
                        # 使用第一个表格
                        first_table = tables["data"]["items"][0]
                        table_id = first_table.get("table_id")
                        print(f"\n[4] 将使用表格: {first_table.get('name')}")
                        print(f"  Table ID: {table_id}")
                        
                        # 保存配置
                        import json
                        config_file = Path(__file__).parent.parent / "config" / "feishu_config.json"
                        config_data = {
                            "app_token": app_token,
                            "table_id": table_id
                        }
                        
                        with open(config_file, 'w', encoding='utf-8') as f:
                            json.dump(config_data, f, ensure_ascii=False, indent=2)
                        
                        print(f"\n✓ 配置已保存到: {config_file}")
                        access_url = f"https://feishu.cn/base/{app_token}"
                        print(f"\n📊 飞书表格访问链接: {access_url}")
                    break
        else:
            print("\n未找到现有表格")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
