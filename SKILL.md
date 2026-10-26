---
name: cnki-download
description: 在 PubMed、知网中文/外文库、Web of Science 或 Google Scholar 检索文献、整理带链接题录，按 PMID、DOI 或题名清单下载及归档可获取的全文。检索外文前确认订阅范围，支持人工验证后的续跑。PubMed 接口不依赖浏览器；浏览器流程沿用已登录 Chrome，Windows 使用 Playwright 官方扩展，macOS 仅使用 Apple Events。
metadata:
  version: "2.0.0-rc.2"
---

# 学术文献检索、下载与归档

## 按任务读取

先确定网站、语言与交付阶段，优先使用[统一命令行](references/cli.md)，只读取当前模式对应的参考文档。正常运行直接执行脚本，不预读全部源码、README、排错文档或其它模式。

| 用户任务 | 此时读取 | 执行入口 |
|---|---|---|
| PubMed、生物医学检索、PMID 或 PubMed URL 清单 | [PubMed](references/pubmed.md) | `search pubmed` → `metadata --source pubmed` → `download pubmed` / `batch --source pubmed` |
| 知网中文期刊、博硕、会议；中文题名清单 | [中文库](references/chinese-macos.md) | `search cnki` → `download cnki`；批量 `batch` |
| 知网外文、WWJD；摘要页给 DOI 无 PDF/CAJ | [外文库](references/foreign-macos.md) | `search cnki-foreign` → `metadata` → `bibliography cnki` |
| Web of Science / WoS / Core Collection | [WoS](references/wos-macos.md) | `search wos` → `bibliography wos` |
| 谷歌学术 / Google Scholar | [Scholar](references/scholar-macos.md) | `search scholar` → `bibliography scholar` |
| 已有完整 DOI，需要实际下载外文全文 | [出版社下载](references/publisher-oa.md) | `download doi`；需要时 `archive` |
| 正常流程失败，需查页面/匹配/归档原因 | [排错](references/troubleshooting-macos.md) | 按退出码只查看相关段落 |

“只做目录”不读取出版社下载和浏览器保存细节。检索阶段不提前加载下载排错。脚本参数、特定站点选择器和经验例外放在上述参考文档；已知入口足够时不要反复读取源码。

## 对话流程

主路径：方向 → 必要时确认网站/语言与订阅范围 → 检索 → 必要时确认交付方式 → 执行 → 核验汇报。用户已说明或已授权的内容不重复询问。

**PubMed、知网外文、WoS、Scholar 的共同前置规则**：检索前若用户未说明，先问“是否考虑付费或订阅文献？”；用户拒绝后，再问“这些文献是放弃，还是保留题录？”并等实际回复。已经明确选择“仅免费，其他保留题录”等时直接沿用。同一任务的选择传到检索、下载、清单与检查点，不能作为其他任务的默认答案。考虑订阅只授权尝试现有机构权限，不授权购买。

将回答映射为 `--access-policy all`（完整候选，免费优先，再尝试机构权限）、`free-only`（只免费，其余排除或待分类）、`free-plus-bib`（完整候选，仅下载免费，其余保留题录）。缺少选择时统一入口返回 `needs_user`，尚不检索；用人工交接补回原任务。没有免费标记不等于收费；未知、等待验证、已证实订阅分别记录。没有可靠免费筛选的来源保留 `unclassified_rows`，不能把它们说成收费或从报告里静默删掉。

- 现成题名清单且要求逐篇下全文：中文走中文库，英文走外文/出版社；不再问网站，缺作者或归档路径先补齐。中文下载必须提供第一作者，脚本会在打开浏览器前校验。
- 只有研究方向：网站或语言未明确时一次问清并等回答，再打开检索页。网站可选知网中文/外文、WoS、Scholar 或多个；语言可选中文、英文、中英。已经说“用 WoS”“用谷歌学术”“从知网下中文”等时直接按指定模式执行。
- 多网站/中英任务分开检索，同一浏览器串行进行。不要因为多个来源就并行抢占活动标签。
- 检索后简述大致命中数、本页提取数和主题相关性。若交付方式尚未指定，再问“能下则下”或“只做目录”；已要求下载或只要目录则直接执行。
- “能下则下”：尝试获取选定全文。验证码、登录与保存窗口属于待人工，尚不能判断无法获取；只有已证实无法获取或用户明确跳过，才保留题录并注明原因。“只做目录”：只整理有发布页链接的 Markdown，不启动全文下载。

用户明确要求仅 PMC、不使用浏览器时，下载和批量加 `--route pmc-only`；默认没有正文 PDF 则记 `deferred`，用户已选择保留题录时加 `--on-unavailable bibliography`。`free-only` 只约束文献访问范围，不等于仅 PMC；有 PMCID 也不保证公开数据服务有正文 PDF。不要替用户自动缩小下载来源。

用户说“全部停，只保留题录”时，对本任务的每份 PubMed 清单执行 `batch ... --cancel --note "实际回复"`，持久保存整批取消，不能只 skip 当前篇。重新运行仍保持取消；只有用户明确要求恢复，才使用 `--resume-cancelled --note "实际回复"`。详见 [PubMed 批次控制](references/pubmed.md#仅-pmc-与整批取消)。

## 待人工时的必需动作

收到 `needs_user` / 退出码 2，或看到人机验证、登录、无法自动处理的保存窗口时：保留当前标签，向用户说明具体文献和所需动作，**发出提问并等待用户回复**。CLI 正在执行的受控 macOS 保存步骤由其完成，规则见[出版社下载](references/publisher-oa.md)。不能只写“建议手动验证后重试”就结束整个下载任务，也不能转去下一篇。Harness 没有提问工具时直接发问并暂停本轮；没有回复、等待超时均不算用户选择跳过。

用户回复后按[统一命令行的人工交接](references/cli.md#人工交接与调度约束)恢复原任务；统一入口返回了 `pending.id` 时先记录决定，已落盘文件优先核验。只有用户明确跳过、取消自动下载或选择下述交付方式后，才能结束该篇的自动下载暂停。待人工项目须单列，不能混入“仅题录/无法获取”，或把部分交付汇报为全部完成。自动调度须使用统一入口，不能改用 curl、自写脚本或旧包装器来回避暂停状态。

连接失效时，实际用户回复后先记录 retry，再 `browser connect` 重新绑定当前篇标签，最后重跑原任务；单纯重跑不会修复旧窗口绑定。纯 PubMed 检索/元数据，以及用户预先选择的 `--route pmc-only` 下载，使用独立任务暂停；其他篇目的纯接口任务可在浏览器等待时执行，不会解除旧任务。同一篇已暂停时不能改模式逃离确认。

`kind=identity_review` 表示可能的题名字形提取误报。向用户展示预期题名、提取片段、作者及 DOI，等实际核对确认后，按[人工身份核验](references/cli.md#人工身份核验归档)通过统一入口归档，绑定 pending id 和文件 SHA-256，单独统计“人工核验”。不能用 skip 后自行复制文件来代替，也不能放行明确错篇、附录或损坏文件。`kind=access_unknown` 仍待用户判断免费证据或交付选择，不自动排除。

**Playwright 查看器不能保证稳定自动下载。** 正文已打开但自动保存未落盘、且目录恢复也未找到文件时，向用户询问：“本轮这类文献是仅整理题录，还是保留各篇标签页，最后由你批量手动点击下载？”等待实际选择，同一任务沿用，不替用户默认降级。仅题录须注明“用户选择仅题录”；保留标签页须建立“待手动下载”清单，不关闭或复用这些标签去打开下一篇，用户保存后再核验归档。具体交接与新建标签命令见[自动保存受阻后的选择](references/cli.md#自动保存受阻后的选择)。验证码、登录和 Cookie 选择仍先按原暂停规则处理，不能把它们直接判成无法下载。用户仍要求继续自动保存时，保留当前暂停并说明限制，不反复点击。

## 共用前提与约束

**macOS 只使用 Apple Events 控制 Chrome，原生保存使用 System Events；不要使用 Playwright，也不要在遇到验证、下载或权限问题时切换为扩展后端。** macOS 浏览器命令显式传 `--backend apple-events`，避免继承旧环境变量或其他平台包的配置；不索要 Playwright Token，不安装扩展或 npm 依赖。Windows 才使用 Playwright 官方扩展。历史扩展实验记录不是 macOS 使用指引。

**Windows 的 Playwright 扩展连接前先取得 Token。** 首次连接或需要重新连接时，先检查 `doctor` 的 `extension_token.present`；没有时向用户索要官方扩展 Token，优先请其配置到运行 Agent 的进程环境 `PLAYWRIGHT_MCP_EXTENSION_TOKEN`，等待实际提供后才执行 `browser connect`。用户已提供时由 Agent 通过进程环境传入；已连接的可用会话沿用，不重复询问。Token 不复述、不写入项目、检查点或发布包，也不作为 `browser resolve --note` 的内容。设置方式见[连接前的 Token](references/cli.md#连接前的-token)。Apple Events、纯 PubMed 接口及离线流程不需要它。

**执行 macOS 界面自动化和原生保存时，Agent/Harness 会请求系统无障碍（辅助功能）权限，以及控制 Chrome / System Events 的自动化权限。授权前须说明用途；用户有安全顾虑或拒绝授权时停止该操作，不反复索要或换工具绕过。** 权限提示见两端安装说明。Windows 当前保存窗口由用户操作，不为其虚构一项 macOS 式的无障碍授权。

1. 新用户先读[平台安装](references/install-windows.md)（Windows）或[macOS 安装](references/install-macos.md)。PubMed 官方接口检索、元数据与题录只需要 Python 和网络，不要求 Chrome、Node.js 或扩展；PMC 官方公开文件也可直接下载。需要出版社会话时才连接浏览器。其他浏览器流程默认沿用已登录 Chrome，不导出 cookie；Windows 扩展后端为预览，实机验收状态见 `VERIFICATION.md`。
2. 使用 `scripts/academic.py` 统一入口；机器调用将 `--json` 放在子命令之前。自定义编排也应调用该入口，不直接导入 `cnki.download` 等内部函数，它们不能作为独立 API 使用。Windows 使用 `py -3`，macOS 使用 `python3`。浏览器连接后绑定选定标签，同一用户的浏览器任务串行执行。出现 `needs_user` 时停止调度，待用户处理后重跑；原始 shell 入口仅用于兼容 macOS。
3. CNKI 登录/机构权限在中文或外文模式检查；WoS 机构访问在 basic-search 检查。不要要求 Scholar 或纯离线整理任务先登录知网。机构访问与 WoS 顶栏个人 Sign In 不同。
4. 外文库/WoS 没有知网式 PDF/CAJ 按钮，禁止对这些详情页运行 `cnki_click.js`。外文全文走完整 DOI → 出版社，或真实可用的 PDF 链接。
5. 中文下载保留详情页 referrer。macOS Apple Events 保持页内跳转；Windows 扩展方式点击已核对的可见按钮，保留网站点击事件，并监听下载。不要直接 open/curl 知网下载地址，或在没有落盘时自行追加点击。语言库状态会跨检索保留，中文检索前点回中文。
6. 验证码、人机验证、登录墙按上面的人工交接处理，不自动绕过。只能根据该篇在验证完成后的实际页面确认权限；期刊为订阅制、缺少机构标识、HTTP 请求失败都不能单独证明无权限。网络错误、链接缺失与非 OA 不混为“机构订阅”。
7. 开始下载/整理前查看工作区已有分类与相关目录，复用用户归档结构，避免覆盖与重复下载。目标未指定时补齐路径。跨设备移动使用支持复制再删除的归档流程。
8. 页面等待按目标页面和内容稳定性判断，并保留超时；访问节奏与页面就绪独立。不要为提速取消作者匹配、文件稳定性验证、PDF 类型检查或验证码暂停。

## 目录与交付要求

每条文献都要有可点击的发布页链接：题名写成 `[题名](url)`，另保留 `- 链接：` 或 `- 全文：` 行。URL 优先使用出版社落地页/完整 DOI，其次知网摘要页、Scholar 题名 href、WoS full-record，最后才用侧栏 PDF 并注明来源。不能输出无 URL 的正式目录条目；未抽出链接的条目单独记为待补，不能静默当作已完成。

使用各模式的题录脚本，保持来源、题名、作者、年、DOI 等真实提取值；缺失字段不猜测。外文 DOI 可能被截断，下载前按外文参考文档补齐。只有中文搜索结果行时不要误套外文完整元数据格式。

Windows 含双引号的复杂检索式使用 UTF-8 `--query-file`，避免 PowerShell 5.1 / `.cmd` 参数拆分；例子见统一命令行。检索精度调整须同时说明可能减少召回，不强制所有主题词使用标题字段。

搜索/提取进度保存在输出旁的 `.progress.json`。同参数重跑会复用已完成页/URL；要重新获取最新结果时用 `--refresh`。部分完成的结果不能汇报成全部完成。批量下载的身份与文件核验机制见中文参考文档。

全文落盘后核对实际文件类型、题名作者和归档路径，并核对是文章正文而非附录/补充材料；`pdf_pages.py` 给出页数辅助信息，页数不能独自证明正文身份，null 不单独证明下载失败。统计排除 `._*`，CAJ 格式单独注明。

所有 PDF 归档与续跑共用完整性检查，并使用可选 `pypdf` 检查解析、页数；取得可靠题名作者时再核对首页身份。**未安装或文字提取失败仍可完成格式检查与归档**，必须标记“正文未自动核验”；文件不完整、已安装解析器却无法解析、或明确身份不符时均不能计为成功正文；保留文件并报告具体原因。结束时分别报告“已归档”和“已完成正文自动核验”，说明本轮是否安装并使用了 `pypdf`。未自动核验时提醒：可能未发现错篇、正文与附录混淆或解析问题；安装方式为在 Skill 目录运行 `python3 -m pip install -r requirements-pdf.txt`（Windows 用 `py -3`），重跑原下载命令核验已有文件，无需重下。

汇报目录与归档路径、已有资源、本次新增全文数、仅题录数，以及失败/待人工清单。将检索命中总数、本次抽取数与最终交付数区分开。

PubMed 下载后用 `bibliography pubmed metadata.json 目录.md --progress 清单.json.batch-progress.json` 合并题录和下载状态；同时核对输出的 `discrepancies`。分别报告已归档、正文自动核验和人工核验数量，不用 `free` 代替下载完成状态。
