# Figma 需求提取工具 - 使用指南

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install requests
```

或使用 requirements.txt:

```bash
pip install -r requirements.txt
```

### 2. 获取 Figma Access Token

1. 访问 https://www.figma.com/settings
2. 滚动到 "Personal access tokens" 部分
3. 点击 "Generate new token"
4. 输入 token 名称（如 "Claude Requirements Extraction"）
5. 复制生成的 token（格式类似：`figd_xxxxxxxxxxxxxxxxxxxx`）

⚠️ **注意**: Token 只会显示一次，请妥善保存！

### 3. 运行脚本

**方式1: 使用 Figma 链接**

```bash
python figma_extractor.py "https://www.figma.com/file/AbCd1234EfGh5678/MyDesign" "figd_your_token_here"
```

**方式2: 直接使用 File Key**

```bash
python figma_extractor.py "AbCd1234EfGh5678" "figd_your_token_here"
```

**方式3: 指定输出目录**

```bash
python figma_extractor.py "AbCd1234EfGh5678" "figd_your_token_here" --output-dir ./my_requirements
```

## 📤 输出文件说明

脚本运行后会在输出目录中生成以下文件：

```
figma_output/
├── {文件名}_需求文档.md          # 📄 主要的需求文档（Markdown格式）
├── figma_raw_data.json          # 📊 Figma API 返回的原始JSON数据
└── component_mapping.json       # 📊 组件与接口的映射关系
```

### 主要文档结构

生成的 Markdown 需求文档包含：

1. **文档概览** - 统计信息摘要
2. **功能清单** 
   - 独立开发任务（纯前端）
   - SDK/接口依赖任务
3. **接口依赖详细规格** - 每个接口的完整规格说明
4. **技术实现要点** - 状态管理、数据流建议
5. **联调计划** - 三方对齐 Checklist
6. **风险点和依赖关系** - 阻塞性依赖分析

## 🔍 如何获取 Figma File Key

### 从 Figma 链接中提取

Figma 链接通常是这样的：

```
https://www.figma.com/file/AbCd1234EfGh5678/MyDesignName
                          ^^^^^^^^^^^^^^^^^^^
                          这部分就是 File Key
```

支持的链接格式：
- `https://www.figma.com/file/{FILE_KEY}/{FILE_NAME}`
- `https://www.figma.com/design/{FILE_KEY}/{FILE_NAME}`
- `https://www.figma.com/proto/{FILE_KEY}/{FILE_NAME}`

### 手动提取 File Key

1. 打开 Figma 设计稿
2. 查看浏览器地址栏
3. 复制 `/file/` 或 `/design/` 后面的一长串字符（通常是22位）

## ⚙️ 高级用法

### 1. 自定义输出目录

```bash
python figma_extractor.py <FILE_KEY> <TOKEN> --output-dir ./custom_path
```

### 2. 批量处理多个设计稿

创建一个 bash 脚本：

```bash
#!/bin/bash
TOKEN="figd_your_token_here"

python figma_extractor.py "FileKey1" "$TOKEN" --output-dir ./project1
python figma_extractor.py "FileKey2" "$TOKEN" --output-dir ./project2
python figma_extractor.py "FileKey3" "$TOKEN" --output-dir ./project3
```

### 3. 集成到 CI/CD

```yaml
# .github/workflows/figma-extract.yml
name: Extract Figma Requirements

on:
  workflow_dispatch:
    inputs:
      figma_url:
        description: 'Figma File URL'
        required: true

jobs:
  extract:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: pip install requests
      
      - name: Extract requirements
        env:
          FIGMA_TOKEN: ${{ secrets.FIGMA_TOKEN }}
        run: |
          python figma_extractor.py "${{ github.event.inputs.figma_url }}" "$FIGMA_TOKEN"
      
      - name: Upload artifacts
        uses: actions/upload-artifact@v2
        with:
          name: figma-requirements
          path: figma_output/
```

## 🐛 常见问题

### Q1: 提示 "403 Forbidden" 错误

**原因**: Token 无效或无权限访问文件

**解决方案**:
1. 检查 Token 是否正确复制（无空格、无换行）
2. 确认 Token 未过期
3. 确认您是文件的编辑者或查看者
4. 让设计师将文件设置为"任何拥有链接的人都可以查看"

### Q2: 提示 "404 Not Found" 错误

**原因**: File Key 不正确

**解决方案**:
1. 重新检查 URL 中的 File Key
2. 确认使用的是 `/file/` 或 `/design/` 后面的部分
3. 不要使用 Community 文件的链接（那些不是个人文件）

### Q3: 没有识别到按钮或组件

**原因**: Figma 中的命名不规范

**解决方案**:
1. 在 Figma 中给组件起有意义的名字（如 "开始按钮"、"电量显示"）
2. 使用英文关键词（button, input, list 等）
3. 重新运行脚本

### Q4: 接口规格不准确

**原因**: 自动推断有局限性

**解决方案**:
1. 生成的文档是初稿，需要人工审核
2. 根据实际业务逻辑调整接口参数和返回值
3. 补充具体的业务规则

### Q5: 提取的组件太多/太少

**原因**: 默认提取深度为10层

**解决方案**:
编辑 `figma_extractor.py`，修改 `extract_components` 方法中的 `depth` 限制：

```python
# 第 103 行附近
if depth > 10:  # 改为 15 或其他值
    return
```

## 📝 最佳实践

### 1. Figma 设计规范

为了提高自动识别准确率，建议设计师：

- ✅ 使用有意义的图层命名（如 "开始按钮" 而不是 "Rectangle 1"）
- ✅ 使用 Figma 组件系统（Component）
- ✅ 按功能模块组织图层结构
- ✅ 标注关键交互（使用原型功能）
- ✅ 在文本图层中使用真实文案（避免 Lorem Ipsum）

### 2. 后续人工审核

自动生成的文档需要：

- [ ] 确认所有接口依赖是否识别正确
- [ ] 补充自动推断遗漏的接口
- [ ] 调整接口参数和返回值的具体字段
- [ ] 添加业务逻辑和边界条件说明
- [ ] 与SDK/后端团队对齐确认

### 3. 版本管理

- 每次设计稿更新后重新运行脚本
- 使用 Git 对比前后版本的差异
- 在需求文档中标注版本号和更新日志

## 🔧 扩展开发

### 添加自定义识别规则

编辑 `figma_extractor.py` 的 `_identify_ui_element` 方法：

```python
# 添加自己的关键词
CUSTOM_KEYWORDS = ["特殊组件", "custom"]

if any(kw in name_lower for kw in CUSTOM_KEYWORDS):
    return "CUSTOM_TYPE"
```

### 自定义接口规格模板

编辑 `_infer_api_spec` 方法，添加新的推断逻辑：

```python
# 添加自定义推断
if "特定关键词" in name_lower:
    return APISpec(
        api_name="自定义接口名称",
        # ... 其他字段
    )
```

## 📚 相关资源

- [Figma API 官方文档](https://www.figma.com/developers/api)
- [Figma 设计规范指南](https://www.figma.com/best-practices/)
- [REST API 最佳实践](https://restfulapi.net/)

## 💡 提示

- 首次使用建议先用一个简单的设计稿测试
- Token 只在本次会话使用，不会被存储
- 定期更新 Token（建议每3个月）
- 保持设计稿结构清晰，有助于提高识别准确率

## 📧 反馈与支持

如有问题或建议，欢迎：
- 提交 Issue
- 补充需求场景
- 贡献代码优化

---

**祝您使用愉快！ 🎉**
