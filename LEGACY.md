# Legacy Version 1（macOS 可选下载）

> **重要权限与安全提示：使用 macOS 界面自动化时，Agent/Harness 可能向你请求系统无障碍（辅助功能）权限，以及控制 Chrome / System Events 的自动化权限。无障碍授权允许应用控制系统界面，范围不限于网页。若有任何安全顾虑，请勿使用本 Skill，也不要授予相关权限。**
>
> **Accessibility and safety: macOS automation may request system Accessibility and automation permissions. If you have security concerns, DO NOT USE THIS SKILL or grant these permissions.**

Legacy Version 1 保留原主分支的 `1.6.0` 代码，面向需要继续使用旧版知网、Google Scholar 或 Web of Science 流程的 macOS 用户。它没有 2.0 的 PubMed 支持、Windows 后端或新的下载核验修复。

- 保留分支：[legacy-version-1](https://github.com/spectrum527/academic-automation-skill/tree/legacy-version-1)。
- 同一 [Latest Release](https://github.com/spectrum527/academic-automation-skill/releases/latest) 提供 `academic-automation-legacy-v1.6.0-macos.zip`。
- 历史 [v1.6.0 Release](https://github.com/spectrum527/academic-automation-skill/releases/tag/v1.6.0) 和此前标签继续保留。

解压后仍得到 `cnki-download`。安装到当前 Agent 使用的 Skill 目录，整体选择 RC1 或 Legacy 其中一个版本；两者 Skill 名相同，不能混合覆盖源码，也不应同时作为活动 Skill 加载。切换前备份原安装及任务记录，保留已有文献。2.0 的检查点不能交给 1.x 续跑；旧流程按包内原始 `SKILL.md` 执行。

Legacy 的运行源码、Skill 和原始 README 保持旧主分支内容。包内额外的 `LEGACY_SOURCE.json` 记录冻结提交和各文件 SHA-256；`INSTALL.md` 是本说明。包不捆绑 Python、Chrome、浏览器配置或文献文件，仍需自行准备 macOS 日常 Chrome、Python，并启用 Chrome 的 Allow JavaScript from Apple Events。

维护者可用 `python3 scripts/build_release.py --legacy-ref <冻结提交>` 在生成 RC1 两个平台包的同时生成 Legacy 包，三个附件共同写入 `SHA256SUMS`。
