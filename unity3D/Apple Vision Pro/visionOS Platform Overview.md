## vision​OS Modes
Unity 对 visionOS 的支持将 Unity 编辑器和运行时引擎的全部功能与 RealityKit 提供的渲染功能相结合。Unity 的核心功能，包括脚本、物理、动画混合、人工智能、场景管理等无需修改即可得到支持。

For rendering, visionOS support is provided through RealityKit. Core features such as meshes, materials, textures should work transparently. More complex features like particles are subject to limitations.目前不支持全屏后处理和贴花等高级功能。具体的限制如下：
- 需要 Unity 2022.3（LTS）或更高的unity版本
- visionOS 编译需要 Xcode 15 beta 2，而且必须使用 Apple Silicon（M1/M2）Mac 才能为 visionOS 进行编译。
- RealityKit 上的渲染与 Unity 渲染有视觉差异。
- 只支持 URP 渲染管线
- 只支持 Unity ShaderGraph，ShaderLab and other coding shaders are not supported
## PolySpatial Mixed Reality apps on visionOS
Mixed Reality content on visionOS can be in one of two modes, which we refer to as "shared" and "exclusive" mode.
- Shared：可以与其他应用程序共存，ARKit information such as hand position, planes, or world mesh is unavailable in this mode.
- exclusive：