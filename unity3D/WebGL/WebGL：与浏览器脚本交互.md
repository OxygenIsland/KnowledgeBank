构建适用于 Web 的内容时，可能需要与网页上的其他元素进行通信。或者，您可能希望使用 Unity 当前在默认情况下未公开的 Web API 来实现功能。在这两种情况下，都需要直接与浏览器的 JavaScript 引擎连接。Unity WebGL 提供了不同的方法来执行此操作。
##  从 Unity 脚本调用 JavaScript 函数
在项目中使用浏览器 JavaScript 的建议方法是将 JavaScript 源代码添加到项目中，然后直接从脚本代码中调用这些函数。为此，请使用 .jslib 扩展名将包含 JavaScript 代码的文件放置在 Assets 文件夹中的“Plugins”子文件夹下。插件文件需要有如下所示的语法：
```csharp
mergeInto(LibraryManager.library, { 
	Hello: function () { 
		window.alert("Hello, world!"); 
	}, 
	
	HelloString: function (str) { 
		window.alert(Pointer_stringify(str)); 
	}, 
	
	PrintFloatArray: function (array, size) { 
		for(var i = 0; i < size; i++) 
		console.log(HEAPF32[(array >> 2) + i]); 
	}, 
	
	AddNumbers: function (x, y) { 
	return x + y; 
	}, 
	
	StringReturnValueFunction: function () { 
		var returnStr = "bla"; 
		var bufferSize = lengthBytesUTF8(returnStr) + 1; 
		var buffer = _malloc(bufferSize); 
		stringToUTF8(returnStr, buffer, bufferSize); return buffer; 
	}, 
	
	BindWebGLTexture: function (texture) { 
		GLctx.bindTexture(GLctx.TEXTURE_2D, GL.textures[texture]); 
	}, 
});
```
然后，可从 C# 脚本调用这些函数，如下所示：
```csharp
using UnityEngine; 
using System.Runtime.InteropServices; 
public class NewBehaviourScript : MonoBehaviour 
{ 
	[DllImport("__Internal")] private static extern void Hello(); 
	[DllImport("__Internal")] private static extern void HelloString(string str); 
	[DllImport("__Internal")] private static extern void PrintFloatArray(float[] array, int size); 
	[DllImport("__Internal")] private static extern int AddNumbers(int x, int y); 
	[DllImport("__Internal")] private static extern string StringReturnValueFunction(); 
	[DllImport("__Internal")] private static extern void BindWebGLTexture(int texture); 
	void Start() 
	{ 
		Hello(); 
		HelloString("This is a string."); 
		float[] myArray = new float[10]; 
		PrintFloatArray(myArray, myArray.Length); 
		int result = AddNumbers(5, 7); 
		Debug.Log(result); 
		Debug.Log(StringReturnValueFunction()); 
		var texture = new Texture2D(0, 0, TextureFormat.ARGB32, false); 
		BindWebGLTexture(texture.GetNativeTextureID()); 
	} 
}
```
简单的数字类型可在函数参数中传递给 JavaScript，无需进行任何转换。其他数据类型将作为 emscripten 堆（实际上就是 JavaScript 中的一个大型数组）中的指针进行传递。对于字符串，可使用 `Pointer_stringify` helper 函数转换为 JavaScript 字符串。要返回字符串值，必须调用 `_malloc` 来分配一些内存，并调用 `stringToUTF8` helper 函数向其中写入 JavaScript 字符串。如果字符串是返回值，则 il2cpp 运行时将负责为您释放内存。对于原始类型的数组，`emscripten` 针对内存的不同大小的整数、无符号整数或浮点数表示形式，提供其堆的不同 `ArrayBufferViews`：__HEAP8、HEAPU8、HEAP16、HEAPU16、HEAP32、HEAPU32、HEAPF32、HEAPF64__。
为了在 WebGL 中访问纹理，emscripten 提供了 `GL.textures` 数组，该数组将本机纹理 ID 从 Unity 映射到 WebGL 纹理对象。可在 emscripten 的 WebGL 上下文 `GLctx` 中调用 WebGL 函数。具体可见 [[unity webgl获取网络摄像头|unity webgl获取网络摄像头]]
## 从 JavaScript 调用 Unity 脚本函数
有时需要从浏览器的 JavaScript 向 Unity 脚本发送一些数据或通知。建议的做法是调用内容中的游戏对象上的方法。如果要从嵌入在项目中的 JavaScript 插件执行调用，可使用以下代码：
`SendMessage(objectName, methodName, value);`
其中，__objectName__ 是场景中的对象名称；__methodName__ 是当前附加到该对象的脚本中的方法名称；__value__ 可以是字符串、数字，也可为空。例如：
```csharp
unityinstance.SendMessage('MyGameObject', 'MyFunction'); 
SendMessage('MyGameObject', 'MyFunction', 5); 
SendMessage('MyGameObject', 'MyFunction', 'MyString');
```

在 index.html 中调用时，需要在 Unity 的资源已经加载完成才可以，这个好解决，js 加个 button；
<button Type="button" onclick="TestSend()">WebToUnity</button>
其次在调用这个方法前需要先实例化 UnityInstance 变量；
```js
//这是用于渲染 Unity 项目的 WebGL canvas 元素。Unity 将在此处渲染其内容。
<canvas id="unity-canvas" width=360 height=640></canvas>
var canvas = document.querySelector("#unity-canvas");

//创建配置信息
var buildUrl = "Build";
var loaderUrl = buildUrl + "/Build.loader.js";
var config = {
	dataUrl: buildUrl + "/Build.data.unityweb",
	frameworkUrl: buildUrl + "/Build.framework.js.unityweb",
	codeUrl: buildUrl + "/Build.wasm.unityweb",
	streamingAssetsUrl: "StreamingAssets",
	showBanner: unityShowBanner,
};

//创建unity实例
var script = document.createElement("script");
var glctx;
var unityInstanceV;
script.src = loaderUrl;
script.onload = () => {
	createUnityInstance(canvas, config, (progress) => {
	    progressBarFull.style.width = 100 * progress + "%";
	}).then((unityInstance) => {
        loadingBar.style.display = "none";
        unityInstanceV = unityInstance
        //调用其他js脚本里的函数，传递unity实例
        InitUnityInstance(unityInstance)
	}).catch((message) => {
		alert(message);
	});
};
document.body.appendChild(script);

```
最后调用
```js
if (unityInstance != null) {
	var msg = `${videoWidth},${videoHeight}`
	console.log('[WebCamera] albert:js调用c#的回调函数' + msg);
	unityInstance.SendMessage('WebglCameraMan', 'InitCallback', msg);
}
```
