# 流式输出速度控制指南

## 问题说明

在测试环境（test_run）中，Agent的回复会快速显示，可能看起来像机器人的即时输出。这是因为流式输出速度由框架和API决定，测试环境默认快速显示。

## 解决方案

在实际部署时，可以通过以下方式控制流式输出速度，模拟真人打字效果：

### 方案1: 前端JavaScript控制（推荐）

在前端聊天界面中，使用JavaScript延迟显示每个字符或token：

```javascript
// 示例：模拟真人打字速度
function simulateTyping(element, text, speed) {
  let index = 0;
  element.textContent = '';

  function type() {
    if (index < text.length) {
      // 根据字符类型调整速度
      const char = text[index];
      let delay = speed;

      // 标点符号后停顿更长
      if (['.', '!', '?', '。', '！', '？'].includes(char)) {
        delay = speed * 3;  // 标点后停顿3倍时间
      }
      // 逗号后短暂停顿
      else if ([';', ',', '，', '；'].includes(char)) {
        delay = speed * 1.5;
      }
      // 空格后短暂停顿
      else if (char === ' ') {
        delay = speed * 0.5;
      }

      element.textContent += char;
      index++;
      setTimeout(type, delay);
    }
  }

  type();
}

// 使用示例
// speed: 每个字符的显示时间（毫秒）
// 50-100ms 模拟正常打字速度
// 30-50ms 模拟快速打字
// 100-150ms 模拟慢速打字
simulateTyping(chatElement, aiResponse, 70);
```

### 方案2: 后端流式控制

在后端的流式处理逻辑中添加延迟：

```python
# 在 src/main.py 或流式处理逻辑中
import asyncio
import re

async def slow_stream(content, chat_element):
    """慢速流式输出"""
    words = re.split(r'(\s+)', content)  # 保留空格

    for word in words:
        if word.strip():  # 非空格词
            # 根据词长调整速度
            delay = min(len(word) * 10, 100)  # 每个字符10ms，最多100ms
            await asyncio.sleep(delay / 1000)  # 转换为秒

        # 标点符号后额外停顿
        if word and word[-1] in ['.', '!', '?', '。', '！', '？']:
            await asyncio.sleep(0.2)  # 停顿200ms
```

### 方案3: 智能速度控制

根据回复长度和内容调整速度：

```javascript
function smartTypingSpeed(text) {
  const wordCount = text.split(/\s+/).length;
  const charCount = text.length;

  // 短回复（<50字符）：较快
  if (charCount < 50) {
    return 40;  // 40ms per char
  }
  // 中等回复（50-150字符）：正常速度
  else if (charCount < 150) {
    return 60;  // 60ms per char
  }
  // 长回复（150+字符）：较慢
  else {
    return 80;  // 80ms per char
  }
}

// 使用
const speed = smartTypingSpeed(aiResponse);
simulateTyping(chatElement, aiResponse, speed);
```

## 当前优化（已实现）

虽然无法直接控制test_run中的流式速度，但我们已经在系统提示词中优化了文本结构，让回复即使快速显示也显得自然：

✅ **已实现的优化**：
1. 使用短句而非长段落
2. 使用换行符创建自然停顿
3. 使用emoji作为视觉分隔
4. 使用口语化表达
5. 每个想法独立成段
6. 添加自然对话标记

这些优化使得即使回复快速显示，也不会显得过于机器人化。

## 推荐配置

**正常打字速度**：50-80ms per character
- 模拟正常人的打字速度
- 适合大多数场景

**快速打字**：30-50ms per character
- 模拟熟练打字员
- 适合简短回复

**慢速打字**：80-120ms per character
- 模拟思考中的打字
- 适合复杂或长回复

## 注意事项

⚠️ **重要提示**：
1. 延迟不要过长，否则客户会感到不耐烦
2. 标点符号后的停顿要明显但不夸张
3. 保持一致性，不要忽快忽慢
4. 考虑网络延迟，总延迟 = 打字模拟 + 网络传输

## 测试建议

在部署前，测试不同速度设置的效果：
- 邀请真实用户测试
- 收集关于"自然度"的反馈
- 调整速度参数找到最佳平衡点
