from __future__ import annotations

import hashlib

from esg_commitment_audit.api import audit_text
from esg_commitment_audit.extractor import extract_commitments
from esg_commitment_audit.ingest import ingest_bytes
from esg_commitment_audit.models import DocumentBlock, IngestedDocument


def test_extracts_structured_climate_commitment() -> None:
    text = (
        "公司承诺以2020年为基准年，到2030年将范围1和范围2碳排放减少50%，"
        "由可持续发展委员会负责并每年披露进展。"
    )
    report = audit_text(text)
    assert len(report.commitments) == 1
    item = report.commitments[0]
    assert item.category == "E"
    assert item.facts.baseline_year == 2020
    assert item.facts.target_year == 2030
    assert 50.0 in item.facts.target_percentages
    assert item.facts.scopes_covered
    assert item.facts.responsible_bodies


def test_does_not_treat_factual_description_as_commitment() -> None:
    document = ingest_bytes(
        b"The report describes historical carbon emissions in 2023.",
        "history.txt",
    )
    assert extract_commitments(document) == []


def test_does_not_treat_explicit_negation_as_commitment() -> None:
    document = ingest_bytes(
        b"The company does not commit to a carbon target.",
        "negative.txt",
    )
    assert extract_commitments(document) == []


def test_weak_language_is_preserved() -> None:
    document = ingest_bytes(
        "我们努力在未来条件允许时适当减少碳排放。".encode(),
        "weak.txt",
    )
    records = extract_commitments(document)
    assert len(records) == 1
    assert records[0].strength == "weak"


def test_duplicate_sentences_are_merged() -> None:
    text = "公司承诺到2030年减少碳排放50%。\n\n公司承诺到2030年减少碳排放50%。"
    report = audit_text(text)
    assert report.summary.commitment_count == 1


def test_progress_and_target_scope_notes_are_not_commitments() -> None:
    text = (
        "In line with our target, projects already divert 75% of construction "
        "waste.\n\nStrengthened our replenishment target to focus on total "
        "water withdrawals."
    )
    report = audit_text(text)
    assert report.summary.commitment_count == 0


def test_external_country_target_is_not_company_commitment() -> None:
    report = audit_text("中国2030年碳达峰目标\n\n中国2060年碳中和目标")
    assert report.summary.commitment_count == 0


def test_table_target_and_progress_labels_are_atomized() -> None:
    report = audit_text(
        "减量目标：2025年单位产量碳排放较2021年减少10%。目标进展：推进中。"
    )
    assert report.summary.commitment_count == 1
    assert "减量目标" in report.commitments[0].text
    assert "推进中" not in report.commitments[0].text


def test_candidate_key_is_stable_for_same_evidence() -> None:
    text = "公司承诺到2030年减少碳排放50%。"
    first = audit_text(text).commitments[0].candidate_key
    second = audit_text(text).commitments[0].candidate_key
    assert first == second
    assert first.startswith(hashlib.sha256(text.encode()).hexdigest()[:10] + "-p000-")


def test_progress_framing_and_third_party_goal_are_rejected() -> None:
    text = (
        "We’re approaching our goal to remove plastics by 2030. "
        "By joining in our goal to remove plastics by 2030, some vendors "
        "are taking action."
    )
    report = audit_text(text)
    assert report.summary.commitment_count == 0


def test_future_aim_with_quantity_is_accepted() -> None:
    report = audit_text(
        "By 2030, we aim for 25% of our devices’ product content to come "
        "from recycled materials."
    )
    assert report.summary.commitment_count == 1
    assert report.commitments[0].category == "E"


def test_spelled_out_percent_is_parsed_as_quantity() -> None:
    report = audit_text(
        "We are committed to reducing emissions by 75 percent by 2030 "
        "from a 2015 baseline."
    )
    assert report.summary.commitment_count == 1
    assert report.commitments[0].facts.target_percentages == [75.0]


def test_table_year_outcome_is_target_but_milestone_label_is_not() -> None:
    blocks = [
        DocumentBlock(
            block_id="b00001",
            text="中期（至2032年的科学碳目标）",
            paragraph_index=1,
            table_role="target",
            source_type="table",
        ),
        DocumentBlock(
            block_id="b00002",
            text="不晚于2050年实现碳中和",
            paragraph_index=2,
            table_role="target",
            source_type="table",
        ),
    ]
    document = IngestedDocument(
        filename="table.pdf",
        extension=".pdf",
        sha256="abc",
        character_count=sum(len(block.text) for block in blocks),
        blocks=blocks,
    )
    commitments = extract_commitments(document)
    assert len(commitments) == 1
    assert "2050" in commitments[0].text


def test_concrete_recurring_obligation_is_accepted() -> None:
    report = audit_text("公司每年至少举办一次供应商负责任矿产管理培训。")
    assert report.summary.commitment_count == 1
    assert report.commitments[0].category == "S"


def test_reworded_quantified_targets_are_deduplicated() -> None:
    text = (
        "By 2030, we aim for 25% of our devices’ content to come from "
        "recycled materials. "
        "25% of our devices’ content is expected to come from recycled "
        "materials by 2030."
    )
    report = audit_text(text)
    assert report.summary.commitment_count == 1


def test_same_percentage_without_target_years_is_not_deduplicated() -> None:
    blocks = [
        DocumentBlock(
            block_id=f"b{index:05d}",
            text=text,
            paragraph_index=index,
            table_role="target",
            source_type="table",
        )
        for index, text in enumerate(
            ("供应商行为准则签署率100%", "董事会独立董事比例不低于100%"),
            start=1,
        )
    ]
    document = IngestedDocument(
        filename="table.pdf",
        extension=".pdf",
        sha256="same-percent",
        character_count=sum(len(block.text) for block in blocks),
        blocks=blocks,
    )
    assert len(extract_commitments(document)) == 2
