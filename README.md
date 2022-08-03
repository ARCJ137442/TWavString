# TWavString

## 什么是`TWavString`？

* TWavString是一个音频-二进制转换器.

## 怎么使用`TWavString`？

### 从命令提示符调用

* 你可以执行命令`python TWavString.exe <PATH_TO_FILE>`
* 命令中的两个参数：`-e` 启用强制编码，`-d` 启用强制解码

### 拖动文件 or 直接打开

* 你可以拖动文件到TWavString.exe
* 你可以直接打开可执行文件，进入命令行模式再输入指定的路径来进行文件转换

## `TWavString`的原理是什么？

* 技术基石：wav中无损包含、可获取写入的bytes数据（rawData）

### 库实现：pydub

* 读取实现：AudioSegment类的raw_data属性
* 写入实现：AudioSegment类构造函数中的data参数

### 默认音频技术参数

* 采样率：44100 Hz
* 采样宽度：2
* 声道数：2

### 重要技术障碍

* 数据中的「字节单元」（数据的长度只能是数据单元长度的整数倍数）所造成的「补全问题」

## `TWavString`有开源许可证吗？

* `TWavString`现采用***MIT许可证***(参见LICENCE)
