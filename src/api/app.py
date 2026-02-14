"""
Flask API Service for Customer Support Agent
提供客服智能体的HTTP API接口
"""

from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS
import uuid
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
    """聊天接口（非流式）"""
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
        
        logger.info(f"Received message: {message[:50]}... (session: {session_id})")
        
        result = agent_instance.invoke(
            {"messages": [("user", message)]},
            config={"configurable": {"thread_id": session_id}}
        )
        
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
    """聊天接口（流式响应）"""
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
                full_response = ""
                
                for chunk in agent_instance.stream(
                    {"messages": [("user", message)]},
                    config={"configurable": {"thread_id": session_id}},
                    stream_mode="messages"
                ):
                    if hasattr(chunk, 'content'):
                        content = chunk.content
                        if content:
                            full_response += content
                            yield f"data: {json.dumps({'content': content, 'done': False})}\n\n"
                
                logger.info(f"Stream response completed (session: {session_id})")
                yield f"data: {json.dumps({'content': '', 'done': True, 'session_id': session_id})}\n\n"
                
            except Exception as e:
                logger.error(f"Error in stream: {e}", exc_info=True)
                yield f"data: {json.dumps({'error': str(e), 'done': True})}\n\n"
        
        return Response(
            stream_with_context(generate()),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'X-Accel-Buffering': 'no'
            }
        )
        
    except Exception as e:
        logger.error(f"Error in chat_stream: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/api/config', methods=['GET'])
def get_config():
    """获取配置信息"""
    if not agent_config:
        return jsonify({'error': 'Agent not initialized'}), 500
    
    return jsonify({
        'model': agent_config['config'].get('model'),
        'company_info': {
            'website': 'www.paperbagglue.com',
            'whatsapp': '+8613323273311',
            'email': 'LarryChen@paperbagglue.com'
        }
    })


if __name__ == '__main__':
    # 初始化Agent
    initialize_agent()
    
    # 启动Flask服务
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True, threaded=True)
