import _thread
import os
import time
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import jsonpath
import requests
import win32api
from tkinterdnd2 import DND_FILES, TkinterDnD

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
    "x-requested-with": "XMLHttpRequest",
}


class GUI:
    def __init__(self, master):
        self.master = master
        self.master.title("全网音乐下载器")

        # 创建三个区域
        self.top_frame = tk.Frame(master, padx=10, pady=10)
        self.middle_frame = tk.Frame(master, padx=10, pady=10)
        self.bottom_frame = tk.Frame(master, padx=10, pady=10)

        # 顶部区域
        self.drives = win32api.GetLogicalDriveStrings()  # 获取所有盘符
        self.drives = self.drives.split('\000')[:-1]
        self.location_label = tk.Label(self.top_frame, text="选择存储位置：", font=('楷体', 15))
        self.location_label.pack(side=tk.LEFT)
        self.location_var = tk.StringVar()
        self.location_var.set(self.drives[len(self.drives) - 1])
        for drive in self.drives:
            drive_radio = tk.Radiobutton(self.top_frame, text=drive, variable=self.location_var, value=drive,
                                         font=('楷体', 13))
            drive_radio.pack(side=tk.LEFT, padx=5, pady=5)

        # 中间区域
        # 设置窗口大小以及出现的位置
        label1 = tk.Label(self.middle_frame, text="方式一、批量下载", font=('楷体', 18))
        label1.grid(row=0, columnspan=3, sticky='W')

        self.file_label = ttk.Label(self.middle_frame, text='拖拽文件到此处即可打开', font=('楷体', 15),
                                    background='#c3d7a8')
        self.file_label.grid(row=1, columnspan=2, sticky="NSEW")
        # 启用点击功能
        self.file_label.bind("<Button-1>", self.open_file_dialog)
        # 启用拖放功能
        self.file_label.drop_target_register(DND_FILES)
        self.file_label.dnd_bind("<<Drop>>", lambda e: self.open_file(e.data))
        self.file_open = tk.Button(self.middle_frame, text='开始下载', font=('楷体', 15), command=self.batch_download)
        self.file_open.grid(row=1, column=2)
        self.curr_file_lines = []
        self.curr_batch_run = False

        label2 = tk.Label(self.middle_frame, text="方式二、单曲下载", font=('楷体', 18))
        label2.grid(row=2, columnspan=3, sticky='W')
        self.label = tk.Label(self.middle_frame, text="请输入下载的歌曲：", font=('楷体', 15))
        self.label.grid(row=3, columnspan=3, sticky='W')
        self.addr = tk.StringVar(value='')
        self.oneName = tk.Entry(self.middle_frame, font=('宋体', 20), textvariable=self.addr, width=25)
        self.oneName.grid(row=4, column=0, padx=5, pady=5)
        # 单选按钮
        self.platfrom = tk.StringVar(value='qq')
        self.r1 = tk.Radiobutton(self.middle_frame, text='网易云', variable=self.platfrom, value='netease',
                                 font=('楷体', 13))
        self.r1.grid(row=4, column=1, padx=5, pady=5)
        self.r2 = tk.Radiobutton(self.middle_frame, text='QQ', variable=self.platfrom, value='qq', font=('楷体', 13))
        self.r2.grid(row=4, column=2, padx=5, pady=5)
        # 下载按钮
        self.button1 = tk.Button(self.middle_frame, text='开始下载', font=('楷体', 15), command=self.one_download)
        self.button1.grid(row=5, column=1, padx=5, pady=5, sticky='w')
        self.button2 = tk.Button(self.middle_frame, text='退出程序', font=('楷体', 15), command=root.quit)
        self.button2.grid(row=5, column=2, padx=5, pady=5, sticky='e')

        # 底部区域
        self.text = tk.Listbox(self.bottom_frame, font=('楷体', 13), width=60, height=15)
        self.text.grid(row=2, columnspan=3, padx=5, pady=5)

        # 整合三个区域
        self.top_frame.pack()
        self.middle_frame.pack()
        self.bottom_frame.pack()

    def open_file_dialog(self, event):
        filetypes = [
            ("文本文件", "*.txt")
            # , ('Python源文件', '*.py')
        ]
        file_name = filedialog.askopenfilename(title='选择单个文件',
                                               filetypes=filetypes,
                                               initialdir='./'  # 打开当前程序工作目录
                                               )
        self.open_file(file_name)

    def open_file(self, file_name):
        try:
            if os.path.isfile(file_name):
                with open(file_name, "r", encoding='utf-8') as f:
                    lens = f.readlines()
                    fn = file_name[file_name.rindex('/') + 1:]
                    self.file_label.config(text='成功加载：{}'.format(fn))
                    self.curr_file_lines = []
                    for line in lens:
                        self.log(line)
                        if len(line.strip()) > 1:
                            self.curr_file_lines.append(line)
                    self.log('共加载{}首歌曲'.format(len(self.curr_file_lines)))
            else:
                self.file_label.config(text='您选择的不是文件！请重新拖放')
        except Exception as e:
            self.log('IoException: {}'.format(e), type='err')
            pass

    def log(self, text, type='info'):
        self.text.insert(tk.END, text)
        if type == 'err':
            self.text.itemconfig(tk.END, {'foreground': 'red'})
        self.text.see(tk.END)
        self.text.update()

    def song_download(self, url, title, author):
        self.log('歌曲:{0}-{1},正在下载...'.format(title, author))
        # 下载
        path = '{0}{1}-{2}.mp3'.format(self.location_var.get(), title, author)
        try:
            if self.down_file(url, path):
                self.log('下载完毕,{0}-{1}'.format(title, author))
            else:
                self.log('下载失败,{0}-{1}'.format(title, author), type='err')
        except Exception as e:
            self.log('下载出错: {}'.format(e), type='err')

    @staticmethod
    def down_file(url, path) -> bool:
        down_res = requests.get(url, headers=headers)
        contentType = down_res.headers['content-type']
        if down_res.status_code == 200 and contentType.find('audio') != -1:
            with open(path, "wb") as code:
                code.write(down_res.content)
            return True
        return False

    def batch_download(self):
        if self.curr_batch_run:
            self.curr_batch_run = False
            self.file_open.configure(text='开始下载')
            return

        if len(self.curr_file_lines) < 1:
            self.log("提示：当前未加载任何歌曲列表，请先拖入文件！！！", type='err')
            return
        else:
            def down_work_thread():
                self.file_open.configure(text='取消下载')
                self.curr_batch_run = True
                count = len(self.curr_file_lines)
                for index, name in enumerate(self.curr_file_lines):
                    if not self.curr_batch_run:
                        break
                    self.log('当前进度：（{}/{}）  开始下载：{}'.format(index + 1, count, name))
                    self.get_music_name(name, self.platfrom.get())
                    time.sleep(1)
                self.file_open.configure(text='开始下载')
                self.curr_batch_run = False

            _thread.start_new_thread(down_work_thread, ())

    def one_download(self):
        name = self.oneName.get()
        platfrom = self.platfrom.get()

        if len(name) < 1:
            self.log("请输入歌曲名称！", type='err')
            return

        def down_one_thread():
            self.get_music_name(name, platfrom)

        _thread.start_new_thread(down_one_thread, ())

    def get_music_name(self, name, platfrom):
        url = 'https://music.liuzhijin.cn/'
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
# pyinstaller  --onefile --windowed -i .\resource\main.ico --additional-hooks-dir=. main.py
if __name__ == '__main__':
    root = TkinterDnD.Tk()
    gui = GUI(root)
    root.geometry('600x650+400+200')
    root.mainloop()
