# 环境准备

目标是让 Agent 完成准备工作，用户只处理账号和系统弹出的必要授权。优先复用已安装的兼容软件，记录实际版本、路径和启动结果；检查不到不等于不存在。

## 官方来源

| 依赖 | 来源 | 安装后的验证 |
|---|---|---|
| Python 3.9+ | https://www.python.org/downloads/ | 执行版本命令；用于本仓库工具 |
| Charakuru | https://github.com/nanocle/Charakuru/releases | 专用发布 ZIP 内有 AGENTS.md、package.json、server.mjs |
| Node.js | https://nodejs.org/en/download | `node --version`，满足 Charakuru 要求 |
| Blender | https://www.blender.org/download/ ，历史包 https://download.blender.org/release/ | 打开并执行脚本，版本满足当前 Charakuru 和插件 |
| VRM Add-on | https://github.com/saturday06/VRM-Addon-for-Blender/releases | 在目标 Blender 中启用，可导入/导出 VRM |
| XR Animator | https://github.com/ButzYung/SystemAnimatorOnline/releases | 打开桌面程序、载入最终模型、接摄像头 |
| Blender MCP（上游流程需要时） | 根据宿主已安装连接器的官方说明 | 实际执行简单场景查询，不只看到配置文件 |

没有浏览器时从浏览器厂商官方渠道安装支持的桌面 Chromium 浏览器。不要安装直播伴侣、OBS 或无关软件。

## Charakuru 和 XR 的下载工具

```sh
python3 scripts/workflow.py install charakuru
python3 scripts/workflow.py install xr-animator
```

Windows 可把 `python3` 换为 `py -3`。默认写入仓库 `.local/`，可用 `AVATAR_WORKFLOW_HOME` 指定独立位置。发布的依赖清单锁定官方资产与版本；如果提供了官方 SHA-256，下载工具会验证；如果未提供，会记录本地哈希并明确它不是发行方校验。

解压到独立版本目录，不覆盖用户已有软件。断网时残留的 `.partial` 会清除，下次重新下载；已下载的完整包会验证后复用。没有实现 HTTP 断点续传。

### Charakuru

在解压目录找到实际包含 `package.json` 的套件根目录。阅读其中 README、AGENTS、LICENSE 和依赖要求；不要下载 GitHub 自动生成的 Source code ZIP 冒充可运行套件。

使用兼容 Node 在该目录执行官方 `npm start`，仅绑定本机服务，并打开实际日志里的本地地址。不要假定端口一定是 8766。验证页面加载、项目创建和 Blender 自动化连接后记录环境证据。

锁定版本初始为 1.1.1，升级须重新核对文档和完整流程。原有角色项目不要在未备份时迁移。

### XR Animator（必须完成）

下载工具选择 macOS ARM64/x64、Windows x64、Linux x64 的对应官方包。没有对应包时停止并报告，不能假装安装成功或悄悄换架构。

阅读解压后的 `readme.txt`，以该版本说明为准：

- macOS：官方包可能分为 Electron 运行时 ZIP 和 XR 资源 ZIP。外层解压完成不代表应用安装完成。若存在内层包，使用系统 `ditto` 或图形解压工具解开对应架构的 Electron，再按官方 readme 合并 XR 资源至 Electron.app 的 Contents/Resources 等位置。保留框架符号链接及可执行权限，放入用户 Applications 中的独立目录。不得用字符串同名规则猜测覆盖路径。若已经提供完整 app 则直接验证，不重复套用旧教程。
- Windows：按官方 readme 解压运行包，打开对应 Electron/XR 可执行文件；不要只复制 exe 而丢失旁边的资源。
- Linux：某些官方包包含符号链接，本仓库通用解压器会拒绝这种包；使用官方推荐的系统解压器保留链接，检查指向包内。运行前核对执行权限及官方列出的系统依赖。

首次打开被系统拦截时，引导用户从系统设置正常授权。不得全局关闭安全防护或盲目删除隔离属性。

实际打开 XR 后记录启动路径，给用户提供易找到的入口（例如 Finder 中的位置或桌面快捷方式，避免只藏在工具目录）。先验证应用启动，最终模型完成后按 ACCEPTANCE.md 验收。

### Blender 和 VRM 插件

这两项由 Agent 从官方页面读取匹配版本并下载、安装；本仓库未硬编码跨平台安装命令。Windows/macOS/Linux 安装方式不同，不能用一条系统命令冒充全平台支持。

在**实际用于制作的 Blender 版本**内安装和启用 VRM 插件，确认导入导出操作存在。Agent 可用无界面脚本处理批量步骤，使用图形界面检查最终外观。若上游要求 Blender MCP，连接并执行一次真实查询。保存安装清单后才将 environment 标记为 pass。

## 环境证据至少包括

系统/架构、依赖的版本与实际路径、官方下载地址、包校验情况、启动结果、VRM 插件启用情况、可用 Agent 能力、XR 启动结果。不要记录账号令牌、Cookie 或密码。
