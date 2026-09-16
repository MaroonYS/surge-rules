# Domain source notes

本页记录新增或调整的金融域名。活动规则优先收录机构第一方域名及有证据的专属资源；
登记册用于确认机构身份，具体主机以机构官网为最终依据。金融表格核对日期：2026-07-30；Capital One/Equifax 与 Polymarket 补充核对日期：2026-08-20；FUTU/Moomoo 地区复核日期：2026-08-24。

## Apple 边界

2026-09-16 按最新要求撤销 Apple Pay/Cash 三条住宅规则和账户/账单六条窄规则，
同时撤销设备的 Private Relay 住宅绑定。用户随后明确原先启用的全部 Sukka 订阅须保留，
因此误删的 Private Relay 官方资源已恢复并改绑 `United States`，Apple 基础层共保留
五个 Sukka 资源；不额外启用其他可选专项。这一澄清取代上一版删除订阅和 9 月 15 日恢复
自定义窄规则的决定，见 [Apple 回归 Sukka](apple-sukka-only.md)。主 Profile 不添加
Apple/iCloud MITM 正项、负项或条件禁用；相关 hostname 仍由保留模块管理。

## LemFi 美国住宅归属

2026-09-15，配置所有者要求 LemFi 相关流量使用美国家宽。此前本仓库活动/历史
域名清单和两份设备 Profile 的显式域名规则没有 LemFi 专项；本次在既有
`us-residential.conf` 增加以下 7 条，以现有 `Res-Frontier,extended-matching`
绑定早于通用 CDN/地区兜底。不改主配置策略、节点、模块或其他 App 的归属。

| 条目 | 匹配边界 | 一手证据 |
| --- | --- | --- |
| `.lemfi.com` | 当前官网及其 API、mobile、asset、support 等子域 | [官网联系页](https://lemfi.com/en-us/contact-us)、[官方 App Store 页面](https://apps.apple.com/us/app/lemfi/id1533066809) |
| `.lemonade.finance` | 历史首方命名空间，包括生产应用/邮箱验证入口与 referral | [官网当前 JS](https://lemfi.com/_nuxt/3oCc-B_K.js) 使用 `referral.lemonade.finance`；[mobile.lemfi.com](https://mobile.lemfi.com/) 的公开源码将生产邮箱验证跳转至 `app.lemonade.finance` |
| `lemfi.onelink.me` | 仅此精确深链租户 | 官网联系页直接链接；[Apple App Site Association](https://lemfi.onelink.me/.well-known/apple-app-site-association) |
| `lemonadefi.app.link` | 仅此精确历史深链租户 | [Apple App Site Association](https://lemonadefi.app.link/.well-known/apple-app-site-association) |
| `lemonadefi-alternate.app.link` | 仅此精确历史深链备用租户 | [Apple App Site Association](https://lemonadefi-alternate.app.link/.well-known/apple-app-site-association) |
| `d1c5a9xrl5sbk8.cloudfront.net` | 仅此精确静态资源分发主机 | 官网联系页 HTML 和当前 JS 直接加载此主机 |
| `lemonadefinancehelp.zendesk.com` | 仅此精确帮助中心租户 | [官方公开帮助中心接口](https://support.lemfi.com/api/v2/help_center/en-us/articles.json?page=1&per_page=100) 中文章 API URL 指向此租户，而页面 URL 指向 `support.lemfi.com` |

三个深链主机的 AASA 均包含同一 iOS App ID
`5NMXKR499R.com.limefinance.Lemonade.ios`；OneLink 同时包含其 App Clip。
只读取公开页面与关联文件，没有访问带验证码/令牌的验证链接或登录账户。
两个后缀会覆盖其现有及未来子域；五个共享服务租户只精确匹配，不覆盖更深子域、
其他租户或整个 `app.link`、`onelink.me`、`cloudfront.net`、`zendesk.com`。
无关保险品牌 `lemonade.com` 明确不在 LemFi 集合。

官网代码也出现 `o4509826029518848.ingest.de.sentry.io`，但目前证据只说明它是网页
错误遥测，不能证明该组织主机只服务 LemFi 或是原生登录/支付必需；本次不为其新增
放行，不改任何共享 Sentry 或 KYC 后缀及既有拒绝规则。原生 App 实际使用的共享
认证/风控主机仍需设备记录，不能把“已确认专属域覆盖”说成运行时全部请求已穷尽。

LemFi 的[官方登录排查说明](https://support.lemfi.com/hc/en-us/articles/45742225517073-I-can-t-log-in-to-my-account)
建议遇到登录问题时确认没有使用 VPN；固定住宅出口只执行用户的路由选择，
不保证平台接受代理，不改变真实居住地、账户资格或安全审查。

## 监管目录

- 香港：[HKMA 认可机构登记册](https://vpr.hkma.gov.hk/eng/regulatory-resources/registers/register-of-ais-and-lros/)
- 新加坡：[MAS Financial Institutions Directory](https://eservices.mas.gov.sg/fid)
- 日本：[金融庁 金融機関情報](https://www.fsa.go.jp/policy/chusho/shihyou.html)

## 第一方官网

| 地区 | 机构 / 用途 | 活动域名 | 第一方来源 |
| --- | --- | --- | --- |
| CN | 中国农业银行别名 | `.95599.cn` | [95599.cn](https://www.95599.cn/) |
| CN | 平安银行（收窄） | `.bank.pingan.com` | [bank.pingan.com](https://bank.pingan.com/) |
| CN | 招商银行别名 | `.cmbchina.com.cn` | [cmbchina.com.cn](https://www.cmbchina.com.cn/) |
| CN | 中国工商银行全球域 | `.icbc.com` | [icbc.com](https://www.icbc.com/) |
| Cross-region | 中国银行全球根域 | `.bankofchina.com` | [bankofchina.com](https://www.bankofchina.com/) |
| HK | 交通银行香港 | `.bankcomm.com.hk` | [bankcomm.com.hk](https://www.bankcomm.com.hk/) |
| HK | 创兴银行 | `.chbank.com` | [chbank.com](https://www.chbank.com/) |
| HK | 集友银行 | `.chiyubank.com` | [chiyubank.com](https://www.chiyubank.com/) |
| HK | 招商永隆银行 | `.cmbwinglungbank.com` | [cmbwinglungbank.com](https://www.cmbwinglungbank.com/) |
| HK | 中信银行（国际） | `.cncbinternational.com` | [cncbinternational.com](https://www.cncbinternational.com/) |
| HK | 南洋商业银行 | `.ncb.com.hk` | [ncb.com.hk](https://www.ncb.com.hk/) |
| HK | 大众银行（香港） | `.publicbank.com.hk` | [publicbank.com.hk](https://www.publicbank.com.hk/) |
| HK | 上海商业银行 | `.shacombank.com.hk` | [shacombank.com.hk](https://www.shacombank.com.hk/) |
| SG | Bank of Singapore | `.bankofsingapore.com` | [bankofsingapore.com](https://www.bankofsingapore.com/) |
| SG | Citibank Singapore | `.citibank.com.sg` | [citibank.com.sg](https://www.citibank.com.sg/) |
| SG | HSBC Singapore | `.hsbc.com.sg` | [hsbc.com.sg](https://www.hsbc.com.sg/) |
| SG | Singapore Exchange | `.sgx.com` | [sgx.com](https://www.sgx.com/) |
| JP | AEON Bank | `.aeonbank.co.jp` | [aeonbank.co.jp](https://www.aeonbank.co.jp/) |
| JP | au Jibun Bank | `.jibunbank.co.jp` | [jibunbank.co.jp](https://www.jibunbank.co.jp/) |
| JP | Resona Bank | `.resonabank.co.jp` | [resonabank.co.jp](https://www.resonabank.co.jp/) |
| JP | SBI Shinsei Bank | `.sbishinseibank.co.jp` | [sbishinseibank.co.jp](https://www.sbishinseibank.co.jp/) |
| JP | SMBC Trust Bank | `.smbctb.co.jp` | [smbctb.co.jp](https://www.smbctb.co.jp/) |
| JP | Seven Bank | `.sevenbank.co.jp` | [sevenbank.co.jp](https://www.sevenbank.co.jp/) |
| KR | K Bank | `.kbanknow.com` | [kbanknow.com](https://www.kbanknow.com/) |
| UK | Atom Bank | `.atombank.co.uk` | [atombank.co.uk](https://www.atombank.co.uk/) |
| UK | Bank of Scotland | `.bankofscotland.co.uk` | [bankofscotland.co.uk](https://www.bankofscotland.co.uk/) |
| UK | Co-operative Bank | `.co-operativebank.co.uk` | [co-operativebank.co.uk](https://www.co-operativebank.co.uk/) |
| UK | Metro Bank | `.metrobankonline.co.uk` | [metrobankonline.co.uk](https://www.metrobankonline.co.uk/) |
| US | Cadence Bank | `.cadencebank.com` | [cadencebank.com](https://cadencebank.com/) |
| US | East West Bank | `.eastwestbank.com` | [eastwestbank.com](https://www.eastwestbank.com/) |
| US | First Horizon | `.firsthorizon.com` | [firsthorizon.com](https://www.firsthorizon.com/) |
| US | Flagstar Bank | `.flagstar.com` | [flagstar.com](https://www.flagstar.com/) |
| US | Frost Bank | `.frostbank.com` | [frostbank.com](https://www.frostbank.com/) |
| US | Old National Bank | `.oldnational.com` | [oldnational.com](https://www.oldnational.com/) |
| US | Bank OZK | `.ozk.com` | [ozk.com](https://www.ozk.com/) |
| US | Synovus | `.synovus.com` | [synovus.com](https://www.synovus.com/) |
| US | Umpqua Bank | `.umpquabank.com` | [umpquabank.com](https://www.umpquabank.com/) |
| US | Webster Bank | `.websterbank.com` | [websterbank.com](https://www.websterbank.com/) |
| US | Zions Bank | `.zionsbank.com` | [zionsbank.com](https://www.zionsbank.com/) |
| US | Apex Clearing | `.apexclearing.com` | [apexclearing.com](https://www.apexclearing.com/) |
| US | Early Warning | `.earlywarning.com` | [earlywarning.com](https://www.earlywarning.com/) |
| US | ID.me | `.id.me` | [id.me](https://www.id.me/) |
| US | Login.gov | `.login.gov` | [login.gov](https://www.login.gov/) |
| US | Capital One Medallia 租户 | `capitalone.md-apis.medallia.com`、`capitalone-resources.digital-cloud.medallia.com` | [Medallia API hosts](https://docs.medallia.com/en/medallia-experience-cloud/integration/apis/api-hosts)；用户 Surge 会话实测 |
| US | myEquifax 消费者门户 | `.myequifax.com` | [Equifax 官方发布](https://investor.equifax.com/news-events/press-releases/detail/101/equifax-launches-core-credit) |

## 无法靠域名自动判断的边界

`bankofchina.com` 的不同国家页面共用一个根域并按路径分区，Surge 域名规则无法按
URL 路径选择国家。2026-09-16 配置所有者明确要求中国银行整体直连，因此该根域从
Finance 迁至 `direct-cn.conf`，连同 `.boc.cn` 固定 `DIRECT`；全球共用站点也受此
个人选择影响，独立的中银香港 `.bochk.com` 仍为 HK。本次新增来源与 24 App 归属见
[个人地区清单](finance-app-matrix.md)。

PayPal 第一方域仍因当前美国账户场景收录在 `us-residential.conf`；Apple Account
与账单已撤销额外住宅绑定，按 Sukka 公共资源分流，不保证与 PayPal 同一出口。账户地区、
账单资料和支付服务商验证仍须符合 [Apple 官方要求](https://support.apple.com/en-us/111741)。

## 2026-09 重点业务与共享身份边界

MEXC 的 15 条第一方/专属资源已从 UK 移至 `ch-finance.conf`，现统一将 CH 登记到
manifest、主骨架、契约与展开版；本轮不新增 MEXC 共享 KYC 或遥测放行。
N26、Loqbox、Kraken/Krak、Monzo、Lloyds 沿用现有 UK 归属；Coinbase/Base、ether.fi、
OnePay、Capital One、Equifax、PayPal、Google Account/Voice、X 与 Polymarket 沿用
美国住宅。重点回归与证据边界见 [完整性验收](routing-completeness.md)。

当前配置所有者明确使用 HSBC HK、Futu/Moomoo HK 与 Longbridge HK。它们的部分
App API 使用无法从域名判断地区的共享基础设施，因此这些既有第一方域名已合并到
`hk-finance.conf`，并在通用 `finance-context.conf` 之前固定到 `Hong Kong`。
这是个人账户上下文绑定，不应作为公共香港规则集直接照搬。

FUTU HK 官方下载页当前加载的前端包将 `futuhk8.com`、`futuhongkong.com` 与
`futunh.com` 列入开户、登录、资金及账户管理兼容域，因此只补入这三个可验证后缀。
`futuau.com` 属澳洲业务，不固定香港；`moomootrustee.com` 对应新加坡实体，归入
`sg-finance.conf`。没有官方页面或 iPhone 失败日志证明的数字域名、通用 Tencent
Cloud 网段及裸 IP 均不作为兜底加入，避免把其他 App 的共享云流量误送香港。
[FUTU HK 官方前端包](https://static.futunn.com/futuhk_common/dist/futuhkHeadFoot-d147c85d53fba81cc550.js)
与 [Moomoo 持牌实体列表](https://www.moomoo.com/sg/licensedentities) 用于这次地区核对。

## X 的当前第一方命名空间

- X 官方 API 文档使用 `api.x.com`，官方帮助文档分别确认
  [`t.co` 链接缩短](https://help.x.com/en/using-x/url-shortener)、
  [`twimg.com` 媒体](https://help.x.com/en/using-x/x-videos) 以及
  [X Live / Periscope](https://help.x.com/en/using-x/periscope-faq) 的现行关系。
  因此 `us-residential.conf` 中的 X 小节只收录 `.x.com`、`.twitter.com`、`.t.co`、
  `.twimg.com`、`.pscp.tv`、`.periscope.tv`，不猜测 `xpayments.com`
  或共享第三方 KYC/银行联接域。
- [X Money FAQ](https://money.x.com/en/i/faq) 明确要求真实美国居民、
  已验证美国手机号和身份验证。路由绑定只用于稳定出口，不代替开户资格。
## Polymarket 产品边界

- [Polymarket 官方地域说明](https://help.polymarket.com/en/articles/13364163-geographic-restrictions)
  明确国际 `.com` 会按请求 IP 执行地域限制；美国用户使用的是独立 `.us` 产品。
- `.polymarket.com`、精确 Auth0 租户、上传主机与 `.polymarket.us` 仍按产品边界维护，
  但已合并进 `us-residential.conf` 并统一固定 `Res-Frontier` 家宽。路由只保持出口稳定，
  不改变真实地区及账户资格，也不用于绕过限制。
