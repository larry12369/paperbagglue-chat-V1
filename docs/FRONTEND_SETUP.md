# 📦 前端代码包使用说明

## 🎯 这个文件包包含什么？

将以下文件上传到你的网站即可使用聊天功能：

1. **chat-widget.js** - 聊天小部件JavaScript文件（必须）
2. **chat-widget.html** - 完整聊天页面（可选）
3. **embed-code.txt** - 嵌入代码示例（参考）

---

## 🚀 三步集成到你的网站

### 第1步：上传文件

通过你的网站后台，将文件上传到网站目录：

```
你的网站根目录/
├── js/
│   └── chat-widget.js    ← 上传这个文件
└── chat.html             ← 可选：上传这个文件
```

**如何上传：**
1. 登录你的网站后台
2. 找到"文件管理"或"上传文件"功能
3. 将 `chat-widget.js` 上传到 `js` 文件夹
4. 如果没有 `js` 文件夹，可以先创建

### 第2步：添加嵌入代码

在你想显示聊天的页面HTML中，添加以下代码：

**位置：** 在 `</body>` 标签之前

```html
<!-- 聊天小部件代码 - 添加到</body>标签之前 -->
<script src="/js/chat-widget.js"></script>
<script>
  new ChatWidget({
    apiUrl: 'https://你的Render地址.onrender.com'
  });
</script>
```

### 第3步：测试

1. 保存并发布你的网站
2. 刷新页面
3. 你应该看到右下角有一个紫色的聊天按钮 💬
4. 点击按钮，发送消息测试

---

## 📝 完整示例

假设你的网站是 `www.paperbagglue.com`，你的Render地址是 `https://paperbagglue-chat.onrender.com`

### 在网站首页添加聊天功能

打开你的网站首页HTML文件，找到 `</body>` 标签，在它之前添加：

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Paper Bag Glue</title>
    <!-- 你的其他代码 -->
</head>
<body>
    <!-- 你的网站内容 -->
    <header>...</header>
    <main>...</main>
    <footer>...</footer>

    <!-- 聊天小部件 - 添加到这里 -->
    <script src="/js/chat-widget.js"></script>
    <script>
      new ChatWidget({
        apiUrl: 'https://paperbagglue-chat.onrender.com'
      });
    </script>
</body>
</html>
```

---

## 🎨 自定义样式

### 修改主题颜色

1. 打开 `chat-widget.js` 文件
2. 找到这两行：
   ```javascript
   background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
   ```
3. 替换为你喜欢的颜色：
   ```javascript
   // 蓝色主题
   background: linear-gradient(135deg, #2196F3 0%, #21CBF3 100%);
   
   // 绿色主题
   background: linear-gradient(135deg, #00b09b 0%, #96c93d 100%);
   
   // 橙色主题
   background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
   ```
4. 保存并重新上传文件

### 修改聊天按钮位置

在 `.pbglue-chat-button` CSS类中修改：

```css
.pbglue-chat-button {
    /* 默认在右下角 */
    bottom: 30px;
    right: 30px;
    
    /* 改为左下角 */
    bottom: 30px;
    left: 30px;
}
```

---

## 📱 使用完整聊天页面

如果你想要一个独立的聊天页面（不是浮动按钮）：

### 方法1：使用提供的HTML文件

1. 上传 `chat-widget.html` 到网站根目录
2. 修改文件中的API地址：
   ```javascript
   const API_BASE_URL = 'https://你的Render地址.onrender.com';
   ```
3. 在导航中添加链接：
   ```html
   <a href="/chat.html">💬 Chat with Us</a>
   ```

### 方法2：嵌入到现有页面

在任何页面中添加iframe：

```html
<iframe 
    src="/chat.html" 
    width="100%" 
    height="600" 
    frameborder="0">
</iframe>
```

---

## 🔍 常见问题

### Q1: 聊天按钮不显示

**可能原因：**
- 文件路径错误
- JavaScript被浏览器阻止
- API地址配置错误

**解决方法：**
1. 按F12打开浏览器开发者工具
2. 查看 **Console** 标签是否有错误
3. 确认文件路径：`/js/chat-widget.js` 必须能访问
4. 检查API地址是否正确

### Q2: 发送消息无响应

**可能原因：**
- 后端服务未启动
- API地址错误
- 网络连接问题

**解决方法：**
1. 检查Render服务是否正常运行
2. 在浏览器中访问：`https://你的Render地址.onrender.com/health`
3. 应该看到：`{"status":"healthy","agent_loaded":true}`
4. 如果看到这个，说明后端正常，检查前端API地址配置

### Q3: 如何只在某些页面显示聊天

在页面中添加条件代码：

```html
<!-- 只在首页显示 -->
<script>
  if (window.location.pathname === '/' || window.location.pathname === '/index.html') {
    new ChatWidget({
      apiUrl: 'https://你的Render地址.onrender.com'
    });
  }
</script>
```

### Q4: 如何隐藏聊天按钮，用其他方式触发

```html
<!-- 自定义触发按钮 -->
<button onclick="chatWidget.openChat()">💬 联系客服</button>

<script src="/js/chat-widget.js"></script>
<script>
  const chatWidget = new ChatWidget({
    apiUrl: 'https://你的Render地址.onrender.com'
  });
  
  // 隐藏默认浮动按钮
  document.querySelector('.pbglue-chat-button').style.display = 'none';
</script>
```

---

## 📞 需要帮助？

如果遇到问题：
1. 按F12打开开发者工具查看错误
2. 检查API地址是否正确
3. 确认Render服务是否正常运行
4. 查看 `docs/RENDER_DEPLOYMENT.md` 获取更多帮助

---

## ✅ 完成检查清单

- [ ] 已上传 `chat-widget.js` 到网站
- [ ] 已在HTML中添加嵌入代码
- [ ] 已修改API地址为你的Render地址
- [ ] 已测试聊天按钮是否显示
- [ ] 已测试发送消息是否正常
- [ ] 已在手机端测试（响应式）

---

## 🎉 恭喜！

如果以上都完成，你的网站现在有了智能客服功能！

访问你的网站 www.paperbagglue.com，你应该能在右下角看到聊天按钮！
