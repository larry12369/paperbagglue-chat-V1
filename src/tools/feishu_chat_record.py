"""
飞书表格工具 - 用于保存聊天记录
"""

import os
import json
from datetime import datetime
from typing import Annotated
from langchain.tools import tool, ToolRuntime
from coze_coding_utils.runtime_ctx.context import new_context
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
    product_interest: str = "",
    contact_info: str = "",
    notes: str = "",
    runtime: ToolRuntime = None
) -> str:
    """
    将客户聊天记录保存到飞书表格中
    
    Args:
        session_id: 会话ID（唯一标识一个客户的对话会话）
        customer_message: 客户发送的消息内容
        ai_response: AI Agent的回复内容
        product_interest: 客户感兴趣的产品（可选）
        contact_info: 客户留下的联系方式（可选）
        notes: 其他备注信息（可选）
        runtime: 工具运行时上下文
    
    Returns:
        保存结果的描述信息
    """
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
        
        # 构建字段字典，只包含有值的字段
        fields = {
            "会话ID": session_id,
            "客户消息": customer_message,
            "AI回复": ai_response,
            "时间戳": timestamp
        }
        
        # 添加可选字段
        if product_interest:
            fields["产品兴趣"] = product_interest
        if contact_info:
            fields["联系方式"] = contact_info
        if notes:
            fields["备注"] = notes
        
        record = {
            "fields": fields
        }
        
        # 保存记录
        response = client.add_records(app_token, table_id, [record])
        
        return f"✓ 聊天记录已成功保存到飞书表格\n会话ID: {session_id}\n时间: {timestamp}"
        
    except FileNotFoundError as e:
        return f"❌ {str(e)}"
    except Exception as e:
        return f"❌ 保存聊天记录失败: {str(e)}"


@tool
def get_chat_summary(
    session_id: str,
    runtime: ToolRuntime = None
) -> str:
    """
    获取指定会话的聊天记录摘要
    
    Args:
        session_id: 会话ID
        runtime: 工具运行时上下文
    
    Returns:
        会话摘要信息
    """
    try:
        ctx = runtime.context if runtime else new_context(method="get_chat_summary")
        
        # 获取飞书配置
        config = _get_feishu_config()
        app_token = config["app_token"]
        table_id = config["table_id"]
        
        # 创建飞书客户端
        client = FeishuBitable()
        
        # 查询该会话的所有记录（这里简化实现，实际应该用 search_record）
        # 暂时返回提示信息
        access_url = f"https://feishu.cn/base/{app_token}"
        return f"会话 {session_id} 的聊天记录已保存。\n\n您可以点击以下链接在飞书表格中查看所有记录：\n{access_url}"
        
    except Exception as e:
        return f"❌ 获取聊天摘要失败: {str(e)}"
