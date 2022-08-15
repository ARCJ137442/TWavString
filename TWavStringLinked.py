'''file2wav的技术基石：wav中无损包含、可获取写入的bytes数据（rawData）
借用通用模块实现的TWavString测试
'''

from io import BufferedRandom, BufferedReader, BufferedWriter # 返回值类型标注
from pydub import AudioSegment # 音频处理

# 知识点：音频处理（pydub@AudioSegment），字节流处理&读写，交互式命令行
# 测试结果：在首次循环处理自身（文本文件）时存在3字节缺失，但其它文件（exe、7z）循环处理中均一字不差

COMPRESSED_FILE_SUFFIX='.wav'
'''转存目标格式'''

# 默认音频输出参数
OUTPUT_SAMPLE_WIDTH:int=2 # 输出采样宽度
OUTPUT_CHANNELS:int=2# 输出声道数
OUTPUT_FRAME_RATE:int=44100 # 输出帧速率

#lb=lambda x,l:[(x>>(8*i))&0xff for i in range(l,reversed=True)] # 数字转byteList
#bs=lambda x:bytes(lb(x)) # 数字转bytes

# 核心模块 #

# file2wav
def file2bytes(path:str) -> bytes:
    '''提取文件内数据'''
    with open(file=path,mode='rb') as testText:
        result=testText.read()
    return result

def bytes2wav(rawData:bytes,outPath:str,sampleWidth:int,channels:int,frameRate:int) -> BufferedRandom:
    '''将数据转存至wav'''
    # TODO：wav转换为文件时，尝试保留采样率等信息
    # 字节单元自动补位（最后一个字节代表的数字+一个字节单元，目的是降低「原始音频」的误认率）
    byteUnitSize:int=sampleWidth*channels
    spareNum:int=(byteUnitSize<<1)-len(rawData)%byteUnitSize # 自动补位将产生的空数据（1~byteUnitSize + byteUnitSize）
    bytesToAppend:bytes=bytes([spareNum])*spareNum # 将自动补位产生的字节追加至数据中
    rawDataFinal:bytes=rawData+bytesToAppend # 根据采样宽度与声道数量自动补位，并将最后一个字节用于剪切（若无冗余也创造一个冗余使之不被误认）
    # 生成文件并保存
    testSound = AudioSegment(
        # raw audio data (bytes)
        data=rawDataFinal,# 与from_file()的raw_data格式相同（此为file2wav的技术基石）
        # sampleWidth byte (16 bit) samples
        sample_width=sampleWidth,
        # frameRate Hz frame rate
        frame_rate=frameRate,
        # mono=1,stereo=2
        channels=channels
    )
    return testSound.export(outPath, format="wav")

def file2wav(path:str,outPath:str,sampleWidth:int,channels:int,frameRate:int) -> BufferedRandom:
    '''将文件内数据转存至wav'''
    return bytes2wav(rawData=file2bytes(path=path),outPath=outPath,
        sampleWidth=sampleWidth,channels=channels,frameRate=frameRate
    )

# wav2file
def wav2bytes(path:str) -> bytes:
    '''提取wav存储的数据'''
    # 读取文件
    asFile:AudioSegment=AudioSegment.from_file(path)
    rawData:bytes=asFile.raw_data
    # 剪裁（尽可能降低误认率）
    '''因「无法辨别标识字节处的字节码之用处」可能的效应：原始文件的末尾遭受被误认的标识字节的剪裁'''
    byteUnitSize:int=asFile.channels*asFile.sample_width
    toSliceByteNum:int=rawData[-1] # bytes 在截取单一byte时自动转换为int
    needSlice:bool=( # 辨认是否需要进行裁剪
        toSliceByteNum<=(byteUnitSize<<1) and
        toSliceByteNum>byteUnitSize and # 辨认条件：「末尾字节」对应数字大于单元尺寸（但不超过两倍）
        rawData[-toSliceByteNum:]==bytes([toSliceByteNum])*toSliceByteNum # 辨认条件：一个单元再加「末尾字节」个数的字节均为「末尾字节」
        )
    '''（能辨认大部分「原生音频」）若待裁剪字节数超出应有范围（1~字节单元大小 + 字节单元大小），则不予裁剪（0的处理也是不裁剪）'''
    return rawData[:len(rawData)-toSliceByteNum] if needSlice else rawData
    # 一次失真，永久保真：字节单元问题给「原生音频」带来的影响微乎其微（仅有一点长度缩短）

def bytes2file(rawData:bytes,outPath:str) -> BufferedWriter:
    '''将数据写入文件'''
    # 写入文件
    with open(file=outPath,mode='wb',buffering=-1) as result:
        result.write(rawData)
    return result

def wav2file(path:str,outPath:str) -> BufferedWriter:
    '''提取wav存储的数据并将其写入文件'''
    return bytes2file(rawData=wav2bytes(path=path),outPath=outPath)

# 面向输入的重写
def f2w(path:str,outPath:str,customArgvs:dict=None) -> BufferedRandom:
    '''文件到wav'''
    return file2wav(path=path,
        outPath=outPath,
        sampleWidth=customArgvs["sampleWidth"],
        channels=customArgvs["channels"],
        frameRate=customArgvs["frameRate"]
    ) # 添加扩展名wav

def w2f(path:str,outPath:str,customArgvs:dict=None) -> BufferedWriter:
    '''wav到文件'''
    return wav2file(path=path,outPath=outPath) # 去掉扩展名wav

# 面向通用模块的重写
from 字节码封装程序通用模块 import *
LBtSTDV_EN:str='(Leave blank to select the default value %d)'
LBtSTDV_ZH:str='（留空以选择默认值%d）'
selfProgram=ByteEncapsulatingProgram(
    name='TWavString',version='2.0.0',
    fileEncapsulateFunc=f2w,
    fileDecapsulateFunc=w2f,
    defaultEncasulateSuffix=COMPRESSED_FILE_SUFFIX,
    defaultDecasulateSuffixes=[COMPRESSED_FILE_SUFFIX],
    customInputArgvTerms=[
        ("sampleWidth",int,OUTPUT_SAMPLE_WIDTH,OUTPUT_SAMPLE_WIDTH,-1,LBtSTDV_EN+'Sample Width: ',LBtSTDV_ZH+'采样宽度：'),
        ("channels",int,OUTPUT_CHANNELS,OUTPUT_CHANNELS,-1,LBtSTDV_EN+'Channels: ',LBtSTDV_ZH+'声道数：'),
        ("frameRate",int,OUTPUT_FRAME_RATE,OUTPUT_FRAME_RATE,-1,LBtSTDV_EN+'Frame Rate: ',LBtSTDV_ZH+'帧速率：')
    ] # (参数名,类型,格式化参数,空时默认值,限定提供情况标签,en提示,zh提示)
)

# 主函数
if __name__ == "__main__":
    from sys import argv
    selfProgram.executeAsMain(argv=argv)
