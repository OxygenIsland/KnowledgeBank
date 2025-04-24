---
title: "[[URP 实现毛玻璃效果]]"
type: Literature
status: done
Creation Date: 2025-03-23 14:42
tags:
---
## 适用于3D物体
![[8638144608a04c81bb78d481d3177ea5.gif|500]]
**毛玻璃也叫磨砂玻璃：** 是用物理或化学方法处理过的一种表面粗糙不平整的半透明玻璃。

**毛玻璃成像原理：** 毛玻璃表面不平整，光线通过毛玻璃被反射后向四面八方射出去（因为毛玻璃表面不是光滑的平面，使光产生了漫反射），折射到视网膜上已经是不完整的像，于是就看不清楚（很模糊）玻璃背后的东西了。

**毛玻璃效果的应用：**

最上面的浏览器地址栏为毛玻璃背景的地址栏。
左上角的为普通毛玻璃，带凹凸不平玻璃纹理
右上角的为毛玻璃背景的一个相册实现，相框上面的相片layer为AfterBlurGlass，所以最后被渲染
左下角的为毛玻璃带贴花的一种实现，“福“字图案为毛玻璃的贴图
右下角为另一个好看的毛玻璃效果实现

### **游戏开发中的毛玻璃效果展示与实现原理：**
然而正常在游戏引擎或者PhotoShop中的半透明面片，只会叠加颜色并不能产生模糊的效果。那么如何实现毛玻璃效果呢？
实现如上效果，的原理如下：

1.先渲染除毛玻璃外的物体（不透明和半透明），然后做高斯模糊，将结果保存到RenderTexture。
2.再渲染毛玻璃，算出屏幕坐标，去高斯模糊过的RenderTexture上面采样。将玻璃贴图和高斯模糊过的贴图做混合处理。
3.最后渲染压在毛玻璃上面的贴纸。

下面我们以UnityURP管线实现下如上的效果

首先实现一个BlurGlassRenderPass在 渲染半透明物体后 把颜色缓冲区中的图像做高斯模糊，并存保存在一个RT上。

管线配置如下图：
![[Pasted image 20250325155906.png|500]]

可以看到这边配置了一个[[3.Universal Renderer(通用渲染器)|渲染器]] ，根据[[3.Universal Renderer(通用渲染器)#Filtering|Filtering]]的配置，可以知道，这个renderer的透明层和不透明层，不渲染BlurGlass和AfterBlurGlass这两个层级。
依次来看一下这个renderer中的 [[4.URP Renderer Feature|Renderer Feature]] ,第一个BeforeBlurGlass是我们自定义的RenderFeature，如何创建custom RenderFeature，请参见[[How to create a custom Renderer Feature]]
### BeforeBlurGlass
RendererFeature的代码如下：
```csharp
using UnityEngine;
using UnityEngine.Rendering.Universal;
namespace BlurGlass
{
    public class BlurGlassRenderPassFeature : ScriptableRendererFeature
    {
        [System.Serializable]
        public class Settings
        {
	        //在后处理前执行
            public RenderPassEvent renderEvent = RenderPassEvent.BeforeRenderingPostProcessing;
            public LayerMask layerMask = -1;  // -1表示所有层（二进制全1）

            public Material blurMat;    //模糊用的材质球
            public RenderTexture blurRT;    //模糊后的图像输出到的RT
            public int blurIterations = 3;   //模糊迭代次数
            public int blurDownSample = 2;  //模糊向下压缩图像大小
            public float blurSize = 3f;     //模糊的偏移量
        }

        BlurGlassRenderPass m_ScriptablePass;
        public Settings settings;
        public override void Create()
        {
	        //初始化渲染通道实例
            m_ScriptablePass = new BlurGlassRenderPass(settings);
            // 设置渲染事件触发时机
            m_ScriptablePass.renderPassEvent = settings.renderEvent;
        }
		// 将自定义Pass加入URP渲染队列，每帧自动调用
        public override void AddRenderPasses(ScriptableRenderer renderer, ref RenderingData renderingData)
        {
            renderer.EnqueuePass(m_ScriptablePass);
        }
    }
}
```

RenerPass代码如下：
```csharp
namespace BlurGlass
{
    public class BlurGlassRenderPass : ScriptableRenderPass
    {
        private Material _blurMat;  //存储模糊Shader的材质实例，用于执行模糊算法
        private RenderTexture _blurRt;   //最终输出模糊结果的渲染目标
        private RenderTargetIdentifier _source;  //主相机的原始颜色缓冲区，即需要被模糊处理的输入图像
        private RTHandle _tempRTHandle1;   // 交替使用的临时渲染目标，用于多Pass模糊处理
        private RTHandle _tempRTHandle2;

        private int _iterations;     // 模糊迭代次数，每次迭代包含水平+垂直两个方向的模糊处理
        private float _blurSize;     //模糊半径（单位：像素），控制模糊强度
        private int _downSample;     //降采样系数（2的幂次方），用于缩小临时RT尺寸以提升性能
        private int _offsetsID;

        public BlurGlassRenderPass(BlurGlassRenderPassFeature.Settings param)
        {
            renderPassEvent = param.renderEvent;
            _blurMat = param.blurMat;
            _iterations = param.blurIterations;
            _downSample = param.blurDownSample;
            _blurSize = param.blurSize;
            _blurRt = param.blurRT;
            _offsetsID = Shader.PropertyToID("offsets");  // 通过Shader.PropertyToID预计算Shader属性ID，避免在渲染循环中频繁字符串查询
        }

		//  准备阶段
        public override void OnCameraSetup(CommandBuffer cmd, ref RenderingData renderingData)
        {
            base.OnCameraSetup(cmd, ref renderingData);
            _source = renderingData.cameraData.renderer.cameraColorTargetHandle;
			// 计算缩放因子：1/2^downSample (如downSample=2 → 1/4分辨率)
            float scaleFactor = 1f / Mathf.Pow(2, _downSample);
            RenderTextureDescriptor blitTargetDescriptor = renderingData.cameraData.cameraTargetDescriptor;
            blitTargetDescriptor.depthBufferBits = 0;
            blitTargetDescriptor.colorFormat = RenderTextureFormat.Default;
			//  根据降采样参数创建低分辨率临时RT
            RenderingUtils.ReAllocateIfNeeded(ref _tempRTHandle1, new Vector2(scaleFactor, scaleFactor), in blitTargetDescriptor, FilterMode.Bilinear, TextureWrapMode.Clamp);
            RenderingUtils.ReAllocateIfNeeded(ref _tempRTHandle2, new Vector2(scaleFactor, scaleFactor), in blitTargetDescriptor, FilterMode.Bilinear, TextureWrapMode.Clamp);
        }
		//  执行阶段
        public override void Execute(ScriptableRenderContext context, ref RenderingData renderingData)
        {
            CommandBuffer cmd = CommandBufferPool.Get();
            RenderTextureDescriptor opaqueDesc = renderingData.cameraData.cameraTargetDescriptor;
            opaqueDesc.depthBufferBits = 0;
            //  初始拷贝
            cmd.Blit(_source, _tempRTHandle1);
            for (int i = 0; i < _iterations; ++i)
            {
                float x = _blurSize / Screen.width;
                float y = _blurSize / Screen.height;
                // 水平模糊
                cmd.SetGlobalVector(_offsetsID, new Vector2(x, 0));
                cmd.Blit(_tempRTHandle1, _tempRTHandle2, _blurMat);
                //垂直模糊
                cmd.SetGlobalVector(_offsetsID, new Vector2(0, y));
                cmd.Blit(_tempRTHandle2, _tempRTHandle1, _blurMat);
            }
            //输出结果
            cmd.Blit(_tempRTHandle1, _blurRt);
            context.ExecuteCommandBuffer(cmd);
            CommandBufferPool.Release(cmd);
        }

		public override void OnCameraCleanup(CommandBuffer cmd) 
		{
			// 在Pass结束时统一释放，避免内存泄漏
		    _tempRTHandle1?.Release();
		    _tempRTHandle2?.Release();
		}
    }
}
```

模糊shader：
```cshader
Shader "mgo/Blur" {
	Properties
	{
		_MainTex ("Base (RGB)", 2D) = "" {}
	}

	HLSLINCLUDE
	
	#include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"

	struct appdata
	{
		float4 vertex:POSITION;
		float2 texcoord:TEXCOORD0;
	};
	struct v2f 
	{
		float4 pos : POSITION;
		float2 uv0 : TEXCOORD0;
		float4 uv1 : TEXCOORD1;
		float4 uv2 : TEXCOORD2;
		float4 uv3 : TEXCOORD3;
	};
	
	float2 offsets;
	sampler2D _MainTex;
	
	v2f vert (appdata v) 
	{
		v2f o;
		VertexPositionInputs vertexInput = GetVertexPositionInputs(v.vertex.xyz);
		o.pos = vertexInput.positionCS;
		o.uv0.xy = v.texcoord.xy;

		o.uv1 =  v.texcoord.xyxy + offsets.xyxy * float4(1,1, -1,-1);
		o.uv2 =  v.texcoord.xyxy + offsets.xyxy * float4(1,1, -1,-1) * 2.0;
		o.uv3 =  v.texcoord.xyxy + offsets.xyxy * float4(1,1, -1,-1) * 3.0;
		return o;
	}
	
	half4 frag (v2f i) : COLOR
	{
		half4 color = float4 (0,0,0,0);

		color += 0.40 * tex2D (_MainTex, i.uv0);
		color += 0.15 * tex2D (_MainTex, i.uv1.xy);
		color += 0.15 * tex2D (_MainTex, i.uv1.zw);
		color += 0.10 * tex2D (_MainTex, i.uv2.xy);
		color += 0.10 * tex2D (_MainTex, i.uv2.zw);
		color += 0.05 * tex2D (_MainTex, i.uv3.xy);
		color += 0.05 * tex2D (_MainTex, i.uv3.zw);
		return color;
	}

	ENDHLSL
	
	Subshader 
	{
		Tags { "RenderType"="Opaque" }
        LOD 100

		Pass 
		{
			ZTest Always
			Cull Off 
			ZWrite Off
			HLSLPROGRAM
			#pragma vertex vert
			#pragma fragment frag
			ENDHLSL
		}
	}
}
```
渲染毛玻璃的shader：

```cshader
Shader "mgo/BlurGlass" 
{
	Properties
	{
		_MainTexture("MainTexture", 2D) = "" {}
		_BlurTexture("BlurTexture", 2D) = "" {}
		_TintColor("TintColor", Color) = (0, 0, 1, 0.5)
	}

	Subshader 
	{
		Pass
		{
			Tags
			{
				"LightMode" = "UniversalForward"
			}

			ZTest Always Cull Off ZWrite Off
			Blend SrcAlpha OneMinusSrcAlpha

			CGPROGRAM

			#include "UnityCG.cginc"

			struct appdata
			{
				float4 vertex:POSITION;
				float2 uv:TEXCOORD0;
			};
			struct v2f
			{
				float4 pos : POSITION;
				float2 uv : TEXCOORD0;
			};

			sampler2D _MainTexture;
			float4 _MainTexture_ST;
			sampler2D _BlurTexture;
			float4 _TintColor;

			v2f vert(appdata v) 
			{
				v2f o;
				//计算出裁剪空间下的坐标
				o.pos = UnityObjectToClipPos(v.vertex.xyz);
				o.uv = TRANSFORM_TEX(v.uv, _MainTexture);
				return o;
			}

			half4 frag(v2f i) : SV_Target
			{
				//_ScreenParams.xy 
				//x 是摄像机目标纹理的宽度（以像素为单位），y 是摄像机目标纹理的高度（以像素为单位）
				half2 screenUV = (i.pos.xy / _ScreenParams.xy);
				//对模糊RT采样
				half4 blurCol = tex2D(_BlurTexture, screenUV);
				//对玻璃贴图采样
				half4 mainCol = tex2D(_MainTexture, i.uv);
				mainCol *= _TintColor;
				//根据玻璃颜色和模糊RT计算最终呈现的颜色
				blurCol.rgb = blurCol.rgb * (1-mainCol.a) + mainCol.rgb * mainCol.a;
				if(mainCol.a < 0.005)
				{
					blurCol.a = 0;
				}
				return blurCol;
			}

			#pragma vertex vert
			#pragma fragment frag
			ENDCG
		}
	}
}
```

### BlurGlass
[[4.URP Renderer Feature#Render Objects渲染器功能|Render Objects]]是URP预构建的Renderer Feature。
BlurGlass在渲染完透明物体后，会渲染BlurGlass层的所有不透明物体，也就是所有的毛玻璃
###  AfterBlurGlass
AfterBlurGlass在渲染后处理之前，会渲染AfterBlurGlass层的所有透明物体，也就是压在毛玻璃上的透明物体

## 适用于UI
下面介绍的是一个开源项目[Unified-Universal-Blur](https://github.com/lukakldiashvili/Unified-Universal-Blur) **Unified Blur** is best used with UI components that are part of the `Screen Space - Overlay` canvas.

渲染管线的配置就不多说了，就是在添加renderer feature的时候，发现只有添加到default renderer才会生效
![[1743646843249.png|439]]

下面是renderer feature 的代码
```csharp
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;

namespace Unified.Universal.Blur
{
    public class UniversalBlurFeature : ScriptableRendererFeature
    {
        public enum InjectionPoint
        {
            BeforeRenderingTransparents = RenderPassEvent.BeforeRenderingTransparents,
            BeforeRenderingPostProcessing = RenderPassEvent.BeforeRenderingPostProcessing,
            AfterRenderingPostProcessing = RenderPassEvent.AfterRenderingPostProcessing,
        }

        public Material passMaterial; // 模糊材质
        [HideInInspector] public int passIndex = 0; // 材质Pass索引

        [Header("Blur Settings")]
        public InjectionPoint injectionPoint = InjectionPoint.AfterRenderingPostProcessing;

        [Space]
        [Range(0f, 1f)] public float intensity = 1.0f;  // 模糊强度
        [Range(1f, 10f)] public float downsample = 2.0f; // 降采样比例
        [Range(0f, 5f)] public float scale = .5f;   // 模糊缩放
        [Range(1, 20)] public int iterations = 6;  // 迭代次数


        // 声明该渲染通道（`UniversalBlurPass`）默认需要的输入资源类型（此处为颜色缓冲区 `Color`）。
        //大多数全屏后处理效果（如模糊）需要基于当前颜色缓冲区的数据进行处理。
        private ScriptableRenderPassInput requirements = ScriptableRenderPassInput.Color;

        // Hidden by scope because of incorrect behaviour in the editor
        private bool disableInSceneView = true;

        private UniversalBlurPass fullScreenPass;
        private bool requiresColor;
        private bool injectedBeforeTransparents;

        /// <inheritdoc/>
        public override void Create()
        {
            // 初始化模糊Pass并配置渲染事件
            fullScreenPass = new UniversalBlurPass();
            fullScreenPass.renderPassEvent = (RenderPassEvent)injectionPoint;

            ScriptableRenderPassInput modifiedRequirements = requirements;

            requiresColor = (requirements & ScriptableRenderPassInput.Color) != 0;
            injectedBeforeTransparents = injectionPoint <= InjectionPoint.BeforeRenderingTransparents;

            if (requiresColor && !injectedBeforeTransparents)
            {
                modifiedRequirements ^= ScriptableRenderPassInput.Color;
            }

            fullScreenPass.ConfigureInput(modifiedRequirements);
        }

        /// <inheritdoc/>
        public override void AddRenderPasses(ScriptableRenderer renderer, ref RenderingData renderingData)
        {
            if (passMaterial == null)
            {
                Debug.LogWarningFormat("Missing Post Processing effect Material. {0} Fullscreen pass will not execute. Check for missing reference in the assigned renderer.", GetType().Name);
                return;
            }

            fullScreenPass.Setup(SetupPassData, downsample, renderingData);

            renderer.EnqueuePass(fullScreenPass);
        }

        /// <inheritdoc/>
        protected override void Dispose(bool disposing)
        {
            fullScreenPass.Dispose();
        }

        void SetupPassData(UniversalBlurPass.PassData passData)
        {
            passData.effectMaterial = passMaterial;
            passData.intensity = intensity;
            passData.passIndex = passIndex;
            passData.requiresColor = requiresColor;
            passData.profilingSampler ??= new ProfilingSampler("FullScreenPassRendererFeature");
            passData.scale = scale;
            passData.iterations = iterations;
            passData.disableInSceneView = disableInSceneView;
        }
    }
}
```