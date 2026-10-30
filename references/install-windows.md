# Windows 安装（预览版）

> **权限与安全提示：本 Skill 包含会让 Agent/Harness 向用户索要系统无障碍（辅助功能）及自动化权限的桌面操作流程，目前用于 macOS 原生保存。此提示在两个平台版本中均显著保留：若对 Agent/Harness 获取系统控制权限有任何安全顾虑，请勿使用本 Skill。Windows 当前通过扩展操作网页，系统保存窗口由用户处理；请审慎判断 Harness 请求的额外权限。**

纯 PubMed 检索、元数据、题录和 PMC 官方公开文件只需要 Python 与网络，不需要 Chrome、Node.js 或扩展。先运行 `python3 scripts/academic.py --json doctor --capability pubmed-data`（Windows 用 `py -3`）。仅当转入出版社会话时，才需要以下浏览器配置。可选正文核验运行 `python3 -m pip install -r requirements-pdf.txt`；未安装仍可归档，但必须报告“正文未自动核验”。见 [PubMed 流程](pubmed.md)。

面向 Windows 10/11 上能执行本地命令的 Coding Agents。已有 Windows 测试者回报部分流程跑通及下载问题，本版据此修复，真实扩展与网站仍待复测，各 Agent 需分别验收；不要把安装成功等同于功能验收通过。

1. 下载 Release 中的 `academic-automation-v<版本号>-windows.zip`，解压得到 `academic-automation`。当前源码与新构建包使用此名称，历史发布包以包内 `SKILL.md` 的名称为准。将完整目录放进所用 Agent 的 Skill 目录，或让 Agent 读取其 `SKILL.md`。
2. 安装 Python（代码最低 3.9，新安装建议 3.11+）、Node.js 22+ 和 Google Chrome。Chrome 使用自己的日常账户及机构权限。
3. 在 Chrome 安装[微软 Playwright 官方扩展](https://chromewebstore.google.com/detail/playwright-extension/mmlmfjhmonkocbjadbfplnigmagldckm)。需要能访问 Chrome Web Store；机构禁止扩展时不能宣称该后端可用。
4. 在解压目录打开 PowerShell，安装锁定的依赖（不需要 Git Bash、WSL 或全局 npm 安装）：

```powershell
npm.cmd ci --ignore-scripts
.\academic.cmd --json doctor
```

5. 按[连接前的 Token](cli.md#连接前的-token)先取得 Playwright 官方扩展 Token，提供给运行 Agent 的进程环境；缺少时 Agent 须等待，不先发起连接。用户已提供或已有可用会话时不重复索要。

```powershell
.\academic.cmd browser connect
.\academic.cmd --json doctor --browser
```

Token 用于自动建立扩展连接，随后确认要操作的普通标签；若仍显示授权界面，由用户处理。执行命令的 Agent、Chrome 和文件必须在同一台电脑。扩展或浏览器没有连接时，CLI 会提示处理，不会改用新的登录配置。

若 Chrome 下载位置不是用户 Downloads，请在命令最前面加入 `--downloads-dir "D:\文献下载"`。具体检索和下载命令见[统一命令行](cli.md)，验收步骤见[平台验收](acceptance.md)。

**出现 PDF 查看器后，Playwright 自动保存尚未被证明稳定可用。** 自动获取和目录恢复均无文件时，Agent 必须先询问“仅整理题录”或“保留各篇标签页，由用户批量手动点击下载”，收到实际选择后再调整交付。保留页不得被下一篇覆盖；手动文件仍需核验归档。步骤见[自动保存受阻后的选择](cli.md#自动保存受阻后的选择)。

操作结束运行 `.\academic.cmd browser disconnect`。升级时保留文献目录及其进度文件，替换 Skill 代码后重新执行 `npm.cmd ci --ignore-scripts`。不要将 `node_modules`、Chrome 配置、连接令牌或文献文件上传到仓库。

复杂 PubMed 查询在 Windows PowerShell 5.1 下使用 UTF-8 `--query-file`，见 [查询文件示例](pubmed.md#检索式与-windows-引号)。纯 PMC 任务需显式加 `--route pmc-only`，才能保证不进入浏览器；只按 PMCID 筛选不足以保证这一点。

安装需要访问发布源，并能写入选定 Skill 目录；文献下载需要访问数据源并能写入文献目录。按 Harness 支持的方式授予这些具体权限，不要求统一启用 `danger-full-access` 或关闭审批。安装目录在工作区外时需另行允许该目录写入。
