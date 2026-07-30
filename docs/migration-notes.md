# Migration notes

本仓库的规则数据来自配置所有者提供的 555 行 `[Rule]` 清单，并按最终策略拆分。

## 已迁移覆盖

| 来源策略 | 仓库位置 | 处理 |
| --- | --- | --- |
| `DIRECT` | `direct-cn.conf` | 全部迁移 |
| `HK-FINANCE` | `hk-finance.conf` | 全部迁移 |
| `SG-FINANCE` | `sg-finance.conf` | 全部迁移 |
| `JP-FINANCE` | `jp-finance.conf` | 全部迁移 |
| `KR-FINANCE` | `kr-finance.conf` | 全部迁移 |
| `UK-FINANCE` | `uk-finance.conf` | 全部迁移 |
| `Res-Frontier` | `polymarket.conf`、`us-residential.conf` | Polymarket；美国第一方金融、Apple Cash/Pay 与 PayPal |
| `Finance` | `finance-context.conf` | 跨地区金融机构自身域名迁移 |
| `Identity` | `identity-context.conf`、`risk-context.conf` | KYC/身份验证与设备指纹/反欺诈分层 |
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
- Private Relay 保持 `Apple`，Apple Intelligence 保持 `AIGC`。
- Apple Cash/Pay 与 PayPal 归入 `us-residential.conf`。
- Polymarket 从宽泛 `DOMAIN-KEYWORD` 收窄为 `.com`、`.us` 和一个精确 Auth0 租户，
  独立放入最优先的 `polymarket.conf`。
- `bankofchina.com` 因不同国家站点共用根域且按路径分区，从大陆直连移到 `Finance`；
  `pingan.com` 收窄为 `bank.pingan.com`。
- 美国住宅文件移除共享清算、身份、征信及反欺诈基础设施，补充 11 个第一方区域银行。
- KYC/身份验证与设备指纹/反欺诈供应商不进入 `Finance`，分别进入
  `identity-context.conf` 与 `risk-context.conf`，统一使用 `Identity`。
- 美国住宅文件明确补回 Apex Clearing、Early Warning、ID.me 与 Login.gov。
- 删除宽泛 `.icbc.com`，保留大陆专用 `.icbc.com.cn` 与香港 `.icbcasia.com`。
- Apple CDN 从已废弃的 `non_ip` 占位切换至有效 DOMAIN-SET。
- 删除只有 SKK 哨兵的 `ip/stream_us.conf`，并删除与聚合 Streaming 同策略的
  `non_ip/stream_us.conf`。
- reject-drop 不使用 `pre-matching`，避免越过前置业务规则；Adblock4limbo
  只加载合规的清洗补集。
- `api.github.com` 在通用 AI 规则前固定到 `PROXY`；删除无法精确验证的 cr18 关键词。

Identity 与 Risk 文件的活动条目由校验器按文件、策略与域名三重锁定。
