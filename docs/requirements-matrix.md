# 17 段要求核对

`rules-contract.json` 是机器可读的唯一契约。CI 会逐条比较以下 17 段的标题、
规则、策略、参数和顺序；少一条、多一条或换位置都会失败。

| 序号 | 要求 | 实现与校验 |
| ---: | --- | --- |
| 1 | STUN、MTProto、LAN | 3 条全部保留；STUN=`REJECT`，LAN=`DIRECT,no-resolve` |
| 2 | Polymarket 最优先 | `DOMAIN-KEYWORD` 保留并固定到 `Res-Frontier` |
| 3 | iCloud Private Relay | SKK DOMAIN-SET 固定到 `Apple` |
| 4 | Apple Intelligence / Siri / PCC | `apple-ai.conf` 固定到 `AIGC` |
| 5 | 中国大陆银行 | `direct-cn.conf`，23 条，`DIRECT` |
| 6 | 分地区金融 | HK 20、SG 11、JP 8、KR 9、UK 14，策略逐一固定 |
| 7 | 美国住宅出口 | `us-residential.conf`；包括 Apple Cash/Pay、美国第一方金融及 PayPal |
| 8 | 跨地区金融等 | `finance-context.conf` 固定到 `Finance`；共享验证供应商不激活 |
| 9 | 中心化交易所 | `crypto.conf`，15 条，`Crypto` |
| 10 | Web3 | `web3.conf`，168 条有效语义，`Web3` |
| 11 | 剩余系统服务 | `RULE-SET,SYSTEM,DIRECT` |
| 12 | 广告和恶意域名 | 5 个拒绝资源，顺序与要求一致 |
| 13 | 服务专用 | Emby、cr18、Telegram、AIGC、两组 Streaming 全部保留 |
| 14 | Apple / Microsoft | 5 个资源及对应策略全部保留 |
| 15 | 下载和 CDN | Speedtest、两组 Download、两组 CDN 全部保留 |
| 16 | 国内和海外基础规则 | Domestic、WeChat、Direct、Global，顺序固定 |
| 17 | IP 类与 FINAL | Reject、Telegram、两组 Streaming、Domestic、China IP 均 `no-resolve`；FINAL 最后 |

## 活动 DOMAIN-SET

| 文件 | 策略 |
| --- | --- |
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

## 精准性约束

CI 还会拒绝重复、父子后缀冗余、跨策略覆盖、错策略、漏引用、过宽共享后缀、
缺少 `extended-matching`、IP 规则缺少 `no-resolve` 以及归档文件被活动 Rule 引用。

第 8 段的 52 个共享支付聚合、KYC、验证码、指纹及反欺诈供应商不会统一绑定
`Finance` 或住宅出口。它们横跨多个站点和地区，批量改道既不精准，也不作为本仓库的活动功能。
