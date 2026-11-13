# 常见问题

| 状态 | 处理方式 | 继续条件 |
|---|---|---|
| 未登录 | 打开 Tripo 登录或注册入口 | 用户完成登录 |
| 积分不足 | 显示余额与阶段费用，打开官方充值入口 | 余额满足下一阶段费用，且在用户预算内 |
| 余额未知 | 刷新账户页面，必要时请用户协助确认 | 取得可核实的余额信息 |
| 提交后连接中断 | 保存当前状态，查询原任务 | 取得任务状态和结果 |
| 缺少 Agent 工具 | 提供对应能力的配置方法 | 工具连接并通过功能检查 |
| 摄像头权限未开启 | 引导用户完成系统授权 | 摄像头画面与实时捕捉正常 |
| XR 无法启动 | 检查系统架构、资源完整性及官方安装说明 | 应用正常启动 |
| 上游版本变化 | 保存项目，检查新版说明及兼容性 | 从兼容的已保存阶段继续 |

## 状态记录

```sh
python3 scripts/workflow.py open tripo
python3 scripts/workflow.py block projects/my-avatar login_required --note '等待登录'
python3 scripts/workflow.py status projects/my-avatar
python3 scripts/workflow.py block projects/my-avatar clear
```

处理完成并确认状态后，执行 `clear` 继续流程。`open` 用于打开服务页面，登录和余额信息由 Agent 通过页面读取。

项目状态采用原子替换保存。同一项目使用单一写入进程顺序更新。
