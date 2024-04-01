本文是基于 WebRTC 的 RTSP 播放器的 JavaScript 代码。利用 WebRTC 技术来获取摄像头的视频流，并通过 Canvas 将视频渲染出来。
1、首先在 unity 中创建一个纹理用于存储摄像头的视频流
```csharp
public void Load(string url, int width, int height)
{
    if (status != Status.Initializing && status != Status.Released)
    {
        return;
    }
    Debug.Log("[WebRTSPPlayer] Load");
    texture = new Texture2D(width, height);
    //获取纹理对象的指针，并将其转换为整数类型 `_textureId`。
	//在 WebGL 构建中将纹理对象的指针传递给 JavaScript，以便在 WebGL 上下文中绑定纹理对象。这样，在 WebGL 构建中就可以使用这个 `_textureId` 来操作 Unity 中创建的纹理对象。
    _textureId = (int)texture.GetNativeTexturePtr();
#if UNITY_WEBGL && !UNITY_EDITOR
	//调用js中的方法将纹理对象的指针传递给 JavaScript
    RtspPlayerCreate(url, _textureId, width, height);
#endif
	status = Status.Initialized;
    onInitSuccess.Invoke();
}
```
2、调用 js 将视频流绘制到纹理上
```jslib
mergeInto(LibraryManager.library, {
	RtspPlayerInit: function() {
        // Get the WebGL texture object from the Emscripten texture ID.
		WebRtspPlayerInit();
    },

	RtspPlayerCreate: function(url,id,width,height) {
        // Get the WebGL texture object from the Emscripten texture ID.
		WebRtspPlayerCreate(Pointer_stringify(url),id,width,height);
    },

	RtspPlayerUpdate: function(id) {
        var canvas = WebRtspPlayerGetCanvas(id);
		WebRtspPlayerUpdate(id);

		var textureObj = GL.textures[id];
		// GLctx is the webgl context of the Unity canvas
        GLctx.bindTexture(GLctx.TEXTURE_2D, textureObj);
        GLctx.texParameteri(GLctx.TEXTURE_2D, GLctx.TEXTURE_WRAP_S, GLctx.CLAMP_TO_EDGE);
        GLctx.texParameteri(GLctx.TEXTURE_2D, GLctx.TEXTURE_WRAP_T, GLctx.CLAMP_TO_EDGE);
        GLctx.texParameteri(GLctx.TEXTURE_2D, GLctx.TEXTURE_MIN_FILTER, GLctx.LINEAR);
 
        // Upload the canvas image to the GPU texture.
        GLctx.texSubImage2D(GLctx.TEXTURE_2D, 0, 0, 0, GLctx.RGBA, GLctx.UNSIGNED_BYTE, canvas);
	},
});
```
主要关注一下 RtspPlayerUpdate 这个函数
1.  `WebRtspPlayerGetCanvas(id)`：获取指定 id 的 RTSP 播放器的画布对象。这个画布包含了当前视频帧的图像数据。
```js
function WebRtspPlayerGetCanvas(textureId) {
	if (ct_canvas == null) {
		ct_canvas = document.createElement("canvas");
		ct_canvas.width = width;
		ct_canvas.height = height;
    }
    return ct_canvas;
}
```
2. `WebRtspPlayerUpdate(id)`：更新指定 id 的 RTSP 播放器，可能用于获取新的视频帧。
```js
function WebRtspPlayerUpdate(textureId) {
	//获取 Canvas 元素的 2D 渲染上下文对象，用于在 Canvas 上进行绘制操作。
	var ctx = ct_canvas.getContext("2d");
	//获取 id 为 `videoElement` 的 `<video>` 元素对象，这是一个 HTML5 视频元素。
	const video = document.getElementById('videoElement');
	//将视频元素的当前帧绘制到 Canvas 上。
	ctx.drawImage(video, 0, 0, ct_canvas.width, ct_canvas.height);
}
```
3. `GL.textures[id]`：从 WebGL 上下文中获取指定 id 的纹理对象。
    
4. `GLctx.bindTexture(GLctx.TEXTURE_2D, textureObj)`：将纹理对象绑定到 WebGL 上下文的 2D 纹理目标上。
    
5. `GLctx.texParameteri(...)`：设置纹理参数，包括水平和垂直方向的纹理包裹模式、纹理缩小过滤模式等。
    
6. `GLctx.texSubImage2D(...)`：将画布中的图像数据上传到 GPU 中的纹理对象中，用于更新纹理。
