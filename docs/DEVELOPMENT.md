# 开发指南

## 本地测试

```sh
python3 -m unittest discover -s tests -v
python3 scripts/workflow.py doctor
```

[CI 模板](ci-template.yml) 支持在 Windows、macOS 和 Linux 运行基础工具测试。自动测试尚未启用；维护者可将模板移至 `.github/workflows/tests.yml` 配置 GitHub Actions。

## 验证范围

| 功能 | 状态 |
|---|---|
| 项目状态、任务记录、验收门槛、平台选择、归档路径检查 | macOS ARM64 / Python 3.9 下离线测试通过 |
| Charakuru 1.1.1 官方下载、SHA-256 校验及解压 | 已验证 |
| XR Animator 全新环境安装与真人捕捉 | 待验证 |
| Windows/Linux 完整安装与制作流程 | 待验证 |
| 付费生成到最终真人测试的完整流程 | 待验证 |

## 依赖维护

从官方 Release 核对版本、资产名、下载地址和校验值，更新 dependencies.json。升级后分别验证下载解压、软件启动、制作步骤、VRM 导出和 XR 动作测试。

发布内容包含原创代码、文档和依赖清单。第三方软件包和用户项目保存在本地忽略目录中。

## 工具职责

- 下载工具获取和解压依赖；Agent 按平台指南完成配置与启动检查。
- 任务记录保存生成进度及费用信息；Agent 操作 Tripo 页面并读取实际状态。
- `ready` 检查记录和证据文件的完整性；模型质量通过制作与验收流程评估。
- 状态文件支持原子写入，同一项目按顺序更新。

新增功能应包含对应测试，并注明实际验证的平台。
