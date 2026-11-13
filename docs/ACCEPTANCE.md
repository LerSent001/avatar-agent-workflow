# 验收与交付

必须区分“结构正确”“动画观察通过”“XR 载入成功”“真人动捕通过”。同一段待机动画不能同时证明四项。

## 结构、外观与导出

- reference：用户确认角色外观、全身构成和头身比例。
- environment：必需软件均可用，XR 已启动验证，Blender 与插件可执行。
- geometry：检查正/侧/背面，无明显重复脸、断颈、漂浮附件或缺肢；保存预览。
- rig：人形映射正确；权重完整且归一；左右、肩肘腕、髋膝踝动作方向合理。至少检查手臂下垂/前伸/抬高、弯肘、翻腕、弯膝和转头。记录具体动作及发现，不保证未测极端姿态。
- expressions：有表情的角色检查眨眼、中间状态、闭眼、张嘴和支持的口型；确认导出文件里存在真实绑定。固定表情设计可以不适用，须用户知道并有说明。
- springs：有摆动部位则检查根部稳定、动态响应和碰撞范围。无摆动部位可不适用；单纯存在骨骼不等于物理有效。
- export_reimport：导出 VRM 后在独立场景重导入，检查贴图嵌入、材质、骨骼、表情及物理。报告写入最终 VRM 的 SHA-256。

## XR Animator 必须检查

使用当前最终 VRM，不使用中间件。记录版本、模型路径/哈希、启动时间和截图。

1. `xr_loaded`：实际载入模型，显示正确贴图与形体。人物约占画面高度 80%，头顶含耳朵/呆毛与脚完整可见。开启捕捉后重新核对构图。
2. `live_capture`：用户授权摄像头后开启脸、身体、手的跟踪。默认桌前可用完整站姿加上半身捕捉；腿部跟踪只有实际启用并测试才能声称通过。
3. 引导用户依次：左右转头、点头、眨眼、张嘴、双手抬起放下、弯肘、翻腕/挥手；有手指时张手握拳。同步观察耳朵/头发/尾巴响应。
4. 将每项写为通过/失败/未测/设计不适用，并注明截图或用户观察记录。无法直接观察时明确是用户报告，不能伪称 Agent 已观察。
5. 发现左右错位、嘴型不动、衣服牵拉、明显穿模或物理异常，返回源文件修复并重测。

用户没有摄像头、未授权、暂不在场或拒绝测试时，真人验收保持 pending。可交付待测版本，不得让 `ready` 通过。不要为了测试安装直播伴侣或开启直播。背景使用用户提供/选择的背景，不捆绑原项目的私人背景素材。

## 记录命令

```sh
python3 scripts/workflow.py check projects/my-avatar rig pass --evidence projects/my-avatar/reports/rig.json
python3 scripts/workflow.py check projects/my-avatar live_capture pending --evidence projects/my-avatar/reports/live-capture.md
python3 scripts/workflow.py ready projects/my-avatar
```

证据必须先存在并由 Agent 实际核实。`ready` 只检查记录、哈希、未完成任务及阻塞，不能识别造假的报告，也不能自动判断审美或动作质量。任何报告修改后需重新记录。

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

manifest 包含每个交付文件的相对路径与 SHA-256，模型作者/使用条件由用户确认；README 说明如何在 XR 加载、已知限制与待测项。保留贴图及源文件需要的资源。交付包不能夹带 Charakuru 应用/Skills/供体、账号数据或其他人的角色。项目内部任务记录留在用户电脑，不自动公开。
