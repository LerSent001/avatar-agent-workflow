# Avatar Agent Workflow

从一张角色插画开始，在 AI Agent 的协助下制作带骨骼、表情和摆动效果的 VRM 角色，并使用摄像头测试动作跟踪。

项目串联 Charakuru、Tripo、Blender 和 XR Animator，提供环境准备、制作引导、进度保存与模型检查流程。

## 开始使用

将本仓库链接和一张角色全身图发给你的 AI Agent：

> 请按照 https://github.com/LerSent001/avatar-agent-workflow 的使用说明，帮我把这张图制作成可动角色。

Agent 会检查电脑环境，协助下载和配置所需软件，然后引导你完成制作。已有的兼容软件可以直接复用。需要登录、补充积分或确认角色外观时，它会提示你；处理完成后可以继续之前的进度。

执行入口：[AGENTS.md](AGENTS.md)。

## 准备什么

- **角色图片**：PNG、JPEG 或 WebP 格式，建议提供头部、四肢和脚完整可见的全身图。
- **AI Agent**：需要能够读写本地文件、运行程序并操作浏览器或桌面；需要补充参考图时，还需具备图像生成能力。
- **Tripo 账号与积分**：用于生成模型和贴图，费用按 Tripo 实际使用情况计算。
- **摄像头**：用于在 XR Animator 中测试面部、身体和手部跟踪。

## 制作流程

1. **准备环境** — 检查并配置所需软件。
2. **确认造型** — 整理参考图，选择模型候选，调整头身比例与贴图。
3. **绑定角色** — 处理骨骼、权重，以及适合角色设计的表情和摆动部位。
4. **检查模型** — 检查动作变形、材质和导出文件。
5. **摄像头测试** — 在 XR Animator 中测试转头、眨眼、张嘴、抬手等动作。
6. **导出成果** — 整理模型、可编辑源文件、预览和检查报告。

制作过程保存任务记录，便于中断后继续。复杂服装、特殊比例和面部结构可能需要额外修复；造型选择与最终效果由你确认。

## 使用的软件

| 工具 | 用途 |
|---|---|
| [Charakuru](https://github.com/nanocle/Charakuru) | 角色制作流程与分部处理 |
| [Tripo](https://studio.tripo3d.ai/) | 模型与贴图生成 |
| [Blender](https://www.blender.org/) + [VRM Add-on](https://github.com/saturday06/VRM-Addon-for-Blender) | 模型编辑、骨骼绑定与 VRM 导出 |
| [XR Animator](https://github.com/ButzYung/SystemAnimatorOnline) | 必需的摄像头动作测试工具 |

软件从官方渠道获取。Node.js、Python 等运行环境由 Agent 一并检查，具体配置见[安装指南](docs/INSTALL.md)。

## 输出文件

- **VRM 模型**：用于支持 VRM 的应用。
- **Blender 源文件**：方便继续修改角色。
- **预览与检查报告**：记录已完成的检查和需要继续调整的部分。

## 项目状态

当前为早期版本，主要面向有四肢的人形及可爱动物角色。下载与进度管理工具已完成基础测试，完整制作流程仍需更多实际验证。各平台的验证范围见[开发文档](docs/DEVELOPMENT.md)。

## 文档

[安装指南](docs/INSTALL.md) · [制作流程](docs/WORKFLOW.md) · [模型与动作检查](docs/ACCEPTANCE.md) · [常见问题](docs/TROUBLESHOOTING.md) · [参与贡献](CONTRIBUTING.md)

## 许可证与致谢

本项目原创代码和文档使用 [MIT License](LICENSE)。

感谢 Charakuru、Blender、VRM Add-on 和 XR Animator 提供的工具。Charakuru 从官方发布页单独下载，采用其自己的许可，并非 MIT。第三方软件与服务遵循各自条款，详见[第三方说明](THIRD_PARTY_NOTICES.md)。
