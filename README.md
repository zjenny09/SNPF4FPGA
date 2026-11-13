# SNPF4FPGA — 共享 FPGA 配置实验数据集

本项目共享已冻结的 eFPGA 候选配置目录、目标分组、逐候选物理响应、推荐名单与评分结果，供检查共享配置在覆盖率、面积、延迟和 ADP 上的取舍。

SNPF4FPGA shares frozen FPGA configuration catalogs, target groups, physical responses, recommendation lists, and evaluation results.

本包不含第三方 RTL、BLIF/网表、架构 XML、VPR 工作目录、CAD 工具链或训练模型二进制。它支持从已发布 CSV 复算指定评分与检查数据完整性，**不提供从综合、布局布线到模型重训练的全流程复现**。

## 1. 数据与证据边界

- 物理响应库存包含 72 个设计 × 208 个候选；历史队列 52 项，补充队列 20 项。
- 主评分包含 10 个目标组（历史队列 4 组、补充队列 6 组）；另有 1 个 NN 来源敏感性组，独立列示，不计入主组均值。
- 冻结名单是观测记录；随机参照为相同目录和预算下的精确期望，而非重复抽样结果。
- `natural_references/` 是读取响应后的回顾性补充与诊断，不是预声明实验或前瞻验证；真实前沿可达界不是可部署基线。
- 失败记录保留，QoR 留空；不得删除失败记录或将其填补为成功。

| 可复核内容 | 数据位置（相对 `data/`） |
|---|---|
| 预算 8 下 10 组 × 4 策略 × 2 指标，共 80 个逐组数值 | `results/prefix_quality.csv`、`results/natural_references/comparison_quality.csv` |
| 预算 8 下 2 队列 × 4 策略 × 2 指标，共 16 个均值数值 | `results/natural_references/cohort_mean_quality.csv` |
| 预算 1–8 的覆盖率与 ADP regret 曲线 | `results/prefix_quality.csv`、`results/natural_references/comparison_quality.csv` |
| 逐成员损失、组前沿与响应完整性 | `results/member_losses.csv`、`results/group_fronts.csv`、`results/source_response_integrity.csv` |
| 容差、名单交换与目录难度的回顾性诊断 | `results/natural_references/` |
| 冻结名单与选择次序 | `shortlists/` |

## 2. 校验方法

在解压后的项目根目录运行：

```bash
python tools/verify_release.py
```

脚本只读、仅使用 Python 标准库：按 `MANIFEST.sha256` 检查当前发布文件字节，检查物理响应长表维度与失败记录保留口径，并从 CSV 复算上述 80 个逐组数值与 16 个均值数值，与内置冻结数值逐项比较。它不运行综合、布局布线、训练或推理，也不将回顾性观察变为前瞻证据。

## 3. 目录

```
data/
  data_dictionary.md              # 字段、主键、口径与限制
  matrix/qor_long_72x208.csv      # 72 设计 × 208 候选的物理响应长表
  results/                        # 冻结名单评分、成员损失、组前沿、完整性
    natural_references/           # 回顾性随机参照与诊断
  protocol/                       # 协议、候选目录、库存、隔离单元、训练组
  shortlists/                     # 11 组冻结名单的公开副本与汇总 CSV
  diagnostics/                    # 冻结成本与特征缓存审计
tools/verify_release.py
MANIFEST.sha256
```

## 4. 来源快照与当前发布文件

| 字段 | 来源快照标识或评估口径 |
|---|---|
| `task_id` | `snpf4fpga-known-set-shared-parameters-v1` |
| `protocol_sha256` | `24d5c55a9acd96cd2996d3bb7bb8ef4b11aa2f45086781dfe725d33e6d0976da` |
| `reference_id` | `snpf4fpga-known-set-retrospective-natural-references-20261027-v3` |
| 回顾性评分日期 | 2026-10-27 |
| 主目标数 / 敏感性目标数 | 10 / 1 |
| 候选数 | 208 = 4 组 (K,N) × 52 路由配置 |
| 预算范围 | 1–8；8 为评估上限，不是推荐长度 |

`frozen_protocol.json` 的 `main_target_count=7` 是首轮预声明的初始集合数；后续扩展到 10 组，当前评分口径以 `results/evaluation_manifest.json` 的 `main_target_count=10` 为准。

公开副本对显示标识及本机路径作了中性化处理，未改动实测数值、成员、候选或选择次序。`protocol_sha256`、`model_sha256`、`shortlist_sha256`、`source_sha256` 及各来源清单中的原有哈希保留为**来源快照标识**，不表示修改后公开文件的当前字节哈希。当前发布文件仅以根目录 `MANIFEST.sha256` 校验。

`source_snapshot/` 下的路径是中性化的来源定位串，不代表本包包含该路径或文件；其他来源记录也可能指向未分发的实验输入。包内实际文件请按本目录结构查找。

## 5. 设计来源与许可

- 历史队列 52 个设计与公开框架仓库 [HorizonArch](https://github.com/zjenny09/HorizonArch) 的 benchmark 清单逐名对应；其中 34 项由该仓库按上游许可提供，18 项通过固定上游提交定位。
- 补充队列 20 个设计来自 EPFL 组合基准、VTR 仓内 Koios 网络、Secworks、ZipCPU 及钉定提交的 RISC-V 与外设核。
- 逐设计的上游仓库、修订、许可依据、再分发状态与网表哈希见 `data/protocol/benchmark_sources.csv`；成员来源定位及哈希另见 `data/protocol/inventory72.json` 与 `data/protocol/frozen_source_manifest.json`。
- 本包自产数据与代码采用 MIT，见 `LICENSE`；数据补充说明见 `LICENSE-DATA.txt`。第三方材料不随本包分发，权利仍归各上游，见 `NOTICE.md`。

## 6. 引用本数据集

引用时请记录所用发布版本及对应 `MANIFEST.sha256`，并使用项目地址：

```
SNPF4FPGA: Shared FPGA Configuration Experimental Dataset, 2026.
https://github.com/zjenny09/SNPF4FPGA
```
