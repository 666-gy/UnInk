# Unlnk

> 右键快捷方式，一键直达卸载

像手机长按图标卸载一样简单，Windows 右键菜单增强工具。

![Windows](https://img.shields.io/badge/Windows-10%2F11-blue?logo=windows)
![Python](https://img.shields.io/badge/Python-3.8+-green?logo=python)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 为什么需要这个工具？

| 场景 | 传统方式 | Unlnk |
|------|---------|-----------------|
| 卸载软件 | 设置 → 应用 → 找到软件 → 卸载 | 右键快捷方式 → 卸载 |
| 绿色软件 | 找不到卸载入口，手动删文件夹 | 自动识别，提示删除位置 |
| 多软件卸载 | 反复打开设置 | 桌面直接操作 |

---

## 安装

### 方式一：直接下载（推荐）

1. 下载 [Releases](https://github.com/666-gy/Unlnk/releases) 中的 `Unlnk.zip`
2. 解压后依次双击`bulid.bat`和`install.bat`
3. 完成！右键任意快捷方式即可使用

### 方式二：从源码构建

```bash
# 克隆仓库
git clone https://github.com/666-gy/Unlnk.git
cd Unlnk

# 构建可执行文件
build.bat

# 安装右键菜单
install.bat
```

---

## 使用

### 标准软件（有卸载程序）

```
右键快捷方式 → 显示更多选项 → Uninstall This App
```

流程：
1. 解析快捷方式目标
2. 查找注册表卸载信息
3. 弹出确认对话框
4. 打开软件自带卸载程序

### 绿色软件（无卸载程序）

自动识别便携软件，显示软件位置和手动卸载建议：

```
==================================================
   该软件为绿色/便携版本
   未注册系统卸载程序
==================================================

软件位置: D:\Tools\Tor Browser\Browser\firefox.exe
所在目录: D:\Tools\Tor Browser

卸载建议:
  1. 直接删除上述文件夹即可卸载
  2. 检查配置残留:
     %APPDATA%\Tor Browser
     %LOCALAPPDATA%\Tor Browser
```

---

## 功能特性

- ⚡ **快速直达** - 右键快捷方式直接打开卸载程序
- 🎯 **智能识别** - 自动区分安装版和绿色版软件
- 🛡️ **安全确认** - 卸载前弹出确认对话框，防止误操作
- 📁 **路径提示** - 绿色软件显示完整路径和卸载建议
- 🔧 **易于安装** - 一键安装/卸载，无需复杂配置

---

## 技术原理

```
快捷方式 (.lnk)
    ↓
解析目标路径 → C:\Program Files\App\app.exe
    ↓
注册表匹配 → HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall
    ↓
获取 UninstallString → "C:\Program Files\App\uninstall.exe"
    ↓
执行卸载程序
```

---

## 项目结构

```
Unlnk/
├── uninstall_helper.py    # 核心逻辑（构建时生成 exe）
├── build.bat              # 构建脚本
├── install.bat            # 安装右键菜单
├── uninstall.bat          # 移除右键菜单
└── README.md
```

---

## 卸载本工具

双击 `uninstall.bat` 即可移除右键菜单项。

---

## 兼容性

| 系统 | 状态 |
|------|------|
| Windows 11 | ✅ 完全支持 |
| Windows 10 | ✅ 完全支持 |
| Windows 7/8 | ⚠️ 未测试 |

| 软件类型 | 支持情况 |
|---------|---------|
| MSI 安装包 | ✅ 支持 |
| EXE 安装包 | ✅ 支持 |
| 绿色/便携软件 | ✅ 提示手动卸载 |
| UWP 应用 | ❌ 暂不支持 |

---

## 贡献

欢迎提交 Issue 和 PR！

---

## License

MIT License © 2024
