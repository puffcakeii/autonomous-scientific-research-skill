# 自动化科研 Skill

一个面向 Codex 的自动化科研流程控制器：从文献路线、实验注册表、claim ledger 到泄漏审计，避免“自动跑实验但科研不成立”。

![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)
![Codex Skill](https://img.shields.io/badge/Codex-Skill-111827)
![Research Workflow](https://img.shields.io/badge/Workflow-Stage%200--4-2563eb)
![Claim Ledger](https://img.shields.io/badge/Integrity-Claim%20Ledger-16a34a)

它不是简单的“给 AI 一个目标然后自动跑实验”的脚本，而是一套带确认门、证据约束、实验审计和论文守门的科研工作流 skill。适合 AI、信号处理、生物医学、控制、材料、机械等需要真实数据、实验闭环和论文交付的研究项目。

## 为什么需要它

很多“自动化科研”流程容易出现三个问题：

- 没有真实数据源就开始设计路线；
- 只追单一分数或 review 分数，忽略泄漏、过拟合和协议漂移；
- 实验没验证完，就把结果写成论文贡献。

这个 skill 的核心目标是把这些风险前置：先确认数据和路线，再锁定协议，最后用指标、guardrail、泄漏审计和 claim ledger 判断结果是否真的成立。

## 核心能力

- 文献驱动的选题分析与研究路线设计
- 经典论文和近 5-10 年前沿工作的综述
- 3-5 条候选研究路线比较
- 最优方案细化、实验设计、baseline 锁定
- Stage 3 实验循环：运行、记录、保留或丢弃分支
- Stage 4 固定数据版本下的优化、消融和验证
- 泄漏、过拟合、协议漂移审计
- claim ledger：记录论文或报告中每个关键结论的证据状态
- review score sanity check：评审分数只能作为诊断信号，不能作为唯一目标
- 中文工程论文写作、润色、图表叙述和 claim-evidence 审核

## 适合谁

- 想用 Codex 做科研项目管理、实验执行和论文整理的用户
- 需要把“文献路线 - 实验 - 结果 - 论文 claim”串起来的研究者
- 做 AI/机器学习、信号处理、生物医学、控制、材料、机械等方向的学生或工程研究人员
- 不想让自动化实验变成“刷高分但不可复现”的团队

## 不适合什么

- 没有真实数据源、数据集或明确数据获取路径的空想项目
- 只想让模型无限试错刷分、但不关心泄漏和验证的任务
- 需要伪造论文、实验、指标、引用或审稿意见的任务
- 只想做文字包装、不愿暴露未验证 claim 的论文写作

## 工作阶段

- Stage 0：问题定义、真实数据源确认、目标和约束整理
- Stage 1：文献综述和候选研究路线，等待用户确认
- Stage 2：围绕确认路线形成详细最佳方案，再次等待用户确认
- Stage 3：在锁定协议下实现、调试、实验和记录
- Stage 4：在固定官方数据版本上进一步优化、验证和交付

该 skill 默认要求先有真实数据源或明确的数据获取路径。没有真实数据时，不会直接生成空想方案、实验路线或结果图表。

## 安装

将 skill 文件夹复制到 Codex 的 skills 目录：

```powershell
Copy-Item -Recurse .\autonomous-scientific-research "$env:USERPROFILE\.codex\skills\autonomous-scientific-research"
```

然后重启 Codex。

## 快速使用

在 Codex 中可以这样触发：

```text
使用 autonomous-scientific-research，帮我围绕这个研究方向做 Stage 0 intake，并检查真实数据源、研究目标、约束和成功标准。
```

如果已经有数据和方向，可以继续：

```text
使用 autonomous-scientific-research，基于我的数据和目标做 Stage 1 文献综述，给出 3-5 条候选研究路线，先不要实现，等我确认路线。
```

如果已经确认方案，可以进入实验：

```text
使用 autonomous-scientific-research，按已确认的 Stage 2 方案启动 Stage 3，先锁定 baseline、数据版本、split、primary metric、guardrail 和 keep/discard 规则。
```

## Python 环境配置

如果需要执行科研代码，请配置 GPU Python 解释器路径：

```powershell
$env:AUTONOMOUS_RESEARCH_PYTHON="C:\Users\<you>\.conda\envs\GPU\python.exe"
```

也可以在系统环境变量或 shell 配置中持久化该变量。

如果没有设置 `AUTONOMOUS_RESEARCH_PYTHON`，而任务又需要运行 Python，skill 会要求先配置解释器，不会随意切换到其他环境。

## 目录结构

- `autonomous-scientific-research/SKILL.md`：主 skill 说明和硬约束
- `autonomous-scientific-research/references/`：工作流、证据规则、领域分流、写作规则、实验循环和评审完整性规则
- `autonomous-scientific-research/scripts/init_stage3_registry.py`：初始化 Stage 3 实验注册表的辅助脚本
- `autonomous-scientific-research/agents/openai.yaml`：Codex UI 元数据

## 亮点：不把 review 分数当唯一目标

这个 skill 专门加入了 review-score sanity control：

- 高 review 分数不等于方法成立；
- 低 review 分数不等于方法无效；
- reviewer comment 需要先分级：validity-critical、method-critical、evidence-critical、presentation-critical、style-preference；
- 如果 review 分数提高，但泄漏风险、guardrail、claim 支撑或协议可比性变差，该分支应被丢弃或标记为 exploratory；
- 只有 metric gate、guardrail gate、leakage/overfit audit、claim ledger 和复现实物同时过关，才可以说科研结果成立。

## 设计原则

- 不把 review 分数当成唯一目标
- 不把一次跑通的 baseline 当成完成
- 不把未验证结果写成科研贡献
- 不编造论文、数据、指标、实验或引用
- 不在没有真实数据源时输出完整研究方案
- 不把泄漏或过拟合得到的高分当成有效结果

最终完成状态必须同时考虑指标门槛、guardrail 指标、泄漏/过拟合审计、claim ledger、复现实物和未解决限制。

## 许可证

本项目采用 GNU General Public License v3.0 开源许可证，详见 [LICENSE](LICENSE)。

这意味着你可以使用、复制、修改和分发本项目，但如果你分发修改后的版本，也需要按照 GPL-3.0 的要求开放相应源代码并保留许可证说明。
