"""
飞书表格工具 - 用于保存聊天记录（扩展版）
"""

import os
import json
import logging
from datetime import datetime
from typing import Annotated
from langchain.tools import tool, ToolRuntime
from coze_coding_utils.runtime_ctx.context import new_context
from coze_workload_identity import Client
from cozeloop.decorator import observe
import requests

logger = logging.getLogger(__name__)


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

    def add_records(self, app_token: str, table_id: str, records: list) -> dict:
        """批量新增记录"""
        body = {"records": records}
        return self._request("POST", f"/bitable/v1/apps/{app_token}/tables/{table_id}/records/batch_create", json=body)


def _get_feishu_config():
    """获取飞书配置"""
    workspace_path = os.getenv("COZE_WORKSPACE_PATH", "/workspace/projects")
    config_path = os.path.join(workspace_path, "assets/feishu_config.json")

    if not os.path.exists(config_path):
        raise FileNotFoundError(f"飞书配置文件不存在: {config_path}\n请先运行: python scripts/init_feishu_table.py")

    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


@tool
def save_chat_record(
    session_id: str,
    customer_message: str,
    ai_response: str,
    # ... 其他参数省略，完整版本在项目中
    runtime: ToolRuntime = None
) -> str:
    """将客户聊天记录保存到飞书表格中"""
    try:
        ctx = runtime.context if runtime else new_context(method="save_chat_record")
        
        # 获取飞书配置
        config = _get_feishu_config()
        app_token = config["app_token"]
        table_id = config["table_id"]
        
        # 创建飞书客户端
        client = FeishuBitable()
        
        # 准备记录数据
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 构建字段字典
        fields = {
            "会话ID": session_id,
            "客户消息": customer_message,
            "AI回复": ai_response,
            "时间戳": timestamp,
            # ... 其他字段
        }
        
        # 保存记录
        client.add_records(app_token, table_id, [{"fields": fields}])
        
        return ""  # 返回空字符串，对客户静默
        
    except Exception as e:
        logger.error(f"Failed to save chat record: {e}")
        return ""  # 即使失败也返回空字符串


@tool
def get_chat_summary(runtime: ToolRuntime = None) -> str:
    """获取聊天摘要"""
    try:
        ctx = runtime.context if runtime else new_context(method="get_chat_summary")
        
        # 获取飞书配置
        config = _get_feishu_config()
        
        # 查询最近的聊天记录
        # ... 实现逻辑
        
        return ""  # 返回空字符串，对客户静默
        
    except Exception as e:
        logger.error(f"Failed to get chat summary: {e}")
        return ""
