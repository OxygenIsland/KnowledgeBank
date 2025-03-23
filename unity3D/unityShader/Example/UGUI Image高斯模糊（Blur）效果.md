---
title: "[[UGUI Image高斯模糊（Blur）效果]]"
type: Literature
status: ing
Creation Date: 2025-03-23 14:42
tags:
---
```csharp
Shader "Custom/MaskedUIBlur" {
    Properties {
	    //模糊强度，控制采样范围
        _Size ("Blur", Range(0, 30)) = 1
        //遮罩纹理，决定模糊效果的可见区域（Alpha 通道控制）。
        [HideInInspector] _MainTex ("Masking Texture", 2D) = "white" {}
        //调整模糊结果的颜色（叠加和乘法色调）
        _AdditiveColor ("Additive Tint color", Color) = (0, 0, 0, 0)
        _MultiplyColor ("Multiply Tint color", Color) = (1, 1, 1, 1)
    }

    Category {
        // W设置为 `"Queue"="Transparent"`，确保在透明阶段渲染，避免遮挡其他物体。
        Tags { "Queue"="Transparent" "IgnoreProjector"="True" "RenderType"="Opaque" }
        SubShader
        {
            // Horizontal blur，GrabPass 抓取屏幕内容到 `_HBlur` 纹理。
            GrabPass
            {
                "_HBlur"
            }
            /*
            ZTest Off
            Blend SrcAlpha OneMinusSrcAlpha
            */
			//- 关闭剔除（`Cull Off`）、光照（`Lighting Off`）和深度写入（`ZWrite Off`），适配 UI 渲染需求。
            Cull Off
            Lighting Off
            ZWrite Off
            ZTest [unity_GUIZTestMode]
            //支持透明度混合
            Blend SrcAlpha OneMinusSrcAlpha

            Pass
            {          
                CGPROGRAM
                #pragma vertex vert
                #pragma fragment frag
                #pragma fragmentoption ARB_precision_hint_fastest
                #include "UnityCG.cginc"

                struct appdata_t {
                    float4 vertex : POSITION;
                    float2 texcoord : TEXCOORD0;
                };

                struct v2f {
                    float4 vertex : POSITION;
                    float4 uvgrab : TEXCOORD0;
                    float2 uvmain : TEXCOORD1;
                };

                sampler2D _MainTex;
                float4 _MainTex_ST;

                v2f vert (appdata_t v)
                {
                    v2f o;
                    o.vertex = UnityObjectToClipPos(v.vertex);

                    #if UNITY_UV_STARTS_AT_TOP
                    float scale = -1.0;
                    #else
                    float scale = 1.0;
                    #endif

                    o.uvgrab.xy = (float2(o.vertex.x, o.vertex.y * scale) + o.vertex.w) * 0.5;
                    o.uvgrab.zw = o.vertex.zw;

                    o.uvmain = TRANSFORM_TEX(v.texcoord, _MainTex);
                    return o;
                }

                sampler2D _HBlur;
                float4 _HBlur_TexelSize;
                float _Size;
                float4 _AdditiveColor;
                float4 _MultiplyColor;

                half4 frag( v2f i ) : COLOR
                {   
                    half4 sum = half4(0,0,0,0);

                    #define GRABPIXEL(weight,kernelx) tex2Dproj( _HBlur, UNITY_PROJ_COORD(float4(i.uvgrab.x + _HBlur_TexelSize.x * kernelx * _Size, i.uvgrab.y, i.uvgrab.z, i.uvgrab.w))) * weight

                    sum += GRABPIXEL(0.05, -4.0);
                    sum += GRABPIXEL(0.09, -3.0);
                    sum += GRABPIXEL(0.12, -2.0);
                    sum += GRABPIXEL(0.15, -1.0);
                    sum += GRABPIXEL(0.18,  0.0);
                    sum += GRABPIXEL(0.15, +1.0);
                    sum += GRABPIXEL(0.12, +2.0);
                    sum += GRABPIXEL(0.09, +3.0);
                    sum += GRABPIXEL(0.05, +4.0);


                    half4 result = half4(sum.r * _MultiplyColor.r + _AdditiveColor.r, 
                                        sum.g * _MultiplyColor.g + _AdditiveColor.g, 
                                        sum.b * _MultiplyColor.b + _AdditiveColor.b, 
                                        tex2D(_MainTex, i.uvmain).a);
                    return result;
                }
                ENDCG
            }

            // Vertical blur
            GrabPass
            {
                "_VBlur"
            }

            Pass
            {          
                CGPROGRAM
                #pragma vertex vert
                #pragma fragment frag
                #pragma fragmentoption ARB_precision_hint_fastest
                #include "UnityCG.cginc"

                struct appdata_t {
                    float4 vertex : POSITION;
                    float2 texcoord: TEXCOORD0;
                };

                struct v2f {
                    float4 vertex : POSITION;
                    float4 uvgrab : TEXCOORD0;
                    float2 uvmain : TEXCOORD1;
                };

                sampler2D _MainTex;
                float4 _MainTex_ST;

                v2f vert (appdata_t v) {
                    v2f o;
                    o.vertex = UnityObjectToClipPos(v.vertex);

                    #if UNITY_UV_STARTS_AT_TOP
                    float scale = -1.0;
                    #else
                    float scale = 1.0;
                    #endif

                    o.uvgrab.xy = (float2(o.vertex.x, o.vertex.y * scale) + o.vertex.w) * 0.5;
                    o.uvgrab.zw = o.vertex.zw;

                    o.uvmain = TRANSFORM_TEX(v.texcoord, _MainTex);

                    return o;
                }

                sampler2D _VBlur;
                float4 _VBlur_TexelSize;
                float _Size;
                float4 _AdditiveColor;
                float4 _MultiplyColor;

                half4 frag( v2f i ) : COLOR
                {
                    half4 sum = half4(0,0,0,0);

                    #define GRABPIXEL(weight,kernely) tex2Dproj( _VBlur, UNITY_PROJ_COORD(float4(i.uvgrab.x, i.uvgrab.y + _VBlur_TexelSize.y * kernely * _Size, i.uvgrab.z, i.uvgrab.w))) * weight

                    sum += GRABPIXEL(0.05, -4.0);
                    sum += GRABPIXEL(0.09, -3.0);
                    sum += GRABPIXEL(0.12, -2.0);
                    sum += GRABPIXEL(0.15, -1.0);
                    sum += GRABPIXEL(0.18,  0.0);
                    sum += GRABPIXEL(0.15, +1.0);
                    sum += GRABPIXEL(0.12, +2.0);
                    sum += GRABPIXEL(0.09, +3.0);
                    sum += GRABPIXEL(0.05, +4.0);

                    half4 result = half4(sum.r * _MultiplyColor.r + _AdditiveColor.r, 
                                        sum.g * _MultiplyColor.g + _AdditiveColor.g, 
                                        sum.b * _MultiplyColor.b + _AdditiveColor.b, 
                                        tex2D(_MainTex, i.uvmain).a);
                    return result;
                }
                ENDCG
            }
        }
    }
}

```