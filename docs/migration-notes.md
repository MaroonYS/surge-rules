# Migration notes

本仓库的规则数据来自配置所有者提供的 555 行 `[Rule]` 清单，并按语义角色拆分。
当前配置不再为每个语义角色创建策略组；Identity/Risk 与跨地区 Finance 一样
固定使用 `Res-Frontier`。`rules-manifest.json` 用
`semantic_role` 保留验证边界，用 `policy` 记录实际运行出口。

## 已迁移覆盖

| 来源策略 / 语义角色 | 仓库位置 | 处理 |
| --- | --- | --- |
| `Res-Frontier`（X） | `x-residential.conf` | X 第一方账户、API、Money、跳转、媒体与 Live 统一住宅出口 |
| `DIRECT` | `direct-cn.conf` | 中国大陆银行与银联迁移 |
| `DIRECT`（Bilibili） | `bilibili-direct.conf` | 原宽泛关键词收窄为 3 个视频 CDN 后缀并恢复前置优先级 |
| `HK-FINANCE` | `hk-finance.conf`、`hk-finance-context.conf` | 香港第一方域名迁移；当前账户的香港汇丰及香港券商共享基础设施从跨地区集合固定到香港上下文 |
| `SG-FINANCE` | `sg-finance.conf` | 全部迁移 |
| `JP-FINANCE` | `jp-finance.conf` | 全部迁移 |
| `KR-FINANCE` | `kr-finance.conf` | 全部迁移 |
| `UK-FINANCE` | `uk-finance.conf` | 全部迁移 |
| `DIRECT` / `Res-Frontier` | `polymarket-global.conf`、`polymarket.conf`、`us-residential.conf` | Polymarket 国际产品使用真实地点、美国独立产品走住宅；美国第一方金融、Apple Cash/Pay 与 PayPal 走住宅 |
| `Finance` | `finance-context.conf` | 跨地区金融机构自身域名迁移 |
| `Identity` / `Risk` | `identity-context.conf`、`risk-context.conf` | KYC/身份验证与保守设备情报/指纹分层；共享多租户域固定使用 `Res-Frontier` 兜底 |
| `Bybit` / Gate / `Crypto` | `bybit.conf`、`gate.conf`、`crypto.conf` | Bybit 独立限定受支持地区；Gate 保持真实地点并由服务端判定资格；其余中心化交易所保留通用手动组 |
| `Web3` | `web3.conf` | 全部有效语义迁移 |
| `AIGC` | `apple-ai.conf` | 全部迁移；运行时固定 `United States` |

没有任何金融机构因为“推测未使用”而被删除或归档。

## 等价去重

来源中的：

```text
.moonbeam.moonscan.io
.moonscan.io
```

前者已经被后者完整覆盖，因此仓库只保留 `.moonscan.io`。实际匹配范围不变。

## 有意调整

- 按 17 段契约保留 `PROTOCOL,STUN,REJECT`，并在其前将 NTP/UDP 123 固定 `DIRECT`，避免系统时间同步误入普通代理。
- X 六个第一方后缀在 Google/Reject/CDN/Global 之前固定住宅出口；不扩大 X MITM，也不把路由当作 X Money 居住或身份资格。
- Gate 的 `.gate.com`、`.gate.io`、`.gateio.ws` 固定 `DIRECT`，避免整域拒绝把官网、帮助和资格错误伪装成网络故障；真实地点与账户/KYC 资格仍由 Gate 判定。
- 原 `DOMAIN-KEYWORD,bilivideo,DIRECT,extended-matching` 收窄为 `.bilivideo.com`、
  `.bilivideo.cn`、`.bilivideo.net`，并在第 2 段首位加载，保证先于共享
  Reject、Streaming、CDN 与 Global 规则命中。
- Bilibili 前置文件不收录 `bilibili.com` 与 `biliapi.net` API 域，保证
  BiliUniverse Global 的脚本、MITM 与 `http-client-policy` 地区选择不被覆盖；
  模块保持 `ForceHost=1`。
- Private Relay 与 Apple Intelligence 从宽泛 Apple 路径拆出，运行时固定普通
  `United States` 节点；Private Relay 不使用住宅 SOCKS5。
- Apple Cash/Pay 与 PayPal 归入 `us-residential.conf`。
- Polymarket 从宽泛 `DOMAIN-KEYWORD` 收窄并按产品拆分：国际 `.com`、精确 Auth0
  租户及上传主机进入 `polymarket-global.conf,DIRECT`；美国 `.us` 单独进入
  `polymarket.conf,Res-Frontier`。
- `bankofchina.com` 因不同国家站点共用根域且按路径分区，从大陆直连移到 `Finance`；
  `pingan.com` 收窄为 `bank.pingan.com`。
- 美国住宅文件移除共享清算、身份、征信及反欺诈基础设施，补充 11 个第一方区域银行。
- KYC/身份验证与设备指纹/反欺诈供应商不混入 Finance 语义文件，分别进入
  `identity-context.conf` 与 `risk-context.conf`；Finance、Identity 与 Risk 在运行时
  均固定 `Res-Frontier`，不再要求用户手动切换验证上下文。
- Identity 删除宽泛 `.persona.com`，保留产品域 `.withpersona.com`；Risk 收窄为
  8 个设备情报、设备信誉、行为生物识别与指纹域名。
- 中国、香港、新加坡、日本、韩国、英国银行第一方集合继续优先命中各自静态地区策略；
  Bybit、Crypto 与 Web3 第一方集合也继续使用各自非美策略。共享 KYC/风控根域无法由
  iOS 识别调用 App，因此固定住宅仅是美国金融优先的确定性兜底。只有能由真实日志证明
  租户归属的精确 hostname 才能在共享层之前增加对应地区或加密业务覆盖。
- HSBC HK、Futu/Moomoo HK 与 Longbridge HK 的共享基础设施从
  `finance-context.conf` 移入 `hk-finance-context.conf`，避免当前账户误走美国住宅。
- Bybit 从通用 `Crypto` 拆为独立策略；只有账户本人真实且受支持
  地区一致的线路才能由用户显式加入，是否保留 `REJECT` 由各设备的组定义决定。
- 美国住宅文件明确补回 Apex Clearing、Early Warning、ID.me 与 Login.gov。
- 删除宽泛 `.icbc.com`，保留大陆专用 `.icbc.com.cn` 与香港 `.icbcasia.com`。
- Apple CDN 从已废弃的 `non_ip` 占位切换至有效 DOMAIN-SET。
- 删除只有 SKK 哨兵的 `ip/stream_us.conf`，并删除与聚合 Streaming 同策略的
  `non_ip/stream_us.conf`。
- reject-drop 不使用 `pre-matching`，避免越过前置业务规则；Adblock4limbo
  只加载合规的清洗补集。
- `api.github.com` 在通用 AI 规则前固定到 `PROXY`；删除无法精确验证的 cr18 关键词。

Identity 与 Risk 文件的活动条目由校验器按文件、语义角色与域名三重锁定。
