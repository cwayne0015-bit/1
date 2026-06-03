# 更新日志

**Show Me The Money** 的所有重要变更都记录在此。README 首页只展示当前版本，
更早的发布说明在这里归档。

[English](CHANGELOG.md) | [中文](CHANGELOG.zh-CN.md)

---

## v2.5.1 — 2026-05-12

继 v2.5.0 之后的小而实用的修复。

- **价值量化（Value Quantification）模块现在能在终端 markdown 阅读器中正确渲染。**
  之前的空表头两列表格（`| | |`）在 Claude Code 的终端渲染器中会塌缩成
  “Column 1 / Column 2” 的文字。已在 13 个 SKILL.md 文件中改为带**加粗前缀**的
  无序列表——在终端、GitHub 以及其他所有 markdown 阅读器中都能干净渲染。
- 在 `/money` 的模板中新增了一条明确规则，禁止再次引入空表头形式。
- **“What's New” 历史拆分为独立的更新日志。** 旧的发布说明原本内联在 README 中，
  越来越长；现在统一放到这里（英文版见
  [CHANGELOG.md](CHANGELOG.md)）。

---

## v2.5.0 — 2026-05-11

- **业务类型感知（7 种类型）。** 各技能会根据所构建业务的类型（如 API、开发者
  工具、消费级应用、内容、平台、服务、信息产品）调整其框架，而不再假设单一形态。
- **`/money-strategy iterate`** —— PMF 之后的迭代模式，跳过从零开始的框架，
  识别当前的约束瓶颈，并提出一个用于放松该瓶颈的假设。

---

## v2.4.0 — 2026-05-10

- 为 `/money-ops` 新增**运行模式**（open / staging / production），并配有
  编辑边界（edit perimeter）与紧急停止（panic stop）。
- **最窄下注（narrowest-bet）**陈述成为 `/money-discover` 的必需产出。
- `/money-product` 中的**发布生命周期**：VERSION + CHANGELOG + 发布说明。
- 在 OWASP 之外，为 `/money-quality` 新增 **STRIDE** 威胁建模。
- `/money-learn` 中跨所有项目共享的**组合（portfolio）经验沉淀**。
- 通过 `/money-upgrade` 实现**自动更新**。

---

## v2.3.1 — 2026-05-03

- 创始人原子（founder-atom）打磨、各技能提示框、以及一处工作流修复。

---

## v2.3.0 — 2026-05-03

- **创始人原子**知识库——小而可复用、可组合的经验单元。

---

## v2.2.0 — 2026-04

- **评审小组**（`/money-panel`）及四位评审员。
- 跨会话学习的基础能力。

---

## v2.1.0

- **跨会话状态管理** —— `/money-save`、`/money-restore`、`/money-report`。
