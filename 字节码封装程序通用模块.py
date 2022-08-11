'''字节码封装程序通用模块 Ver.20220811
功能：封装任何基于文件↔媒体（图片、音频等）的字节码封装
将核心逻辑与用户输入分离，当增加新格式时只需专注算法
'''

from pathlib import Path # 路径处理
from 字符串处理程序通用模块 import * # 字符串处理&国际化文本
# TODO 基于命令行参数的可自定义编解封
# TODO 路径截取&扩展名修改
# TODO 命令行用户输入功能

# 知识点：，路径处理，交互式命令行，面向对象编程

class ByteEncapsulatingProgram:
    
    # 名称标识 #
    programName="UNKNOWN"
    defaultDecasulateSuffix:list=[]
    
    # 构造函数 #
    def __init__(self,name:str=None,
                 defaultDecasulateSuffixes:list=None,
                 fileEncapsulateFunc=None,
                 fileDecapsulateFunc=None,
                 customInputArgvTerms:list=None
    ) -> None:
        __smpInpDef=lambda input,default: input if input else default
        self.programName=__smpInpDef(name,self.programName)
        self.defaultDecasulateSuffix=__smpInpDef(defaultDecasulateSuffixes,self.defaultDecasulateSuffix)
        self.fileEncapsulateFunc=__smpInpDef(fileEncapsulateFunc,self.fileEncapsulateFunc)
        self.fileDecapsulateFunc=__smpInpDef(fileDecapsulateFunc,self.fileDecapsulateFunc)
        self.customInputArgvTerms=__smpInpDef(customInputArgvTerms,self.customInputArgvTerms)
        
        
    # 析构函数 #
    def __del__(self):
        self.programName=None
        self.defaultDecasulateSuffix=None
        self.fileEncapsulateFunc=None
        self.fileDecapsulateFunc=None
        self.argvBoolSpecialOptions=None
        self.customInputArgvTerms=None
        self.numExcept=0
    
    # 处理函数引用&自定义参数需求 #
    fileEncapsulateFunc=None
    '''存储封装函数的引用：function(path:str,customArgvs:dict) -> any\n
    ！返回非空值代表封装成功
    '''
    fileDecapsulateFunc=None
    '''存储解封函数的引用：function(path:str,customArgvs:dict) -> any\n
    ！返回非空值代表解封成功
    '''
    
    customInputArgvTerms:list=[]
    '''处理命令行模式下特定的参数需求。\n
    格式：[(参数名,类型,格式化参数,空时默认值,en提示,zh提示),...] TODO:聚合语言包
    '''
    
    @staticmethod
    def fetchCustomInputArgv(argvs:dict,argvName:str=''):
        return argvs[argvName] if (argvs and argvName in argvs) else None
    
    # 命令行模式 #
    def getCustomInputArgvs(self) -> dict:
        '''从用户的一系列输入中获取一个参数字典，用于自定义命令行模式的参数'''
        result={}
        for varName,inpType,formatObj,defaultWhenEmpty,hintEN,hintZH in self.customInputArgvTerms:
            result[varName]=autoTypeInputBL(inputType=inpType,formatObj=formatObj,defaultWhenEmpty=defaultWhenEmpty,en=hintEN,zh=hintZH)
        return result

    numExcept:int=0
    '''错误计数，用于在多次错误后提示结束程序'''
    def cmdLineMode(self,argv:list):
        '''命令行模式，移植自TWayFoil并泛化为一般式处理函数'''
        print("<===="+Path(argv[0]).stem+"====>")
        while(True):
            try:
                # 请求输入路径、强制封装等「默认参数」
                path=inputBL(en="Please insert PATH:",zh="\u8bf7\u8f93\u5165\u8def\u5f84\uff1a")
                # 处理自定义参数需求
                customInputArgvs=self.getCustomInputArgvs()
                # 处理强制封装解封
                forceEncode=inputBool(getFormedStrByLanguage(format='Y/N:',en="Forced encoding? %s",zh="强制封装？%s"))
                # 开始处理单个项目
                self.handleOnePath(path=path,
                    forceEncode=forceEncode,
                    forceDecode=False if forceEncode else inputBool(gsbl(en="Forced decoding? %s",zh="强制解封？%s")%'Y/N:'),
                    customInputArgvs=customInputArgvs
                )
            except BaseException as e:
                catchExcept(e,path,"cmdLineMode()->")
                self.numExcept+=1
            if self.numExcept>1:
                try:
                    if inputBool(gsbl(en="Do you want to terminate the program?",zh="\u4f60\u60f3\u7ec8\u6b62\u7a0b\u5e8f\u5417\uff1f")+"Y/N:"):
                        break
                except:
                    break
            print()#new line

    def handleOnePath(self,path:str,forceEncode:bool=False,forceDecode:bool=False,customInputArgvs:dict=None):
        '''处理单个文件路径'''
        result=None
        pathO:Path=Path(path)
        if pathO.exists():
            # 第一次计算是封装还是解封（通过重用变量减少代码量）
            result=((pathO.suffix in self.defaultDecasulateSuffix) # 若为默认解封的扩展名（带"."），解封，否则封装
                    if forceEncode == forceDecode # 全真or全假 → 智能决定
                    else (not forceEncode) # 强制封装&强制解封
            )
            # 第二次开始封装/解封（真则解，假则封）
            result=(self.fileDecapsulateFunc(path=path,customArgvs=customInputArgvs) if result
                    else self.fileEncapsulateFunc(path=path,customArgvs=customInputArgvs))
        else:
            result=0
        # 显示消息
        if result: # 成功
            printFormedBL(format=(path,result.name),en="File \"%s\" has been successfully converted to \"%s\"!",zh="文件「%s」已成功转换为「%s」！")
        elif result==0: # 文件不存在
            printFormedBL(format=path,en="File \"%s\" is not exist!",zh="文件「%s」不存在！")
        else: # 失败
            printFormedBL(format=path,en="Failed to convert file \"%s\"!",zh="文件「%s」转换失败！")

    # 特殊布尔参数 #
    
    argvBoolSpecialOptions:dict={}
    '''泛化并用于处理命令行输入指令时附带的类似「-r」一类布尔值参数'''
    
    def getBoolCLSettingsInArgv(self,argv:list) -> dict:
        result:dict={}
        for boolSName,boolSValue in self.argvBoolSpecialOptions.items():
            result[boolSName]=boolSValue in argv
        return result
    
    @staticmethod
    def getBoolCLSetting(settings,key:any) -> bool:
        return key in settings and settings[key]
            
    # 主函数模式 #
    def executeAsMain(self,argv:list) -> None:
        '''以主函数形式运行；命令行默认将"-e"与"-d"作为强制封装、解封之特殊布尔参数'''
        boolCLSettings:dict=self.getBoolCLSettingsInArgv(argv=argv)
        if len(argv)>1:# 若有参数则根据参数进行处理
            for path in argv[1:]:
                self.handleOnePath(path=path,
                    forceEncode=self.getBoolCLSetting(settings=boolCLSettings,key="-e"),
                    forceDecode=self.getBoolCLSetting(settings=boolCLSettings,key="-d")
                )
        else: # 否则进入命令行模式
            self.cmdLineMode(argv=argv)
