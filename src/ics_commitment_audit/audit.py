from __future__ import annotations

from collections import defaultdict
from datetime import UTC, datetime

from .extractor import extract_commitments
from .models import (
    AuditReport,
    CheckResult,
    CheckStatus,
    CommitmentAudit,
    CommitmentRecord,
    DimensionResult,
    DocumentSummary,
    EvidenceSpan,
    IngestedDocument,
    ReportSummary,
    WeightPreset,
)
from .rules import get_weight_preset

DISCLAIMER = (
    "本报告只评估书面承诺的结构与可追溯性。它不是法律意见、鉴证意见、"
    "监管合规结论、投资建议，也不是漂绿判定。分数不衡量实际环境绩效。"
    "This report is not a legal opinion, assurance opinion, regulatory compliance "
    "finding, investment recommendation, or determination of greenwashing."
)


def _check(
    key: str,
    label: str,
    weight: float,
    status: CheckStatus,
    evidence: list[EvidenceSpan],
    note: str,
) -> CheckResult:
    multiplier = {
        CheckStatus.PRESENT: 1.0,
        CheckStatus.PARTIAL: 0.5,
        CheckStatus.MISSING: 0.0,
    }[status]
    return CheckResult(
        key=key,
        label=label,
        status=status,
        weight=weight,
        points=round(weight * multiplier, 4),
        evidence=evidence if status != CheckStatus.MISSING else [],
        note=note,
    )


def _matched_note(prefix: str, values: list[str]) -> str:
    if not values:
        return prefix
    return f"{prefix}: {', '.join(values[:6])}"


def _sources(record: CommitmentRecord, *keys: str) -> list[EvidenceSpan]:
    result: list[EvidenceSpan] = []
    seen: set[tuple[str, int | None, str]] = set()
    for key in keys:
        for item in record.evidence_by_fact.get(key, []):
            marker = (item.block_id, item.unit_index, item.text[:120])
            if marker not in seen:
                seen.add(marker)
                result.append(item)
    return result or [record.evidence]


def _observability(record: CommitmentRecord) -> DimensionResult:
    facts = record.facts
    has_quantitative = bool(facts.quantitative_expressions or facts.target_percentages)
    has_boundary = bool(facts.scopes_covered or facts.responsible_bodies)
    has_method = bool(facts.reporting_standards or facts.method_terms)
    has_progress = bool(facts.assurance_terms or facts.reporting_terms)
    checks = [
        _check(
            "quantified_target",
            "量化目标 / Quantified target",
            0.30,
            CheckStatus.PRESENT if has_quantitative else CheckStatus.MISSING,
            _sources(record, "quantitative", "timeframe"),
            _matched_note(
                "数值目标",
                facts.quantitative_expressions
                + [f"{value:g}%" for value in facts.target_percentages],
            )
            if has_quantitative
            else "未发现数值目标或百分比。",
        ),
        _check(
            "baseline",
            "基准年份或基准值 / Baseline",
            0.20,
            CheckStatus.PRESENT if facts.baseline_year else CheckStatus.MISSING,
            _sources(record, "baseline"),
            f"基准年：{facts.baseline_year}"
            if facts.baseline_year
            else "未发现明确基准年。",
        ),
        _check(
            "boundary",
            "边界、范围或责任主体 / Boundary",
            0.15,
            CheckStatus.PRESENT if has_boundary else CheckStatus.MISSING,
            _sources(record, "scope", "owner"),
            _matched_note(
                "边界线索",
                facts.scopes_covered + facts.responsible_bodies,
            )
            if has_boundary
            else "未发现范围、组织边界或责任主体。",
        ),
        _check(
            "timeframe",
            "目标年或中间里程碑 / Milestones",
            0.15,
            CheckStatus.PRESENT
            if facts.target_year or facts.milestone_years
            else CheckStatus.MISSING,
            _sources(record, "timeframe"),
            (
                f"目标年：{facts.target_year}；里程碑："
                f"{facts.milestone_years or '未发现'}"
            )
            if facts.target_year or facts.milestone_years
            else "未发现目标年或中间里程碑。",
        ),
        _check(
            "method",
            "核算标准或方法 / Method",
            0.10,
            CheckStatus.PRESENT if has_method else CheckStatus.MISSING,
            _sources(record, "standards", "method"),
            _matched_note(
                "方法线索",
                facts.reporting_standards + facts.method_terms,
            )
            if has_method
            else "未发现核算方法或可识别框架。",
        ),
        _check(
            "assurance_or_progress",
            "鉴证或定期进展披露 / Assurance",
            0.10,
            CheckStatus.PRESENT if has_progress else CheckStatus.MISSING,
            _sources(record, "assurance", "reporting"),
            _matched_note(
                "进展披露线索",
                facts.assurance_terms + facts.reporting_terms,
            )
            if has_progress
            else "未发现外部鉴证或定期进展披露。",
        ),
    ]
    return DimensionResult(
        key="V_obs",
        label="可观测性 / Observability",
        score=round(sum(check.points for check in checks), 4),
        checks=checks,
    )


def _enforceability(record: CommitmentRecord) -> DimensionResult:
    facts = record.facts
    has_owner = bool(facts.responsible_bodies)
    has_progress = bool(facts.reporting_terms or facts.milestone_years)
    has_binding = bool(facts.binding_terms)
    has_remedy = bool(facts.remedy_terms)
    has_assurance = bool(facts.assurance_terms)
    controlled_dependencies = not facts.conditional_terms or bool(
        facts.mitigation_terms
    )

    checks = [
        _check(
            "owner",
            "责任主体或监督机构 / Owner",
            0.15,
            CheckStatus.PRESENT if has_owner else CheckStatus.MISSING,
            _sources(record, "owner"),
            _matched_note("责任主体", facts.responsible_bodies)
            if has_owner
            else "未发现责任主体或监督机构。",
        ),
        _check(
            "progress",
            "进展报告或里程碑 / Progress",
            0.15,
            CheckStatus.PRESENT if has_progress else CheckStatus.MISSING,
            _sources(record, "reporting", "timeframe"),
            _matched_note(
                "进展机制",
                facts.reporting_terms + [str(year) for year in facts.milestone_years],
            )
            if has_progress
            else "未发现报告频率或里程碑。",
        ),
        _check(
            "binding",
            "监管、合同或薪酬约束 / Binding",
            0.25,
            CheckStatus.PRESENT if has_binding else CheckStatus.MISSING,
            _sources(record, "binding"),
            _matched_note("约束线索", facts.binding_terms)
            if has_binding
            else "未发现法律、监管、合同或薪酬约束。",
        ),
        _check(
            "remedy",
            "补救、处罚、纠正或升级机制 / Remedy",
            0.20,
            CheckStatus.PRESENT if has_remedy else CheckStatus.MISSING,
            _sources(record, "remedy"),
            _matched_note("补救线索", facts.remedy_terms)
            if has_remedy
            else "未发现失败后果或纠正机制。",
        ),
        _check(
            "assurance",
            "外部鉴证 / External assurance",
            0.10,
            CheckStatus.PRESENT if has_assurance else CheckStatus.MISSING,
            _sources(record, "assurance"),
            _matched_note("鉴证线索", facts.assurance_terms)
            if has_assurance
            else "未发现外部鉴证。",
        ),
        _check(
            "dependency_control",
            "受控依赖或备用方案 / Fallback",
            0.15,
            CheckStatus.PRESENT if controlled_dependencies else CheckStatus.MISSING,
            _sources(record, "conditional", "mitigation"),
            (
                "未发现未受控的条件性表述。"
                if not facts.conditional_terms
                else _matched_note(
                    "条件性表述配有备用方案",
                    facts.mitigation_terms,
                )
            )
            if controlled_dependencies
            else _matched_note(
                "存在条件性表述，但未发现备用方案",
                facts.conditional_terms,
            ),
        ),
    ]
    return DimensionResult(
        key="V_enf",
        label="可执行性 / Enforceability",
        score=round(sum(check.points for check in checks), 4),
        checks=checks,
    )


def _reversibility(record: CommitmentRecord) -> DimensionResult:
    facts = record.facts
    has_review = bool(facts.review_terms)
    has_trigger = bool(facts.revision_trigger_terms or facts.reporting_terms)
    has_withdrawal = bool(facts.withdrawal_terms)
    has_mitigation = bool(facts.mitigation_terms)
    has_staged = bool(facts.milestone_years or facts.staged_terms)

    checks = [
        _check(
            "review",
            "复核或修订机制 / Review",
            0.25,
            CheckStatus.PRESENT if has_review else CheckStatus.MISSING,
            _sources(record, "review"),
            _matched_note("复核线索", facts.review_terms)
            if has_review
            else "未发现复核或修订机制。",
        ),
        _check(
            "trigger",
            "修订触发条件或频率 / Trigger",
            0.20,
            CheckStatus.PRESENT if has_trigger else CheckStatus.MISSING,
            _sources(record, "trigger", "reporting"),
            _matched_note(
                "触发或频率线索",
                facts.revision_trigger_terms + facts.reporting_terms,
            )
            if has_trigger
            else "未发现修订触发条件或复核频率。",
        ),
        _check(
            "withdrawal",
            "撤销或退出程序 / Withdrawal",
            0.20,
            CheckStatus.PRESENT if has_withdrawal else CheckStatus.MISSING,
            _sources(record, "withdrawal"),
            _matched_note("撤销线索", facts.withdrawal_terms)
            if has_withdrawal
            else "未发现撤销或退出程序。",
        ),
        _check(
            "mitigation",
            "缓解、补偿或回滚路径 / Mitigation",
            0.20,
            CheckStatus.PRESENT if has_mitigation else CheckStatus.MISSING,
            _sources(record, "mitigation"),
            _matched_note("缓解线索", facts.mitigation_terms)
            if has_mitigation
            else "未发现缓解、补偿或回滚路径。",
        ),
        _check(
            "staged",
            "中间里程碑或分阶段实施 / Staged",
            0.15,
            CheckStatus.PRESENT if has_staged else CheckStatus.MISSING,
            _sources(record, "timeframe", "staged"),
            _matched_note(
                "分阶段线索",
                [str(year) for year in facts.milestone_years] + facts.staged_terms,
            )
            if has_staged
            else "未发现中间里程碑或分阶段实施。",
        ),
    ]
    return DimensionResult(
        key="V_rev",
        label="可逆性 / Reversibility",
        score=round(sum(check.points for check in checks), 4),
        checks=checks,
    )


def _grade(score: float) -> str:
    if score < 0.30:
        return "低结构完整性"
    if score < 0.50:
        return "有限结构完整性"
    if score < 0.70:
        return "中等结构完整性"
    if score < 0.85:
        return "高结构完整性"
    return "很高结构完整性"


def _warnings_and_recommendations(
    record: CommitmentRecord,
    dimensions: list[DimensionResult],
) -> tuple[list[str], list[str]]:
    facts = record.facts
    by_key = {dimension.key: dimension for dimension in dimensions}
    warnings: list[str] = []
    recommendations: list[str] = []

    if record.strength == "weak":
        warnings.append("表述使用努力、希望或条件性语言，承诺强度有限。")
        recommendations.append("使用明确的承诺动词，并说明该承诺是否具有约束力。")
    if not (facts.quantitative_expressions or facts.target_percentages):
        warnings.append("未发现量化目标。")
        recommendations.append("补充目标值、单位、范围、基准年和目标年。")
    if not facts.baseline_year:
        warnings.append("未发现明确基准。")
        recommendations.append("明确基准年和基准值。")
    if not facts.target_year:
        warnings.append("未发现目标年。")
        recommendations.append("补充目标年及中间里程碑。")
    if not facts.responsible_bodies:
        warnings.append("未发现责任主体或监督机构。")
        recommendations.append("指定责任部门和监督机构。")
    if not facts.binding_terms:
        warnings.append("未发现监管、合同或薪酬挂钩的约束机制。")
        recommendations.append("说明承诺是否具有约束力，以及违反时如何产生后果。")
    if not facts.remedy_terms:
        warnings.append("未发现补救或纠正机制。")
        recommendations.append("说明纠正措施、升级程序及失败后果。")
    if not facts.review_terms:
        warnings.append("未发现复核或修订机制。")
        recommendations.append("补充复核频率、修订触发条件及公开更新规则。")
    if facts.conditional_terms and not facts.mitigation_terms:
        warnings.append("存在条件性表述，但未发现备用方案。")
        recommendations.append("说明条件未满足时的处理方式。")
    if (
        facts.target_year
        and facts.target_year - datetime.now(UTC).year > 10
        and not facts.milestone_years
    ):
        warnings.append("只发现长期目标，未发现中间里程碑。")
        recommendations.append("在长期目标前增加带年份的中间里程碑。")
    if by_key["V_obs"].score < 0.40:
        warnings.append("按当前权重，可观测性偏低。")
    if by_key["V_enf"].score < 0.30:
        warnings.append("按当前权重，可执行性偏低。")
    if by_key["V_rev"].score < 0.30:
        warnings.append("按当前权重，可逆性 / 可修订性偏低。")

    return list(dict.fromkeys(warnings)), list(dict.fromkeys(recommendations))


def _audit_commitment(
    record: CommitmentRecord,
    weights: WeightPreset,
) -> CommitmentAudit:
    dimensions = [
        _observability(record),
        _enforceability(record),
        _reversibility(record),
    ]
    scores = {dimension.key: dimension.score for dimension in dimensions}
    crv_score = round(
        weights.V_obs * scores["V_obs"]
        + weights.V_enf * scores["V_enf"]
        + weights.V_rev * scores["V_rev"],
        4,
    )
    warnings, recommendations = _warnings_and_recommendations(record, dimensions)
    return CommitmentAudit(
        **record.model_dump(),
        dimensions=dimensions,
        crv_score=crv_score,
        grade=_grade(crv_score),
        warnings=warnings,
        recommendations=recommendations,
    )


def _document_warnings(commitments: list[CommitmentAudit]) -> list[str]:
    warnings: list[str] = []
    if not commitments:
        return [
            "未识别到承诺句。该结果不证明文件不存在承诺；请检查规则覆盖范围或原文结构。"
        ]

    same_year_targets: dict[tuple[str, int], set[float]] = defaultdict(set)
    for commitment in commitments:
        if (
            commitment.category == "E"
            and commitment.facts.target_year
            and commitment.facts.target_percentages
        ):
            same_year_targets[
                (commitment.subcategory, commitment.facts.target_year)
            ].update(commitment.facts.target_percentages)

    for (subcategory, year), values in sorted(same_year_targets.items()):
        if len(values) > 1:
            rendered = ", ".join(f"{value:g}%" for value in sorted(values))
            warnings.append(
                f"{subcategory} 在 {year} 年出现不同百分比目标：{rendered}。"
                "请确认这些目标属于不同范围，还是存在表述冲突。"
            )
    return warnings


def audit_document(
    document: IngestedDocument,
    weight_preset: str = "default",
) -> AuditReport:
    weights = get_weight_preset(weight_preset)
    records = extract_commitments(document)
    commitments = [_audit_commitment(record, weights) for record in records]
    document_warnings = _document_warnings(commitments)
    average = (
        round(sum(item.crv_score for item in commitments) / len(commitments), 4)
        if commitments
        else None
    )

    return AuditReport(
        generated_at=datetime.now(UTC),
        document=DocumentSummary(
            filename=document.filename,
            extension=document.extension,
            sha256=document.sha256,
            character_count=document.character_count,
            block_count=len(document.blocks),
            parse_warnings=document.warnings,
        ),
        weights=weights,
        summary=ReportSummary(
            commitment_count=len(commitments),
            average_crv=average,
            high_structure_count=sum(item.crv_score >= 0.70 for item in commitments),
            moderate_structure_count=sum(
                0.50 <= item.crv_score < 0.70 for item in commitments
            ),
            limited_structure_count=sum(item.crv_score < 0.50 for item in commitments),
            document_warnings=document_warnings,
        ),
        commitments=commitments,
        disclaimer=DISCLAIMER,
    )
