# Domain source notes

本页记录 1.3.0 新增或调整的金融域名。活动规则只收录机构第一方域名；
登记册用于确认机构身份，具体主机以机构官网为最终依据。核对日期：2026-07-30。

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

## 无法靠域名自动判断的边界

`bankofchina.com` 的不同国家页面共用一个根域并按路径分区，Surge 域名规则无法按
URL 路径选择国家，因此该根域保留在 Finance 语义文件并固定到 `Res-Frontier`，
而 `.boc.cn` 等大陆专用域继续 `DIRECT`。

Apple Pay 与 PayPal 是跨地区服务。本仓库仅因配置所有者明确使用美国账户而将其
放入 `Res-Frontier`；其他账户地区不应照搬这一选择。

Apple Account 绑定 PayPal 的登录与账单控制面会使用
`account.apple.com`、`appleid.cdn-apple.com`、`idmsa.apple.com`、`gsa.apple.com` 以及
`p*-buy.itunes.apple.com`。配置所有者
的 Surge 会话在 2026-08-09 与 2026-08-11 观察到
`p100-buy.itunes.apple.com` 经 `DIRECT` 返回空 DNS 结果，同时 PayPal 主链经
`Res-Frontier`，形成同一授权流程的出口分裂。由于 `p100-buy` 是完整 DNS 标签，
普通后缀 `.buy.itunes.apple.com` 无法命中；因此使用独立 RULE-SET 中的 5 条精确
`DOMAIN` 与 `DOMAIN-WILDCARD,*-buy.itunes.apple.com`，使登录与动态分片与 PayPal
保持同一住宅出口；
不加入 `.apple.com`、`.itunes.apple.com`、其他 Apple ID 通用域或共享 Braintree
基础设施。美国 Apple Account 当前支持 PayPal，但账户地区、账单资料和支付服务商
验证仍须符合 [Apple 官方要求](https://support.apple.com/en-us/111741)。

当前配置所有者明确使用 HSBC HK、Futu/Moomoo HK 与 Longbridge HK。它们的部分
App API 使用无法从域名判断地区的共享基础设施，因此这些既有第一方域名被移动到
`hk-finance-context.conf` 并在通用 `finance-context.conf` 之前固定到 `Hong Kong`。
这是个人账户上下文绑定，不应作为公共香港规则集直接照搬。
