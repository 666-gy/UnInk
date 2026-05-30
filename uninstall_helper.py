# -*- coding: utf-8 -*-
"""
Quick Uninstall Helper - 右键快捷方式直接卸载工具
功能：解析快捷方式目标 → 查找注册表卸载信息 → 执行卸载程序
"""

import sys
import os
import subprocess
import winreg
import ctypes
from pathlib import Path


def parse_shortcut(lnk_path):
    """
    解析快捷方式，获取目标程序路径
    
    Args:
        lnk_path: 快捷方式文件路径 (.lnk)
    
    Returns:
        目标程序路径，失败返回 None
    """
    try:
        import win32com.client
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortcut(lnk_path)
        target = shortcut.TargetPath
        
        if target and os.path.exists(target):
            return os.path.normpath(target)
        return None
    except ImportError:
        # 如果没有 win32com，使用 PowerShell 解析
        try:
            cmd = f'''$sh = New-Object -ComObject WScript.Shell; $lnk = $sh.CreateShortcut("{lnk_path}"); $lnk.TargetPath'''
            result = subprocess.run(
                ['powershell', '-Command', cmd],
                capture_output=True, text=True, timeout=10
            )
            target = result.stdout.strip()
            if target and os.path.exists(target):
                return os.path.normpath(target)
        except:
            pass
    return None


def find_uninstall_info(target_path):
    """
    在注册表中查找软件的卸载信息
    
    Args:
        target_path: 目标程序路径
    
    Returns:
        dict: {'name': 软件名, 'uninstall_cmd': 卸载命令, 'publisher': 发布者}
        未找到返回 None
    """
    target_path = os.path.normpath(target_path).lower()
    target_dir = os.path.dirname(target_path)
    target_name = os.path.basename(target_path)
    
    # 注册表卸载信息位置
    reg_paths = [
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Uninstall"),
    ]
    
    matches = []
    
    for hkey, subkey in reg_paths:
        try:
            with winreg.OpenKey(hkey, subkey) as key:
                i = 0
                while True:
                    try:
                        app_key_name = winreg.EnumKey(key, i)
                        with winreg.OpenKey(key, app_key_name) as app_key:
                            info = {}
                            
                            # 读取各项信息
                            for value_name in ['DisplayName', 'UninstallString', 'QuietUninstallString', 
                                              'InstallLocation', 'Publisher', 'DisplayIcon']:
                                try:
                                    value, _ = winreg.QueryValueEx(app_key, value_name)
                                    info[value_name] = str(value) if value else ""
                                except FileNotFoundError:
                                    info[value_name] = ""
                            
                            # 必须有卸载命令
                            if not info.get('UninstallString'):
                                i += 1
                                continue
                            
                            # 计算匹配分数
                            score = 0
                            
                            # 检查 InstallLocation
                            install_loc = info.get('InstallLocation', '').lower()
                            if install_loc:
                                if target_dir.startswith(install_loc.rstrip('\\').lower()):
                                    score += 100
                            
                            # 检查 DisplayIcon
                            display_icon = info.get('DisplayIcon', '').lower()
                            if display_icon:
                                icon_path = display_icon.split(',')[0]
                                if os.path.exists(icon_path):
                                    if os.path.normpath(icon_path).lower() == target_path:
                                        score += 80
                                    elif os.path.dirname(os.path.normpath(icon_path).lower()) == target_dir:
                                        score += 40
                            
                            # 检查 UninstallString 是否包含目标目录
                            uninstall_str = info.get('UninstallString', '').lower()
                            if target_dir.lower() in uninstall_str:
                                score += 30
                            
                            # 检查软件名是否在目标路径中
                            display_name = info.get('DisplayName', '')
                            if display_name:
                                name_lower = display_name.lower()
                                if name_lower in target_path or name_lower in target_dir:
                                    score += 20
                            
                            if score > 0:
                                matches.append({
                                    'name': info.get('DisplayName', app_key_name),
                                    'uninstall_cmd': info.get('QuietUninstallString') or info.get('UninstallString'),
                                    'publisher': info.get('Publisher', ''),
                                    'score': score
                                })
                        
                        i += 1
                    except OSError:
                        break
        except FileNotFoundError:
            continue
    
    if matches:
        # 按匹配分数排序，返回最佳匹配
        matches.sort(key=lambda x: x['score'], reverse=True)
        best = matches[0]
        return {
            'name': best['name'],
            'uninstall_cmd': best['uninstall_cmd'],
            'publisher': best['publisher']
        }
    
    return None


def confirm_uninstall(software_name, publisher):
    """
    显示确认对话框，询问用户是否卸载
    
    Returns:
        bool: 用户是否确认卸载
    """
    import tkinter as tk
    from tkinter import messagebox
    
    # 创建隐藏的主窗口
    root = tk.Tk()
    root.withdraw()
    
    # 构建确认消息
    msg = f"确定要卸载 {software_name} 吗？"
    if publisher:
        msg += f"\n\n发布者: {publisher}"
    msg += '\n\n点击"确定"将打开卸载程序。'
    
    # 显示确认对话框
    result = messagebox.askokcancel(
        "确认卸载",
        msg,
        icon='warning'
    )
    
    root.destroy()
    return result


def execute_uninstall(uninstall_cmd, software_name):
    """
    执行卸载命令，并等待卸载程序启动
    
    Args:
        uninstall_cmd: 卸载命令字符串
        software_name: 软件名称（用于提示）
    
    Returns:
        bool: 是否成功启动
    """
    if not uninstall_cmd:
        return False
    
    # 处理不同类型的卸载命令
    uninstall_cmd = uninstall_cmd.strip()
    
    # 处理带引号的命令
    if uninstall_cmd.startswith('"'):
        end_quote = uninstall_cmd.find('"', 1)
        if end_quote > 0:
            exe = uninstall_cmd[1:end_quote]
            args = uninstall_cmd[end_quote+1:].strip()
        else:
            exe = uninstall_cmd
            args = ""
    else:
        parts = uninstall_cmd.split(None, 1)
        exe = parts[0]
        args = parts[1] if len(parts) > 1 else ""
    
    try:
        # 使用 subprocess 启动
        startupinfo = subprocess.STARTUPINFO()
        
        process = subprocess.Popen(
            [exe] + (args.split() if args else []),
            shell=True,
            startupinfo=startupinfo
        )
        
        # 等待一小段时间看进程是否成功启动
        import time
        time.sleep(0.5)
        
        # 检查进程是否还在运行（说明启动成功了）
        if process.poll() is None:
            return True
        
        # 如果进程已经结束，可能是 UAC 被拒绝或程序出错
        return True
        
    except Exception as e:
        print(f"执行卸载失败: {e}")
        return False


def main():
    """主函数"""
    # 检查参数
    if len(sys.argv) < 2:
        print("用法: uninstall_helper.exe <快捷方式路径>")
        print('示例: uninstall_helper.exe "C:\\Users\\Desktop\\Chrome.lnk"')
        input("\n按回车键退出...")
        return 1
    
    lnk_path = sys.argv[1]
    
    # 检查文件是否存在
    if not os.path.exists(lnk_path):
        print(f"错误: 找不到文件 '{lnk_path}'")
        input("\n按回车键退出...")
        return 1
    
    # 检查是否是快捷方式
    if not lnk_path.lower().endswith('.lnk'):
        print(f"错误: 不是快捷方式文件")
        input("\n按回车键退出...")
        return 1
    
    print(f"正在分析快捷方式: {os.path.basename(lnk_path)}")
    print("-" * 50)
    
    # 步骤1: 解析快捷方式
    print("1. 解析快捷方式目标...")
    target_path = parse_shortcut(lnk_path)
    
    if not target_path:
        print("   错误: 无法解析快捷方式目标")
        input("\n按回车键退出...")
        return 1
    
    print(f"   目标程序: {target_path}")
    
    # 步骤2: 查找卸载信息
    print("\n2. 查找卸载信息...")
    uninstall_info = find_uninstall_info(target_path)
    
    if not uninstall_info:
        print("   未找到该软件的卸载信息")
        print("\n" + "=" * 50)
        print("   该软件可能是绿色/便携版软件")
        print("   没有注册卸载程序")
        print("=" * 50)
        print(f"\n软件位置: {target_path}")
        print(f"所在文件夹: {os.path.dirname(target_path)}")
        print("\n卸载建议:")
        print("  1. 如需卸载，请手动删除上述文件夹")
        print("  2. 检查是否有残留的配置文件在:")
        print(f"     %APPDATA%\\{os.path.basename(os.path.dirname(target_path))}")
        print(f"     %LOCALAPPDATA%\\{os.path.basename(os.path.dirname(target_path))}")
        input("\n按回车键退出...")
        return 0
    
    print(f"   软件名称: {uninstall_info['name']}")
    if uninstall_info['publisher']:
        print(f"   发布者:   {uninstall_info['publisher']}")
    
    # 步骤3: 用户确认
    print("\n3. 等待用户确认...")
    if not confirm_uninstall(uninstall_info['name'], uninstall_info['publisher']):
        print("   用户取消卸载")
        input("\n按回车键退出...")
        return 0
    
    # 步骤4: 执行卸载
    print("\n4. 启动卸载程序...")
    success = execute_uninstall(uninstall_info['uninstall_cmd'], uninstall_info['name'])
    
    if success:
        print(f"   已启动 {uninstall_info['name']} 的卸载程序")
        print("   请在卸载窗口中完成卸载操作")
        input("\n按回车键关闭此窗口...")
    else:
        print("   启动卸载程序失败")
        input("\n按回车键退出...")
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
