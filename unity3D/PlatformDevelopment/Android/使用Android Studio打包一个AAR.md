---
title: "[[使用Android Studio打包一个AAR]]"
type: Permanent
status: done
Creation Date: 2025-08-09 10:29
tags:
---
## 1、在 Android Studio 中创建和打包插件 (AAR)
> AAR ([[Android Archive]]) 文件是安卓库项目的二进制分发形式，它包含了编译后的代码（Java/Kotlin）、资源文件和 AndroidManifest.xml。Unity 可以直接使用这种格式的插件。

**1. 创建一个新的 Android Studio 项目**

- 打开 Android Studio，选择 "File" -> "New" -> "New Project..."。
- 选择 "No Activity" 模板，然后点击 "Next"。[1](https://www.google.com/url?sa=E&q=https%3A%2F%2Fvertexaisearch.cloud.google.com%2Fgrounding-api-redirect%2FAUZIYQG-QFX618DC6eEthiEDkPVcqjwahzjFeG8nPJ69DtPptWdUAd4ZxDxrvBetJ7RR0uknSQBjhOPDulZFq2LFThDMShOER6chqN3fYuZL1GyPE5jSxQ-bWNO0EMOKbyCY7K1GdkMGc8v1)
- 配置你的项目名称、包名 (Package name)、保存位置和最低 SDK 版本。包名非常重要，之后在 Unity 中调用代码时会用到。[1](https://www.google.com/url?sa=E&q=https%3A%2F%2Fvertexaisearch.cloud.google.com%2Fgrounding-api-redirect%2FAUZIYQG-QFX618DC6eEthiEDkPVcqjwahzjFeG8nPJ69DtPptWdUAd4ZxDxrvBetJ7RR0uknSQBjhOPDulZFq2LFThDMShOER6chqN3fYuZL1GyPE5jSxQ-bWNO0EMOKbyCY7K1GdkMGc8v1)
    

**2. 创建一个安卓库模块 (Android Library Module)**

你的插件功能将在这个模块中实现。
- 在项目创建后，选择 "File" -> "New" -> "New Module..."。[2](https://www.google.com/url?sa=E&q=https%3A%2F%2Fvertexaisearch.cloud.google.com%2Fgrounding-api-redirect%2FAUZIYQFDXsTtv3CgRgswf_O1Szd05-qOpekzlIKwWXXP0Yl0IOSVfezPS0FqyoQvcj71hAWtqIDGcxgcd36f3pP678D3BuzKmevAoTBjvHIf9LCvgVQDSFzg6wACseQTNuLoAbGvGq0PmRpuWaIXHO3v3tM7dFZ8ObE6xF9EFmXiVmTQgbaR-6SDtFbZ6BE%3D)
- 在弹出的窗口中选择 "Android Library"，然后点击 "Next"。[3](https://www.google.com/url?sa=E&q=https%3A%2F%2Fvertexaisearch.cloud.google.com%2Fgrounding-api-redirect%2FAUZIYQF85HcUpbejYzNe8VL8kasn-kHRtF9INNNWLNLQse_PeSc_4rlCY0G9moE4aZc1ALJIrCd1vEnouTFj1aQ97vdleGp6_cKftowxTVPbcNF4vXLvzUQV0ecEBxDmckr8BK1ynIs_I1c%3D)
- 为你的库模块命名，并确认模块名称和包名。完成后点击 "Finish"。[3](https://www.google.com/url?sa=E&q=https%3A%2F%2Fvertexaisearch.cloud.google.com%2Fgrounding-api-redirect%2FAUZIYQF85HcUpbejYzNe8VL8kasn-kHRtF9INNNWLNLQse_PeSc_4rlCY0G9moE4aZc1ALJIrCd1vEnouTFj1aQ97vdleGp6_cKftowxTVPbcNF4vXLvzUQV0ecEBxDmckr8BK1ynIs_I1c%3D)[4](https://www.google.com/url?sa=E&q=https%3A%2F%2Fvertexaisearch.cloud.google.com%2Fgrounding-api-redirect%2FAUZIYQHx86Pium89-KhZRC1sJS96kQ4iffDEA37OFBhYa3XO2-KYk9h0XTO12qxUgc29r2spM31kHG6jzI1HdE4ASBMSceRMA8epOyRnmBlv_7RMkomyina8avpD9mjA-LVkJYaEv8sX_kY%3D)

**3. 编写原生代码 (Java/Kotlin)**
现在你可以在新创建的库模块中编写你的插件功能了。

- 在项目视图中，找到你的库模块，然后在 src/main/java/你的包名 路径下创建一个新的 Java 或 Kotlin 类。[1](https://www.google.com/url?sa=E&q=https%3A%2F%2Fvertexaisearch.cloud.google.com%2Fgrounding-api-redirect%2FAUZIYQG-QFX618DC6eEthiEDkPVcqjwahzjFeG8nPJ69DtPptWdUAd4ZxDxrvBetJ7RR0uknSQBjhOPDulZFq2LFThDMShOER6chqN3fYuZL1GyPE5jSxQ-bWNO0EMOKbyCY7K1GdkMGc8v1)
- 在这个类中，你可以编写任何你想要在 Unity 中调用的方法。例如，一个简单的静态方法：
```Java
package com.example.myunityplugin;

import android.app.Activity;
import android.widget.Toast;

public class MyPlugin {
    // 用于接收 Unity 的 Activity 上下文
    private static Activity unityActivity;

    public static void receiveUnityActivity(Activity activity) {
        unityActivity = activity;
    }

    public static void showToast(String message) {
        if (unityActivity != null) {
            unityActivity.runOnUiThread(() -> {
                Toast.makeText(unityActivity, message, Toast.LENGTH_SHORT).show();
            });
        }
    }

    public static int getFive() {
        return 5;
    }
}
```
**4. (可选但推荐) 引入 Unity 的 classes.jar**
如果你需要从安卓插件向 Unity 发送消息（例如，通过回调），你需要引用 Unity 的 classes.jar 文件。[2](https://www.google.com/url?sa=E&q=https%3A%2F%2Fvertexaisearch.cloud.google.com%2Fgrounding-api-redirect%2FAUZIYQFDXsTtv3CgRgswf_O1Szd05-qOpekzlIKwWXXP0Yl0IOSVfezPS0FqyoQvcj71hAWtqIDGcxgcd36f3pP678D3BuzKmevAoTBjvHIf9LCvgVQDSFzg6wACseQTNuLoAbGvGq0PmRpuWaIXHO3v3tM7dFZ8ObE6xF9EFmXiVmTQgbaR-6SDtFbZ6BE%3D)[5](https://www.google.com/url?sa=E&q=https%3A%2F%2Fvertexaisearch.cloud.google.com%2Fgrounding-api-redirect%2FAUZIYQGs6xyPTwVHGeWdXzRXSSRRLxXrJclbMMt9qAyMu1z0YwZOjfnF140-TRgWw0oYKWIpoo6NxcoTtBogTXeZI6vJE_rJXIu26UzHm0AiO6A3JZIRTmMytZpXNbmEl6Ol1HUme3sTGyg%3D)这允许你在 Java/Kotlin 代码中访问 com.unity3d.player.UnityPlayer 类。

- 找到你 Unity 安装目录下的 classes.jar 文件。路径通常是：Unity安装目录/Editor/Data/PlaybackEngines/AndroidPlayer/Variations/mono/Release/Classes/ classes.jar。
- 在 Android Studio 中，将 classes.jar 文件复制到你的库模块的 libs 目录下（如果不存在 libs 目录，可以手动创建一个）。[2](https://www.google.com/url?sa=E&q=https%3A%2F%2Fvertexaisearch.cloud.google.com%2Fgrounding-api-redirect%2FAUZIYQFDXsTtv3CgRgswf_O1Szd05-qOpekzlIKwWXXP0Yl0IOSVfezPS0FqyoQvcj71hAWtqIDGcxgcd36f3pP678D3BuzKmevAoTBjvHIf9LCvgVQDSFzg6wACseQTNuLoAbGvGq0PmRpuWaIXHO3v3tM7dFZ8ObE6xF9EFmXiVmTQgbaR-6SDtFbZ6BE%3D)
- 右键点击复制进来的 classes.jar 文件，选择 "Add As Library..."。

**5. 配置 build.gradle 文件**
你需要修改库模块的 build.gradle 文件，以确保它被构建成一个库 (AAR) 而不是一个应用 (APK)。
- 打开你的库模块下的 build.gradle 文件。
- 确保文件顶部的插件声明是 apply plugin: 'com.android.library'。[6](https://www.google.com/url?sa=E&q=https%3A%2F%2Fvertexaisearch.cloud.google.com%2Fgrounding-api-redirect%2FAUZIYQGL6kV3RMP_riyhd6stl_hQuxNAyIixFEXSWrKn062c8Qcm3O8jO--6bVrk2FW1Fbb7sLF8hKevlVotZ1qxElN_90KRy9n2e-zns-DqssJrT5JPgwazfBQcmdjb_XoT58_Np009Upd4IwWvN967MOpL63gWoYbo2qjvsUNJVeIX7nP4WScmhapbrQ%3D%3D)
- 在 dependencies 部分，添加对 classes.jar 的引用：
```Groovy
dependencies {
    implementation fileTree(dir: 'libs', include: ['*.jar'])
    // 其他依赖
}
```

**6. 处理 AndroidManifest.xml**

每个安卓库都有自己的 AndroidManifest.xml 文件。Unity 在构建最终的 APK 时，会将所有插件的 Manifest 文件与主 Manifest 文件合并。[7](https://www.google.com/url?sa=E&q=https%3A%2F%2Fvertexaisearch.cloud.google.com%2Fgrounding-api-redirect%2FAUZIYQFuLATA5rGxRV2ED-aoxCygxBYFCBCVhadKJBdITBdX_nT0q5XLr85pHFUQq6mAYcFOTI-rEQdSddBsmt-_N44KXH-_H9zfvL4liWbrjJbVV90DHZ1f0JayTIx7qQoezeHWXdm5SqMLsXIwRYdRjpvp46VJ6XeImBKdEeV7yGGvH3PPEOAv)[8](https://www.google.com/url?sa=E&q=https%3A%2F%2Fvertexaisearch.cloud.google.com%2Fgrounding-api-redirect%2FAUZIYQEynJB02xNtR6iB6dpNRw9qZ2VjzM_ba4tS5k1KRShQ9l-nz-Mm2IP1XADeMCJimQCOiJ89mTiioeC7-yEN8IYkMEPZnT7O7IozglYgttZ0f9D62pd0lu2MgWlPnZwTymZRejzDzNLu1JtyUz4xZM9_F4n6ZH-5TCFswqZ3XamHeLYFmH6G)]

- 你可以在 src/main/AndroidManifest.xml 中声明你的插件所需要的权限、服务等。例如，如果你的插件需要网络权限，可以添加：  
    `<uses-permission android:name="android.permission.INTERNET" />`
- Unity 会自动处理合并过程。[7](https://www.google.com/url?sa=E&q=https%3A%2F%2Fvertexaisearch.cloud.google.com%2Fgrounding-api-redirect%2FAUZIYQFuLATA5rGxRV2ED-aoxCygxBYFCBCVhadKJBdITBdX_nT0q5XLr85pHFUQq6mAYcFOTI-rEQdSddBsmt-_N44KXH-_H9zfvL4liWbrjJbVV90DHZ1f0JayTIx7qQoezeHWXdm5SqMLsXIwRYdRjpvp46VJ6XeImBKdEeV7yGGvH3PPEOAv)

完成以上步骤后，你就可以构建 AAR 文件了。
- 在 Android Studio 的右侧，打开 "Gradle" 标签。[9](https://www.google.com/url?sa=E&q=https%3A%2F%2Fvertexaisearch.cloud.google.com%2Fgrounding-api-redirect%2FAUZIYQEuwE_rB92DJVqKX2JISmXbzTQmWUqWi4stWFA9NK_F8Awzuuh6hGZ8dedPITGxIz6MMaVpENdcpLqifASMX7iCJQfGkomVvfDTH2L3Z6KBGVJT8IdGb87AhdgmQ0BjeYVENbPiBMxVPocBwbJL5tPC)
- 在你的库模块下，找到 "Tasks" -> "build"，然后双击 "assemble" 或 "build" 任务。[9](https://www.google.com/url?sa=E&q=https%3A%2F%2Fvertexaisearch.cloud.google.com%2Fgrounding-api-redirect%2FAUZIYQEuwE_rB92DJVqKX2JISmXbzTQmWUqWi4stWFA9NK_F8Awzuuh6hGZ8dedPITGxIz6MMaVpENdcpLqifASMX7iCJQfGkomVvfDTH2L3Z6KBGVJT8IdGb87AhdgmQ0BjeYVENbPiBMxVPocBwbJL5tPC)
- 构建成功后，你可以在库模块的 build/outputs/aar/ 目录下找到生成的 .aar 文件（通常会有 debug 和 release 两个版本，建议使用 release 版本）。[6](https://www.google.com/url?sa=E&q=https%3A%2F%2Fvertexaisearch.cloud.google.com%2Fgrounding-api-redirect%2FAUZIYQGL6kV3RMP_riyhd6stl_hQuxNAyIixFEXSWrKn062c8Qcm3O8jO--6bVrk2FW1Fbb7sLF8hKevlVotZ1qxElN_90KRy9n2e-zns-DqssJrT5JPgwazfBQcmdjb_XoT58_Np009Upd4IwWvN967MOpL63gWoYbo2qjvsUNJVeIX7nP4WScmhapbrQ%3D%3D)
