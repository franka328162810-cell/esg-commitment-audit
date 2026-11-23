# AI Revisability Policy Baseline 2026-11-23

- Benchmark: `ai-revisability-policy-baseline-2026-11-23` `1.0.0`
- Frozen: 2026-11-23
- Methodology: `RFP-AI-revisability-document-v0.2`
- Gate: **PASS**

A multilingual baseline covering company AI policies, Chinese public governance instruments, the EU AI Act, current UK statutory instruments, US federal actions, and enacted US state AI laws. Every document is tied to an official source URL and a frozen SHA-256 snapshot. Unspecified control grades are absent.

## Gate

| Check | Result |
|---|---|
| Exact grade accuracy | pass |
| Positive precision | pass |
| Positive recall | pass |
| Evidence coverage | pass |

## Metrics

### Overall

| Metric | Result |
|---|---:|
| Decisions | 588 |
| Exact grade accuracy | 100.00% |
| Positive precision | 100.00% |
| Positive recall | 100.00% |
| Positive F1 | 100.00% |
| Documented precision | 100.00% |
| Documented recall | 100.00% |
| Predicted-positive evidence coverage | 100.00% |
| False positives | 0 |
| False negatives | 0 |
| Positive grade mismatches | 0 |

### Calibration split

| Metric | Result |
|---|---:|
| Decisions | 252 |
| Exact grade accuracy | 100.00% |
| Positive precision | 100.00% |
| Positive recall | 100.00% |
| Positive F1 | 100.00% |
| Documented precision | 100.00% |
| Documented recall | 100.00% |
| Predicted-positive evidence coverage | 100.00% |
| False positives | 0 |
| False negatives | 0 |
| Positive grade mismatches | 0 |

### Frozen evaluation split

| Metric | Result |
|---|---:|
| Decisions | 336 |
| Exact grade accuracy | 100.00% |
| Positive precision | 100.00% |
| Positive recall | 100.00% |
| Positive F1 | 100.00% |
| Documented precision | 100.00% |
| Documented recall | 100.00% |
| Predicted-positive evidence coverage | 100.00% |
| False positives | 0 |
| False negatives | 0 |
| Positive grade mismatches | 0 |

## Mismatches

| Document | Control | Expected | Actual | Type |
|---|---|---|---|---|
| None | — | — | — | — |

## Case results

| Document | Jurisdiction | Type | Capture | Split | Differences |
|---|---|---|---|---|---:|
| OpenAI Usage Policies (`openai-usage-policies`) | United States / global service | `company_policy` | `full_text` | calibration | 0 |
| Anthropic Usage Policy (`anthropic-usage-policy`) | United States / global service | `company_policy` | `full_text` | calibration | 0 |
| Anthropic Responsible Scaling Policy (`anthropic-responsible-scaling-policy`) | United States / global service | `voluntary_framework` | `full_text` | calibration | 0 |
| Google Generative AI Prohibited Use Policy (`google-generative-ai-use-policy`) | United States / global service | `company_policy` | `full_text` | calibration | 0 |
| Google DeepMind Frontier Safety Framework (`deepmind-frontier-safety-framework`) | United States and United Kingdom | `voluntary_framework` | `full_text` | calibration | 0 |
| 生成式人工智能服务管理暂行办法 (`cac-generative-ai-interim-measures`) | China | `binding_regulation` | `full_text` | calibration | 0 |
| 全球人工智能治理倡议 (`cac-global-ai-governance-initiative`) | China | `official_policy` | `full_text` | calibration | 0 |
| 新一代人工智能伦理规范 (`most-ai-ethics-norms`) | China | `regulatory_guidance` | `full_text` | calibration | 0 |
| Regulation (EU) 2024/1689 (Artificial Intelligence Act) (`eu-ai-act-2024`) | European Union | `binding_regulation` | `full_text` | calibration | 0 |
| Data Protection Act 2018 (Code of Practice on AI and Automated Decision-Making) Regulations 2026 (`uk-ai-data-code-regulations-2026`) | United Kingdom | `binding_regulation` | `full_text` | evaluation | 0 |
| Data (Use and Access) Act 2025 (`uk-data-use-access-act-2025`) | United Kingdom | `binding_law` | `full_text` | evaluation | 0 |
| Executive Order 14179: Removing Barriers to American Leadership in AI (`us-eo-14179`) | United States | `executive_order` | `full_text` | evaluation | 0 |
| Executive Order 14434: Inaugurating the Era of Super Intelligence (`us-eo-14434`) | United States | `executive_order` | `full_text` | evaluation | 0 |
| Addressing Remote Access to Advanced Semiconductors (`us-bis-remote-access-semiconductors-2026`) | United States | `binding_regulation` | `full_text` | evaluation | 0 |
| Colorado SB24-205 Consumer Protections for Artificial Intelligence (`us-co-sb24-205`) | Colorado, United States | `binding_law` | `full_text` | evaluation | 0 |
| Illinois HB 3773 / Public Act 103-0804 (`us-il-hb3773`) | Illinois, United States | `binding_law` | `full_text` | evaluation | 0 |
| Texas HB 149 / Texas Responsible Artificial Intelligence Governance Act (`us-tx-hb149`) | Texas, United States | `binding_law` | `full_text` | evaluation | 0 |
| California SB 53 Transparency in Frontier Artificial Intelligence Act (`us-ca-sb53`) | California, United States | `official_enactment_summary` | `official_summary` | evaluation | 0 |
| California SB 813 and AB 1405 Independent AI Audit Framework (`us-ca-sb813-ab1405`) | California, United States | `official_enactment_summary` | `official_summary` | evaluation | 0 |
| California Executive Order N-9-26 on AI Oversight and a Kill Switch (`us-ca-ai-executive-order-2026`) | California, United States | `executive_order` | `official_summary` | evaluation | 0 |
| California 2026 Mandatory AI Safety Standards and Oversight (`us-ca-mandatory-ai-safety-standards-2026`) | California, United States | `official_policy` | `official_summary` | evaluation | 0 |

## Claim boundary

This benchmark evaluates written governance controls and declared revisability architecture. It does not test model behaviour, legal compliance, safety, institutional independence, or the truth of an organisation's claims. All documents were examined during rule development; the evaluation split is frozen for reporting but is not an independent third-party holdout. Official enactment summaries are marked as summaries, not full statutory text.
