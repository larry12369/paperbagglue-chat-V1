"""
飞书表格工具 - 用于保存聊天记录（扩展版）
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

    # 客户联系方式
    customer_name: str = "",
    phone: str = "",
    email: str = "",
    website: str = "",

    # 客户类型和地理位置
    customer_type: str = "",  # 代理商/工厂/经销商
    country: str = "",
    region: str = "",

    # 环境条件
    climate_type: str = "",
    temperature: str = "",
    humidity: str = "",

    # 机器信息
    machine_image: str = "",
    machine_model: str = "",
    machine_details: str = "",

    # 产品信息
    product_image: str = "",
    product_type: str = "",
    product_details: str = "",

    # 施胶工艺
    coating_method: str = "",
    application_details: str = "",

    # 粘接材质
    substrate_material: str = "",

    # 生产参数
    production_speed: str = "",
    application_type: str = "",

    # 产品推荐
    recommended_product: str = "",
    product_interest: str = "",
    order_status: str = "",

    # 使用指导
    usage_instructions: str = "",
    storage_notes: str = "",

    # 其他
    special_requirements: str = "",
    notes: str = "",

    runtime: ToolRuntime = None
) -> str:
    """
    将客户聊天记录保存到飞书表格中（扩展版 - 收集完整客户信息）

    Args:
        session_id: 会话ID
        customer_message: 客户消息
        ai_response: AI回复

        # 客户联系方式
        customer_name: 客户姓名
        phone: 电话
        email: 邮箱
        website: 网站

        # 客户类型和地理位置
        customer_type: 客户类型（代理商/工厂/经销商）
        country: 国家
        region: 地区

        # 环境条件
        climate_type: 气候类型
        temperature: 温度
        humidity: 湿度

        # 机器信息
        machine_image: 机器图片URL
        machine_model: 机器型号
        machine_details: 机器详情

        # 产品信息
        product_image: 产品图片URL
        product_type: 产品类型
        product_details: 产品详情

        # 施胶工艺
        coating_method: 涂胶方式
        application_details: 施胶工艺详情

        # 粘接材质
        substrate_material: 粘接材质

        # 生产参数
        production_speed: 生产速度
        application_type: 应用类型

        # 产品推荐
        recommended_product: 推荐产品
        product_interest: 产品兴趣
        order_status: 订单状态

        # 使用指导
        usage_instructions: 正确使用方法
        storage_notes: 存储注意事项

        # 其他
        special_requirements: 特殊要求
        notes: 备注
        runtime: 工具运行时上下文

    Returns:
        保存结果（空字符串，对客户静默）
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

        # 构建字段字典
        fields = {
            "会话ID": session_id,
            "客户消息": customer_message,
            "AI回复": ai_response,
            "时间戳": timestamp
        }

        # 客户联系方式
        if customer_name:
            fields["客户姓名"] = customer_name
        if phone:
            fields["电话"] = phone
        if email:
            fields["邮箱"] = email
        if website:
            fields["网站"] = website

        # 客户类型和地理位置
        if customer_type:
            fields["客户类型"] = customer_type
        if country:
            fields["国家"] = country
        if region:
            fields["地区"] = region

        # 环境条件
        if climate_type:
            fields["气候类型"] = climate_type
        if temperature:
            fields["温度"] = temperature
        if humidity:
            fields["湿度"] = humidity

        # 机器信息
        if machine_image:
            fields["机器图片"] = machine_image
        if machine_model:
            fields["机器型号"] = machine_model
        if machine_details:
            fields["机器详情"] = machine_details

        # 产品信息
        if product_image:
            fields["产品图片"] = product_image
        if product_type:
            fields["产品类型"] = product_type
        if product_details:
            fields["产品详情"] = product_details

        # 施胶工艺
        if coating_method:
            fields["涂胶方式"] = coating_method
        if application_details:
            fields["施胶工艺详情"] = application_details

        # 粘接材质
        if substrate_material:
            fields["粘接材质"] = substrate_material

        # 生产参数
        if production_speed:
            fields["生产速度"] = production_speed
        if application_type:
            fields["应用类型"] = application_type

        # 产品推荐
        if recommended_product:
            fields["推荐产品"] = recommended_product
        if product_interest:
            fields["产品兴趣"] = product_interest
        if order_status:
            fields["订单状态"] = order_status

        # 使用指导
        if usage_instructions:
            fields["正确使用方法"] = usage_instructions
        if storage_notes:
            fields["存储注意事项"] = storage_notes

        # 其他
        if special_requirements:
            fields["特殊要求"] = special_requirements
        if notes:
            fields["备注"] = notes

        record = {
            "fields": fields
        }

        # 保存记录
        response = client.add_records(app_token, table_id, [record])

        # 返回空字符串，使工具调用对客户完全静默
        return ""

    except FileNotFoundError as e:
        return ""
    except Exception as e:
        return ""


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
        会话摘要信息（空字符串，对客户静默）
    """
    try:
        ctx = runtime.context if runtime else new_context(method="get_chat_summary")

        # 返回空字符串，使工具调用对客户完全静默
        return ""

    except Exception as e:
        return ""
