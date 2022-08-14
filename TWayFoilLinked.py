'''file2图像的技术基石：图像中无损包含、可获取写入的bytes数据（rawData）
借用通用模块实现的TWavString测试
'''

from pydub import AudioSegment # 音频处理
from pathlib import Path # 路径处理
# TODO 支持对音频输出参数的自定义

# 知识点：音频处理（pydub@AudioSegment），路径处理，字节流处理&读写，交互式命令行
# 测试结果：在首次循环处理自身（文本文件）时存在3字节缺失，但其它文件（exe、7z）循环处理中均一字不差

COMPRESSED_FILE_SUFFIX='.图像'
'''转存目标格式'''

# 默认音频输出参数
OUTPUT_SAMPLE_WIDTH:int=2 # 输出采样宽度
OUTPUT_CHANNELS:int=2# 输出声道数
OUTPUT_FRAME_RATE:int=44100 # 输出帧速率

#lb=lambda x,l:[(x>>(8*i))&0xff for i in range(l,reversed=True)] # 数字转byteList
#bs=lambda x:bytes(lb(x)) # 数字转bytes

# 核心模块 #

# file2图像
def file2bytes(path:str) -> bytes:
    '''提取文件内数据'''
    with open(file=path,mode='rb') as testText:
        result=testText.read()
    return result

def bytes2image(rawData:bytes,outPath:str,enableCompressionMode:bool):
    '''将数据转存至图像'''
    # TODO：图像转换为文件时，尝试保留采样率等信息
    # 字节单元自动补位（最后一个字节代表的数字+一个字节单元，目的是降低「原始音频」的误认率）
    byteUnitSize:int=4 # RGBA四通道32位
    spareNum:int=(byteUnitSize<<1)-len(rawData)%byteUnitSize # 自动补位将产生的空数据（1~byteUnitSize + byteUnitSize）
    bytesToAppend:bytes=bytes([spareNum])*spareNum # 将自动补位产生的字节追加至数据中
    rawDataFinal:bytes=rawData+bytesToAppend # 根据采样宽度与声道数量自动补位，并将最后一个字节用于剪切（若无冗余也创造一个冗余使之不被误认）
    # 生成文件并保存
    #TODO
    return 

def file2image(path:str,outPath:str,enableCompressionMode:bool):
    '''将文件内数据转存至图像'''
    return bytes2image(rawData=file2bytes(path=path),outPath=outPath,
        enableCompressionMode=enableCompressionMode
    )

# 图像2file
def image2bytes(path:str) -> bytes:
    '''提取图像存储的数据'''
    # 读取文件
    
    rawData:bytes=
    # 剪裁（尽可能降低误认率）
    '''因「无法辨别标识字节处的字节码之用处」可能的效应：原始文件的末尾遭受被误认的标识字节的剪裁'''
    byteUnitSize:int=4 # 三十二位色
    toSliceByteNum:int=rawData[-1] # bytes 在截取单一byte时自动转换为int
    needSlice:bool=( # 辨认是否需要进行裁剪
        toSliceByteNum<=(byteUnitSize<<1) and
        toSliceByteNum>byteUnitSize and # 辨认条件：「末尾字节」对应数字大于单元尺寸（但不超过两倍）
        rawData[-toSliceByteNum:]==bytes([toSliceByteNum])*toSliceByteNum # 辨认条件：一个单元再加「末尾字节」个数的字节均为「末尾字节」
        )
    '''（能辨认大部分「原生音频」）若待裁剪字节数超出应有范围（1~字节单元大小 + 字节单元大小），则不予裁剪（0的处理也是不裁剪）'''
    return rawData[:len(rawData)-toSliceByteNum] if needSlice else rawData
    # 一次失真，永久保真：字节单元问题给「原生音频」带来的影响微乎其微（仅有一点长度缩短）

def bytes2file(rawData:bytes,outPath:str):
    '''将数据写入文件'''
    # 写入文件
    with open(file=outPath,mode='wb',buffering=-1) as result:
        result.write(rawData)
    return result

def image2file(path:str,outPath:str):
    '''提取图片存储的数据并将其写入文件'''
    return bytes2file(rawData=image2bytes(path=path),outPath=outPath)

# 面向输入的重写
def f2i(path:str,customArgvs:dict=None):
    '''文件到图像'''
    pathO:Path=Path(path)
    return file2image(path=path,
        outPath=str(pathO.with_name(pathO.name+COMPRESSED_FILE_SUFFIX)),
        enableCompressionMode=customArgvs["enableCompressionMode"]
    ) # 添加扩展名图像

def i2f(path:str,customArgvs:dict=None):
    '''图像到文件'''
    pathO:Path=Path(path)
    return image2file(path=path,outPath=str(pathO.with_name(pathO.stem))) # 去掉扩展名图像

# 面向通用模块的重写
from 字节码封装程序通用模块 import *
selfProgram=ByteEncapsulatingProgram(
    name='TWayFoil',
    fileEncapsulateFunc=f2i,
    fileDecapsulateFunc=i2f,
    defaultDecasulateSuffixes=[COMPRESSED_FILE_SUFFIX],
    customInputArgvTerms=[('enableCompressionMode',bool,'Y/N: ',None,0,"Enable compression mode?%s","\u542f\u7528\u538b\u7f29\u6a21\u5f0f\uff1f%s")] # (参数名,类型,格式化参数,空时默认值,限定提供情况标签,en提示,zh提示)
)

# 主函数
if __name__ == "__main__":
    from sys import argv
    selfProgram.executeAsMain(argv=argv)
