## 1. 初始化配置参数
在调试过程中，配置项驱动 VSCode 的行为。配置项被定义在项目的 **.vscode/launch.json** 中。第一次运行可以如下配置：
![[Pasted image 20241218140218.png|500]]
![[Pasted image 20241218140249.png|475]]
## 2. 配置参数
``` json
{
    "version": "0.2.0",
    "configurations": [
        {
            "python": "/home/zdliu/anaconda3/envs/py37/bin/python3",  # 指定python解释器
            "name": "Python: train",
            "type": "python",
            "request": "launch",
            "program": "/home/axjia/train.py",  # 你要调试的 Python 脚本
            "cwd": "tools",   # 用于指定脚本所在目录，比如有的脚本需要先 cd 到 xxx 再运行。
            "console": "integratedTerminal",
            "env": {"CUDA_VISIBLE_DEVICES":"0,1"},   # 指定显卡
            "args": ["--train_dir", "./input/train_data",   # 命令行参数
                "--dev_dir", "./input/valid_data",
            ],
            "justMyCode": false   # 调试封装包里面的代码，可以在里面打断点
        }
    ]
}
```
