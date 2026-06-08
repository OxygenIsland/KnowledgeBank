# Hello World Skill 测试技能

## 重要发现

经过调查，GitHub Copilot Chat (v0.36.2) 中的 MCP 服务器需要通过 **VS Code 扩展**的方式注册，而不是直接在 `settings.json` 中配置。

## 配置方式说明

### ❌ 不支持的方式
直接在 `settings.json` 中配置（已移除）：
```json
{
  "github.copilot.chat.mcpServers": {
    "hello-world": { ... }
  }
}
```

### ✅ 正确的方式
需要创建一个 VS Code 扩展，通过 `mcpServerDefinitionProviders` 贡献点注册 MCP 服务器。

## 当前状态

- ✅ MCP 服务器脚本已创建并可正常运行（hello-world-skill.js）
- ✅ 技能文件已保存在 Obsidian 知识库中
- ⏳ 需要创建 VS Code 扩展来注册服务器（未来工作）

## 功能说明

MCP 服务器实现了两个功能：

1. **sayHello** - 向指定的人打招呼
   - 参数：`name` (字符串) - 要打招呼的人的名字

2. **getCurrentTime** - 获取当前时间
   - 无参数

## 直接测试

可以在终端中直接测试脚本：

```powershell
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}' | & "D:\Program Files\nodejs\node.exe" "D:\LB\KnowledgeBank\AgentSkills\custom-skills\hello-world-skill.js"
```

## 下一步

要在 GitHub Copilot 中使用这个技能，需要：

1. 创建一个简单的 VS Code 扩展
2. 在扩展的 package.json 中声明 `mcpServerDefinitionProviders`
3. 实现扩展代码来注册 MCP 服务器
4. 安装并激活扩展

或者等待 GitHub Copilot 未来版本直接支持通过配置文件注册自定义 MCP 服务器。

## 技术说明

- 使用 Node.js 实现
- 遵循 MCP (Model Context Protocol) 协议
- JSON-RPC 2.0 消息格式
- 通过标准输入/输出进行通信
- 脚本本身完全符合 MCP 规范，可以直接使用
