# Avatar Agent Workflow

将角色插画制作成可动的 VRM 角色。由 AI Agent 协助准备软件、生成模型、绑定骨骼与表情，并在 XR Animator 中完成摄像头动作测试。

## 安装一次，直接使用

首次把链接发给 Agent：

> 帮我安装这个角色制作 Skill：https://github.com/LerSent001/avatar-agent-workflow

安装后，发送角色图片并说：

> 帮我制作这个角色。

无需重复发送链接。安装时只添加 Skill 入口，Blender 等软件会在首次制作时检查，缺少时由 Agent 询问是否安装。

支持 Skill 的 Agent 可根据请求自动选择“角色制作”；也可以在技能列表中手动选择。Codex 中可使用 `$avatar-character` 明确调用。具体安装步骤见 [Skill 安装指南](docs/SKILL_INSTALL.md)。

也可以不安装 Skill，直接把本仓库链接和图片交给 Agent，按[执行入口](AGENTS.md)开始制作。

## 需要准备

- **角色图片**：PNG、JPEG 或 WebP，建议使用头部、四肢和脚完整可见的全身图。已有三视图也可以直接提供。
- **具备电脑操作能力的 AI Agent**：能够操作本地文件、运行程序及控制浏览器；补充视图时需要 Image 图像生成能力。
- **Tripo 账号与积分**：用于模型、贴图等生成任务，费用按服务实际使用情况计算。
- **摄像头**：用于最后的面部、身体和手部动作测试。

本流程主要适用于有四肢的人形及动物角色。复杂服饰、特殊比例和面部结构可能需要额外调整。

## 完整使用流程

### 1. 准备软件

Agent 检查电脑环境，协助配置 Charakuru、Blender、VRM 插件、XR Animator 及所需运行环境。软件从官方渠道获取，兼容的已有安装可以复用。

### 2. 确认参考图

Agent 检查角色外观、比例和现有视角。如果只有正面图，会询问是否使用 Image 补充正面、侧面和背面的三视图。生成结果由你确认后用于建模；也可以自行提供参考视图。

### 3. 登录 Tripo

Agent 打开 Tripo 并检查登录状态和积分。你在官方页面完成注册或登录；积分不足时会收到提示。确认制作费用和预算后开始生成。

### 4. 制作模型

通过 Charakuru 的制作流程选择模型候选、调整头身比例、完成部件组装和贴图。Agent 会展示需要确认的外观，由你选择后继续。

### 5. 绑定与检查

配置身体和四肢的骨骼、权重，并根据角色设计制作眨眼、张嘴等表情，以及头发、耳朵、尾巴等部位的摆动效果。检查动作变形、材质和 VRM 导出结果。

### 6. 摄像头测试

在 XR Animator 中载入模型，授权摄像头后，按引导完成转头、眨眼、张嘴、抬手和挥手等动作。发现问题后调整并复测。暂时无法使用摄像头时，可保存进度，之后继续。

### 7. 获取成果

确认模型名称、作者和使用条件后，获得：

| 文件 | 用途 |
|---|---|
| VRM 模型 | 在支持 VRM 的应用中使用 |
| Blender 源文件 | 继续编辑角色 |
| 参考图与检查资料 | 查看角色设计及动作检查结果 |
| 使用说明与文件清单 | 查找文件、加载模型并核对交付内容 |

Agent 会提供交付文件的位置和 XR Animator 加载方法。保留原项目文件夹，后续可以继续修改。

## 中断后继续

将原项目文件夹交给 Agent，并告诉它继续制作。Agent 会读取已保存的进度和任务状态，从未完成的步骤继续。登录、积分或系统权限问题处理好后，也可以直接继续当前项目。

## 详细指南

[软件准备](docs/INSTALL.md) · [参考图与制作](docs/WORKFLOW.md) · [模型检查与交付](docs/ACCEPTANCE.md) · [常见问题](docs/TROUBLESHOOTING.md)

## 工具与许可

本流程使用 [Charakuru](https://github.com/nanocle/Charakuru)、[Tripo](https://studio.tripo3d.ai/)、[Blender](https://www.blender.org/)、[VRM Add-on](https://github.com/saturday06/VRM-Addon-for-Blender) 和 [XR Animator](https://github.com/ButzYung/SystemAnimatorOnline)。

本项目原创代码和文档采用 [MIT License](LICENSE)。Charakuru 从官方单独下载，采用其自己的许可，并非 MIT。第三方软件、图像生成和模型生成服务遵循各自的使用条件及费用规则，详见[第三方说明](THIRD_PARTY_NOTICES.md)。
