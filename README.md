# 自动化科研 Skill

这是一个面向 Codex 的自动化科研工作流 skill，用于辅助科学与工程方向的文献调研、研究路线比较、方案细化、实验执行、结果验证和论文写作。

它不是简单的“自动跑实验”提示词，而是一套带确认门、证据约束和实验审计的科研流程控制器。

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
