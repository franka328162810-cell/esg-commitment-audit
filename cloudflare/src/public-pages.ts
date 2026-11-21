const style = `
  :root { color-scheme: light; font-family: ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif; }
  body { margin: 0; color: #182126; background: #f4f7f5; }
  main { max-width: 860px; margin: 0 auto; padding: 48px 24px 80px; }
  article { background: #fff; border: 1px solid #dbe4df; border-radius: 18px; padding: 32px; }
  h1 { font-size: clamp(2rem, 5vw, 3.6rem); line-height: 1.05; margin: 0 0 16px; }
  h2 { margin-top: 34px; font-size: 1.3rem; }
  p, li { line-height: 1.75; }
  a { color: #08734f; }
  .eyebrow { text-transform: uppercase; letter-spacing: .12em; color: #08734f; font-weight: 700; }
  .notice { border-left: 4px solid #d69219; background: #fff8e8; padding: 14px 18px; }
  .muted { color: #5e6b66; }
  nav { display: flex; flex-wrap: wrap; gap: 18px; margin-top: 30px; }
`;

function page(title: string, body: string): string {
  return `<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>${title}</title>
  <style>${style}</style>
</head>
<body>
  <main>${body}</main>
</body>
</html>`;
}

export const landingPage = page(
  "ICS Commitment Audit | 承诺审计工作台",
  `<article>
    <p class="eyebrow">ICS-TEC</p>
    <h1>把可持续承诺变成可核查的结构证据</h1>
    <p>ICS Commitment Audit 是面向 ESG、气候与组织承诺文本的结构审计工具。它识别目标、时间、范围、指标和执行强度，并在结果中保留页码或段落证据。</p>
    <p class="notice"><strong>边界：</strong>本工具提供文本结构分析，不构成审计鉴证、法律意见、合规认证、投资建议或“漂绿”事实认定。</p>
    <h2>当前服务</h2>
    <ul>
      <li>支持 TXT、Markdown、DOCX 和 PDF 文本型文件。</li>
      <li>原始文件在成功处理或最终失败后删除；报告默认保留 7 天。</li>
      <li>当前试用账户采用邀请创建，正式在线购买入口尚在配置。</li>
    </ul>
    <h2>开发者接口</h2>
    <p>HTTPS API：<a href="/v1/health">/v1/health</a>。开源客户端与规则位于
      <a href="https://github.com/franka328162810-cell/ics-commitment-audit">GitHub</a>。</p>
    <nav>
      <a href="/privacy">隐私政策草案</a>
      <a href="/terms">服务条款草案</a>
      <a href="mailto:franka328162810@gmail.com">联系</a>
    </nav>
    <p class="muted">运营主体：Xue Zhi Xin (ICS-TEC)。最后更新：2026-11-21。</p>
  </article>`,
);

export const privacyPage = page(
  "隐私政策草案 | ICS Commitment Audit",
  `<article>
    <p class="eyebrow">隐私政策草案</p>
    <h1>我们如何处理数据</h1>
    <p class="notice"><strong>草案提示：</strong>本页是正式收费前的透明说明草案，不构成法律意见，正式商业运营前应由合格律师按实际经营主体、地区与支付方案复核。</p>
    <h2>1. 运营者与联系</h2>
    <p>运营者：Xue Zhi Xin (ICS-TEC)。隐私与删除请求：<a href="mailto:franka328162810@gmail.com">franka328162810@gmail.com</a>。</p>
    <h2>2. 处理的数据</h2>
    <ul>
      <li>用户上传的 TXT、Markdown、DOCX、PDF，以及文件名、大小和内容类型。</li>
      <li>分析生成的承诺、分数、证据位置和报告。</li>
      <li>组织名称、套餐、用量、API Key 的不可逆哈希、前缀、任务状态和错误信息。</li>
      <li>开通付费后产生的支付平台客户、订阅和 Webhook 标识。我们不存储银行卡号或支付验证码。</li>
      <li>保障安全与排障所需的时间、区域、错误和性能日志。</li>
    </ul>
    <h2>3. 处理目的</h2>
    <p>用于执行用户请求的文本分析、生成报告、租户隔离、配额和计费、安全防护、故障排查、支持以及履行法定义务。未经单独同意，不将客户文件用于训练通用 AI 模型，也不出售客户数据。</p>
    <h2>4. 保留与删除</h2>
    <ul>
      <li>原始上传：成功处理或最终失败后立即删除。</li>
      <li>分析报告：默认 7 天后删除；用户可提前删除。</li>
      <li>任务元数据：计划保留 180 天后清理；安全或计费记录可能在法律允许的必要期限内保留。</li>
      <li>删除请求可能受司法、税务、反欺诈或安全保留义务限制。</li>
    </ul>
    <h2>5. 服务商与跨境处理</h2>
    <p>当前基础设施使用 Cloudflare（Workers、D1、R2、Queues、Containers）并在其全球网络中处理数据。启用在线支付后，将使用支付服务商处理交易与账单。正式上线时会列明服务商及必要的跨境安排。</p>
    <h2>6. 安全与控制</h2>
    <p>服务采用 HTTPS、租户隔离、API Key 哈希、私有对象存储、短期报告访问和用量限制。互联网服务不存在绝对安全，用户应保护 API Key，不上传无权处理的机密或高度敏感个人信息。</p>
    <h2>7. 用户权利</h2>
    <p>用户可请求访问、更正、导出或删除与其账户有关的个人数据，并可提出投诉。请使用账户关联邮箱发送请求；为防止冒用，我们可能要求合理验证。</p>
    <h2>8. 儿童与年龄</h2>
    <p>本服务面向机构和成年专业用户，不面向未成年人，也不得用于上传未成年人的敏感个人信息。</p>
    <h2>9. 更新</h2>
    <p>重大变更将通过服务页面或账户联系渠道提示。收费正式启用前，本草案将被替换为经审查的正式版本。</p>
    <nav><a href="/">返回首页</a><a href="/terms">服务条款草案</a></nav>
  </article>`,
);

export const termsPage = page(
  "服务条款草案 | ICS Commitment Audit",
  `<article>
    <p class="eyebrow">服务条款草案</p>
    <h1>使用本服务前请阅读</h1>
    <p class="notice"><strong>草案提示：</strong>本页不构成法律意见。正式收费、订阅、退款和责任条款须在经营主体与支付方案确定后由合格律师复核。</p>
    <h2>1. 服务范围</h2>
    <p>ICS Commitment Audit 对用户提交的承诺文本做结构化抽取、评分和证据定位。结果可能不完整或存在误判，必须由用户结合原文复核。</p>
    <h2>2. 不提供专业鉴证</h2>
    <p>本服务不是审计、鉴证、法律、税务、投资或合规认证服务，不构成对“漂绿”、违法或重大性的事实认定。用户不得把结果作为唯一决策依据，也不得对外声称获得 ICS-TEC 或第三方的认证。</p>
    <h2>3. 账户与 API Key</h2>
    <p>用户应提供真实、必要的账户信息，妥善保管 API Key，并对该凭据下发生的活动负责。发现泄露应立即停用并联系我们。一个组织的额度和报告不得用于规避租户限制。</p>
    <h2>4. 上传内容与授权</h2>
    <p>用户声明其拥有处理上传内容所需的权利和合法基础。不得上传违法内容、无权披露的商业秘密、支付凭证、身份证件、医疗记录或其他与承诺分析无关的高度敏感个人信息。用户授予的服务处理许可仅限于完成请求、安全和依法履约所必需的范围。</p>
    <h2>5. 可接受使用</h2>
    <p>不得攻击、绕过配额、探测其他租户、传播恶意文件、自动生成误导性审计结论、侵犯知识产权或违反适用法律。我们可暂停高风险账户并保留依法报告的权利。</p>
    <h2>6. 试用与付费</h2>
    <p>试用额度、价格、计费周期、取消和退款将在购买页面或订单中明确。当前在线支付尚未启用。订阅取消后，已产生费用和依法应退款项按订单、适用消费者保护规则及正式条款处理。</p>
    <h2>7. 可用性与变更</h2>
    <p>除非另签书面 SLA，本服务按“现状”和“可用”基础提供。我们会采取合理措施维护安全与连续性，但不保证服务永不中断。可能为安全、法律、维护或产品改进限制或更新功能。</p>
    <h2>8. 知识产权</h2>
    <p>开源代码适用仓库中的 Apache License 2.0；形式化材料适用其标注的 CC BY-SA 4.0。托管服务、品牌和用户文件的权利仍归各自权利人。用户保留其上传内容的权利。</p>
    <h2>9. 责任限制</h2>
    <p>在适用法律允许的最大范围内，ICS-TEC 不对因完全依赖自动分析、用户上传侵权内容或用户违反条款造成的间接损失承担责任。最终责任上限与例外将在正式条款中明确，不得排除法律禁止排除的责任。</p>
    <h2>10. 终止与联系</h2>
    <p>用户可停止使用并请求删除。严重违法、安全风险或未付款可能导致暂停或终止。联系：<a href="mailto:franka328162810@gmail.com">franka328162810@gmail.com</a>。</p>
    <nav><a href="/">返回首页</a><a href="/privacy">隐私政策草案</a></nav>
  </article>`,
);

export function htmlResponse(body: string, status = 200): Response {
  return new Response(body, {
    status,
    headers: {
      "content-type": "text/html; charset=utf-8",
      "cache-control": "public, max-age=300",
      "x-content-type-options": "nosniff",
      "referrer-policy": "no-referrer",
      "content-security-policy":
        "default-src 'none'; style-src 'unsafe-inline'; base-uri 'none'; frame-ancestors 'none'; form-action 'none'",
    },
  });
}
