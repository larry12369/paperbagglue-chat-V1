#!/usr/bin/env python3
"""
为飞书表格添加字段
"""

import sys
from pathlib import Path

# 添加项目路径到系统路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from coze_workload_identity import Client
from cozeloop.decorator import observe
import requests
import json


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

    def list_fields(self, app_token: str, table_id: str) -> dict:
        """列出数据表字段"""
        return self._request("GET", f"/bitable/v1/apps/{app_token}/tables/{table_id}/fields")

    def add_field(self, app_token: str, table_id: str, field_name: str, field_type: int = 1) -> dict:
        """添加字段"""
        body = {
            "field_name": field_name,
            "type": field_type
        }
        return self._request("POST", f"/bitable/v1/apps/{app_token}/tables/{table_id}/fields", json=body)


def main():
    """主函数"""
    print("=" * 60)
    print("为飞书表格添加字段")
    print("=" * 60)

    try:
        # 读取配置
        workspace_path = Path(__file__).parent.parent / "assets"
        config_path = workspace_path / "feishu_config.json"

        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)

        app_token = config["app_token"]
        table_id = config["table_id"]

        print(f"\nApp Token: {app_token}")
        print(f"Table ID: {table_id}")

        # 创建客户端
        client = FeishuBitable()

        # 列出当前字段
        print("\n[1] 列出当前字段...")
        fields_response = client.list_fields(app_token, table_id)
        current_fields = fields_response.get("data", {}).get("items", [])
        field_names = {f.get("field_name") for f in current_fields}

        print(f"当前字段: {field_names}")

        # 定义需要添加的字段
        required_fields = {
            "会话ID": 1,
            "客户消息": 1,
            "AI回复": 1,
            "产品兴趣": 1,
            "时间戳": 1,
            "联系方式": 1,
            "备注": 1
        }

        # 添加缺失的字段
        print("\n[2] 添加缺失的字段...")
        for field_name, field_type in required_fields.items():
            if field_name not in field_names:
                try:
                    client.add_field(app_token, table_id, field_name, field_type)
                    print(f"  ✓ 已添加字段: {field_name}")
                except Exception as e:
                    print(f"  ✗ 添加字段 {field_name} 失败: {e}")
            else:
                print(f"  - 字段已存在: {field_name}")

        print("\n✅ 字段添加完成！")
        return True

    except Exception as e:
        print(f"\n❌ 操作失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
