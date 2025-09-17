---
title: "[[GPU Instance]]"
type: Permanent
status: done
Creation Date: 2025-09-17 19:17
tags:
---
GPU instancing is a graphics technique available in Unity to draw lots of the same mesh and material quickly.
它的工作原理是对多个具有相同网格的对象同时发出一个draw call。CPU收集所有对象的转换信息和材质属性，并将它们保存到数组中，然后一次发给GPU，GPU遍历所有的数据并按照提供的顺序将它们一一呈现。限制条件是它一次只能绘制使用相同网格和材质的物体。
>A low number of draw calls is usually a sign of a well-performing game. For each new draw call, the GPU has to do a context switch, which is _expensive_.

在合适的情况下，GPU Instance可以允许你绘制上百万个网格。为了简化我们得开发流程，Unity其实会自动帮我们做一些合批的处理，但是需要遵循一些必要的条件，比如所有的网格需要使用相同的材质，并且GPU Instancing需要勾选，我们的Shader能够支持实例化，还有一点需要注意的是Unity自动合批并不支持Skin mesh renderer。

虽然Unity自动合批简化了我们的开发工作，但是它需要我们去遵守非常苛刻的条件，而且大量的GameObjects和Transforms组件本身也会造成非常大的开销。

针对上面的问题，Unity为我们提供了扩展的接口，利用这个接口我们可以定制自己的批处理方案。扩展的接口有两个，分别是DrawMeshInstanced()和DrawMeshInstancedIndirect()。

## DrawMeshInstanced()

DrawMeshInstanced()是Unity提供的扩展接口之一，它一帧内最多可以绘制1023个网格。使用这个接口来绘制大量移动不明显或者只在shader中做顶点动画的物体（比如树，草）来说是一个非常好的方案。它允许你轻松地将网格推到GPU上，使用MaterialPropertyBlocks自定义它们，并避免GameObjects的沉重开销。另外，Unity在判断时候可实例化这个对象的时候只需要花费很小的开销，如果实例化失败也会抛出一个错误，但并不会削弱性能。主要的缺点就是如果移动这些物体，往往需要执行大量的循环语句，这可能会造成性能的下降。

```csharp
public class DrawMeshInstancedDemo : MonoBehaviour {
    // How many meshes to draw.
    public int population;
    // Range to draw meshes within.
    public float range;

    // Material to use for drawing the meshes.
    public Material material;
  
    private Matrix4x4[] matrices;
    private MaterialPropertyBlock block;

    private Mesh mesh;

    private void Setup() {
        Mesh mesh = CreateQuad();
        this.mesh = mesh;

        matrices = new Matrix4x4[population];
        Vector4[] colors = new Vector4[population];

        block = new MaterialPropertyBlock();

        for (int i = 0; i < population; i++) {
            // Build matrix.
            Vector3 position = new Vector3(Random.Range(-range, range), Random.Range(-range, range), Random.Range(-range, range));
            Quaternion rotation = Quaternion.Euler(Random.Range(-180, 180), Random.Range(-180, 180), Random.Range(-180, 180));
            Vector3 scale = Vector3.one;

            mat = Matrix4x4.TRS(position, rotation, scale);

            matrices[i] = mat;

            colors[i] = Color.Lerp(Color.red, Color.blue, Random.value);
        }

        // Custom shader needed to read these!!
        block.SetVectorArray("_Colors", colors);
    }

    private Mesh CreateQuad(float width = 1f, float height = 1f) {
        // Create a quad mesh.
        // See source for implementation.
    }

    private void Start() {
        Setup();
    }

    private void Update() {
        // Draw a bunch of meshes each frame.
        Graphics.DrawMeshInstanced(mesh, 0, material, matrices, population, block);
    }
}
```

本质上，我们用表示Transform(位置，旋转，缩放)的矩阵填充一个大数组，然后将该数组传递给graphics.drawmeshinstance()，==它将在着色器中自动分配这些矩阵==(假设Shader支持实例化)。  
在shader中，你可以通过MaterialPropertyBlocks来获取instanceID，从而对每个网格进行定制化的修改(比如说颜色，参见color array)，但你可能需要使用一个自定义着色器:
>_A custom shader is only required if you’re customizing per-mesh properties._

```shader
Shader "Custom/InstancedColor" {
    SubShader {
        Tags { "RenderType" = "Opaque" }

        Pass {
            CGPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            #pragma multi_compile_instancing

            #include "UnityCG.cginc"

            struct appdata_t {
                float4 vertex   : POSITION;
                float4 color    : COLOR;
                UNITY_VERTEX_INPUT_INSTANCE_ID
            };

            struct v2f {
                float4 vertex   : SV_POSITION;
                fixed4 color    : COLOR;
            }; 

            float4 _Colors[1023];   // Max instanced batch size.

            v2f vert(appdata_t i, uint instanceID: SV_InstanceID) {
                // Allow instancing.
                UNITY_SETUP_INSTANCE_ID(i);

                v2f o;
                o.vertex = UnityObjectToClipPos(i.vertex);
                o.color = float4(1, 1, 1, 1);

                // If instancing on (it should be) assign per-instance color.
                #ifdef UNITY_INSTANCING_ENABLED
                    o.color = _Colors[instanceID];
                #endif

                return o;
            }

            fixed4 frag(v2f i) : SV_Target {
                return i.color;
            }

            ENDCG
        }
    }
}
```

<figure style="text-align: center;"> 
<img src="unity3D/Graphics/attachments/Pasted image 20250917194440.png" alt="一张可爱小猫的图片" style="width: 600px; height: auto;"> 
<figcaption>1022 meshes with the standard shader</figcaption> 
</figure>
<figure style="text-align: center;"> 
<img src="unity3D/Graphics/attachments/Pasted image 20250917195204.png" alt="一张可爱小猫的图片" style="width: 600px; height: auto;"> 
<figcaption>1022 meshes with a custom shader, and per-mesh colors</figcaption> 
</figure>
>Note that shadows are missing on the colored version. This is because we’re using a custom shader to apply the colors which doesn’t have a shadow pass. Have a look at [this](https://docs.unity3d.com/Manual/SL-VertexFragmentShaderExamples.html) for some examples of adding shadow casting/receiving to a custom shader.

>If setting up a random array in the shader feels awkward, that’s because it is. There doesn’t seem to be a way to get Unity to set up an array for you and index the color automatically. If we were using individual game objects, we could do something like [this](https://docs.unity3d.com/540/Documentation/Manual/GPUInstancing.html). You could probably get this to work by digging into the shader source and having a look at what names Unity uses for the arrays, but that’s pretty convoluted for no good reason.



## DrawMeshInstancedIndirect()
drawmeshinstance()其实是对drawmeshinstanceindirect()的一种包装。您可以在后者中实现与前者相同的一切(反之亦然，不过相对复杂一些)。drawmeshinstance()相对来说是更友好的绘制网格的方式，因为它不需要我们跟GPU打交道。

但是相对的，一些非常美妙的用法在也在抽象包装中丢失了。首先，DrawMeshInstancedIndirect()允许你绕过1023网格的限制，并在单个批次中绘制尽可能多的网格(1023网格限制似乎是因为MaterialPropertyBlock的原因)。但最主要的好处是你可以把所有的工作都转移到GPU上。使用drawmeshinstance()， Unity必须在每一帧将网格矩阵数组上传到GPU，而drawmeshinstanceindirect()则在GPU上无限创建并存储数据。这也意味着使用基于gpu的结构来存储数据，主要是ComputeBuffers，这听起来有点不靠谱，但结果是非常棒的，它就像给我们打开了一扇新的门，一些简单的大规模的并行计算我们可以使用[Compute shader](https://zhida.zhihu.com/search?content_id=177882349&content_type=Article&match_order=1&q=Compute+shader&zhida_source=entity)来完成。

```csharp
public class DrawMeshInstancedIndirectDemo : MonoBehaviour {
    public int population;
    public float range;

    public Material material;

    private ComputeBuffer meshPropertiesBuffer;
    private ComputeBuffer argsBuffer;

    private Mesh mesh;
    private Bounds bounds;

    // Mesh Properties struct to be read from the GPU.
    // Size() is a convenience funciton which returns the stride of the struct.
    private struct MeshProperties {
        public Matrix4x4 mat;
        public Vector4 color;

        public static int Size() {
            return
                sizeof(float) * 4 * 4 + // matrix;
                sizeof(float) * 4;      // color;
        }
    }

    private void Setup() {
        Mesh mesh = CreateQuad();
        this.mesh = mesh;

        // Boundary surrounding the meshes we will be drawing.  Used for occlusion.
        bounds = new Bounds(transform.position, Vector3.one * (range + 1));

        InitializeBuffers();
    }

    private void InitializeBuffers() {
        // Argument buffer used by DrawMeshInstancedIndirect.
        uint[] args = new uint[5] { 0, 0, 0, 0, 0 };
        // Arguments for drawing mesh.
        // 0 == number of triangle indices, 1 == population, others are only relevant if drawing submeshes.
        args[0] = (uint)mesh.GetIndexCount(0);
        args[1] = (uint)population;
        args[2] = (uint)mesh.GetIndexStart(0);
        args[3] = (uint)mesh.GetBaseVertex(0);
        argsBuffer = new ComputeBuffer(1, args.Length * sizeof(uint), ComputeBufferType.IndirectArguments);
        argsBuffer.SetData(args);

        // Initialize buffer with the given population.
        MeshProperties[] properties = new MeshProperties[population];
        for (int i = 0; i < population; i++) {
            MeshProperties props = new MeshProperties();
            Vector3 position = new Vector3(Random.Range(-range, range), Random.Range(-range, range), Random.Range(-range, range));
            Quaternion rotation = Quaternion.Euler(Random.Range(-180, 180), Random.Range(-180, 180), Random.Range(-180, 180));
            Vector3 scale = Vector3.one;

            props.mat = Matrix4x4.TRS(position, rotation, scale);
            props.color = Color.Lerp(Color.red, Color.blue, Random.value);

            properties[i] = props;
        }

        meshPropertiesBuffer = new ComputeBuffer(population, MeshProperties.Size());
        meshPropertiesBuffer.SetData(properties);
        material.SetBuffer("_Properties", meshPropertiesBuffer);
    }

    private Mesh CreateQuad(float width = 1f, float height = 1f) {
        ...
    }

    private void Start() {
        Setup();
    }

    private void Update() {
        Graphics.DrawMeshInstancedIndirect(mesh, 0, material, bounds, argsBuffer);
    }

    private void OnDisable() {
        // Release gracefully.
        if (meshPropertiesBuffer != null) {
            meshPropertiesBuffer.Release();
        }
        meshPropertiesBuffer = null;

        if (argsBuffer != null) {
            argsBuffer.Release();
        }
        argsBuffer = null;
    }
}
```

>The `bounds` parameter of `DrawMeshInstancedIndirect()` is used for determining whether the mesh is in view and culling it. The documentation states `Meshes are not further culled by the view frustum or baked occluders ...` which gave me the impression that culling was simply disabled for all meshes drawn with DrawMeshInstanced/Indirect, but this is not so. Unity will cull all the instanced meshes if the provided mesh bounds are not in view. It will not, however, cull individual instanced meshes – you’ll have to calculate this yourself if you find it necessary.

```shader
Shader "Custom/InstancedIndirectColor" {
    SubShader {
        Tags { "RenderType" = "Opaque" }

        Pass {
            CGPROGRAM
            #pragma vertex vert
            #pragma fragment frag

            #include "UnityCG.cginc"

            struct appdata_t {
                float4 vertex   : POSITION;
                float4 color    : COLOR;
            };

            struct v2f {
                float4 vertex   : SV_POSITION;
                fixed4 color    : COLOR;
            }; 

            struct MeshProperties {
                float4x4 mat;
                float4 color;
            };

            StructuredBuffer<MeshProperties> _Properties;

            v2f vert(appdata_t i, uint instanceID: SV_InstanceID) {
                v2f o;

                float4 pos = mul(_Properties[instanceID].mat, i.vertex);
                o.vertex = UnityObjectToClipPos(pos);
                o.color = _Properties[instanceID].color;

                return o;
            }

            fixed4 frag(v2f i) : SV_Target {
                return i.color;
            }

            ENDCG
        }
    }
}
```

>The struct for your `StructuredBuffer` **must** be byte-wise identical throughout shader/compute shader/script or you’ll see bugginess. These structures are only matched up between script and shader by reading bytes.

<figure style="text-align: center;"> 
<img src="unity3D/Graphics/attachments/Pasted image 20250917201203.png" alt="一张可爱小猫的图片" style="width: 600px; height: auto;"> 
<figcaption>1022 meshes drawn with `DrawMeshInstancedIndirect`</figcaption> 
</figure>

这里的一个关键区别是，使用drawmeshinstance()，我们给了Unity一个矩阵数组，并让它在我们使用着色器之前自动计算出顶点位置。在这里，我们更直接地将矩阵推到GPU，并自己应用转换。着色器实例代码被大幅削减，我们在渲染中节省了大约一毫秒的时间。但需要注意的是，这个数字很大程度上受到游戏其余部分的影响。在我们的基本场景中，没有发生任何事情，带宽和CPU时间是充裕的，所以drawmeshinstanceindirect()的好处可能没有实际应用环境中那么普遍。

1023 个网格的限制也消失了。即使将网格数量增加到 10 万个，对我的系统（Ryzen 1700、1080Ti）也几乎没有影响：
<figure style="text-align: center;"> 
<img src="unity3D/Graphics/attachments/Pasted image 20250917201754.png" alt="一张可爱小猫的图片" style="width: 600px; height: auto;"> 
<figcaption>100k meshes drawn with `DrawMeshInstancedIndirect`</figcaption> 
</figure>
###  使用Compute Shader计算位移
现在我们使用了DrawMeshInstancedIndirect()，我们可以添加一些网格位移但又不会对性能造成影响。[[Compute Shader]]是运行在GPU上的特殊程序，允许你利用图形设备的巨大并行能力来处理非图形代码。[here](http://kylehalladay.com/blog/tutorial/2014/06/27/Compute-Shaders-Are-Nifty.html) is a good blog post talking about them, which covers everything better than I could.

Here’s a compute shader which moves our meshes based on some “pusher”:
```
#pragma kernel CSMain

struct MeshProperties {
    float4x4 mat;
    float4 color;
};

RWStructuredBuffer<MeshProperties> _Properties;
float3 _PusherPosition;

// We used to just be able to use (1, 1, 1) threads for whatever population (not sure the old limit), but a Unity update imposed a thread limit of 65535.  Now, to populations above that, we need to be more granular with our threads.

[numthreads(64,1,1)]
void CSMain (uint3 id : SV_DispatchThreadID) {
    float4x4 mat = _Properties[id.x].mat;
    // In a transform matrix, the position (translation) vector is the last column.
    float3 position = float3(mat[0][3], mat[1][3], mat[2][3]);

    float dist = distance(position, _PusherPosition);
    // Scale and reverse distance so that we get a value which fades as it gets further away.
    // Max distance is 5.0.
    dist = 5.0 - clamp(0.0, 5.0, dist);

    // Get the vector from the pusher to the position, and scale it.
    float3 push = normalize(position - _PusherPosition) * dist;
    // Create a new translation matrix which represents a move in a direction.
    float4x4 translation = float4x4(
        1, 0, 0, push.x,
        0, 1, 0, push.y,
        0, 0, 1, push.z,
        0, 0, 0, 1
    );

    // Apply translation to existing matrix, which will be read in the shader.
    _Properties[id.x].mat = mul(translation, mat);
}
```

你可能也想知道你是否可以在常规着色器中完成同样的事情，通过改变StructuredBuffer为RWStructuredBuffer并做一个类似的计算。提到这个问题，我们要知道==普通shader都是针对单个顶点或者片元进行工作的==,所以也可以取得同样的效果(移动单个网格)你必须要么设置一些标志来标记网格被移动,或者将逐网格方法改为逐顶点方法，可能会得到不同的结果。
Of course, we need to make a couple additions to our script to actually run our compute shader. Where `compute` is our compute shader and `pusher` is the object we want to use to push:
```csharp
public class DrawMeshInstancedIndirectDemo : MonoBehaviour {
    public int population;
    public float range;

    public Material material;
    public ComputeShader compute;
    public Transform pusher;

    private ComputeBuffer meshPropertiesBuffer;
    private ComputeBuffer argsBuffer;

    private Mesh mesh;
    private Bounds bounds;

    ...

    private void InitializeBuffers() {
        int kernel = compute.FindKernel("CSMain");

        // Argument buffer used by DrawMeshInstancedIndirect.
        uint[] args = new uint[5] { 0, 0, 0, 0, 0 };
        // Arguments for drawing mesh.
        // 0 == number of triangle indices, 1 == population, others are only relevant if drawing submeshes.
        args[0] = (uint)mesh.GetIndexCount(0);
        ...

        meshPropertiesBuffer = new ComputeBuffer(population, MeshProperties.Size());
        meshPropertiesBuffer.SetData(properties);
        compute.SetBuffer(kernel, "_Properties", meshPropertiesBuffer);
        material.SetBuffer("_Properties", meshPropertiesBuffer);
    }

    ...

    private void Update() {
        int kernel = compute.FindKernel("CSMain");

        compute.SetVector("_PusherPosition", pusher.position);
        // We used to just be able to use `population` here, but it looks like a Unity update imposed a thread limit (65535) on my device.
        // This is probably for the best, but we have to do some more calculation.  Divide population by numthreads.x (declared in compute shader).
        compute.Dispatch(kernel, Mathf.CeilToInt(population / 64f), 1, 1);
        Graphics.DrawMeshInstancedIndirect(mesh, 0, material, bounds, argsBuffer);
    }
}
```

<figure style="text-align: center;"> 
<img src="unity3D/Graphics/attachments/2019_compute_movement.gif" style="width: 600px; height: auto;"> 
</figure>