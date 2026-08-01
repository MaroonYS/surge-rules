# Migration notes

本仓库的规则数据来自配置所有者提供的 555 行 `[Rule]` 清单，并按最终策略拆分。

## 已迁移覆盖

| 来源策略 | 仓库位置 | 处理 |
| --- | --- | --- |
| `DIRECT` | `direct-cn.conf` | 中国大陆银行与银联迁移 |
| `DIRECT`（Bilibili） | `bilibili-direct.conf` | 原宽泛关键词收窄为 3 个视频 CDN 后缀并恢复前置优先级 |
| `HK-FINANCE` | `hk-finance.conf` | 全部迁移 |
| `SG-FINANCE` | `sg-finance.conf` | 全部迁移 |
| `JP-FINANCE` | `jp-finance.conf` | 全部迁移 |
| `KR-FINANCE` | `kr-finance.conf` | 全部迁移 |
| `UK-FINANCE` | `uk-finance.conf` | 全部迁移 |
| `Res-Frontier` | `polymarket.conf`、`us-residential.conf` | Polymarket（含实测 S3 上传主机）；美国第一方金融、Apple Cash/Pay 与 PayPal |
| `Finance` | `finance-context.conf` | 跨地区金融机构自身域名迁移 |
| `Identity` | `identity-context.conf`、`risk-context.conf` | KYC/身份验证与保守设备情报/指纹分层 |
| `Crypto` | `crypto.conf` | 全部迁移 |
| `Web3` | `web3.conf` | 全部有效语义迁移 |
| `AIGC` | `apple-ai.conf` | 全部迁移并保持 `AIGC` |

没有任何金融机构因为“推测未使用”而被删除或归档。

## 等价去重

来源中的：

```text
.moonbeam.moonscan.io
.moonscan.io
```

前者已经被后者完整覆盖，因此仓库只保留 `.moonscan.io`。实际匹配范围不变。

## 有意调整

- 按 17 段契约保留 `PROTOCOL,STUN,REJECT`。
- 原 `DOMAIN-KEYWORD,bilivideo,DIRECT,extended-matching` 收窄为 `.bilivideo.com`、
  `.bilivideo.cn`、`.bilivideo.net`，并在第 2 段首位加载，保证先于共享
  Reject、Streaming、CDN 与 Global 规则命中。
- Bilibili 前置文件不收录 `bilibili.com` 与 `biliapi.net` API 域，保证
  BiliUniverse Global 的脚本、MITM 与 `http-client-policy` 地区选择不被覆盖；
  模块保持 `ForceHost=1`。
- Private Relay 保持 `Apple`，Apple Intelligence 保持 `AIGC`。
- Apple Cash/Pay 与 PayPal 归入 `us-residential.conf`。
- Polymarket 从宽泛 `DOMAIN-KEYWORD` 收窄为 `.com`、`.us`、精确 Auth0 租户和
  实测 `polymarket-upload.s3.us-east-2.amazonaws.com` 上传主机，独立放入
  最优先的 `polymarket.conf`。
- `bankofchina.com` 因不同国家站点共用根域且按路径分区，从大陆直连移到 `Finance`；
  `pingan.com` 收窄为 `bank.pingan.com`。
- 美国住宅文件移除共享清算、身份、征信及反欺诈基础设施，补充 11 个第一方区域银行。
- KYC/身份验证与设备指纹/反欺诈供应商不进入 `Finance`，分别进入
  `identity-context.conf` 与 `risk-context.conf`，统一使用 `Identity`。
- Identity 删除宽泛 `.persona.com`，保留产品域 `.withpersona.com`；Risk 收窄为
  8 个设备情报、设备信誉、行为生物识别与指纹域名。
- `Identity` 直接选择 `Res-Frontier`、`United States` 与 `Finance`，不再定义
  中间美国金融策略组。
- 美国住宅文件明确补回 Apex Clearing、Early Warning、ID.me 与 Login.gov。
- 删除宽泛 `.icbc.com`，保留大陆专用 `.icbc.com.cn` 与香港 `.icbcasia.com`。
- Apple CDN 从已废弃的 `non_ip` 占位切换至有效 DOMAIN-SET。
- 删除只有 SKK 哨兵的 `ip/stream_us.conf`，并删除与聚合 Streaming 同策略的
  `non_ip/stream_us.conf`。
- reject-drop 不使用 `pre-matching`，避免越过前置业务规则；Adblock4limbo
  只加载合规的清洗补集。
- `api.github.com` 在通用 AI 规则前固定到 `PROXY`；删除无法精确验证的 cr18 关键词。

Identity 与 Risk 文件的活动条目由校验器按文件、策略与域名三重锁定。
