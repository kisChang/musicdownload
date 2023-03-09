import tkinter as tk
import requests
import os
import _thread
import sys

# GitHub用户名、仓库名和软件名称
github_username = 'kisChang'
repo_name = 'musicdownload'
app_name = 'MusicDownloadApp'

# GitHub Releases API的URL
api_url = f'https://api.github.com/repos/{github_username}/{repo_name}/releases/latest'
asset_url_format = 'https://ghproxy.com/https://github.com/{}/{}/releases/download/{}/{}'

# 获取最新版本信息
def get_latest_version():
    response = requests.get(api_url)
    if response.status_code == 200:
        return response.json()['tag_name']
    else:
        return None


# 检查是否需要更新
def check_for_updates_thread(app_version, root):
    latest_version = get_latest_version()
    if latest_version and latest_version != app_version:
        message = f'发现新版本 {latest_version}，是否下载更新？'
        if tk.messagebox.askyesno('更新提示', message):
            _thread.start_new_thread(download_latest_version, (latest_version, root))


def check_for_updates(app_version, root):
    _thread.start_new_thread(check_for_updates_thread, (app_version, root))


# 下载最新版本
def download_latest_version(version, root):
    asset_name = f'{app_name}_v0.{version}.exe'
    asset_url = asset_url_format.format(github_username, repo_name, version, asset_name)
    print('asset_url', asset_url)
    response = requests.get(asset_url)
    if response.status_code == 200:
        with open(asset_name, 'wb') as f:
            f.write(response.content)
        tk.messagebox.showinfo('下载完成', '程序已更新，请重启。')
        current_path_exe = os.path.realpath(sys.executable)
        with open('delete_program.bat', 'w') as f:
            f.write('if "%1"=="hide" goto CmdBegin\n')
            f.write('start mshta vbscript:createobject("wscript.shell").run("""%~0"" hide",0)(window.close)&&exit\n')
            f.write(':CmdBegin\n')
            f.write('@echo off\n')
            f.write('ping -n 5 127.0.0.1 > nul\n')  # 延时5秒，以确保程序已经关闭
            f.write(f'del "{current_path_exe}"\n')
            f.write('del delete_program.bat >nul 2>nul\n')
            f.write('exit\n')
        os.system('start /B delete_program.bat')
        os.system('start "" "' + asset_name + '"')
        root.destroy()
    else:
        tk.messagebox.showerror('下载失败', '下载最新版本失败，请稍后重试。')
