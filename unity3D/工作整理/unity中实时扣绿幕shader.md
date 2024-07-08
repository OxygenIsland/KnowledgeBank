主要的思想：使用当前像素颜色与需要抠掉的颜色相减作比较，然后与一个指定的阈值比较以决定是否将其显示出来；
```csharp
Shader "Unlit/ChromaKey"
{
    Properties
    {
        _MainTex ("Texture", 2D) = "white" {}  // 主要的纹理贴图
        _KeyColor("KeyColor", Color) = (0,1,0,0) // 用于抠像的关键颜色，默认是绿色
        _TintColor("TintColor", Color) = (1,1,1,1)  // 着色器颜色
        _ColorCutoff("Cutoff", Range(0, 1)) = 0.2 // 颜色截止值
        _ColorFeathering("ColorFeathering", Range(0, 1)) = 0.33  // 颜色羽化程度
        _MaskFeathering("MaskFeathering", Range(0, 1)) = 1  // 遮罩羽化程度
        _Sharpening("Sharpening", Range(0, 1)) = 0.5  // 锐化程度

        _Despill("DespillStrength", Range(0, 1)) = 1  // 去溢色强度
        _DespillLuminanceAdd("DespillLuminanceAdd", Range(0, 1)) = 0.2  // 去溢色亮度增加值
    }
    SubShader
    {
        Tags
        {
            // "RenderPipeline"="HDRenderPipeline"
            // "RenderType"="HDUnlitShader"
            "Queue" = "Transparent+1"  // 渲染队列，透明对象稍后渲染
        }

        Blend SrcAlpha OneMinusSrcAlpha  // 混合模式
        ZWrite Off  // 关闭深度写入
        cull off  // 关闭面剔除

        Pass
        {
            CGPROGRAM

            #pragma vertex vert
            #pragma fragment frag

            #include "UnityCG.cginc"

            struct appdata
            {
                float4 vertex : POSITION;
                float2 uv : TEXCOORD0;
            };

            struct v2f
            {
                float2 uv : TEXCOORD0;
                float4 vertex : SV_POSITION;
            };

			// 这些结构体和变量用于在顶点着色器和片段着色器之间传递数据。
            sampler2D _MainTex;
            float4 _MainTex_TexelSize;
            float4 _MainTex_ST;
            float4 _KeyColor;
            float4 _TintColor;
            float _ColorCutoff;
            float _ColorFeathering;
            float _MaskFeathering;
            float _Sharpening;
            float _Despill;
            float _DespillLuminanceAdd;

            // Utility functions -----------用于颜色转换和颜色比较，用于判断一个像素的颜色是否接近关键颜色。
            float rgb2y(float3 c) 
            {
                return (0.299*c.r + 0.587*c.g + 0.114*c.b);
            }
			
            float rgb2cb(float3 c) 
            {
                return (0.5 + -0.168736*c.r - 0.331264*c.g + 0.5*c.b);
            }

            float rgb2cr(float3 c) 
            {
                return (0.5 + 0.5*c.r - 0.418688*c.g - 0.081312*c.b);
            }

			//判断颜色在 YCbCr 色彩空间中的距离，以用于色度键处理。该函数的主要功能是根据给定的阈值，确定两个颜色（一个是像素颜色，另一个是键颜色）在色度空间上的相似度，并返回一个归一化的值。
            float colorclose(float Cb_p, float Cr_p, float Cb_key, float Cr_key, float tola, float tolb)
            {
                float temp = (Cb_key-Cb_p)*(Cb_key-Cb_p)+(Cr_key-Cr_p)*(Cr_key-Cr_p);
                float tola2 = tola*tola;
                float tolb2 = tolb*tolb;
                //如果距离平方小于内层阈值平方，返回 0，表示完全匹配：
                if (temp < tola2) return (0);
                // 如果距离平方在内层阈值和外层阈值之间，返回归一化值，表示部分匹配：
                if (temp < tolb2) return (temp-tola2)/(tolb2-tola2);
                //如果距离平方大于外层阈值平方，返回 1，表示完全不匹配：
                return (1);
            }

			//从给定的纹理中获取颜色，并通过色度键检测该颜色与键颜色的相似度。该函数的目的是生成一个掩码值，用于进一步的图像处理，例如透明度调整。
            float maskedTex2D(sampler2D tex, float2 uv)
            {
	            //采样颜色
                float4 color = tex2D(tex, uv);
                
                // Chroma key to CYK conversion
                float key_cb = rgb2cb(_KeyColor.rgb);
                float key_cr = rgb2cr(_KeyColor.rgb);
                float pix_cb = rgb2cb(color.rgb);
                float pix_cr = rgb2cr(color.rgb);

                return colorclose(pix_cb, pix_cr, key_cb, key_cr, _ColorCutoff, _ColorFeathering);
            }

            //-------------------------
			// 顶点着色器将顶点转换到裁剪空间并传递纹理坐标。
            v2f vert (appdata v)
            {
                v2f o;
                o.vertex = UnityObjectToClipPos(v.vertex);
                o.uv = TRANSFORM_TEX(v.uv, _MainTex);
                return o;
            }
			// 片段着色器对每个像素进行颜色键处理，包括颜色比较、羽化、去溢色等操作，最后输出处理后的颜色和遮罩
            float4 frag (v2f i) : SV_Target
            {
                // Get pixel width
                float2 pixelWidth = float2(1.0 / _MainTex_TexelSize.z, 0);
                float2 pixelHeight = float2(0, 1.0 / _MainTex_TexelSize.w);

                // Unmodified MainTex
                float4 color = tex2D(_MainTex, i.uv);

                // Unfeathered mask
                float mask = maskedTex2D(_MainTex, i.uv);

                // Feathering & smoothing
                float c = mask;
                float r = maskedTex2D(_MainTex, i.uv + pixelWidth);
                float l = maskedTex2D(_MainTex, i.uv - pixelWidth);
                float d = maskedTex2D(_MainTex, i.uv + pixelHeight); 
                float u = maskedTex2D(_MainTex, i.uv - pixelHeight);
                float rd = maskedTex2D(_MainTex, i.uv + pixelWidth + pixelHeight) * .707;
                float dl = maskedTex2D(_MainTex, i.uv - pixelWidth + pixelHeight) * .707;
                float lu = maskedTex2D(_MainTex, i.uv - pixelHeight - pixelWidth) * .707;
                float ur = maskedTex2D(_MainTex, i.uv + pixelWidth - pixelHeight) * .707;
                float blurContribution = (r + l + d + u + rd + dl + lu + ur + c) * 0.12774655;
                float smoothedMask = smoothstep(_Sharpening, 1, lerp(c, blurContribution, _MaskFeathering));
                float4 result = color * smoothedMask;

                // Despill
                float v = (2*result.b+result.r)/4;
                if(result.g > v) result.g = lerp(result.g, v, _Despill);
                float4 dif = (color - result);
                float desaturatedDif = rgb2y(dif.xyz);
                result += lerp(0, desaturatedDif, _DespillLuminanceAdd);
                
                return float4(result.xyz, smoothedMask) * _TintColor;
            }
            ENDCG
        }
    }
}

```

### 颜色转换，RGB 转 YCbCr
YCbCr 色彩空间是一种用于数字图像和视频处理的颜色表示方法。它通过分离亮度（Y）和色度（Cb 和 Cr）信息，使得图像和视频压缩更加高效。这种色彩空间在视频压缩格式（如 MPEG、JPEG）中非常常见。
1. **Y（Luminance 亮度）**:
    - 表示图像的亮度信息。
    - 包含图像的黑白信息，是灰度值。
    - 人眼对亮度变化更为敏感，因此保留更多细节。
2. **Cb（Chrominance Blue-difference 蓝色色度）**:
    - 表示颜色与蓝色分量的差异。
    - 包含色度信息，表示颜色的饱和度和色调。
3. **Cr（Chrominance Red-difference 红色色度）**:
    - 表示颜色与红色分量的差异。
    - 包含色度信息，与 Cb 一样，表示颜色的饱和度和色调。
#### 转换公式

YCbCr 色彩空间可以从 RGB 色彩空间转换而来，其转换公式如下：
- $Y = 0.299 \cdot R + 0.587 \cdot G + 0.114 \cdot B$
- $Cb = 0.5 \cdot (B - Y)$
- $Cr = 0.5 \cdot (R - Y)$
对应的逆转换公式为：
- $R = Y + 1.402 \cdot Cr$
- $G = Y - 0.344136 \cdot Cb - 0.714136 \cdot Cr$
- $B = Y + 1.772 \cdot Cb$
#### 优势
1. **压缩效率**:
    - 人眼对亮度的敏感度高于对色度的敏感度。因此，在压缩图像或视频时，可以在保留较高亮度分辨率的同时，以较低的分辨率表示色度。
    - 例如，在 JPEG 压缩中，通常采用 4:2:0 取样，这意味着色度的水平和垂直分辨率都是亮度的一半，从而大大减少了数据量。
2. **兼容性**:
    - YCbCr 色彩空间在视频信号处理中具有广泛的兼容性，适用于各种显示设备和压缩标准。
3. **处理方便**:
    - 分离的亮度和色度信息可以更方便地进行图像处理操作，如颜色调整、滤波等。
#### 应用
- **视频压缩**:
    - 常见的视频压缩标准，如 MPEG、H.264 等，都使用 YCbCr 色彩空间。
- **图像压缩**:
    - JPEG 图像压缩标准使用 YCbCr 色彩空间，以实现高效的图像存储。
- **图像处理**:
    - 许多图像处理算法，如色度键、白平衡调整等，都基于 YCbCr 色彩空间进行处理。
总之，YCbCr 色彩空间通过将亮度和色度信息分离，使得图像和视频处理更加高效，是数字图像和视频处理中不可或缺的工具。
```csharp
float rgb2y(float3 c) 
{
    return (0.299*c.r + 0.587*c.g + 0.114*c.b);
}
```
这个函数 `rgb2y` 用于将 RGB 颜色转换为亮度（Y 值），这是图像处理和色彩转换中的一个常见操作。具体来说，这个函数计算的是灰度值，它基于人眼对不同颜色的感知敏感度。

这些权重值（0.299、0.587、0.114）反映了人眼对红、绿、蓝三种颜色的不同敏感度。人眼对绿色最敏感，所以绿色的权重最大（0.587），其次是红色（0.299），对蓝色最不敏感，所以蓝色的权重最小（0.114）。

