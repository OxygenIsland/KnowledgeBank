## 一、介绍
本章节将讲解通过API获取CPU上的图像将其装换为RGBA格式，将转换后的图像显示在 RawImage 上，并显示有关图像的信息。这和 ARCameraBackground 组件不同，后者只是在屏幕上显示摄像机图像。获取摄像机画面其实对于我们需要接入其他第三方SDK很有用。（比如：二维码识别、人脸识别、车牌识别、手势识别 等第三方SDK都需要我们传入视频画面）
## 二、案例讲解
这个案例在 [ARFoundation Samples]( https://github.com/Unity-Technologies/arfoundation-samples "ARFoundation Samples") 示例工程中有，叫做“CpuImages”。
1、在 Unity 中新建一个空场景，将场景中的 Main Camera，删除掉。
![[Pasted image 20240409094034.png|450]]
2、在 Hierarchy 面板中单击右键,再弹出的面板中点击 XR->AR Session Origin 按钮。创建一个 AR Session Origin 组件。
![[Pasted image 20240409094053.png|475]]
3、在 Hierarchy 面板中单击右键,再弹出的面板中点击 XR->AR Session 按钮。创建一个 AR Session 组件。
![[Pasted image 20240409094114.png|475]]
4、在 Hierarchy 面板点击右键，再弹出的面板中点击“UI->Raw Image” 按钮，将创建出来的对象命名为“RawCameraImage”，用来显示获取到的相机画面。
![[Pasted image 20240409094156.png|475]]
5、在 Hierarchy 面板点击右键，再弹出的面板中点击“UI->Text” 按钮，将创建出来的对象命名为“ImageInfo”，用来显示获取到的相机画面信息。
![[Pasted image 20240409094223.png|450]]
6、新建一个脚本，命名为 “CpuImageSample.cs”。挂载在 Canvas 对象上（代码如下）
```csharp
using System; 
using Unity.Collections.LowLevel.Unsafe; 
using UnityEngine; 
using UnityEngine.UI; 
using UnityEngine.XR.ARFoundation; 
using UnityEngine.XR.ARSubsystems; 

/// <summary>测试获取CPU图像</summary> 
public class CpuImageSample : MonoBehaviour 
{ 
	private ARCameraManager m_CameraManager; 
	public RawImage rawCameraImage; 
	public Text imageInfo; 
	private Texture2D m_CameraTexture; 
	private void Awake() 
	{ 
		m_CameraManager = FindObjectOfType<ARCameraManager>(); 
	} 
	private void OnEnable() 
	{ 
		if (m_CameraManager != null) 
		{ 
			m_CameraManager.frameReceived += onCameraFrameReceived; 
		} 
	} 
	private void OnDisable() 
	{ 
		if (m_CameraManager != null) 
		{ 
			m_CameraManager.frameReceived -= onCameraFrameReceived; 
		} 
	} 
	private void onCameraFrameReceived(ARCameraFrameEventArgs eventArgs) 
	{ 
		updateCameraImage(); 
	} 
	private unsafe void updateCameraImage() 
	{ 
		if (!m_CameraManager.TryAcquireLatestCpuImage(out XRCpuImage image)) 
		{ 
			return;
		} 
		imageInfo.text = string.Format( "Image info:\n\twidth: {0}\n\theight: {1}\n\tplaneCount: {2}\n\ttimestamp: {3}\n\tformat: {4}", image.width, image.height, image.planeCount, image.timestamp, image.format); 
		var format = TextureFormat.RGBA32; 
		if (m_CameraTexture == null || m_CameraTexture.width != image.width || m_CameraTexture.height != image.height) 
		{ 
			m_CameraTexture = new Texture2D(image.width, image.height, format, false); 
		} 
		var conversionParams = new XRCpuImage.ConversionParams(image, format, XRCpuImage.Transformation.MirrorY); 
		var rawTextureData = m_CameraTexture.GetRawTextureData<byte>(); 
		try 
		{ 
			image.Convert(conversionParams, new IntPtr(rawTextureData.GetUnsafePtr()), rawTextureData.Length); 
		} 
		finally 
		{ 
			image.Dispose(); 
		} 
		m_CameraTexture.Apply(); 
		rawCameraImage.texture = m_CameraTexture; 
	} 
}
```