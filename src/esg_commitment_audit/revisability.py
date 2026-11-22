from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass
from datetime import UTC, datetime

from .models import DocumentSummary, EvidenceSpan, IngestedDocument
from .revisability_models import (
    EvidenceGrade,
    ReviewProfile,
    RevisabilityCheck,
    RevisabilityDimension,
    RevisabilityReport,
    RevisabilitySummary,
)

PROFILE_LABELS: dict[ReviewProfile, str] = {
    "general": "General AI governance",
    "news_media": "News media",
    "advertising": "Advertising services",
    "insurance": "Insurance",
    "industrial_design": "Industrial design",
}

DIMENSION_LABELS: dict[str, str] = {
    "target": "Alignment target and hierarchy",
    "authority": "Authority and participation",
    "revision": "Revisionability",
    "version": "Version traceability",
    "rollback": "Reversibility and rollback",
    "affected": "Affected-party safeguards",
    "monitoring": "Monitoring and evidence integrity",
    "oversight": "Oversight, anti-abuse, and uncertainty",
    "technical": "Written technical-control evidence",
    "sector": "Sector-specific safeguards",
}

DISCLAIMER = (
    "This report reviews the written revisability architecture of AI policies, "
    "constitutions, model/system cards, and governance evidence. It does not "
    "prove alignment, safety, legal compliance, hidden intent, or actual model "
    "behaviour. Missing text is not proof that an internal practice is absent. "
    "Operational evidence and independent verification require separate artifacts."
)


@dataclass(frozen=True)
class RuleDefinition:
    key: str
    label: str
    dimension: str
    strong: tuple[str, ...]
    asserted: tuple[str, ...] = ()
    negative: tuple[str, ...] = ()
    required_artifacts: tuple[str, ...] = ()
    recommendation: str = ""


CORE_RULES: tuple[RuleDefinition, ...] = (
    RuleDefinition(
        key="alignment_target",
        label="Identifiable alignment target, constitution, or governing objective",
        dimension="target",
        strong=(
            r"\balignment target\b",
            r"\bconstitutional principles?\b",
            r"\bmodel objective\b",
            r"\bsystem objective\b",
            r"\bconstitution\b",
            r"对齐目标",
            r"宪法原则",
            r"目标函数",
        ),
        asserted=(
            r"\bresponsible ai\b",
            r"\bethical principles?\b",
            r"\bgoverning values?\b",
            r"负责任\s*ai",
            r"伦理原则",
            r"价值观",
        ),
        required_artifacts=(
            "The current alignment target, constitution, or governing objective",
            "The system or organisational scope to which it applies",
        ),
        recommendation=(
            "Name the governing alignment target or constitution and state its "
            "scope, owner, and version."
        ),
    ),
    RuleDefinition(
        key="normative_hierarchy",
        label="Explicit normative hierarchy or protected tier",
        dimension="target",
        strong=(
            r"\bred[ -]?line\b",
            r"\bnon[- ]negotiable\b",
            r"\bprecedence\b",
            r"\boverrides?\b",
            r"\btier(?:ed|s)?\b",
            r"红线",
            r"不可协商",
            r"优先于",
            r"层级",
        ),
        asserted=(
            r"\bprinciples?\b",
            r"\bvalues?\b",
            r"原则",
            r"价值",
        ),
        required_artifacts=(
            "Clause map showing redlines, principles, indicators, procedures, and operations",
            "Approved precedence or conflict rule",
        ),
        recommendation=(
            "Map redlines, principles, indicators, procedures, and operations "
            "into an explicit hierarchy with precedence rules."
        ),
    ),
    RuleDefinition(
        key="conflict_precedence",
        label="Conflict-resolution and adjudication route",
        dimension="target",
        strong=(
            r"\bconflict.{0,100}\b(?:resolve|precedence|escalat|adjudicat)",
            r"\bconflicts? of principles?\b",
            r"\bescalat(?:e|ion) to\b",
            r"冲突.{0,60}(?:解决|裁决|升级)",
            r"原则冲突",
        ),
        asserted=(r"\bconsistent with\b", r"相互协调", r"保持一致"),
        required_artifacts=(
            "Documented conflict matrix or precedence rule",
            "Named escalation or adjudication authority",
        ),
        recommendation=(
            "State which rule prevails when principles conflict and who resolves "
            "unresolved conflicts."
        ),
    ),
    RuleDefinition(
        key="accountable_owner",
        label="Accountable policy or constitutional owner",
        dimension="authority",
        strong=(
            r"\bpolicy owner\b",
            r"\balignment owner\b",
            r"\baccountable (?:executive|owner|body)\b",
            r"\bresponsible for (?:this|the) (?:policy|constitution|framework)\b",
            r"政策负责人",
            r"对齐负责人",
            r"责任主体",
        ),
        asserted=(r"\bgovernance team\b", r"\bai office\b", r"治理团队", r"ai办公室"),
        required_artifacts=("Named role or body accountable for the instrument",),
        recommendation="Name the accountable role and its authority over the instrument.",
    ),
    RuleDefinition(
        key="revision_authority",
        label="Revision authority and approval process",
        dimension="authority",
        strong=(
            r"\bamend(?:ment)? (?:authority|procedure)\b",
            r"\brevision (?:authority|procedure|process)\b",
            r"\bchange control\b",
            r"\brequires? (?:approval|authorisation|authorization) (?:by|from)\b",
            r"修订程序",
            r"变更审批",
            r"修订须经",
        ),
        asserted=(
            r"\bwe may (?:amend|revise|update)\b",
            r"\bthe company may (?:amend|revise|update)\b",
            r"可(?:修订|修改|更新)",
        ),
        negative=(
            r"\b(?:cannot|may not)\s+be\s+(?:amended|changed|revised)\b",
            r"不可(?:修改|修订|变更)",
        ),
        required_artifacts=(
            "Proposal, review, approval, and effective-date procedure",
            "Named approver or decision threshold",
        ),
        recommendation=(
            "Define who may propose and approve a change, the evidence required, "
            "and the effective-date rule."
        ),
    ),
    RuleDefinition(
        key="stakeholder_participation",
        label="Stakeholder consultation or public-comment route",
        dimension="authority",
        strong=(
            r"\bpublic consultation\b",
            r"\bpublic comment period\b",
            r"\bstakeholder consultation\b",
            r"\bmulti[- ]stakeholder\b",
            r"\baffected groups?.{0,80}\bconsult",
            r"公开征求意见",
            r"利益相关方参与",
            r"公众咨询",
        ),
        asserted=(r"\bstakeholders?\b", r"利益相关方"),
        required_artifacts=(
            "Consultation design and minimum notice period",
            "Record of participants, submissions, and unresolved dissent",
        ),
        recommendation=(
            "State who is consulted, for how long, how submissions are considered, "
            "and how dissent is recorded."
        ),
    ),
    RuleDefinition(
        key="review_cadence",
        label="Scheduled review or reconsideration",
        dimension="revision",
        strong=(
            r"\breview(?:ed)? (?:at least )?(?:every|annually|quarterly|semi-annually)\b",
            r"\bannual review\b",
            r"\bperiodic review\b",
            r"每年(?:审查|复核|评估)",
            r"定期(?:审查|复核|评估)",
        ),
        asserted=(
            r"\breview(?:ed)?\b.{0,80}\b(?:policy|rules|constitution)\b",
            r"\b(?:policy|rules|constitution)\b.{0,80}\breview(?:ed)?\b",
            r"复核",
            r"审查",
        ),
        required_artifacts=("Review schedule and responsible role",),
        recommendation="Specify a recurring review cadence and the role that initiates it.",
    ),
    RuleDefinition(
        key="revision_triggers",
        label="Defined revision triggers",
        dimension="revision",
        strong=(
            r"\brevis(?:e|ion).{0,100}\b(?:when|if|triggered by)\b",
            r"\btrigger(?:s|ed)? (?:a )?revis",
            r"\bmaterial (?:change|incident|error)\b.{0,100}\brevis",
            r"触发.{0,40}(?:修订|复审)",
            r"发生.{0,40}(?:重大变化|事件).{0,40}(?:修订|复审)",
        ),
        asserted=(r"\bwhen needed\b", r"\bas necessary\b", r"视情况", r"必要时"),
        required_artifacts=(
            "Named trigger events and thresholds",
            "Review owner and response deadline for each trigger",
        ),
        recommendation=(
            "List the events that force reconsideration, including model changes, "
            "incidents, new evidence, and legal changes."
        ),
    ),
    RuleDefinition(
        key="gradual_change",
        label="Gradual, staged, or reversible change design",
        dimension="revision",
        strong=(
            r"\bphased (?:rollout|implementation)\b",
            r"\bstaged (?:rollout|implementation)\b",
            r"\bpilot(?:ed| programme| program)?\b",
            r"\bcontrolled rollout\b",
            r"\bsandbox\b",
            r"分阶段",
            r"试点",
            r"沙盒",
        ),
        asserted=(r"\bgradual\b", r"渐进"),
        required_artifacts=(
            "Stage gates, success criteria, and stop conditions",
            "Comparison against the pre-change state",
        ),
        recommendation=(
            "Introduce high-impact changes in stages with explicit success, stop, "
            "and rollback criteria."
        ),
    ),
    RuleDefinition(
        key="version_identifier",
        label="Unique version identifier",
        dimension="version",
        strong=(
            r"\bversion (?:number|identifier|id)\b",
            r"\bsemantic version\b",
            r"\bv\d+(?:\.\d+){1,3}\b",
            r"版本号",
            r"版本标识",
        ),
        asserted=(r"\bversion\b", r"版本"),
        required_artifacts=("Current version identifier and effective date",),
        recommendation="Assign a unique, monotonic version identifier to every release.",
    ),
    RuleDefinition(
        key="change_log",
        label="Change log or revision history",
        dimension="version",
        strong=(
            r"\bchange ?log\b",
            r"\brevision history\b",
            r"\brelease notes?\b",
            r"\bchange record\b",
            r"变更日志",
            r"修订记录",
            r"版本历史",
        ),
        asserted=(r"\bhistory\b", r"历史"),
        required_artifacts=(
            "Dated change log with reason, proposer, approver, and affected clauses",
        ),
        recommendation=(
            "Publish a dated change log explaining what changed, why, who approved "
            "it, and which evidence was considered."
        ),
    ),
    RuleDefinition(
        key="prior_version_access",
        label="Prior-version retention and access",
        dimension="version",
        strong=(
            r"\bprevious versions? (?:remain|are|will be) (?:available|retained|archived)\b",
            r"\bpublic archive\b",
            r"\bhistorical versions?\b",
            r"\barchive of versions?\b",
            r"历史版本",
            r"旧版本.{0,40}(?:保存|可查|公开)",
        ),
        asserted=(r"\barchive\b", r"归档"),
        required_artifacts=(
            "Retention schedule and access rules for prior versions",
            "Evidence that rollback creates a new forward version rather than deleting history",
        ),
        recommendation=(
            "Retain prior versions with effective dates and make the relevant archive "
            "available to authorised reviewers."
        ),
    ),
    RuleDefinition(
        key="rollback_condition",
        label="Rollback or suspension triggers",
        dimension="rollback",
        strong=(
            r"\brollback (?:if|when|condition|trigger)\b",
            r"\btrigger(?:s|ed)? (?:a )?rollback\b",
            r"\bcircuit breaker\b",
            r"回滚条件",
            r"触发回滚",
        ),
        asserted=(r"\brollback\b", r"\brevert\b", r"回滚", r"恢复"),
        required_artifacts=(
            "Objective rollback thresholds and emergency conditions",
            "Decision deadline and post-rollback review",
        ),
        recommendation=(
            "Define measurable rollback triggers, the emergency route, and the "
            "post-rollback review."
        ),
    ),
    RuleDefinition(
        key="rollback_authority",
        label="Rollback decision authority",
        dimension="rollback",
        strong=(
            r"\brollback.{0,100}\b(?:approved|authorised|authorized) by\b",
            r"\b(?:incident commander|change control board).{0,100}\brollback\b",
            r"回滚.{0,50}(?:由|经).{0,30}(?:批准|授权)",
        ),
        required_artifacts=("Named rollback authority and escalation route",),
        recommendation="Name who can order an immediate rollback and who reviews it afterwards.",
    ),
    RuleDefinition(
        key="rollback_evidence",
        label="Rollback exercise and effectiveness evidence",
        dimension="rollback",
        strong=(
            r"\brollback (?:drill|exercise|test)\b",
            r"\btested rollback\b",
            r"\brestore test\b",
            r"回滚演练",
            r"恢复测试",
        ),
        asserted=(r"\brollback plan\b", r"回滚计划"),
        required_artifacts=(
            "Dated rollback exercise record, result, scope, and defects found",
            "Evidence that software, data, model, and external effects were handled",
        ),
        recommendation=(
            "Test rollback in realistic conditions and retain a dated record of the "
            "result, gaps, and corrective actions."
        ),
    ),
    RuleDefinition(
        key="protected_clauses",
        label="Protected redlines or heightened amendment threshold",
        dimension="rollback",
        strong=(
            r"\bsupermajority\b",
            r"\bentrenched clause\b",
            r"\bhigher (?:approval )?threshold\b",
            r"\bcannot be (?:rolled back|amended).{0,80}\b(?:except|unless)\b",
            r"特别多数",
            r"更高表决门槛",
            r"不可回滚",
        ),
        asserted=(r"\bprotected principle\b", r"核心原则"),
        required_artifacts=(
            "Register of protected clauses and justification",
            "Amendments, exception, and independent-review routes",
        ),
        recommendation=(
            "Identify protected clauses and explain why they require a higher "
            "amendment threshold rather than unexplained immutability."
        ),
    ),
    RuleDefinition(
        key="notice",
        label="Advance notice to affected people",
        dimension="affected",
        strong=(
            r"\badvance notice\b",
            r"\b\d+\s+days?\s+(?:of )?(?:advance )?notice\b",
            r"\bnotify.{0,80}\bbefore\b",
            r"提前通知",
            r"变更前.{0,30}通知",
        ),
        asserted=(r"\bnotify\b", r"\bnotice\b", r"通知", r"公告"),
        negative=(
            r"\b(?:may|can|will)\s+(?:change|amend|revise|terminate).{0,100}\bwithout (?:advance )?notice\b",
            r"可.{0,30}(?:变更|修改|终止).{0,30}不另行通知",
        ),
        required_artifacts=("Minimum notice period and publication channel",),
        recommendation="Commit to a minimum notice period before material changes take effect.",
    ),
    RuleDefinition(
        key="explanation",
        label="Explanation of material changes",
        dimension="affected",
        strong=(
            r"\breason for (?:the )?change\b",
            r"\bexplain(?:s|ed|ation)?.{0,80}\bchange\b",
            r"\bplain[- ]language summary\b",
            r"\bimpact assessment\b",
            r"变更理由",
            r"影响评估",
            r"变更说明",
        ),
        asserted=(r"\btransparent\b", r"公开说明"),
        required_artifacts=("Change rationale and affected-party impact explanation",),
        recommendation=(
            "Explain the reason, practical effect, evidence, and unresolved uncertainty "
            "of material changes."
        ),
    ),
    RuleDefinition(
        key="appeal",
        label="Appeal, complaint, or human-review route",
        dimension="affected",
        strong=(
            r"\bappeal\b",
            r"\brequest (?:a )?human review\b",
            r"\bgrievance\b",
            r"\bcomplaint procedure\b",
            r"申诉",
            r"人工复核",
            r"投诉程序",
        ),
        asserted=(r"\bcomplaint\b", r"\breview request\b", r"投诉", r"复核申请"),
        negative=(
            r"\bno (?:right to|route for) appeal\b",
            r"\bcannot (?:be )?appealed\b",
            r"不得申诉",
        ),
        required_artifacts=(
            "Eligibility, response deadline, reviewer independence, and remedies",
        ),
        recommendation=(
            "Provide an appeal or human-review route with a deadline, independent "
            "reviewer, and remedy."
        ),
    ),
    RuleDefinition(
        key="refusal_exit",
        label="Refusal, opt-out, or exit route",
        dimension="affected",
        strong=(
            r"\bopt[- ]out\b",
            r"\bwithdraw consent\b",
            r"\bdiscontinue use\b",
            r"\bexit the service\b",
            r"退出",
            r"撤回同意",
            r"选择不使用",
        ),
        asserted=(
            r"\bstop using\b",
            r"\bclose (?:your )?account\b",
            r"停止使用",
            r"注销账户",
        ),
        negative=(r"\bno (?:option|right) to exit\b", r"不得退出"),
        required_artifacts=(
            "Exit process, consequences, data portability, and deadline",
        ),
        recommendation=(
            "Explain how an affected person can decline, opt out, or exit, including "
            "consequences and data handling."
        ),
    ),
    RuleDefinition(
        key="monitoring_metrics",
        label="Monitoring metrics, thresholds, and escalation",
        dimension="monitoring",
        strong=(
            r"\bmonitoring (?:metrics?|indicators?|thresholds?)\b",
            r"\bdrift (?:metric|threshold|monitoring)\b",
            r"\bescalat(?:e|ion).{0,80}\bthreshold\b",
            r"监测指标",
            r"预警阈值",
            r"异常升级",
        ),
        asserted=(r"\bmonitor(?:ing|ed)?\b", r"监控", r"监测"),
        required_artifacts=(
            "Metric definitions, thresholds, review cadence, and escalation owner",
        ),
        recommendation=(
            "State what is measured, the warning thresholds, who reviews exceptions, "
            "and what action follows."
        ),
    ),
    RuleDefinition(
        key="audit_logs",
        label="Audit logs or audit trail",
        dimension="monitoring",
        strong=(
            r"\baudit logs?\b",
            r"\baudit trails?\b",
            r"\bappend[- ]only\b",
            r"\btamper[- ]evident\b",
            r"审计日志",
            r"审计追踪",
        ),
        asserted=(r"\baudit(?:ing)?\b", r"审计"),
        required_artifacts=(
            "What is logged, who can inspect it, retention period, and integrity control",
        ),
        recommendation=(
            "Define the audit-log content, access rights, retention period, and "
            "tamper-evidence mechanism."
        ),
    ),
    RuleDefinition(
        key="retention",
        label="Evidence retention and legal-hold rules",
        dimension="monitoring",
        strong=(
            r"\bretain(?:ed|tion)? (?:for|of) \d+\s+(?:days|months|years)\b",
            r"\bretention (?:period|schedule|policy)\b",
            r"\blegal hold\b",
            r"保存.{0,30}(?:年|月|日)",
            r"留存期限",
        ),
        asserted=(r"\bretain(?:ed)?\b", r"\bretention\b", r"保存", r"留存"),
        required_artifacts=(
            "Retention schedule, deletion rule, and legal-hold procedure",
        ),
        recommendation=(
            "Specify retention periods, deletion rules, and how evidence is preserved "
            "during a dispute."
        ),
    ),
    RuleDefinition(
        key="independent_oversight",
        label="Independent review or oversight",
        dimension="oversight",
        strong=(
            r"\bindependent (?:review|audit|oversight|ethics) (?:board|committee|panel|auditor)\b",
            r"\bexternal (?:review|reviewer|auditor|audit)\b",
            r"\bthird[- ]party assessment\b",
            r"独立(?:审查|审计|监督|伦理委员会)",
            r"外部审计",
        ),
        asserted=(
            r"\boversight (?:board|committee|panel)\b",
            r"监督委员会",
            r"伦理委员会",
        ),
        required_artifacts=(
            "Reviewer identity, independence rule, terms of reference, and reporting line",
        ),
        recommendation=(
            "Name the independent reviewer and explain its authority, access, conflict "
            "controls, and how findings are handled."
        ),
    ),
    RuleDefinition(
        key="anti_abuse",
        label="Anti-abuse controls for revision and rollback",
        dimension="oversight",
        strong=(
            r"\bcooling[- ]off period\b",
            r"\bconflict[- ]of[- ]interest check\b",
            r"\banti[- ]retaliation\b",
            r"\bselective rollback\b",
            r"冷却期",
            r"利益冲突审查",
            r"防止报复",
            r"选择性回滚",
        ),
        asserted=(r"\bprevent abuse\b", r"防止滥用"),
        required_artifacts=(
            "Anti-oscillation, conflict-check, completeness, and independent-review controls",
        ),
        recommendation=(
            "Add controls against political oscillation, obstructive rollback, selective "
            "rollback, conflicts of interest, and retaliation."
        ),
    ),
    RuleDefinition(
        key="uncertainty",
        label="Uncertainty and error acknowledgment",
        dimension="oversight",
        strong=(
            r"\bdeep uncertainty\b",
            r"\bepistemic (?:humility|uncertainty)\b",
            r"\bconfidence (?:level|threshold|interval)\b",
            r"\bwe may be wrong\b",
            r"深不确定",
            r"认识论谦逊",
            r"置信区间",
            r"可能错误",
        ),
        asserted=(r"\buncertainty\b", r"\bunknowns?\b", r"不确定性", r"未知"),
        required_artifacts=(
            "Uncertainty method, threshold, review route, and reconsideration trigger",
        ),
        recommendation=(
            "State how uncertainty is assessed, what threshold triggers review, and "
            "how the organisation can correct an erroneous target."
        ),
    ),
    RuleDefinition(
        key="capability_gate",
        label="Capability or deployment gate",
        dimension="technical",
        strong=(
            r"\bcapability gate\b",
            r"\brelease gate\b",
            r"\bdeployment approval\b",
            r"\bpre[- ]deployment evaluation\b",
            r"能力门控",
            r"发布门",
            r"部署前评估",
        ),
        asserted=(r"\bpre[- ]deployment\b", r"部署前"),
        required_artifacts=(
            "Gate criteria, approver, evidence package, stop condition, and release record",
        ),
        recommendation=(
            "Define the capability gate, who may approve release, what evidence is "
            "required, and what conditions stop deployment."
        ),
    ),
    RuleDefinition(
        key="interruptibility",
        label="Interruption, shutdown, or kill-switch control",
        dimension="technical",
        strong=(
            r"\bkill switch\b",
            r"\binterrupt(?:ibility| signal|ion)\b",
            r"\bemergency shutdown\b",
            r"\baccept(?:s|ing)? (?:an )?(?:interrupt|shutdown)\b",
            r"紧急停止",
            r"中断信号",
            r"关闭开关",
        ),
        asserted=(r"\bshut ?down\b", r"关闭"),
        required_artifacts=(
            "Controlled interruption test, response time, state preservation, and override authority",
        ),
        recommendation=(
            "Define an external interruption route, test it, and specify what state is "
            "preserved or restored."
        ),
    ),
)


SECTOR_RULES: dict[ReviewProfile, tuple[RuleDefinition, ...]] = {
    "general": (),
    "news_media": (
        RuleDefinition(
            key="content_provenance",
            label="AI content provenance and disclosure",
            dimension="sector",
            strong=(
                r"\bsynthetic (?:media|content)\b",
                r"\bcontent provenance\b",
                r"\bai[- ]generated (?:content|media).{0,100}\b(?:label|disclos)",
                r"合成媒体",
                r"内容来源",
                r"ai生成内容.{0,50}(?:标识|披露)",
            ),
            asserted=(r"\bai[- ]generated\b", r"生成式\s*ai"),
            required_artifacts=(
                "Labeling standard, provenance method, and editorial responsibility",
            ),
            recommendation=(
                "Define when synthetic content is labeled, how provenance is preserved, "
                "and who approves publication."
            ),
        ),
        RuleDefinition(
            key="editorial_correction",
            label="Correction and retraction route for AI-assisted output",
            dimension="sector",
            strong=(
                r"\bcorrection(?:s)? (?:policy|procedure|route)\b",
                r"\bretractions? (?:policy|procedure)\b",
                r"\beditor'?s note\b",
                r"更正程序",
                r"撤稿程序",
            ),
            asserted=(r"\bcorrection\b", r"\bretraction\b", r"更正", r"撤稿"),
            required_artifacts=(
                "Correction trigger, reviewer, publication rule, and archive record",
            ),
            recommendation=(
                "Specify how errors in AI-assisted content are corrected or retracted and "
                "how the correction is retained."
            ),
        ),
    ),
    "advertising": (
        RuleDefinition(
            key="client_disclosure",
            label="Client disclosure and approval for AI use",
            dimension="sector",
            strong=(
                r"\bclient (?:approval|authorisation|authorization|disclosure)\b",
                r"\bdisclos(?:e|ure).{0,80}\bclient\b",
                r"客户.{0,30}(?:批准|授权|披露)",
            ),
            asserted=(r"\bclient\b", r"客户"),
            required_artifacts=(
                "Contract term, disclosure rule, approval record, and exception route",
            ),
            recommendation=(
                "State what AI use must be disclosed to or approved by the client, and "
                "record that approval."
            ),
        ),
        RuleDefinition(
            key="rights_clearance",
            label="Rights, consent, and usage-evidence control",
            dimension="sector",
            strong=(
                r"\brights clearance\b",
                r"\btalent consent\b",
                r"\bcopyright (?:check|record|clearance)\b",
                r"\blicen[cs]e record\b",
                r"版权审核",
                r"肖像授权",
                r"使用许可记录",
            ),
            asserted=(r"\bcopyright\b", r"\bconsent\b", r"版权", r"授权"),
            required_artifacts=(
                "Rights source, consent, usage scope, expiry, and evidence record",
            ),
            recommendation=(
                "Record the rights and consent basis for AI-assisted creative inputs and "
                "outputs, including restrictions and expiry."
            ),
        ),
    ),
    "insurance": (
        RuleDefinition(
            key="adverse_action_explanation",
            label="Adverse-action explanation route",
            dimension="sector",
            strong=(
                r"\badverse action (?:notice|reason|explanation)\b",
                r"\breason for (?:the )?(?:decision|denial)\b",
                r"不利决定说明",
                r"拒赔.{0,30}理由",
            ),
            asserted=(r"\bexplain(?:ation)?.{0,60}\bdecision\b", r"解释.{0,40}决定"),
            required_artifacts=(
                "Decision explanation, affected person, timing, and evidence basis",
            ),
            recommendation=(
                "State how a person is given a meaningful explanation of a materially "
                "adverse AI-assisted decision."
            ),
        ),
        RuleDefinition(
            key="insurance_human_review",
            label="Independent human review for contested decisions",
            dimension="sector",
            strong=(
                r"\bhuman (?:review|decision).{0,100}\b(?:contest|appeal|complaint)\b",
                r"\bqualified reviewer.{0,100}\b(?:denial|claim|underwriting)\b",
                r"人工复核.{0,60}(?:申诉|理赔|核保)",
            ),
            asserted=(r"\bhuman review\b", r"人工复核"),
            required_artifacts=(
                "Reviewer qualification, independence, deadline, and remedy",
            ),
            recommendation=(
                "Provide a qualified, independent human-review route for contested "
                "AI-assisted decisions."
            ),
        ),
    ),
    "industrial_design": (
        RuleDefinition(
            key="design_provenance",
            label="Design artifact provenance and version control",
            dimension="sector",
            strong=(
                r"\bdesign (?:file|artifact).{0,100}\b(?:hash|version|provenance)\b",
                r"\bplm\b",
                r"\bcad\b.{0,80}\bversion\b",
                r"设计文件.{0,50}(?:哈希|版本|来源)",
            ),
            asserted=(r"\bdesign file\b", r"设计文件"),
            required_artifacts=(
                "Artifact hash, source, tool/model version, and approved revision",
            ),
            recommendation=(
                "Record the source, tool or model version, hash, and approval status of "
                "material design artifacts."
            ),
        ),
        RuleDefinition(
            key="design_freeze",
            label="Design-freeze, release, and rollback control",
            dimension="sector",
            strong=(
                r"\bdesign freeze\b",
                r"\bconcept freeze\b",
                r"\bdesign release\b",
                r"设计冻结",
                r"设计发布",
            ),
            asserted=(r"\bfreeze\b", r"\breleased design\b", r"冻结"),
            required_artifacts=(
                "Freeze authority, release criteria, change exception, and prior approved state",
            ),
            recommendation=(
                "Define who can freeze or release a design, what evidence is required, and "
                "how to return to the prior approved state."
            ),
        ),
    ),
}


RISK_PATTERNS: tuple[tuple[str, str], ...] = (
    (
        (
            r"\b(?:may|can|will)\s+(?:change|amend|revise|terminate)"
            r".{0,100}\bwithout (?:advance )?notice\b"
            r"|可.{0,30}(?:变更|修改|终止).{0,30}不另行通知"
        ),
        "The document appears to permit material changes without notice.",
    ),
    (
        r"\bsole discretion\b|最终解释权|自行决定",
        "The document gives one party broad discretionary authority.",
    ),
    (
        r"\b(?:cannot|may not)\s+be\s+(?:amended|changed|revised)\b|不可(?:修改|修订|变更)",
        "The document contains a hard lock; determine whether it is a justified redline or unexplained immutability.",
    ),
    (
        r"\bno (?:right to|route for) appeal\b|不得申诉",
        "The document appears to close the appeal route.",
    ),
)


def _sentence_units(text: str) -> list[str]:
    return [
        item.strip()
        for item in re.split(r"(?<=[。！？!?;；])\s*|\n+", text)
        if item.strip()
    ]


def _evidence(
    document: IngestedDocument,
    block_id: str,
    unit_index: int,
) -> EvidenceSpan:
    block = next(item for item in document.blocks if item.block_id == block_id)
    units = _sentence_units(block.text)
    unit = units[min(unit_index, len(units) - 1)] if units else block.text
    excerpt = unit[:420] + ("…" if len(unit) > 420 else "")
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


def _matches(
    document: IngestedDocument, patterns: tuple[str, ...]
) -> list[EvidenceSpan]:
    evidence: list[EvidenceSpan] = []
    seen: set[tuple[str, int]] = set()
    for block in document.blocks:
        for unit_index, unit in enumerate(_sentence_units(block.text)):
            if any(re.search(pattern, unit, re.IGNORECASE) for pattern in patterns):
                marker = (block.block_id, unit_index)
                if marker not in seen:
                    seen.add(marker)
                    evidence.append(_evidence(document, block.block_id, unit_index))
    return evidence


def _dedupe_evidence(items: list[EvidenceSpan]) -> list[EvidenceSpan]:
    result: list[EvidenceSpan] = []
    seen: set[tuple[str, int | None]] = set()
    for item in items:
        marker = (item.block_id, item.unit_index)
        if marker not in seen:
            seen.add(marker)
            result.append(item)
    return result


def _evaluate_rule(
    document: IngestedDocument,
    rule: RuleDefinition,
) -> RevisabilityCheck:
    negative = _matches(document, rule.negative) if rule.negative else []
    if negative:
        return RevisabilityCheck(
            key=rule.key,
            label=rule.label,
            grade=EvidenceGrade.CONTRADICTED,
            rationale=(
                "The text contains a conflicting hard restriction or explicitly closed "
                "route. Human review is required to distinguish a justified redline from "
                "unexplained lock-in."
            ),
            evidence=negative[:8],
            required_artifacts=list(rule.required_artifacts),
            recommendation=rule.recommendation,
        )

    strong = _matches(document, rule.strong)
    if strong:
        return RevisabilityCheck(
            key=rule.key,
            label=rule.label,
            grade=EvidenceGrade.DOCUMENTED,
            rationale=(
                "The examined text contains a specific written control. This is E2 "
                "evidence only; it does not prove that the control operated."
            ),
            evidence=strong[:8],
            required_artifacts=list(rule.required_artifacts),
            recommendation=rule.recommendation,
        )

    asserted = _matches(document, rule.asserted)
    if asserted:
        return RevisabilityCheck(
            key=rule.key,
            label=rule.label,
            grade=EvidenceGrade.ASSERTED,
            rationale=(
                "The text contains a general assertion or aspiration without enough "
                "detail to establish a specific written control."
            ),
            evidence=_dedupe_evidence(asserted)[:8],
            required_artifacts=list(rule.required_artifacts),
            recommendation=rule.recommendation,
        )

    return RevisabilityCheck(
        key=rule.key,
        label=rule.label,
        grade=EvidenceGrade.ABSENT,
        rationale="The examined text did not support this control.",
        evidence=[],
        required_artifacts=list(rule.required_artifacts),
        recommendation=rule.recommendation,
    )


def _risk_warnings(document: IngestedDocument) -> list[str]:
    warnings: list[str] = []
    for pattern, message in RISK_PATTERNS:
        if any(
            re.search(pattern, block.text, re.IGNORECASE) for block in document.blocks
        ):
            warnings.append(message)
    return list(dict.fromkeys(warnings))


def audit_revisability_document(
    document: IngestedDocument,
    profile: ReviewProfile = "general",
) -> RevisabilityReport:
    if profile not in PROFILE_LABELS:
        raise ValueError(f"Unknown review profile: {profile}")

    rules = CORE_RULES + SECTOR_RULES[profile]
    checks = [_evaluate_rule(document, rule) for rule in rules]
    dimensions: list[RevisabilityDimension] = []
    for key, label in DIMENSION_LABELS.items():
        dimension_checks = [
            check for check, rule in zip(checks, rules) if rule.dimension == key
        ]
        if dimension_checks:
            dimensions.append(
                RevisabilityDimension(
                    key=key,
                    label=label,
                    checks=dimension_checks,
                )
            )

    counts = Counter(check.grade for check in checks)
    recommendations = list(
        dict.fromkeys(
            check.recommendation
            for check in checks
            if check.recommendation
            and check.grade
            in {
                EvidenceGrade.ABSENT,
                EvidenceGrade.ASSERTED,
                EvidenceGrade.CONTRADICTED,
            }
        )
    )
    evidence_requests = list(
        dict.fromkeys(
            artifact
            for check in checks
            if check.grade
            in {
                EvidenceGrade.ASSERTED,
                EvidenceGrade.DOCUMENTED,
                EvidenceGrade.CONTRADICTED,
            }
            for artifact in check.required_artifacts
        )
    )

    return RevisabilityReport(
        generated_at=datetime.now(UTC),
        profile=profile,
        profile_label=PROFILE_LABELS[profile],
        document=DocumentSummary(
            filename=document.filename,
            extension=document.extension,
            sha256=document.sha256,
            character_count=document.character_count,
            block_count=len(document.blocks),
            parse_warnings=document.warnings,
        ),
        summary=RevisabilitySummary(
            dimension_count=len(dimensions),
            check_count=len(checks),
            absent_count=counts[EvidenceGrade.ABSENT],
            asserted_count=counts[EvidenceGrade.ASSERTED],
            documented_count=counts[EvidenceGrade.DOCUMENTED],
            operationally_evidenced_count=counts[EvidenceGrade.OPERATIONALLY_EVIDENCED],
            independently_verified_count=counts[EvidenceGrade.INDEPENDENTLY_VERIFIED],
            contradicted_count=counts[EvidenceGrade.CONTRADICTED],
            not_assessable_count=counts[EvidenceGrade.NOT_ASSESSABLE],
        ),
        dimensions=dimensions,
        warnings=_risk_warnings(document),
        recommendations=recommendations,
        evidence_requests=evidence_requests,
        disclaimer=DISCLAIMER,
    )
