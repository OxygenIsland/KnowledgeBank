---
title: "[[Android Archive]]"
type: Permanent
status: done
Creation Date: 2025-08-12 17:09
tags:
---
AAR（Android Archive）是 Android 平台特有的一种库文件格式，用于封装和分发可复用的 Android 功能模块（如 UI 组件、工具库或 SDK）。相比传统的 JAR（Java Archive）文件，AAR 支持包含 Android 特有的资源文件和配置，更适合 Android 项目的模块化开发。以下是其核心特性和对比：
### 一、AAR 的核心组成

1. ​**​代码文件​**​
    - `classes.jar`：编译后的 Java/Kotlin 字节码文件。
2. ​**​资源文件​**​
    - `res/`：布局文件（XML）、图片、字符串资源等。
    - `assets/`：原始资源文件（如音频、视频）。
3. ​**​配置与元数据​**​
    - `AndroidManifest.xml`：声明库的组件、权限和最低 SDK 版本。
    - `R.txt`：资源索引文件，记录资源 ID 映射关系。
    - `proguard.txt`：代码混淆规则（若启用）。
4. ​**​本地库支持​**​
    - `jni/`：包含 `.so` 文件（如 ARM 架构的本地库）。
    - `libs/`：依赖的第三方 JAR 包。

---
### 二、AAR vs. JAR：关键区别

|​**​特性​**​|​**​AAR​**​|​**​JAR​**​|
|---|---|---|
|​**​包含内容​**​|代码 + Android 资源 + 配置|仅 Java/Kotlin 字节码（`.class`）|
|​**​资源支持​**​|✅ 支持布局、图片、字符串等|❌ 不支持|
|​**​清单文件​**​|✅ 含 `AndroidManifest.xml`|❌ 不含|
|​**​本地库支持​**​|✅ 支持 `.so` 文件|❌ 不支持|
|​**​适用场景​**​|Android UI 组件、功能模块封装|纯逻辑工具类（如网络请求、加密）|

---
### 三、AAR 的核心优势
1. ​**​模块化开发​**​
    - 将 UI、逻辑和资源封装为独立模块，供多个项目复用。
    - 例如：支付模块、自定义控件库可直接打包为 AAR 嵌入不同 App。
2. ​**​简化依赖管理​**​
    - 通过 [[Gradle]] 一键集成：
```gradle
dependencies {
    implementation(name: 'mylibrary', ext: 'aar')  // 本地引用
    implementation 'com.example:sdk:1.0.0'         // 远程仓库引用
}
```
3. ​**​资源隔离与冲突解决​**​
    - 通过 `resourcePrefix` 强制资源名前缀，避免冲突：
```gradle
android {
    resourcePrefix "custom_"  // 资源名变为 custom_button.xml
}
```
---

### 四、AAR 的使用场景
1. ​**​第三方 SDK 分发​**​
    - 如推送服务（友盟）、支付（支付宝 SDK）均以 AAR 形式提供。
2. ​**​团队协作开发​**​
    - 各团队独立开发模块（如登录、地图），打包为 AAR 供主工程集成。
3. ​**​功能模块复用​**​
    - 将成熟功能（如相机控制、网络请求）封装为 AAR，减少重复编码。
---

### 五、注意事项
1. ​**​依赖传递问题​**​
    - AAR ​**​不自动包含​**​其依赖的三方库（如 OkHttp），需在主工程显式声明依赖。
2. ​**​版本兼容性​**​
    - 库的 `minSdkVersion` 必须 ≤ 主工程的 `minSdkVersion`。
3. ​**​混淆规则​**​
    - 库的混淆规则需通过 `consumerProguardFiles` 传递给主工程：
```gradle
android {
    defaultConfig {
        consumerProguardFiles 'lib-proguard-rules.txt'
    }
}
```
---

### 六、生成 AAR 的步骤

1. 在 Android Studio 中创建 ​**​Android Library​**​ 模块。
2. 编写代码和资源文件。
3. 通过 `Build > Make Module` 生成 AAR 文件（路径：`/build/outputs/aar/`）。
4. 分发给其他项目或上传至 Maven 仓库。