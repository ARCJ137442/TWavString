'''file2图像的技术基石：图像中无损包含、可获取写入的bytes数据（rawData）
借用通用模块实现的TWayFoil测试
'''

from io import BufferedReader, BufferedWriter
from PIL import Image # 图片处理
from tqdm import tqdm # 进度条
# 知识点：图片处理（PIL@Image），进度条，字节流处理&读写

COMPRESSED_FILE_SUFFIX='.png'
'''转存目标格式'''

TQDM_NCOLS=70
'''进度条尺寸适配'''

# 默认图像输出参数

#lb=lambda x,l:[(x>>(8*i))&0xff for i in range(l,reversed=True)] # 数字转byteList
#bs=lambda x:bytes(lb(x)) # 数字转bytes

# 核心模块 #

# file2图像
def file2bytes(path:str) -> bytes:
    '''提取文件内数据'''
    with open(file=path,mode='rb') as testText:
        result=testText.read()
    return result

def bytes2image(rawData:bytes,outPath:str,enableCompressionMode:bool) -> Image:
    '''将数据转存至图像'''
    global TQDM_NCOLS
    # TODO：图像转换为文件时，尝试保留采样率等信息
    # 字节单元自动补位（最后一个字节代表的数字+一个字节单元，目的是降低「原始音频」的误认率）
    byteUnitSize:int=4 # RGBA四通道32位
    spareNum:int=(byteUnitSize<<1)-len(rawData)%byteUnitSize # 自动补位将产生的空数据（1~byteUnitSize + byteUnitSize）
    bytesToAppend:bytes=bytes([spareNum])*spareNum # 将自动补位产生的字节追加至数据中
    rawDataFinal:bytes=rawData+bytesToAppend # 根据采样宽度与声道数量自动补位，并将最后一个字节用于剪切（若无冗余也创造一个冗余使之不被误认）
    # 计算像素数量
    lenPixel:int=len(rawDataFinal)
    if lenPixel&0x3>0: raise ValueError("字节码长度非4的倍数！")
    lenPixel//=byteUnitSize # 除以单元大小（像素所占字节数）
    # 决定图片尺寸
    processBar=tqdm(total=4,desc=gsbl('Creating','\u521b\u5efa\u4e2d')+': ',ncols=TQDM_NCOLS)
    width=int(lenPixel**0.5)
    while lenPixel%width>0:
        width=width-1
    height=int(lenPixel/width)
    processBar.update(1)
    # 生成图片
    newImage=Image.frombytes(data=rawDataFinal,size=(width,height),mode="RGBA")
    processBar.update(1)
    niLoad=newImage.load()
    processBar.update(1)
    # 导出图片
    newImage.save(outPath)
    processBar.update(1)
    processBar.close()
    printBL(en="Image File created!",zh="\u56fe\u7247\u6587\u4ef6\u5df2\u521b\u5efa\uff01")
    return newImage

def file2image(path:str,outPath:str,enableCompressionMode:bool) -> Image:
    '''将文件内数据转存至图像'''
    return bytes2image(rawData=file2bytes(path=path),outPath=outPath,
        enableCompressionMode=enableCompressionMode
    )

# 图像2file
def image2bytes(path:str) -> bytes:
    '''提取图像存储的数据'''
    # 读取文件
    image:Image=None
    try: image=Image.open(path)
    except BaseException:image.close() if image!=None else None
    rawData:bytes=image.tobytes()
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

def bytes2file(rawData:bytes,outPath:str) -> BufferedWriter:
    '''将数据写入文件'''
    # 写入文件
    with open(file=outPath,mode='wb',buffering=-1) as result:
        result.write(rawData)
    return result

def image2file(path:str,outPath:str) -> BufferedReader:
    '''提取图片存储的数据并将其写入文件'''
    return bytes2file(rawData=image2bytes(path=path),outPath=outPath)

# 面向输入的重写
def f2i(path:str,outPath:str,customArgvs:dict=None) -> Image:
    '''文件到图像'''
    return file2image(path=path,
        outPath=outPath,
        enableCompressionMode=customArgvs.get("enableCompressionMode")
    ) # 添加扩展名图像

def i2f(path:str,outPath:str,customArgvs:dict=None) -> BufferedReader:
    '''图像到文件'''
    return image2file(path=path,outPath=outPath) # 去掉扩展名图像

# 面向通用模块的重写
from 字节码封装程序通用模块 import *
selfProgram=ByteEncapsulatingProgram(
    name='TWayFoil',version='2.0.0',
    fileEncapsulateFunc=f2i,
    fileDecapsulateFunc=i2f,
    defaultEncasulateSuffix=COMPRESSED_FILE_SUFFIX,
    defaultDecasulateSuffixes=[COMPRESSED_FILE_SUFFIX],
    customInputArgvTerms=[] # (参数名,类型,格式化参数,空时默认值,限定提供情况标签,en提示,zh提示)
)# ('enableCompressionMode',bool,'Y/N: ',None,0,"Enable compression mode?%s","\u542f\u7528\u538b\u7f29\u6a21\u5f0f\uff1f%s")

# 主函数
if __name__ == "__main__":
    from sys import argv
    selfProgram.executeAsMain(argv=argv)
