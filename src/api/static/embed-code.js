/**
 * 纸邦胶业智能客服 - 嵌入代码
 * 将此代码粘贴到网站后台的"客服代码"输入框中
 * 代码会自动从Render服务加载完整的聊天组件
 */
(function(){
  var d = document,
    w = window,
    s = d.createElement('script'),
    head = d.getElementsByTagName('head')[0] || d.documentElement;
  s.async = true;
  s.src = 'https://paperbagglue-chat.onrender.com/static/chat-widget.js?v=' + Date.now();
  s.charset = 'UTF-8';
  s.onerror = function() {
    console.error('Failed to load chat widget');
  };
  head.appendChild(s);
  console.log('PaperBagGlue chat widget initializing...');
})();
