## 简介
 **微动开关探针，采用磁性连接，主要针对 CoreXY 3D 打印机。**
最初，这个项目主要集中在Voron打印机（如V2.4、V1.8、Trident、V0）及其衍生机型上，现在已经重新结构化，以更好地涵盖其他打印机的文档。

本项目的目标是：
- 作为Omron TL-Q5MC2或PL-08N2的替代品（不需要更换工具头），替代BLtouch探针
- 不需要焊接
- 仅需进行最小的调整
- 能够检测所有打印表面
- 尽可能接近热端喷嘴尖端
- 高度可重复且准确的探测
- 减少温度变化
- 不会因零件熔化而受损
- 制作成本低廉
- 尽可能重复利用备用零件

大多数Klicky探针的用户使用Klipper，这里提供了一些简化探测过程的宏，通过自动连接、停靠和使用探针来简化操作。也有一些工作致力于在RRF（RepRapFirmware）中实现相同的功能。

此外，如果你的打印机支持由喷嘴触发的 Z 轴限位开关，它还可以与 Klipper 的[自动 Z 轴校准插件]( https://github.com/protoloft/klipper_z_calibration )配合使用，有效地计算探针与 Z 轴限位开关之间的 Z 轴偏移值。
## Upgrading from an earlier version
If you are upgrading from an earlier version, check the [klipper macros](https://github.com/jlas1/Klicky-Probe/blob/main/Klipper_macros) folder, it contains update instructions.
## Probe options
Right now, there are two probe attachment options, each with two probe types.
### Regular Klicky
First klicky probe, based on the [Quickdraw probe](https://github.com/Annex-Engineering/Quickdraw_Probe), with an added third magnet for added stability and fixed dock gantry setups.
![[Pasted image 20240904212949.png|500]]
It uses magnets to secure the probe to the mount and also to make the electrical connection. The magnets can be glued to prevent them from coming loose. It supports a [microswitch probe](https://github.com/jlas1/Klicky-Probe/blob/main/Probes/KlickyProbe) and [Unklicky](https://github.com/jlas1/Klicky-Probe/blob/main/Probes/Unklicky) ([invented by DustinSpeed](https://github.com/majarspeed/Unklicky)) (self built probe, that so far surpasses the microswitches in common use) based probing.
### KlickyNG
New enclosed magnets probe, it does not require glue to help prevent the magnets from coming loose, magnets are also self aligning. This approach only uses common and easy to source parts.（零件易于获得）
![[Pasted image 20240904213222.png|500]]
## voron 2.4 的安装调试指南
机械安装部分，这里就跳过了，本文主要关注的是 klicky 和 klipper 之间的软件调试
截至目前，Klipper 和 RRF 都不支持可拆卸探针的内置支持，但是，它们都支持非常强大的宏编程，因此你需要添加宏来实现探针的停靠和连接，以及支持其他需要使用探针的功能。这些宏和配置说明位于 Macro 目录中，在继续构建之前，你需要查看这些内容。对于 voron2.4，这是在 klicky-variables.cfg 中推荐的配置：
```python
variable_verbose:               True  # Enable verbose output
variable_travel_speed:          200   # how fast all other travel moves will be performed when running these macros
variable_dock_speed:            50    # how fast should the toolhead move when docking the probe for the final movement
variable_release_speed:         75    # how fast should the toolhead move to release the hold of the magnets after docking
variable_z_drop_speed:          20    # how fast the z will lower when moving to the z location to clear the probe
    
variable_safe_z:         	    25    # Minimum Z for attach/dock and homing functions
# if true it will move the bed away from the nozzle when Z is not homed
variable_enable_z_hop:          CHECK_COMMENT  # True on the v2.4, False on v1.8, Trident and Legacy
    
#Dock move (the final movement required to release the probe on the dock)
Variable_dockmove_x:                40    # Final toolhead movement to release
Variable_dockmove_y:                0     # the probe on the dock
Variable_dockmove_z:                0     # (can be negative)

#Attach move (the final movement required to reach the dock and avoid the arms with the probe attached)
Variable_attachmove_x:              0     # Final toolhead movement to Dock
Variable_attachmove_y:              30    # the probe on the dock
Variable_attachmove_z:              0     # (can be negative)
```
下面的这个示例使用了 E0DET 引脚（引脚 P1.26，"Extruder 0 Detect" 的缩写，即 "挤出机0检测" 引脚）的探针，请根据你的具体配置进行更新。你可以使用其他端口，==但应该使用限位开关引脚，因为这些引脚具有硬件电压上拉功能==，这对于提高精度是必要的。
```python
[probe]
pin: ^P1.26
x_offset: 0
y_offset: 19.75
z_offset: 6.42
speed: 5
samples:3 
samples_result: median
sample_retract_dist: 2.0
samples_tolerance: 0.01
samples_tolerance_retries: 3
```
确保在床网格（bed mesh）和四点调平（QGL）过程中，`horizontal_move_z` 参数设置得足够高，以避免探针撞击到打印床（至少需要设置为 8mm）。
```python
[bed_mesh]
horizontal_move_z: 10

[quad_gantry_level]
horizontal_move_z: 10
```
建议探测速度设置在 3mm/s 到 10mm/s 之间，你可以进行实验，看看哪种速度最适合你的机器。请确认如果你正在使用探针输入，是否已通过使用 `^` 符号启用了上拉电阻（pull-up）。通常情况下，限位开关引脚有硬件解决方案，不需要这个配置。根据你的开关类型，你可能需要添加 `!` 来反转该引脚（常开与常闭之间的区别）。通常情况下，限位开关引脚使用硬件解决方案，因此不需要额外配置。

现在探针上有一个箭头，指示开关的正确位置，以便获得正确的偏移量。

**Z限位开关和探针配置（虚拟Z限位开关）**
如果你想使用 Klicky Probe 作为 Z 轴的限位开关，请阅读 Takuya 和 Clee 撰写的这份优秀文档。
###  klipper Dock/Undock configuration
#### Y max position adjustment
If you are using a hall sensor as endstop, you need to make sure that on your Y maximum, the gantry is almost hitting the AB motor mounts, you can have a Y position maximum "behind" the Y endstop position, like this:
```python
[stepper_y]
position_endstop: y
position_max: y+2
```
Even in the stock Y endstop with a lever, you normally can add a extra mm of Y travel due to the lever extra trigger distance:
```python
[stepper_y]
position_endstop: y
position_max: y+1
```
