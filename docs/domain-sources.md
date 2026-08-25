# Domain source notes

本页记录 1.3.0 新增或调整的金融域名。活动规则只收录机构第一方域名；
登记册用于确认机构身份，具体主机以机构官网为最终依据。金融表格核对日期：2026-07-30；Capital One/Equifax 与 Polymarket 补充核对日期：2026-08-20；FUTU/Moomoo 地区复核日期：2026-08-24。

## Apple 边界

本仓库不再维护或加载 Apple 自定义域名集。基础分流只使用 Sukka README 明确列出的
`apple_cdn`、`apple_intelligence`、`apple_cn` 与 `apple_services`；软件更新由 Sukka
`download` 与 Apple 公共资源承接。Apple Account、Private Relay、iCloud、证书和
APNs 不设置个人化路由。保留模块所需的 Apple/iCloud 负向 MITM 边界仍由
`module-compatibility.json` 管理，但 MITM 排除不等于新增分流规则。

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
URL 路径选择国家，因此该根域保留在 Finance 语义文件并固定到 `Res-Frontier`，
而 `.boc.cn` 等大陆专用域继续 `DIRECT`。

PayPal 第一方域仍因当前美国账户场景收录在 `us-residential.conf`；Apple Account
本身不再随 PayPal 建立联动规则，而是完全交给 Sukka Apple Services。账户地区、
账单资料和支付服务商验证仍须符合 [Apple 官方要求](https://support.apple.com/en-us/111741)。

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
