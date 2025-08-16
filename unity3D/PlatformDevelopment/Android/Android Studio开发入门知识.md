---
title: "[[Android Studio开发入门知识]]"
type: Permanent
status: done
Creation Date: 2025-08-16 11:06
tags:
---
## 1、项目文件的目录结构
Android Studio 的项目目录结构经过了精心组织，以便于管理代码和资源。在默认的 "Android" 视图下，你会看到以下几个核心部分：
![[Pasted image 20250816112609.png|300]]
- **manifests**   
    - AndroidManifest.xml：这是项目的核心配置文件。它定义了应用的包名、组件（如 Activity、Service）、所需的权限（如网络访问、读取联系人）等基本信息。
- **java (或 [[Kotlin|kotlin]])**
    - 在这个目录下，你会看到几个子目录，其中一个是以你的包名命名的（例如 com.example.myapp）。这里存放着你所有的 Java 或 Kotlin 源代码。
    - 另外两个 (androidTest) 和 (test) 结尾的目录分别用于存放自动化测试代码和单元测试代码。
- **res (Resources)**
    - 这是存放所有非代码资源的地方。
        - drawable：存放图片文件。
        - layout：存放定义应用界面的 XML 布局文件。[13](https://www.google.com/url?sa=E&q=https%3A%2F%2Fvertexaisearch.cloud.google.com%2Fgrounding-api-redirect%2FAUZIYQF_MFItmgX_K6LUDw6Xx6Fw2jZBGKx_Aw9hMaW2qA735mrQDZWVtjT8LjnJ6HtTlxiintfKB79LCw63E1nKPhqEK1skYxcQ097lLkwJPxAYeQZpQnKh9Pfzm-ZQIlDJ7P6d7gQ9bakJFdHQaX1EGbIqoL85ALuO8RhYUQ%3D%3D)
        - mipmap：主要存放应用的启动图标。[12](https://www.google.com/url?sa=E&q=https%3A%2F%2Fvertexaisearch.cloud.google.com%2Fgrounding-api-redirect%2FAUZIYQHKqYSlejzH_Sk5OjtvfvMNPeS0voT-JtgwcJ9i58Zg5Wlc61gk8fVAn1LBnhvxLueuQqGZgU03YeeiIDaFjb5T3sOVgJAOAMblY8Hc-LLHLoa6IHh3ZXAcp6AAMADdHrPCvkog63GWpj22QO95QZUtaPN9UWiVO5CcdI8lsu09JsZePERX2JJ8gIQDO_rT0SEBMUDZzFr23z0YN2dw) 
        - values：存放一些值资源，如字符串 (strings.xml)、颜色 (colors.xml)、样式 (styles.xml) 等。[11](https://www.google.com/url?sa=E&q=https%3A%2F%2Fvertexaisearch.cloud.google.com%2Fgrounding-api-redirect%2FAUZIYQHmy6arKD_BLi2F0TIiVj_EyXqOL-UWPlZ6VK3mD6ddZOnVUHArusIxd-JpQNL87o8xIydUye0OdYelsP3tDL634bJ-uVpn7IT9cX8htx3WmFIA28NvoYkVQbhs550M9M872ciqT1R62mQs6ZXhFMO4wiN9NI-7tfjMHsg%3D)[13](https://www.google.com/url?sa=E&q=https%3A%2F%2Fvertexaisearch.cloud.google.com%2Fgrounding-api-redirect%2FAUZIYQF_MFItmgX_K6LUDw6Xx6Fw2jZBGKx_Aw9hMaW2qA735mrQDZWVtjT8LjnJ6HtTlxiintfKB79LCw63E1nKPhqEK1skYxcQ097lLkwJPxAYeQZpQnKh9Pfzm-ZQIlDJ7P6d7gQ9bakJFdHQaX1EGbIqoL85ALuO8RhYUQ%3D%3D) 
- **Gradle**
    - 这里存放着所有与 Gradle 构建相关的文件。具体内容会在下面进行展开

## 2、Gradle相关的文件：
![[Pasted image 20250816114019.png|525]]
### 1. settings.gradle.kts (项目花名册)
- **作用**：这个文件的核心作用是告诉 Gradle，你当前的这个项目**包含了哪些模块 (module)**。
- **详解**：项目里目前只有一个 app 模块。所以 settings.gradle.kts 文件的内容会很简单，就是 include ':app'。如果你以后添加了新的模块（比如一个 AAR 库模块 mylibrary），你就需要在这里面加入 include ':mylibrary'。
    
### 2. build.gradle.kts (项目级的“总指挥”)
- **位置**：位于项目的根目录。
- **作用**：这是**项目级别 (Project-level)** 的构建脚本。它负责配置整个项目所有模块都通用的构建规则和依赖。
- **详解**：在较新的 Android Studio 版本中，这个文件的主要职责被简化了，通常只用来声明插件，比如 Android Gradle 插件 (com.android.application) 和 Kotlin 插件 (org.jetbrains.kotlin.android)，并指定它们的版本。它告诉 Gradle 用什么工具来构建整个项目。

(注意：app 文件夹里面会有一个属于它自己的 build.gradle.kts 文件，那个是模块级别的，负责配置 app 模块的具体信息，比如应用ID、依赖库等，是开发中最常修改的文件)

### 3. libs.versions.toml (依赖库版本中央登记表)
- **作用**：这是一个 **版本目录 (Version Catalog)** 文件，是目前 Google 推荐的、用于**集中管理所有依赖库及其版本号**的最佳实践。
- **详解**：当项目越来越大，引用的第三方库越来越多时，在各个模块的 build.gradle 文件中分别写版本号会变得难以管理。TOML 文件允许你把所有库的名字、版本号都统一写在这个地方，然后在 build.gradle.kts 文件中通过别名来引用它们。这样做的好处是：
    - **统一管理**：升级一个库的版本只需要修改这一个文件。
    - **代码清晰**：build.gradle.kts 文件看起来更整洁。
    - **智能提示**：Android Studio 对这种方式的支持很好，有代码补全。    

### 4. Gradle Wrapper 相关文件 (版本守护者)
这几个文件共同构成了 **Gradle Wrapper**，它们的作用是确保所有参与这个项目的开发者，以及持续集成(CI)服务器，都使用**完全相同版本**的 Gradle 来构建项目，避免因环境不一致导致构建失败。
- **gradlew (Linux/macOS 脚本)** 和 **gradlew.bat (Windows 脚本)**：
    - 这是 Gradle Wrapper 的执行脚本。在命令行里构建项目时，你不应该直接用 gradle 命令，而应该用 ./gradlew (在 Linux/macOS) 或 gradlew (在 Windows)。它会自动检查本地有没有 gradle-wrapper.properties 中指定的 Gradle 版本，如果没有，就会自动下载并使用它。
- **gradle/wrapper/gradle-wrapper.properties**：
    - 这是 Wrapper 的核心配置文件。它里面最关键的一行是 distributionUrl，这个 URL 指明了本项目需要使用的 Gradle 的确切版本和下载地址。
- **gradle/wrapper/gradle-wrapper.jar**：
    - 这是一个二进制 jar 文件，包含了下载和解压指定版本 Gradle 的逻辑。当你运行 gradlew 命令时，实际上就是它在工作。
- **比喻**：Gradle Wrapper 就像项目的“版本守护者”，无论谁拿到这份代码，只要运行 gradlew，就能保证使用的是统一的构建环境，解决了“在我电脑上明明能跑”的经典难题。
    

### 5. 其他配置文件
- **gradle.properties**：
    - 这是一个全局属性配置文件。你可以在这里配置一些影响 Gradle 构建性能的参数，比如设置 JVM 的内存大小 (org.gradle.jvmargs=-Xmx...)，或者开启一些实验性功能。这里配置的属性对项目中所有模块都生效。
        
## 3、项目包名
项目包名Package name一般按照**反向域名**规则来进行命名：
- 如果一个公司拥有域名 example.com，那么他们开发的包名就会以 com.example 开头。[15](https://www.google.com/url?sa=E&q=https%3A%2F%2Fvertexaisearch.cloud.google.com%2Fgrounding-api-redirect%2FAUZIYQETZmom-p8ADbyQ-5y8UYcR2hFBbhp6Ev1dwzK20M0FfXVC28CXsYbL-Rcjr4XmV8ROWzDLhOxKN46qRHWzFJAkTk_RD7zwhRczdRkNKDNdFD3obreLOaF8z3pi0PRVuK55TumpmvG96qDDqx1QSDgObh7Dc_GWhl8DmlZDk3Bk)[16](https://www.google.com/url?sa=E&q=https%3A%2F%2Fvertexaisearch.cloud.google.com%2Fgrounding-api-redirect%2FAUZIYQEHs8ierdbZmCvC2ZinbpfJLQbvdpyVbS-rY25yNu5hwiNn_KnMUwDZ6HAdJeH2M6zbgFb5l8ubTzEvs-PHUfUTttoss7bzWjfsr59XNcgBAX3bZXPEqueFoTlgdRBmVqhMdj-SnOD4TaP87r1Zj5Go-HWwFzOue7Ow9u711o2tjy4sqJ841FHSL2WCRE7Lbk3imfkf5PNI5Np5TXceH75F)  后面可以再跟上项目名或模块名，比如 com.example.myapp。
- com. 本身是顶级域名的一种，代表“商业” (commercial)。[16](https://www.google.com/url?sa=E&q=https%3A%2F%2Fvertexaisearch.cloud.google.com%2Fgrounding-api-redirect%2FAUZIYQEHs8ierdbZmCvC2ZinbpfJLQbvdpyVbS-rY25yNu5hwiNn_KnMUwDZ6HAdJeH2M6zbgFb5l8ubTzEvs-PHUfUTttoss7bzWjfsr59XNcgBAX3bZXPEqueFoTlgdRBmVqhMdj-SnOD4TaP87r1Zj5Go-HWwFzOue7Ow9u711o2tjy4sqJ841FHSL2WCRE7Lbk3imfkf5PNI5Np5TXceH75F)[18](https://www.google.com/url?sa=E&q=https%3A%2F%2Fvertexaisearch.cloud.google.com%2Fgrounding-api-redirect%2FAUZIYQH3w6rq6OPjTl_GwOOKR_0Lf0waXjNqGIB7zL3_xGGmnReLE3rWcLvtb1OdOdVNQEGGgY_-vKqBdMwMs_GymcRosADlVlkNbUBVe-H4OA_E36iEQ4H4KkuPhyyYGvW3wdLanVybVQjtU-up93huej5x52NiT7QU) 其他常见的还有 org. (非营利组织) 和 edu. (教育机构) 等。[17](https://www.google.com/url?sa=E&q=https%3A%2F%2Fvertexaisearch.cloud.google.com%2Fgrounding-api-redirect%2FAUZIYQFQ5NH-dziaQTiuH49_lC_9uLFFW7M_Iuqe5ghKN0X4fEx_7VueMooXF1GJZElsTykNqPq00mVW6wOOz3f-kN-S2Ee1TEZmAO4kNEwfEMjHm2x5ExcN2RDXFJhiM95NuYUVeEvY6nIKt866eHJEmHqddYgu4Rf_q6Mm-FJonb0CDXOYKa-5ZiK8wTs4G7F1yKfD)[18](https://www.google.com/url?sa=E&q=https%3A%2F%2Fvertexaisearch.cloud.google.com%2Fgrounding-api-redirect%2FAUZIYQH3w6rq6OPjTl_GwOOKR_0Lf0waXjNqGIB7zL3_xGGmnReLE3rWcLvtb1OdOdVNQEGGgY_-vKqBdMwMs_GymcRosADlVlkNbUBVe-H4OA_E36iEQ4H4KkuPhyyYGvW3wdLanVybVQjtU-up93huej5x52NiT7QU) 
