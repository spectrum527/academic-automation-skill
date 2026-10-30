# macOS 安装

> **权限与安全提示：本 Skill 会让 Agent/Harness 为 macOS 界面自动化和 PDF 原生保存向你索要系统无障碍（辅助功能）权限，以及 Chrome / System Events 自动化权限。无障碍权限允许控制系统界面；若有任何安全顾虑，请勿使用本 Skill，也不要授予相关权限。**

纯 PubMed 检索、元数据、题录和 PMC 官方公开文件只需要 Python 与网络，不需要 Chrome、Node.js 或扩展。先运行 `python3 scripts/academic.py --json doctor --capability pubmed-data`（Windows 用 `py -3`）。仅当转入出版社会话时，才需要以下浏览器配置。可选正文核验运行 `python3 -m pip install -r requirements-pdf.txt`；未安装仍可归档，但必须报告“正文未自动核验”。见 [PubMed 流程](pubmed.md)。

> 新版优先使用[统一命令行](cli.md)。下列 `.sh` 示例仅为 macOS 兼容入口；Windows 使用对应的统一命令。站点选择器与匹配规则两平台共用，退出状态以新版 CLI 文档为准。

下载 `academic-automation-v<版本号>-macos.zip` 并解压，将完整 `academic-automation` 文件夹放入 Agent 的技能目录。当前源码与新构建包使用此名称，历史发布包以包内 `SKILL.md` 的名称为准。Python 核心最低 3.9；新安装建议使用 3.11+。

macOS **仅使用 Apple Events，不使用 Playwright，也不将它作为失败后的回退方案；不需要浏览器扩展、Token、Node.js 或 npm 依赖**。启用 Google Chrome → View → Developer → Allow JavaScript from Apple Events。浏览器命令显式传 `--backend apple-events`，避免继承旧扩展配置。使用自己的已登录 Chrome，系统首次请求应用自动化权限时按实际需要授权。

出版社 PDF 只在 Chrome 查看器显示、未落盘时，通过 Apple Events 与 System Events 尝试点击“下载”，在识别到的 macOS 保存窗口中选择任务暂存目录，再核验归档。这一步另需在“系统设置 → 隐私与安全性 → 辅助功能”中授权**实际运行 Agent 的应用**（例如 Codex 或终端）；自动化授权也须允许该应用控制 Chrome 和 System Events。仅用 PubMed 接口、PMC 直接下载或普通页内下载时不要求辅助功能权限。

自动保存期间保持任务 PDF 为 Chrome 当前标签。程序可将 Chrome 激活到前台，但不会切换用户另选的标签；用户切走窗口、出现无法识别的对话框或权限不足时停止。暂存路径由程序生成，同名归档不覆盖。当前适配的是 Chrome 内置查看器和标准保存窗口，其他查看器交给用户处理。已验证本机英文系统界面；中文控件文字有离线覆盖，尚未做真实系统语言切换验收。

```text
python3 scripts/academic.py --backend apple-events --json doctor
python3 scripts/academic.py --backend apple-events browser connect
python3 scripts/academic.py --backend apple-events --json doctor --browser
```

下载包也提供 `./academic.command` 启动入口。旧 `.sh` / `.py` 入口仍可使用，主要流程已转到共享 Python 核心。

权限不足时说明所需权限并等待用户；用户拒绝授权时停止该自动化操作，不能改用 Playwright 或其他工具绕过。连接后操作绑定标签，不跟随用户临时切换的活动标签。目标标签关闭或浏览器重启后重新运行 `--backend apple-events browser connect`。结束用 `--backend apple-events browser disconnect`，不会关闭日常浏览器。

详见[统一命令行](cli.md)及[平台验收](acceptance.md)。
