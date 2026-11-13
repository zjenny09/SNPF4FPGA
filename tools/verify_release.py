#!/usr/bin/env python3
"""校验本发布包的完整性与可复核性。

只读运行，不依赖第三方库，不改任何文件。做三件事：

1. 按 ``MANIFEST.sha256`` 逐文件校验 SHA-256。
2. 校验 ``data/matrix/qor_long_72x208.csv`` 的维度与失败记录保留口径。
3. 从发布 CSV 复算 10 组 × 4 策略 × 2 指标的 80 个数值，以及 2 队列 × 4 策略 × 2 指标的 16 个均值数值，与冻结数值比对。

用法::

    python tools/verify_release.py
"""

from __future__ import annotations

import csv
import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

# 冻结数值：B=8 的 3% 组前沿覆盖率与保留组 ADP regret（%）。
# 列顺序：coverage(uniform, balanced, ranker, full) | adp regrett(uniform, balanced, ranker, full)
TABLE2 = {
    "historical_serial3": (38.15, 39.92, 81.82, 100.00, 13.20, 11.96, 3.33, 0.00),
    "historical_cpu2": (27.27, 28.27, 55.56, 66.67, 9.28, 8.32, 10.10, 4.42),
    "historical_weighted2": (34.62, 37.81, 41.67, 75.00, 7.36, 6.03, 2.90, 2.90),
    "historical_cipher4": (26.39, 27.78, 76.92, 76.92, 9.90, 9.09, 3.02, 0.00),
    "external_serial3": (38.94, 40.40, 100.00, 100.00, 9.22, 8.30, 2.13, 2.13),
    "external_cpu2": (45.83, 49.59, 100.00, 100.00, 6.93, 5.78, 1.04, 1.04),
    "external_weighted4": (41.35, 43.29, 71.43, 100.00, 6.58, 5.97, 3.89, 0.00),
    "external_cipher4": (31.40, 32.31, 100.00, 100.00, 7.53, 6.85, 1.14, 0.00),
    "external_dsp_zipcpu2": (36.25, 38.89, 55.56, 88.89, 6.81, 5.76, 2.67, 0.00),
    "external_dsp_epfl2": (47.14, 50.85, 100.00, 100.00, 8.42, 7.60, 0.00, 1.30),
}

TABLE2_MEANS = {
    "history": (31.60, 33.45, 63.99, 79.65, 9.93, 8.85, 4.84, 1.83),
    "extra": (40.15, 42.56, 87.83, 98.15, 7.58, 6.71, 1.81, 0.75),
}

POLICY_ORDER = ("uniform_random", "balanced_random", "group_candidate_prior", "group_fusion")

EXPECTED = {
    "members": 72,
    "candidates": 208,
    "matrix_rows": 72 * 208,
    "scored_members": 28,
    "shortlist_groups": 11,
    "shortlist_rows": 176,
}


def fail(message: str) -> None:
    print(f"失败: {message}")
    sys.exit(1)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def check_manifest() -> int:
    manifest = ROOT / "MANIFEST.sha256"
    if not manifest.is_file():
        fail("缺少 MANIFEST.sha256")
    checked = 0
    for line in manifest.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        digest, _, relpath = line.partition("  ")
        target = ROOT / relpath
        if not target.is_file():
            fail(f"清单中的文件不存在: {relpath}")
        actual = hashlib.sha256(target.read_bytes()).hexdigest()
        if actual != digest:
            fail(f"哈希不一致: {relpath}")
        checked += 1
    print(f"[1/3] MANIFEST.sha256 校验通过，共 {checked} 个文件")
    return checked


def check_matrix() -> None:
    rows = read_csv(DATA / "matrix" / "qor_long_72x208.csv")
    if len(rows) != EXPECTED["matrix_rows"]:
        fail(f"长表行数 {len(rows)} != {EXPECTED['matrix_rows']}")
    members = {row["member_id"] for row in rows}
    candidates = {row["candidate_id"] for row in rows}
    if len(members) != EXPECTED["members"] or len(candidates) != EXPECTED["candidates"]:
        fail(f"长表维度异常: {len(members)} 成员 / {len(candidates)} 候选")
    if len(rows) != len(members) * len(candidates):
        fail("长表不是完整笛卡尔积")

    null_qor = [row for row in rows if not row["cpd_ns"]]
    ok_family = [row for row in rows if row["status"].startswith("OK")]
    if len(null_qor) != len(rows) - len(ok_family):
        fail("空 QoR 行与非 OK 族状态行数不一致，失败记录口径被破坏")
    for row in null_qor:
        if row["status"].startswith("OK"):
            fail(f"OK 族记录缺少 QoR: {row['member_id']} {row['candidate_id']}")

    integrity = {row["member_id"]: row for row in read_csv(DATA / "results" / "source_response_integrity.csv")}
    if len(integrity) != EXPECTED["scored_members"]:
        fail(f"完整性表成员数 {len(integrity)} != {EXPECTED['scored_members']}")
    for member_id, row in integrity.items():
        if row["missing"] != "0":
            fail(f"缺失记录不为 0: {member_id}")
    for member_id in ("dsp/epfl_div", "dsp/epfl_sqrt"):
        successes = sum(1 for row in rows if row["member_id"] == member_id and row["status"].startswith("OK"))
        if successes != int(integrity[member_id]["success"]):
            fail(f"{member_id} 成功数 {successes} 与完整性表 {integrity[member_id]['success']} 不一致")
    print(f"[2/3] 长表 {len(rows)} 行 = {len(members)} 成员 x {len(candidates)} 候选；"
          f"{len(null_qor)} 条路由失败记录保留，QoR 留空")


def check_table2() -> None:
    prefix = [r for r in read_csv(DATA / "results" / "prefix_quality.csv")
              if r["p"] == "8" and r["sensitivity"] == "False"]
    reference = [r for r in read_csv(DATA / "results" / "natural_references" / "comparison_quality.csv")
                 if r["p"] == "8" and r["quality_kind"] == "exact_expectation"]
    means = [r for r in read_csv(DATA / "results" / "natural_references" / "cohort_mean_quality.csv")
             if r["p"] == "8"]

    observed: dict[str, dict[str, tuple[float, float]]] = {}
    for row in reference + prefix:
        observed.setdefault(row["group_id"], {})[row["policy"]] = (
            float(row["coverage_3pct"]) * 100.0,
            float(row["adp_regret_pct"]),
        )

    for group_id, expected in TABLE2.items():
        values = observed.get(group_id, {})
        coverages = tuple(round(values.get(policy, (float("nan"), 0.0))[0], 2) for policy in POLICY_ORDER)
        regrets = tuple(round(values.get(policy, (0.0, float("nan")))[1], 2) for policy in POLICY_ORDER)
        got = coverages + regrets
        if got != expected:
            fail(f"逐组数值不一致 {group_id}: 复算 {got} != 冻结值 {expected}")

    mean_seen = {(r["cohort"], r["policy"]): (round(float(r["coverage_3pct"]) * 100.0, 2),
                                              round(float(r["adp_regret_pct"]), 2)) for r in means}
    for cohort, expected in TABLE2_MEANS.items():
        for index, policy in enumerate(POLICY_ORDER):
            want = (expected[index], expected[index + 4])
            if mean_seen[(cohort, policy)] != want:
                fail(f"队列均值不一致 {cohort}/{policy}: {mean_seen[(cohort, policy)]} != {want}")

    shortlists = read_csv(DATA / "shortlists" / "shortlists.csv")
    if len(shortlists) != EXPECTED["shortlist_rows"]:
        fail(f"名单行数 {len(shortlists)} != {EXPECTED['shortlist_rows']}")
    if len({r["group_id"] for r in shortlists}) != EXPECTED["shortlist_groups"]:
        fail("名单组数不等于 11")

    sources = read_csv(DATA / "protocol" / "benchmark_sources.csv")
    if len(sources) != EXPECTED["members"]:
        fail(f"来源清单行数 {len(sources)} != {EXPECTED['members']}")
    for row in sources:
        for key in ("upstream_repository", "upstream_revision", "license_spdx"):
            if not row[key]:
                fail(f"来源记录缺 {key}: {row['member_id']}")
        if row["horizonarch_scope"] == "in_scope" and not row["cohort"] == "history":
            fail(f"历史队列归属矛盾: {row['member_id']}")

    print(f"[3/3] {len(TABLE2)} 组 x 4 策略 x 2 指标的 80 个数值与 {len(TABLE2_MEANS)} 队列 x 4 策略 x 2 指标的 16 个均值数值全部复算一致；"
          f"名单 {EXPECTED['shortlist_groups']} 组 x 2 策略 x 8 步；来源清单 {len(sources)} 项均有仓库、提交与许可")


def main() -> None:
    check_manifest()
    check_matrix()
    check_table2()
    print("发布包校验通过。")


if __name__ == "__main__":
    main()
