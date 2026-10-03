# Domain source notes

本页记录新增或调整的金融域名。活动规则优先收录机构第一方域名及有证据的专属资源；
登记册用于确认机构身份，具体主机以机构官网为最终依据。金融表格核对日期：2026-07-30；Capital One/Equifax 与 Polymarket 补充核对日期：2026-08-20；FUTU/Moomoo 地区复核日期：2026-08-24。

## MEXC 当前归属：日本单一出口（2026-10-03）

按所有者最新选择，MEXC 只使用日本，不创建日韩自动策略组。将下节已确认的
全部 32 条记录从 `hk-finance.conf` 原样移入现有 `jp-finance.conf`，复用其
`Japan,extended-matching` 绑定，不改其他香港业务或共享身份/风控资源。
本次没有可靠的节点延迟对比，不能把日本描述为实测更快；也未验收登录、KYC、
交易或 iPhone 原生链路。[MEXC 用户协议](https://www.mexc.com/terms)于本次核查时
将香港列为禁止服务地区。路由选择不改变用户实际居住地或账户/KYC 资格，不保证
地区提醒消失，也不能作为虚报地区的依据。

## MEXC 域名补齐与历史香港迁移（2026-10-02）

按当时要求，`crypto.conf` 的 15 条既有 MEXC 后缀与精确资源全部迁入
`hk-finance.conf`，复用现有 `Hong Kong,extended-matching`，不增加订阅或策略组。
此为历史归属，当前以以上 2026-10-03 日本选择为准。旧 CH 文件继续为空。
当时再补以下 17 条，现共 32 条 MEXC 记录，来源与精确边界继续保留：

- `download.mocortech.com`：官方 [App/Web 帮助](https://www.mexc.com/support/app-web)
  明确 APK 下载域；[Lite App 安装说明](https://www.mexc.com/announcements/article/how-to-use-mexc-via-lite-app-17827791527902)
  给出该主机的完整下载路径。保持精确主机匹配。
- `.mexc.link`、`.mexc.cg`、`.mexc.ci`、`.mexc.sg`：2026-09-21
  [官方邮件域说明](https://www.mexc.com/learn/article/why-am-i-unable-to-receive-email-notifications-from-mexc-/1)
  第 2.3 节确认。这是域内链接/资源的覆盖，不改变邮件服务端发送或用户邮箱的接收路线。
- `.mexc.me`、`.mexc.cc`、`.mexc.kr`、`.mexc.io`、`.mexc.ch`、`.mexc.biz.tr`、
  `.mexc.us`：[当前官网加载的短链代码](https://static.mocortech.com/production/web-v4-home-seo/65/_next/static/chunks/3eoba6hvcooe6.js)
  明确将这些品牌命名空间列入 `MEVENT` 短链生成器认可清单。记录其路由归属，
  未声称各镜像当前都可访问；同一清单中的非品牌域及内网样例未扩大收录。
- `watchman-sdk.gotoda.co`、`watchman.gotoda.co`：[当前官方下载页](https://www.mexc.co/download)
  加载 [SDK](https://watchman-sdk.gotoda.co/watchman.umd.js)，初始化为
  `appid=mxc-web-home-seo-v4`、`env=prod`；SDK 的生产收集端是后者。
- `trochilus-web.gotoda.co`、`trochi.gotoda.co`：同一页面加载
  [监测 SDK](https://trochilus-web.gotoda.co/trochilus-web-sdk-integration.js)，代码明确配置
  后者为收集端，并读取 `mexc_session_uid`。
- `e.gotoda.co`：[当前官网遥测代码](https://static.mocortech.com/production/web-v4-home-seo/65/_next/static/chunks/2oxkfm83sb7ji.js)
  定义该精确主机为 `PUBLIC_DEPLOY_STAGE=online` 的目标，应用名同为
  `mxc-web-home-seo-v4`。作为已确认的生产目标纳入覆盖；本轮未取得页面实际
  `PUBLIC_DEPLOY_STAGE` 值，也未把它说成已观察到的设备请求。

官网、现货/合约 API、WebSocket、帮助中心和 `app.mexc.com` 等被既有 `.mexc.com`
覆盖。已迁入的 `static/public/customer-article/learn.mocortech.com`、四个精确 S3
bucket、OneLink 与 GitHub 文档主机全部保留原边界。
不扩大到 `mocortech.com`、`gotoda.co`、AWS 等共享根域；测试环境、NEL 错误报告
候选及通用第三方平台未加入。共享 KYC/身份核验维持现有策略，不能仅靠静态主机名
按调用 App 自动跟随 MEXC 的指定地区；主机匹配测试不代表登录/交易全链路实测。

## OKX 美国住宅归属

2026-10-01，按所有者要求，OKX 统一使用既有 `us-residential.conf` 的
`Res-Frontier,extended-matching` 绑定。迁移正式订阅原有的 7 条后缀
`.okx.com`、`.okex.com`、`.okx-dns.com`、`.okx-dns1.com`、`.okx-dns2.com`、
`.okx.ac`、`.okx.cab`，从 `crypto.conf` 删除同一批条目，不改变其他交易所。
旧域和 DNS 备用域为保留原有覆盖范围，不代表本轮证实它们仍是当前 App 必需请求。

- [官方 API 文档](https://app.okx.com/docs-v5/en/) 明确列出美国 REST
  `us.okx.com`、生产 WebSocket `wsus.okx.com`、模拟 WebSocket `wsuspap.okx.com`。
  它们与官网、`app.okx.com`、`web3.okx.com` 钱包入口、`static.okx.com`
  一起被 `.okx.com` 覆盖，无须重复增加子域规则。
- [官方登录页](https://www.okx.com/account/login) 与
  [美国站首页](https://www.okx.com/en-us) 的 HTML 启动配置确认
  `languageCdnUrl` 使用 `static.coinall.ltd`，`cdnBackupList` 使用
  `static.jingyunyilian.com`，`cdnDomainMap` 包含 `static.okx.reise`。
  只新增这三个精确主机，不扩大到供应商整个根域。
- 同一 `cdnDomainMap` 的 `static.okx.ac`、`static.okx.cab` 已由迁入的既有
  后缀覆盖。美国站默认 CDN 为已覆盖的 `static.okx.com`；其他项是语言、备用
  或地区资源，并非声称美国出口每次都会访问。
- [官方改名公告](https://www.okx.com/en-us/learn/okex-rebrands-to-okx) 支持
  OKEx 的历史品牌关系；未新增缺少一手依据的 `okxcdn.com`、`okxstatic.com`
  或 `okxwallet.com`。Okcoin 是独立旧平台，不作为 OKX 当前登录依赖添加。
  OKLink 独立浏览器继续保持 `web3.conf` / `Web3`，不因品牌关系自动迁移。

不增加 Auth0、AWS、Cloudflare、Google 登录或其他共享供应商的整域规则。
主配置、节点、模块、MITM、DNS 和 Apple/iCloud 参数不变。静态首命中及边界测试
不等于登录后的原生 App 全链路实测，也不保证平台账号或地区资格。

## Trading 212 英国归属

2026-09-27，按配置所有者要求，将以下两条加入既有 `uk-finance.conf`，复用
`United Kingdom,extended-matching`，不新增资源引用或策略组。原列表没有 Trading 212
专项，不从其他金融地区列表复制，也不为已被根域覆盖的子域另加重复条目。

- `.trading212.com`：覆盖官网、App/Web 登录及 API、帮助中心、社区和该命名空间下
  的资源。官方 [API 文档](https://docs.trading212.com/api/accounts) 明确列出
  `live.trading212.com` 与 `demo.trading212.com`；
  [密码帮助](https://helpcentre.trading212.com/hc/en-us/articles/360007430797-How-do-I-change-my-password)
  同时确认 `info.trading212.com`。
- `.t212.cc`：Trading 212 官方支持短链接；官方工作人员在
  [近期社区回复](https://community.trading212.com/t/new-cashback-terms-is-absurd/92518/11)
  将 `t212.cc/ask` 列为客服入口。

只修改已证实的首方命名空间。不将 Apple/Google 登录、共享身份核验、整个 CDN 或
深链供应商归入英国。首命中测试是静态规则验收，不等于原生 App 全链路实测；
英国出口也不保证平台接受代理，见官方 [Access Denied 说明](https://helpcentre.trading212.com/hc/en-us/articles/32239787777437-Why-am-I-seeing-Access-Denied-Message)。

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

MEXC 的历史迁移顺序为 UK → CH → Crypto → Hong Kong；2026-10-03 最新选择为日本，
32 条有证据的品牌与精确资源整体归 `jp-finance.conf`，见本页最上方说明。旧 CH 引用继续退休，旧文件
仅保留注释兼容入口；共享身份核验维持原有策略。静态规则验收不等于原生 App
登录、交易或身份核验全链路实测。
N26、Loqbox、Kraken/Krak、Monzo、Lloyds 沿用现有 UK 归属；Coinbase/Base、ether.fi、
OnePay、Capital One、Equifax、PayPal、Google Account/Voice、X 与 Polymarket 沿用
美国住宅。重点回归与证据边界见 [完整性验收](routing-completeness.md)。

2026-08 原配置所有者使用 HSBC HK、Futu/Moomoo HK 与 Longbridge HK。它们的部分
App API 使用无法从域名判断地区的共享基础设施，因此这些既有第一方域名已合并到
`hk-finance.conf`，并在通用 `finance-context.conf` 之前固定到 `Hong Kong`。
这是个人账户上下文绑定，不应作为公共香港规则集直接照搬。

2026-09-27 最新要求将 Moomoo 专属域迁至美国住宅，Futubull 与共用 Futu 静态资源仍 HK；
旧的 Moomoo HK 绑定已被覆盖。新增应用及官方来源见
[29 App 照片补充清单](finance-photo-matrix-20260927.md)。

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
