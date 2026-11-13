# Avatar Agent Workflow · 图片到皮套人

把这个仓库链接和一张角色图片发给具备电脑操作能力的 AI Agent，让它准备软件、协助制作模型、绑定骨骼与表情，并在 **XR Animator** 中完成摄像头测试。

这是一个 **Agent 驱动的工作流项目**，包含入口说明、官方依赖下载工具、项目记录和验收规范。它不是独立的 AI 建模引擎，也不要求用户安装某一种 Skill。

## 直接开始

给你的 Agent 发这句话，并附上角色全身图：

> 请阅读 https://github.com/LerSent001/avatar-agent-workflow 的 README.md 和 AGENTS.md，按流程用附图制作可动角色。自动准备缺少的软件，Charakuru 从官方下载，XR Animator 必须安装并测试。需要登录、充值或系统授权时告诉我，保留进度后继续。不要安装直播伴侣。

**Agent：请继续读取 [AGENTS.md](AGENTS.md)，执行环境检查，而不只是解释项目。** 在本机建立独立工作目录；读取完整说明后再执行脚本。默认仅制作这一张图的一个角色，不自动批量生成。

## 会完成什么

图片检查 → 环境准备 → Tripo 登录/积分检查 → Charakuru 分部制作 → 形体与贴图确认 → 骨骼和权重 → 适用的表情与摆动物理 → VRM 导出复检 → XR Animator 真人测试 → 打包交付。

- Charakuru 从其[官方 Releases](https://github.com/nanocle/Charakuru/releases)下载，不在本仓库中重新分发。
- XR Animator 是**必装、必检项**，不能以 Blender 渲染或待机动画替代真人动捕验收。
- 未登录时打开 Tripo，请用户登录或注册；积分不足时提示并引导用户处理；余额读不到时明确说明未知。
- 保存任务地址和进度，网络异常先查原任务，避免重复扣分。
- 不安装直播伴侣，不安装 OBS，不开播。

## 用户需要准备

一张有权使用的 PNG/JPEG/WebP 角色全身图、能使用的摄像头，以及支持文件读写、运行程序、浏览器/桌面控制的 Agent。需要补图时还需要图像生成能力。纯聊天机器人无法在你的电脑安装软件。Tripo 账户、生成费用和 Agent 使用费用由用户自行承担；本仓库不收集密码、Cookie 或 API Key。

初版主要面向有四肢的人形及可爱动物角色。复杂衣饰、非常规结构和面部拓扑可能需要修复与人工判断。造型选择、付费预算、登录/验证码、充值和摄像头授权需要用户参与。

## 软件

| 软件 | 用途 | 必需 |
|---|---|---|
| Charakuru | 上游角色制作工作流 | 是，从官方获取 |
| Blender + VRM Add-on | 编辑、绑定、检查与 VRM 导出 | 是 |
| Node.js | 运行 Charakuru | 是，最低要求以锁定版本文档为准 |
| XR Animator | 最终模型加载与真人动捕 | **是** |
| 浏览器 | Tripo、本地制作界面 | 是 |
| Blender MCP 或 Agent 可用的 Blender 自动化通道 | 控制 Blender | 需要一个可工作的通道 |

本仓库下载工具使用 Python 3.9+ 标准库。不存在 Python 时由 Agent 从官方准备；Windows 可使用 `py -3`，macOS/Linux 使用 `python3`。详见[安装指南](docs/INSTALL.md)。

## 本地工具

```sh
python3 scripts/workflow.py doctor
python3 scripts/workflow.py install charakuru
python3 scripts/workflow.py install xr-animator
python3 scripts/workflow.py init projects/my-avatar --image /path/to/character.png
python3 scripts/workflow.py status projects/my-avatar
```

`install` 从官方发布资产下载并解压到 `.local/tools/`，**不是完成所有软件配置**。Agent 继续按安装指南检查启动程序、插件与摄像头。已有兼容软件可复用，不能仅因它不在 PATH 中就重复安装。

锁定的发布版本和 SHA-256 位于 [dependencies.json](dependencies.json)。下载支持 macOS ARM64/x64、Windows x64、Linux x64 的对应 XR 官方包；包可下载不代表各平台完整流程已验收。不要在制作中途自动升级上游版本。

## 交付与验收

交付 `avatar.vrm`、可编辑 `.blend`、参考图、模型授权信息、动作/表情预览及分层检查报告。报告明确区分结构检查、静态/动画观察、XR 加载和真人测试。未完成真人测试可交付“待真人验收”版本，但不可称为完整验收通过。

参见[制作流程](docs/WORKFLOW.md)、[XR 验收](docs/ACCEPTANCE.md)、[故障与恢复](docs/TROUBLESHOOTING.md)、[开发与测试](docs/DEVELOPMENT.md)。

## 开源范围

本仓库原创内容使用 MIT 协议。**Charakuru 不采用 MIT**，下载后须遵守它的使用条件；本仓库的 MIT 不授予第三方软件或素材的使用/分发权。这里只保存官方来源与独立编写的编排工具，不包含 Charakuru 代码、Skills、供体模型、用户角色或软件安装包。详见[第三方说明](THIRD_PARTY_NOTICES.md)。

本项目是独立工作流，不代表上游作者认可或提供支持。
