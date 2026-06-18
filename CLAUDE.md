# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

一篇投稿至 *Aerospace Science and Technology* 期刊的论文手稿，主题为"物理信息驱动的 LSTM 和 BiGRU 方法用于可机动卫星集群轨迹预测与意图识别"。使用 Elsevier CAS 双栏模板（`cas-dc.cls` v2.4）。

当前状态：全文已按 IEEE TAES 风格参考文献重写完毕，写作风格更严谨、技术细节更准确。包含问题建模、PI-LSTM轨迹预测、BiGRU意图识别、数值仿真与分析、结论等全部章节。待完成工作包括模型架构图（Fig. 1/2 目前为注释占位符）、最终润色和投稿准备。

## 关联代码仓库

三个独立的代码仓库与论文内容密切相关，论文中的描述应始终与代码实现保持一致：

| 代码目录 | 内容 | 关键文件 |
|---------|------|---------|
| `D:/Office/2026.1/意图识别论文/TrajectoryPrediction/` | PI-LSTM 轨迹预测模型 | `models/pinn_lstm.py`, `models/physics_loss.py`, `config.py` |
| `D:/Office/2026.1/意图识别论文/IntentRecognition_V2/` | BiGRU 意图识别模型 | `model.py`, `physics_features.py`, `config.py` |
| `D:/Office/2026.1/意图识别论文/IntentRecognitionDataset/` | 数据集生成（PPO仿真，5种机动意图） | `Env_1v1_3D_*.py`, `PPO_Max_std.py`, `merge_csv_Summary.py` |

### 数据集要点

- 共 5 种机动意图场景：Capture（捕获追击）、Detection（探测）、Lurk（潜伏）、Obstruction（遮挡）、Mix（混合），通过不同 PPO 奖励函数生成
- 先训练 PPO 策略收集单星轨迹，再随机分组为 N=2/3/4 的多星集群样本
- 标签 Y = [N, d_min, phi]：集群数量（2/3/4）、全局最近距离（km）、散布角（rad）
- 总样本 23,787，70/15/15 划分，seed 42

### 轨迹预测要点

- 基础架构：LSTM Encoder-Decoder + 残差 delta 预测（`TrajectoryLSTM`）
- PI增强：`DeltaVEstimator`（可微CW逆推）+ `ConditionBuilder`（模式嵌入+ΔvMLP）
- 物理损失：`PhysicsLoss`（CW自由演化残差 + 速度变化边界惩罚 + 平滑正则化）
- 数据流向：输入(10步) → Δv估计(9步) → 条件向量(8维) → 扩展输入(per-agent 6+8维) → Encoder(3层LSTM) → Decoder(3层LSTM, 自回归) → 输出(10步 delta)
- 约 2.9M 参数，训练 lr=1e-3, AdamW, cosine warmup, 早停 patience=50

### 意图识别要点

- 逐目标编码器：`PerTargetEncoder`（Conv1D投影 + 2层BiGRU, hidden=128, 输出256维嵌入）
- 置换不变聚合：`SetAttentionAggregation`（4头注意力, learnable seed query）
- 成对交互模块：`PairwiseInteraction`（4种拼接→MLP→max-pooling→256维）
- 多任务头：N分类(CE) + d_min回归(Huber) + phi回归(MSE+余弦惩罚)
- 10通道物理特征：r, v, v_r, h, E, CW残差(pos/vel), cos_min/max/mean
- 9维全局特征：距离统计 + 速度统计 + 目标间关系统计
- 约 3.5M 参数，损失权重 λ_N=1.0, λ_d=1.0, λ_φ=2.0

## 编译构建

```bash
# 单次编译（用于快速检查格式）
pdflatex -interaction=nonstopmode manuscript.tex

# 完全编译（含参考文献）
pdflatex -interaction=nonstopmode manuscript.tex
bibtex manuscript
pdflatex -interaction=nonstopmode manuscript.tex
pdflatex -interaction=nonstopmode manuscript.tex
```

编译产物 `manuscript.pdf` 即论文 PDF。

## Git 与 GitHub 备份

- 每次修改完论文内容（`.tex` 文件）后，必须及时做 git 提交，确保更改被版本记录
- 远程仓库地址：`git@github.com:NPULXY/IntentionRecognitionManuscript.git`（SSH，需先配置 SSH 密钥认证）
- 推送前先 `git status` 确认更改范围，`git add` 暂存相关文件（`.tex`、`.bib`、`figs/` 等），然后 `git commit` 并 `git push`
- 本地分支名为 `main`，与 GitHub 默认分支一致
- 重要节点（如完成章节重写、添加图表、格式修正）后务必提交并推送，防止本地工作丢失

## 关键文件

| 文件 | 用途 |
|------|------|
| `manuscript.tex` | 主稿件，含所有章节、图表、元数据 |
| `cas-dc.cls` | Elsevier CAS 双栏文档类（v2.4, 2024） |
| `cas-common.sty` | CAS 模板通用样式包 |
| `cas-model2-names.bst` | 参考文献格式（author-year 模式） |
| `cas-refs.bib` | 参考文献数据库（航天领域实际文献） |
| `figs/` | 图片目录（待添加模型架构图等） |
| `els-cas-templates/` | 官方 CAS 模板原始文件（参考用，非稿件文件） |
| `.gitignore` | 忽略 LaTeX 辅助文件（`.aux` `.log` `.out` 等）和 `.ps1` 脚本 |

## 模板注意事项

- `cas-dc.cls` 和 `cas-common.sty` 是出版社模板文件，不应修改
- 作者信息、署名（含 ORCID）、基金号等元数据已填入（三作者：罗轩宇、刘闯、岳晓奎，西北工业大学航空学院）
- 当前使用 `\bibliographystyle{cas-model2-names}`（author-year 模式），`natbib` 亦采用 `authoryear` 选项
- 模板中 `\tnotemark`/`\tnotetext` 用于标题脚注（基金致谢），`\cormark`/`\cortext` 用于通讯作者标注

## 论文架构

论文提出一个两阶段深度学习框架：

1. **Stage 1 — PI-LSTM 轨迹预测**（Section 3）：物理信息条件 LSTM，通过可微分 CW 反演估计 Δv 作为条件信号，结合物理一致性正则化损失。编码器-解码器结构，采用残差（delta）预测策略。约 290 万参数。

2. **Stage 2 — BiGRU 意图识别**（Section 4）：共享权重的 BiGRU 编码器 + 集合注意力聚合（来自 Deep Sets）+ 成对交互模块。多任务输出：N 分类、d_min 回归、φ 回归。输入包含 10 通道物理信息特征（CW 残差、轨道不变量、目标间余弦角等）。约 350 万参数。

## 写作风格说明（TAES 风格参考）

当前论文参考了 IEEE Transactions on Aerospace and Electronic Systems 论文的写作风格重写，主要遵循以下原则：

- **贡献明确**：Introduction 末尾以编号列表给出论文的关键贡献
- **数学严谨**：关键方程给出完整展开形式（如 CW 状态转移矩阵的非零元素）
- **结构清晰**：Problem formulation → Method → Analysis → Simulation → Conclusion
- **语言客观**：避免主观评价性词汇，使用精确的技术描述和定量指标
- **数据集完整描述**：明确说明数据生成方式、各场景的奖励结构和数据分布

与 TAES 风格的关键区别：本论文使用 Elsevier CAS 模板（双栏），而非 IEEE 模板。

## 待完成事项

- **模型架构图**：Fig. 1（PI-LSTM 架构）和 Fig. 2（BiGRU 架构）目前为注释占位符 `\begin{figure}`，需绘制并放入 `figs/`
- 论文提交前最终语言润色

## 翻译注释规则

在所有 `.tex` 文件的每个段落下方添加以 `%` 开头的中文翻译注释。具体规则如下：

- 每个正文段落（以空行分隔的文本块）后紧跟一行 `% 中文：...` 注释
- 图注、表注（caption）后添加对应的中文翻译注释
- 列表项（itemize/enumerate 的每个 `\item`）后添加中文翻译注释
- 摘要、关键词、研究亮点、作者贡献声明等元数据块后添加中文翻译注释
- 数学公式、算法伪代码、表格数据等 LaTeX 结构内部不添加注释，仅在其前后的说明文本后添加
- 此规则适用于所有已提交的 `.tex` 文件
- **同步更新**：在修改、增删或重写任何 `.tex` 文件中的英文段落时，必须同时更新或添加对应的 `% 中文：...` 翻译注释，确保中英文内容始终保持一致，不允许出现仅有英文而无翻译注释，或翻译注释与英文内容不对应的情况