# Requirements Matrix

| 阶段 | 目标 | 落地规则 |
| --- | --- | --- |
| 1 | NTP、MTProto 与模块资源 | NTP 直连、MTProto 新加坡、GitHub 模块资源香港；不含 Apple 自定义例外 |
| 2 | 固定地区与高风控业务 | 固定媒体 → 中国大陆实体金融 → 分地区实体金融 → 美国住宅、身份与风控 → Crypto 与 Web3；12 个本仓库 `DOMAIN-SET` 先于大型 Reject 域名集 |
| 3 | 域名集 | Sukka Reject 基础 → Reject Extra → Reject Phishing → `speedtest` → `cdn` → `apple_cdn` → `download` |
| 4 | Sukka 非 IP 集 | Reject Drop → Reject → Reject No Drop → CDN、Stream、AI、Telegram、Apple、Microsoft、Download、LAN、Domestic/Direct/Global；窄 Apple CN 先于宽 Apple Services |
| 5 | Sukka IP 与最终规则 | Reject → Stream → AI → Telegram 官方 CIDR → Sukka LAN → Domestic → China IP → `FINAL` |

## 活动资源

| 文件 | 类型 | 固定策略 | 保留理由 |
| --- | --- | --- | --- |
| `direct-cn.conf` | `DOMAIN-SET` | `DIRECT` | 中国大陆实体银行与银联 |
| `hk-finance.conf` | `DOMAIN-SET` | `Hong Kong` | 香港银行、Futu/Moomoo、Longbridge 等香港账户上下文 |
| `sg-finance.conf` | `DOMAIN-SET` | `Singapore` | 新加坡实体银行与券商 |
| `jp-finance.conf` | `DOMAIN-SET` | `Japan` | 日本实体银行与券商 |
| `kr-finance.conf` | `DOMAIN-SET` | `Korea` | 韩国实体银行 |
| `uk-finance.conf` | `DOMAIN-SET` | `United Kingdom` | 英国实体银行与券商 |
| `us-residential.conf` | `DOMAIN-SET` | `Res-Frontier` | 美国金融、信用、X Money、Google Account/Voice、Polymarket |
| `finance-context.conf` | `DOMAIN-SET` | `Res-Frontier` | 无法仅由主机名判断地区的金融首方域 |
| `identity-context.conf` | `DOMAIN-SET` | `Res-Frontier` | KYC/身份验证共享基础设施 |
| `risk-context.conf` | `DOMAIN-SET` | `Res-Frontier` | 指纹、设备情报、反欺诈基础设施 |
| `crypto.conf` | `DOMAIN-SET` | `Crypto` | Bybit 与其余中心化交易所 |
| `web3.conf` | `DOMAIN-SET` | `Web3` | 钱包、RPC、DeFi、NFT、浏览器 |

## 明确不加载

- Apple 自定义更新、付款、Private Relay、iCloud、证书与 APNs 规则；只保留 Sukka
  `apple_cdn`、`apple_intelligence`、`apple_cn`、`apple_services`。
- Sukka `reject-url-regex.conf` 与新的 MITM 拦截层：上游已警告此类匹配的性能开销；
  域名、非 IP 与 IP Reject 资源（包括 Phishing）仍全部加载。
- Adblock4limbo 外部规则集：当前源近半数规则已被 Sukka 覆盖，规范化后仅剩 224 条
  增量；为减少第三方供应链和重复维护，移除其规则、生成文件与同步任务。保留模块内
  的网页处理脚本不属于基础分流，本次不改。
- 全局 `PROTOCOL,STUN,REJECT`：会破坏 Voice、WebRTC 和部分验证流程。
- `RULE-SET,SYSTEM` 与 APNs 专用覆盖：当前 `include-apns=false`，系统关键链路改由精确规则处理。
- Telegram ASN：仅作为上游可选补充；当前已同时加载 `non_ip` 与官方 CIDR。
- 第三方 Emby 总表：仅保留 `nano.cr18.eu.org` → `Singapore`。
- Gate 专用分流：不创建无明确 App/账户用途的覆盖。

## 模块边界

所有现有模块继续保留；本次只重建基础 `[Rule]`。模块所需 MITM 正向主机和金融、
iCloud、Polymarket 等保护性排除仍由 `module-compatibility.json` 与
`docs/module-baseline.md` 校验。
