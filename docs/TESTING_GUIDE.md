# 🧪 部署测试和验证指南

## ✅ 完整部署检查清单

### 阶段1：GitHub准备
- [ ] 项目文件已准备好
- [ ] GitHub仓库已创建
- [ ] 代码已上传到GitHub
- [ ] render.yaml 文件在根目录

### 阶段2：Render部署
- [ ] Render账号已注册
- [ ] GitHub已连接到Render
- [ ] 项目已选择并连接
- [ ] 环境变量已配置
  - [ ] COZE_WORKLOAD_IDENTITY_API_KEY
  - [ ] COZE_INTEGRATION_MODEL_BASE_URL
  - [ ] COZE_WORKSPACE_PATH
- [ ] 免费套餐已选择
- [ ] 部署已启动
- [ ] 部署状态显示 "Live"

### 阶段3：后端验证
- [ ] 健康检查通过
- [ ] API可以正常访问
- [ ] 聊天接口可以正常响应

### 阶段4：前端集成
- [ ] chat-widget.js 已上传到网站
- [ ] 嵌入代码已添加到HTML
- [ ] API地址已正确配置
- [ ] 网站已发布

### 阶段5：功能测试
- [ ] 聊天按钮可以显示
- [ ] 聊天窗口可以打开
- [ ] 可以发送消息
- [ ] 可以收到AI回复
- [ ] 流式响应正常工作
- [ ] 移动端显示正常

---

## 🔍 详细测试步骤

### 测试1：后端健康检查

**步骤：**
1. 打开浏览器
2. 访问：`https://你的Render地址.onrender.com/health`

**预期结果：**
```json
{
  "status": "healthy",
  "agent_loaded": true
}
```

**如果失败：**
- 检查Render日志
- 确认服务是否正在运行
- 确认端口是否正确

### 测试2：普通聊天接口测试

**使用curl测试：**

```bash
curl -X POST https://你的Render地址.onrender.com/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello, I need help with paper bag glue",
    "session_id": "test-session-001"
  }'
```

**预期结果：**
```json
{
  "response": "Hello! I'd be happy to help you with paper bag glue...",
  "session_id": "test-session-001"
}
```

**如果失败：**
- 检查环境变量是否正确配置
- 查看Render日志获取详细错误信息

### 测试3：流式聊天接口测试

**使用浏览器开发者工具测试：**

1. 打开任意网站
2. 按F12打开开发者工具
3. 切换到 **Console** 标签
4. 粘贴以下代码：

```javascript
fetch('https://你的Render地址.onrender.com/api/chat/stream', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    message: 'Tell me about your products',
    session_id: 'test-stream-001'
  })
})
.then(response => {
  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  
  function read() {
    reader.read().then(({done, value}) => {
      if (done) return;
      
      const text = decoder.decode(value);
      console.log('Received:', text);
      read();
    });
  }
  read();
});
```

**预期结果：**
- 控制台会输出多条SSE格式的数据
- 数据格式：`data: {"content":"...","done":false}`

### 测试4：前端集成测试

**步骤：**
1. 访问你的网站 www.paperbagglue.com
2. 查看右下角是否有聊天按钮
3. 点击聊天按钮
4. 发送测试消息：`"I need adhesive for paper bags"`

**预期结果：**
- 聊天按钮显示正常
- 聊天窗口可以打开
- 可以发送消息
- 可以收到AI回复（带打字效果）

**如果失败：**
1. 按F12打开开发者工具
2. 查看 **Console** 标签的错误信息
3. 检查文件路径是否正确
4. 检查API地址是否正确

### 测试5：移动端测试

**步骤：**
1. 使用手机浏览器访问你的网站
2. 或者使用浏览器的手机模拟器（按F12 → 点击手机图标）
3. 测试聊天功能

**预期结果：**
- 聊天按钮在手机上也能正常显示
- 聊天窗口适合手机屏幕
- 可以正常发送和接收消息

---

## 🐛 常见问题和解决方案

### 问题1：健康检查返回404

**原因：** 路由配置错误

**解决：**
1. 检查 `src/api/app.py` 中的路由是否正确
2. 确认URL路径：`/health` 而不是 `/health/`

### 问题2：API返回500错误

**原因：** Agent初始化失败

**解决：**
1. 检查Render日志
2. 确认环境变量已正确配置
3. 确认 `config/agent_llm_config.json` 文件存在

### 问题3：前端无法连接API

**原因：** CORS配置问题或API地址错误

**解决：**
1. 确认Flask应用已启用CORS：`CORS(app)`
2. 确认API地址正确（使用HTTPS）
3. 检查浏览器控制台的CORS错误

### 问题4：首次访问很慢（30秒+）

**原因：** Render免费套餐会休眠，需要唤醒时间

**说明：** 这是正常行为

**解决：**
- 接受首次访问较慢
- 或者升级到付费套餐（$7/月起）

### 问题5：聊天记录丢失

**原因：** Render免费套餐每次重启会清空临时数据

**说明：** 不影响聊天记录

**解决：**
- 聊天记录已保存在飞书表格，不会丢失
- Render重启不影响飞书数据

---

## 📊 性能测试

### 测试响应时间

使用以下命令测试API响应时间：

```bash
time curl -X POST https://你的Render地址.onrender.com/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Test"}'
```

**预期结果：**
- 首次请求：5-30秒（包含唤醒时间）
- 后续请求：2-5秒

### 测试并发请求

使用Apache Bench测试：

```bash
# 安装ab（如果未安装）
# Ubuntu/Debian: sudo apt-get install apache2-utils
# Mac: brew install httpd

# 测试10个并发，总共100个请求
ab -n 100 -c 10 -p test.json -T application/json \
  https://你的Render地址.onrender.com/api/chat
```

创建 `test.json` 文件：
```json
{"message": "Test message"}
```

**预期结果：**
- 免费套餐可能在高并发时响应变慢
- 如果需要高性能，考虑升级套餐

---

## 📈 监控和日志

### 查看Render日志

1. 登录Render
2. 进入项目页面
3. 点击 **Logs** 标签
4. 实时查看应用日志

### 查看性能指标

1. 点击 **Metrics** 标签
2. 查看：
   - CPU使用率
   - 内存使用率
   - 响应时间
   - 请求数量

### 查看飞书聊天记录

1. 登录飞书多维表格
2. 打开聊天记录表格
3. 查看所有对话历史

---

## 🔒 安全检查

### 检查清单

- [ ] API地址使用HTTPS（而非HTTP）
- [ ] 环境变量已正确设置，不在代码中暴露
- [ ] 敏感信息（API密钥）已正确配置
- [ ] CORS配置只允许必要的域名
- [ ] 速率限制已启用（可选）

---

## ✅ 最终验证

### 完整功能测试流程

1. **后端测试**
   ```bash
   # 健康检查
   curl https://你的Render地址.onrender.com/health
   
   # 聊天测试
   curl -X POST https://你的Render地址.onrender.com/api/chat \
     -H "Content-Type: application/json" \
     -d '{"message":"Test"}'
   ```

2. **前端测试**
   - 访问网站
   - 点击聊天按钮
   - 发送消息
   - 验证回复

3. **跨设备测试**
   - 电脑浏览器测试
   - 手机浏览器测试
   - 平板浏览器测试

4. **数据验证**
   - 检查飞书表格是否保存了聊天记录
   - 验证会话ID是否一致

---

## 🎉 部署成功标志

如果你完成了以上所有测试并且都通过，恭喜你！🎉

**成功标志：**
- ✅ 健康检查通过
- ✅ API可以正常响应
- ✅ 前端聊天功能正常
- ✅ 流式响应工作正常
- ✅ 聊天记录保存到飞书
- ✅ 多设备访问正常

**现在你的网站已经拥有了智能客服功能！**

---

## 📞 需要进一步帮助？

- Render文档：https://render.com/docs
- 查看详细部署教程：`docs/RENDER_DEPLOYMENT.md`
- 查看前端集成教程：`docs/FRONTEND_SETUP.md`
