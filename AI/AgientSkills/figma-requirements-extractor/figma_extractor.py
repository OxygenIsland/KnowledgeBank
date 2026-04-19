#!/usr/bin/env python3
"""
Figma Design Spec Extractor - Enhanced Version
自动从 Figma API 提取设计稿数据并生成需求文档

使用方法:
    python figma_extractor.py <FILE_KEY> <ACCESS_TOKEN> [--output-dir OUTPUT_DIR]

示例:
    python figma_extractor.py AbCd1234EfGh5678 figd_xxxxxxxxxxxx --output-dir ./requirements
"""

import requests
import json
import sys
import os
import re
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict


@dataclass
class ComponentInfo:
    """组件信息数据类"""
    id: str
    name: str
    type: str
    ui_element_type: Optional[str] = None
    text: Optional[str] = None
    children_count: int = 0
    width: Optional[float] = None
    height: Optional[float] = None
    x: Optional[float] = None
    y: Optional[float] = None


@dataclass
class APISpec:
    """接口规格数据类"""
    api_name: str
    dependency_type: str
    trigger_timing: str
    request_params: List[Dict[str, str]]
    response_data: List[Dict[str, str]]
    priority: str
    acceptance_criteria: List[str]
    related_component: str


class FigmaExtractor:
    """Figma 设计稿提取器"""
    
    # UI 关键词映射
    BUTTON_KEYWORDS = ["button", "btn", "按钮", "操作", "确认", "取消", "提交"]
    INPUT_KEYWORDS = ["input", "textfield", "text field", "输入", "搜索", "search"]
    LIST_KEYWORDS = ["list", "列表", "item", "card", "卡片"]
    STATUS_KEYWORDS = ["status", "state", "状态", "电量", "battery", "speed", "温度", "temperature"]
    CONTROL_KEYWORDS = ["start", "stop", "pause", "control", "开始", "停止", "暂停", "控制", "启动"]
    DATA_KEYWORDS = ["history", "record", "log", "历史", "记录", "日志", "统计", "chart", "graph"]
    
    def __init__(self, access_token: str, file_key: str):
        self.access_token = access_token
        self.file_key = file_key
        self.base_url = "https://api.figma.com/v1"
        self.headers = {"X-Figma-Token": access_token}
        self.components: List[ComponentInfo] = []
        self.api_specs: List[APISpec] = []
    
    def get_file_data(self) -> Dict[str, Any]:
        """获取 Figma 文件完整数据"""
        url = f"{self.base_url}/files/{self.file_key}"
        print(f"🔍 正在获取 Figma 文件数据...")
        
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            print("✅ 文件数据获取成功")
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ 获取文件失败: {e}")
            raise
    
    def extract_components(self, node: Dict[str, Any], depth: int = 0) -> None:
        """递归提取所有组件信息"""
        node_type = node.get("type", "")
        node_name = node.get("name", "")
        node_id = node.get("id", "")
        
        # 跳过过于底层的节点
        if depth > 10:
            return
        
        # 提取边界信息
        bounds = node.get("absoluteBoundingBox", {})
        
        # 创建组件信息
        component = ComponentInfo(
            id=node_id,
            name=node_name,
            type=node_type,
            children_count=len(node.get("children", [])),
            width=bounds.get("width"),
            height=bounds.get("height"),
            x=bounds.get("x"),
            y=bounds.get("y"),
        )
        
        # 提取文本内容
        if node_type == "TEXT":
            component.text = node.get("characters", "")
        
        # 识别 UI 元素类型
        component.ui_element_type = self._identify_ui_element(node)
        
        # 提取按钮文本
        if component.ui_element_type == "BUTTON":
            component.text = self._extract_text_from_node(node)
        
        # 提取输入框占位符
        if component.ui_element_type == "INPUT":
            component.text = self._extract_text_from_node(node)
        
        # 只保存有意义的组件
        if node_type in ["FRAME", "COMPONENT", "INSTANCE", "GROUP", "TEXT"] or component.ui_element_type:
            self.components.append(component)
        
        # 递归处理子节点
        for child in node.get("children", []):
            self.extract_components(child, depth + 1)
    
    def _identify_ui_element(self, node: Dict[str, Any]) -> Optional[str]:
        """识别 UI 元素类型"""
        name_lower = node.get("name", "").lower()
        node_type = node.get("type", "")
        
        # 按钮识别
        if any(kw in name_lower for kw in self.BUTTON_KEYWORDS):
            return "BUTTON"
        
        # 输入框识别
        if any(kw in name_lower for kw in self.INPUT_KEYWORDS):
            return "INPUT"
        
        # 列表识别
        if any(kw in name_lower for kw in self.LIST_KEYWORDS):
            children = node.get("children", [])
            # 列表通常有多个重复子元素
            if len(children) >= 2:
                return "LIST"
        
        # 状态显示识别
        if any(kw in name_lower for kw in self.STATUS_KEYWORDS):
            return "STATUS_DISPLAY"
        
        # 图表识别
        if "chart" in name_lower or "graph" in name_lower or "统计" in name_lower:
            return "CHART"
        
        return None
    
    def _extract_text_from_node(self, node: Dict[str, Any]) -> str:
        """从节点及其子节点中提取文本"""
        texts = []
        
        if node.get("type") == "TEXT":
            texts.append(node.get("characters", ""))
        
        for child in node.get("children", []):
            child_text = self._extract_text_from_node(child)
            if child_text:
                texts.append(child_text)
        
        return " ".join(texts).strip()
    
    def generate_api_specs(self) -> None:
        """根据组件自动生成接口规格"""
        print("🔄 正在分析组件并生成接口规格...")
        
        for component in self.components:
            spec = self._infer_api_spec(component)
            if spec:
                self.api_specs.append(spec)
        
        print(f"✅ 共生成 {len(self.api_specs)} 个接口规格")
    
    def _infer_api_spec(self, component: ComponentInfo) -> Optional[APISpec]:
        """根据组件推断接口规格"""
        name_lower = component.name.lower()
        text_lower = (component.text or "").lower()
        
        # 控制类按钮
        if component.ui_element_type == "BUTTON":
            if any(kw in text_lower or kw in name_lower for kw in self.CONTROL_KEYWORDS):
                return APISpec(
                    api_name=f"控制_{component.text or component.name}",
                    dependency_type="SDK封装 + 底层服务验证",
                    trigger_timing=f"用户点击'{component.text or component.name}'按钮时",
                    request_params=[
                        {"name": "action", "type": "string", "desc": f"{component.text or component.name}动作指令"},
                        {"name": "params", "type": "object", "desc": "可选参数"},
                    ],
                    response_data=[
                        {"name": "status", "type": "string", "desc": "执行状态 success/failed"},
                        {"name": "message", "type": "string", "desc": "结果描述"},
                    ],
                    priority="P0",
                    acceptance_criteria=[
                        "SDK接口调用返回success",
                        f"设备实际执行了{component.text or component.name}动作",
                        "UI状态正确更新"
                    ],
                    related_component=component.name
                )
            
            # 数据提交按钮
            if any(kw in text_lower for kw in ["保存", "提交", "上传", "save", "submit", "upload"]):
                return APISpec(
                    api_name=f"提交_{component.text or component.name}",
                    dependency_type="后端API",
                    trigger_timing=f"用户点击'{component.text or component.name}'按钮时",
                    request_params=[
                        {"name": "data", "type": "object", "desc": "提交的数据对象"},
                    ],
                    response_data=[
                        {"name": "status", "type": "string", "desc": "提交状态"},
                        {"name": "id", "type": "string", "desc": "生成的记录ID"},
                    ],
                    priority="P1",
                    acceptance_criteria=[
                        "数据成功保存到后端",
                        "返回有效的记录ID",
                        "UI显示成功提示"
                    ],
                    related_component=component.name
                )
        
        # 状态显示组件
        if component.ui_element_type == "STATUS_DISPLAY":
            if "电量" in name_lower or "battery" in name_lower:
                return APISpec(
                    api_name="查询电池电量",
                    dependency_type="SDK封装",
                    trigger_timing="页面加载时 / 定时轮询（建议间隔5秒）",
                    request_params=[],
                    response_data=[
                        {"name": "level", "type": "int", "desc": "电量百分比 0-100"},
                        {"name": "charging", "type": "boolean", "desc": "是否正在充电"},
                        {"name": "voltage", "type": "float", "desc": "电压（可选）"},
                    ],
                    priority="P1",
                    acceptance_criteria=[
                        "电量显示与实际设备电量一致（误差<5%）",
                        "充电状态正确显示",
                        "数据更新及时"
                    ],
                    related_component=component.name
                )
            
            if "速度" in name_lower or "speed" in name_lower:
                return APISpec(
                    api_name="查询当前速度",
                    dependency_type="SDK封装",
                    trigger_timing="实时查询或轮询（建议间隔1秒）",
                    request_params=[],
                    response_data=[
                        {"name": "speed", "type": "float", "desc": "当前速度值"},
                        {"name": "unit", "type": "string", "desc": "速度单位（m/s, km/h等）"},
                    ],
                    priority="P1",
                    acceptance_criteria=[
                        "速度显示与实际设备速度一致",
                        "更新频率满足实时性要求"
                    ],
                    related_component=component.name
                )
        
        # 列表组件
        if component.ui_element_type == "LIST":
            if any(kw in name_lower for kw in self.DATA_KEYWORDS):
                return APISpec(
                    api_name=f"查询_{component.name}_列表",
                    dependency_type="后端API",
                    trigger_timing="页面加载时 / 下拉刷新时",
                    request_params=[
                        {"name": "page", "type": "int", "desc": "页码（支持分页）"},
                        {"name": "page_size", "type": "int", "desc": "每页条数"},
                        {"name": "filters", "type": "object", "desc": "筛选条件（可选）"},
                    ],
                    response_data=[
                        {"name": "items", "type": "array", "desc": "数据列表"},
                        {"name": "total", "type": "int", "desc": "总条数"},
                        {"name": "has_more", "type": "boolean", "desc": "是否有更多数据"},
                    ],
                    priority="P2",
                    acceptance_criteria=[
                        "列表数据正确显示",
                        "分页功能正常",
                        "空状态正确处理"
                    ],
                    related_component=component.name
                )
        
        # 图表组件
        if component.ui_element_type == "CHART":
            return APISpec(
                api_name=f"获取_{component.name}_数据",
                dependency_type="后端API",
                trigger_timing="页面加载时 / 切换时间范围时",
                request_params=[
                    {"name": "start_time", "type": "string", "desc": "开始时间"},
                    {"name": "end_time", "type": "string", "desc": "结束时间"},
                    {"name": "granularity", "type": "string", "desc": "数据粒度（hour/day/week）"},
                ],
                response_data=[
                    {"name": "data_points", "type": "array", "desc": "数据点列表"},
                    {"name": "labels", "type": "array", "desc": "标签列表"},
                ],
                priority="P2",
                acceptance_criteria=[
                    "图表正确渲染数据",
                    "数据点与时间轴对应正确",
                    "支持时间范围切换"
                ],
                related_component=component.name
            )
        
        return None
    
    def classify_components(self) -> Dict[str, List[ComponentInfo]]:
        """将组件分类为前端任务、SDK依赖、底层服务依赖"""
        classification = {
            "frontend_only": [],
            "sdk_dependency": [],
            "service_dependency": [],
        }
        
        for component in self.components:
            # 纯UI组件
            if component.type in ["FRAME", "GROUP"] and not component.ui_element_type:
                classification["frontend_only"].append(component)
            
            # 简单交互按钮（不涉及数据）
            elif component.ui_element_type == "BUTTON":
                text_lower = (component.text or "").lower()
                if any(kw in text_lower for kw in ["切换", "选择", "tab", "switch"]):
                    classification["frontend_only"].append(component)
                else:
                    classification["sdk_dependency"].append(component)
            
            # 需要数据的组件
            elif component.ui_element_type in ["STATUS_DISPLAY", "LIST", "CHART"]:
                classification["sdk_dependency"].append(component)
            
            # 输入框（可能需要验证接口）
            elif component.ui_element_type == "INPUT":
                classification["frontend_only"].append(component)
        
        return classification
    
    def generate_markdown_report(self, file_data: Dict, output_path: str) -> None:
        """生成 Markdown 格式的需求文档"""
        print("📝 正在生成 Markdown 需求文档...")
        
        file_name = file_data.get("name", "未命名")
        last_modified = file_data.get("lastModified", "")
        
        # 分类组件
        classification = self.classify_components()
        
        # 构建 Markdown 内容
        md_content = f"""# {file_name} - 需求文档

> 📅 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
> 🔗 Figma 文件: `{self.file_key}`  
> 📝 最后修改: {last_modified}

---

## 📊 文档概览

- **总组件数**: {len(self.components)}
- **识别的接口依赖**: {len(self.api_specs)}
- **纯前端任务**: {len(classification['frontend_only'])}
- **SDK/后端依赖**: {len(classification['sdk_dependency'])}

---

## 1️⃣ 功能清单

### 1.1 独立开发任务（纯前端实现）

以下功能可以完全由前端独立完成，无需等待后端/SDK接口：

"""
        
        # 纯前端任务
        if classification["frontend_only"]:
            for comp in classification["frontend_only"]:
                md_content += f"- [ ] **{comp.name}** - {comp.type}"
                if comp.ui_element_type:
                    md_content += f" ({comp.ui_element_type})"
                if comp.text:
                    md_content += f" - \"{comp.text}\""
                md_content += "\n"
        else:
            md_content += "_暂无纯前端任务_\n"
        
        md_content += "\n### 1.2 SDK/接口依赖任务\n\n以下功能需要调用SDK或后端接口：\n\n"
        
        # SDK依赖任务
        if classification["sdk_dependency"]:
            for comp in classification["sdk_dependency"]:
                md_content += f"- [ ] **{comp.name}**"
                if comp.ui_element_type:
                    md_content += f" ({comp.ui_element_type})"
                if comp.text:
                    md_content += f" - \"{comp.text}\""
                md_content += "\n"
        else:
            md_content += "_暂无SDK依赖任务_\n"
        
        md_content += "\n---\n\n## 2️⃣ 接口依赖详细规格\n\n"
        
        # 按优先级排序接口
        sorted_specs = sorted(self.api_specs, key=lambda x: x.priority)
        
        for idx, spec in enumerate(sorted_specs, 1):
            priority_emoji = {"P0": "🔴", "P1": "🟡", "P2": "🟢"}.get(spec.priority, "⚪")
            
            md_content += f"### {idx}. {spec.api_name} {priority_emoji}\n\n"
            md_content += f"**依赖类型**: {spec.dependency_type}  \n"
            md_content += f"**调用时机**: {spec.trigger_timing}  \n"
            md_content += f"**关联组件**: `{spec.related_component}`  \n\n"
            
            md_content += "**请求参数**:\n\n"
            if spec.request_params:
                md_content += "| 参数名 | 类型 | 说明 |\n"
                md_content += "|--------|------|------|\n"
                for param in spec.request_params:
                    md_content += f"| `{param['name']}` | {param['type']} | {param['desc']} |\n"
            else:
                md_content += "_无参数_\n"
            
            md_content += "\n**返回数据**:\n\n"
            md_content += "| 字段名 | 类型 | 说明 |\n"
            md_content += "|--------|------|------|\n"
            for field in spec.response_data:
                md_content += f"| `{field['name']}` | {field['type']} | {field['desc']} |\n"
            
            md_content += "\n**验收标准**:\n\n"
            for criterion in spec.acceptance_criteria:
                md_content += f"- [ ] {criterion}\n"
            
            md_content += f"\n**优先级**: {spec.priority}\n\n"
            md_content += "---\n\n"
        
        # 添加技术实现要点
        md_content += """## 3️⃣ 技术实现要点

### 状态管理建议

- **全局状态**: 使用 Redux/MobX/Provider 管理跨页面共享的状态（如用户信息、设备连接状态）
- **本地状态**: 使用组件内部 state 管理页面级别的UI状态
- **数据缓存**: 对频繁查询的数据（如电量、速度）考虑实现本地缓存机制

### 数据流设计

```
用户操作 → UI事件 → Action → SDK/API调用 → 响应处理 → State更新 → UI刷新
```

### 错误处理

- **网络异常**: 显示友好的错误提示，提供重试按钮
- **超时处理**: 设置合理的超时时间（建议5-10秒）
- **降级方案**: 关键功能失败时的备用方案

---

## 4️⃣ 联调计划

### 三方对齐会议 Checklist

在开发前，需要与SDK团队/后端团队确认：

- [ ] 所有接口的请求/响应格式已确认
- [ ] 接口的调用频率和性能要求已明确
- [ ] 错误码和异常处理机制已定义
- [ ] 测试环境已就绪
- [ ] Mock数据已准备（用于前端独立开发）

### 分阶段验证策略

1. **阶段1**: 使用Mock数据完成UI开发和本地交互
2. **阶段2**: 集成SDK，验证接口调用流程
3. **阶段3**: 端到端测试，验证设备实际执行效果
4. **阶段4**: 性能优化和异常场景测试

---

## 5️⃣ 风险点和依赖关系

### 阻塞性依赖 🔴

"""
        
        # 列出P0接口
        p0_specs = [s for s in self.api_specs if s.priority == "P0"]
        if p0_specs:
            for spec in p0_specs:
                md_content += f"- **{spec.api_name}**: 核心功能依赖，缺失将导致功能无法演示\n"
        else:
            md_content += "_暂无阻塞性依赖_\n"
        
        md_content += "\n### 建议联调顺序\n\n"
        md_content += "1. 优先对接 P0 级别接口，确保核心流程打通\n"
        md_content += "2. 其次对接 P1 级别接口，完善用户体验\n"
        md_content += "3. 最后对接 P2 级别接口，锦上添花\n"
        
        md_content += "\n---\n\n## 📎 附录\n\n"
        md_content += f"### 组件统计\n\n"
        md_content += f"- Frame: {sum(1 for c in self.components if c.type == 'FRAME')}\n"
        md_content += f"- Component: {sum(1 for c in self.components if c.type == 'COMPONENT')}\n"
        md_content += f"- Instance: {sum(1 for c in self.components if c.type == 'INSTANCE')}\n"
        md_content += f"- Text: {sum(1 for c in self.components if c.type == 'TEXT')}\n"
        md_content += f"- Button: {sum(1 for c in self.components if c.ui_element_type == 'BUTTON')}\n"
        md_content += f"- Input: {sum(1 for c in self.components if c.ui_element_type == 'INPUT')}\n"
        md_content += f"- List: {sum(1 for c in self.components if c.ui_element_type == 'LIST')}\n"
        
        # 写入文件
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(md_content)
        
        print(f"✅ Markdown 文档已生成: {output_path}")
    
    def save_raw_data(self, file_data: Dict, output_path: str) -> None:
        """保存原始 JSON 数据"""
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(file_data, f, indent=2, ensure_ascii=False)
        print(f"✅ 原始数据已保存: {output_path}")
    
    def save_component_mapping(self, output_path: str) -> None:
        """保存组件-接口映射关系"""
        mapping = {
            "components": [asdict(c) for c in self.components],
            "api_specs": [asdict(s) for s in self.api_specs],
        }
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(mapping, f, indent=2, ensure_ascii=False)
        print(f"✅ 组件映射已保存: {output_path}")
    
    def run(self, output_dir: str = "./figma_output") -> None:
        """执行完整的提取流程"""
        print("=" * 60)
        print("🚀 Figma 设计稿需求提取工具")
        print("=" * 60)
        
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        # 获取文件数据
        file_data = self.get_file_data()
        file_name = file_data.get("name", "未命名").replace(" ", "_")
        
        # 提取组件
        print("🔍 正在解析组件结构...")
        for page in file_data.get("document", {}).get("children", []):
            self.extract_components(page)
        print(f"✅ 共提取 {len(self.components)} 个组件")
        
        # 生成接口规格
        self.generate_api_specs()
        
        # 生成报告
        md_path = os.path.join(output_dir, f"{file_name}_需求文档.md")
        self.generate_markdown_report(file_data, md_path)
        
        # 保存原始数据
        json_path = os.path.join(output_dir, "figma_raw_data.json")
        self.save_raw_data(file_data, json_path)
        
        # 保存组件映射
        mapping_path = os.path.join(output_dir, "component_mapping.json")
        self.save_component_mapping(mapping_path)
        
        print("\n" + "=" * 60)
        print("🎉 提取完成！生成的文件：")
        print(f"  📄 {md_path}")
        print(f"  📊 {json_path}")
        print(f"  📊 {mapping_path}")
        print("=" * 60)


def extract_file_key_from_url(url: str) -> Optional[str]:
    """从 Figma URL 中提取 File Key"""
    patterns = [
        r"figma\.com/file/([a-zA-Z0-9]+)",
        r"figma\.com/design/([a-zA-Z0-9]+)",
        r"figma\.com/proto/([a-zA-Z0-9]+)",
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return None


def main():
    """主函数"""
    if len(sys.argv) < 3:
        print("用法:")
        print("  方式1: python figma_extractor.py <FILE_KEY> <ACCESS_TOKEN> [--output-dir OUTPUT_DIR]")
        print("  方式2: python figma_extractor.py <FIGMA_URL> <ACCESS_TOKEN> [--output-dir OUTPUT_DIR]")
        print("\n示例:")
        print("  python figma_extractor.py AbCd1234EfGh5678 figd_xxxxxxxxxxxx")
        print("  python figma_extractor.py https://www.figma.com/file/AbCd1234/MyDesign figd_xxxxxxxxxxxx")
        sys.exit(1)
    
    file_key_or_url = sys.argv[1]
    access_token = sys.argv[2]
    output_dir = "./figma_output"
    
    # 解析可选参数
    if "--output-dir" in sys.argv:
        idx = sys.argv.index("--output-dir")
        if idx + 1 < len(sys.argv):
            output_dir = sys.argv[idx + 1]
    
    # 提取 File Key
    if file_key_or_url.startswith("http"):
        file_key = extract_file_key_from_url(file_key_or_url)
        if not file_key:
            print("❌ 无法从 URL 中提取 File Key")
            print("请确认 URL 格式: https://www.figma.com/file/{FILE_KEY}/...")
            sys.exit(1)
        print(f"✅ 从 URL 中提取到 File Key: {file_key}")
    else:
        file_key = file_key_or_url
    
    # 执行提取
    try:
        extractor = FigmaExtractor(access_token, file_key)
        extractor.run(output_dir)
    except Exception as e:
        print(f"\n❌ 提取失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
