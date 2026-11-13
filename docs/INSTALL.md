# 环境准备

检查系统和已有应用，复用兼容版本，从官方渠道安装缺少的依赖。

首次使用先确认 Python 运行环境，再执行 `python3 scripts/workflow.py doctor`，按返回的检查结果完成准备。选择可写目录并检查可用空间；安装包大小以所选发布资产为准，预留解压和角色项目所需空间。

## 依赖

| 软件 | 官方来源 | 配置检查 |
|---|---|---|
| Python 3.9+ | https://www.python.org/downloads/ | 可运行本仓库脚本 |
| Node.js | https://nodejs.org/en/download | 满足 Charakuru 的版本要求 |
| Charakuru | https://github.com/nanocle/Charakuru/releases | 本地界面和项目功能正常 |
| Blender | https://www.blender.org/download/ | 可启动并执行制作脚本 |
| VRM Add-on | https://github.com/saturday06/VRM-Addon-for-Blender/releases | 在制作使用的 Blender 中启用，可导入导出 VRM |
| XR Animator | https://github.com/ButzYung/SystemAnimatorOnline/releases | 可启动、载入模型并使用摄像头 |

此外，需要桌面 Chromium 浏览器及可用的 Blender 自动化通道。若 Charakuru 当前版本要求 Blender MCP，按连接器的官方说明配置，连接后执行一次场景查询。

## 下载 Charakuru 和 XR Animator

```sh
python3 scripts/workflow.py install charakuru
python3 scripts/workflow.py install xr-animator
```

Windows 可使用 `py -3` 代替 `python3`。默认安装目录为 `.local/tools/`，可通过 `AVATAR_WORKFLOW_HOME` 指定其他位置。

依赖清单 dependencies.json 保存官方发布版本、资产地址和校验值。工具验证发行方提供的 SHA-256，并保存下载记录。已完成的下载可复用；中断的下载将在重试时重新开始。

## 配置 Charakuru

1. 找到解压目录中包含 package.json 的套件根目录。
2. 阅读随附的 README、AGENTS.md、LICENSE 和版本要求。
3. 使用兼容的 Node.js 执行 `npm start`。
4. 打开启动日志中的本地地址，检查页面、项目创建和 Blender 连接。

使用官方 Releases 中的专用运行套件。升级前备份项目，核对新版本要求并验证兼容性。

## 配置 XR Animator

下载工具提供 macOS ARM64/x64、Windows x64 和 Linux x64 的官方包。其他平台需先确认上游支持情况。解压后按该版本的 readme.txt 完成配置：

- **macOS**：如果发布包分别提供 Electron 运行时与 XR 资源，使用系统解压工具解开对应架构的运行时，按照随附说明合并资源。保留应用的符号链接和执行权限。完整应用可放入用户 Applications 目录。
- **Windows**：解压完整运行目录，保留可执行文件及配套资源，按随附说明启动。
- **Linux**：检查执行权限和系统依赖。包含符号链接的包使用平台解压工具处理，保留包内链接结构。

系统要求首次运行授权时，引导用户完成正常授权。启动成功后提供应用位置或快捷方式，最终模型制作完成后进行摄像头测试。

## 配置 Blender 与 VRM 插件

根据系统平台和 Charakuru 的版本要求，从官方渠道选择兼容的 Blender 与 VRM 插件。在制作使用的 Blender 中安装并启用插件，验证导入、导出和自动化操作。

## 保存环境记录

记录系统架构、软件版本与路径、下载来源、校验结果、插件状态及启动检查结果。上述配置完成后，将项目的 `environment` 检查项记录为 `pass`。
