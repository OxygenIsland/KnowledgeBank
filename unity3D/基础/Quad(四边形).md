---
title: "[[Quad(四边形)]]"
type: Literature
status: done
Creation Date: 2024-05-30 18:33
tags:
---
在 Unity 中，Quad（四边形）是一种非常基本的 3 D 几何体，它是由两个三角形组成的平面，通常用于创建 2 D 或简单的平面图形。

1. **构成**：Quad 由两个三角形组成，每个三角形有三个顶点。因此，一个 Quad 总共有 6 个顶点和 6 个顶点索引。

2. **使用场景**：Quads 通常用于以下情况：
   - 创建 2 D 游戏中的背景、地板、墙壁等。
   - 用于 GUI（图形用户界面）元素，如按钮、面板等。
   - 用于粒子系统的渲染。
   - 作为剪影平面，用于实现实时阴影。

3. **创建方式**：你可以通过以下几种方式创建 Quad：
   - 在 Unity 的 3 D 场景中手动创建，这可以通过在 Hierarchy 面板中右键点击并选择 Create Empty 创建一个空对象，然后将 Quad 作为其子对象添加。
   - 通过代码创建，使用 `GameObject.CreatePrimitive(PrimitiveType.Quad)` 可以在代码中创建 Quad。
   - 使用 Unity 的内置 3 D 建模工具创建，例如 ProBuilder。

4. **材质和纹理**：Quad 通常需要一个材质（Material）和纹理（Texture）来定义其外观。你可以在材质中指定 Quad 的颜色、贴图等属性。材质和纹理可以在 Unity 的 Inspector 面板中设置。

5. **渲染顺序**：与其他 3 D 对象一样，Quad 的渲染顺序可以通过设置其所在层级（Hierarchy）中的位置以及渲染队列（Queue）来控制。渲染队列用于指定渲染对象的绘制顺序。

6. **性能注意事项**：虽然 Quads 非常适合用于 2 D 元素和简单的平面，但在大量使用时可能会对性能产生影响。在需要大量平面时，考虑使用 SpriteRenderer 或 UI 系统（Canvas）来处理 2 D 元素，因为它们在性能上更优化。