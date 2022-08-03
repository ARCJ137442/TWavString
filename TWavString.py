'''file2wav的技术基石：wav中无损包含、可获取写入的bytes数据（rawData）'''

from pydub import AudioSegment # 音频处理
from pathlib import Path # 路径处理
# TODO 基于命令行参数的可自定义编解码
# TODO 路径截取&扩展名修改
# TODO 命令行用户输入功能
# TODO 《文件「字节单元」的补全与信息混淆问题》

# 知识点：音频处理（pydub@AudioSegment），路径处理，字节流处理&读写，交互式命令行
# 测试结果：在首次循环处理自身（文本文件）时存在3字节缺失，但其它文件（exe、7z）循环处理中均一字不差

COMPRESSED_FILE_SUFFIX='.wav'
'''转存目标格式'''

# 默认音频输出参数
OUTPUT_SAMPLE_WIDTH:int=2
OUTPUT_CHANNELS:int=2
OUTPUT_FRAME_RATE:int=44100

#lb=lambda x,l:[(x>>(8*i))&0xff for i in range(l,reversed=True)] # 数字转byteList
#bs=lambda x:bytes(lb(x)) # 数字转bytes

# 核心模块 #

# file2wav
def file2bytes(path:str) -> bytes:
    '''提取文件内数据'''
    with open(file=path,mode='rb') as testText:
        result=testText.read()
    return result

def bytes2wav(rawData:bytes,outPath:str):
    '''将数据转存至wav'''
    # TODO：wav转换为文件时，尝试保留采样率等信息
    # 字节单元自动补位（最后一个字节代表的数字+一个字节单元，目的是降低「原始音频」的误认率）
    byteUnitSize:int=OUTPUT_SAMPLE_WIDTH*OUTPUT_CHANNELS
    spareNum:int=(byteUnitSize<<1)-len(rawData)%byteUnitSize # 自动补位将产生的空数据（1~byteUnitSize + byteUnitSize）
    bytesToAppend:bytes=bytes([spareNum])*spareNum # 将自动补位产生的字节追加至数据中
    rawDataFinal:bytes=rawData+bytesToAppend # 根据采样宽度与声道数量自动补位，并将最后一个字节用于剪切（若无冗余也创造一个冗余使之不被误认）
    # 生成文件并保存
    testSound = AudioSegment(
        # raw audio data (bytes)
        data=rawDataFinal,# 与from_file()的raw_data格式相同（此为file2wav的技术基石）
        # 2 byte (16 bit) samples
        sample_width=OUTPUT_SAMPLE_WIDTH,
        # 44.1 kHz frame rate
        frame_rate=OUTPUT_FRAME_RATE,
        # stereo
        channels=OUTPUT_CHANNELS
    )
    return testSound.export(outPath, format="wav")

def file2wav(path:str,outPath:str):
    '''将文件内数据转存至wav'''
    return bytes2wav(rawData=file2bytes(path=path),outPath=outPath)

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

def bytes2file(rawData:bytes,outPath:str):
    '''将数据写入文件'''
    # 写入文件
    with open(file=outPath,mode='wb',buffering=-1) as result:
        result.write(rawData)
    return result

def wav2file(path:str,outPath:str):
    '''提取wav存储的数据并将其写入文件'''
    return bytes2file(rawData=wav2bytes(path=path),outPath=outPath)

# 面向输入的重写
def f2w(path:str):
    '''文件到wav'''
    pathO:Path=Path(path)
    return file2wav(path=path,outPath=str(pathO.with_name(pathO.name+COMPRESSED_FILE_SUFFIX))) # 添加扩展名wav

def w2f(path:str):
    '''wav到文件'''
    pathO:Path=Path(path)
    return wav2file(path=path,outPath=str(pathO.with_name(pathO.stem))) # 去掉扩展名wav

# 命令行模式
SELF_NAME='TWavString'
from 字符串处理程序通用模块 import *
def cmdLineMode(argv:list):
    '''命令行模式，移植自TWayFoil'''
    global numExcept
    print("<===="+Path(argv[0]).stem+"====>")
    while(True):
        try:
            numExcept=0
            path=inputBL(en="Please insert PATH:",zh="\u8bf7\u8f93\u5165\u8def\u5f84\uff1a")
            forceEncode=inputBool(gsbl(en="Forced encoding? %s",zh="强制编码？%s")%'Y/N:')
            handleOnePath(path=path,
                          forceEncode=forceEncode,
                          forceDecode=False if forceEncode else inputBool(gsbl(en="Forced decoding? %s",zh="强制解码？%s")%'Y/N:'))
        except BaseException as e:
            catchExcept(e,path,"cmdLineMode()->")
        if numExcept>0 and inputBool(gsbl(en="Do you want to terminate the program?",zh="\u4f60\u60f3\u7ec8\u6b62\u7a0b\u5e8f\u5417\uff1f")+"Y/N:"):
            break
        numExcept=0
        print()#new line

def handleOnePath(path:str,forceEncode:bool=False,forceDecode:bool=False):
    '''处理单个文件路径'''
    result=None
    pathO=Path(path)
    if pathO.exists():
        if forceEncode == forceDecode: # 全真or全假 → 智能决定
            if pathO.suffix==COMPRESSED_FILE_SUFFIX: # 是wav，解码
                result=w2f(path=path)
            else:
                result=f2w(path=path)
        elif forceEncode: # 若强制编码
            result=f2w(path=path)
        else: # 强制解码
            result=w2f(path=path)
    else:
        result=0
    # 显示消息
    if result: # 成功
        print(getFormedStrByLanguage(formet=(path,result.name),en="File \"%s\" has been successfully converted to \"%s\"!",zh="文件「%s」已成功转换为「%s」！"))
    elif result==0: # 文件不存在
        print(getFormedStrByLanguage(formet=path,en="File \"%s\" is not exist!",zh="文件「%s」不存在！"))
    else: # 失败
        print(getFormedStrByLanguage(formet=path,en="Failed to convert file \"%s\"!",zh="文件「%s」转换失败！"))

# 主函数
if __name__ == "__main__":
    from sys import argv
    forceEncode='-e' in argv
    forceDecode='-d' in argv
    if len(argv)>1:# 若有参数则根据参数进行处理
        pathO:Path
        for path in argv[1:]:
           handleOnePath(path=path,forceEncode=forceEncode,forceDecode=forceDecode)
    else: # 否则进入命令行模式
        cmdLineMode(argv=argv)
    #file_handle=file2wav(path="test.txt",outPath="test_.wav")
    #file_handle=wav2file(path="test_.wav",outPath="outTest.txt")
    
    #file_handle=wav2file(path="test.wav",outPath="test_.txt")
    #file_handle=file2wav(path="test_.txt",outPath="outTest.wav")
    
    #f2w("TWavString_.py")
    #w2f("TWavString_.py.wav")
