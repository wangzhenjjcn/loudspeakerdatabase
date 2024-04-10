#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os, sys,time,time,json,validators,configparser,re,requests
import requests,threading,pyperclip

from io import BytesIO
import subprocess
from selenium import webdriver 
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from urllib.parse import urljoin
try:
    from tkinter import *
except ImportError:  #Python 2.x
    PythonVersion = 2
    from Tkinter import *
    from tkFont import Font
    from ttk import *
    #Usage:showinfo/warning/error,askquestion/okcancel/yesno/retrycancel
    from tkMessageBox import *
    #Usage:f=tkFileDialog.askopenfilename(initialdir='E:/Python')
    #import tkFileDialog
    #import tkSimpleDialog
else:  #Python 3.x
    PythonVersion = 3
    from tkinter.font import Font
    from tkinter.ttk import *
    from tkinter.messagebox import *
    #import tkinter.filedialog as tkFileDialog
    #import tkinter.simpledialog as tkSimpleDialog    #askstring()



class Application_ui(Frame):
    #这个类仅实现界面生成功能，具体事件处理代码在子类Application中。
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.master.title('数据读取软件')
        self.master.geometry('1163x687')
        self.createWidgets()

    def createWidgets(self):
        self.top = self.winfo_toplevel()
        self.style = Style()

        self.style.configure('FrameLog.TLabelframe',font=('宋体',9))
        self.FrameLog = LabelFrame(self.top, text='运行日志', style='FrameLog.TLabelframe')
        self.FrameLog.place(relx=0.186, rely=0.023, relwidth=0.792, relheight=0.945)

        self.style.configure('FrameChromeOptions.TLabelframe',font=('宋体',9))
        self.FrameChromeOptions = LabelFrame(self.top, text='浏览器操作', style='FrameChromeOptions.TLabelframe')
        self.FrameChromeOptions.place(relx=0.021, rely=0.023, relwidth=0.152, relheight=0.945)

        self.ListLogVar = StringVar(value='')
        self.ListLogFont = Font(font=('宋体',9))
        self.ListLog = Listbox(self.FrameLog, listvariable=self.ListLogVar, font=self.ListLogFont)
        self.ListLog.place(relx=0.026, rely=0.049, relwidth=0.948, relheight=0.912)

        self.style.configure('CommandSaveData.TButton',font=('宋体',9))
        self.CommandSaveData = Button(self.FrameChromeOptions, text='保存数据', command=self.CommandSaveData_Cmd, style='CommandSaveData.TButton')
        self.CommandSaveData.place(relx=0.136, rely=0.468, relwidth=0.729, relheight=0.063)

        self.style.configure('CommandHeadlessChrome.TButton',font=('宋体',9))
        self.CommandHeadlessChrome = Button(self.FrameChromeOptions, text='隐藏浏览器', command=self.CommandHeadlessChrome_Cmd, style='CommandHeadlessChrome.TButton')
        self.CommandHeadlessChrome.place(relx=0.136, rely=0.123, relwidth=0.729, relheight=0.063)

        self.style.configure('CommandReadFromCurrent.TButton',font=('宋体',9))
        self.CommandReadFromCurrent = Button(self.FrameChromeOptions, text='从当前页读取', command=self.CommandReadFromCurrent_Cmd, style='CommandReadFromCurrent.TButton')
        self.CommandReadFromCurrent.place(relx=0.136, rely=0.382, relwidth=0.729, relheight=0.063)

        self.style.configure('CommandReadData.TButton',font=('宋体',9))
        self.CommandReadData = Button(self.FrameChromeOptions, text='读取数据', command=self.CommandReadData_Cmd, style='CommandReadData.TButton')
        self.CommandReadData.place(relx=0.136, rely=0.296, relwidth=0.729, relheight=0.063)

        self.style.configure('CommandCheckStatus.TButton',font=('宋体',9))
        self.CommandCheckStatus = Button(self.FrameChromeOptions, text='检查登录状态', command=self.CommandCheckStatus_Cmd, style='CommandCheckStatus.TButton')
        self.CommandCheckStatus.place(relx=0.136, rely=0.21, relwidth=0.729, relheight=0.063)

        self.style.configure('CommandOpenChrome.TButton',font=('宋体',9))
        self.CommandOpenChrome = Button(self.FrameChromeOptions, text='打开浏览器', command=self.CommandOpenChrome_Cmd, style='CommandOpenChrome.TButton')
        self.CommandOpenChrome.place(relx=0.136, rely=0.037, relwidth=0.729, relheight=0.063)


class Application(Application_ui):
    #这个类实现具体的事件处理回调函数。界面生成代码在Application_ui中。
    def __init__(self, master=None):
        Application_ui.__init__(self, master)
        self.datas={}
        self.config={}
        self.driver=None
        self.cookies=None
        self.showChrome=True
        self.driverInited=False
        self.configInited=False
        self.btnStates=[1,0,0,1,0,0]##打开浏览器、隐藏浏览器、检查、读取、当前读取、保存
        self.initDriver_thread=threading.Thread(target=self.initDriver)
        setBtnStatus_thread=threading.Thread(target=self.setAllBtnStatus)
        setBtnStatus_thread.start()
        self.loginfo("Init success,System Ready!")
        
    def setIconStatus(self):
        try:
            if self.btnStates[0]==1:
                self.CommandOpenChrome['state'] = 'normal'
            else:
                self.CommandOpenChrome['state'] = 'disable'
                
            if self.btnStates[1]==1:
                self.CommandHeadlessChrome['state'] = 'normal'
            else:
                self.CommandHeadlessChrome['state'] = 'disable'
            if self.btnStates[2]==1:
                self.CommandCheckStatus['state'] = 'normal'
            else:
                self.CommandCheckStatus['state'] = 'disable'
            if self.btnStates[3]==1:
                self.CommandReadData['state'] = 'normal'
            else:
                self.CommandReadData['state'] = 'disable'
            if self.btnStates[4]==1:
                self.CommandReadFromCurrent['state'] = 'normal'
            else:
                self.CommandReadFromCurrent['state'] = 'disable'
            if self.btnStates[5]==1:
                self.CommandSaveData['state'] = 'normal'
            else:
                self.CommandSaveData['state'] = 'disable'
        except:
            print("System down!")
            exit()
        
        
        
    def initConfig(self):
        global config_file_path
        
        # Create a ConfigParser object
        config = configparser.ConfigParser()
        
        # Check if the config file exists
        if not os.path.exists(config_file_path):
            self.loginfo("Init Config.ini")
            # Create config file and set initial values if it doesn't exist
            config['DEFAULT'] = {
                'loginurl':'https://loudspeakerdatabase.com/',
                'debugPort': '9222',
                'logLevel': '3',
                'useProxy': 'False',
                'socks5Proxy': 'socks5://127.0.0.1:12345',
                'httpProxy': 'http://127.0.0.1:12346',
                'proxyType' : 'socks5'
            }
            # Write the new configuration to file
            with open(config_file_path, 'w') as configfile:
                config.write(configfile)
        else:
            # Read the existing config file
            self.loginfo("Read the existing config file:"+ config_file_path+" ")
            config.read(config_file_path)
            
            
            
        # 打印 DEFAULT 节下的配置
        self.loginfo("DEFAULT section:")
        for key in config['DEFAULT']:
            self.loginfo(f"{key}: {config['DEFAULT'][key]}")

        # 如果还有其他节，也可以打印出来
        self.loginfo("Current configuration:")
        for section in config.sections():
            for key in config[section]:
                self.loginfo(f"{key}: {config[section][key]}")
        
        self.config=config
        pass
        
    def initDriver(self):
        if not self.configInited:
            self.initConfig()
        #Settings
        loginurl = self.config['DEFAULT']['loginurl']
        debugPort=self.config['DEFAULT']['debugPort']
        logLevel=self.config['DEFAULT']['logLevel']
        useProxy=self.config['DEFAULT']['useProxy']
        socks5Proxy=self.config['DEFAULT']['socks5Proxy']
        httpProxy=self.config['DEFAULT']['httpProxy']
        proxyType=self.config['DEFAULT']['proxyType']
        proxyServer=httpProxy
        if(proxyType=="socks5"):
            proxyServer=socks5Proxy
            
        self.loginfo("Start to init driver")
        self.loginfo("Loading Chrome.")
        global driver,chrome_options
        # 自动安装Chrome驱动
        self.loginfo("Checking Chrome Driver.")
        ChromeDriverManager().install()
        self.loginfo("Inited Chrome Driver.")
        # 启用 Chrome 的日志记录
        capabilities = DesiredCapabilities.CHROME
        capabilities['goog:loggingPrefs'] = {'performance': 'ALL'}
        # 设置 Chrome 选项
        chrome_options = Options()
        # chrome_options.add_argument("--enable-logging")
        # chrome_options.add_experimental_option("perfLoggingPrefs", {"enableNetwork": True})
        chrome_options.add_argument("--log-level="+logLevel) 
        chrome_options.add_argument("--remote-debugging-port="+debugPort)  # 这通常是为了启用性能日志记录
        if not self.showChrome:
            chrome_options.add_argument("--headless")  # 使用 headless 模式，如果不需要可视化浏览器可以开启
        chrome_options.add_argument("--autoplay-policy=no-user-gesture-required")  # 允许自动播放
        chrome_options.add_argument("--mute-audio")
        chrome_options.add_argument('--ignore-ssl-errors')
        chrome_options.add_argument("--ignore-certificate-errors")
        if useProxy==True:
            self.loginfo("--proxyAddress:"+proxyServer)
            chrome_options.add_argument("--proxy-server="+proxyServer) # 代理版本
        # 初始化webdriver
        self.loginfo("Loading driver")
        driver = webdriver.Chrome(options=chrome_options)
        driver.implicitly_wait(10)  # 设置隐式等待时间为10秒
        self.driver=driver
        self.driverInited=True
        self.driver.get(loginurl)
        if self.cookies or os.path.exists("cookies.txt"):
            # 加载并设置cookies
            with open("cookies.txt", "r") as file:
                cookies = json.load(file)
                for cookie in cookies:
                    driver.add_cookie(cookie)
                    self.loginfo("add cookie:"+str(cookie))
            self.driver.get(loginurl)
        
        self.loginfo("Init driver sucess")
        self.btnStates=[0,1,1,1,1,0]##打开浏览器、隐藏浏览器、检查、读取、当前读取、保存
        


    def CommandSaveData_Cmd(self, event=None):
        #TODO, Please finish the function here!
        
        pass
         

    def CommandHeadlessChrome_Cmd(self, event=None):
        #TODO, Please finish the function here!
        self.btnStates=[0,0,1,1,1,0]##打开浏览器、隐藏浏览器、检查、读取、当前读取、保存
        # 保存cookies
        self.showChrome=False
        cookies=None
        if self.driverInited:
            cookies = self.driver.get_cookies()
            with open("cookies.txt", "w") as file:
                file.write(json.dumps(cookies))
            self.driver.quit()
            self.cookies=cookies
        self.driverInited=False
        self.initDriver_thread=threading.Thread(target=self.initDriver)
        self.initDriver_thread.start()
        pass
     
        

    def CommandReadFromCurrent_Cmd(self, event=None):
        #TODO, Please finish the function here!
 
        pass

    def CommandReadData_Cmd(self, event=None):
        self.readData_thread=threading.Thread(target=self.readData)
        self.readData_thread.start()
    

    def CommandCheckStatus_Cmd(self, event=None):
        #TODO, Please finish the function here!
        if self.driverInited:
            cookies = self.driver.get_cookies()
            with open("cookies.txt", "w") as file:
                file.write(json.dumps(cookies))
            self.cookies=cookies
            self.loginfo("LoginStatusSaved")
        else:
            self.loginfo("ChromeErr")
        pass

    def CommandOpenChrome_Cmd(self, event=None):
        #TODO, Please finish the function here!
        self.btnStates=[0,0,0,0,0,0]##打开浏览器、隐藏浏览器、检查、读取、当前读取、保存
        self.initDriver_thread.start()
        
        pass

    def loginfo(self,msg):
        print(msg)
        try:
            self.ListLog.insert('end', str(msg))
            self.ListLog.yview(END)
        except:
            print("System down!")
            exit()
        pass

    def setAllBtnStatus(self):
        while True:
            self.setIconStatus()
            # self.loginfo(self.btnStates)
            time.sleep(0.5)

    def readData(self):
        self.btnStates=[0,0,0,0,0,0]##打开浏览器、隐藏浏览器、检查、读取、当前读取、保存
        try:
            #TODO, Please finish the function here!
            urls=[]
            base_url = "https://loudspeakerdatabase.com"
            for i in range(0,5000,40):
                if len(urls)>=3886:
                    continue
            # for i in range(0,55,40):
                pageUrl='https://loudspeakerdatabase.com/next_page_api/offset='+str(i)
                self.loginfo(str(i)+" - "+pageUrl)
                # 发送GET请求
                response = requests.get(pageUrl)
                # 确保请求成功
                if response.status_code == 200:
                    # Parse the HTML content with BeautifulSoup
                    soup = BeautifulSoup(response.text, 'html.parser')
                    # Find all <a> tags
                    a_tags = soup.find_all('a')            
                    # Extract the href attribute from each <a> tag and complete the URL
                    full_urls = [base_url + a.get('href') for a in a_tags if a.get('href')]
               
                    urls.extend(full_urls)
                else:
                    print(f"请求失败，状态码：{response.status_code}")
                    time.sleep(2)
                
            urlFile = os.path.join(os.getcwd(), 'database',"url.txt")
            with open(urlFile, 'w', encoding='utf-8') as file:
                file.write(str(urls))   
            
            self.datas['readedCount']=0
            self.datas['listedCount']=0
            for speakurl in urls:
                self.datas['listedCount']+=1
                self.loginfo(speakurl)
                if "next_page_api" in speakurl or "offset" in speakurl:
                    self.loginfo("ignore:"+ speakurl)
                    continue
                # 发送GET请求
                
                # 移除协议部分，并分割剩余的URL成路径部分
                path_parts = str(speakurl).replace('http://', '').replace('https://', '').split('/')[1:] # 忽略域名
                # 定义一个名为'database'的基础文件夹，确保它存在
                base_path = os.path.join(os.getcwd(), 'database')
                if not os.path.exists(base_path):
                    os.makedirs(base_path)
                    
                # 逐个处理每个路径部分
                for part in path_parts:
                    base_path = os.path.join(base_path, part)  # 更新当前的基路径
                    if not os.path.exists(base_path):  # 检查这个路径是否存在
                        os.makedirs(base_path)  # 创建文件夹
                        
                        
                self.loginfo("open:"+speakurl)
                
                if (self.datas['listedCount']-self.datas['readedCount']>5):
                    time.sleep(5)
                self.readUrlData_thread=threading.Thread(target=self.readUrlData,args=(speakurl,base_path))
                self.readUrlData_thread.start()
                    
        except Exception as e:
            print("err:")
            print(e)
        self.btnStates=[0,1,1,1,1,1]##打开浏览器、隐藏浏览器、检查、读取、当前读取、保存
        # # 执行 JavaScript，滚动到页面底部
        # self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        # # 使用 PAGE_DOWN 键向下滚动
        # html = self.driver.find_element_by_tag_name('html')
        # html.send_keys(Keys.PAGE_DOWN)
        # self.countData_thread=threading.Thread(target=self.countData)
        # self.countData_thread.start()
        pass


    def readUrlData(self,url,path):
        data_file_path = os.path.join(path, 'data.txt')
        if  os.path.exists(data_file_path):
            self.loginfo(data_file_path+" exists ignore")
            self.datas['readedCount']+=1
            return
        response = requests.get(url)
        # 确保请求成功
        if response.status_code == 200:
            with open(data_file_path, 'w', encoding='utf-8') as file:
                file.write(response.text)   
            print(f"文件 {data_file_path} 已创建。")
        else:
            print(f"请求失败，状态码：{response.status_code}")
            time.sleep(2)
        self.datas['readedCount']+=1
        

    def countData(self):
        # # ID
        # element_by_id = driver.find_element(By.ID, "特定的ID")
        # element_by_id.click()
        try:
            woofer_cards = self.driver.find_elements_by_css_selector('div.results .woofer_card')
            woofer_cards_count = len(woofer_cards)
            print(f"找到的'woofer_card'元素数量为: {woofer_cards_count}")
            
            # 定位到类名为 'results_count' 的span元素
            results_count_element = driver.find_element(By.CLASS_NAME, 'results_count')
            # 获取该元素的文本值
            results_count_text = results_count_element.text
            # 使用正则表达式从文本中提取数字
            numbers_in_text = re.findall('\d+', results_count_text)
            if numbers_in_text:
                # 假设我们只关心第一个匹配的数字
                print(f"从文本中提取的数字是: {numbers_in_text[0]}")
            else:
                print("文本中没有找到数字。")
        except:
            
            pass
    



if __name__ == "__main__":
    # 获取可执行文件的完整路径
    executable_path = sys.argv[0]
    # 获取文件名（不包含路径）
    executable_name = os.path.basename(executable_path)
    directory_path = os.path.dirname(os.path.abspath(executable_path))
    # Define the path for the config file
    config_file_path = directory_path+'\\config.ini'
    # 检查是否为 PyInstaller 打包的环境
    app_path=""
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        # 如果是，使用临时解压目录
        app_path = sys._MEIPASS
    else:
        # 否则使用脚本所在的目录
        app_path = os.path.dirname(os.path.abspath(__file__))
    print("Executable Name:", executable_name,"Directory:",directory_path,"App_path:",app_path," By:WangZhen")
    
    top = Tk()
    Application(top).mainloop()
    try: top.destroy()
    except: pass
