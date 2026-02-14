# 🚀 Paper Bag Glue - Render部署快速检查清单

## 📋 部署前准备

### 准备文件
- [ ] render.yaml（Render部署配置）
- [ ] requirements.txt（Python依赖）
- [ ] config/agent_llm_config.json（Agent配置）
- [ ] src/api/app.py（Flask应用）
- [ ] src/agents/agent.py（Agent代码）
- [ ] src/tools/feishu_chat_record.py（飞书工具）

### 准备账号
- [ ] GitHub账号
- [ ] Render账号

---

## 第1步：上传到GitHub

- [ ] 创建GitHub仓库
- [ ] 上传所有项目文件
- [ ] 确认render.yaml在根目录

---

## 第2步：部署到Render

### 连接账号
- [ ] 登录Render
- [ ] 连接GitHub账号

### 创建服务
- [ ] 点击 "New +"
- [ ] 选择 "Web Service"
- [ ] 选择你的GitHub仓库
- [ ] 点击 "Connect"

### 配置服务
- [ ] 确认自动检测的配置
- [ ] 添加环境变量：
  - [ ] COZE_WORKLOAD_IDENTITY_API_KEY
  - [ ] COZE_INTEGRATION_MODEL_BASE_URL
  - [ ] COZE_WORKSPACE_PATH = `/opt/render/project/src`

### 部署
- [ ] 选择 "Free" 套餐
- [ ] 点击 "Create Web Service"
- [ ] 等待部署完成（2-3分钟）
- [ ] 确认状态显示 "Live"

---

## 第3步：获取API地址

- [ ] 复制Render提供的URL
- [ ] 格式：`https://xxx.onrender.com`
- [ ] 保存这个地址

---

## 第4步：测试后端

### 健康检查
- [ ] 访问：`https://你的URL.onrender.com/health`
- [ ] 确认返回：`{"status":"healthy","agent_loaded":true}`

### 聊天测试
- [ ] 在浏览器控制台运行测试代码
- [ ] 确认能收到AI回复

---

## 第5步：集成到网站

### 上传前端文件
- [ ] 上传 chat-widget.js 到网站 js/ 目录
- [ ] 或上传 chat-widget.html 到网站根目录

### 添加嵌入代码
- [ ] 在HTML的 `</body>` 标签前添加代码
- [ ] 修改API地址为你的Render URL

### 发布网站
- [ ] 保存网站更改
- [ ] 发布网站

---

## 第6步：功能测试

### 基础功能
- [ ] 访问网站，看到聊天按钮
- [ ] 点击聊天按钮，窗口打开
- [ ] 发送测试消息
- [ ] 收到AI回复

### 流式响应
- [ ] 观察打字效果
- [ ] 确认是流式输出

### 多设备测试
- [ ] 电脑浏览器测试
- [ ] 手机浏览器测试

---

## 第7步：数据验证

- [ ] 登录飞书多维表格
- [ ] 确认聊天记录已保存
- [ ] 检查客户信息字段

---

## ✅ 完成标志

当你完成以上所有检查项，你的智能客服已经成功部署！

**最终状态：**
- ✅ 后端服务运行在Render
- ✅ 前端聊天功能集成到网站
- ✅ 聊天记录自动保存到飞书
- ✅ 支持流式响应
- ✅ 支持多设备访问

---

## 🎉 恭喜完成！

现在访问 www.paperbagglue.com，你应该能看到聊天按钮了！

---

## 📚 详细文档

如果需要更详细的说明，请查看：

- **完整部署教程**: `docs/RENDER_DEPLOYMENT.md`
- **前端集成教程**: `docs/FRONTEND_SETUP.md`
- **测试验证指南**: `docs/TESTING_GUIDE.md`
- **网站集成指南**: `docs/WEBSITE_INTEGRATION.md`

---

## 🔧 需要获取API密钥？

在项目目录执行：

```bash
echo $COZE_WORKLOAD_IDENTITY_API_KEY
echo $COZE_INTEGRATION_MODEL_BASE_URL
```

将这两个值添加到Render的环境变量中。

---

## 💡 提示

- Render免费套餐会休眠，首次访问较慢是正常的
- 聊天记录保存在飞书，Render重启不影响
- 每次推送代码到GitHub，Render会自动重新部署

---

## 🆘 遇到问题？

1. 查看Render日志
2. 检查环境变量配置
3. 查看浏览器控制台错误
4. 参考详细文档

祝你部署顺利！🚀
