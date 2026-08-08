# 17 段要求核对

`rules-contract.json` 是机器可读的唯一契约。CI 会逐条比较以下 17 段的标题、
规则、策略、参数和顺序；少一条、多一条或换位置都会失败。

| 序号 | 要求 | 实现与校验 |
| ---: | --- | --- |
| 1 | Google Voice、STUN、MTProto、LAN | Google Voice 的 2 条页面/控制域进入 `GoogleVoice-Control`，1 条 STUN 域和 `google-voice-media-rules.conf` 的 5 条 Workspace 官方 UDP 媒体规则进入 `GoogleVoice-Media`，全部先于全局 STUN 拦截；MTProto、SKK 非 IP LAN 和内建 `LAN,DIRECT,no-resolve` 保留 |
| 2 | 特殊服务最优先 | Bilibili 的 3 个精确视频 CDN 后缀固定到 `DIRECT`；仅恢复淘宝/天猫品牌 mini-app 的 1 个运行时后缀；随后是 Polymarket 的 4 个精确目标，全部位于共享 Reject/CDN 规则之前 |
| 3 | iCloud Private Relay | SKK DOMAIN-SET 固定到 `Apple` |
| 4 | Apple Intelligence / Siri / PCC | `apple-ai.conf` 固定到 `AIGC` |
| 5 | 中国大陆银行 | `direct-cn.conf`，24 条，`DIRECT`；跨地区的 `bankofchina.com` 与宽泛 `.icbc.com` 不在此强制直连 |
| 6 | 分地区金融 | HK 41、SG 21、JP 15、KR 10、UK 20，策略逐一固定 |
| 7 | 美国住宅出口 | `us-residential.conf`，119 条；包括 Apple Cash/Pay、美国第一方金融、PayPal 及 4 个明确启用的美国身份/清算服务 |
| 8 | 跨地区金融、身份与风控 | Finance 67、Identity 20、Risk 8；顺序固定为 Finance → Identity → Risk |
| 9 | 中心化交易所 | `bybit.conf` 2 条先补齐 Bybit 已证实 App/API 域，再加载 `crypto.conf` 14 条，统一使用 `Crypto` |
| 10 | Web3 | `web3.conf`，168 条有效语义，`Web3` |
| 11 | Apple Push 与剩余系统服务 | APNs 的 3 个精确域/CNAME 及 `apple-push-rules.conf` 中 Apple 公开网段上的 9 条 TCP 5223 规则先进入 `Apple-Push`；其后保留 `RULE-SET,SYSTEM,DIRECT` |
| 12 | 广告和恶意域名 | reject-drop 不使用 `pre-matching`，保证前置业务规则优先；随后为 reject DOMAIN-SET → 精简补集 → reject → reject-no-drop |
| 13 | 服务专用 | Emby、Telegram、GitHub API 精确例外、AIGC 与聚合 Streaming；删除 cr18 关键词与冗余 stream_us |
| 14 | Apple / Microsoft | Apple CDN 改用有效的 `domainset/apple_cdn.conf`；其余 4 个资源按上游示例参数加载 |
| 15 | 下载和 CDN | Speedtest、两组 Download、两组 CDN 全部保留 |
| 16 | 国内和海外基础规则 | Domestic、WeChat、Direct、Global，顺序固定 |
| 17 | IP 类与 FINAL | Telegram 位于通用 Reject IP 之前；随后是 Streaming、Domestic、China IP，均不覆盖上游内部解析语义；FINAL 最后 |

## 活动本仓库规则文件

| 文件 | 类型 | 策略 |
| --- | --- | --- |
| `google-voice.conf` | `DOMAIN-SET` | `GoogleVoice-Control` |
| `google-voice-media.conf` | `DOMAIN-SET` | `GoogleVoice-Media` |
| `google-voice-media-rules.conf` | `RULE-SET` | `GoogleVoice-Media` |
| `bilibili-direct.conf` | `DOMAIN-SET` | `DIRECT` |
| `taobao-functional.conf` | `DOMAIN-SET` | `DIRECT` |
| `polymarket.conf` | `DOMAIN-SET` | `Res-Frontier` |
| `apple-ai.conf` | `DOMAIN-SET` | `AIGC` |
| `direct-cn.conf` | `DOMAIN-SET` | `DIRECT` |
| `hk-finance.conf` | `DOMAIN-SET` | `HK-FINANCE` |
| `sg-finance.conf` | `DOMAIN-SET` | `SG-FINANCE` |
| `jp-finance.conf` | `DOMAIN-SET` | `JP-FINANCE` |
| `kr-finance.conf` | `DOMAIN-SET` | `KR-FINANCE` |
| `uk-finance.conf` | `DOMAIN-SET` | `UK-FINANCE` |
| `us-residential.conf` | `DOMAIN-SET` | `Res-Frontier` |
| `finance-context.conf` | `DOMAIN-SET` | `Finance` |
| `identity-context.conf` | `DOMAIN-SET` | `Identity` |
| `risk-context.conf` | `DOMAIN-SET` | `Identity` |
| `bybit.conf` | `DOMAIN-SET` | `Crypto` |
| `crypto.conf` | `DOMAIN-SET` | `Crypto` |
| `web3.conf` | `DOMAIN-SET` | `Web3` |
| `apple-push.conf` | `DOMAIN-SET` | `Apple-Push` |
| `apple-push-rules.conf` | `RULE-SET` | `Apple-Push` |
| `adblock4limbo-supplement.conf` | `DOMAIN-SET` | `REJECT` |

## 精准性约束

CI 还会拒绝重复、父子后缀冗余、跨策略覆盖、错策略、漏引用、过宽共享后缀、
共享验证基础设施被整域绑定到敏感策略、外部 RULE-SET 内嵌策略列，以及归档文件被活动 Rule 引用。

Identity 与 Risk 的 28 条共享服务严格限定为两个指定文件及 `Identity` 策略；
校验器会拒绝把这些豁免复制到其他文件或策略。美国住宅文件中的
`.apexclearing.com`、`.earlywarning.com`、`.id.me`、`.login.gov` 同样使用
“文件 + 策略 + 域名”三重限定。

`api.github.com` 在 SKK `ai.conf` 前精确进入 `PROXY`，避免普通 GitHub API
请求被 AIGC 接管。活动主 Rule 不再包含 `DOMAIN-KEYWORD`。

Bilibili 前置文件只包含 `bilivideo` 媒体 CDN 后缀，不包含 BiliUniverse Global
执行脚本、MITM 和动态地区策略所需的 `bilibili.com` / `biliapi.net` API 主机。
CI 会实时下载官方最新 Surge 模块并检查两者没有交集。
