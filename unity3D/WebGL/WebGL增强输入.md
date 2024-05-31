unity 打包出来的 webgl 应用存在两个问题：
1、网页不支持中文输入
2、输入框不支持精准的光标插入，选中文字等操作
原因：
unity 的 webgl 平台目前不支持 IME（An input method is an operating system component or program that allows users to enter characters and symbols not found on their input device.  For instance, on the computer, this allows the user of ‘Western’ keyboards to input Chinese, Japanese, Korean and Indic characters.）
解决方法：
使用了一个插件 [WebGLInput](https://github.com/kou-yeung/WebGLInput) ，这个插件的原理就是当你在 unity 的 webgl 应用中输入的时候，在网页上生成一个新的输入框，这个新的输入框是支持中文输入的，在这个输入框中完成中文输入之后，再将内容传回 unity 中，这样 unity 的输入框就可以正常显示中文了。
这个方法解决了第一个问题，带来了第二个问题，如下图，其中蓝色的框是网页端用 js 生成的
![[Pasted image 20240531110657.png|454]]![[Pasted image 20240531110748.png|475]]
因为我们对文字的操作是在蓝框中进行的，但是为了美观，蓝框一般是不会显示出来的，而且蓝框与黑框之间不是对齐的，所以我们是无法在黑框中实现对文字的精准控制的，比如说在文字中间插入光标。如果我们可以将蓝框和黑框精准的重合在一起，字体的 size 和居中、靠右等格式完全一致的话，再将蓝框隐藏（变透明），那么就可以解决问题 2 了。
![[Pasted image 20240531110810.png|469]]

## WebGLInput 主要函数解析
在 unity 中调用 js 代码需要[[WebGL：与浏览器脚本交互#从 Unity 脚本调用 JavaScript 函数|特定的语法]] ，在这个插件中，我又学到了一种用法
```jslib
var WebGLInput = {
    $instances: [],
	WebGLInputInit : function() {	},
	........
}
	
autoAddDeps(WebGLInput, '$instances'); 
mergeInto(LibraryManager.library, WebGLInput);
```
**autoAddDeps(WebGLInput, '$instances')**:
- `autoAddDeps` 是一个 Emscripten 提供的工具函数，用于声明模块之间的依赖关系。
- `WebGLInput` 是一个对象，包含了多个方法和属性，用于处理输入字段的操作。
- `'$instances'` 是一个全局数组，用于存储所有创建的输入字段实例。
- 这行代码的作用是将 `'$instances'` 数组作为 `WebGLInput` 模块的依赖项，确保在使用 `WebGLInput` 模块时，`'$instances'` 已经被正确加载。
所有函数都被包装到了 WebGLInput 这个对象中，这个对象中又包含了全局数组 instances，用来管理所有创建的 inputFiled
### 初始化函数
检查 `Runtime` 对象是否已经定义，如果没有定义，则创建一个包含 `dynCall` 函数的 `Runtime` 对象。`Runtime` 是一个包含许多与 WebAssembly 交互的工具和方法的对象。`dynCall` 是其中的方法之一，用于动态调用 WebAssembly 导出的 C 函数。
```jslib
WebGLInputInit : function() {
		// Remove the `Runtime` object from "v1.37.27: 12/24/2017"
		// if Runtime not defined. create and add functon!!
		if(typeof Runtime === "undefined") Runtime = { dynCall : dynCall }
	}
```
### WebGLInputCreate
创建网页端的输入框
### WebGLInputEnterSubmit
设置回车提交行为
```jslib
WebGLInputEnterSubmit: function(id, falg){
		var input = instances[id];
		// for enter key
		input.addEventListener('keydown', function(e) {
			if ((e.which && e.which === 13) || (e.keyCode && e.keyCode === 13)) {
				if(falg)
				{
					e.preventDefault();
					input.blur();
				}
			}
		});
    }
```
### WebGLInputTab
输入 Tab 键的操作
```jslib
WebGLInputTab:function(id, cb) {
		var input = instances[id];
		// for tab key
        input.addEventListener('keydown', function (e) {
            if ((e.which && e.which === 9) || (e.keyCode && e.keyCode === 9)) {
                e.preventDefault();
				// if enable tab text
				if(input.enableTabText){
                    var val = input.value;
                    var start = input.selectionStart;
                    var end = input.selectionEnd;
                    input.value = val.substr(0, start) + '\t' + val.substr(end, val.length);
                    input.setSelectionRange(start + 1, start + 1);
                    input.oninput();	// call oninput to exe ValueChange function!!
				} else {
				    Runtime.dynCall("vii", cb, [id, e.shiftKey ? -1 : 1]);
				}
            }
		});
	}
```
### WebGLInputFocus
使指定的输入框获取焦点。
```jslib
WebGLInputFocus: function(id){
	var input = instances[id];
	input.focus();
}
```
### WebGLInputOnFocus
设置输入框获取焦点时的回调函数
```jslib
WebGLInputOnFocus: function (id, cb) {
        var input = instances[id];
        input.onfocus = function () {
            Runtime.dynCall("vi", cb, [id]);
        };
    },
```
dynCall 函数中的参数解释
- **"vi"**:
    - `"vi"` 是一个签名字符串，用于指示被调用的函数的参数和返回类型。
    - `"v"` 表示函数没有返回值 (`void`)。
    - `"i"` 表示函数接受一个整数类型的参数 (`int`)。
- **cb**:
    - `cb` 是一个函数指针，指向一个在 Unity 中定义的 C 函数。
    - 这个指针通常是在 Unity 和 JavaScript 之间传递的，用于在 JavaScript 代码中调用 Unity 中的函数。
- **id**:
    - `[id]` 是传递给函数的参数列表。
    - 这里 `id` 是一个整数，通常用于标识某个输入字段实例或者其他需要回调处理的对象。
接下来的函数就不一一解释了
### WebGLInputOnBlur
设置输入框失去焦点时的回调函数
### WebGLInputIsFocus
检查指定的输入框是否为当前活动（聚焦）元素。
### WebGLInputOnValueChange
设置当输入框的值发生变化时触发的回调函数
```jslib
WebGLInputOnValueChange:function(id, cb){
        var input = instances[id];
        input.oninput = function () {
			var intArray = intArrayFromString(input.value);
            var value = (allocate.length <= 2) ? allocate(intArray, ALLOC_NORMAL):allocate(intArray, 'i8', ALLOC_NORMAL);
            Runtime.dynCall("vii", cb, [id,value]);
        };
    },
```
### WebGLInputOnEditEnd
设置当输入框编辑结束时触发的回调函数。
### WebGLInputSelectionStart
获取输入框中当前选择文本的起始位置
### WebGLInputSelectionEnd
获取输入框中当前选择文本的结束位置
### WebGLInputSelectionDirection
获取输入框中当前选择文本的方向。
### WebGLInputSetSelectionRange
设置输入框中选定文本的范围
### WebGLInputMaxLength
设置输入框的最大输入长度
### WebGLInputText
设置输入框的文本内容
```jslib
WebGLInputText:function(id, text){
        var input = instances[id];
		input.value = UTF8ToString(text);
	},
```
### WebGLInputDelete
删除指定 `id` 的输入框
### WebGLInputEnableTabText
启用或禁用指定 `id` 的输入框的 Tab 键功能
### WebGLInputForceBlur
强制将指定 `id` 的输入框失去焦点（即模拟输入框被用户手动点击其他地方以取消输入状态）。
### GetChineseInput
获取指定 `id` 的输入框中的文本，并清空输入框
```jslib
GetChineseInput:function(id) {
		var input = instances[id];
		var inputText = input.value;
		input.value = "";
		return inputText;
	}
```
