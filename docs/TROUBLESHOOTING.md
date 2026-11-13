# 阻塞与恢复

| 状态 | Agent 行为 | 恢复条件 |
|---|---|---|
| 未登录 | 打开 Tripo 登录/注册入口，记录 login_required | 实际看到已登录 |
| 积分不足 | 告知可核实余额和下一步费用，打开当前页面的官方充值入口 | 用户处理后再次核实余额与预算 |
| 余额未知 | 检查账户页/刷新；不声称为零 | 确认余额或用户提供可核实信息 |
| 点击提交后断网 | 保留 intent/unknown，查询历史任务和余额 | 确认原任务存在与状态，禁止盲目重交 |
| 缺少 Agent 工具 | 说明缺少哪项，记录 capability_missing | 连接并实际验证该工具 |
| 摄像头权限未开 | 引导系统权限设置 | 用户授权并看到实时捕捉 |
| XR 无法启动 | 核对架构、完整资源和官方说明 | 正常启动；不关闭系统防护绕过 |
| 上游版本/界面改变 | 停在当前步骤并保存项目，阅读当前官方说明 | 核实兼容后继续，不自动重做整个角色 |

```sh
python3 scripts/workflow.py open tripo
python3 scripts/workflow.py block projects/my-avatar login_required --note '等待用户在官方页面登录'
python3 scripts/workflow.py status projects/my-avatar
# 重新核实实际状态后：
python3 scripts/workflow.py block projects/my-avatar clear
```

`open` 只打开地址；不会检测登录状态、余额或付款结果。相关判断由具备浏览器控制能力的 Agent 从实际页面取得。

状态文件采用原子替换保存，但不支持多个进程并发修改同一项目。不要让多个 Agent 同时操作同一 Tripo 任务或项目账本。
