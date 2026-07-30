# 17 段要求核对

`rules-contract.json` 是机器可读的唯一契约。CI 会逐条比较以下 17 段的标题、
规则、策略、参数和顺序；少一条、多一条或换位置都会失败。

| 序号 | 要求 | 实现与校验 |
| ---: | --- | --- |
| 1 | STUN、MTProto、LAN | 4 条全部保留；补充 SKK 非 IP LAN，内建 LAN 保持 `DIRECT,no-resolve` |
| 2 | Polymarket 最优先 | 3 个精确目标放入 `polymarket.conf`，不再宽泛匹配关键词 |
| 3 | iCloud Private Relay | SKK DOMAIN-SET 固定到 `Apple` |
| 4 | Apple Intelligence / Siri / PCC | `apple-ai.conf` 固定到 `AIGC` |
| 5 | 中国大陆银行 | `direct-cn.conf`，24 条，`DIRECT`；跨地区的 `bankofchina.com` 与宽泛 `.icbc.com` 不在此强制直连 |
| 6 | 分地区金融 | HK 28、SG 15、JP 14、KR 10、UK 18，策略逐一固定 |
| 7 | 美国住宅出口 | `us-residential.conf`，119 条；包括 Apple Cash/Pay、美国第一方金融、PayPal 及 4 个明确启用的美国身份/清算服务 |
| 8 | 跨地区金融、身份与风控 | Finance 27、Identity 21、Risk 15；顺序固定为 Finance → Identity → Risk |
| 9 | 中心化交易所 | `crypto.conf`，15 条，`Crypto` |
| 10 | Web3 | `web3.conf`，168 条有效语义，`Web3` |
| 11 | 剩余系统服务 | `RULE-SET,SYSTEM,DIRECT` |
| 12 | 广告和恶意域名 | reject-drop 不使用 `pre-matching`，保证前置业务规则优先；随后为 reject DOMAIN-SET → 精简补集 → reject → reject-no-drop |
| 13 | 服务专用 | Emby、Telegram、GitHub API 精确例外、AIGC 与聚合 Streaming；删除 cr18 关键词与冗余 stream_us |
| 14 | Apple / Microsoft | Apple CDN 改用有效的 `domainset/apple_cdn.conf`；其余 4 个资源按上游示例参数加载 |
| 15 | 下载和 CDN | Speedtest、两组 Download、两组 CDN 全部保留 |
| 16 | 国内和海外基础规则 | Domestic、WeChat、Direct、Global，顺序固定 |
| 17 | IP 类与 FINAL | Reject、Telegram、Streaming、Domestic、China IP 不覆盖上游内部解析语义；FINAL 最后 |

## 活动 DOMAIN-SET

| 文件 | 策略 |
| --- | --- |
| `polymarket.conf` | `Res-Frontier` |
| `apple-ai.conf` | `AIGC` |
| `direct-cn.conf` | `DIRECT` |
| `hk-finance.conf` | `HK-FINANCE` |
| `sg-finance.conf` | `SG-FINANCE` |
| `jp-finance.conf` | `JP-FINANCE` |
| `kr-finance.conf` | `KR-FINANCE` |
| `uk-finance.conf` | `UK-FINANCE` |
| `us-residential.conf` | `Res-Frontier` |
| `finance-context.conf` | `Finance` |
| `identity-context.conf` | `Identity` |
| `risk-context.conf` | `Identity` |
| `crypto.conf` | `Crypto` |
| `web3.conf` | `Web3` |
| `adblock4limbo-supplement.conf` | `REJECT` |

## 精准性约束

CI 还会拒绝重复、父子后缀冗余、跨策略覆盖、错策略、漏引用、过宽共享后缀、
共享验证基础设施被整域绑定到敏感策略、外部 RULE-SET 内嵌策略列，以及归档文件被活动 Rule 引用。

Identity 与 Risk 的 36 条共享服务严格限定为两个指定文件及 `Identity` 策略；
校验器会拒绝把这些豁免复制到其他文件或策略。美国住宅文件中的
`.apexclearing.com`、`.earlywarning.com`、`.id.me`、`.login.gov` 同样使用
“文件 + 策略 + 域名”三重限定。

`api.github.com` 在 SKK `ai.conf` 前精确进入 `PROXY`，避免普通 GitHub API
请求被 AIGC 接管。活动主 Rule 不再包含 `DOMAIN-KEYWORD`。
