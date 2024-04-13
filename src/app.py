#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os, sys,time,time,json,configparser,requests,threading
# import pyperclip,re,validators
import pandas as pd
# from io import BytesIO
# import subprocess
from selenium import webdriver 
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
 
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
        self.CommandReadFromCurrent = Button(self.FrameChromeOptions, text='解析数据', command=self.CommandReadFromCurrent_Cmd, style='CommandReadFromCurrent.TButton')
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
        self.btnStates=[1,0,0,1,1,0]##打开浏览器、隐藏浏览器、检查、读取、当前读取、保存
        self.initDriver_thread=threading.Thread(target=self.initDriver)
        setBtnStatus_thread=threading.Thread(target=self.setAllBtnStatus)
        setBtnStatus_thread.start()
        if not self.configInited:
            self.initConfig()
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
                'proxyType' : 'socks5',
                'maxPage' :'5000'
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
        self.btnStates=[1,1,1,0,0,0]##打开浏览器、隐藏浏览器、检查、读取、当前读取、保存
        self.decodeData_thread=threading.Thread(target=self.decodeData)
        self.decodeData_thread.start()
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
            base_path = os.path.join(os.getcwd(), 'database')
            if not os.path.exists(base_path):
                os.makedirs(base_path)
            #TODO, Please finish the function here!
            urls=[]
            imgs=[]
            base_url = "https://loudspeakerdatabase.com"
            maxnum=int(self.config['DEFAULT']['maxPage'])
            if maxnum==None or maxnum<1:
                maxnum=5000
            for i in range(0,maxnum,80):
               
                try:
                    pageUrl='https://loudspeakerdatabase.com/next_page_api/offset='+str(i)
                    self.loginfo(str(len(urls))+"/"+str(i)+" - "+pageUrl)
                    # 发送GET请求
                    response = requests.get(pageUrl)
                    # 确保请求成功
                    if response.status_code == 200:
                        # Parse the HTML content with BeautifulSoup
                        response.encoding = 'utf-8'
                        soup = BeautifulSoup(response.text, 'html.parser',from_encoding='utf-8')
                        # Find all <a> tags
                        a_tags = soup.find_all('a')   
                        img_tags = soup.find_all('img')          
                        # Extract the href attribute from each <a> tag and complete the URL
                        full_urls = [base_url + a.get('href') for a in a_tags if a.get('href')]
                        full_imgurls = [base_url + img.get('src') for img in img_tags if img.get('src')]
                        urls.extend(full_urls)
                        imgs.extend(full_imgurls)
                        if len(full_urls)<1:
                            continue
                    else:
                        print(f"请求失败，状态码：{response.status_code}")
                        time.sleep(2)
                        break
                except Exception as e:
                    print(e)
                    break
                finally:
                    pass
                    # if len(urls)==startlen:
                    #     i=i+40    
                    # else:
                    #     i=starti+len(urls)-startlen
                
            urlFile = os.path.join(os.getcwd(), 'database',"url.txt")
            imgFile = os.path.join(os.getcwd(), 'database',"img.txt")
            with open(urlFile, 'w', encoding='utf-8') as file:
                file.write(str(urls))   
            with open(imgFile, 'w', encoding='utf-8') as file2:
                file2.write(str(imgs)) 
            self.datas['readedCount']=0
            self.datas['listedCount']=0
            
            for speakurl in urls:
                self.datas['listedCount']+=1
                # self.loginfo(speakurl)
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
                # self.loginfo("open:"+speakurl)
                if (self.datas['listedCount']-self.datas['readedCount']>10):
                    time.sleep(1)
                self.readUrlData_thread=threading.Thread(target=self.readUrlData,args=(speakurl,base_path))
                self.readUrlData_thread.start()      
        except Exception as e:
            print("err:")
            print(e)
        self.btnStates=[0,1,1,1,1,1]##打开浏览器、隐藏浏览器、检查、读取、当前读取、保存
        self.loginfo("Task End Submit!")
        # # 执行 JavaScript，滚动到页面底部
        # self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        # # 使用 PAGE_DOWN 键向下滚动
        # html = self.driver.find_element_by_tag_name('html')
        # html.send_keys(Keys.PAGE_DOWN)
        # self.countData_thread=threading.Thread(target=self.countData)
        # self.countData_thread.start()
        pass



    def readUrlData(self,url,path):
        # 定义请求头部
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7,ja;q=0.6',
            'Cookie': '_ga=GA1.1.860630619.1712469598; _ym_uid=1712469598459879214; _ym_d=1712469598; _ym_isad=1; _ym_visorc=w; _clck=1aibkm1|2|fkt|0|1558; _clsk=1e8r1f9|1712719918134|1|1|i.clarity.ms/collect; _lsdb_v2_nouser_session=bHVja3k=--OITgVblbmDQoISeWu0gmrj/eUsGI6juNheOfn4aDdB4BuV9Gg9xxXFihAF+PyLshZss2Qwtvr4dxMadATDpyBBUT35mkSVfwcaUgvA49RTUcxpr89Sf+eYrkurQz3PyR; _ga_0Z8NXL8KJP=GS1.1.1712719909.4.1.1712719968.0.0.0',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
        }
        
        data_file_path = os.path.join(path, 'data.html')
        decodedata_file_path = os.path.join(path, 'data.json')
        if  os.path.exists(data_file_path):
            # self.loginfo(data_file_path+" exists ignore")
            self.datas['readedCount']+=1
            # self.loginfo(self.datas['readedCount'])
            return
        response = requests.get(url, headers=headers)
        # 确保请求成功
        # if "basudgan8 SAMPLE TEXT sd78n" in response.text:
        #     self.datas['readedCount']+=1
        #     self.loginfo(self.datas['readedCount'])
        #     return
        if response.status_code == 200:
            response.encoding = 'utf-8'
            loudspeaker=self.decodeDataByHtml(response.text) 
            with open(data_file_path, 'w', encoding='utf-8') as file:
                file.write(response.text)   
            with open(decodedata_file_path, 'w', encoding='utf-8') as file:
                file.write(str(loudspeaker))   
            # print(f"文件 {data_file_path} 已创建。")
            self.downloadPdfData(response.text,path)
            self.downloadImgData(response.text,path)
            # print(loudspeaker)
        else:
            # print(f"请求失败，状态码：{response.status_code}")
            time.sleep(2)
        self.datas['readedCount']+=1
    
    def downloadPdfData(self,html,path):
        # 使用BeautifulSoup解析HTML
        soup = BeautifulSoup(html, 'html.parser',from_encoding='utf-8')

        # 找到class为'datasheet'的div
        datasheet_div = soup.find('div', class_='datasheet')

        # 初始化基础URL
        base_url = 'https://loudspeakerdatabase.com'

        # 检查是否找到了目标div
        if datasheet_div:
            # 在datasheet div中找到第一个a标签
            first_a_tag = datasheet_div.find('a')
            
            if first_a_tag:
                # 获取a标签的href属性值
                href_value = first_a_tag.get('href', '')
                # 补齐链接地址
                full_url = base_url + href_value
                # 打印完整的链接地址
                # print(f"Full URL: {full_url}")
                filename = os.path.basename(href_value)
                file_path = os.path.join(path, filename)
                if  os.path.exists(file_path):
                    # self.loginfo(file_path+" exists ignore")
                    return
                try:
                    # 获取pdf数据
                    pdf_data=None
                    if not base_url in href_value:
                        pdf_data = requests.get(full_url).content
                    else:
                        pdf_data = requests.get(href_value).content
                    if pdf_data==None:
                        return
                    # 保存pdf
                    with open(file_path, 'wb') as file:
                        file.write(pdf_data)
                    # print(f"pdf {filename} 已被保存到 {file_path}")
                except Exception as e:
                    # print(f"下载pdf {filename} 失败: {e}")        
                    time.sleep(2)
                
    
        
    def downloadImgData(self,html,path):
        base_url = "https://loudspeakerdatabase.com"
        # 使用 BeautifulSoup 解析 HTML
        soup = BeautifulSoup(html, 'html.parser',from_encoding='utf-8')
        # 寻找所有的图片链接
        img_tags = soup.find_all('img')
        
        # 对于找到的每一个 img 标签
        for img in img_tags:
            # 获取图片的 URL
            img_url = img.get('src')
            # 如果 img_url 有效
            if img_url:
                # 获取图片文件名
                filename = os.path.basename(img_url)
                basename=os.path.basename(path)
                # 完整的文件路径
                file_path = os.path.join(path, filename)
                if  os.path.exists(file_path):
                    # self.loginfo(file_path+" exists ignore")
                    return
                if not basename in filename:
                    return
                # 尝试下载并保存图片
                try:
                    # 获取图片数据
                    img_data=None
                    if not base_url in img_url:
                        img_data = requests.get(base_url+img_url).content
                    else:
                        img_data = requests.get(img_url).content
                    if img_data==None:
                        return
                    # 保存图片
                    with open(file_path, 'wb') as file:
                        file.write(img_data)
                    # print(f"图片 {filename} 已被保存到 {file_path}")
                except Exception as e:
                    # print(f"下载图片 {filename} 失败: {e}")        
                    time.sleep(2)
    
    def decodeData(self):
        # 初始化一个空数组来存储符合条件的文件路径
        files = []
        datas=[]
        base_path = os.path.join(os.getcwd(), 'database')
        # 使用os.walk()遍历start_dir下的所有文件夹及其子文件夹
        for dirpath, dirnames, filenames in os.walk(base_path):
            # 检查当前遍历的文件夹内是否存在文件名为'data.html'的文件
            if 'data.html' in filenames:
                # 构建完整的文件路径并添加到files数组中
                files.append(os.path.join(dirpath, 'data.html'))
        self.loginfo("All data:"+str(len(files)))
        for datafile in files:
            # print(datafile)
            try:
                with open(datafile, 'r', encoding='utf-8') as file:
                    html = file.read()
                    loudspeaker=self.decodeDataByHtml(html) 
                    datas.append(loudspeaker)
                    # print(loudspeaker)
            except Exception as e:
                print(e)
           
        # print(datas)
     
        # 处理所有数据，将它们转换为平铺的字典格式
        flattened_data_list = [flatten(item) for item in datas]
        # 创建DataFrame
        df = pd.DataFrame(flattened_data_list)
        df.to_excel(base_path+"/speaker_data.xlsx", index=False)  
        self.btnStates=[1,1,1,0,1,1]##打开浏览器、隐藏浏览器、检查、读取、当前读取、保存
        pass        

   


    def decodeDataByHtml(self,html):
        # print(html)
        loudspeaker={}
        soup = BeautifulSoup(html, 'html.parser',from_encoding='utf-8')
        # Find the div with class 'title'
        title_div = soup.find('div', class_='title')
        # Check if the div is found
        if title_div:
            # Find the span with class 'brand' within the div
            brand_span = title_div.find('span', class_='brand')
            if brand_span:
                # print(f"Brand: {brand_span.text}")
                loudspeaker['brand']=brand_span.text
            # Find the span with class 'ref' within the div
            ref_span = title_div.find('span', class_='ref')
            if ref_span:
                # print(f"Ref: {ref_span.text}")
                loudspeaker['ref']=ref_span.text
            
       
        
        
        # Find the div with the class 'essentials'
        essentials_div = soup.find('div', class_='essentials')
    
        # Check if the essentials div is found
        if essentials_div:
            # 在'essentials' div中找到所有的div元素
            all_divs = essentials_div.find_all('div')

            for div in all_divs:
                # 获取每个div的class属性值，class是一个列表，所以我们使用' '.join将其转换为字符串
                class_value = ' '.join(div.get('class', []))  # 如果没有class属性，返回空列表

                # 获取每个div的data-highlight属性值
                data_highlight_value = div.get('data-highlight', '')  # 如果没有data-highlight属性，则返回空字符串
                
                # 获取div的文本内容
                text_value = div.text.strip()  # .strip()移除字符串开头和结尾的空白符

                # 打印结果
                # print(f"Class: {class_value}, Data-Highlight: {data_highlight_value}, Text: {text_value}")

                if data_highlight_value not in loudspeaker.keys():
                    loudspeaker[data_highlight_value]={}
                loudspeaker[data_highlight_value][class_value]=text_value
        # 找到class为'params'的div
        params_div = soup.find('div', class_='params')

        # 如果找到了params div，进行处理
        if params_div:
            # 在params div中找到所有的div元素
            all_divs = params_div.find_all('div')
            
            for div in all_divs:
                # 获取div的class属性值，因为一个标签可以有多个class，这里我们取全部
                paramsclass_values = ' '.join(div.get('class', []))
                
                # 获取div的data-highlight属性值
                paramsdata_highlight = div.get('data-highlight', 'None')
                
                # 获取div的文本内容
                paramstext_data = div.text.strip()
                
                # 打印结果
                # print(f"Class: {class_values}, Data-Highlight: {data_highlight}, Text: {text_data}")
                if   paramsdata_highlight not in loudspeaker.keys():
                    loudspeaker[paramsdata_highlight]={}
                loudspeaker[paramsdata_highlight][paramsclass_values]=paramstext_data
        # print(loudspeaker)
        return loudspeaker





# 将JSON数据转换为DataFrame需要的格式
# 这个函数会递归地处理嵌套字典，并将它们平铺开
def flatten(data, prefix=''):
    items = []
    for k, v in data.items():
        new_key = prefix + k if prefix else k
        if isinstance(v, dict):
            items.extend(flatten(v, new_key + '_').items())
        else:
            items.append((new_key, v))
    return dict(items)






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
