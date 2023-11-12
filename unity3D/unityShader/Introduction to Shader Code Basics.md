unity Shader 的主要结构如下所示：
![[Screen Shot 2023-11-12 at 10.37.55.png|475]]
Shader "" 引号中是该 Shader 的名字，也可以采用目录式命名，方便管理，下图展示的是 Properties 中常见的属性变量，以及在 unity 面板中的样式
![[Screen Shot 2023-11-12 at 10.36.38.png|475]] ![[Screen Shot 2023-11-12 at 10.41.42.png|475]]
接下来看 SubShader 的部分，SubShader 可以包含多个 Pass{}，一个 Pass{}就相当于一个完整的 GPU 渲染管线。
![[Screen Shot 2023-11-12 at 11.37.21.png|600]]
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
//注意：
//float4 是32位的，主要用于坐标点
//half 是16位的，主要用于uv和大部分向量
//fixed是8位的，主要用于颜色
```