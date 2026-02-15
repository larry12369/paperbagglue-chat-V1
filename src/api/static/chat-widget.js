/**
 * 纸邦胶业智能客服聊天组件
 * 完整版代码托管在 Render 服务
 */
(function() {
  'use strict';

  // ==================== 配置 ====================
  const CONFIG = {
    API_URL: 'https://paperbagglue-chat.onrender.com/api/chat',
    WIDGET_ID: 'chat-widget-container',
  };

  // 生成会话ID
  let sessionId = 'session-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);

  // ==================== 创建HTML结构 ====================
  function createWidgetHTML() {
    return `
      <div id="chat-widget-container">
        <!-- 聊天按钮 -->
        <button id="chat-toggle-btn" onclick="window.chatWidget.toggle()">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M20 2H4C2.9 2 2 2.9 2 4V22L6 18H20C21.1 18 22 17.1 22 16V4C22 2.9 21.1 2 20 2ZM20 16H6L4 18V4H20V16Z" fill="white"/>
            <circle cx="9" cy="11" r="1.5" fill="#00A859"/>
            <circle cx="12" cy="11" r="1.5" fill="#00A859"/>
            <circle cx="15" cy="11" r="1.5" fill="#00A859"/>
          </svg>
          <span>咨询</span>
        </button>

        <!-- 聊天窗口 -->
        <div id="chat-window">
          <!-- 聊天头部 -->
          <div class="chat-header">
            <div class="chat-header-left">
              <img src="https://paperbagglue.com/wp-content/uploads/2025/01/logo.png" alt="Logo" class="chat-logo" onerror="this.style.display='none'">
              <div class="chat-header-info">
                <h3>Larry Chen</h3>
                <p class="online-status">● 在线</p>
              </div>
            </div>
            <button class="close-btn" onclick="window.chatWidget.toggle()">×</button>
          </div>

          <!-- 欢迎消息 -->
          <div id="welcome-message" class="message bot-message">
            <div class="message-content">
              <p>您好！我是河北鑫邦包装材料有限公司的销售经理 Larry Chen。👋</p>
              <p>我可以帮您：</p>
              <ul>
                <li>推荐适合的环保水性胶水</li>
                <li>提供产品技术参数</li>
                <li>解答生产应用问题</li>
                <li>获取报价和样品</li>
              </ul>
              <p>请问有什么可以帮助您的吗？😊</p>
            </div>
          </div>

          <!-- 消息区域 -->
          <div id="chat-messages" class="chat-messages"></div>

          <!-- 输入区域 -->
          <div class="chat-input-area">
            <textarea 
              id="chat-input" 
              placeholder="输入您的问题..." 
              rows="2"
            ></textarea>
            <button id="send-btn" onclick="window.chatWidget.send()" disabled>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z" fill="white"/>
              </svg>
            </button>
          </div>
        </div>
      </div>
    `;
  }

  // ==================== 创建CSS样式 ====================
  function createWidgetCSS() {
    return `
      <style>
        /* 聊天组件容器 */
        #chat-widget-container {
          position: fixed !important;
          bottom: 30px !important;
          right: 30px !important;
          z-index: 9999 !important;
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif !important;
        }

        /* 聊天按钮 */
        #chat-toggle-btn {
          position: fixed !important;
          bottom: 30px !important;
          right: 30px !important;
          width: 60px !important;
          height: 60px !important;
          border-radius: 50% !important;
          background: linear-gradient(135deg, #00A859 0%, #008F4D 100%) !important;
          border: none !important;
          cursor: pointer !important;
          box-shadow: 0 4px 12px rgba(0, 168, 89, 0.4) !important;
          display: flex !important;
          flex-direction: column !important;
          align-items: center !important;
          justify-content: center !important;
          transition: all 0.3s ease !important;
          z-index: 10000 !important;
        }

        #chat-toggle-btn:hover {
          transform: scale(1.05) !important;
          box-shadow: 0 6px 16px rgba(0, 168, 89, 0.5) !important;
        }

        #chat-toggle-btn span {
          color: white !important;
          font-size: 12px !important;
          margin-top: 2px !important;
          font-weight: 600 !important;
        }

        #chat-toggle-btn svg {
          width: 24px !important;
          height: 24px !important;
        }

        /* 聊天窗口 */
        #chat-window {
          position: fixed !important;
          bottom: 100px !important;
          right: 30px !important;
          width: 380px !important;
          height: 500px !important;
          background: white !important;
          border-radius: 16px !important;
          box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15) !important;
          display: none !important;
          flex-direction: column !important;
          z-index: 9999 !important;
          overflow: hidden !important;
        }

        #chat-window.active {
          display: flex !important;
          animation: slideIn 0.3s ease !important;
        }

        @keyframes slideIn {
          from { opacity: 0; transform: translateY(20px); }
          to { opacity: 1; transform: translateY(0); }
        }

        /* 聊天头部 */
        .chat-header {
          background: linear-gradient(135deg, #00A859 0%, #008F4D 100%) !important;
          color: white !important;
          padding: 20px !important;
          display: flex !important;
          justify-content: space-between !important;
          align-items: center !important;
        }

        .chat-header-left {
          display: flex !important;
          align-items: center !important;
          gap: 12px !important;
        }

        .chat-logo {
          width: 45px !important;
          height: 45px !important;
          border-radius: 50% !important;
          background: white !important;
          padding: 2px !important;
          object-fit: contain !important;
        }

        .chat-header-info h3 {
          margin: 0 !important;
          font-size: 16px !important;
          font-weight: 600 !important;
        }

        .online-status {
          margin: 0 !important;
          font-size: 12px !important;
          opacity: 0.9 !important;
        }

        .close-btn {
          background: none !important;
          border: none !important;
          color: white !important;
          font-size: 28px !important;
          cursor: pointer !important;
          width: 30px !important;
          height: 30px !important;
          display: flex !important;
          align-items: center !important;
          justify-content: center !important;
          border-radius: 50% !important;
          transition: background 0.2s !important;
        }

        .close-btn:hover {
          background: rgba(255, 255, 255, 0.2) !important;
        }

        /* 消息区域 */
        .chat-messages {
          flex: 1 !important;
          overflow-y: auto !important;
          padding: 20px !important;
          background: #f8f9fa !important;
        }

        #welcome-message {
          margin-bottom: 20px !important;
        }

        .message {
          display: flex !important;
          margin-bottom: 16px !important;
          animation: fadeIn 0.3s ease !important;
        }

        @keyframes fadeIn {
          from { opacity: 0; }
          to { opacity: 1; }
        }

        .bot-message {
          justify-content: flex-start !important;
        }

        .user-message {
          justify-content: flex-end !important;
        }

        .message-content {
          max-width: 80% !important;
          padding: 12px 16px !important;
          border-radius: 12px !important;
          font-size: 14px !important;
          line-height: 1.5 !important;
          word-wrap: break-word !important;
        }

        .bot-message .message-content {
          background: white !important;
          color: #333 !important;
          border-bottom-left-radius: 4px !important;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05) !important;
        }

        .user-message .message-content {
          background: linear-gradient(135deg, #00A859 0%, #008F4D 100%) !important;
          color: white !important;
          border-bottom-right-radius: 4px !important;
        }

        .message-content p {
          margin: 0 0 8px 0 !important;
        }

        .message-content p:last-child {
          margin: 0 !important;
        }

        .message-content ul {
          margin: 0 !important;
          padding-left: 20px !important;
        }

        .message-content li {
          margin: 4px 0 !important;
        }

        /* 输入区域 */
        .chat-input-area {
          padding: 16px !important;
          background: white !important;
          border-top: 1px solid #e8e8e8 !important;
          display: flex !important;
          gap: 12px !important;
          align-items: flex-end !important;
        }

        #chat-input {
          flex: 1 !important;
          border: 1px solid #d9d9d9 !important;
          border-radius: 8px !important;
          padding: 10px 12px !important;
          font-size: 14px !important;
          resize: none !important;
          outline: none !important;
          transition: border-color 0.2s !important;
          font-family: inherit !important;
          max-height: 100px !important;
        }

        #chat-input:focus {
          border-color: #00A859 !important;
        }

        #send-btn {
          width: 40px !important;
          height: 40px !important;
          border-radius: 8px !important;
          background: linear-gradient(135deg, #00A859 0%, #008F4D 100%) !important;
          border: none !important;
          color: white !important;
          cursor: pointer !important;
          display: flex !important;
          align-items: center !important;
          justify-content: center !important;
          transition: all 0.2s !important;
        }

        #send-btn:hover:not(:disabled) {
          transform: scale(1.05) !important;
          box-shadow: 0 2px 8px rgba(0, 168, 89, 0.4) !important;
        }

        #send-btn:disabled {
          opacity: 0.5 !important;
          cursor: not-allowed !important;
        }

        #send-btn svg {
          width: 20px !important;
          height: 20px !important;
        }

        /* 加载动画 */
        .typing-indicator {
          display: flex !important;
          gap: 4px !important;
          padding: 12px 16px !important;
        }

        .typing-indicator span {
          width: 8px !important;
          height: 8px !important;
          background: #999 !important;
          border-radius: 50% !important;
          animation: typing 1.4s infinite ease-in-out !important;
        }

        .typing-indicator span:nth-child(1) {
          animation-delay: -0.32s !important;
        }

        .typing-indicator span:nth-child(2) {
          animation-delay: -0.16s !important;
        }

        @keyframes typing {
          0%, 80%, 100% {
            transform: scale(0.6);
            opacity: 0.5;
          }
          40% {
            transform: scale(1);
            opacity: 1;
          }
        }

        /* 移动端适配 */
        @media (max-width: 480px) {
          #chat-widget-container {
            bottom: 20px !important;
            right: 20px !important;
          }

          #chat-toggle-btn {
            width: 55px !important;
            height: 55px !important;
            bottom: 20px !important;
            right: 20px !important;
          }

          #chat-window {
            width: calc(100vw - 40px) !important;
            height: calc(100vh - 120px) !important;
            bottom: 80px !important;
            right: 20px !important;
            border-radius: 12px !important;
          }

          .chat-header {
            padding: 16px !important;
          }

          .chat-logo {
            width: 40px !important;
            height: 40px !important;
          }

          .chat-header-info h3 {
            font-size: 14px !important;
          }
        }
      </style>
    `;
  }

  // ==================== 功能函数 ====================
  function toggleChat() {
    const chatWindow = document.getElementById('chat-window');
    const toggleBtn = document.getElementById('chat-toggle-btn');

    if (chatWindow.classList.contains('active')) {
      chatWindow.classList.remove('active');
      toggleBtn.style.display = 'flex';
    } else {
      chatWindow.classList.add('active');
      toggleBtn.style.display = 'none';

      setTimeout(() => {
        document.getElementById('chat-input').focus();
      }, 300);
    }
  }

  function handleKeyDown(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      send();
    }
  }

  async function send() {
    const input = document.getElementById('chat-input');
    const message = input.value.trim();

    if (!message) return;

    input.disabled = true;
    document.getElementById('send-btn').disabled = true;

    addMessage(message, 'user');
    input.value = '';

    showTypingIndicator();

    try {
      const response = await fetch(CONFIG.API_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: message,
          session_id: sessionId
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      removeTypingIndicator();

      if (data.response) {
        addMessage(data.response, 'bot');
      } else {
        throw new Error('No response from server');
      }

    } catch (error) {
      console.error('Error:', error);

      removeTypingIndicator();

      addMessage('抱歉，我遇到了一些问题。请稍后再试，或者通过以下方式联系我们：\n\n📱 WhatsApp: +8613323273311\n📧 Email: LarryChen@paperbagglue.com', 'bot');
    } finally {
      input.disabled = false;
      document.getElementById('send-btn').disabled = true;
      input.focus();
    }
  }

  function addMessage(content, type) {
    const messagesContainer = document.getElementById('chat-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}-message`;

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';

    const processedContent = processMessageContent(content);
    contentDiv.innerHTML = processedContent;

    messageDiv.appendChild(contentDiv);
    messagesContainer.appendChild(messageDiv);

    scrollToBottom();
  }

  function processMessageContent(content) {
    let processed = content
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');

    processed = processed.replace(/\n/g, '<br>');

    processed = processed.replace(
      /(https?:\/\/[^\s]+)/g,
      '<a href="$1" target="_blank" style="color: #00A859; text-decoration: underline;">$1</a>'
    );

    processed = processed.replace(
      /\*\*([^*]+)\*\*/g,
      '<strong>$1</strong>'
    );

    return processed;
  }

  function showTypingIndicator() {
    const messagesContainer = document.getElementById('chat-messages');
    const typingDiv = document.createElement('div');
    typingDiv.className = 'message bot-message';
    typingDiv.id = 'typing-indicator';

    typingDiv.innerHTML = `
      <div class="typing-indicator">
        <span></span>
        <span></span>
        <span></span>
      </div>
    `;

    messagesContainer.appendChild(typingDiv);
    scrollToBottom();
  }

  function removeTypingIndicator() {
    const typingIndicator = document.getElementById('typing-indicator');
    if (typingIndicator) {
      typingIndicator.remove();
    }
  }

  function scrollToBottom() {
    const messagesContainer = document.getElementById('chat-messages');
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
  }

  // ==================== 初始化 ====================
  function init() {
    // 检查是否已加载
    if (document.getElementById(CONFIG.WIDGET_ID)) {
      console.log('Chat widget already loaded');
      return;
    }

    // 插入CSS
    document.head.insertAdjacentHTML('beforeend', createWidgetCSS());

    // 插入HTML
    document.body.insertAdjacentHTML('beforeend', createWidgetHTML());

    // 绑定事件
    const chatInput = document.getElementById('chat-input');
    chatInput.addEventListener('input', function() {
      const sendBtn = document.getElementById('send-btn');
      sendBtn.disabled = this.value.trim() === '';
    });

    chatInput.addEventListener('keydown', handleKeyDown);

    // 暴露全局API
    window.chatWidget = {
      toggle: toggleChat,
      send: send,
      open: function() {
        if (!document.getElementById('chat-window').classList.contains('active')) {
          toggleChat();
        }
      },
      close: function() {
        if (document.getElementById('chat-window').classList.contains('active')) {
          toggleChat();
        }
      }
    };

    console.log('PaperBagGlue Chat Widget loaded successfully');
  }

  // 页面加载完成后初始化
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();
