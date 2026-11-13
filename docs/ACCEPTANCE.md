# 模型检查与交付

检查覆盖模型结构、动作变形、导出文件和实时跟踪。每项记录结果及对应模型版本。

## 检查项目

| 记录项 | 完成标准 |
|---|---|
| `reference` | 用户确认角色外观和比例 |
| `environment` | 所需软件可用，VRM 插件和 Blender 自动化连接正常，XR Animator 可启动 |
| `geometry` | 正面、侧面、背面的形体、部件连接及材质正确 |
| `rig` | 人形映射正确，权重完整且归一，关节动作和服装变形正常 |
| `expressions` | 设计所需的眨眼、张嘴等表情在导出模型中正常工作 |
| `springs` | 摆动部位根部稳定，动态响应与碰撞符合预期 |
| `export_reimport` | VRM 在独立场景重导入后，贴图、材质、骨骼、表情及物理正确 |
| `xr_loaded` | 最终 VRM 在 XR Animator 中正确加载 |
| `live_capture` | 摄像头驱动下的面部、身体和手部测试完成 |

固定表情设计或没有摆动部位的角色，可将对应项记为 `not_applicable`，并附原因。其他项目按实际结果记录 `pass`、`fail` 或 `pending`。

## XR Animator 测试

1. 载入最终 VRM，记录应用版本、模型路径和文件哈希。
2. 调整镜头，让角色完整可见，便于观察关节和配饰。
3. 请用户授权摄像头，开启脸部、身体和手部跟踪，选择适合测试场景的捕捉模式。
4. 引导用户完成转头、点头、眨眼、张嘴、抬手、弯肘、翻腕和挥手。有手指的角色增加张手、握拳；需要腿部跟踪时增加全身动作。
5. 观察模型跟随、衣服变形及耳朵、头发、尾巴等部位的响应，记录各项结果和截图。
6. 修复发现的问题，重新导出并重复相关测试。

记录中注明观察方式：Agent 直接观察或用户反馈。暂时无法使用摄像头时，保存进度并将真人测试保留为 `pending`。

## 保存结果

先登记本次检查使用的模型与源文件：

```sh
python3 scripts/workflow.py model projects/my-avatar --vrm /path/to/avatar.vrm --source /path/to/avatar.blend
```

模型文件更新后重新登记，相关检查会转为待测状态。

```sh
python3 scripts/workflow.py check projects/my-avatar rig pass --evidence projects/my-avatar/reports/rig.json
python3 scripts/workflow.py check projects/my-avatar live_capture pending --evidence projects/my-avatar/reports/live-capture.md
python3 scripts/workflow.py ready projects/my-avatar
```

`check` 保存报告位置及哈希。`ready` 检查记录是否完整、证据文件是否变化，以及是否存在未完成任务或阻塞。模型外观和动作质量由上述测试评估；报告更新后重新记录。

## 交付目录

```text
avatar-delivery/
  avatar.vrm
  avatar.blend
  reference.png
  previews/
  reports/
  manifest.json
  README.md
```

`manifest.json` 保存交付文件的相对路径和 SHA-256。README 说明加载方法、已完成的检查、已知限制及待测项。保留源文件需要的贴图资源，模型作者和使用条件由用户确认。


检查通过后生成交付目录：

```sh
python3 scripts/workflow.py deliver projects/my-avatar --output /path/to/avatar-delivery --name '角色名称' --author '用户确认的作者' --usage '用户确认的使用条件'
```

工具复制模型、源文件、参考图和已登记的检查报告，核对文件哈希，并生成使用说明和清单。预览图可作为检查证据登记并随报告交付。交付目录已存在时使用新目录，以保留已有版本。

交付前从新目录重新打开模型及源文件，核对贴图资源，并向用户提供文件入口。继续修改时使用原项目目录及 `status` 恢复进度。
