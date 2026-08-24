这个目录用来存放自用的 Agent Skills，跨设备同步使用。

当前收录：

- [`video-note-summary/`](./video-note-summary/) — 读取视频字幕文件或 B 站视频链接，总结生成结构化学习笔记

## 路径占位符

为了在不同电脑上都能用，skill 文件里凡涉及本地绝对路径，都写成 `{{...}}` 占位符形式，例如：

- `{{KNOWLEDGE_BANK}}` — 你的知识库根目录（默认是 `~/Documents/KnowledgeBank`）

启用 skill 时，只需在脑子里 / 提示里替换成你电脑上的实际路径即可。

## 在新电脑上使用

手动安装步骤：

1. 把想要用的 skill 目录（例如 `video-note-summary/`）拷贝到 Cursor 的 skills 目录：

   ```bash
   # macOS / Linux
   cp -R video-note-summary/ ~/.cursor/skills/

   # Windows (PowerShell)
   Copy-Item -Recurse video-note-summary/ $env:USERPROFILE\.cursor\skills\
   ```

2. 在 agent 中输入触发场景（例如 "帮我总结这个视频字幕"，或粘贴一个 B 站链接），skill 会被自动加载。

3. 第一次使用时，把 skill 文件里出现的 `{{KNOWLEDGE_BANK}}` 替换成你电脑上知识库的实际路径（例如 `/Users/yourname/Documents/KnowledgeBank`）。

## 更新

skill 文件改动后，把仓库里的新版本同步到本地 skills 目录即可：

```bash
cp -R video-note-summary/ ~/.cursor/skills/
```
