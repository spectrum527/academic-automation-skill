# 2.0.0 RC3：统一技能名称与离线 CI（2026-10-30）

RC3 将 Skill 名、安装目录说明和 Windows/macOS 包的根目录统一为 `academic-automation`。版本号为 `2.0.0-rc.3`，历史发布附件保持原样。Legacy 包继续使用冻结提交中的名称与原始内容。

新增 GitHub Actions 离线检查：在 Python 3.9 与 3.13 上运行回归测试，构建两平台与冻结 Legacy 包，并核对校验和。

| 附件 | 使用范围 |
|---|---|
| `academic-automation-v2.0.0-rc.3-windows.zip` | Windows RC3，官方 Playwright 扩展后端 |
| `academic-automation-v2.0.0-rc.3-macos.zip` | macOS RC3，仅 Apple Events 后端 |
| `academic-automation-legacy-v1.6.0-macos.zip` | macOS Legacy Version 1，保留冻结源码 |
| `SHA256SUMS` | 本次三个 ZIP 的 SHA-256 校验值 |

安装入口：[RC3 Release](https://github.com/spectrum527/academic-automation-skill/releases/tag/v2.0.0-rc.3)。RC3 以 Pre-release 发布，不标记为 Latest。升级时保留任务记录和已下载文献，替换旧的活动 Skill，避免同时加载新旧名称的两份安装。

本次仅调整名称、打包及检查流程，不新增真实网站或账户验收结论。验证范围见 [VERIFICATION.md](VERIFICATION.md)。以下为历史发布记录。

---

# 2.0.0 RC2：新仓库、文档与视觉标识（2026-10-26）

**重要权限与安全提示：macOS 界面自动化与 PDF 原生保存仍需要 Agent/Harness 的系统无障碍权限及 Chrome / System Events 自动化权限。若有任何安全顾虑，请勿使用本 Skill，也不要授予这些权限。Windows 当前仍由用户处理系统保存窗口。**

RC2 在新仓库 `spectrum527/academic-automation-skill` 发布为 Pre-release。它沿用 RC1 的检索、下载与人工交接逻辑，不新增真实平台验收结论。

- 保留本地 Git 历史、旧分支与标签，更新文档中的仓库链接；RC1 的重建发布继续保留。
- 纳入维护者修订的中英文 README 与 MIT 许可证，以及 README 头图和独立 Logo。
- 修复安装包缺少 README 图片的问题，两个平台包都包含对应资源；打包回归核对图片引用与字节内容。
- 本地维护环境删除了两个仅用于 Qoder AI 代码追踪的 Git hooks，避免提交和检出时启动 Qoder CN。这是本机 `.git/hooks` 的清理，不会通过发布包修改用户的 Git 配置。

| 附件 | 使用范围 |
|---|---|
| `academic-automation-v2.0.0-rc.2-windows.zip` | Windows RC2，官方 Playwright 扩展后端 |
| `academic-automation-v2.0.0-rc.2-macos.zip` | macOS RC2，仅 Apple Events 后端 |
| `academic-automation-legacy-v1.6.0-macos.zip` | 从保留的冻结提交重建的 macOS Legacy Version 1 |
| `SHA256SUMS` | 本次三个 ZIP 的 SHA-256 校验值 |

安装入口：[RC2 Release](https://github.com/spectrum527/academic-automation-skill/releases/tag/v2.0.0-rc.2)。候选版不标记为 Latest。两个 RC2 平台包使用当前 RC2 源码；Legacy 运行源码与原始 README 保持冻结版本，额外安装说明指向新仓库。

验证范围见 [VERIFICATION.md](VERIFICATION.md)。Windows 原生扩展与出版社保存，以及不同 Harness 的完整流程仍需分别实测；本次不操作网站、账户或机构会话。

---

以下为 RC1 及此前的历史发布说明，其中 Latest 等描述记录当时状态；当前下载请使用上方 RC3 入口。

> **重要权限与安全提示：本 Skill 会让 Agent/Harness 在执行 macOS 界面自动化和 PDF 原生保存时，向你索要系统无障碍（辅助功能）权限，以及控制 Chrome / System Events 的自动化权限。无障碍权限允许应用控制系统界面，授权范围不限于单个网页。若有任何安全顾虑，请勿使用本 Skill，也不要授予相关权限。**
>
> **Windows 当前通过 Playwright 官方扩展操作网页，系统保存窗口由用户处理。请审慎判断所用 Agent/Harness 请求的任何额外系统控制权限。RC1 两个平台包的中英文 README 均保留普通字号加粗的权限提示，Legacy 下载也附带权限说明。**
>
> **Accessibility and safety: macOS UI automation will ask your Agent/Harness to obtain system Accessibility and automation permissions. These permissions extend beyond a webpage. If you have security concerns, DO NOT USE THIS SKILL or grant these permissions. Windows currently leaves system Save dialogs to the user.**

# 2.0.0 RC1：PubMed 下载修复与跨平台候选版

RC1 以 9 月 14 日的 macOS 与 Windows 测试反馈为依据，将正文识别、下载状态和用户交接结合，修复正常正文被判为补充材料、复杂检索式在 Windows 下被拆分，以及停止批次后重跑仍可能继续下载的问题，为后续测试保留逐篇可核对的结果。

本版版本号为 `2.0.0-rc.1`，发布页设为 **Latest Release**。RC1 仍处于候选阶段，已验证的官方接口与 PMC 下载可以使用，Windows 扩展及不同出版社的完整流程仍需分别验收。跨平台代码进入 `main`；原主分支的 1.6.0 内容保留在 `legacy-version-1`，作为 macOS 可选的 **Legacy Version 1** 下载，此前 Beta 和 1.x 标签继续保留。

## 下载选择

| 附件 | 使用范围 |
|---|---|
| `academic-automation-v2.0.0-rc.1-windows.zip` | Windows RC1，提供 `academic.cmd` 和共享 Python 入口 |
| `academic-automation-v2.0.0-rc.1-macos.zip` | macOS RC1，提供 `academic.command` 和旧入口兼容包装 |
| `academic-automation-legacy-v1.6.0-macos.zip` | macOS Legacy Version 1，保留原主分支运行源码；不包含 PubMed、Windows 后端及 2.0 的下载修复 |
| `SHA256SUMS` | 上述三个 ZIP 的 SHA-256 校验值 |

当时的三个包使用相同的 Skill 目录名，名称见各包的 `SKILL.md`。RC1 与 Legacy 应选择其中一个作为活动安装，不能混合覆盖，也不应让 Agent 同时加载同名 Skill。包内不捆绑 Python、Node.js 或 Chrome，不包含登录信息、Token、个人任务和文献文件。Legacy 的 `LEGACY_SOURCE.json` 记录原提交与逐文件摘要，具体切换说明见 [Legacy Version 1](https://github.com/spectrum527/academic-automation-skill/blob/v2.0.0-rc.1/LEGACY.md)。

## 本版修复

| 测试中出现的问题 | RC1 的处理 |
|---|---|
| J Glob Health 正文首页提示另有补充材料，却被拦截 | 区分完整的期刊声明与真正的补充材料标题；声明不再阻断正文，但真实附录及错篇仍须拦截 |
| 只有 PMCID 的清单仍进入出版社，连接暂停拖住后续篇目 | 新增用户明确选择的 `--route pmc-only`，无公开正文默认暂缓，也可预先选择仅题录；其他篇目的 PMC 任务与浏览器暂停分开处理 |
| 用户说“全部停”，程序只跳过当前篇 | 新增整批取消及明确恢复，决定保存在清单检查点中；重排或普通重跑不会自动恢复，其他任务的待办保持原状 |
| PowerShell 5.1 将嵌套引号拆成多个参数 | 新增 UTF-8 `--query-file`；查询和 JSON 清单均兼容 BOM，原有直接查询参数继续保留 |
| 扩展内部页的旧连接记录容易被误认为可用 | 状态明确区分无效页面与尚未实时检查的历史连接；Token 是否存在、页面是否可读及能否下载分别记录 |
| 内嵌 JavaScript 产生 Python 转义告警 | 使用原始字符串保留 JavaScript 正则含义，消除无效转义警告 |
| 用 PMC 子集进度生成目录，遗漏完整清单中的其余题录 | 合并完整元数据与子集进度，按 PMID 去重，分别统计暂缓、取消及已归档结果 |

RC1 也纳入此前 `beta.4.fix.1` 的修复：PMC 与出版社 PDF 共用分块传输及有界续传；β 字形提取歧义需实际人工确认，并绑定文件 SHA-256。缺少免费证据保留为待确认，JAMA 正文跳转补充识别，检索和元数据任务与浏览器待办隔离。文件完整性核验仍覆盖首次归档、人工归档及缓存复用。

“仅免费”只限定文献访问范围，有 PMCID 也不保证公开数据服务提供 PDF。用户明确不需要浏览器时才采用仅 PMC 模式；未取得 PDF 应记录为暂缓或用户选择的仅题录，不能推断收费。已经暂停的同一篇也不能通过切换模式避开确认。

## 平台与权限

| 流程 | 依赖与操作方式 |
|---|---|
| PubMed 官方接口、题录、显式仅 PMC 下载 | Python 3.9+ 与网络；不需要 Chrome、Node.js、扩展或系统无障碍权限 |
| macOS RC1 浏览器流程 | 使用日常 Chrome，启用 Allow JavaScript from Apple Events；**仅使用 Apple Events，不使用 Playwright**。原生保存通过 System Events 操作已识别窗口，需要上方强调的权限 |
| Windows RC1 浏览器流程 | Python 3.9+、Node.js 22+、锁定的 Playwright CLI 0.1.19，以及[官方 Chrome 扩展](https://chromewebstore.google.com/detail/playwright-extension/mmlmfjhmonkocbjadbfplnigmagldckm)；新连接前须提供 Token |
| Legacy Version 1 | 仅 macOS，按旧版 Skill 及包内 `INSTALL.md` 执行；没有 2.0 的跨平台和 PubMed 功能 |

Windows 的 Token 通过运行 Agent 的进程环境 `PLAYWRIGHT_MCP_EXTENSION_TOKEN` 提供。缺少时先询问并等待，已有可用会话可沿用；Token 不回显、不写入项目，也不能替代网站登录和验证码。

**Playwright 出现 PDF 查看器后，仍不能保证稳定自动下载。** 自动保存和目录恢复均无文件时，Agent 应询问仅整理题录，或保留各篇标签页供用户集中手动下载，等实际选择后再调整交付。验证码及登录暂停仍须等待用户处理，不能自动变成仅题录。macOS 原生保存也只操作已识别的当前篇和标准保存窗口，遇未知窗口或权限不足则暂停。

`pypdf` 为可选依赖，用于检查可解析性、页数与首页题名作者。未安装或文字无法提取时，必须说明“正文未自动核验”，可能遗漏错篇、正文与附录混淆或解析问题；已安装解析器明确发现损坏或身份不符时不得计为成功。已归档、自动核验及人工核验分别统计，页数不能单独证明正文身份。

## 升级与使用

从 Beta 4 升级时，整体替换 Skill 代码，保留文献目录、任务检查点及用户决定。重新加载 Skill 后运行 `doctor` 核对 `2.0.0-rc.1`。Legacy 与 RC1 的检查点格式不同，切换版本前备份，不将 2.0 任务交给旧版续跑。

macOS 在解压后的 Skill 目录执行：

```bash
./academic.command --backend apple-events --json doctor
```

Windows 纯接口任务可先执行 `py -3 scripts/academic.py --json doctor --capability pubmed-data`；需要浏览器时再安装依赖并提供扩展 Token：

```powershell
npm.cmd ci --ignore-scripts
.\academic.cmd --json doctor
.\academic.cmd browser connect
.\academic.cmd --json doctor --browser
```

可选正文核验依赖在 Skill 目录安装：macOS 用 `python3 -m pip install -r requirements-pdf.txt`，Windows 用 `py -3 -m pip install -r requirements-pdf.txt`。安装和下载只需相应网络访问及目标目录写入权限，不统一要求关闭 Harness 审批或使用全面文件访问。

查询文件、仅 PMC 下载，以及整批取消的完整命令见 [PubMed 使用说明](https://github.com/spectrum527/academic-automation-skill/blob/v2.0.0-rc.1/references/pubmed.md)。平台安装见 [macOS](https://github.com/spectrum527/academic-automation-skill/blob/v2.0.0-rc.1/references/install-macos.md) 与 [Windows](https://github.com/spectrum527/academic-automation-skill/blob/v2.0.0-rc.1/references/install-windows.md)。

## 验证与不足

本轮离线回归共 **191 项，190 项通过，1 项隔离 Chrome 测试按配置跳过**。新增 24 项覆盖本轮 Windows 反馈及打包约束，保留此前 167 项。禁用可选第三方 Python 包的回归结果、解压入口及 Legacy 文件核对记录见 [VERIFICATION.md](https://github.com/spectrum527/academic-automation-skill/blob/v2.0.0-rc.1/VERIFICATION.md)。

| 真实样本 | 本轮结果 |
|---|---|
| PMID 42693903，J Glob Health | 从官方 PMC 重新取得 1,835,920 字节、13 页正文；题名与第一作者核验通过，正常声明不再触发补充材料误判 |
| PMID 41947537 | 当前 PMC 服务无可分发正文 PDF，显式仅 PMC 模式返回暂缓，没有进入浏览器连接 |

本轮真实网络复测在 macOS 上完成。Windows 测试者此前报告已完成 PubMed 检索、题录与两篇 PMC 下载，尚不能据此证明 RC1 的 Windows 扩展、出版社保存或各 Harness 已全部通过。Wiley 的线上验证仍待用户处理，JAMA 新规则已有离线覆盖但未重新完成线上保存；这些限制随候选版保留。
