# 17 段要求核对

`rules-contract.json` 是机器可读的唯一契约。CI 会逐条比较以下 17 段的标题、
规则、策略、参数和顺序；少一条、多一条或换位置都会失败。

| 序号 | 要求 | 实现与校验 |
| ---: | --- | --- |
| 1 | STUN、MTProto、LAN | 4 条全部保留；补充 SKK 非 IP LAN，内建 LAN 保持 `DIRECT,no-resolve` |
| 2 | Polymarket 最优先 | 3 个精确目标放入 `polymarket.conf`，不再宽泛匹配关键词 |
| 3 | iCloud Private Relay | SKK DOMAIN-SET 固定到 `Apple` |
| 4 | Apple Intelligence / Siri / PCC | `apple-ai.conf` 固定到 `AIGC` |
| 5 | 中国大陆银行 | `direct-cn.conf`，25 条，`DIRECT`；跨地区的 `bankofchina.com` 不在此强制直连 |
| 6 | 分地区金融 | HK 28、SG 15、JP 14、KR 10、UK 18，策略逐一固定 |
| 7 | 美国住宅出口 | `us-residential.conf`，115 条；包括 Apple Cash/Pay、美国第一方金融及 PayPal |
| 8 | 跨地区金融等 | `finance-context.conf`，27 条，固定到 `Finance`；共享验证供应商不激活 |
| 9 | 中心化交易所 | `crypto.conf`，15 条，`Crypto` |
| 10 | Web3 | `web3.conf`，168 条有效语义，`Web3` |
| 11 | 剩余系统服务 | `RULE-SET,SYSTEM,DIRECT` |
| 12 | 广告和恶意域名 | 严格按 SukkaW 顺序：reject-drop `pre-matching` → reject DOMAIN-SET → 精简补集 → reject → reject-no-drop |
| 13 | 服务专用 | Emby、cr18、Telegram、AIGC 与聚合 Streaming；删除同策略下冗余的 stream_us |
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
| `crypto.conf` | `Crypto` |
| `web3.conf` | `Web3` |
| `adblock4limbo-supplement.conf` | `REJECT` |

## 精准性约束

CI 还会拒绝重复、父子后缀冗余、跨策略覆盖、错策略、漏引用、过宽共享后缀、
共享验证基础设施被整域绑定到敏感策略、外部 RULE-SET 内嵌策略列，以及归档文件被活动 Rule 引用。

第 8 段的 52 个共享支付聚合、KYC、验证码、指纹及反欺诈供应商不会统一绑定
`Finance` 或住宅出口。它们横跨多个站点和地区，批量改道既不精准，也不作为本仓库的活动功能。

`cr18` 是唯一保留的 `DOMAIN-KEYWORD`。目前没有足够可靠的精确主机证据；
后续应以 Surge 请求日志为依据收窄，不能凭名称猜测域名。
