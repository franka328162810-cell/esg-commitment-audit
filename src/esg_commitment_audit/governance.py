from __future__ import annotations

import re
from datetime import UTC, datetime

from .models import (
    CheckStatus,
    DocumentSummary,
    EvidenceSpan,
    GovernanceCheck,
    GovernanceReport,
    GovernanceSummary,
    IngestedDocument,
)

GOVERNANCE_DISCLAIMER = (
    "This report reviews the written structure of an AI policy or governance "
    "document. It does not establish legal compliance, safety, truthfulness, "
    "or the actual behavior of an AI system. It is not a psychological test "
    "of any individual and must not be used for employment, education, credit, "
    "immigration, insurance, political, or judicial decisions."
)

CHECK_DEFINITIONS = [
    {
        "key": "scope_and_owner",
        "label": "Scope, effective date, and accountable owner",
        "groups": [
            [
                r"\b(?:this|the) (?:usage )?policy (?:applies to|covers|governs)\b",
                r"\bapplies to (?:all )?(?:users|people|developers|organizations|customers)\b",
                r"\byour use of .{0,80}\b(?:must|shall) follow\b",
                r"\b(?:restrictions|requirements) apply to\b",
                r"本政策(?:适用于|覆盖)",
                r"适用范围",
            ],
            [
                r"\bpolicy owner\b",
                r"\bowner of (?:this|the) policy\b",
                r"\baccountable (?:owner|executive|body)\b",
                (
                    r"\b(?:team|department|officer|committee)\b.{0,80}"
                    r"\bresponsible for (?:this|the) policy\b"
                ),
                r"政策负责人",
                r"责任主体",
            ],
            [
                r"\beffective(?: date)?\s*:\s*",
                r"\blast (?:modified|updated)\s*:\s*",
                r"\bversion date\s*:\s*",
                r"生效日期",
                r"最后更新",
            ],
        ],
        "present_min_groups": 3,
        "partial": [r"\bpolicy\b", r"\bgovernance\b", r"政策", r"治理"],
        "note": "Identifies what the policy governs and who is accountable.",
        "recommendation": "State the policy scope, effective date, and accountable owner.",
    },
    {
        "key": "review_cadence",
        "label": "Scheduled review or reconsideration",
        "strong": [
            r"\breview(?:ed)? (?:at least )?(?:every|annually|quarterly|semi-annually)\b",
            r"\bannual review\b",
            r"\bperiodic review\b",
            r"每年(?:审查|复核|评估)",
            r"定期(?:审查|复核|评估)",
            r"复核周期",
        ],
        "partial": [
            (
                r"\b(?:review(?:ed)?|reconsider|update|revise)\b.{0,100}"
                r"\b(?:policy|policies|rules|terms)\b"
            ),
            (
                r"\b(?:policy|policies|rules|terms)\b.{0,100}"
                r"\b(?:review(?:ed)?|reconsider|update|revise)\b"
            ),
            r"(?:复核|审查|更新|修订).{0,60}(?:政策|规则|条款)",
            r"(?:政策|规则|条款).{0,60}(?:复核|审查|更新|修订)",
        ],
        "note": "Provides a recurring opportunity to reconsider the policy.",
        "recommendation": "Specify a review cadence and the role responsible for initiating review.",
    },
    {
        "key": "revision_process",
        "label": "Defined revision authority and process",
        "strong": [
            r"\b(?:amend|revise|modify|update) (?:this |the )?policy\b",
            r"\brevision procedure\b",
            r"\bchange control\b",
            r"修订程序",
            r"修订权",
            r"变更审批",
            r"修改本政策",
        ],
        "partial": [
            (
                r"\b(?:amend|revise|modify|update)\b.{0,60}"
                r"\b(?:policy|policies|rules|terms)\b"
            ),
            (
                r"\b(?:policy|policies|rules|terms)\b.{0,60}"
                r"\b(?:amend|revise|modify|update)\b"
            ),
            r"(?:修订|更新|修改).{0,40}(?:政策|规则|条款)",
        ],
        "note": "Explains how the normative document itself can be changed.",
        "recommendation": "Define who may propose and approve changes, and what evidence is required.",
    },
    {
        "key": "version_history",
        "label": "Version history and change log",
        "strong": [
            r"\bversion history\b",
            r"\bchange log\b",
            r"\bchangelog\b",
            r"\brevision history\b",
            r"版本历史",
            r"变更记录",
            r"修订日志",
        ],
        "partial": [r"\bversion\b", r"版本号", r"版本"],
        "note": "Makes changes traceable after they occur.",
        "recommendation": "Publish a dated change log and retain prior versions.",
    },
    {
        "key": "notice",
        "label": "Advance notice to affected people",
        "strong": [
            r"\badvance notice\b",
            r"\b\d+\s+days?\s+(?:of )?(?:advance )?notice\b",
            (
                r"\b(?:notify|inform) "
                r"(?:users|affected|stakeholders|the public)\b.{0,80}\bbefore\b"
            ),
            r"\bprior notice\b|\bnotice prior to\b",
            r"提前通知",
            r"通知受影响",
            r"公告变更",
        ],
        "partial": [
            r"\b(?:notify|inform|notice) (?:users|affected|stakeholders|the public)\b",
            r"\bkeep up with .{0,40}\bupdates?\b",
            r"\bupdates? (?:page|feed|newsletter|form|subscription)\b",
            r"\bnotice\b.{0,80}\b(?:policy|policies|rules)\b",
            r"(?:订阅|关注).{0,40}(?:更新|修订|通知)",
        ],
        "note": "Allows affected parties to understand and respond to changes.",
        "recommendation": "Commit to advance notice, a minimum notice period, and a public archive.",
    },
    {
        "key": "appeal_human_review",
        "label": "Appeal and human review",
        "strong": [
            r"\bappeal\b",
            r"\bhuman review\b",
            r"\brequest (?:a )?human review\b",
            r"\bgrievance\b",
            r"申诉",
            r"人工复核",
            r"人工审核",
        ],
        "partial": [r"\breview request\b", r"\bcomplaint\b", r"投诉", r"复核申请"],
        "note": "Creates a route to challenge decisions or interpretations.",
        "recommendation": "Provide an appeal path with an independent human reviewer.",
    },
    {
        "key": "refusal_exit",
        "label": "Refusal, opt-out, and exit",
        "strong": [
            r"\bopt[- ]out\b",
            r"\bwithdraw consent\b",
            r"\brefuse\b",
            r"\bdiscontinue use\b",
            r"\bexit\b",
            r"退出",
            r"拒绝",
            r"撤回同意",
        ],
        "partial": [
            r"\bstop using (?:our|the) (?:services|products|platform)\b",
            r"\b(?:close|delete|terminate) your (?:account|workspace)\b",
            r"停止使用(?:本|该)?(?:服务|产品|平台)",
            r"(?:关闭|注销|删除).{0,20}(?:账户|账号)",
        ],
        "note": "Preserves an affected person's ability to decline or leave.",
        "recommendation": "Explain how refusal or exit works and what consequences follow.",
    },
    {
        "key": "monitoring_audit",
        "label": "Monitoring, audit logs, and evidence",
        "strong": [
            r"\baudit logs?\b",
            r"\baudit trails?\b",
            r"\bevidence records?\b",
            r"审计日志",
            r"审计追踪",
            r"证据记录(?:文件)?",
        ],
        "partial": [
            r"\bmonitor(?:ing|ed)?\b",
            r"\bdetection and monitoring\b",
            r"\baudit(?:ing)?\b",
            r"监控",
            r"审计",
        ],
        "note": "Supports verification of whether stated controls are operating.",
        "recommendation": "Define what is logged, who can review it, and how long it is retained.",
    },
    {
        "key": "rollback_deprecation",
        "label": "Rollback, suspension, and deprecation",
        "strong": [
            r"\brollback\b",
            r"\brevert\b",
            r"\bdeprecat(?:e|ed|ion)\b",
            r"\bsunset\b",
            r"\bsuspend (?:this|the) (?:policy|model|system|feature)\b",
            r"回滚",
            r"退役",
        ],
        "partial": [
            r"\bretir(?:e|ed|ing) (?:this|the) (?:policy|model|system|feature)\b",
            r"\bwithdraw (?:this|the) (?:policy|model|system|feature)\b",
            r"(?:停用|暂停).{0,20}(?:政策|模型|系统|功能)",
        ],
        "note": "Preserves recoverability when a policy or system change fails.",
        "recommendation": "Describe rollback, suspension, or deprecation conditions and authority.",
    },
    {
        "key": "independent_oversight",
        "label": "Independent oversight",
        "strong": [
            r"\bindependent (?:review|audit|oversight|ethics) (?:board|committee|panel|auditor)\b",
            r"\bindependent oversight\b.{0,120}\b(?:board|committee|panel|auditor)\b",
            r"\bexternal audit\b",
            r"\bexternal (?:review|reviewer|reviewers)\b",
            r"\b(?:board|trust|committee)\b.{0,120}\bexternal reviewers?\b",
            r"独立(?:审查|审计|监督|伦理委员会)",
            r"外部审计",
        ],
        "partial": [
            r"\boversight (?:board|committee|body|panel)\b",
            r"\bethics (?:board|committee|panel)\b",
            r"(?:监督|伦理).{0,12}(?:委员会|机构|小组)",
        ],
        "note": "Checks whether review is independent of the operating team.",
        "recommendation": "Specify who conducts independent review and how its findings are handled.",
    },
]

RISK_PATTERNS: list[tuple[str, str]] = [
    (
        r"\b(?:without|no) notice\b|不另行通知",
        "The document permits changes without notice.",
    ),
    (
        r"\bsole discretion\b|最终解释权|自行决定",
        "The document gives one party broad discretionary authority.",
    ),
    (
        r"\b(?:cannot|may not) (?:be )?(?:changed|amended|appealed)\b|不可(?:修改|修订|申诉)",
        "The text signals a hard lock or closed appeal path.",
    ),
]


def _sentence_units(text: str) -> list[str]:
    return [
        item.strip()
        for item in re.split(r"(?<=[。！？!?;；])\s*|\n+", text)
        if item.strip()
    ]


def _evidence(
    document: IngestedDocument, block_id: str, unit_index: int
) -> EvidenceSpan:
    block = next(item for item in document.blocks if item.block_id == block_id)
    units = _sentence_units(block.text)
    unit = units[min(unit_index, len(units) - 1)] if units else block.text
    excerpt = unit[:360] + ("…" if len(unit) > 360 else "")
    return EvidenceSpan(
        block_id=block.block_id,
        paragraph_index=block.paragraph_index,
        unit_index=unit_index,
        page_number=block.page_number,
        section=block.section,
        source_type=block.source_type,
        table_role=block.table_role,
        text=unit,
        excerpt=excerpt,
    )


def _matches(document: IngestedDocument, patterns: list[str]) -> list[EvidenceSpan]:
    evidence: list[EvidenceSpan] = []
    seen: set[tuple[str, int]] = set()
    for block in document.blocks:
        units = _sentence_units(block.text)
        for unit_index, unit in enumerate(units):
            if any(re.search(pattern, unit, re.IGNORECASE) for pattern in patterns):
                marker = (block.block_id, unit_index)
                if marker not in seen:
                    seen.add(marker)
                    evidence.append(_evidence(document, block.block_id, unit_index))
    return evidence


def _dedupe_evidence(items: list[EvidenceSpan]) -> list[EvidenceSpan]:
    deduped: list[EvidenceSpan] = []
    seen: set[tuple[str, int | None]] = set()
    for item in items:
        marker = (item.block_id, item.unit_index)
        if marker in seen:
            continue
        seen.add(marker)
        deduped.append(item)
    return deduped


def _has_unqualified_change_without_notice(text: str) -> bool:
    phrase = re.compile(
        r"\b(?:without|no) (?:advance )?notice\b|不另行通知",
        re.IGNORECASE,
    )
    safeguard = re.compile(
        r"\b(?:will|shall|may|can|does|do)\s+not\b.{0,100}"
        r"\bwithout (?:advance )?notice\b"
        r"|\b(?:never|not)\b.{0,100}\bwithout (?:advance )?notice\b",
        re.IGNORECASE | re.DOTALL,
    )
    return bool(phrase.search(text)) and not bool(safeguard.search(text))


def _has_closed_revision_path(text: str) -> bool:
    closed_path = re.compile(
        r"\b(?:cannot|may not|cannot ever) (?:be )?"
        r"(?:changed|amended|revised|appealed)\b|不可(?:修改|修订|申诉)",
        re.IGNORECASE,
    )
    exception = re.compile(
        r"\b(?:unless|except|subject to|following|after|with)\b|"
        r"(?:除非|经.+同意|按照.+程序)",
        re.IGNORECASE,
    )
    return bool(closed_path.search(text)) and not bool(exception.search(text))


def _risk_warnings(text: str) -> list[str]:
    warnings: list[str] = []
    for pattern, message in RISK_PATTERNS:
        if message == "The document permits changes without notice.":
            matched = _has_unqualified_change_without_notice(text)
        elif message == "The text signals a hard lock or closed appeal path.":
            matched = _has_closed_revision_path(text)
        else:
            matched = bool(re.search(pattern, text, re.IGNORECASE))
        if matched:
            warnings.append(message)
    return warnings


def audit_governance_document(document: IngestedDocument) -> GovernanceReport:
    checks: list[GovernanceCheck] = []
    recommendations: list[str] = []
    for definition in CHECK_DEFINITIONS:
        groups = definition.get("groups")
        if groups:
            group_evidence = [
                _matches(document, group_patterns) for group_patterns in groups
            ]
            covered_groups = sum(bool(items) for items in group_evidence)
            evidence = _dedupe_evidence(
                [item for items in group_evidence for item in items]
            )
            present_min_groups = int(definition.get("present_min_groups", len(groups)))
            status = (
                CheckStatus.PRESENT
                if covered_groups >= present_min_groups
                else CheckStatus.PARTIAL
                if covered_groups
                else CheckStatus.MISSING
            )
        else:
            strong_evidence = _matches(document, definition["strong"])
            evidence = strong_evidence or _matches(document, definition["partial"])
            status = (
                CheckStatus.PRESENT
                if strong_evidence
                else CheckStatus.PARTIAL
                if evidence
                else CheckStatus.MISSING
            )
        checks.append(
            GovernanceCheck(
                key=definition["key"],
                label=definition["label"],
                status=status,
                note=definition["note"],
                evidence=evidence[:8],
            )
        )
        if status != CheckStatus.PRESENT:
            recommendations.append(definition["recommendation"])

    warnings = list(
        dict.fromkeys(
            warning
            for block in document.blocks
            for warning in _risk_warnings(block.text)
        )
    )
    return GovernanceReport(
        generated_at=datetime.now(UTC),
        document=DocumentSummary(
            filename=document.filename,
            extension=document.extension,
            sha256=document.sha256,
            character_count=document.character_count,
            block_count=len(document.blocks),
            parse_warnings=document.warnings,
        ),
        summary=GovernanceSummary(
            check_count=len(checks),
            present_count=sum(check.status == CheckStatus.PRESENT for check in checks),
            partial_count=sum(check.status == CheckStatus.PARTIAL for check in checks),
            missing_count=sum(check.status == CheckStatus.MISSING for check in checks),
            document_warnings=list(dict.fromkeys(warnings)),
        ),
        checks=checks,
        recommendations=recommendations,
        disclaimer=GOVERNANCE_DISCLAIMER,
    )
