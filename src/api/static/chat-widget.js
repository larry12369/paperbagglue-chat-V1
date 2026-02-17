/**
 * 纸邦胶业智能客服聊天组件 - 优化版
 * 添加加载提示和健康检查
 */
(function() {
  'use strict';

  // ==================== 配置 ====================
  const CONFIG = {
    API_URL: 'https://paperbagglue-chat.onrender.com/api/chat',
    UPLOAD_URL: 'https://paperbagglue-chat.onrender.com/api/upload',
    WIDGET_ID: 'chat-widget-container',
    AUTO_OPEN_DELAY: 3000, // 3秒后自动打开
    API_TIMEOUT: 10000, // 10秒超时
    KEEP_ALIVE_INTERVAL: 5 * 60 * 1000, // 5分钟保持活跃
    VERSION: '2.1', // 版本号，用于强制刷新缓存
  };

  // 生成会话ID
  let sessionId = 'session-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);
  let isServiceAvailable = false;
  let keepAliveTimer = null;

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
          <span>Inquiry</span>
        </button>

        <!-- 聊天窗口 -->
        <div id="chat-window">
          <!-- 聊天头部 -->
          <div class="chat-header">
            <div class="chat-header-left">
              <img src="https://paperbagglue.com/wp-content/uploads/2025/01/logo.png" alt="Logo" class="chat-logo" onerror="this.style.display='none'">
              <div class="chat-header-info">
                <h3>Larry Chen</h3>
                <p class="online-status">● <span id="connection-status">Connecting...</span></p>
              </div>
            </div>
            <div class="chat-header-actions">
              <button class="expand-btn" onclick="window.chatWidget.toggleExpand()" title="Expand">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M15 3H21V9" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  <path d="M10 14L21 3" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  <path d="M9 21H3V15" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  <path d="M14 10L3 21" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
              </button>
              <button class="close-btn" onclick="window.chatWidget.toggle()">×</button>
            </div>
          </div>

          <!-- 欢迎消息 -->
          <div id="welcome-message" class="message bot-message">
            <div class="message-content">
              <p>Hello 👋 I'm Larry.</p>
              <p>I recommend or customize adhesives based on your equipment and speed.</p>
              <p>Chat here or WhatsApp: +86 133-2327-3311</p>
            </div>
          </div>

          <!-- 加载提示 -->
          <div id="loading-message" class="message bot-message" style="display: none;">
            <div class="message-content loading-content">
              <div class="loading-spinner"></div>
              <p id="loading-text">Connecting to service...</p>
            </div>
          </div>

          <!-- 消息区域 -->
          <div id="chat-messages" class="chat-messages"></div>

          <!-- 输入区域 -->
          <div class="chat-input-area">
            <input type="file" id="image-upload" accept="image/*" style="display: none;" onchange="window.chatWidget.handleFileUpload(this)">
            <button id="upload-btn" onclick="document.getElementById('image-upload').click()" title="Upload Image">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M21 15V19C21 19.5304 20.7893 20.0391 20.4142 20.4142C20.0391 20.7893 19.5304 21 19 21H5C4.46957 21 3.96086 20.7893 3.58579 20.4142C3.21071 20.7891 3 19.5304 3 19V15" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M17 8L12 3L7 8" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M12 3V15" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </button>
            <textarea 
              id="chat-input" 
              placeholder="Type your message..." 
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
          padding: 8px 12px !important;
          display: flex !important;
          justify-content: space-between !important;
          align-items: center !important;
        }

        .chat-header-left {
          display: flex !important;
          align-items: center !important;
          gap: 8px !important;
        }

        .chat-logo {
          width: 28px !important;
          height: 28px !important;
          border-radius: 50% !important;
          background: white !important;
          padding: 2px !important;
          object-fit: contain !important;
        }

        .chat-header-info h3 {
          margin: 0 !important;
          font-size: 14px !important;
          font-weight: 600 !important;
        }

        .online-status {
          margin: 0 !important;
          font-size: 10px !important;
          opacity: 0.9 !important;
        }

        /* 头部右侧按钮容器 */
        .chat-header-actions {
          display: flex !important;
          gap: 4px !important;
          align-items: center !important;
        }

        /* 放大按钮 */
        .expand-btn {
          background: none !important;
          border: none !important;
          color: white !important;
          cursor: pointer !important;
          width: 26px !important;
          height: 26px !important;
          display: flex !important;
          align-items: center !important;
          justify-content: center !important;
          border-radius: 50% !important;
          transition: background 0.2s !important;
        }

        .expand-btn:hover {
          background: rgba(255, 255, 255, 0.2) !important;
        }

        .expand-btn svg {
          width: 18px !important;
          height: 18px !important;
        }

        /* 放大状态样式 */
        #chat-window.expanded {
          width: 760px !important;
          height: 600px !important;
          bottom: 50px !important;
          right: 50% !important;
          transform: translateX(50%) !important;
        }

        .close-btn {
          background: none !important;
          border: none !important;
          color: white !important;
          font-size: 24px !important;
          cursor: pointer !important;
          width: 26px !important;
          height: 26px !important;
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

        /* 加载样式 */
        .loading-content {
          display: flex !important;
          align-items: center !important;
          gap: 12px !important;
          padding: 12px 16px !important;
        }

        .loading-spinner {
          width: 20px !important;
          height: 20px !important;
          border: 2px solid #f3f3f3 !important;
          border-top: 2px solid #00A859 !important;
          border-radius: 50% !important;
          animation: spin 1s linear infinite !important;
        }

        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }

        #loading-text {
          margin: 0 !important;
          color: #666 !important;
          font-size: 13px !important;
        }

        /* 输入区域 */
        .chat-input-area {
          padding: 12px 16px !important;
          background: white !important;
          border-top: 1px solid #e8e8e8 !important;
          display: flex !important;
          gap: 8px !important;
          align-items: flex-end !important;
        }

        /* Hide upload button - image upload is disabled */
        #upload-btn {
          display: none !important;
        }

        #upload-btn {
          width: 36px !important;
          height: 36px !important;
          border-radius: 8px !important;
          background: #f0f0f0 !important;
          border: 1px solid #d9d9d9 !important;
          color: #666 !important;
          cursor: pointer !important;
          display: flex !important;
          align-items: center !important;
          justify-content: center !important;
          transition: all 0.2s !important;
        }

        #upload-btn:hover {
          background: #e0e0e0 !important;
          color: #333 !important;
        }

        #upload-btn svg {
          width: 18px !important;
          height: 18px !important;
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
          width: 36px !important;
          height: 36px !important;
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
          width: 18px !important;
          height: 18px !important;
        }

        /* 图片消息样式 */
        .message-image {
          max-width: 250px !important;
          max-height: 250px !important;
          border-radius: 8px !important;
          cursor: pointer !important;
          transition: transform 0.2s !important;
        }

        .message-image:hover {
          transform: scale(1.02) !important;
        }

        /* 加载动画 - Larry is typing */
        .typing-indicator-text {
          display: flex !important;
          align-items: center !important;
          gap: 6px !important;
          padding: 12px 16px !important;
          font-size: 14px !important;
          color: #333 !important;
        }

        .typing-indicator-dots {
          display: flex !important;
          gap: 4px !important;
        }

        .typing-indicator-dots span {
          width: 8px !important;
          height: 8px !important;
          background: #999 !important;
          border-radius: 50% !important;
          animation: typing 1.4s infinite ease-in-out !important;
        }

        .typing-indicator-dots span:nth-child(1) {
          animation-delay: -0.32s !important;
        }

        .typing-indicator-dots span:nth-child(2) {
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
            padding: 6px 10px !important;
          }

          .chat-logo {
            width: 24px !important;
            height: 24px !important;
          }

          .chat-header-info h3 {
            font-size: 13px !important;
          }

          .online-status {
            font-size: 9px !important;
          }
        }
      </style>
    `;
  }

  // ==================== 功能函数 ====================
  
  // 健康检查
  async function healthCheck() {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), CONFIG.API_TIMEOUT);
      
      const response = await fetch(CONFIG.API_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: '',
          session_id: sessionId,
          health_check: true
        }),
        signal: controller.signal
      });

      clearTimeout(timeoutId);

      isServiceAvailable = response.ok;
      updateConnectionStatus(isServiceAvailable ? 'Online' : 'Offline');
      
      return isServiceAvailable;
    } catch (error) {
      console.log('Health check failed:', error);
      isServiceAvailable = false;
      updateConnectionStatus('Connecting...');
      return false;
    }
  }

  // 更新连接状态
  function updateConnectionStatus(status) {
    const statusEl = document.getElementById('connection-status');
    if (statusEl) {
      // 显示We're Online而不是Online
      if (status === 'Online') {
        statusEl.textContent = "We're Online";
      } else {
        statusEl.textContent = status;
      }
      
      if (status === 'Online') {
        statusEl.style.color = '#4CAF50';
      } else if (status === 'Offline') {
        statusEl.style.color = '#ff4444';
      } else {
        statusEl.style.color = '#ff9800';
      }
    }
  }

  // Keep-alive定时器
  function startKeepAlive() {
    if (keepAliveTimer) {
      clearInterval(keepAliveTimer);
    }
    
    keepAliveTimer = setInterval(async () => {
      console.log('Keep-alive ping...');
      await healthCheck();
    }, CONFIG.KEEP_ALIVE_INTERVAL);
  }

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

      // 窗口打开时，检查服务状态
      healthCheck();
    }
  }

  function toggleExpand() {
    const chatWindow = document.getElementById('chat-window');
    chatWindow.classList.toggle('expanded');
  }

  function handleKeyDown(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      send();
    }
  }

  async function handleFileUpload(input) {
    const file = input.files[0];
    if (!file) return;

    // 显示用户上传的图片
    const reader = new FileReader();
    reader.onload = function(e) {
      addImageMessage(e.target.result, 'user');
    };
    reader.readAsDataURL(file);

    // 上传到服务器
    const formData = new FormData();
    formData.append('file', file);
    formData.append('session_id', sessionId);

    try {
      const response = await fetch(CONFIG.UPLOAD_URL, {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        throw new Error('Upload failed');
      }

      const result = await response.json();

      // 发送消息通知AI有新图片
      await sendText(`[Image uploaded] ${result.file_id}`);

    } catch (error) {
      console.error('Upload error:', error);
      addMessage('Failed to upload image. Please try again.', 'bot');
    }

    // 清空input
    input.value = '';
  }

  function addImageMessage(imageUrl, type) {
    const messagesContainer = document.getElementById('chat-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}-message`;

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';

    const img = document.createElement('img');
    img.src = imageUrl;
    img.className = 'message-image';
    img.onclick = function() {
      window.open(imageUrl, '_blank');
    };

    contentDiv.appendChild(img);
    messageDiv.appendChild(contentDiv);
    messagesContainer.appendChild(messageDiv);

    scrollToBottom();
  }

  async function send() {
    const input = document.getElementById('chat-input');
    const message = input.value.trim();

    if (!message) return;

    await sendText(message);
    input.value = '';
  }

  async function sendText(message) {
    const input = document.getElementById('chat-input');
    
    input.disabled = true;
    document.getElementById('send-btn').disabled = true;

    if (!message.startsWith('[Image uploaded]')) {
      addMessage(message, 'user');
    }

    showTypingIndicator();

    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), CONFIG.API_TIMEOUT);

      const response = await fetch(CONFIG.API_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: message,
          session_id: sessionId
        }),
        signal: controller.signal
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      removeTypingIndicator();

      if (data.response) {
        addMessage(data.response, 'bot');
        isServiceAvailable = true;
        updateConnectionStatus('Online');
      } else {
        throw new Error('No response from server');
      }

    } catch (error) {
      console.error('Error:', error);

      removeTypingIndicator();

      // 超时或错误，显示备用联系方式
      addMessage(`Sorry, the service is temporarily unavailable. This might be due to high traffic or the service is waking up.\n\nPlease try again in a moment, or contact me directly:\n\n📱 WhatsApp: +8613323273311\n📧 Email: LarryChen@paperbagglue.com`, 'bot');
      
      isServiceAvailable = false;
      updateConnectionStatus('Offline');
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

    // 处理换行
    processed = processed.replace(/\n/g, '<br>');

    // 处理链接（自动链接）
    processed = processed.replace(
      /(https?:\/\/[^\s]+)/g,
      '<a href="$1" target="_blank" rel="noopener noreferrer" style="color: #00A859; text-decoration: underline; font-weight: 500;">$1</a>'
    );

    // 处理加粗文本（**文本**）
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
      <div class="message-content">
        <div class="typing-indicator-text">
          Larry is typing
          <div class="typing-indicator-dots">
            <span></span>
            <span></span>
            <span></span>
          </div>
        </div>
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
      toggleExpand: toggleExpand,
      send: send,
      sendText: sendText,
      handleFileUpload: handleFileUpload,
      open: function() {
        if (!document.getElementById('chat-window').classList.contains('active')) {
          toggleChat();
        }
      },
      close: function() {
        if (document.getElementById('chat-window').classList.contains('active')) {
          toggleChat();
        }
      },
      healthCheck: healthCheck
    };

    console.log('PaperBagGlue Chat Widget loaded successfully');

    // 启动健康检查和keep-alive
    healthCheck().then(() => {
      startKeepAlive();
    });

    // 3秒后自动打开聊天窗口
    setTimeout(function() {
      // 检查用户是否还没有打开过
      if (!document.getElementById('chat-window').classList.contains('active')) {
        window.chatWidget.open();
        console.log('Auto-opened chat widget');
      }
    }, CONFIG.AUTO_OPEN_DELAY);
  }

  // 页面加载完成后初始化
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();
