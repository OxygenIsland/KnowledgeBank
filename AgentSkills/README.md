# Agent Skills

这个目录用于存放 GitHub Copilot 的自定义 Agent Skills（MCP 服务器配置）。

## 配置说明

将此目录配置到 VS Code 中：

1. 打开 VS Code 设置（文件 > 首选项 > 设置）
2. 搜索 "mcp" 或 "GitHub Copilot"
3. 添加此目录路径：`D:\LB\KnowledgeBank\AgentSkills`

## 目录结构

```
AgentSkills/
├── README.md           # 本文件
├── custom-skills/      # 自定义技能配置
└── examples/           # 示例配置
```

## 创建新技能

在 `custom-skills` 目录下创建 JSON 配置文件，例如：

```json
{
  "name": "my-skill",
  "description": "我的自定义技能",
  "capabilities": {
    // 技能配置
  }
}
```

## 注意事项

- 所有配置文件使用 JSON 格式
- 由 Obsidian 统一管理和编辑
- 修改后需要重启 VS Code 或重新加载窗口
