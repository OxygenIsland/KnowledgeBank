---
title: "[[Kotlin]]"
type: Reference
status: done
Creation Date: 2025-08-16 12:08
tags:
---
### 1. Kotlin 简介

Kotlin 是一种由 JetBrains（就是开发 IntelliJ IDEA 和 ReSharper 的那家公司）开发的现代化、静态类型的编程语言。2017 年，谷歌宣布 Kotlin 成为 Android 开发的官方语言。[1](https://www.google.com/url?sa=E&q=https%3A%2F%2Fvertexaisearch.cloud.google.com%2Fgrounding-api-redirect%2FAUZIYQHapS1gj3OzBRs2Es2qAxA_rDN0xtT0DnSEwLNCbpVSoXwHqiG-RnnOAdLOneG_ywIN3aGGQhXbaRk9FxsMXy1E6lh7FT7elqESHj1yzbd8eYOAZbr_LA5JmtQmuyYz5PXJUJTqw0or1h7CdWdJupRSgUOIz-SmojA%3D) 
**核心特点：**
- **简洁 (Concise)**：相比 Java，Kotlin 能用更少的代码实现同样的功能，代码更易读、更易维护。[1](https://www.google.com/url?sa=E&q=https%3A%2F%2Fvertexaisearch.cloud.google.com%2Fgrounding-api-redirect%2FAUZIYQHapS1gj3OzBRs2Es2qAxA_rDN0xtT0DnSEwLNCbpVSoXwHqiG-RnnOAdLOneG_ywIN3aGGQhXbaRk9FxsMXy1E6lh7FT7elqESHj1yzbd8eYOAZbr_LA5JmtQmuyYz5PXJUJTqw0or1h7CdWdJupRSgUOIz-SmojA%3D)[2](https://www.google.com/url?sa=E&q=https%3A%2F%2Fvertexaisearch.cloud.google.com%2Fgrounding-api-redirect%2FAUZIYQGm_LUjuSdZp4hQY2set0iUJ2sK1ZTzS8dFllOh3X6pYZ2dHjQWL7Qv-W0lYkOqEmlEmImHHAS12rTJ-ySkE3NN68tWwYSU-_m6OqQYQvxLIWjT6iFR7sVbwKWH7v0430-XpOLWyFjDrXcWCcqdteqgsJsxZP2w8Qs3tNFM) 
- **安全 (Safe)**：Kotlin 在类型系统中内置了**空安全 (Null Safety)** 机制，旨在从根本上消除困扰许多程序员的 NullPointerException (空指针异常)。[3](https://www.google.com/url?sa=E&q=https%3A%2F%2Fvertexaisearch.cloud.google.com%2Fgrounding-api-redirect%2FAUZIYQEj88rVAprRVN3LKemWYC80VOL94LjllMyCU-rCrUHYhUG2LcnW7iqw9t_K600XV0-tGVivK1fTTdf1Qrd_cgerlKTTPXvi2HZERO3jQi4er3B58nQLjFI0GxTqjws4_ceaLKvAbjSvFcj9) 
    
- **互操作性强 (Interoperable)**：Kotlin 可以与 Java 语言 100% 互操作。这意味着你可以在 Kotlin 项目中无缝调用 Java 代码，反之亦然，并且可以继续使用所有成熟的 Java 库。[4](https://www.google.com/url?sa=E&q=https%3A%2F%2Fvertexaisearch.cloud.google.com%2Fgrounding-api-redirect%2FAUZIYQGVcdL1ensCXRCN_OY6N42zIVYLmjHpvY9x9IcWFWsjpazKqgREyxv0W2JN-ufFgIJYyC_ZRxj4K-7Pz_qJsZeb6iVMebyg4EXpRLkjbKoVYTisExCdGZnneHKSxsVvUTZwYuZ2Zw%3D%3D)[5](https://www.google.com/url?sa=E&q=https%3A%2F%2Fvertexaisearch.cloud.google.com%2Fgrounding-api-redirect%2FAUZIYQFvuDXNulFFOD5xRUj7YjZs_1clZBvIDKZV1BOb7uNRYGRuuwPHq2BzwHOZFKA3VIdO8xF9NqAMIfuFd-gJst4e6ohuGcjf79q90q3qJfl_ozOYqPGmoRhWDPfMStoWx0luvt6t9dCJxsqzhKIL) 
    
- **多平台 (Multiplatform)**：Kotlin 不仅限于 Android 开发，还可以用于服务器后端开发、Web 前端 (通过编译成 JavaScript)，甚至桌面和 iOS 应用 (通过 Kotlin Multiplatform)。[1](https://www.google.com/url?sa=E&q=https%3A%2F%2Fvertexaisearch.cloud.google.com%2Fgrounding-api-redirect%2FAUZIYQHapS1gj3OzBRs2Es2qAxA_rDN0xtT0DnSEwLNCbpVSoXwHqiG-RnnOAdLOneG_ywIN3aGGQhXbaRk9FxsMXy1E6lh7FT7elqESHj1yzbd8eYOAZbr_LA5JmtQmuyYz5PXJUJTqw0or1h7CdWdJupRSgUOIz-SmojA%3D)[6](https://www.google.com/url?sa=E&q=https%3A%2F%2Fvertexaisearch.cloud.google.com%2Fgrounding-api-redirect%2FAUZIYQGkEDJAPUHJ-RPMcBjELB_8q06qfGzlSodoGFjxKZV2KeqqN2JfBaC8o-KEpujsBLbJdiwAyjwAgToU_cPc-yMBdmULWkasDPg39NM4DEq-eDzy9pU9CshM07nm6xA3xM9AKC5K7pqLmPVbmBwTLfOclyWrKaq92ox3FhDdBplJ5bkFIY1iQVSrGShyms4QyVfvc5uMtQ%3D%3D) 
    

对于 C# 开发者来说，Kotlin 感觉会很亲切，因为它吸收了许多现代语言的优秀特性，其中不少特性 C# 也拥有或正在引入。[7](https://www.google.com/url?sa=E&q=https%3A%2F%2Fvertexaisearch.cloud.google.com%2Fgrounding-api-redirect%2FAUZIYQGNcKJheJ0rgT4YKHy0wHCWPxlM0Kx7VGZbRY_Nms3ontNHcCMpkc832_DsQiGdi5FM6B9kNCaHI9wx8zzwCrFCTqdM2cs4DvPMHR3hxEq6WNM4Lr9PnD5yEGImXayHENT8JFTsfQ%3D%3D) 

### 2. C# 开发者快速上手：核心语法对比
#### **变量声明**

一个核心区别是，Kotlin 的类型声明在变量名**之后**，用冒号隔开。[8](https://www.google.com/url?sa=E&q=https%3A%2F%2Fvertexaisearch.cloud.google.com%2Fgrounding-api-redirect%2FAUZIYQExvIAaI9NTP36Fd0UZg52xfLkbb2nAuIRUTVDP-G1eQNK6tI18T7YvRAjQdBfM_vKboVWQJX667RfvvUn2DpaSC_Ri0VZtXfjwTT1C-uc9DvAni6oE_Ms77P9J5CaELKUICOYgvWmGwsi6up9wQ3MWPLF4pf-AcVO0trN0) 

- **var (可变变量)**：类似于 C# 的 var，但用法更普遍。
    
- **val (不可变变量/只读)**：一旦赋值后就不能再改变。这类似于 C# 的 readonly 关键字，但 val 的使用频率在 Kotlin 中高得多，鼓励编写不可变的代码。[2](https://www.google.com/url?sa=E&q=https%3A%2F%2Fvertexaisearch.cloud.google.com%2Fgrounding-api-redirect%2FAUZIYQGm_LUjuSdZp4hQY2set0iUJ2sK1ZTzS8dFllOh3X6pYZ2dHjQWL7Qv-W0lYkOqEmlEmImHHAS12rTJ-ySkE3NN68tWwYSU-_m6OqQYQvxLIWjT6iFR7sVbwKWH7v0430-XpOLWyFjDrXcWCcqdteqgsJsxZP2w8Qs3tNFM)[8](https://www.google.com/url?sa=E&q=https%3A%2F%2Fvertexaisearch.cloud.google.com%2Fgrounding-api-redirect%2FAUZIYQExvIAaI9NTP36Fd0UZg52xfLkbb2nAuIRUTVDP-G1eQNK6tI18T7YvRAjQdBfM_vKboVWQJX667RfvvUn2DpaSC_Ri0VZtXfjwTT1C-uc9DvAni6oE_Ms77P9J5CaELKUICOYgvWmGwsi6up9wQ3MWPLF4pf-AcVO0trN0) 
    
|   |   |   |
|---|---|---|
|C#|Kotlin|说明|
|string name = "World";|var name: String = "World"|声明一个可变字符串|
|var score = 100;|var score = 100|类型推断，score 为 Int|
|const string ApiKey = "...";|const val API_KEY = "..."|编译期常量|
|readonly int MaxSize = 10;|val maxSize = 10|运行时常量（只读）|

---
#### **函数 (方法)**
Kotlin 使用 fun 关键字定义函数，返回值类型同样在函数名**之后**。[7](https://www.google.com/url?sa=E&q=https%3A%2F%2Fvertexaisearch.cloud.google.com%2Fgrounding-api-redirect%2FAUZIYQGNcKJheJ0rgT4YKHy0wHCWPxlM0Kx7VGZbRY_Nms3ontNHcCMpkc832_DsQiGdi5FM6B9kNCaHI9wx8zzwCrFCTqdM2cs4DvPMHR3hxEq6WNM4Lr9PnD5yEGImXayHENT8JFTsfQ%3D%3D)[8](https://www.google.com/url?sa=E&q=https%3A%2F%2Fvertexaisearch.cloud.google.com%2Fgrounding-api-redirect%2FAUZIYQExvIAaI9NTP36Fd0UZg52xfLkbb2nAuIRUTVDP-G1eQNK6tI18T7YvRAjQdBfM_vKboVWQJX667RfvvUn2DpaSC_Ri0VZtXfjwTT1C-uc9DvAni6oE_Ms77P9J5CaELKUICOYgvWmGwsi6up9wQ3MWPLF4pf-AcVO0trN0) 

|   |   |   |
|---|---|---|
|C#|Kotlin|说明|
|int Add(int a, int b)<br/>{ return a + b; }|fun add(a: Int, b: Int): Int <br/>{ return a + b }|标准函数定义|
|int Add(int a, int b) => a + b;|fun add(a: Int, b: Int) = a + b|表达式函数体，更简洁|
|void Log(string message)<br/>{ Console.WriteLine(message); }|fun log(message: String) <br/>{ println(message) }|void 在 Kotlin 中对应 Unit，通常可以省略[[8](https://www.google.com/url?sa=E&q=https%3A%2F%2Fvertexaisearch.cloud.google.com%2Fgrounding-api-redirect%2FAUZIYQExvIAaI9NTP36Fd0UZg52xfLkbb2nAuIRUTVDP-G1eQNK6tI18T7YvRAjQdBfM_vKboVWQJX667RfvvUn2DpaSC_Ri0VZtXfjwTT1C-uc9DvAni6oE_Ms77P9J5CaELKUICOYgvWmGwsi6up9wQ3MWPLF4pf-AcVO0trN0)]|

---

#### **空安全 (Null Safety)**

这是 Kotlin 最大的亮点之一，也是和 C#（8.0 之前的版本）最显著的区别。Kotlin 的类型系统默认**不允许**为 null。

|   |   |   |
|---|---|---|
|C# (Nullable enabled)|Kotlin|说明|
|string name = "test";<br/>name = null; // 警告|var name: String = "test"<br/>name = null // 编译错误！|默认类型不可为 null|
|string? name = "test";<br/>name = null; // OK|var name: String? = "test"<br/>name = null // OK|在类型后加 ? 表示可为 null|
|int length = name?.Length ?? 0;|val length = name?.length ?: 0|安全调用 ?. 和 Elvis 操作符 ?: (功能和 C# 的 ?? 完全一样)|

---

#### **字符串模板 (String Interpolation)**
与 C# 几乎一样，只是语法稍有不同。

|   |   |   |
|---|---|---|
|C#|Kotlin|说明|
|var name = "Alex"; <br/>var text = $"Hello, {name}";|val name = "Alex" <br/>val text = "Hello, $name"|简单变量直接用 $|
|var text = $"Length: {name.Length}";|val text = "Length: ${name.length}"|表达式用 ${} 包裹|

---

#### **流程控制：if 和 when (对应 C# 的 switch)**

if-else 在 Kotlin 中是**表达式**，意味着它可以有返回值。 when 是 switch 的超级增强版。

|   |   |
|---|---|
|C#|Kotlin|
|int value = 1;<br/>string result;<br/>if (value > 0) { result = "Positive"; } else { result = "Non-positive"; }|val value = 1<br/>val result = if (value > 0) "Positive" else "Non-positive"|
|switch (statusCode)<br/>{<br/>case 200: result = "OK"; break;<br/>case 404: result = "Not Found"; break;<br/>default: result = "Unknown"; break;<br/>}|val result = when (statusCode) {<br/>200 -> "OK"<br/>404 -> "Not Found"<br/>else -> "Unknown"<br/>}|

when 还可以匹配范围、类型等，非常强大。

---

#### **类和数据类 (Classes and Data Classes)**

Kotlin 的类定义非常简洁，构造函数可以直接在类名后声明。

|   |   |
|---|---|
|C#|Kotlin|
|public class User <br/>{<br/>public string Name { get; set; }<br/>public int Age { get; set; }<br/>public User(string name, int age)<br/>{<br/>Name = name;<br/>Age = age;<br/>}<br/>}|class User(val name: String, val age: Int)|
|需要手动实现 Equals, GetHashCode, ToString 等|data class User(val name: String, val age: Int)|

**data class** 是 Kotlin 的一个“杀手锏”。只需在 class 前加上 data，编译器会自动为你生成 equals()、hashCode()、toString()、copy() 等方法，这在 C# 中对应计划引入的 record 类型。[7](https://www.google.com/url?sa=E&q=https%3A%2F%2Fvertexaisearch.cloud.google.com%2Fgrounding-api-redirect%2FAUZIYQGNcKJheJ0rgT4YKHy0wHCWPxlM0Kx7VGZbRY_Nms3ontNHcCMpkc832_DsQiGdi5FM6B9kNCaHI9wx8zzwCrFCTqdM2cs4DvPMHR3hxEq6WNM4Lr9PnD5yEGImXayHENT8JFTsfQ%3D%3D) 

### 3. C# 开发者的快速上手建议

1. **拥抱 val**：尽可能使用 val 来声明变量。这会引导你写出更稳定、副作用更少的代码，符合函数式编程的理念。
    
2. **熟悉空安全**：这是思维方式上最大的转变。习惯于处理可空类型 (?)，并善用 ?. 和 ?: 来写出优雅又安全的代码。
    
3. **利用 Android Studio 的工具**：
    
    - **Java 到 Kotlin 转换器**：虽然没有直接的 C# 到 Kotlin 转换器，但你可以找一段类似的 Java 代码，或者将你的 C# 代码思路先用 Java “翻译”一下，然后粘贴到 Kotlin 文件中，Android Studio 会提示你自动转换为 Kotlin。这个过程能帮助你快速学习语法对应关系。[9](https://www.google.com/url?sa=E&q=https%3A%2F%2Fvertexaisearch.cloud.google.com%2Fgrounding-api-redirect%2FAUZIYQF-pY3ohGwUeV0JuhrMny7OwHu-J6en9kKSsRuAm3LfeoeBj_XlJxei_BvuNLA6B6AsE8iIq_qMXKT548utl_RH9Wleh0mbFwFIur9txDeg0fv8Zrcs4KFuBRUrSDAbngs9uOo-Irq7_NaF2tgO7-kEqHrZNSDnbEZXUHEK5uZhcRfgVXH2Eh9VSwXPxl8kZV_ns5dwMt1bHQ%3D%3D) 
        
    - **多看范例**：在学习 Android 开发时，直接去看官方的 Kotlin 范例代码，模仿其风格和写法。
        
4. **忘记分号**：Kotlin 代码行末尾不需要分号。[8](https://www.google.com/url?sa=E&q=https%3A%2F%2Fvertexaisearch.cloud.google.com%2Fgrounding-api-redirect%2FAUZIYQExvIAaI9NTP36Fd0UZg52xfLkbb2nAuIRUTVDP-G1eQNK6tI18T7YvRAjQdBfM_vKboVWQJX667RfvvUn2DpaSC_Ri0VZtXfjwTT1C-uc9DvAni6oE_Ms77P9J5CaELKUICOYgvWmGwsi6up9wQ3MWPLF4pf-AcVO0trN0) 
    
5. **扩展函数 (Extension Functions)**：这个概念和[[扩展方法(Extension Methods)|C# 的扩展方法]]完全一样，可以让你在不继承类的情况下为其添加新功能，非常实用。[3](https://www.google.com/url?sa=E&q=https%3A%2F%2Fvertexaisearch.cloud.google.com%2Fgrounding-api-redirect%2FAUZIYQEj88rVAprRVN3LKemWYC80VOL94LjllMyCU-rCrUHYhUG2LcnW7iqw9t_K600XV0-tGVivK1fTTdf1Qrd_cgerlKTTPXvi2HZERO3jQi4er3B58nQLjFI0GxTqjws4_ceaLKvAbjSvFcj9) 
    
总而言之，你已有的 C# 编程经验是学习 Kotlin 的巨大优势。你只需要关注语法上的细微差异和 Kotlin 独有的特性（如空安全和 data class），很快就能熟练地使用 Kotlin 进行开发。