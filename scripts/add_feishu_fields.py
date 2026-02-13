#!/usr/bin/env python3
"""
飞书表格字段扩展脚本
添加新的字段以收集更详细的客户信息
"""

import sys
import json
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

    def list_fields(self, app_token: str, table_id: str) -> dict:
        """列出数据表字段"""
        return self._request("GET", f"/bitable/v1/apps/{app_token}/tables/{table_id}/fields")

    def create_field(self, app_token: str, table_id: str, field_name: str, field_type: int = 1) -> dict:
        """创建字段"""
        body = {
            "field_name": field_name,
            "type": field_type
        }
        return self._request("POST", f"/bitable/v1/apps/{app_token}/tables/{table_id}/fields", json=body)

def main():
    """主函数"""
    print("=" * 80)
    print("飞书表格字段扩展 - 添加详细客户信息字段")
    print("=" * 80)

    try:
        # 读取配置
        config_file = Path(__file__).parent.parent / "assets" / "feishu_config.json"

        if not config_file.exists():
            print(f"\n❌ 配置文件不存在: {config_file}")
            print("请先运行: python scripts/init_feishu_table.py")
            return False

        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)

        app_token = config["app_token"]
        table_id = config["table_id"]

        print(f"\n📊 连接到表格:")
        print(f"   App Token: {app_token}")
        print(f"   Table ID: {table_id}")

        client = FeishuBitable()

        # 列出当前已有字段
        print("\n[1/2] 检查当前字段...")
        existing_fields = client.list_fields(app_token, table_id)
        existing_field_names = {field["field_name"] for field in existing_fields.get("data", {}).get("items", [])}

        print(f"   当前已有 {len(existing_field_names)} 个字段:")
        for name in sorted(existing_field_names):
            print(f"     - {name}")

        # 定义要添加的新字段
        print("\n[2/2] 添加新字段...")

        new_fields = [
            # 客户联系方式
            {"name": "客户姓名", "type": 1},
            {"name": "电话", "type": 1},
            {"name": "邮箱", "type": 1},
            {"name": "网站", "type": 1},

            # 客户类型和地理位置
            {"name": "客户类型", "type": 1},  # 代理商/工厂/经销商
            {"name": "国家", "type": 1},
            {"name": "地区", "type": 1},

            # 环境条件
            {"name": "气候类型", "type": 1},
            {"name": "温度", "type": 1},
            {"name": "湿度", "type": 1},

            # 机器信息
            {"name": "机器图片", "type": 1},  # 图片URL
            {"name": "机器型号", "type": 1},
            {"name": "机器详情", "type": 1},

            # 产品信息
            {"name": "产品图片", "type": 1},  # 图片URL
            {"name": "产品类型", "type": 1},
            {"name": "产品详情", "type": 1},

            # 施胶工艺
            {"name": "涂胶方式", "type": 1},
            {"name": "施胶工艺详情", "type": 1},

            # 粘接材质
            {"name": "粘接材质", "type": 1},

            # 生产参数
            {"name": "生产速度", "type": 1},
            {"name": "应用类型", "type": 1},

            # 产品推荐
            {"name": "推荐产品", "type": 1},
            {"name": "产品兴趣", "type": 1},
            {"name": "订单状态", "type": 1},

            # 使用指导
            {"name": "正确使用方法", "type": 1},
            {"name": "存储注意事项", "type": 1},

            # 其他
            {"name": "特殊要求", "type": 1},
            {"name": "备注", "type": 1}
        ]

        added_count = 0
        skipped_count = 0

        for field_def in new_fields:
            field_name = field_def["name"]
            field_type = field_def["type"]

            if field_name in existing_field_names:
                print(f"   ⊘ 跳过 (已存在): {field_name}")
                skipped_count += 1
                continue

            try:
                client.create_field(app_token, table_id, field_name, field_type)
                print(f"   ✓ 添加成功: {field_name}")
                added_count += 1
            except Exception as e:
                print(f"   ✗ 添加失败: {field_name} - {str(e)}")

        print("\n" + "=" * 80)
        print("✅ 字段扩展完成！")
        print("=" * 80)
        print(f"\n📊 统计:")
        print(f"   成功添加: {added_count} 个字段")
        print(f"   已存在跳过: {skipped_count} 个字段")
        print(f"   总计字段数: {len(existing_field_names) + added_count}")

        # 显示访问链接
        access_url = f"https://feishu.cn/base/{app_token}"
        print(f"\n📱 飞书表格访问链接:")
        print(f"   {access_url}")
        print("\n" + "=" * 80)

        return True

    except Exception as e:
        print(f"\n❌ 字段扩展失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
