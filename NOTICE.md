# 第三方材料与来源说明

## 本包不含第三方 RTL

本仓库只分发项目自产的**处理结果**：冻结候选目录、目标分组、逐候选物理响应数值、冻结名单与评分表。
不含任何第三方 RTL 源码、综合网表（BLIF）、VPR 架构 XML、布局布线中间文件或工具链二进制，
因此不转移任何上游权利。

## 上游来源记录

`data/protocol/benchmark_sources.csv` 是唯一的来源索引，逐设计给出：

| 列 | 含义 |
|---|---|
| `member_id` | `域/电路`，与 `inventory72.json` 一致 |
| `cohort` | `history`（52 项）或 `additional`（20 项） |
| `horizonarch_scope` | 该设计在公开框架仓库 HorizonArch 的基准清单中的归属（`in_scope` 或 `not_listed`） |
| `upstream_repository` | 上游仓库地址 |
| `upstream_revision` | 上游提交号 |
| `license_spdx` | SPDX 许可标识 |
| `license_evidence` | 许可判定依据（许可文件、源码头、上游清单等） |
| `redistribution_status` | `approved`（可按许可随仓分发）、`download-only`（仅可按地址下载）、`not_recorded`（本包未记录判定） |
| `upstream_path` | 上游文件路径或固定下载地址 |
| `top` / `rtl_files` | 综合顶层与文件清单 |
| `blif_k4_sha256` / `blif_k6_sha256` | 实验中使用的 K4/K6 网表哈希 |

分布：52 项历史设计来自 HorizonArch 的基准清单（其中 34 项由该仓库按上游许可在仓内提供，18 项以固定提交下载）；
20 项补充设计来自 EPFL 组合基准、VTR 仓内 Koios 网络、Secworks、ZipCPU 及若干钉定提交的 RISC-V 与外设核。
许可标识按 SPDX 记录，包含 `MIT`、`BSD-2-Clause`、`BSD-3-Clause`、`Apache-2.0`、`ISC`、`LGPL-2.1-or-later`、
`LGPL-3.0-only`、`GPL-2.0-or-later`、`GPL-3.0-only`、`LicenseRef-OpenCores-Permissive`、
`LicenseRef-Upstream-Benchmark-Terms` 与 `NOASSERTION`。**后两者表示上游未给出明确许可头或按逐基准条款处理**，
使用方需自行确认，不得据本表推断可再分发。

需要 RTL 时请按 `upstream_repository` 与 `upstream_revision` 回到上游获取，并遵守其许可。

## 工具链

实验使用 OpenFPGA 主干（含 VTR 与 Yosys 子模块）在 Ubuntu 20.04 上构建；工具链本身不随本包分发。

## 引用

若使用本数据，请引用 SNPF4FPGA 数据集及所用发布版本：https://github.com/zjenny09/SNPF4FPGA 。来源定位串不意味着本包分发了对应上游文件；原有来源哈希标识实验快照，当前发布文件字节以根目录 `MANIFEST.sha256` 为准。
