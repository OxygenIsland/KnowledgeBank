---
title: "[[Unity中CSharp脚本进行打包]]"
type: Literature
status: done
Creation Date: 2024-03-29 16:35
tags:
---
```csharp
using System;
using System.IO;
using UnityEditor;
using UnityEditor.Build.Reporting;
using UnityEditor.XR.ARCore;
using UnityEditor.XR.ARKit;
using UnityEngine;

public class ARViewerBuilder
{
    [MenuItem("MultiBuild/Build/ForGlasses")]
    public static void BuildAPKForAndroid()
    {
        Build(BuildTarget.Android);
    }

    [MenuItem("MultiBuild/Build/ForPad")]
    public static void BuildForPad()
    {
        Build(BuildTarget.iOS);
    }

    [MenuItem("MultiBuild/Build/ForWebGL")]
    public static void BuildForWebGL()
    {
        Build(BuildTarget.WebGL);
    }

    private static void Build(BuildTarget buildTarget)
    {
        Debug.Log("********Build package begin*******");
        BuildTargetGroup buildGroup = BuildTargetGroup.Android;
        string scene = "";
        switch (buildTarget)
        {
            case BuildTarget.iOS:
                scene = "Assets/Scene/stARview_Phone.unity";
                buildGroup = BuildTargetGroup.iOS;
                break;
            case BuildTarget.StandaloneWindows:
                scene = "Assets/Scene/stARview_Phone.unity";
                buildGroup = BuildTargetGroup.Standalone;
                break;
            case BuildTarget.Android:
                scene = "Assets/Scene/stARview_Glasses.unity";
                buildGroup = BuildTargetGroup.Android;
                break;
            case BuildTarget.WebGL:
                scene = "Assets/Scene/stARview_Wechat.unity";
                buildGroup = BuildTargetGroup.WebGL;
                PlayerSettings.WebGL.memorySize = 2 * 1024;
                PlayerSettings.WebGL.emscriptenArgs = "-s TOTAL_MEMORY=2048MB";
                PlayerSettings.WebGL.emscriptenArgs = "-s ALLOW_MEMORY_GROWTH=1";
                break;
            default:
                break;
        }

        SetXRSettingsByPlatform(buildTarget);
        EditorUserBuildSettings.SwitchActiveBuildTarget(buildGroup, buildTarget);
        string out_put_folder = $"{Application.dataPath}/../Build";
        if (!Directory.Exists(out_put_folder))
        {
            Directory.CreateDirectory(out_put_folder);
        }
        AssetDatabase.Refresh();

        var version = PlayerSettings.bundleVersion;
        string[] version_param = version.Split('.');
        string version_new = string.Format($"{version_param[0]}.{version_param[1]}.{version_param[2][0]}{DateTime.Now.ToString("MM.dd").Replace(".", "")}");
        PlayerSettings.bundleVersion = version_new;
        string output_path = GetOutPutPathByPlatform(out_put_folder, buildTarget);
        Debug.Log("Out put path:" + output_path);
        BuildPlayerOptions buildPlayerOptions = new BuildPlayerOptions();
        string[] scene_path = new string[1] { scene };
        buildPlayerOptions.scenes = scene_path;
        buildPlayerOptions.locationPathName = output_path;
        buildPlayerOptions.targetGroup = buildGroup;
        buildPlayerOptions.target = buildTarget;
        buildPlayerOptions.options = BuildOptions.None;

        BuildReport report = BuildPipeline.BuildPlayer(buildPlayerOptions);
        Debug.Log("********Build package end*******");
        OpenInFolder(out_put_folder);
    }

    private static string GetOutPutPathByPlatform(string folder, BuildTarget buildTarget)
    {
        switch (buildTarget)
        {
            case BuildTarget.Android:
                return $"{folder}/{PlayerSettings.productName}_Glasses_v{PlayerSettings.bundleVersion}.apk";
            case BuildTarget.iOS:
            case BuildTarget.StandaloneWindows:
            default:
                return folder;
        }
    }

    /// <summary>
    /// XR设置
    /// </summary>
    /// <param name="buildTarget"></param>
    private static void SetXRSettingsByPlatform(BuildTarget buildTarget)
    {
        switch (buildTarget)
        {
            case BuildTarget.Android:
	            //查找项目中指定类型（`t:ARCoreSettings`）的资源，并返回它们的GUID（全局唯一标识符）数组。
                string[] guids1 = AssetDatabase.FindAssets("t:ARCoreSettings", null);
                var arcore_setting = AssetDatabase.LoadAssetAtPath<ARCoreSettings>(AssetDatabase.GUIDToAssetPath(guids1[0]));
                arcore_setting.requirement = ARCoreSettings.Requirement.Required;
                guids1 = AssetDatabase.FindAssets("t:ARKitSettings", null);
                var arkit_setting = AssetDatabase.LoadAssetAtPath<ARKitSettings>(AssetDatabase.GUIDToAssetPath(guids1[0]));
                arkit_setting.requirement = ARKitSettings.Requirement.Optional;
                AssetDatabase.Refresh();
                break;
            case BuildTarget.iOS:
                guids1 = AssetDatabase.FindAssets("t:ARCoreSettings", null);
                arcore_setting = AssetDatabase.LoadAssetAtPath<ARCoreSettings>(AssetDatabase.GUIDToAssetPath(guids1[0]));
                arcore_setting.requirement = ARCoreSettings.Requirement.Optional;
                guids1 = AssetDatabase.FindAssets("t:ARKitSettings", null);
                arkit_setting = AssetDatabase.LoadAssetAtPath<ARKitSettings>(AssetDatabase.GUIDToAssetPath(guids1[0]));
                arkit_setting.requirement = ARKitSettings.Requirement.Required;
                AssetDatabase.Refresh();
                break;
            case BuildTarget.StandaloneWindows:
            default:
                break;
        }
    }

    public static void OpenInFolder(string folderPath)
    {
        Application.OpenURL("file:///" + folderPath);
    }
}

```
## 对上面的脚本进行一些简单的分析 ：
### 1、build 方法上的 `[MenuItem]` 标签，这使得这些方法可以在 Unity 编辑器的菜单中被找到和执行。

### 2 、根据不同的打包平台对 unity 中插件进行相应的设置
比如**SetXRSettingsByPlatform 方法**，根据不同的构建目标设置了 XR（扩展现实）的相关参数，主要可以分为以下 3 个步骤：
- 2.1找到需要修改参数的插件资源的 guid
	使用 `AssetDatabase.FindAssets` 方法来查找项目中指定类型（`t:ARCoreSettings`）的资源，并返回它们的 GUID（全局唯一标识符）数组。 `"t:ARCoreSettings"` 是一个 [[Unity中CSharp脚本进行打包#相关知识#搜索过滤器|搜索过滤器]]，它告诉 Unity 查找所有类型为 `ARCoreSettings` 的资源。
	
- 2.2获取插件的类型对象
	`AssetDatabase.GUIDToAssetPath(guids1[0])`：这部分代码将从给定的 GUID（全局唯一标识符）获取资源的路径。在上下文中，`guids1[0]` 可能是之前使用搜索过滤器找到的第一个资源的 GUID。
	`AssetDatabase.LoadAssetAtPath<ARCoreSettings>(...)`：这部分代码将从指定路径加载资源，并将其转换为 `ARCoreSettings` 类型。`LoadAssetAtPath` 方法的泛型参数 `<T>` 是所需加载资源的类型。
	
- 2.3对插件对象中的一些属性进行设置
### 3、切换构建平台
`EditorUserBuildSettings.SwitchActiveBuildTarget(buildGroup, buildTarget)` 这行代码是用于在 Unity 编辑器中切换当前的活动构建目标。它会将指定的构建目标（`buildTarget`）设置为当前活动的构建目标，并且会将此构建目标的相关设置应用到项目中。

具体来说，`buildGroup` 参数表示要切换的构建目标的目标平台组（比如 Android、iOS、Standalone 等）。`buildTarget` 参数则表示要切换到的具体构建目标（比如 Android、iOS、Windows 等）。

### 4、刷新资源库
`AssetDatabase.Refresh()` 是 Unity 中的一个方法，用于刷新 AssetDatabase，即刷新资源数据库。在调用此方法后，Unity 会重新加载项目中的所有资源，并更新资源数据库中的信息。

通常情况下，在对项目进行了一些修改后（比如导入新的资源、删除或移动资源等），需要调用 `AssetDatabase.Refresh()` 来确保 Unity 编辑器中的资源列表和数据库与项目中的实际情况保持同步。

### 5、设置 PlayerSettings 和 BuildPlayerOptions（build 参数）
- `BuildPlayerOptions` 是用于配置构建玩家（Build Player）时的选项的类。
- `buildPlayerOptions.scenes`用于指定需要构建的场景的路径。
- `buildPlayerOptions.locationPathName` 用于指定构建的输出路径和名称。
- `buildPlayerOptions.targetGroup` 是一个枚举值，用于指定构建的平台组。
- `buildPlayerOptions.target` 是一个枚举值，用于指定构建的目标平台。
- `buildPlayerOptions.options` 是一个枚举值，用于指定构建的选项。

### 6 、开始 build
- `BuildPipeline.BuildPlayer(buildPlayerOptions)` 是用于执行实际的构建操作的方法。它接受一个 `BuildPlayerOptions` 类型的参数，该参数包含了构建玩家的配置信息。执行该方法后，将返回一个 `BuildReport` 对象，其中包含了构建操作的结果报告。

## 相关知识
### 搜索过滤器
在 Unity 的 `AssetDatabase.FindAssets` 方法中，搜索过滤器用于指定要搜索的资源类型或名称的条件。这些过滤器可以帮助你精确地定位到你需要的资源，而不必遍历整个项目。

搜索过滤器可以采用多种形式，以下是一些常用的用法：
1. **按类型过滤**：使用 `t:` 后跟 Unity 类型名称，如 `t:Texture`、`t:Material`、`t:Prefab` 等。例如，`"t:ScriptableObject"` 将会返回所有的 ScriptableObject 类型资源。
    
2. **按名称过滤**：直接输入资源的名称，例如 `"MyPrefab"`、`"MyScript"` 等。这将返回所有名称与指定字符串匹配的资源。
    
3. **组合过滤器**：可以同时使用多个过滤器来进行组合搜索，使用空格分隔。例如，`"t:ScriptableObject MyAsset"` 将会返回所有类型为 ScriptableObject 并且名称包含 "MyAsset" 的资源。
    
4. **按标签过滤**：使用 `l:` 后跟标签名称来搜索已经标记了特定标签的资源。例如，`"l:MyTag"` 将会返回所有标记了 "MyTag" 标签的资源。
    
5. **按路径过滤**：使用 `p:` 后跟路径来搜索指定路径下的资源。例如，`"p:Assets/Textures"` 将会返回指定路径下的所有资源。

这些过滤器可以单独使用，也可以组合使用以获取特定的资源集合。使用搜索过滤器可以提高资源定位的效率，并帮助你更快速地管理项目中的资源。

# 使用命令行打包
```bat
@echo off
echo lunch unity.exe ,please wait a moment...
"C:\Program Files\Unity\Hub\Editor\2020.3.18f1c1\Editor\Unity.exe" -quit -batchmode -projectPath "D:\Unity\Unity\FViteMVC" -executeMethod ARViewerBuilder.BuildAPKForAndroid
echo "Build WebGL done"
pause
```
