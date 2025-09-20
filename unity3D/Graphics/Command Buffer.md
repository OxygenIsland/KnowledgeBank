---
title: "[[Command Buffer]]"
type: Permanent
status: done
Creation Date: 2025-09-20 13:34
tags:
---
[[1、Verview#5 . Command Buffer|CommandBuffer 是一个包含了渲染命令列表的缓冲区]]，这些命令可以在渲染过程中的特定点被执行。[1](https://www.google.com/url?sa=E&q=https%3A%2F%2Fvertexaisearch.cloud.google.com%2Fgrounding-api-redirect%2FAUZIYQGy9k2_YD7hm7gKsaPpg1tjjCcFwNKVhLPcMuO8dLdkZXMPkkmh0JjgHpwvzH7FEez4f0XCm5aZuHOqkn-C4Arm1SmEFLjZOSg_HWVhYELV2ul_4WqG75hYBjHWZxmU4YIn-YmPKJ-0wFjWosgKOfkehiwXO9xCLj_W4F2F_IJzdoOZRVCZoNS-V2m6-H7Qyv0ft2xYIw%3D%3D) 在unity中，它允许开发人员扩展Unity的渲染管线，实现自定义的渲染效果。之前我也了解过URP 的[[4.URP Renderer Feature|Renderer Feature]] ，这是一个高层级的、结构化的系统，它专门用来在 URP (通用渲染管线) 中管理和注入 CommandBuffer。也就是说CommandBuffer 是比Renderer Feature更底层的工具。

## 核心概念

**延迟执行 (Delayed Execution)**：CommandBuffer 的核心思想是延迟执行。当你调用 CommandBuffer 的方法（例如 DrawRenderer 或 Blit）时，这些命令并不会立即执行，而是被添加到一个队列中。然后，这个队列（即 CommandBuffer）可以在渲染管线的特定事件点被一次性地提交给GPU执行。[2](https://www.google.com/url?sa=E&q=https%3A%2F%2Fvertexaisearch.cloud.google.com%2Fgrounding-api-redirect%2FAUZIYQH9eCPN278ogAE9vU_1TihUfVFa7r32o003rJq2HSCLu-IgM_TfXz4PlnwB5A-pAlvCvurQaiGFFEeuV-lsZoFI98syUshmeeiM9olc7AwEXOsCO_7iR0IhOww81_T5zaPIA0fHIMiDdcPK7UFxkI7jgt06OXeKgtFR5HZ7BsWUKP69PveY8CFiLYe5) 

## CommandBuffer 的工作流程
1. **创建 CommandBuffer**：首先，你需要创建一个 CommandBuffer 的实例。[3](https://www.google.com/url?sa=E&q=https%3A%2F%2Fvertexaisearch.cloud.google.com%2Fgrounding-api-redirect%2FAUZIYQHekAH2WxR9EOXeIqudnd_V2N0i89UrFrySKxnvYldxWP_67TSkzl_blNWYGeVPmrIMYxBr_shNNF1Z8aMbxRZqwCOuQp1L6OUaZYQdCN3_FDZEUiLfuZ5KL4KYwtCsKgyyiCTY-Q-pZHAZaxBY3rTGUv9VTO6GCbFfUYcreQJkkvG-PwPG4EeNj9PeP9-e3Rs%3D) 
    
2. **填充命令**：然后，你可以使用 CommandBuffer 类提供的各种方法向其添加渲染命令。这些命令包括但不限于：
    - 设置渲染目标 (SetRenderTarget)[2](https://www.google.com/url?sa=E&q=https%3A%2F%2Fvertexaisearch.cloud.google.com%2Fgrounding-api-redirect%2FAUZIYQH9eCPN278ogAE9vU_1TihUfVFa7r32o003rJq2HSCLu-IgM_TfXz4PlnwB5A-pAlvCvurQaiGFFEeuV-lsZoFI98syUshmeeiM9olc7AwEXOsCO_7iR0IhOww81_T5zaPIA0fHIMiDdcPK7UFxkI7jgt06OXeKgtFR5HZ7BsWUKP69PveY8CFiLYe5) 
    - 清除渲染目标 (ClearRenderTarget)[2](https://www.google.com/url?sa=E&q=https%3A%2F%2Fvertexaisearch.cloud.google.com%2Fgrounding-api-redirect%2FAUZIYQH9eCPN278ogAE9vU_1TihUfVFa7r32o003rJq2HSCLu-IgM_TfXz4PlnwB5A-pAlvCvurQaiGFFEeuV-lsZoFI98syUshmeeiM9olc7AwEXOsCO_7iR0IhOww81_T5zaPIA0fHIMiDdcPK7UFxkI7jgt06OXeKgtFR5HZ7BsWUKP69PveY8CFiLYe5) 
    - 绘制渲染器 (DrawRenderer)[2](https://www.google.com/url?sa=E&q=https%3A%2F%2Fvertexaisearch.cloud.google.com%2Fgrounding-api-redirect%2FAUZIYQH9eCPN278ogAE9vU_1TihUfVFa7r32o003rJq2HSCLu-IgM_TfXz4PlnwB5A-pAlvCvurQaiGFFEeuV-lsZoFI98syUshmeeiM9olc7AwEXOsCO_7iR0IhOww81_T5zaPIA0fHIMiDdcPK7UFxkI7jgt06OXeKgtFR5HZ7BsWUKP69PveY8CFiLYe5) 
    - 绘制网格 (DrawMesh)[1](https://www.google.com/url?sa=E&q=https%3A%2F%2Fvertexaisearch.cloud.google.com%2Fgrounding-api-redirect%2FAUZIYQGy9k2_YD7hm7gKsaPpg1tjjCcFwNKVhLPcMuO8dLdkZXMPkkmh0JjgHpwvzH7FEez4f0XCm5aZuHOqkn-C4Arm1SmEFLjZOSg_HWVhYELV2ul_4WqG75hYBjHWZxmU4YIn-YmPKJ-0wFjWosgKOfkehiwXO9xCLj_W4F2F_IJzdoOZRVCZoNS-V2m6-H7Qyv0ft2xYIw%3D%3D) 
    - 执行图像混合 (Blit)[2](https://www.google.com/url?sa=E&q=https%3A%2F%2Fvertexaisearch.cloud.google.com%2Fgrounding-api-redirect%2FAUZIYQH9eCPN278ogAE9vU_1TihUfVFa7r32o003rJq2HSCLu-IgM_TfXz4PlnwB5A-pAlvCvurQaiGFFEeuV-lsZoFI98syUshmeeiM9olc7AwEXOsCO_7iR0IhOww81_T5zaPIA0fHIMiDdcPK7UFxkI7jgt06OXeKgtFR5HZ7BsWUKP69PveY8CFiLYe5) 
    - 设置全局着色器属性 (SetGlobalTexture, SetGlobalFloat, 等)[3](https://www.google.com/url?sa=E&q=https%3A%2F%2Fvertexaisearch.cloud.google.com%2Fgrounding-api-redirect%2FAUZIYQHekAH2WxR9EOXeIqudnd_V2N0i89UrFrySKxnvYldxWP_67TSkzl_blNWYGeVPmrIMYxBr_shNNF1Z8aMbxRZqwCOuQp1L6OUaZYQdCN3_FDZEUiLfuZ5KL4KYwtCsKgyyiCTY-Q-pZHAZaxBY3rTGUv9VTO6GCbFfUYcreQJkkvG-PwPG4EeNj9PeP9-e3Rs%3D) 
        
3. **执行 CommandBuffer**：填充完命令后，你可以通过以下几种方式来执行 CommandBuffer：
    - **附加到相机 (Camera)**：使用 Camera.AddCommandBuffer，可以将 CommandBuffer 附加到相机的渲染流程中的特定事件点（由 CameraEvent 枚举定义）。例如，你可以在不透明物体渲染后、天空盒渲染前、或者所有渲染完成后执行自定义的渲染命令。[2](https://www.google.com/url?sa=E&q=https%3A%2F%2Fvertexaisearch.cloud.google.com%2Fgrounding-api-redirect%2FAUZIYQH9eCPN278ogAE9vU_1TihUfVFa7r32o003rJq2HSCLu-IgM_TfXz4PlnwB5A-pAlvCvurQaiGFFEeuV-lsZoFI98syUshmeeiM9olc7AwEXOsCO_7iR0IhOww81_T5zaPIA0fHIMiDdcPK7UFxkI7jgt06OXeKgtFR5HZ7BsWUKP69PveY8CFiLYe5)[4](https://www.google.com/url?sa=E&q=https%3A%2F%2Fvertexaisearch.cloud.google.com%2Fgrounding-api-redirect%2FAUZIYQHWWOf8LzgWgJPYm73AVJMu5QrUTk_A6hWO3hHIBcHzXAZlo1-eTYdaVd5JdtMq3mZ9B9nYP6rVPzYGUElDBs_CG3aahDW14Zqz80e023wpaIf4dLHP8ALF3kAYHwLcrXURU3_9vhYax21HjSAYqU06VJRxeQytb-Z-P1fN710mDyjLBcMRtOPhfA3n) 
        
    - **附加到光源 (Light)**：类似于附加到相机，你可以使用 Light.AddCommandBuffer 将 CommandBuffer 附加到光源的渲染流程中，例如在阴影贴图渲染时执行。[2](https://www.google.com/url?sa=E&q=https%3A%2F%2Fvertexaisearch.cloud.google.com%2Fgrounding-api-redirect%2FAUZIYQH9eCPN278ogAE9vU_1TihUfVFa7r32o003rJq2HSCLu-IgM_TfXz4PlnwB5A-pAlvCvurQaiGFFEeuV-lsZoFI98syUshmeeiM9olc7AwEXOsCO_7iR0IhOww81_T5zaPIA0fHIMiDdcPK7UFxkI7jgt06OXeKgtFR5HZ7BsWUKP69PveY8CFiLYe5)[4](https://www.google.com/url?sa=E&q=https%3A%2F%2Fvertexaisearch.cloud.google.com%2Fgrounding-api-redirect%2FAUZIYQHWWOf8LzgWgJPYm73AVJMu5QrUTk_A6hWO3hHIBcHzXAZlo1-eTYdaVd5JdtMq3mZ9B9nYP6rVPzYGUElDBs_CG3aahDW14Zqz80e023wpaIf4dLHP8ALF3kAYHwLcrXURU3_9vhYax21HjSAYqU06VJRxeQytb-Z-P1fN710mDyjLBcMRtOPhfA3n) 
        
    - **立即执行**：通过 Graphics.ExecuteCommandBuffer，可以立即执行一个 CommandBuffer。这种方式适用于需要一次性、按需执行的渲染任务。[2](https://www.google.com/url?sa=E&q=https%3A%2F%2Fvertexaisearch.cloud.google.com%2Fgrounding-api-redirect%2FAUZIYQH9eCPN278ogAE9vU_1TihUfVFa7r32o003rJq2HSCLu-IgM_TfXz4PlnwB5A-pAlvCvurQaiGFFEeuV-lsZoFI98syUshmeeiM9olc7AwEXOsCO_7iR0IhOww81_T5zaPIA0fHIMiDdcPK7UFxkI7jgt06OXeKgtFR5HZ7BsWUKP69PveY8CFiLYe5)[4](https://www.google.com/url?sa=E&q=https%3A%2F%2Fvertexaisearch.cloud.google.com%2Fgrounding-api-redirect%2FAUZIYQHWWOf8LzgWgJPYm73AVJMu5QrUTk_A6hWO3hHIBcHzXAZlo1-eTYdaVd5JdtMq3mZ9B9nYP6rVPzYGUElDBs_CG3aahDW14Zqz80e023wpaIf4dLHP8ALF3kAYHwLcrXURU3_9vhYax21HjSAYqU06VJRxeQytb-Z-P1fN710mDyjLBcMRtOPhfA3n) 
        
## 适用场景与示例

CommandBuffer 的应用非常广泛，尤其是在需要对默认渲染管线进行扩展和定制的场景中。以下是一些常见的使用案例：
- **自定义渲染效果**：可以实现一些默认管线难以做到的特殊效果，例如选择性辉光（只让特定物体发光）、贴花（Decals）、自定义轮廓线渲染等。[3](https://www.google.com/url?sa=E&q=https%3A%2F%2Fvertexaisearch.cloud.google.com%2Fgrounding-api-redirect%2FAUZIYQHekAH2WxR9EOXeIqudnd_V2N0i89UrFrySKxnvYldxWP_67TSkzl_blNWYGeVPmrIMYxBr_shNNF1Z8aMbxRZqwCOuQp1L6OUaZYQdCN3_FDZEUiLfuZ5KL4KYwtCsKgyyiCTY-Q-pZHAZaxBY3rTGUv9VTO6GCbFfUYcreQJkkvG-PwPG4EeNj9PeP9-e3Rs%3D) 
- **扩展 G-Buffer**：在延迟渲染（Deferred Rendering）中，可以向G-Buffer（几何缓冲区）中写入额外的数据，供后续的光照计算或其他效果使用。
- **后处理效果**：虽然很多后处理效果可以通过 OnRenderImage 实现，但 CommandBuffer 提供了更灵活的控制，可以将效果插入到渲染流程的更早阶段。[3](https://www.google.com/url?sa=E&q=https%3A%2F%2Fvertexaisearch.cloud.google.com%2Fgrounding-api-redirect%2FAUZIYQHekAH2WxR9EOXeIqudnd_V2N0i89UrFrySKxnvYldxWP_67TSkzl_blNWYGeVPmrIMYxBr_shNNF1Z8aMbxRZqwCOuQp1L6OUaZYQdCN3_FDZEUiLfuZ5KL4KYwtCsKgyyiCTY-Q-pZHAZaxBY3rTGUv9VTO6GCbFfUYcreQJkkvG-PwPG4EeNj9PeP9-e3Rs%3D) 
- **性能优化**：通过 CommandBuffer，可以对一些渲染进行更精细的控制，例如手动合批（Batching）等，从而优化性能。

## 在不同渲染管线中的使用

- **内置渲染管线 (Built-in Render Pipeline)**：在内置渲染管线中，CommandBuffer 是扩展渲染功能的主要方式。上述的 Camera.AddCommandBuffer 和 Light.AddCommandBuffer 主要用于此管线。[4](https://www.google.com/url?sa=E&q=https%3A%2F%2Fvertexaisearch.cloud.google.com%2Fgrounding-api-redirect%2FAUZIYQHWWOf8LzgWgJPYm73AVJMu5QrUTk_A6hWO3hHIBcHzXAZlo1-eTYdaVd5JdtMq3mZ9B9nYP6rVPzYGUElDBs_CG3aahDW14Zqz80e023wpaIf4dLHP8ALF3kAYHwLcrXURU3_9vhYax21HjSAYqU06VJRxeQytb-Z-P1fN710mDyjLBcMRtOPhfA3n) 
- **可编程渲染管线 (Scriptable Render Pipelines - URP & HDRP)**：在URP（通用渲染管线）和HDRP（高清渲染管线）中，虽然 CommandBuffer 仍然是核心的渲染命令容器，但其使用方式有所不同。在SRP中，通常通过 ScriptableRenderContext 来执行 CommandBuffer。此外，URP中的 Renderer Features 和HDRP中的 Custom Passes 提供了更结构化和用户友好的方式来注入自定义的渲染逻辑，而这些功能底层依然依赖于 CommandBuffer 来实现。\[[2](https://www.google.com/url?sa=E&q=https%3A%2F%2Fvertexaisearch.cloud.google.com%2Fgrounding-api-redirect%2FAUZIYQH9eCPN278ogAE9vU_1TihUfVFa7r32o003rJq2HSCLu-IgM_TfXz4PlnwB5A-pAlvCvurQaiGFFEeuV-lsZoFI98syUshmeeiM9olc7AwEXOsCO_7iR0IhOww81_T5zaPIA0fHIMiDdcPK7UFxkI7jgt06OXeKgtFR5HZ7BsWUKP69PveY8CFiLYe5)] \[[3](https://www.google.com/url?sa=E&q=https%3A%2F%2Fvertexaisearch.cloud.google.com%2Fgrounding-api-redirect%2FAUZIYQHekAH2WxR9EOXeIqudnd_V2N0i89UrFrySKxnvYldxWP_67TSkzl_blNWYGeVPmrIMYxBr_shNNF1Z8aMbxRZqwCOuQp1L6OUaZYQdCN3_FDZEUiLfuZ5KL4KYwtCsKgyyiCTY-Q-pZHAZaxBY3rTGUv9VTO6GCbFfUYcreQJkkvG-PwPG4EeNj9PeP9-e3Rs%3D)]
    
### 注意事项
- **性能**：CommandBuffer 的创建和填充应避免在每一帧都执行，除非必要。可以缓存 CommandBuffer 实例并根据需要进行更新。\[[2](https://www.google.com/url?sa=E&q=https%3A%2F%2Fvertexaisearch.cloud.google.com%2Fgrounding-api-redirect%2FAUZIYQH9eCPN278ogAE9vU_1TihUfVFa7r32o003rJq2HSCLu-IgM_TfXz4PlnwB5A-pAlvCvurQaiGFFEeuV-lsZoFI98syUshmeeiM9olc7AwEXOsCO_7iR0IhOww81_T5zaPIA0fHIMiDdcPK7UFxkI7jgt06OXeKgtFR5HZ7BsWUKP69PveY8CFiLYe5)]
- **资源管理**：如果 CommandBuffer 中创建了临时的渲染纹理（GetTemporaryRT），需要在使用完毕后通过 ReleaseTemporaryRT 进行释放，以避免内存泄漏。\[[3](https://www.google.com/url?sa=E&q=https%3A%2F%2Fvertexaisearch.cloud.google.com%2Fgrounding-api-redirect%2FAUZIYQHekAH2WxR9EOXeIqudnd_V2N0i89UrFrySKxnvYldxWP_67TSkzl_blNWYGeVPmrIMYxBr_shNNF1Z8aMbxRZqwCOuQp1L6OUaZYQdCN3_FDZEUiLfuZ5KL4KYwtCsKgyyiCTY-Q-pZHAZaxBY3rTGUv9VTO6GCbFfUYcreQJkkvG-PwPG4EeNj9PeP9-e3Rs%3D)]
- **调试**：Unity的 **Frame Debugger** 是调试 CommandBuffer 的利器。通过它可以查看到 CommandBuffer 在渲染管线中的具体位置，以及每一步渲染命令执行后的结果，对于排查问题非常有帮助。\[[3](https://www.google.com/url?sa=E&q=https%3A%2F%2Fvertexaisearch.cloud.google.com%2Fgrounding-api-redirect%2FAUZIYQHekAH2WxR9EOXeIqudnd_V2N0i89UrFrySKxnvYldxWP_67TSkzl_blNWYGeVPmrIMYxBr_shNNF1Z8aMbxRZqwCOuQp1L6OUaZYQdCN3_FDZEUiLfuZ5KL4KYwtCsKgyyiCTY-Q-pZHAZaxBY3rTGUv9VTO6GCbFfUYcreQJkkvG-PwPG4EeNj9PeP9-e3Rs%3D)]
## Exemple
```csharp
using UnityEngine;
using UnityEngine.Rendering;

public class CommandBufferExample : MonoBehaviour
{
    // 用于执行绘制的材质
    public Material effectMaterial;

    // 需要被Command Buffer绘制的渲染器
    public Renderer targetRenderer;

    private CommandBuffer commandBuffer;

    void OnEnable()
    {
        // 创建一个新的Command Buffer
        commandBuffer = new CommandBuffer();
        commandBuffer.name = "My Command Buffer";

        // 在Command Buffer中添加绘制命令
        // 这个命令会使用指定的材质来绘制目标渲染器
        if (targetRenderer != null && effectMaterial != null)
        {
            commandBuffer.DrawRenderer(targetRenderer, effectMaterial);
        }

        // 将Command Buffer添加到相机的渲染事件中
        // CameraEvent.AfterForwardOpaque 表示在不透明物体渲染之后执行
        Camera.main.AddCommandBuffer(CameraEvent.AfterForwardOpaque, commandBuffer);
    }

    void OnDisable()
    {
        // 当脚本禁用或物体销毁时，从相机中移除Command Buffer并释放资源
        if (commandBuffer != null)
        {
            Camera.main.RemoveCommandBuffer(CameraEvent.AfterForwardOpaque, commandBuffer);
            commandBuffer.Release();
            commandBuffer = null;
        }
    }
}
```