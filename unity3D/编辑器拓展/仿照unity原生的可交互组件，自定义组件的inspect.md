---
title: "[[仿照unity原生的可交互组件，自定义组件的inspect]]"
type: Permanent
status: done
Creation Date: 2025-03-19 11:10
tags:
---
前因后果详见[[交互组件切换颜色方式的拓展]]，这里不在赘述
下面对SelectableItem组件的Inspect面板进行定制化显示，并且实现自动获取组件并赋值的功能
```csharp
using TMPro;
using UnityEditor;
using UnityEngine;
using UnityEngine.UI;

[CustomEditor(typeof(SelectableItem))]
public class SelectableItemEditor : Editor
{
    private SerializedProperty m_Target => serializedObject.FindProperty("m_Target");
    private SerializedProperty borderImage => serializedObject.FindProperty("borderImage");
    private SerializedProperty buttonText => serializedObject.FindProperty("buttonText");
    private SerializedProperty m_ColorBlock => serializedObject.FindProperty("m_itemColor");

    private void OnEnable()
    {

    }
    public override void OnInspectorGUI()
    {
        serializedObject.Update();

        // 显示 Target 类型选择
        EditorGUILayout.PropertyField(m_Target);

        // 根据 Target 类型显示对应组件字段
        var targetType = (SelectableItem.Target)m_Target.enumValueIndex;
        switch (targetType)
        {
            case SelectableItem.Target.Image:
                EditorGUILayout.PropertyField(borderImage, new GUIContent("Border Image"));
                TryAutoAssignComponent<Image>(borderImage, "Image");
                break;
            case SelectableItem.Target.Text:
                EditorGUILayout.PropertyField(buttonText, new GUIContent("Button Text"));
                TryAutoAssignComponent<TMP_Text>(buttonText, "TextMeshPro");
                break;
        }

        EditorGUILayout.LabelField("Color Settings", EditorStyles.boldLabel);
        EditorGUI.indentLevel++;
        DrawColorBlockProperties();
        EditorGUI.indentLevel--;

        // 应用修改
        serializedObject.ApplyModifiedProperties();
    }

    void DrawColorBlockProperties()
    {
        EditorGUILayout.PropertyField(m_ColorBlock.FindPropertyRelative("m_NormalColor"));
        EditorGUILayout.PropertyField(m_ColorBlock.FindPropertyRelative("m_HighlightedColor"));
        EditorGUILayout.PropertyField(m_ColorBlock.FindPropertyRelative("m_PressedColor"));
        EditorGUILayout.PropertyField(m_ColorBlock.FindPropertyRelative("m_SelectedColor"));
        EditorGUILayout.PropertyField(m_ColorBlock.FindPropertyRelative("m_DisabledColor"));

        // 高级设置
        EditorGUILayout.PropertyField(m_ColorBlock.FindPropertyRelative("m_ColorMultiplier"));
        EditorGUILayout.PropertyField(m_ColorBlock.FindPropertyRelative("m_FadeDuration"));
    }
    /// <summary>
    /// 尝试自动获取组件（如果字段为空）
    /// </summary>
    private void TryAutoAssignComponent<T>(SerializedProperty property, string componentName) where T : Component
    {
        if (property.objectReferenceValue == null)
        {
            var component = ((SelectableItem)target).GetComponent<T>();
            if (component != null)
            {
                property.objectReferenceValue = component;
                serializedObject.ApplyModifiedProperties();
                EditorUtility.SetDirty(target);
            }
            else
            {
                EditorGUILayout.HelpBox($"No {componentName} component found on this GameObject.", MessageType.Warning);
            }
        }
    }
}

```
`SerializedObject` 是 UnityEditor 中的核心类，本质是 ​**序列化数据的代理容器**。它的主要职责是：
1. ​**统一管理** 多个对象的序列化数据
2. ​**安全访问** 通过 `SerializedProperty` 系统
3. ​**自动处理** 撤销/重做（Undo）和多对象编辑
从代码中的注释可以看到，A SerializedObject representing the object or objects being inspected.

所以我们通过serializedObject从序列化对象中查找指定名称的字段对应的 `SerializedProperty`，例如
```csharp
private SerializedProperty m_Target => serializedObject.FindProperty("m_Target");
private SerializedProperty m_ColorBlock => serializedObject.FindProperty("m_itemColor");
```
然后我们可以将SerializedProperty显示出来
```csharp
EditorGUILayout.PropertyField(borderImage, new GUIContent("Border Image"));
```
 `new GUIContent("Border Image")`用于自定义字段在 UI 中显示的标签文本。`GUIContent` 还可以包含工具提示和图标：
```csharp
  new GUIContent("Border Image", "The image used as the border of the selectable item.")
```
我们还可以将SerializedProperty对象中相关的属性也显示出来
```csharp
EditorGUILayout.PropertyField(m_ColorBlock.FindPropertyRelative("m_NormalColor"));
```

自动获取组件并赋值，先通过Editor中的target（The object being inspected）来查找对应的组件
```csharp
var component = ((SelectableItem)target).GetComponent<T>();
```

如果组件不为空，则进行赋值
```csharp
if (component != null)
{
    property.objectReferenceValue = component;
    serializedObject.ApplyModifiedProperties();
    //标记目标对象为“已修改”，确保修改被保存
    EditorUtility.SetDirty(target);
}
```