'''字符串处理程序通用模块 Ver.20220811
功能：
中文、英文的国际化交互实现（按照系统语言调整输出）
错误追踪的格式化输出
快捷读取文件内容
'''
# TODO 去除输入中仅能有en/zh的限制，采用dict包实现国际化

# 内部模块
import errno # 错误码
from traceback import format_exc # 错误追踪

# 自动获取系统语言
SYSTEM_LANGUAGE=0
try:
    import pywintypes # 防止打包的exe因win32api的问题出错
    from win32api import GetUserDefaultLangID
    SYSTEM_LANGUAGE=GetUserDefaultLangID()
except:pass

# 按照系统语言调整输出
def getStrByLanguage(en:str='',zh:str='') -> str:
    '''按照系统语言选择字符串'''
    if SYSTEM_LANGUAGE==0x804:return zh
    return en
def gsbl(en:str='',zh:str='') -> str:
    '''按照系统语言选择字符串（缩写）'''
    return getStrByLanguage(en=en,zh=zh)
def printBL(en:str='',zh:str='') -> None:
    '''按照系统语言选择字符串并打印'''
    print(getStrByLanguage(en=en,zh=zh))
    
def getFormedStrByLanguage(format,en:str='',zh:str='') -> str:
    '''按照系统语言选择字符串，并加以格式化处理'''
    return getStrByLanguage(en=en,zh=zh)%format
def printFormedBL(format,en:str='',zh:str='') -> None:
    '''按照系统语言选择字符串并打印'''
    print(getFormedStrByLanguage(format=format,en=en,zh=zh))

# 基于国际化输出的智能输入

def inputBL(en:str='',zh:str='') -> str:
    '''获取输入并按照系统语言选择输入提示字符串'''
    return input(gsbl(en=en,zh=zh))

YES_ALTERNATIVES=('Yes','Y','True','T','1','✓','Да','是','だ','はい')
def inputBool(message:str) -> bool:
    '''获取输入，将其转换为布尔值，并按照系统语言选择输入提示字符串'''
    return input(message) in YES_ALTERNATIVES
def inputBoolBL(en:str='',zh:str='') -> bool:
    '''获取输入，将其转换为布尔值，并按照系统语言选择输入提示字符串'''
    return inputBool(gsbl(en=en,zh=zh))

def inputInt(defaultWhenEmpty:int=0,message:str='') -> int:
    '''获取输入（整数）'''
    return _softParseInt(defaultWhenEmpty=defaultWhenEmpty,context=input(message))
def inputIntBL(defaultWhenEmpty:int=0,en:str='',zh:str='') -> int:
    '''获取输入（整数）并按照系统语言选择输入提示字符串'''
    return inputInt(defaultWhenEmpty=defaultWhenEmpty,message=gsbl(en=en,zh=zh))
def _softParseInt(context:str,defaultWhenEmpty:int=0) -> int:
    return int(context) if context else defaultWhenEmpty

def autoTypeInputBL(inputType:any,en:str='',zh:str='',formatObj:any=None,defaultWhenEmpty=None) -> any:
    message=gsbl(en=en,zh=zh)
    message=message%formatObj if formatObj else message
    if inputType==int:
        return inputInt(defaultWhenEmpty=int(defaultWhenEmpty) if defaultWhenEmpty else 0,message=message)
    elif inputType==bool:
        return inputBool(defaultWhenEmpty=defaultWhenEmpty if defaultWhenEmpty else False,message=message)
    else:
        message=input(message=message)
        return message if message else (defaultWhenEmpty if defaultWhenEmpty else '')
        

# 将消息与路径进行整合

def printPath(message:str,path:str) -> str:
    '''将消息与路径整合在一起'''
    return print(message%('\"'+path+'\"'))

def printPathBL(path:str,en:str,zh:str) -> str:
    '''按照系统语言选择选择消息，并将其与路径整合在一起'''
    return printPath(gsbl(en=en,zh=zh),path=path)

# 报错相关
def printExcept(exc:BaseException,funcPointer:str) -> None:
    '''有提示消息地报错'''
    print(funcPointer+gsbl(en="A exception was found:",zh="\u53d1\u73b0\u5f02\u5e38\uff1a"),exc,"\n"+format_exc())

def catchExcept(err:BaseException,path:str,head:str) -> None:
    '''有提示消息地报错，并分错误码呈现提示消息'''
    if isinstance(err,FileNotFoundError):
        printPathBL(en="%s not found!",zh="\u672a\u627e\u5230%s\uff01",path=path)
    elif isinstance(err,OSError):
        if err.errno==errno.ENOENT:printPathBL(en="%s read/write faild!",zh="\u8bfb\u5199%s\u5931\u8d25\uff01",path=path)
        elif err.errno==errno.EPERM:printPathBL(en="Permission denied!",zh="\u8bbf\u95ee\u88ab\u62d2\u7edd\uff01",path=path)
        elif err.errno==errno.EISDIR:printPathBL(en="%s is a directory!",zh="%s\u662f\u4e00\u4e2a\u76ee\u5f55\uff01",path=path)
        elif err.errno==errno.ENOSPC:printPathBL(en="Not enough equipment space!",zh="\u8bbe\u5907\u7a7a\u95f4\u4e0d\u8db3\uff01",path=path)
        elif err.errno==errno.ENAMETOOLONG:printPathBL(en="The File name is too long!",zh="\u6587\u4ef6\u540d\u8fc7\u957f\uff01",path=path)
        elif err.errno==errno.EINVAL:printPathBL(en="Invalid File name: %s",zh="\u6587\u4ef6\u540d\u65e0\u6548\uff1a%s",path=path)
        else:printPathBL(en="Reading/Writeing %s error!",zh="\u8bfb\u5199\u6587\u4ef6%s\u9519\u8bef\uff01",path=path)
    else:
        printExcept(err,head)

# 文件相关
def readFile(path:str) -> str:
    '''快捷读取文件内容(UTF-8)'''
    try:
        try:
            f=open(path,'r',encoding='utf-8')
            result=f.read()
            f.flush()
        except BaseException:
            f=open(path,'rb')
            result=f.read()
            f.flush()
        return result
    except BaseException as error:return (-1,error,None)
#return (code,binary or error,image or None)

# 配置相关
def getBoolConfigInStr(format:str,index:int) -> bool:
    '''基于单字符表示布尔值的字符串配置读取'''
    return index<len(format) and format[index] not in '-_0 ' #索引在字符串中且不为特定字符