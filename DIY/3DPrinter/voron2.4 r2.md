## EBBCAN通信线束弹力方案
1、orbiter2.0挤出机使用的3d打印件会有一定的倾斜角度，需要从交流群中获取修改过后的文件
2、需要确定主板typeC接口是否支持 can协议
3、
can bus 通信协议

## 玩转 MKS 主板
![[Pasted image 20240710205227.png|500]]![[Pasted image 20240710213946.png|500]]
### 1、主板供电需要接 24V 直流电输入，所以调试主板首先要将电源接起来
电源如何接，voron原版上有一个5v的电源，还用不用接？
### 2、系统镜像文件应该已经是烧录过的，所以这一步可以跳过
### 3、网络连接
#### 3.1 EMMC模块会分出一个255M的分区，打开该分区，找到wpa_supplicant-wlan0.conf文件，打开该文件进行配置wifi名称和密码的配置。
或者使用网线进行连接
#### 3.2 网络连接成功之后，在Putty发送指令 ip a查看 IP地址
### 4、Putty 连接
Putty 的作用是通过数据线连接系统，进行固件的编译，在线升级等
#### 4.1用Type_c数据线与主板的Host_USB连接，主板供电，在电脑的设备管理器查看com口，然后打开Putty  
#### 4.2选择com口，设置波特率1500000，点击Open打开连接
![[Pasted image 20240711213042.png|426]]
#### 4.3进入下面界面，点击回车（ENTER）键
![[Pasted image 20240711213117.png|475]]
#### 4.4然后输入账号：mks, 密码：makerbase
### 5、SSH连接
SSH的作用是无线发送指令操作系统，进行固件的编译，在线升级等
这里使用坤哥推荐的那个软件试一试也可以
1）下载安装Xshell软件，Xshell6Portable 下载地址：https://www.netsarang.com/zh/free-for-home-school/
2）打开Xshell软件，建立新的会话
![[Pasted image 20240711213306.png|441]]
![[Pasted image 20240711213324.png|475]]
2）然后点击连接
![[Pasted image 20240711213357.png|475]]
4）连接后弹出设置用户名界面，输入用户名：mks
![[Pasted image 20240711213434.png|353]]
5）双击新建的会话连接，弹出密码输入界面，密码：makerbase输入密码后进入linux操作系统的用户界面shell。
### 6、MKS PI_TS35屏幕连接和操作

将TS35屏幕排线接到PI上的SPI接口，启动后可在屏幕上进行操作打印机。
这一步可以连接电脑显示屏和鼠标来操作打印机，调试电机驱动的时候可以用该方法
### 7、加速度传感器ADXL345连接和配置

MKS PI与ADXL345的连接如下：
![[Pasted image 20240711213952.png|475]]
MKS PI镜像默认已安装加速度计算库和依赖库，不用额外配置，在配置文件中配置ADXL345和测试位置参数即可。  
1、在配置文件中配置adxl345，将以下参数复制到配置文件中
```
[mcu rpi]
serial: /tmp/klipper_host_mcu

[adxl345]
cs_pin: rpi:None
spi_bus: spidev0.2
```
保存重启，网页界面没有报错后发送查询指令：
`ACCELEROMETER_QUERY`
软硬件安装正常，能接收到加速度传感器数据，数据类似如下：
`Recv: // adxl345 values (x, y, z): 430.619210, 831.432400, 8718.156800...`
2、配置adxl345的测试位置，一般安装在平台的中间位置,
#todo 平台的中间位置是在哪里？热床上面？在b站找一下相关的教程，can板上有没有类似的传感器？
```
[resonance_tester]
accel_chip: adxl345
probe_points:
    115, 115, 20  # an example
```
3、测试加速度，配置input_shaper数据  
测试前，先把打印机的加速度配置调大（测试完后可以改小）
```[printer]
max_accel: 7000
max_accel_to_decel: 7000
```
如果配置文件中有input_shaper功能参数，需要发送指令关掉
如何在配置文件中找到这个参数呢？
`SET_INPUT_SHAPER SHAPER_FREQ_X=0 SHAPER_FREQ_Y=0`
然后发送自动测试配置命令开始测试震动
`SHAPER_CALIBRATE`
测试完后会返回x轴和y轴推荐的配置方法和配置值，把值配置在配置文件中，然后保存重启，配置类似如下
```
[input_shaper]
shaper_type_x = 3hump_ei
shaper_freq_x = 52.4
shaper_type_y = 2hump_ei
shaper_freq_y = 37.5
```
### 8、USB摄像头连接和配置
到时候可以试一下小米的那个摄像头
默认镜像文件已经安装MJPG-Streamer，只需要在fluidd网页上配置摄像头参数即可，配置项如下：  
1、在网页界面的配置项→选择摄像头→添加摄像头
![[Pasted image 20240711215030.png|475]]
2、启用摄像头→配置摄像头名称→视频类型选择为MJPEG视频流，然后保存，返回到主界面能查看到图像即可。
![[Pasted image 20240711215102.png|475]]
### 9、主板固件更新
主板固件更新指的是将3D打印机主板上的固件（即嵌入式软件）升级到最新版本的过程。固件是控制和管理主板及其连接的所有硬件设备的低级软件。
### 10、[[Kliper#Klipper配置|klipper 配置文件]] 配置
### 11、驱动跳线
1、TMC2208、2209、2226普通模式16细分跳线
![[Pasted image 20240711233251.png|500]]
2、TMC2225普通模式16细分跳线
![[Pasted image 20240711233316.png|500]]
3、A4988 16细分跳线
![[Pasted image 20240711233341.png|475]]
4、TMC驱动[[Kliper#3.4 TMC驱动 UART模式配置|UART模式]]跳线
![[Pasted image 20240711233401.png|475]]