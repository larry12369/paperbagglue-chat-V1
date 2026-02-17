"""
Flask API Service for Customer Support Agent
提供客服智能体的HTTP API接口
"""

from flask import Flask, request, jsonify, Response, stream_with_context, send_from_directory
from flask_cors import CORS
import uuid
import asyncio
from typing import Dict, Any
import logging
import os
import sys
import json
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.agent import build_agent
from coze_coding_dev_sdk.s3 import S3SyncStorage
from coze_workload_identity import Client
from functools import wraps
from cozeloop.decorator import observe
import requests

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 全局Agent实例
agent_instance = None
agent_config = None


def initialize_agent():
    """初始化Agent实例"""
    global agent_instance, agent_config
    
    try:
        logger.info("Initializing agent...")
        agent_instance = build_agent()
        
        # 读取配置
        config_path = os.path.join(os.getenv('COZE_WORKSPACE_PATH', '/workspace/projects'), 
                                   'config/agent_llm_config.json')
        with open(config_path, 'r', encoding='utf-8') as f:
            agent_config = json.load(f)
        
        logger.info("Agent initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize agent: {e}")
        return False


# ==================== 对象存储初始化 ====================
storage = None

def initialize_storage():
    """初始化对象存储"""
    global storage
    try:
        storage = S3SyncStorage(
            endpoint_url=os.getenv("COZE_BUCKET_ENDPOINT_URL"),
            access_key="",
            secret_key="",
            bucket_name=os.getenv("COZE_BUCKET_NAME"),
            region="cn-beijing",
        )
        logger.info("Storage initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize storage: {e}")
        return False


# ==================== 飞书多维表格集成 ====================
feishu_client = None  # 初始化为 None，表示飞书功能可能不可用
feishu_base_token = None
feishu_table_id = None
feishu_enabled = False  # 标记飞书功能是否可用

def initialize_feishu_client():
    """初始化飞书客户端"""
    global feishu_client, feishu_enabled
    
    try:
        feishu_client = Client()
        feishu_enabled = True
        logger.info("Feishu client initialized successfully")
        return True
    except Exception as e:
        logger.warning(f"Feishu client initialization failed (this is expected on Render): {e}")
        logger.info("Feishu integration is disabled, but the app will continue to run")
        feishu_client = None
        feishu_enabled = False
        return False

def get_feishu_token():
    """获取飞书访问令牌"""
    if feishu_client is None:
        logger.warning("Feishu client is not initialized")
        return None
    return feishu_client.get_integration_credential("integration-feishu-base")

def initialize_feishu():
    """初始化飞书多维表格"""
    global feishu_base_token, feishu_table_id
    
    try:
        access_token = get_feishu_token()
        if not access_token:
            logger.warning("Feishu token not available")
            return False
        
        # 搜索或创建"客服聊天记录"表格
        # 这里使用环境变量或配置来指定base_token和table_id
        feishu_base_token = os.getenv("FEISHU_BASE_TOKEN", "")
        feishu_table_id = os.getenv("FEISHU_TABLE_ID", "")
        
        if not feishu_base_token or not feishu_table_id:
            logger.warning("Feishu base_token or table_id not configured")
            return False
        
        logger.info("Feishu initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize feishu: {e}")
        return False

def save_chat_to_feishu(session_id: str, message_type: str, content: str, file_url: str = None):
    """保存聊天记录到飞书多维表格"""
    try:
        access_token = get_feishu_token()
        if not access_token or not feishu_base_token or not feishu_table_id:
            logger.warning("Feishu not properly configured, skipping save")
            return
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json; charset=utf-8",
        }
        
        # 准备记录数据
        fields = {
            "会话ID": session_id,
            "消息类型": message_type,
            "内容": content,
            "时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        
        if file_url:
            fields["文件链接"] = file_url
        
        # 添加记录到飞书表格
        body = {
            "records": [{"fields": fields}]
        }
        
        url = f"https://open.larkoffice.com/open-apis/bitable/v1/apps/{feishu_base_token}/tables/{feishu_table_id}/records/batch_create"
        response = requests.post(url, headers=headers, json=body, timeout=30)
        
        if response.status_code == 200:
            logger.info(f"Chat record saved to Feishu successfully")
        else:
            logger.warning(f"Failed to save to Feishu: {response.status_code} - {response.text}")
            
    except Exception as e:
        logger.error(f"Error saving to Feishu: {e}")


@app.route('/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({
        'status': 'healthy',
        'agent_loaded': agent_instance is not None
    })


@app.route('/api/chat', methods=['POST'])
def chat():
    """
    聊天接口（非流式）
    
    请求体：
    {
        "message": "用户消息",
        "session_id": "会话ID（可选）",
        "customer_info": {  // 可选
            "name": "客户名称",
            "email": "邮箱",
            "phone": "电话"
        }
    }
    
    返回：
    {
        "response": "AI回复",
        "session_id": "会话ID"
    }
    """
    try:
        data = request.json
        message = data.get('message', '').strip()
        session_id = data.get('session_id', str(uuid.uuid4()))
        customer_info = data.get('customer_info', {})
        
        if not message:
            return jsonify({'error': 'Message is required'}), 400
        
        if not agent_instance:
            if not initialize_agent():
                return jsonify({'error': 'Agent initialization failed'}), 500
        
        # 同步调用Agent
        logger.info(f"Received message: {message[:50]}... (session: {session_id})")
        
        result = agent_instance.invoke(
            {"messages": [("user", message)]},
            config={"configurable": {"thread_id": session_id}}
        )
        
        # 提取AI回复
        response = result["messages"][-1].content
        
        logger.info(f"Response: {response[:50]}... (session: {session_id})")
        
        return jsonify({
            'response': response,
            'session_id': session_id
        })
        
    except Exception as e:
        logger.error(f"Error in chat: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/api/chat/stream', methods=['POST'])
def chat_stream():
    """
    聊天接口（流式响应）
    使用Server-Sent Events (SSE)实现实时流式输出
    
    请求体：
    {
        "message": "用户消息",
        "session_id": "会话ID（可选）",
        "customer_info": {  // 可选
            "name": "客户名称",
            "email": "邮箱",
            "phone": "电话"
        }
    }
    
    返回：SSE流式响应
    """
    try:
        data = request.json
        message = data.get('message', '').strip()
        session_id = data.get('session_id', str(uuid.uuid4()))
        customer_info = data.get('customer_info', {})
        
        if not message:
            return jsonify({'error': 'Message is required'}), 400
        
        if not agent_instance:
            if not initialize_agent():
                return jsonify({'error': 'Agent initialization failed'}), 500
        
        logger.info(f"Received stream message: {message[:50]}... (session: {session_id})")
        
        def generate():
            try:
                # 流式调用Agent
                full_response = ""
                
                for chunk in agent_instance.stream(
                    {"messages": [("user", message)]},
                    config={"configurable": {"thread_id": session_id}},
                    stream_mode="messages"
                ):
                    # 提取消息内容
                    if hasattr(chunk, 'content'):
                        content = chunk.content
                        if content:
                            full_response += content
                            # 发送SSE事件
                            yield f"data: {json.dumps({'content': content, 'done': False})}\n\n"
                
                logger.info(f"Stream response completed (session: {session_id})")
                
                # 发送完成事件
                yield f"data: {json.dumps({'content': '', 'done': True, 'session_id': session_id})}\n\n"
                
            except Exception as e:
                logger.error(f"Error in stream: {e}", exc_info=True)
                yield f"data: {json.dumps({'error': str(e), 'done': True})}\n\n"
        
        return Response(
            stream_with_context(generate()),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'X-Accel-Buffering': 'no'  # 禁用Nginx缓冲
            }
        )
        
    except Exception as e:
        logger.error(f"Error in chat_stream: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/api/config', methods=['GET'])
def get_config():
    """获取Agent配置信息（不含敏感信息）"""
    if not agent_config:
        return jsonify({'error': 'Agent not initialized'}), 500
    
    # 只返回非敏感配置
    return jsonify({
        'model': agent_config['config'].get('model'),
        'company_info': {
            'website': 'www.paperbagglue.com',
            'whatsapp': '+8613323273311',
            'email': 'LarryChen@paperbagglue.com'
        }
    })


@app.route('/')
@app.route('/<path:path>')
def serve_frontend(path=None):
    """
    提供前端页面服务
    所有非API路由都返回前端页面
    """
    try:
        # 获取web目录的绝对路径
        web_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'web')
        
        # 如果路径为空或者是根路径，返回 example-website.html
        if path is None or path == '':
            html_file = os.path.join(web_dir, 'example-website.html')
            if os.path.exists(html_file):
                return send_from_directory(web_dir, 'example-website.html')
        
        # 尝试请求的文件
        if path:
            file_path = os.path.join(web_dir, path)
            if os.path.exists(file_path) and os.path.isfile(file_path):
                return send_from_directory(web_dir, path)
        
        # 如果都不是，返回 index.html 或 example-website.html
        return send_from_directory(web_dir, 'example-website.html')
    except Exception as e:
        logger.error(f"Error serving frontend: {e}")
        return jsonify({'error': 'Page not found'}), 404


@app.route('/static/<path:filename>')
def serve_static(filename):
    """
    提供静态文件服务
    用于提供聊天组件的JavaScript文件
    """
    try:
        static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
        return send_from_directory(static_dir, filename, cache_timeout=0)
    except Exception as e:
        logger.error(f"Error serving static file {filename}: {e}")
        return jsonify({'error': 'File not found'}), 404


@app.route('/api/upload', methods=['POST'])
def upload_file():
    """
    文件上传接口
    支持上传图片并保存到对象存储和飞书多维表格
    
    请求体：
    - multipart/form-data
      - file: 上传的文件
      - session_id: 会话ID（可选）
    
    返回：
    {
        "success": true,
        "file_id": "文件ID",
        "file_url": "文件访问URL",
        "session_id": "会话ID"
    }
    """
    global storage
    
    try:
        # 检查是否有文件
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # 获取session_id
        session_id = request.form.get('session_id', str(uuid.uuid4()))
        
        # 初始化存储（如果还没有初始化）
        if not storage:
            if not initialize_storage():
                return jsonify({'error': 'Storage initialization failed'}), 500
        
        # 读取文件内容
        file_content = file.read()
        file_name = file.filename
        
        # 根据文件类型设置content_type
        content_type = file.content_type or 'application/octet-stream'
        
        # 上传到对象存储
        logger.info(f"Uploading file: {file_name} (size: {len(file_content)} bytes)")
        
        # 使用stream_upload_file上传文件
        import io
        file_obj = io.BytesIO(file_content)
        file_key = storage.stream_upload_file(
            fileobj=file_obj,
            file_name=file_name,
            content_type=content_type,
        )
        
        logger.info(f"File uploaded successfully: {file_key}")
        
        # 生成访问URL
        file_url = storage.generate_presigned_url(key=file_key, expire_time=86400)  # 24小时有效期
        
        # 保存到飞书多维表格
        save_chat_to_feishu(
            session_id=session_id,
            message_type="image_upload",
            content=f"Uploaded file: {file_name}",
            file_url=file_url
        )
        
        return jsonify({
            'success': True,
            'file_id': file_key,
            'file_url': file_url,
            'file_name': file_name,
            'session_id': session_id
        })
        
    except Exception as e:
        logger.error(f"Error in upload_file: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    # 初始化Agent
    initialize_agent()
    
    # 初始化对象存储
    initialize_storage()
    
    # 初始化飞书客户端（可选功能）
    initialize_feishu_client()
    
    # 初始化飞书多维表格（仅当客户端可用时）
    if feishu_enabled:
        initialize_feishu()
    
    # 启动Flask服务
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True, threaded=True)
