# 安装角色制作 Skill

把仓库链接发给 Agent，并告诉它“安装这个角色制作 Skill”。安装后，发送角色图片并说“制作角色”即可使用。

## Agent 安装步骤

1. 读取 `skills/avatar-character/SKILL.md`。安装源目录为 `skills/avatar-character`，名称为 `avatar-character`。
2. 使用当前宿主提供的 Skill 安装器，从本仓库获取该目录。目标为当前用户的 Skill 目录，以便在其他项目和聊天中使用。保留 `SKILL.md`、`agents/openai.yaml` 、`scripts/resolve_workflow.py` 和 `LICENSE` 的相对结构。
3. 已安装同名 Skill 时检查现有版本，保留用户改动。安装完成后核对上述文件，并刷新宿主的 Skill 列表。
4. 告诉用户：“安装完成，下次发送角色图片并说‘制作角色’即可。”宿主未刷新时提示重新打开聊天或重启应用。也可通过宿主的技能选择器选择“角色制作”。

安装阶段只放置 Skill 文件。所需建模软件、插件和运行环境在第一次制作时检查，经用户同意后准备。安装入口无需登录 Tripo 或生成素材。

## 安装方式

支持从 GitHub 安装 Skill 的宿主，使用仓库 `LerSent001/avatar-agent-workflow` 和路径 `skills/avatar-character`。

已下载仓库且有 Python 时，可运行：

```sh
python3 scripts/install_skill.py --dest /path/to/your/agent/skills
```

没有 Python 时，使用宿主的文件工具将 `skills/avatar-character` 整个目录复制到其用户 Skill 目录，即可完成入口安装。

Codex 可使用内置 Skill 安装器，或放入用户级 `~/.agents/skills/`。已有自定义 Skill 目录时沿用宿主配置；同一宿主只安装一份。其他 Agent 使用其支持的用户 Skill 目录。

## 第一次制作

Skill 在首次使用时取得固定版本的工作流代码，存放于用户本地缓存。Agent 随后检查环境、询问缺少软件的安装许可，并进入角色制作。后续直接调用即可，正在进行的项目沿用其保存的工作流版本。
