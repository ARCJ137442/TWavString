import os

from PIL import Image # 图片处理
from tqdm import tqdm # 进度条
from pathlib import Path # 路径处理

from 字符串处理程序通用模块 import *

# 知识点：图片处理（pydub@AudioSegment），进度条，路径处理，字节流处理&读写

'''For The Core,see README'''

NCOLS=70
SELF_NAME='TWayFoil'
VERSION='3.0.0'
COMPRESSED_FILE_SUFFIX='.png'

# 核心代码 #

#0=binary,1=image,-1=exception
def readFile(path):
    try:
        file0=readImage(path)
        if file0==None:
            file0=readBinary(path)
            if file0==None:
                return (-1,FileNotFoundError(path),None)
            return (0,file0,None)
        else:
            return (1,readBinary(path),file0)
    except BaseException as error:return (-1,error,None)
#return (code,binary or error,image or None)

def autoReadFile(path,forceImage=False):
    try:
        file0=readImage(path)
        if forceImage:
            file0=readImage(path)
        elif file0==None:
            file0=readBinary(path)
        return file0
    except BaseException as e:
        printExcept(e,"autoReadFile()->")
        return None
#return image or binary or None

def autoConver(path:str,forceImage=False,customArgvs:dict=None):
    #====Define====#
    currentFile=autoReadFile(path,forceImage=forceImage)
    if Image.isImageType(currentFile):
        printBL(en="Image file read successfully!",zh="\u56fe\u50cf\u6587\u4ef6\u8bfb\u53d6\u6210\u529f\uff01")
        try:
            result=converImageToBinary(imageFile=currentFile,path=path,compressMode=False,message=True)
            result[1].close()
        except BaseException as e:
            printExcept(e,"autoConver()->")
        else:return
    if (not forceImage) and not Image.isImageType(currentFile):
        printPathBL(en="Now try to load %s as binary",zh="\u73b0\u5728\u5c1d\u8bd5\u8bfb\u53d6\u4e8c\u8fdb\u5236\u6570\u636e %s",path=path)
    converBinaryToImage(path=path,binaryFile=readBinary(path),returnBytes=False,compressMode=False,message=True)

#aa,rr,gg,bb -> 0xaarrggbb
def binaryToPixelBytes(binary):#bytes binary
    global NCOLS
    result=binary
    processBar=tqdm(range(3),desc=gsbl('Converting','\u8f6c\u6362\u4e2d'))
    binaryLength=len(binary)
    processBar.update(1)
    lenMod4m3=3-binaryLength%4
    processBar.update(1)
    if lenMod4m3<0:
        result=result+b'\x00\x00\x00\x03'
    else:
        result=result+(lenMod4m3)*b'\x00'+bytes((lenMod4m3,))
    processBar.update(1)
    processBar.close()
    return result
#returns bytes

#binaryFile:A BufferedReader or bytes(will set to bRead),Image(will convert to bytes)
def converBinaryToImage(path,binaryFile,returnBytes=False,message=None,compressMode=False):
    #========Auto Refer========#
    if message==None:message=not returnBytes
    #========From Binary========#
    if binaryFile==None:
        printPathBL(en="Faild to load binary %s",zh="\u8bfb\u53d6\u4e8c\u8fdb\u5236\u6587\u4ef6%s\u5931\u8d25",path=path)
        return
    elif type(binaryFile)==bytes:
        bReadBytes=binaryFile
    elif isinstance(binaryFile,Image.Image):
        bReadBytes=binaryFile.tobytes()
    else:
        bReadBytes=binaryFile.read()
    #====Convert Binary and Insert Pixel====#
    if bReadBytes!=None:
        if compressMode:
            return compressFromBinary(path,bReadBytes)
        printBL(en="Binary file read successfully!",zh="\u4e8c\u8fdb\u5236\u6587\u4ef6\u8bfb\u53d6\u6210\u529f\uff01")
        pixelBytes=binaryToPixelBytes(bReadBytes)
    #====Close File====#
    if (not returnBytes) and type(binaryFile)!=bytes:
        binaryFile.close()
    #====Create Image and Return Tuple====#
    return createImageFromPixelBytes(path,pixelBytes,message=message)
#return (image,bytes)

#imageFile is FileReader
def converImageToBinary(imageFile,path,compressMode=False,message=True):
    #========From Image========#
    #====1 Convert Image to Pixel,and Get Length====#
    #====2 Convert Pixel to Binary and 3 Delete the L Byte====#
    if compressMode:
        result=releaseFromImage(path,imageFile)
        imageFile.close()
        return (None,imageFile,None)
    pixelBytes=getFormedPixelBytes(imageFile)
    #====4 Create Binary File and Return====#
    imageFile.close()
    return createBinaryFile(pixelBytes,path,message=message,compressMode=compressMode)
#return (image,file,fileBytes) the file in returns[1] need to close!

def compressFromBinary(path,binary):
    oResult=converBinaryToImage(binaryFile=binary,path=path)#(image,bytes)
    lengthN=-1
    while True:
        lengthO=len(oResult[1])
        nResult=converBinaryToImage(binaryFile=oResult[1],path=path)
        lengthN=len(nResult[1])
        if lengthN>lengthO:
            nResult[0].close()
            break
        oResult=nResult
    oResult[0].save(path+COMPRESSED_FILE_SUFFIX)#required not closed image
    oResult[0].close()#close at there
    printBL(en="Binary File compressed!",zh="\u4e8c\u8fdb\u5236\u6587\u4ef6\u5df2\u538b\u7f29\uff01")
    return None
#return (pixels,path)

def releaseFromImage(path,image):
    tPath='temp_'+path
    oResult=converImageToBinary(imageFile=image,path=tPath,message=False,compressMode=False)#(image,bytes)
    while True:
        try:nResult=converImageToBinary(imageFile=oResult[0],path=tPath,compressMode=False,message=False)
        except BaseException as e:
            #printExcept(e,"releaseFromImage/while()->")
            break
        if len(nResult[2])<1:break
        oResult=nResult
        if nResult!=None and nResult[1]!=None:nResult[1].close()
    oResult=createBinaryFile(oResult[2],generateFileNameFromImage(path,removeDotPngs=True),message=True,compressMode=False)#required not closed file
    oResult[1].close()#close at there
    try:
        printPathBL(en="Deleting temp file %s...",zh="\u6b63\u5728\u5220\u9664\u4e34\u65f6\u6587\u4ef6%s\u3002\u3002\u3002",path=tPath)
        os.remove(tPath)
    except BaseException as e:
        printExcept(e,"releaseFromImage()->")
    else:printBL(en="Delete temp file successed!",zh="\u5220\u9664\u4e34\u65f6\u6587\u4ef6\u6210\u529f\uff01")
    printBL(en="Image file unzipped!",zh="\u56fe\u7247\u6587\u4ef6\u5df2\u89e3\u538b\uff01")
    return None

#image is Image.Image,alse can be a list of pixels
def getFormedPixelBytes(image):
    global NCOLS
    processBar=tqdm(total=2,desc=gsbl('Scanning','\u626b\u63cf\u4e2d')+': ',ncols=NCOLS)
    result=image.tobytes()
    processBar.update(1)
    length=int(result[-1])
    processBar.update(1)
    result=result[:-(1+length)]
    processBar.close()
    return result
#returns bytes

def createImageFromPixelBytes(sourcePath,pixelBytes,message=True):
    global NCOLS
    #==Operate Image==#
    #Operate pixel count
    lenPixel=len(pixelBytes)
    if lenPixel&3>0:
        lenPixel=(lenPixel//4)+1
    else:
        lenPixel=lenPixel//4
    #Determine size
    processBar=tqdm(total=4,desc=gsbl('Creating','\u521b\u5efa\u4e2d')+': ',ncols=NCOLS)
    width=int(lenPixel**0.5)
    while lenPixel%width>0:
        width=width-1
    height=int(lenPixel/width)
    processBar.update(1)
    #Generate image
    nImage=Image.frombytes(data=pixelBytes,size=(width,height),mode="RGBA")
    processBar.update(1)
    niLoad=nImage.load()
    processBar.update(1)
    #==Save Image==#
    nImage.save(sourcePath+COMPRESSED_FILE_SUFFIX)
    processBar.update(1)
    processBar.close()
    if message:
        printBL(en="Image File created!",zh="\u56fe\u7247\u6587\u4ef6\u5df2\u521b\u5efa\uff01")
    return (nImage,open(sourcePath+COMPRESSED_FILE_SUFFIX,'rb').read())
#return (image,imageBytes) imageBytes is (compressed png file)'s bytes!!!

def createBinaryFile(binary,path,message=True,compressMode=False):#bytes binary,str path
    #TO DEBUG
    processBar=tqdm(total=3,desc=gsbl('Generating','\u751f\u6210\u4e2d')+': ',ncols=NCOLS)
    try:
        if message and not compressMode:
            fileName=generateFileNameFromImage(path,removeDotPngs=not compressMode)#Auto Mode
        else:
            fileName=path
        file=open(fileName,'wb',-1)
        processBar.update()
        file.write(binary)
        file.close()
        processBar.update()
        try:image=Image.open(fileName)
        except:image=None
    except BaseException as exception:
        printExcept(exception,"createBinaryFile()->")
        return (None,None,None)
    #==Return,may Close File==#
    processBar.update()
    processBar.close()
    if message:#not close
        printPathBL(path=fileName,en="Binary File %s generated!",zh="\u4e8c\u8fdb\u5236\u6587\u4ef6%s\u5df2\u751f\u6210\uff01")
    file=open(fileName,'rb+',-1)
    return (image,file,file.read())
#return tuple(image,file,fileBytes)

def generateFileNameFromImage(originPath,removeDotPngs=False):
    baseName=os.path.basename(originPath)
    result=baseName
    if result.count('.')>1:
        result=result[:result.rindex('.')]
    if removeDotPngs:
        while result[-4:]==COMPRESSED_FILE_SUFFIX:
            result=result[:-4]
    if (COMPRESSED_FILE_SUFFIX in result) or result==baseName:
        result+='.txt'
    return result

def readImage(path):
    ima=None
    try:
        ima=Image.open(path)
    except BaseException as e:
        if ima!=None:ima.close()
    return ima

def readBinary(path):
    return open(path,'rb')#raises error

# 面向通用模块的重写
from 字节码封装程序通用模块 import *
selfProgram=ByteEncapsulatingProgram(
    name='TWayFoil',
    fileEncapsulateFunc=autoConver,
    fileDecapsulateFunc=autoConver,
    defaultDecasulateSuffixes=[COMPRESSED_FILE_SUFFIX],
    customInputArgvTerms=[('enableCompressionMode',bool,'Y/N: ',None,0,"Enable compression mode?%s","\u542f\u7528\u538b\u7f29\u6a21\u5f0f\uff1f%s")] # (参数名,类型,格式化参数,空时默认值,限定提供情况标签,en提示,zh提示)
)

# 主函数
if __name__ == "__main__":
    from sys import argv
    selfProgram.executeAsMain(argv=argv)
