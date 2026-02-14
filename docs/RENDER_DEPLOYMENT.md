# Render.com 一键部署教程

## 📋 准备工作

### 需要准备：
1. ✅ 一个GitHub账号（如果已有，直接使用）
2. ✅ 一个Render账号（免费注册）
3. ✅ 本地电脑上的项目文件

---

## 🚀 部署步骤（约10分钟）

### 第1步：准备项目文件（2分钟）

在你的本地电脑上，确保项目包含以下文件：

```
/paperbagglue-chat/
├── render.yaml              # Render部署配置（已创建）
├── requirements.txt         # Python依赖
├── config/
│   └── agent_llm_config.json
├── src/
│   ├── agents/
│   │   └── agent.py
│   ├── api/
│   │   └── app.py           # Flask应用
│   ├── tools/
│   │   └── feishu_chat_record.py
│   └── storage/
│       └── memory/
│           └── memory_saver.py
└── README.md
```

### 第2步：上传代码到GitHub（3分钟）

#### 2.1 创建GitHub仓库

1. 访问 [GitHub.com](https://github.com)
2. 点击右上角 **+** → **New repository**
3. 填写信息：
   - Repository name: `paperbagglue-chat`
   - Description: `Paper Bag Glue Customer Service Chat Agent`
   - 选择 **Public** 或 **Private** 都可以
   - ❌ 不要勾选 "Add a README file"
4. 点击 **Create repository**

#### 2.2 上传文件（两种方式）

**方式A：使用GitHub网页上传（推荐，无需安装Git）**

1. 在新创建的仓库页面，点击 **uploading an existing file**
2. 将所有项目文件拖拽到上传区域
3. 等待上传完成
4. 滚动到底部，输入提交信息：
   ```
   Initial commit: Add chat agent code
   ```
5. 点击 **Commit changes**

**方式B：使用Git命令行（如果熟悉Git）**

```bash
# 在项目目录执行
cd /workspace/projects
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/paperbagglue-chat.git
git branch -M main
git push -u origin main
```

### 第3步：注册Render账号（2分钟）

1. 访问 [Render.com](https://render.com)
2. 点击右上角 **Get Started**
3. 选择注册方式：
   - 使用 **GitHub** 账号登录（推荐，方便部署）
   - 或者使用 **Google** 账号登录
   - 或者使用邮箱注册
4. 完成注册（免费，无需信用卡）

### 第4步：连接GitHub并部署（3分钟）

#### 4.1 连接GitHub

1. 登录Render后，点击 **New +** 按钮
2. 选择 **Web Service**
3. 第一次使用会提示连接GitHub，点击 **Connect GitHub**
4. 授权Render访问你的GitHub账号

#### 4.2 选择仓库

1. 在 **Build and deploy from a Git repository** 页面
2. 找到并选择 `paperbagglue-chat` 仓库
3. 点击 **Connect**

#### 4.3 配置部署

Render会自动检测到 `render.yaml` 文件，配置会自动填充：

**自动填充的配置（无需修改）：**
- **Name**: `paperbagglue-chat`
- **Region**: Oregon
- **Branch**: `main`
- **Runtime**: Python 3
- **Build Command**: `pip install --no-cache-dir -r requirements.txt`
- **Start Command**: `gunicorn -w 2 -b 0.0.0.0:$PORT src.api.app:app`

**需要配置的环境变量：**

在 **Environment** 部分，点击 **Add Environment Variable**，添加以下变量：

| Key | Value | 说明 |
|-----|-------|------|
| `COZE_WORKLOAD_IDENTITY_API_KEY` | 你的API密钥 | 从环境变量获取 |
| `COZE_INTEGRATION_MODEL_BASE_URL` | 你的模型API地址 | 从环境变量获取 |
| `COZE_WORKSPACE_PATH` | `/opt/render/project/src` | 固定值 |

**注意：** 你需要从当前开发环境获取这两个API密钥，稍后我会告诉你如何获取。

#### 4.4 选择免费套餐

1. 在 **Instance Type** 下
2. 选择 **Free** 套餐
3. 确认每月免费750小时

#### 4.5 开始部署

1. 检查所有配置无误
2. 点击底部的 **Create Web Service**
3. 等待部署完成（约2-3分钟）

### 第5步：获取API地址（1分钟）

1. 部署完成后，会看到绿色的 **Live** 状态
2. 在顶部找到 **URL**，例如：
   ```
   https://paperbagglue-chat.onrender.com
   ```
3. 复制这个地址，稍后用于前端配置

---

## ✅ 验证部署

### 1. 健康检查

在浏览器中访问：
```
https://paperbagglue-chat.onrender.com/health
```

应该看到：
```json
{
  "status": "healthy",
  "agent_loaded": true
}
```

### 2. 测试聊天接口（可选）

使用curl或Postman测试：
```bash
curl -X POST https://paperbagglue-chat.onrender.com/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello"}'
```

---

## 🔑 获取API密钥

### 从当前环境获取

在项目目录执行：

```bash
# 获取COZE_WORKLOAD_IDENTITY_API_KEY
echo $COZE_WORKLOAD_IDENTITY_API_KEY

# 获取COZE_INTEGRATION_MODEL_BASE_URL
echo $COZE_INTEGRATION_MODEL_BASE_URL
```

### 添加到Render环境变量

1. 进入Render项目页面
2. 点击 **Environment** 标签
3. 点击 **Add Environment Variable**
4. 添加上面获取的两个变量

### 重新部署

添加环境变量后，Render会自动重新部署。

---

## 📱 将聊天功能添加到你的网站

### 方法1：嵌入聊天小部件（推荐）

1. 下载 `src/web/chat-widget.js` 文件
2. 上传到你的网站后台（例如上传到 `/js/` 目录）
3. 在你的网站HTML中添加以下代码：

```html
<!-- 在</body>标签前添加 -->
<script src="/js/chat-widget.js"></script>
<script>
  new ChatWidget({
    apiUrl: 'https://paperbagglue-chat.onrender.com'  // 使用你的Render地址
  });
</script>
```

### 方法2：使用完整聊天页面

1. 下载 `src/web/chat-widget.html` 文件
2. 修改文件中的API地址：
   ```javascript
   const API_BASE_URL = 'https://paperbagglue-chat.onrender.com';
   ```
3. 上传到你的网站
4. 在导航中添加链接：
   ```html
   <a href="/chat.html">💬 Chat with Us</a>
   ```

---

## 🔄 自动部署

配置完成后，每次你推送代码到GitHub，Render会自动重新部署：

```bash
git add .
git commit -m "Update chat agent"
git push
```

---

## 📊 监控和日志

### 查看日志

1. 进入Render项目页面
2. 点击 **Logs** 标签
3. 实时查看应用日志

### 查看指标

1. 点击 **Metrics** 标签
2. 查看CPU、内存、响应时间等

---

## ⚠️ 免费套餐限制

Render免费套餐的限制：
- ✅ 每月750小时运行时间
- ✅ 512MB内存
- ✅ 0.1CPU
- ❌ 15分钟后无访问会自动休眠（下次访问需要约30秒唤醒）
- ❌ 每次重启数据会丢失（但我们使用飞书存储聊天记录，不影响）

**解决方案：**
- 首次访问稍慢是正常的
- 聊天记录保存在飞书，不会丢失

---

## 🆘 常见问题

### Q1: 部署失败

**检查：**
1. 查看 **Logs** 标签的错误信息
2. 确认 `requirements.txt` 包含所有依赖
3. 确认 `render.yaml` 配置正确

### Q2: 环境变量未设置

**解决：**
1. 进入项目页面
2. 点击 **Environment** 标签
3. 添加所有必需的环境变量
4. 等待自动重新部署

### Q3: 15分钟后休眠

**说明：** 这是免费套餐的正常行为

**解决：**
- 接受唤醒时间（约30秒）
- 或者升级到付费套餐（$7/月起）

### Q4: 如何更新代码

**步骤：**
1. 修改本地代码
2. 推送到GitHub：
   ```bash
   git add .
   git commit -m "Update message"
   git push
   ```
3. Render自动检测并重新部署

---

## 📞 需要帮助？

- Render文档：https://render.com/docs
- Render社区：https://community.render.com

---

## 🎉 部署完成！

现在你的客服智能体已经运行在云端，可以在任何地方访问！

下一步：将聊天功能嵌入到你的网站 www.paperbagglue.com
