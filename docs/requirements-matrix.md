# 17 段要求核对

`rules-contract.json` 是机器可读的唯一契约。CI 会逐条比较以下 17 段的标题、
规则、策略、参数和顺序；少一条、多一条或换位置都会失败。

| 序号 | 要求 | 实现与校验 |
| ---: | --- | --- |
| 1 | NTP、X、Google Account、Google Voice、STUN、MTProto、Telegram、LAN | NTP/UDP 123 先固定 `DIRECT`；X 的 6 个第一方后缀随后固定 `Res-Frontier`；Google Account 的 6 个精确登录/管理/OAuth 主机在 Google Voice 之前固定 `Res-Frontier`；Google Voice 的页面/控制域固定 `Res-Frontier`，5 个 STUN 主机和 5 条 Workspace 官方 UDP 媒体规则固定 `DIRECT`，全部先于全局 STUN 拦截；MTProto 与 Telegram 非 IP 规则固定 `Singapore` 并先于广告栈，随后保留 SKK 非 IP LAN 和内建 `LAN,DIRECT,no-resolve` |
| 2 | 特殊服务最优先 | Bilibili 的 3 个精确视频 CDN 后缀固定到 `DIRECT`；仅恢复淘宝/天猫品牌 mini-app 的 1 个运行时后缀；随后是 Polymarket 的 4 个精确目标，全部位于共享 Reject/CDN 规则之前 |
| 3 | iCloud Private Relay | SKK DOMAIN-SET 固定到普通 `United States` 节点，不使用住宅 SOCKS5 |
| 4 | Apple Intelligence / Siri / PCC | `apple-ai.conf` 固定到 `United States` |
| 5 | 中国大陆银行 | `direct-cn.conf`，24 条，`DIRECT`；跨地区的 `bankofchina.com` 与宽泛 `.icbc.com` 不在此强制直连 |
| 6 | 分地区金融 | HK 第一方 41、当前账户香港共享上下文 26、SG 21、JP 15、KR 10、UK 20，策略逐一固定；香港上下文覆盖 HSBC HK、Futu/Moomoo HK 与 Longbridge HK |
| 7 | 美国住宅出口 | `apple-account-payment-rules.conf` 以 6 条规则覆盖 4 个精确 Apple Account 登录控制主机、账单根域及动态 `*-buy` 分片族；随后 `us-residential.conf` 119 条覆盖 Apple Cash/Pay、美国第一方金融、PayPal 及 4 个明确启用的美国身份/清算服务 |
| 8 | 跨地区金融、身份与风控 | Finance 41、Identity 21、Risk 8；语义顺序固定为 Finance → Identity → Risk，Finance 运行时固定 `Res-Frontier`，Identity/Risk 统一进入手动 `Verification` 组；默认延续美国住宅出口，并允许 Bybit/Crypto/Web3 与港、新、日、韩、英地区上下文；iOS 可用粘性 App-open 自动化切换，但共享域仍不能可靠识别调用 App |
| 9 | 中心化交易所 | `bybit.conf` 2 条先补齐 Bybit 已证实 App/API 域并进入独立受支持地区 `Bybit`；Gate 的 3 个当前官网/API 后缀单独 `REJECT`，因当前全部可选地区均受限；其余 `crypto.conf` 13 条进入 `Crypto` |
| 10 | Web3 | `web3.conf`，169 条有效语义，`Web3` |
| 11 | Apple Push 与剩余系统服务 | APNs 的 3 个精确域/CNAME 及 10 条 TCP 5223 规则先固定到 `United States`；其后保留 `RULE-SET,SYSTEM,DIRECT` |
| 12 | 广告和恶意域名 | reject-drop 不使用 `pre-matching`，保证前置业务规则优先；随后为 reject DOMAIN-SET → 精简补集 → reject → reject-no-drop |
| 13 | 服务专用 | Emby 固定 `Singapore`，GitHub API 精确例外进入 `PROXY`，AI 与聚合 Streaming 固定 `United States`；Telegram 非 IP 已前移到第 1 段 |
| 14 | Apple / Microsoft | Apple/Microsoft CDN 保持 `DIRECT`；其余 Apple/Microsoft 服务固定 `United States` |
| 15 | 下载和 CDN | Speedtest/CDN 使用 `PROXY`，两组 Download 固定 `Hong Kong` |
| 16 | 国内和海外基础规则 | Domestic、WeChat、Direct、Global，顺序固定 |
| 17 | IP 类与 FINAL | Telegram 位于通用 Reject IP 之前；随后是 Streaming、Domestic、China IP，均不覆盖上游内部解析语义；FINAL 最后 |

## 活动本仓库规则文件

| 文件 | 类型 | 策略 |
| --- | --- | --- |
| `x-residential.conf` | `DOMAIN-SET` | `Res-Frontier` |
| `google-account.conf` | `DOMAIN-SET` | `Res-Frontier` |
| `google-voice.conf` | `DOMAIN-SET` | `Res-Frontier` |
| `google-voice-media.conf` | `DOMAIN-SET` | `DIRECT` |
| `google-voice-media-rules.conf` | `RULE-SET` | `DIRECT` |
| `bilibili-direct.conf` | `DOMAIN-SET` | `DIRECT` |
| `taobao-functional.conf` | `DOMAIN-SET` | `DIRECT` |
| `polymarket.conf` | `DOMAIN-SET` | `Res-Frontier` |
| `apple-ai.conf` | `DOMAIN-SET` | `United States` |
| `direct-cn.conf` | `DOMAIN-SET` | `DIRECT` |
| `hk-finance.conf` | `DOMAIN-SET` | `Hong Kong` |
| `hk-finance-context.conf` | `DOMAIN-SET` | `Hong Kong` |
| `sg-finance.conf` | `DOMAIN-SET` | `Singapore` |
| `jp-finance.conf` | `DOMAIN-SET` | `Japan` |
| `kr-finance.conf` | `DOMAIN-SET` | `Korea` |
| `uk-finance.conf` | `DOMAIN-SET` | `United Kingdom` |
| `apple-account-payment-rules.conf` | `RULE-SET` | `Res-Frontier` |
| `us-residential.conf` | `DOMAIN-SET` | `Res-Frontier` |
| `finance-context.conf` | `DOMAIN-SET` | `Res-Frontier`（语义角色 `Finance`） |
| `identity-context.conf` | `DOMAIN-SET` | `Verification`（语义角色 `Identity`） |
| `risk-context.conf` | `DOMAIN-SET` | `Verification`（语义角色 `Risk`） |
| `bybit.conf` | `DOMAIN-SET` | `Bybit` |
| `gate.conf` | `DOMAIN-SET` | `REJECT` |
| `crypto.conf` | `DOMAIN-SET` | `Crypto` |
| `web3.conf` | `DOMAIN-SET` | `Web3` |
| `apple-push.conf` | `DOMAIN-SET` | `United States` |
| `apple-push-rules.conf` | `RULE-SET` | `United States` |
| `adblock4limbo-supplement.conf` | `DOMAIN-SET` | `REJECT` |

## 精准性约束

CI 还会拒绝重复、父子后缀冗余、跨策略覆盖、错策略、漏引用、过宽共享后缀、
共享验证基础设施被整域绑定到敏感策略、外部 RULE-SET 内嵌策略列，以及归档文件被活动 Rule 引用。

Identity 与 Risk 的 29 条共享服务严格限定为两个指定文件及各自语义角色；
校验器会拒绝把这些豁免复制到其他文件或策略。美国住宅文件中的
`.apexclearing.com`、`.earlywarning.com`、`.id.me`、`.login.gov` 同样使用
“文件 + 策略 + 域名”三重限定。

`api.github.com` 在 SKK `ai.conf` 前精确进入 `PROXY`，避免普通 GitHub API
请求被聚合 AI 规则接管。活动主 Rule 不再包含 `DOMAIN-KEYWORD`。

Bilibili 前置文件只包含 `bilivideo` 媒体 CDN 后缀，不包含 BiliUniverse Global
执行脚本、MITM 和动态地区策略所需的 `bilibili.com` / `biliapi.net` API 主机。
CI 会实时下载官方最新 Surge 模块并检查两者没有交集。
