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

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.agent import build_agent

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


if __name__ == '__main__':
    # 初始化Agent
    initialize_agent()
    
    # 启动Flask服务
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True, threaded=True)
