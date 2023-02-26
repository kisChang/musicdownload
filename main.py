# 导入模块
import tkinter as tk
import requests
import jsonpath
import os
import win32api
from urllib.request import urlretrieve

class GUI:
    def __init__(self, master):
        self.master = master
        master.title("全网音乐下载器")

        # 创建三个区域
        self.top_frame = tk.Frame(master, padx=10, pady=10)
        self.middle_frame = tk.Frame(master, padx=10, pady=10)
        self.bottom_frame = tk.Frame(master, padx=10, pady=10)

        # 顶部区域
        self.drives = win32api.GetLogicalDriveStrings()  # 获取所有盘符
        self.drives = self.drives.split('\000')[:-1]
        self.location_label = tk.Label(self.top_frame, text="选择存储位置：", font=('楷体', 18))
        self.location_label.pack(side=tk.LEFT)
        self.location_var = tk.StringVar()
        self.location_var.set(self.drives[0])
        for drive in self.drives:
            drive_radio = tk.Radiobutton(self.top_frame, text=drive, variable=self.location_var, value=drive)
            drive_radio.pack(side=tk.LEFT, padx=5, pady=5)

        # 中间区域
        # 设置窗口大小以及出现的位置
        self.label = tk.Label(self.middle_frame, text="请输入下载的歌曲", font=('楷体', 18))
        self.label.grid(row=0, columnspan=2, pady=5)
        self.addr = tk.StringVar(value='')
        self.entry = tk.Entry(self.middle_frame, font=('宋体', 20), textvariable=self.addr, width=25)
        self.entry.grid(row=1, column=0, padx=5, pady=5)
        # 单选按钮
        self.var = tk.StringVar(value='netease')
        self.r1 = tk.Radiobutton(self.middle_frame, text='网易云', variable=self.var, value='netease')
        self.r1.grid(row=1, column=1, padx=5, pady=5)
        self.r2 = tk.Radiobutton(self.middle_frame, text='QQ', variable=self.var, value='qq')
        self.r2.grid(row=1, column=2, padx=5, pady=5)
        # 下载按钮
        self.button1 = tk.Button(self.middle_frame, text='开始下载', font=('楷体', 15), command=self.get_music_name)
        self.button1.grid(row=3, column=1, padx=5, pady=5, sticky='w')
        self.button2 = tk.Button(self.middle_frame, text='退出程序', font=('楷体', 15), command=root.quit)
        self.button2.grid(row=3, column=2, padx=5, pady=5, sticky='e')

        # 底部区域
        self.text = tk.Listbox(self.bottom_frame, font=('楷体', 16), width=50, height=15)
        self.text.grid(row=2, columnspan=3, padx=5, pady=5)

        # 整合三个区域
        self.top_frame.pack()
        self.middle_frame.pack()
        self.bottom_frame.pack()

    def song_download(self, url, title, author):
        # 创建文件夹
        os.makedirs("music", exist_ok=True)
        path = 'music\{}.mp3'.format(title)
        self.text.insert(tk.END, '歌曲:{0}-{1},正在下载...'.format(title, author))
        # 文本框滑动
        self.text.see(tk.END)
        # 更新
        self.text.update()
        # 下载
        urlretrieve(url, path)
        self.text.insert(tk.END, '下载完毕,{0}-{1},请试听'.format(title, author))
        # 文本框滑动
        self.text.see(tk.END)
        # 更新
        self.text.update()

    def get_music_name(self):
        """
        搜索歌曲名称
        :return:
        """
        name = self.entry.get()
        platfrom = self.var.get()
        url = 'https://music.liuzhijin.cn/'
        headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
            "x-requested-with": "XMLHttpRequest",
        }
        param = {
            "input": name,
            "filter": "name",
            "type": platfrom,
            "page": 1,
        }
        res = requests.post(url, data=param, headers=headers)
        json_text = res.json()

        title = jsonpath.jsonpath(json_text, '$..title')
        author = jsonpath.jsonpath(json_text, '$..author')
        url = jsonpath.jsonpath(json_text, '$..url')
        self.song_download(url[0], title[0], author[0])


# .py to .exe :
# pyinstaller --onefile -w 'main.py'
# pyinstaller -F -w 'main.py'
if __name__ == '__main__':
    root = tk.Tk()
    gui = GUI(root)
    root.geometry('600x600+400+200')
    root.mainloop()