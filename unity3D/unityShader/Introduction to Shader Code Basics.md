unity Shader 的主要结构如下所示：
![[Screen Shot 2023-11-12 at 10.37.55.png|475]]
Shader "" 引号中是该 Shader 的名字，也可以采用目录式命名，方便管理，下图展示的是 Properties 中常见的属性变量，以及在 unity 面板中的样式
![[Screen Shot 2023-11-12 at 10.36.38.png|475]] ![[Screen Shot 2023-11-12 at 10.41.42.png|475]]
接下来看 SubShader 的部分，SubShader 可以包含多个 Pass{}，一个 Pass{}就相当于一个完整的 GPU 渲染管线。

要访问不同的顶点数据，您需要自己声明顶点结构，或将输入参数添加到顶点着色器。顶点数据由Cg / HLSL语义标识，并且必须来自以下列表：
- POSITION是顶点位置，通常是afloat3或float4。
- NORMAL是顶点法线，通常是float3。
- TEXCOORD0是所述第一 UV 坐标，典型的float2，float3或 float4。
- TEXCOORD1，TEXCOORD2并且TEXCOORD3是第2，第3和第4个UV坐标。
- TANGENT是切线向量（用于法线贴图），通常为float4。
- COLOR是每个顶点的颜色，通常是float4。

```csharp
 Shsder “01MiniShader”
 {
	 Properties
	 {
		 _MainTex("MainTex",2D) = "black"{}
		 _Float("Float",Float) = 0.0
		 _Range("Range",Range(0.0,1.0)) = 0.0
		 _Vector("Vector",Vector) = (1,1,1,1)
		 _Color("Color",Color) = (0.5,0.5,0.5,0.5) 
	 }
 }
 SubShader
 {
	 Pass
	 {
		 CGPROGRAM //CGPROGRAM 和 ENDCG 是一对关键字，表示两个关键字之间的代码是 unity CG 的代码。
		 #pragma vertex vert //指定一个顶点shader，名字叫做 vert
		 #pragma fragment frag //指定一个片元shader
		 #include "UnityCG.cginc"//这个头文件包含丰富的函数和内置变量可以调用
		 struct appdata//定义一个结构体，从cpu中拿数据
		 {
			 float4 vertex : POSITION;//模型顶点坐标
			 float2 uv : TEXCOORD0;//第一套uv
			 float3 normal : NORMSL;//法线
			 float4 color : COLOR;//顶点色
		 }
		 struct v2f//定义顶点shader输出的结构体
		 {
			 float4 pos : SV_POSITION;//输出的顶点坐标
			 float2 uv : TEXCOORD0;//储存器
		 }
		 float4 _Color;//命名必须和properties里的名称一样才会有动态链接
		 sampler2D _MainTex;
		 float4 _MainTex_ST;//对应纹理贴图面板的参数
		 v2f vert(appdata v)//顶点shader
		 {
			 v2f o;
			 float4 pos_world = mul(unity_ObjectToWorld, v.vertex);//模型空间转世界空间，mul代表矩阵乘法的意思
			 float4 pos_view = mul(UNITY_MATRIX_V, pos_world);//世界空间转相机空间
			 float4 pos_clip = mul(UNITY_MATRIX_P, pos_view);//转到剪裁空间
			 o.pose = pos_clip;
			 o.uv = v.uv * _MainTex_ST.xy + _MainTex_ST.zw;//xy分量对uv进行缩放，zw分量对uv进行偏移
			 return o;
		 }
		 half4 frag(v2f i) : SV_Target//片元shader输出的是一个颜色值，所以类型为half4
		 {
		 fixed4 col = tex2D(_MainTex,i.uv )
			 return col;//直接输出一个绿色
		 }
		 ENDCG
	 }
 }
```
**注意：**
	float 4 是 32 位的，主要用于坐标点
	half 是 16 位的，主要用于 uv 和大部分向量
	fixed 是 8 位的，主要用于颜色
