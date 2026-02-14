# 📖 Render部署方案 - 总览

## 🎯 方案概述

这是一个为 **www.paperbagglue.com** 设计的完全免费的云端部署方案。

### 核心特点
- ✅ **完全免费** - 使用Render免费套餐
- ✅ **无需服务器** - 无需购买VPS或云服务器
- ✅ **无需编程** - 简单上传文件即可
- ✅ **自动部署** - 代码更新后自动重新部署
- ✅ **全球访问** - 通过CDN加速
- ✅ **数据安全** - 聊天记录保存在飞书

---

## 📦 包含的文件

### 部署配置
- `render.yaml` - Render自动部署配置

### 前端文件
- `src/web/chat-widget.js` - 嵌入式聊天小部件
- `src/web/chat-widget.html` - 完整聊天页面
- `src/web/example-website.html` - 示例网站

### 文档
- `docs/DEPLOYMENT_CHECKLIST.md` - ⭐ 快速检查清单（从这里开始！）
- `docs/RENDER_DEPLOYMENT.md` - 详细部署教程
- `docs/FRONTEND_SETUP.md` - 前端集成教程
- `docs/TESTING_GUIDE.md` - 测试验证指南
- `docs/WEBSITE_INTEGRATION.md` - 完整集成指南
- `docs/QUICK_START.md` - 快速开始指南

---

## 🚀 5分钟快速开始

### 第1步：准备（2分钟）
1. 准备项目文件
2. 上传到GitHub
3. 注册Render账号

### 第2步：部署（2分钟）
1. 连接GitHub到Render
2. 选择仓库并配置
3. 添加环境变量
4. 等待部署完成

### 第3步：集成（1分钟）
1. 上传chat-widget.js到网站
2. 添加嵌入代码
3. 测试功能

**详细步骤请查看：`docs/DEPLOYMENT_CHECKLIST.md`**

---

## 📋 部署流程图

```
开始
  ↓
准备项目文件
  ↓
上传到GitHub
  ↓
注册Render账号
  ↓
连接GitHub到Render
  ↓
配置服务（添加环境变量）
  ↓
部署到Render
  ↓
测试后端API
  ↓
上传前端文件到网站
  ↓
添加嵌入代码
  ↓
测试聊天功能
  ↓
完成！✅
```

---

## 🔑 需要的环境变量

部署到Render时，需要配置以下环境变量：

| 变量名 | 说明 | 获取方式 |
|-------|------|---------|
| `COZE_WORKLOAD_IDENTITY_API_KEY` | API密钥 | 从开发环境获取 |
| `COZE_INTEGRATION_MODEL_BASE_URL` | 模型API地址 | 从开发环境获取 |
| `COZE_WORKSPACE_PATH` | 工作目录 | 固定值：`/opt/render/project/src` |

---

## 📚 文档导航

### 新手推荐路径
1. **快速开始**: 先看 `docs/DEPLOYMENT_CHECKLIST.md` ⭐
2. **部署教程**: 详细步骤看 `docs/RENDER_DEPLOYMENT.md`
3. **前端集成**: 看不懂前端？看 `docs/FRONTEND_SETUP.md`
4. **测试验证**: 部署完成？看 `docs/TESTING_GUIDE.md`

### 按角色查看

#### 如果你只有网站后台权限
→ 直接看 `docs/FRONTEND_SETUP.md`（前端集成部分）

#### 如果你会使用GitHub
→ 看 `docs/RENDER_DEPLOYMENT.md`（完整部署教程）

#### 如果你想了解技术细节
→ 看 `docs/WEBSITE_INTEGRATION.md`（完整技术文档）

---

## 🎯 三种集成方式

### 方式1：嵌入式小部件（推荐）
- 浮动按钮设计
- 不占用页面空间
- 适合所有网站

**文件**: `src/web/chat-widget.js`

**使用**: 参考文档 `docs/FRONTEND_SETUP.md`

### 方式2：完整聊天页面
- 独立的聊天页面
- 适合专业客服场景

**文件**: `src/web/chat-widget.html`

**使用**: 链接到 `/chat.html`

### 方式3：嵌入式iframe
- 将聊天嵌入现有页面
- 完全自定义布局

**使用**: 参考文档 `docs/WEBSITE_INTEGRATION.md`

---

## 💰 成本说明

### Render免费套餐
- ✅ 每月750小时运行时间
- ✅ 512MB内存
- ✅ 0.1CPU
- ✅ 100GB出站流量
- ❌ 15分钟后无访问会休眠

### 升级到付费套餐（可选）
- Starter: $7/月（更多CPU和内存）
- Standard: $25/月（适合高流量）
- Pro: $100/月（企业级）

**注意**: 免费套餐已经足够应对一般使用场景

---

## 🔧 常见问题速查

### Q: 部署需要多少钱？
A: 完全免费！Render免费套餐足够使用。

### Q: 我需要会编程吗？
A: 不需要！只需按照教程上传文件即可。

### Q: 需要多长时间？
A: 首次部署约10分钟，更新后自动部署约2分钟。

### Q: 首次访问很慢？
A: 正常现象。免费套餐会休眠，首次访问需要唤醒（约30秒）。

### Q: 聊天记录会丢失吗？
A: 不会！所有聊天记录保存在飞书表格，不会丢失。

### Q: 如何更新代码？
A: 推送到GitHub，Render自动重新部署。

### Q: 支持移动端吗？
A: 支持！完全响应式设计。

---

## 📞 技术支持

### 文档资源
- Render官方文档：https://render.com/docs
- GitHub文档：https://docs.github.com

### 获取帮助
1. 查看文档中的"常见问题"部分
2. 检查Render日志
3. 检查浏览器控制台错误

---

## 🎉 部署成功后的样子

部署成功后，你的网站 www.paperbagglue.com 会有：

✅ 右下角显示紫色聊天按钮
✅ 点击按钮打开聊天窗口
✅ AI智能回复客户问题
✅ 流式打字效果
✅ 自动保存聊天记录到飞书
✅ 支持电脑和手机访问

---

## 📝 更新日志

### v1.0.0 (2024-02-14)
- 初始版本发布
- 支持Render免费部署
- 提供完整文档
- 支持流式响应
- 集成飞书聊天记录

---

## 🚀 下一步

**开始部署吧！**

1. 打开 `docs/DEPLOYMENT_CHECKLIST.md` ⭐
2. 按照步骤操作
3. 完成！

有任何问题，随时查看详细文档或提问。

祝你部署顺利！🎉
