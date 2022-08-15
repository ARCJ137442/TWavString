'''字节码封装程序通用模块 Ver.20220811
功能：封装任何基于文件↔媒体（图片、音频等）的字节码封装
将核心逻辑与用户输入分离，当增加新格式时只需专注算法
'''

from pathlib import Path # 路径处理
from 字符串处理程序通用模块 import * # 字符串处理&国际化文本
# TODO 基于命令行参数的可自定义编解封
# TODO 路径截取&扩展名修改
# TODO 命令行用户输入功能

# 知识点：路径处理，交互式命令行，面向对象编程

class ByteEncapsulatingProgram:
    
    # 名称标识 #
    programName:str="UNKNOWN"
    '''存储程序名称'''
    
    programVersion:str=None
    '''存储程序版本'''
    
    defaultDecasulateSuffixes:list
    '''存储程序默认进行解压的扩展名'''
    
    defaultEncasulateSuffix:str=None
    '''存储程序默认压缩成的扩展名'''
    
    # 构造函数 #
    def __init__(self,name:str=None,version:str=None,
                 defaultEncasulateSuffix:list=None,
                 defaultDecasulateSuffixes:list=None,
                 fileEncapsulateFunc=None,
                 fileDecapsulateFunc=None,
                 customInputArgvTerms:list=None
    ) -> None:
        __smpInpDef=lambda input,default: input if input else default
        self.programName=__smpInpDef(name,self.programName)
        self.programVersion=__smpInpDef(version,self.programVersion)
        self.defaultEncasulateSuffix=__smpInpDef(defaultEncasulateSuffix,self.defaultEncasulateSuffix)
        self.defaultDecasulateSuffixes=__smpInpDef(defaultDecasulateSuffixes,[self.defaultEncasulateSuffix])
        self.fileEncapsulateFunc=__smpInpDef(fileEncapsulateFunc,self.fileEncapsulateFunc)
        self.fileDecapsulateFunc=__smpInpDef(fileDecapsulateFunc,self.fileDecapsulateFunc)
        self.customInputArgvTerms=__smpInpDef(customInputArgvTerms,self.customInputArgvTerms)
        
        
    # 析构函数 #
    def __del__(self) -> None:
        self.programName=None
        self.programVersion=None
        self.defaultDecasulateSuffixes=None
        self.defaultEncasulateSuffix=None
        self.fileEncapsulateFunc=None
        self.fileDecapsulateFunc=None
        self.argvBoolSpecialOptions=None
        self.customInputArgvTerms=None
        self.numExcept=0
        self.cachedCustomInputArgvs=None
    
    # 处理函数引用&自定义参数需求 #
    fileEncapsulateFunc=None
    '''存储封装函数的引用：function(path:str,outPath:str,customArgvs:dict) -> any\n
    ！返回非空值代表封装成功
    '''
    fileDecapsulateFunc=None
    '''存储解封函数的引用：function(path:str,outPath:str,customArgvs:dict) -> any\n
    ！返回非空值代表解封成功
    '''
    
    customInputArgvTerms:list=[]
    '''处理命令行模式下特定的参数需求。\n
    格式：[(参数名,类型,格式化参数,空时默认值,限定提供情况标签,en提示,zh提示),...] TODO:聚合语言包
    限定提供情况标签：指定是否仅在封装/解封时要求输入，0为不限，-仅封装，+仅解封
    '''
    
    def getCustomInputArgv(self,argvs:dict=None,argvName:str='') -> any:
        '''从用户输入的自定义参数中获取某个自定义参数；\n
        在字典空余时，若有缓存的自定义参数，则优先直接读取而不要求输入'''
        return argvs.get(argvName) if argvs else self.getCustomInputArgv(argvs=self.cachedCustomInputArgvs,argvName=argvName)
    
    def generateCustomInputArgvs(self,modeFlag:int=0,toPutIn:dict=None) -> dict:
        '''从用户的一系列输入中获取一个参数字典，用于自定义命令行模式的参数\n
        情况标签：指定是否仅在封装/解封时要求输入，0为不限，-仅封装，+仅解封
        '''
        result={} if toPutIn==None else toPutIn # 区分None与{}
        for varName,inpType,formatObj,defaultWhenEmpty,limitingFlag,hintEN,hintZH in self.customInputArgvTerms:
            if modeFlag*limitingFlag>=0: # 仅在任一方不限或模式标签相同时请求输入
                result[varName]=autoTypeInputBL(inputType=inpType,formatObj=formatObj,defaultWhenEmpty=defaultWhenEmpty,en=hintEN,zh=hintZH)
        return result
    
    cachedCustomInputArgvs:dict={}
    '''缓存了的对象列表'''
    
    isEncapsulateArgvsCached:bool=False
    '''程序是否缓存了封装相关的自定义参数'''
    
    isDecapsulateArgvsCached:bool=False
    '''程序是否缓存了解封相关的自定义参数'''
    
    def isCustomInputArgvsCached(self,modeFlag:int=0) -> bool:
        return (modeFlag>0 or self.isEncapsulateArgvsCached) and (modeFlag<0 or self.isDecapsulateArgvsCached)
        
    def cacheCustomInputArgvs(self,modeFlag:int=0) -> dict:
        '''向程序缓存设置，用于在有参数模式下减少非必要重复参数输入\n
        情况标签：指定是否仅在封装/解封时要求输入，0为不限，-仅封装，+仅解封'''
        self.generateCustomInputArgvs(modeFlag=modeFlag,toPutIn=self.cachedCustomInputArgvs)
        # 更新标签
        if modeFlag<=0: self.isEncapsulateArgvsCached=True
        if modeFlag>=0: self.isDecapsulateArgvsCached=True
    
    def deleteCachedCustomArgvs(self) -> None:
        self.isEncapsulateArgvsCached=False
        self.isDecapsulateArgvsCached=False
        self.cachedCustomInputArgvs={}
    
    # 命令行模式 #
    numExcept:int=0
    '''错误计数，用于在多次错误后提示结束程序'''
    def cmdLineMode(self,argv:list) -> None:
        '''命令行模式，移植自TWayFoil并泛化为一般式处理函数'''
        print("<====%s%s====>"%(self.programName,
            ' Ver '+self.programVersion if self.programVersion else '')
        )
        pathO:Path
        while(True):
            try:
                # 请求输入路径（提前判断不存在）
                while True:
                    path=inputBL(en="Please insert path:",zh="\u8bf7\u8f93\u5165\u8def\u5f84\uff1a")
                    pathO=Path(path)
                    if not (pathO and pathO.exists()):
                        printFormedBL(format=path,en="File \"%s\" is not exist!",zh="文件「%s」不存在！") or print() # 用or加上一行空行
                    else:
                        break
                # 处理强制封装解封
                forceEncode=inputBool(getFormedStrByLanguage(format='Y/N:',en="Forced encoding? %s",zh="强制封装？%s"))
                # 开始处理单个项目
                self.handleOnePath(path=path,
                    forceEncode=forceEncode,
                    forceDecode=False if forceEncode else inputBool(gsbl(en="Forced decoding? %s",zh="强制解封？%s")%'Y/N:'),
                    customInputArgvs=None
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

    def handleOnePath(self,path:str,forceEncode:bool=False,forceDecode:bool=False,customInputArgvs:dict=None) -> None:
        '''处理单个文件路径（不检查路径是否存在）'''
        result=None
        # 第一次计算是封装还是解封（通过重用变量减少代码量）
        result=((Path(path).suffix in self.defaultDecasulateSuffixes) # 若为默认解封的扩展名（带"."），解封，否则封装
                if forceEncode == forceDecode # 全真or全假 → 智能决定
                else (not forceEncode) # 强制封装&强制解封
        )
        # 若无自定义输入则要求输入自定义参数（无参数模式中强制要求）
        modeFlag:int=1 if result else -1
        if customInputArgvs==None: # 区分None与空字典
            customInputArgvs=self.generateCustomInputArgvs(modeFlag=modeFlag)# 正解负加
        else: # 若有（非命令行模式）则只要求输入一次（使用缓存系统）
            if not self.isCustomInputArgvsCached(modeFlag=modeFlag):
                self.cacheCustomInputArgvs(modeFlag=modeFlag) # 缓存
            customInputArgvs=self.cachedCustomInputArgvs
        # 生成输出路径
        pathO:Path=Path(path)
        outPath:str=(str(pathO.with_name(pathO.stem)) if result
            else str(pathO.with_name(pathO.name+self.defaultEncasulateSuffix))
        )
        # 第二次开始封装/解封（真则解，假则封）
        result=(self.fileDecapsulateFunc(path=path,outPath=outPath,customArgvs=customInputArgvs) if result
            else self.fileEncapsulateFunc(path=path,outPath=outPath,customArgvs=customInputArgvs)
        )
        # 显示消息
        if result: # 成功
            printFormedBL(format=(path,outPath),en="File \"%s\" has been successfully converted to \"%s\"!",zh="文件「%s」已成功转换为「%s」！")
        else: # 失败
            printFormedBL(format=path,en="Failed to convert file \"%s\"!",zh="文件「%s」转换失败！")

    # 特殊布尔参数 #
    
    argvBoolSpecialOptions:dict={}
    '''泛化并用于处理命令行输入指令时附带的类似「-r」一类布尔值参数'''
    
    def getBoolCLSettingsInArgv(self,argv:list) -> dict:
        '''返回{setting1:True,setting2:False}类似的字典'''
        result:dict={}
        for boolSName,boolSValue in self.argvBoolSpecialOptions.items():
            result[boolSName]=boolSValue in argv
        return result
    
    @staticmethod
    def getBoolCLSetting(settings:dict,key:any) -> bool:
        return key in settings and settings[key]
            
    # 主函数模式 #
    def executeAsMain(self,argv:list) -> None:
        '''以主函数形式运行；命令行默认将"-e"与"-d"作为强制封装、解封之特殊布尔参数'''
        if len(argv)>1:# 若有参数则根据参数进行处理
            # 处理自定义参数
            self.cachedCustomInputArgvs.update(self.getBoolCLSettingsInArgv(argv=argv)) # 并入输入参数中的自定义参数
            for path in argv[1:]:
                # 开始逐个处理路
                if Path(path).exists():
                    self.handleOnePath(path=path,
                        forceEncode=self.getBoolCLSetting(settings=self.cachedCustomInputArgvs,key="-e"),
                        forceDecode=self.getBoolCLSetting(settings=self.cachedCustomInputArgvs,key="-d"),
                        customInputArgvs=self.cachedCustomInputArgvs
                    )
        else: # 否则进入命令行模式
            self.cmdLineMode(argv=argv)
