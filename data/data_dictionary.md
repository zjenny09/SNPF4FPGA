# 数据字典

本目录只含**项目自产的处理结果**，不含第三方 RTL、BLIF、架构 XML、VPR 工作目录或模型二进制。
所有 CSV 均以 UTF-8 编码，部分沿用源文件的 BOM，读取时请用 `utf-8-sig`。

## 1. `results/` —— 主观察与单点证据

| 文件 | 行数 | 主键 | 说明 |
|---|---:|---|---|
| `prefix_quality.csv` | 176 | (`group_id`,`policy`,`p`,`sensitivity`) | 冻结名单每个前缀的覆盖与 regret；`policy=group_candidate_prior` 为仅排序器策略，`group_fusion` 为完整方法 |
| `member_losses.csv` | 512 | (`group_id`,`policy`,`p`,`member_id`) | 名单内所选 ADP 点的逐成员损失，用于最差成员损失论述 |
| `group_fronts.csv` | 2288 | (`group_id`,`candidate_id`) | 目标集合的聚合面积/延迟/ADP 与前沿标记，可复算覆盖分母与 6.09% ADP 界 |
| `source_response_integrity.csv` | 28 | (`cohort`,`member_id`) | 28 个评分成员的物理矩阵完整性：计划/成功/失败/缺失 |
| `evaluation_manifest.json` | — | — | 输入与输出的 SHA-256、协议哈希、行数、目标数等冻结身份锚 |
| `EVALUATION_REPORT.md` | — | — | 人可读结果摘要 |

`prefix_quality.csv` 的 `sensitivity` 列区分主目标（`False`，10 个）与 NN 来源敏感性目标（`True`，1 个，不计入任何均值）。
`adp_worst_member_loss_pct` 与 `selected_*_id` 给出该前缀选中的面积/CPD/ADP 点。

## 2. `results/natural_references/` —— 揭盲后的回顾性评分

这些结果属于**回顾性补充**，不是预声明实验，也不是前瞻验证。身份字段在 `reference_manifest.json` 与 `reference_protocol.json` 中保留（`reference_id`、`scientific_status`、`random_is_exact_expectation=true`）；显示标识经过中性化，原有来源哈希不重算。

| 文件 | 行数 | 说明 |
|---|---:|---|
| `comparison_quality.csv` | 320 | 四条策略 × 10 组 × 8 个预算的覆盖与 regret；`quality_kind=exact_expectation` 为随机策略的精确期望，`frozen_observation` 为冻结观察 |
| `reference_quality.csv` | 160 | 随机参照的独立记录（与上一文件的随机行重叠） |
| `cohort_mean_quality.csv` | 64 | 两个队列 × 四策略 × 预算的等权均值，`support_count` 为参与组数 |
| `epsilon_sensitivity.csv` | 80 | 容差 0%/1%/5% 的重评分（仅 `p=8`） |
| `shortlist_exchange.csv` | 288 | 名单交叉交换后的重评分（`donor_group_id` 提供名单，`group_id` 被评分） |
| `catalog_difficulty.csv` | 10 | 真实前沿点数、单候选最大覆盖、全覆盖所需最小候选数 |
| `reference_manifest.json` / `reference_protocol.json` | — | 回顾性评分的身份与哈希 |

`quality_kind` 取值含义：

- `exact_expectation`：同一目录与预算下无放回随机策略的精确期望（解析值，非抽样）。
- `frozen_observation`：冻结名单的实际观察值。
- `posthoc_frozen_list_diagnostic`：揭盲后对未改动名单与矩阵的重评分诊断。
- `posthoc_truth_bound_not_deployable_baseline`：真实前沿的可达界，不可作为可用方法基线。

## 3. `matrix/qor_long_72x208.csv` —— 逐候选物理响应长表

72 个设计 × 208 个候选 = 14 976 行，包含评分所用物理响应输入。

| 列 | 含义 |
|---|---|
| `target_cohort` | `history`（52 个历史设计）或 `additional`（20 个补充设计） |
| `member_id` | `域/电路`，与 `inventory72.json` 的成员标识一致 |
| `domain`, `circuit` | 应用域与电路名 |
| `anchor`, `K`, `N`, `routing_id` | 候选参数；`candidate_id = anchor_routing_id`，与 `candidate_catalog.json` 对齐 |
| `status` | VPR 状态。以 `OK` 开头者计入成功族（`OK`、`OK_RT2_RT10_NOT_REACHED`、`OK_RT10_NOT_REACHED`） |
| `route_success`, `fail_category` | 路由结果与失败类别 |
| `cpd_ns` | 最终关键路径延迟 |
| `full_total_area_br_eta07` | 冻结评分采用的面积代理（η=0.7） |
| `full_adp_br_eta07` | 上述面积与 `cpd_ns` 的乘积 |
| `blif_sha256`, `physical_xml_sha256` | 该行使用的网表与架构文件哈希 |

**失败口径**：7 条记录属于非 OK 族（`dsp/epfl_div` 1 条、`dsp/epfl_sqrt` 3 条、`ctrl/mips_16_vtr` 3 条），其 QoR 列留空、记录保留、不删除也不填补。`ctrl/mips_16_vtr` 只存在于库存，不参与训练或评分，故评分目标是 9 组 208/208 与 DSP EPFL 205/208。

本表是**导出副本**：两套源矩阵保持原样并以其 SHA-256 为身份凭证，见 `results/evaluation_manifest.json` 的 `sources` 字段。`full_total_area_br_eta03/eta10` 等未在本表列出的字段仍在源矩阵中，本包不复制。

## 4. `protocol/` —— 冻结协议、目录与库存

| 文件 | 说明 |
|---|---|
| `frozen_protocol.json` | 折划分、来源闭包、面积/CPD 列绑定、候选语义；其 `main_target_count=7` 是首轮预声明口径 |
| `candidate_catalog.json` | 208 个候选的完整参数（`K`、`N`、`Fc_in`、`Fc_out`、`Fs`、`SB_type`、段长等） |
| `inventory72.json` | 72 个成员的 K4/K6 BLIF 路径与哈希、队列、场景、特征文件 |
| `isolation_units.json` | 72 成员 → 65 个隔离单元的映射（用于来源隔离） |
| `feature_schema.json` | 61 维组特征与 30 维成员特征名 |
| `frozen_source_manifest.json` | 全量源文件哈希 |
| `benchmark_sources.csv` | 72 项基准设计的来源索引：上游仓库、提交号、SPDX 许可、许可依据、再分发状态、顶层、文件清单与 K4/K6 网表哈希 |
| `training_groups/*.json` | 6 个模型的训练组成员定义 |

评估口径以 `results/evaluation_manifest.json` 的 `main_target_count=10` 为准；`frozen_protocol.json` 中的 7 是首轮预声明的初始集合数，后续扩展到 10。

## 5. `shortlists/` —— 冻结名单

`shortlists.csv` 把 11 组 × 2 策略 × 8 步的冻结名单转录为一行一步：`step` 为选择次序，`candidate_id` 为该步选中候选，`selected_ids` 为 `;` 分隔的完整 8 步名单，`fusion_score`/`prior_score`/`group_cond_gain` 等为当步内部量，尾部携带 `model_sha256`、`protocol_sha256`、`shortlist_sha256`、`shortlist_frozen_at`。

同名 `.json` 是冻结名单的公开副本，`.manifest.json` 保留来源快照的哈希记录。公开副本的显示标识和路径经过中性化；`protocol_sha256`、`model_sha256`、`shortlist_sha256`、`source_sha256` 及来源清单中的原有哈希标识来源快照，不能当作当前公开文件的字节哈希。当前发布文件仅按根目录 `MANIFEST.sha256` 校验。`source_snapshot/` 路径是来源快照的中性定位串，不表示本包实际包含对应文件。CSV 与 JSON 的成员、候选及选择次序保持不变。

## 6. `diagnostics/` —— 可选诊断

| 文件 | 行数 | 说明 |
|---|---:|---|
| `cost_summary.csv` | 220 | 冻结名单的计时（`origin=frozen_shortlist_cost_not_remeasured`），不是重新测量的运行成本 |
| `feature_cache_identity_audit.csv` | 144 | 72 成员 × 2 预算的特征缓存一致性（`identity_match` 全为 `True`） |

## 7. 常见口径问题

- **覆盖率单位**：`coverage_3pct` 为 0–1 小数；按百分比展示时乘 100。
- **regret 单位**：`*_regret_pct` 已是百分数，直接引用。
- **组数**：`|G|` 等于成员数，见 `prefix_quality.csv` 的 `member_count`。
- **无穷值**：预期出现的 `inf` 表示该组在该策略下没有保留任何共同有效候选，属于保留在分母中的失败，不可丢弃。
