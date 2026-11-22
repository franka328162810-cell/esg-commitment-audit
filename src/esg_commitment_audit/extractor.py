from __future__ import annotations

import hashlib
import re
from collections.abc import Iterable
from difflib import SequenceMatcher
from functools import lru_cache

from .models import (
    CommitmentFacts,
    CommitmentRecord,
    DocumentBlock,
    EvidenceSpan,
    IngestedDocument,
)
from .rules import load_rule_pack

YEAR_RE = re.compile(r"(?<!\d)((?:19|20)\d{2}|2100)(?!\d)")
PERCENT_RE = re.compile(
    r"(?<![\d.])(\d{1,3}(?:\.\d+)?)\s*(?:%|％|percent\b)",
    re.IGNORECASE,
)
QUANTITY_RE = re.compile(
    r"(?<![\d.])(\d+(?:\.\d+)?)\s*"
    r"(?:%|％|tco2e|tco₂e|吨二氧化碳当量|万吨|万度|mwh|gwh|吨|立方米|m³|"
    r"litres?|升|mg/l|mg/m3|mw|kw)",
    re.IGNORECASE,
)
SENTENCE_SPLIT_RE = re.compile(
    r"(?<=[。！？!?；;])\s*|"
    r"(?<=\.)(?:\d{1,3}|\s*[†‡*])?\s+(?=[A-Z0-9])|\n+"
)
BULLET_SPLIT_RE = re.compile(r"[\uf0a7\uf0b7■•▪◦●◆◇]")
TABLE_SECTION_SPLIT_RE = re.compile(
    r"(?=(?:减量目标|目标进展|污染防治设施|处理方式|管理制度|废物类型|"
    r"主要污染物|目标及承诺|进展\s*[：:]))"
)
NON_COMMITMENT_RE = re.compile(
    r"(?:does\s+not\s+commit|not\s+committed|no\s+commitment|"
    r"\b(?:may|might|could)\s+(?:face|be|have|include|vary|depend)|"
    r"\b(?:may|might|could)\s+(?:also\s+)?(?:reduce|lower|increase|avoid|enable)\b|"
    r"\bwill\s+require\b|\baims?\s+to\s+determine\b|"
    r"\bcommitted\s+to\s+taking\s+actions\s+that\s+support\s+this\s+goal\b|"
    r"\bplan\s+to\s+join\b|\bprogram[^.]{0,40}\bprovides\b|"
    r"\bbecame\s+an\s+assessment\s+requirement\b|"
    r"\bcommitted\s+to\s+amplifying\s+the\s+reach\b|"
    r"\bearly\s+investigations?\b|\bwe\s+believe\b|\bcan\s+reduce\b|"
    r"\bby\s+joining\s+in\s+our\s+goal\b|\bsome\s+vendors?\b|"
    r"\brather\s+than\s+rounding\s+down\b|"
    r"\bremain\s+committed\s+to\s+reporting\b|"
    r"\bis\s+essential\s+to\s+meeting\b[^.]{0,80}\bgoal\b|"
    r"\b(?:suppliers?|manufacturers?|vendors?)\s+have\s+committed\b|"
    r"\bcontinued\s+to\b|"
    r"不承诺|未承诺|不会承诺|没有承诺|可能面临|可能受到)",
    re.IGNORECASE,
)
FUTURE_HARD_RE = re.compile(
    r"\b(?:commits?|committed|pledges?|will|shall|"
    r"aim(?:s|ing)?\s+(?:to|for)|working\s+to|"
    r"plans?\s+to|intends?\s+to)\b|(?:承诺|将在|将于|致力于|"
    r"计划(?:在|到|于|将|实现)|"
    r"将(?:会|在|于|确保|推进|要求|持续|实现|完成|达到|到))",
    re.IGNORECASE,
)
ONGOING_RE = re.compile(
    r"\b(?:continue|continues|continuing|will continue)\b|"
    r"(?:持续推动|持续推进|持续完善|持续改进|不断优化|逐步推广)",
    re.IGNORECASE,
)
HISTORICAL_RE = re.compile(
    r"\b(?:in fy\d{2}|in fiscal year \d{4}|in 20\d{2}|reporting period|"
    r"continued to|achieved|reached|completed|"
    r"obtained certification|was|were|has|have|had)\b|"
    r"(?:报告期内|截至报告期末|同比|已达成|已完成|取得|实现了|达到了|下降了|"
    r"提升了)",
    re.IGNORECASE,
)
COMPLETED_ACTION_RE = re.compile(
    r"\b(?:achieved|reached|completed|diverted|expanded|funded|launched|"
    r"installed|contributed|harvested|published|obtained)\b|"
    r"(?:已达成|已完成|报告期内|制定并公开发布|完成新建)",
    re.IGNORECASE,
)
METHOD_RE = re.compile(
    r"\b(?:focuses? on|we advance this work by|we do this by|through|"
    r"by prioritizing|based on|in line with|establishes?|established?)\b|"
    r"(?:基于|通过|依据|按照|建立|建成|编制|修订|覆盖|纳入|实施)",
    re.IGNORECASE,
)
GOVERNANCE_RE = re.compile(
    r"\b(?:committee|board|oversight|responsible for|governance|management "
    r"architecture)\b|(?:董事会|委员会|负责(?!任)|监督|治理体系|管理架构)",
    re.IGNORECASE,
)
SCENARIO_RE = re.compile(
    r"\b(?:scenario|scenarios|nze 2050|rcp\s*\d|ssp\s*\d)\b|"
    r"(?:情景|情景分析|代表性浓度路径)",
    re.IGNORECASE,
)
TARGET_REFERENCE_RE = re.compile(
    r"(?:\b(?:targets?|commitments?|goals?)\b|"
    r"目标|承诺|减量目标|管理目标|碳中和目标|减排目标)"
    r"[^。；;.!?]{0,65}"
    r"(?:\d{1,3}(?:\.\d+)?\s*[%％]|(?:19|20)\d{2})|"
    r"(?:\d{1,3}(?:\.\d+)?\s*[%％]|(?:19|20)\d{2})"
    r"[^。；;.!?]{0,65}(?:\b(?:targets?|commitments?|goals?)\b|目标|承诺)",
    re.IGNORECASE,
)
TARGET_YEAR_CONTEXT_RE = re.compile(
    r"\b(?:by|before|from|starting|no later than)\s+"
    r"(?:the\s+)?(?:end\s+of\s+)?(?:fiscal\s+year\s+|calendar\s+year\s+)?"
    r"(?:19|20)\d{2}\b|"
    r"(?:到|于|在)\s*(?:20\d{2})\s*年?|"
    r"(?:20\d{2})\s*年?(?:前|实现|达到|完成|目标)",
    re.IGNORECASE,
)
PERCENT_TARGET_ADJACENT_RE = re.compile(
    r"\d{1,3}(?:\.\d+)?\s*[%％]\s*(?:target|goal|目标)",
    re.IGNORECASE,
)
TARGET_LIST_RE = re.compile(
    r"\b(?:targets?|goals?|commitments?)\b"
    r"[^。；;.!?]{0,140}"
    r"\b(?:eliminate|design|use|reduce|achieve|maintain|source)\b",
    re.IGNORECASE,
)
WEAK_RE = re.compile(
    r"\b(?:aspire|endeavor|strive|hope|seek|may|might|could)\b|"
    r"(?:努力|希望|争取|力求|力争|尽可能)",
    re.IGNORECASE,
)
BINDING_REQUIREMENT_RE = re.compile(
    r"\b(?:require|requires|required)\b[^。；;.!?]{0,70}"
    r"\b(?:target|commitment|reduction)\b|"
    r"(?:要求|需要)[^。；;.!?]{0,70}(?:目标|承诺|减量)",
    re.IGNORECASE,
)
CITATION_RE = re.compile(
    r"https?://|www\.|doi:|see\s+(?:page|appendix)|\breferences?\b|"
    r"资料来源|数据来源|参见|附录",
    re.IGNORECASE,
)
PROGRESS_START_RE = re.compile(
    r"^(?:in\s+(?:fy)?\d{2,4}|as\s+of\b|\d{4}\s+progress|"
    r"截至|报告期内|202\d\s*年|20\d{2}\s*年|"
    r"achieved\b|reached\b|completed\b|reduced\b|increased\b|expanded\b|"
    r"strengthened\b|supported\b|signed\b|joined\b|allocated\b|"
    r"we(?:['’]re|\s+are)\s+(?:approaching|nearing|on\s+track)\b|"
    r"approaching\b|nearing\b|on\s+track\b|"
    r"已完成|已达成|实现了|下降了|提升了|已达到|达到)",
    re.IGNORECASE,
)
EXTERNAL_TARGET_RE = re.compile(
    r"^(?:中国|国家|政府|欧盟|美国|全球|联合国|"
    r"china|the\s+government|governments?|eu|united\s+nations|global)"
    r"[^。；;.!?]{0,60}(?:目标|target|goal)",
    re.IGNORECASE,
)
PAGE_NAV_RE = re.compile(
    r"(?:about\s+this\s+report|contents|introduction|appendix|later sections|"
    r"关于本报告|董事长寄语|走进|附录)",
    re.IGNORECASE,
)
RUNNING_HEADER_RE = re.compile(
    r"^(?:endnotes?\s+\d+|overview\s+appendix|appendix\s+\d+|"
    r"contents\s+introduction|关于本报告)",
    re.IGNORECASE,
)
ADVOCACY_RE = re.compile(
    r"^(?:encourage|urge|called?\s+on|advocate|support\s+polic(?:y|ies)|"
    r"鼓励|呼吁|倡导政府|支持政策)",
    re.IGNORECASE,
)
GOAL_OUTCOME_RE = re.compile(
    r"replenish|remove\s+plastics?|recycled|renewable materials?|"
    r"eliminate waste|zero[\s-]+waste|waste\s+diversion|waste\s+prevention|"
    r"carbon[\s-]+neutral|clean electricity|"
    r"renewable electricity|source\s+100\s*%|single-use\s+plastics?|"
    r"recyclable\s+packaging|"
    r"water reuse|net[\s-]+zero|减排|碳中和|零废弃|回用|再生材料|清洁能源",
    re.IGNORECASE,
)
CONCRETE_FUTURE_ACTION_RE = re.compile(
    r"\b(?:complete|require|increase|report|disclose|publish|source|train|"
    r"conduct|certify|ensure|improve|reduce|cut|transition|achieve)\b|"
    r"(?:完成|要求|提高|报告|披露|发布|采购|培训|开展|认证|确保|改善|减少|降低|"
    r"转型|实现|达到|恢复|保护|设定|建立)",
    re.IGNORECASE,
)
RECURRING_ACTION_RE = re.compile(
    r"\b(?:audit|review|assess|train|survey|interview|inspect|disclose|report|"
    r"publish|monitor|certify|sign|evaluate|communicate)\b|"
    r"(?:审核|评价|评估|培训|调研|访谈|检查|审计|披露|报告|发布|监测|认证|签署|"
    r"签订|沟通|回顾|更新|评选|召开|组织|检查)",
    re.IGNORECASE,
)
IMPERATIVE_GOAL_RE = re.compile(
    r"^(?:replenish|remove|eliminate|certify|increase|transition|achieve|"
    r"become|protect|source|reduce|maintain|zero[\s-]+waste)\b|"
    r"^(?:补充|消除|认证|提高|实现|成为|保护|采购|减少|维持|零废弃)",
    re.IGNORECASE,
)

CATEGORY_BOOSTS: dict[str, tuple[str, ...]] = {
    "E1": (
        "carbon negative",
        "carbon neutral",
        "net zero",
        "greenhouse gas",
        "scope 1",
        "scope 2",
        "scope 3",
        "emissions",
        "volatile organic compounds",
        "vocs",
        "碳中和",
        "净零",
        "碳排放",
        "温室气体",
        "nox",
        "氮氧化物",
        "有机废气",
        "废气",
        "environmental audit",
        "environmental compliance",
        "环境审计",
        "环境合规",
    ),
    "E2": (
        "renewable electricity",
        "renewable energy",
        "clean energy",
        "green power",
        "可再生能源",
        "清洁能源",
        "绿电",
        "节能",
        "能耗",
    ),
    "E3": (
        "water positive",
        "water use",
        "water withdrawal",
        "freshwater withdrawal",
        "freshwater",
        "water usage effectiveness",
        "wue",
        "aws standard",
        "water stewardship",
        "wastewater",
        "cod",
        "废水",
        "污水",
        "总镍",
        "初期雨水",
        "取水",
        "水资源",
    ),
    "E4": (
        "ecosystem",
        "biodiversity",
        "habitat",
        "more land than",
        "生态",
        "生物多样性",
        "栖息地",
        "森林",
    ),
    "E5": (
        "zero waste",
        "waste diversion",
        "hazardous waste",
        "recycling",
        "circular",
        "plastic",
        "packaging",
        "recycled content",
        "recycled material",
        "recycled cobalt",
        "recycled tin",
        "recycled gold",
        "rare earth",
        "废弃物",
        "固体废物",
        "危险废物",
        "回收",
        "循环利用",
        "塑料",
        "包装",
        "再生材料",
        "再生钴",
        "再生锡",
        "再生金",
        "稀土",
    ),
    "S1": (
        "employee",
        "workforce",
        "安全生产",
        "员工",
        "职业健康",
        "工亡",
        "工伤",
        "职业病",
    ),
    "S2": (
        "supplier",
        "supply chain",
        "供应商",
        "供应链",
        "3tg",
        "rmap",
        "原产国追溯",
    ),
    "S3": (
        "customer",
        "privacy",
        "information security",
        "客户",
        "数据保护",
        "信息安全",
        "隐私保护",
    ),
    "S4": ("community", "社区", "公益"),
    "G1": ("board", "governance", "董事会", "公司治理"),
    "G2": ("remuneration", "executive pay", "薪酬"),
    "G3": ("anti-corruption", "bribery", "反腐败", "反贿赂"),
    "G4": ("tax transparency", "税务透明"),
}

THEME_PATTERNS: dict[str, re.Pattern[str]] = {
    "carbon_neutral": re.compile(r"carbon[ -]?neutral|碳中和", re.IGNORECASE),
    "carbon_negative": re.compile(r"carbon[ -]?negative|负碳", re.IGNORECASE),
    "carbon_2030": re.compile(
        r"(?:carbon[ -]?neutral|carbon[ -]?negative|75\s+percent)"
        r"[^.]{0,100}2030|2030[^.]{0,100}(?:carbon|emissions)",
        re.IGNORECASE,
    ),
    "net_zero": re.compile(r"net[ -]?zero|净零", re.IGNORECASE),
    "water_positive": re.compile(r"water[ -]?positive|水正效益", re.IGNORECASE),
    "water_replenish": re.compile(
        r"replenish[^.]{0,80}water|freshwater withdrawals|水回补|回补",
        re.IGNORECASE,
    ),
    "supplier_water_reuse": re.compile(
        r"supplier[^.]{0,100}water[^.]{0,100}reuse|"
        r"water\s+reuse\s+rate",
        re.IGNORECASE,
    ),
    "aws_water_standard": re.compile(
        r"Alliance for Water Stewardship|AWS Standard|AWS认证",
        re.IGNORECASE,
    ),
    "waste_diversion": re.compile(
        r"waste diversion rate|waste sent to landfill|废弃物平均转化率",
        re.IGNORECASE,
    ),
    "recycled_materials": re.compile(
        r"recycled cobalt|recycled tin|recycled gold|rare earth",
        re.IGNORECASE,
    ),
    "zero_waste": re.compile(r"zero[ -]?waste|零废弃", re.IGNORECASE),
    "plastics_removal": re.compile(
        r"remove\s+plastics?|single-use\s+plastics?|fiber-based\s+packaging|"
        r"去除塑料|塑料包装",
        re.IGNORECASE,
    ),
    "ecosystem_land": re.compile(
        r"protect(?:ing)? more land|ecosystem|biodiversity|生态|生物多样性",
        re.IGNORECASE,
    ),
    "cod": re.compile(r"\bcod\b|化学需氧量", re.IGNORECASE),
    "nox": re.compile(r"\bnox\b|氮氧化物", re.IGNORECASE),
    "hazardous_waste": re.compile(r"hazardous waste|危险废物", re.IGNORECASE),
    "voc": re.compile(r"\bvoc s?\b|挥发性有机物", re.IGNORECASE),
}


def _term_occurs(text: str, term: str) -> bool:
    clean = term.strip()
    if not clean:
        return False
    if re.search(r"[\u3400-\u9fff]", clean):
        return clean.casefold() in text.casefold()
    words = re.split(r"\s+", clean.casefold())
    escaped = r"\s+".join(re.escape(word) for word in words)
    if clean.casefold() == "board":
        pattern = rf"(?<![a-z0-9]){escaped}(?![a-z0-9])"
    else:
        pattern = (
            rf"(?<![a-z0-9]){escaped}"
            r"(?:s|es|ed|ing|ization|ize|ized)?(?![a-z0-9])"
        )
    return bool(re.search(pattern, text, re.IGNORECASE))


def _contains_any(text: str, phrases: Iterable[str]) -> list[str]:
    return [phrase for phrase in phrases if _term_occurs(text, phrase)]


def _sentence_parts(text: str) -> list[str]:
    return [
        part.strip() for part in SENTENCE_SPLIT_RE.split(text) if part and part.strip()
    ]


def _commitment_units(text: str) -> list[str]:
    units: list[str] = []
    for bullet_group in BULLET_SPLIT_RE.split(text):
        for section in TABLE_SECTION_SPLIT_RE.split(bullet_group):
            units.extend(_sentence_parts(section))
    return [unit.strip(" ■•▪◦●◆◇") for unit in units if unit.strip(" ■•▪◦●◆◇")]


@lru_cache(maxsize=50000)
def _category_matches(text: str) -> tuple[tuple[str, str, float], ...]:
    pack = load_rule_pack()
    matches: list[tuple[str, str, float]] = []
    for category_id, category in pack["categories"].items():
        general_count = sum(1 for term in category["terms"] if _term_occurs(text, term))
        boost_count = sum(
            1
            for term in CATEGORY_BOOSTS.get(category_id, ())
            if _term_occurs(text, term)
        )
        score = general_count + (boost_count * 4.0)
        if score:
            matches.append((category_id, category["label"], score))
    return tuple(matches)


def _choose_category(text: str) -> tuple[str, str]:
    pack = load_rule_pack()
    matches = _category_matches(text)
    by_id = {
        category_id: (category_id, category["label"])
        for category_id, category in pack["categories"].items()
    }
    priority_patterns = (
        ("G4", r"tax transparency|税务透明|税收策略"),
        (
            "G3",
            (
                r"anti[- ]?corruption|bribery|whistleblower|"
                r"商业道德|反腐败|反贿赂|廉洁|举报"
            ),
        ),
        ("G2", r"remuneration|executive pay|高管薪酬|薪酬挂钩"),
        ("G1", r"\bboard\b|independent director|董事会|独立董事"),
        ("S3", r"information security|data protection|privacy|信息安全|隐私|数据保护"),
        ("E3", r"water|wastewater|freshwater|水资源|用水|取水|废水|污水"),
        (
            "E5",
            (
                r"recycled|recycling|rare earth|zero waste|waste diversion|"
                r"\bwaste\b|plastic|packaging|circular|"
                r"再生|回收|稀土|废弃物|塑料|包装|循环"
            ),
        ),
        (
            "E1",
            (
                r"emission|greenhouse|net zero|carbon|scope [123]|"
                r"温室气体|排放|净零|碳中和|碳足迹|减碳|减排"
            ),
        ),
        (
            "E2",
            (
                r"renewable energy|clean energy|clean electricity|"
                r"renewable electricity|energy efficiency|"
                r"可再生能源|清洁能源|绿电|节能|能效"
            ),
        ),
        ("E4", r"biodiversity|ecosystem|habitat|生物多样性|生态系统|栖息地"),
        (
            "S1",
            (
                r"employee|workforce|injury|training|occupational health|"
                r"员工|工伤|职业健康|培训|多元化|女性董事"
            ),
        ),
        ("S2", r"supplier|supply chain|human rights|3tg|供应商|供应链|人权|强迫劳动"),
        ("S4", r"community|philanthropy|社区|公益"),
    )
    for category_id, pattern in priority_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return by_id[category_id]
    if matches:
        category_id, label, _ = max(matches, key=lambda item: (item[2], item[0]))
        return category_id, label
    return by_id["E1"]


def _verb_strength(text: str) -> tuple[str, float]:
    verbs = load_rule_pack()["commitment_verbs"]
    strong = _contains_any(text, verbs["strong"])
    medium = _contains_any(text, verbs["medium"])
    weak = _contains_any(text, verbs["weak"])
    if strong:
        return "strong", 0.90
    if weak:
        return "weak", 0.55
    if medium:
        return "medium", 0.75
    return "weak", 0.0


def _classify_statement(
    text: str,
    *,
    section: str | None = None,
    source_type: str = "paragraph",
    table_role: str | None = None,
) -> bool:
    clean = " ".join(text.split())
    clean = re.sub(r"(?<=\d)\s+(?=\d\s*[%％])", "", clean)
    if len(clean) > 1500 or CITATION_RE.search(clean):
        return False
    if RUNNING_HEADER_RE.search(clean):
        return False
    if PAGE_NAV_RE.search(clean) and len(clean) > 120:
        return False
    if ADVOCACY_RE.search(clean) and not re.search(
        r"\b(?:we|our company|company)\b|(?:公司|我们)",
        clean,
        re.IGNORECASE,
    ):
        return False
    if EXTERNAL_TARGET_RE.search(clean):
        return False
    if NON_COMMITMENT_RE.search(clean):
        return False
    if not _category_matches(clean):
        return False
    if SCENARIO_RE.search(clean) and not re.search(
        r"\b(?:we|microsoft|company)\b.{0,30}\b(?:commit|will|target)\b|"
        r"(?:公司|我们).{0,20}(?:承诺|将|目标)",
        clean,
        re.IGNORECASE,
    ):
        return False

    hard_future = bool(FUTURE_HARD_RE.search(clean))
    ongoing = bool(ONGOING_RE.search(clean))
    target_reference = bool(TARGET_REFERENCE_RE.search(clean))
    completed = bool(COMPLETED_ACTION_RE.search(clean))
    historical = bool(HISTORICAL_RE.search(clean))
    method = bool(METHOD_RE.search(clean))
    governance = bool(GOVERNANCE_RE.search(clean))
    weak = bool(WEAK_RE.search(clean))
    binding_requirement = bool(BINDING_REQUIREMENT_RE.search(clean))
    table_target = table_role == "target"
    table_quantified = table_target and bool(
        re.search(
            r"\d{1,3}(?:\.\d+)?\s*[%％]|达到|下降|提高|降低|减少|"
            r"累计节能|不低于|不少于|每年至少|三分之一|二分之一|一半|"
            r"所有产品|零工亡|零职业病",
            clean,
        )
    )
    goal_outcome = bool(GOAL_OUTCOME_RE.search(clean))
    table_year_outcome = table_target and bool(YEAR_RE.search(clean)) and goal_outcome
    table_recurring = table_target and bool(
        re.match(
            r"^(?:定期|每年|年度|开展|构建|建立|完善|强化|推动|保持|聘请)",
            clean,
        )
    )
    explicit_reduction = bool(
        re.search(
            r"\b(?:reduc(?:e|es|ed|ing|tion)|cut(?:s|ting)?|"
            r"lower(?:s|ed|ing)?|decreas(?:e|es|ed|ing))\b|"
            r"减少|降低|削减|下降",
            clean,
            re.IGNORECASE,
        )
    )
    explicit_outcome_target = bool(
        TARGET_YEAR_CONTEXT_RE.search(clean)
        and re.search(
            r"carbon[ -]?neutral|carbon[ -]?negative|net[ -]?zero|"
            r"water[ -]?positive|zero[ -]?waste|replenish|remove\s+plastics?|"
            r"transition[^.]{0,80}(?:recycled|renewable)|"
            r"protect(?:ing)?\s+more\s+land|recycled|waste\s+diversion|certify|"
            r"protect|restore|ecosystem|biodiversity|"
            r"increase\s+supplier|clean\s+(?:electricity|energy)|"
            r"renewable\s+(?:electricity|energy)|reduce|reduction|"
            r"碳中和|碳减排|减少|降低|零废弃|水正效益",
            clean,
            re.IGNORECASE,
        )
    )
    concrete_recurring = bool(
        re.search(
            r"\b(?:annual|annually|each year|every year|quarterly|"
            r"semi-?annual|monthly|every\s+\d+\s+years?)\b|"
            r"(?:每年|年度|每季度|每半年|每\s*\d+\s*年)",
            clean,
            re.IGNORECASE,
        )
    )
    year_count = len(set(YEAR_RE.findall(clean)))
    percent_count = len(PERCENT_RE.findall(clean))
    data_dump = (
        (year_count >= 4 or percent_count >= 4) and not hard_future and not table_target
    )
    if data_dump:
        return False

    historical_result = (
        historical
        and not hard_future
        and not table_target
        and not target_reference
        and not explicit_outcome_target
        and not TARGET_LIST_RE.search(clean)
    )
    completed_result = (
        completed
        and not hard_future
        and not table_target
        and not target_reference
        and not explicit_outcome_target
    )
    if historical_result or completed_result:
        return False

    has_target_signal = bool(
        target_reference
        or explicit_outcome_target
        or binding_requirement
        or (YEAR_RE.search(clean) and (goal_outcome or explicit_reduction))
        or (
            TARGET_YEAR_CONTEXT_RE.search(clean)
            and (
                PERCENT_RE.search(clean)
                or QUANTITY_RE.search(clean)
                or CONCRETE_FUTURE_ACTION_RE.search(clean)
            )
        )
        or (
            (PERCENT_RE.search(clean) or QUANTITY_RE.search(clean))
            and (goal_outcome or explicit_reduction)
        )
    )

    if table_target and (table_quantified or table_recurring or table_year_outcome):
        return True
    if TARGET_LIST_RE.search(clean) and goal_outcome:
        return True
    if (
        target_reference
        and not re.search(
            r"\bexceed(?:ed|ing)?\b|超过|优于",
            clean,
            re.IGNORECASE,
        )
        and (
            hard_future
            or explicit_outcome_target
            or explicit_reduction
            or goal_outcome
            or TARGET_YEAR_CONTEXT_RE.search(clean)
            or PERCENT_TARGET_ADJACENT_RE.search(clean)
        )
    ):
        return True
    if explicit_outcome_target and not completed:
        return True
    if (
        binding_requirement
        and not completed
        and (hard_future or TARGET_YEAR_CONTEXT_RE.search(clean) or table_target)
    ):
        return True
    if (
        hard_future
        and has_target_signal
        and (
            TARGET_YEAR_CONTEXT_RE.search(clean)
            or PERCENT_RE.search(clean)
            or table_target
        )
    ):
        return True
    if (
        ongoing
        and concrete_recurring
        and has_target_signal
        and not (method and not target_reference)
    ):
        return True
    if concrete_recurring and RECURRING_ACTION_RE.search(clean):
        return True
    if (method or governance) and not hard_future and not table_target:
        return False
    if IMPERATIVE_GOAL_RE.search(clean) and goal_outcome:
        return True
    return bool(
        weak and re.search(r"未来|future", clean, re.IGNORECASE) and explicit_reduction
    )


def _likelihood(text: str) -> float:
    strength, verb_confidence = _verb_strength(text)
    if verb_confidence == 0.0:
        verb_confidence = 0.55 if FUTURE_HARD_RE.search(text) else 0.35

    category_matches = _category_matches(text)
    has_quantity = bool(QUANTITY_RE.search(text) or PERCENT_RE.search(text))
    has_year = bool(YEAR_RE.search(text))
    score = 0.20 + (verb_confidence * 0.24)
    if strength == "strong":
        score += 0.12
    elif strength == "weak":
        score -= 0.03
    if category_matches:
        score += 0.12
    if has_quantity:
        score += 0.12
    if has_year:
        score += 0.08
    if re.search(r"scope\s*[123]|范围[一二三123]", text, re.IGNORECASE):
        score += 0.04
    return round(min(1.0, max(0.0, score)), 4)


def _excerpt(text: str, limit: int = 360) -> str:
    clean = " ".join(text.split())
    return clean if len(clean) <= limit else clean[: limit - 1].rstrip() + "…"


def _evidence(
    block: DocumentBlock, text: str, unit_index: int | None = None
) -> EvidenceSpan:
    return EvidenceSpan(
        block_id=block.block_id,
        paragraph_index=block.paragraph_index,
        unit_index=unit_index,
        page_number=block.page_number,
        section=block.section,
        source_type=block.source_type,
        table_role=block.table_role,
        text=text,
        excerpt=_excerpt(text),
    )


def _find_nearby_year(
    text: str, anchors: Iterable[str], radius: int = 36
) -> int | None:
    lower = text.casefold()
    for anchor in anchors:
        start = 0
        anchor_lower = anchor.casefold()
        while True:
            index = lower.find(anchor_lower, start)
            if index < 0:
                break
            window = text[max(0, index - radius) : index + len(anchor) + radius]
            years = [int(match.group(1)) for match in YEAR_RE.finditer(window)]
            if years:
                return years[0]
            start = index + len(anchor)
    return None


def _select_context_blocks(
    document: IngestedDocument,
    primary_index: int,
    primary: DocumentBlock,
) -> list[DocumentBlock]:
    selected: dict[str, DocumentBlock] = {}

    for offset in range(-3, 4):
        index = primary_index + offset
        if index < 0 or index >= len(document.blocks) or index == primary_index:
            continue
        block = document.blocks[index]
        if block.is_heading:
            continue
        same_page = (
            primary.page_number is not None and block.page_number == primary.page_number
        )
        same_section = primary.section is not None and block.section == primary.section
        if same_page or same_section:
            selected[block.block_id] = block

    global_terms = (
        "committee",
        "board",
        "oversight",
        "assurance",
        "verification",
        "ghg protocol",
        "gri",
        "issb",
        "tcfd",
        "annual report",
        "董事",
        "委员会",
        "监督",
        "鉴证",
        "审验",
        "年度报告",
        "可持续发展报告",
        "绩效",
    )
    for block in document.blocks:
        if block.block_id in selected or block.block_id == primary.block_id:
            continue
        if block.is_heading:
            continue
        if _contains_any(block.text, global_terms):
            selected[block.block_id] = block
        if len(selected) >= 16:
            break
    return list(selected.values())


def _evidence_for_terms(
    primary_text: str,
    primary_evidence: EvidenceSpan,
    context_blocks: list[DocumentBlock],
    terms: Iterable[str],
    *,
    primary_only: bool = False,
) -> list[EvidenceSpan]:
    sources: list[EvidenceSpan] = []
    if _contains_any(primary_text, terms):
        sources.append(primary_evidence)
    if primary_only:
        return sources
    for block in context_blocks:
        if _contains_any(block.text, terms):
            sources.append(_evidence(block, block.text))
    return _dedupe_evidence(sources)[:4]


def _dedupe_evidence(evidence: list[EvidenceSpan]) -> list[EvidenceSpan]:
    seen: set[tuple[str, int | None, str]] = set()
    result: list[EvidenceSpan] = []
    for item in evidence:
        key = (item.block_id, item.unit_index, item.text[:120])
        if key not in seen:
            seen.add(key)
            result.append(item)
    return result


def _extract_facts(
    text: str,
    primary_evidence: EvidenceSpan,
    context_blocks: list[DocumentBlock],
) -> tuple[CommitmentFacts, dict[str, list[EvidenceSpan]]]:
    pack = load_rule_pack()
    years = [int(match.group(1)) for match in YEAR_RE.finditer(text)]
    baseline_year = _find_nearby_year(
        text,
        ("baseline", "base year", "基准年", "基准线", "以", "compared with", "较"),
    )
    if baseline_year not in years:
        baseline_year = None

    target_years = [
        year
        for year in years
        if re.search(
            rf"(?:by|before|no later than|到|于|前|实现|达到|目标)"
            rf"[^。；;.!?]{{0,18}}{year}|"
            rf"{year}[^。；;.!?]{{0,12}}(?:前|实现|达到|目标)",
            text,
            re.IGNORECASE,
        )
    ]
    if not target_years:
        target_years = [year for year in years if year != baseline_year]
    target_year = max(target_years) if target_years else None
    milestone_years = sorted(
        {year for year in years if year != baseline_year and year != target_year}
    )

    target_percentages: list[float] = []
    reduction_context = re.compile(
        r"(?:reduce|cut|lower|decrease|减少|降低|削减|下降)"
        r"[^。；;.!?]{0,48}?(\d{1,3}(?:\.\d+)?)\s*"
        r"(?:%|％|percent\b)",
        re.IGNORECASE,
    )
    for match in reduction_context.finditer(text):
        value = float(match.group(1))
        if 0 <= value <= 100:
            target_percentages.append(value)
    if not target_percentages:
        for match in PERCENT_RE.finditer(text):
            value = float(match.group(1))
            window = text[max(0, match.start() - 60) : match.end() + 60]
            if 0 <= value <= 100 and re.search(
                r"target|goal|aim|expected|ensure|require|commit|reduce|cut|"
                r"recycled|renewable|waste|water|emission|footprint|scope|"
                r"energy|减排|目标|降低|回收|可再生|废弃物|水|能源",
                window,
                re.IGNORECASE,
            ):
                target_percentages.append(value)

    scopes = sorted(
        {
            scope
            for scope in (
                "Scope 1",
                "Scope 2",
                "Scope 3",
                "范围一",
                "范围二",
                "范围三",
                "范围1",
                "范围2",
                "范围3",
            )
            if scope.casefold() in text.casefold()
        }
    )
    standards = []
    for standard, terms in pack["standards"].items():
        if _contains_any(text, terms) or any(
            _contains_any(block.text, terms) for block in context_blocks
        ):
            standards.append(standard)

    sources: dict[str, list[EvidenceSpan]] = {}
    sources["quantitative"] = (
        [primary_evidence]
        if QUANTITY_RE.search(text) or PERCENT_RE.search(text)
        else []
    )
    sources["baseline"] = [primary_evidence] if baseline_year else []
    sources["scope"] = [primary_evidence] if scopes else []
    sources["timeframe"] = [primary_evidence] if target_year or milestone_years else []
    sources["owner"] = _evidence_for_terms(
        text, primary_evidence, context_blocks, pack["owners"]
    )
    sources["standards"] = _evidence_for_terms(
        text,
        primary_evidence,
        context_blocks,
        [term for terms in pack["standards"].values() for term in terms],
    )
    sources["assurance"] = _evidence_for_terms(
        text, primary_evidence, context_blocks, pack["assurance_terms"]
    )
    sources["reporting"] = _evidence_for_terms(
        text, primary_evidence, context_blocks, pack["reporting_terms"]
    )
    sources["binding"] = _evidence_for_terms(
        text, primary_evidence, context_blocks, pack["binding_terms"]
    )
    sources["remedy"] = _evidence_for_terms(
        text, primary_evidence, context_blocks, pack["remedy_terms"]
    )
    sources["review"] = _evidence_for_terms(
        text, primary_evidence, context_blocks, pack["review_terms"]
    )
    sources["trigger"] = _evidence_for_terms(
        text, primary_evidence, context_blocks, pack["revision_trigger_terms"]
    )
    sources["withdrawal"] = _evidence_for_terms(
        text, primary_evidence, context_blocks, pack["withdrawal_terms"]
    )
    sources["mitigation"] = _evidence_for_terms(
        text, primary_evidence, context_blocks, pack["mitigation_terms"]
    )
    sources["conditional"] = _evidence_for_terms(
        text,
        primary_evidence,
        [],
        pack["conditional_terms"],
        primary_only=True,
    )
    sources["method"] = _evidence_for_terms(
        text, primary_evidence, context_blocks, pack["method_terms"]
    )
    sources["staged"] = _evidence_for_terms(
        text, primary_evidence, context_blocks, pack["staged_terms"]
    )

    facts = CommitmentFacts(
        quantitative_expressions=[
            match.group(0) for match in QUANTITY_RE.finditer(text)
        ],
        target_percentages=sorted(set(target_percentages)),
        baseline_year=baseline_year,
        target_year=target_year,
        all_years=sorted(set(years)),
        milestone_years=milestone_years,
        scopes_covered=scopes,
        reporting_standards=standards,
        responsible_bodies=_contains_any(text, pack["owners"])
        or [
            phrase
            for block in context_blocks
            for phrase in _contains_any(block.text, pack["owners"])
        ],
        assurance_terms=_contains_any(text, pack["assurance_terms"])
        or [
            phrase
            for block in context_blocks
            for phrase in _contains_any(block.text, pack["assurance_terms"])
        ],
        reporting_terms=_contains_any(text, pack["reporting_terms"])
        or [
            phrase
            for block in context_blocks
            for phrase in _contains_any(block.text, pack["reporting_terms"])
        ],
        binding_terms=_contains_any(text, pack["binding_terms"])
        or [
            phrase
            for block in context_blocks
            for phrase in _contains_any(block.text, pack["binding_terms"])
        ],
        remedy_terms=_contains_any(text, pack["remedy_terms"])
        or [
            phrase
            for block in context_blocks
            for phrase in _contains_any(block.text, pack["remedy_terms"])
        ],
        review_terms=_contains_any(text, pack["review_terms"])
        or [
            phrase
            for block in context_blocks
            for phrase in _contains_any(block.text, pack["review_terms"])
        ],
        revision_trigger_terms=_contains_any(text, pack["revision_trigger_terms"])
        or [
            phrase
            for block in context_blocks
            for phrase in _contains_any(block.text, pack["revision_trigger_terms"])
        ],
        withdrawal_terms=_contains_any(text, pack["withdrawal_terms"])
        or [
            phrase
            for block in context_blocks
            for phrase in _contains_any(block.text, pack["withdrawal_terms"])
        ],
        mitigation_terms=_contains_any(text, pack["mitigation_terms"])
        or [
            phrase
            for block in context_blocks
            for phrase in _contains_any(block.text, pack["mitigation_terms"])
        ],
        conditional_terms=_contains_any(text, pack["conditional_terms"]),
        method_terms=_contains_any(text, pack["method_terms"])
        or [
            phrase
            for block in context_blocks
            for phrase in _contains_any(block.text, pack["method_terms"])
        ],
        staged_terms=_contains_any(text, pack["staged_terms"]),
    )
    return facts, sources


def _themes(text: str) -> set[str]:
    return {name for name, pattern in THEME_PATTERNS.items() if pattern.search(text)}


def _normalized(text: str) -> str:
    return re.sub(r"\s+", " ", text.casefold()).strip(" .。;；:：")


def _is_duplicate(left: CommitmentRecord, right: CommitmentRecord) -> bool:
    if left.category != right.category:
        return False
    left_scopes = set(left.facts.scopes_covered)
    right_scopes = set(right.facts.scopes_covered)
    if left_scopes and right_scopes and left_scopes != right_scopes:
        return False
    left_percentages = set(left.facts.target_percentages)
    right_percentages = set(right.facts.target_percentages)
    if left_percentages and right_percentages and left_percentages != right_percentages:
        return False

    normalized_left = _normalized(left.text)
    normalized_right = _normalized(right.text)
    similarity = SequenceMatcher(None, normalized_left, normalized_right).ratio()
    if normalized_left in normalized_right or normalized_right in normalized_left:
        length_ratio = min(len(normalized_left), len(normalized_right)) / max(
            len(normalized_left), len(normalized_right)
        )
        if length_ratio >= 0.65:
            return True

    if (
        left_percentages
        and left_percentages == right_percentages
        and left.facts.target_year is not None
        and (left.facts.target_year == right.facts.target_year)
        and (similarity >= 0.20 or bool(_themes(left.text) & _themes(right.text)))
    ):
        return True

    common_themes = _themes(left.text) & _themes(right.text)
    common_years = set(left.facts.all_years) & set(right.facts.all_years)
    if (
        {"plastics_removal", "zero_waste"} & common_themes
        and left.facts.target_year is not None
        and left.facts.target_year == right.facts.target_year
        and similarity >= 0.25
    ):
        return True
    if (
        len(common_themes) >= 2
        and left.facts.target_year is not None
        and left.facts.target_year == right.facts.target_year
        and similarity >= 0.30
    ):
        return True
    if common_themes and common_years and similarity >= 0.55:
        return True
    return similarity >= 0.90


def _candidate_key(document: IngestedDocument, record: CommitmentRecord) -> str:
    page = record.evidence.page_number or 0
    digest = hashlib.sha256(
        f"{document.sha256}|{page}|{_normalized(record.text)}".encode()
    ).hexdigest()[:12]
    return f"{document.sha256[:10]}-p{page:03d}-{digest}"


def _deduplicate(records: list[CommitmentRecord]) -> list[CommitmentRecord]:
    unique: list[CommitmentRecord] = []
    for record in records:
        duplicate = next(
            (existing for existing in unique if _is_duplicate(existing, record)),
            None,
        )
        if duplicate is None:
            unique.append(record)
        elif (
            record.evidence.source_type == "table"
            and duplicate.evidence.source_type != "table"
        ) or (
            _normalized(duplicate.text) in _normalized(record.text)
            and len(record.text) > len(duplicate.text) + 15
        ):
            duplicate.duplicate_evidence.append(duplicate.evidence)
            duplicate.evidence = record.evidence
            duplicate.text = record.text
            duplicate.extraction_confidence = record.extraction_confidence
            duplicate.facts = record.facts
            duplicate.evidence_by_fact = record.evidence_by_fact
            duplicate.related_evidence = record.related_evidence
        else:
            duplicate.duplicate_evidence.append(record.evidence)
            duplicate.duplicate_evidence = _dedupe_evidence(
                duplicate.duplicate_evidence
            )
    for index, record in enumerate(unique, start=1):
        record.commitment_id = f"c{index:03d}"
    return unique


def extract_commitments(document: IngestedDocument) -> list[CommitmentRecord]:
    records: list[CommitmentRecord] = []
    seen: set[str] = set()
    sequence = 0

    for block_index, block in enumerate(document.blocks):
        if block.is_heading or block.table_role == "progress":
            continue
        for unit_index, unit in enumerate(_commitment_units(block.text), start=1):
            if re.match(r"^(?:目标进展|进展\s*[：:])", unit):
                continue
            if (
                block.table_role != "target"
                and PROGRESS_START_RE.match(unit)
                and not FUTURE_HARD_RE.search(unit)
            ):
                continue
            if len(unit) < 8 or not _classify_statement(
                unit,
                section=block.section,
                source_type=block.source_type,
                table_role=block.table_role,
            ):
                continue
            normalized = _normalized(unit)
            if normalized in seen:
                continue
            seen.add(normalized)

            sequence += 1
            strength, _ = _verb_strength(unit)
            category, subcategory_label = _choose_category(unit)
            primary_evidence = _evidence(block, unit, unit_index=unit_index)
            context_blocks = _select_context_blocks(document, block_index, block)
            facts, evidence_by_fact = _extract_facts(
                unit, primary_evidence, context_blocks
            )
            related_evidence = _dedupe_evidence(
                [
                    source
                    for sources in evidence_by_fact.values()
                    for source in sources
                    if source.text != primary_evidence.text
                ]
            )
            records.append(
                CommitmentRecord(
                    commitment_id=f"c{sequence:03d}",
                    candidate_key="",
                    text=unit,
                    strength=strength,
                    extraction_confidence=_likelihood(unit),
                    category=category[0],
                    subcategory=subcategory_label,
                    evidence=primary_evidence,
                    related_evidence=related_evidence,
                    evidence_by_fact=evidence_by_fact,
                    facts=facts,
                )
            )

    commitments = _deduplicate(records)
    for record in commitments:
        record.candidate_key = _candidate_key(document, record)
    return commitments
