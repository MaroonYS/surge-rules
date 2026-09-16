# Requirements Matrix

最新个人 App 地区要求及迁移/去重证据见 [2026-09-16 的 24 App 清单](finance-app-matrix.md)。
后续 Apple 支付、账户与 Private Relay 住宅例外已撤销；用户最新澄清要求保留原先启用的
全部 Sukka 订阅，误删的 Private Relay 官方集已恢复并改绑 `United States`，见 [Apple 回归 Sukka](apple-sukka-only.md)。

| 阶段 | 目标 | 落地规则 |
| --- | --- | --- |
| 1 | NTP、MTProto 与模块资源 | NTP 直连、MTProto 新加坡、GitHub 模块资源香港；不含 Apple 自定义例外 |
| 2 | 固定地区与高风控业务 | Supercell 域名直连 → 固定媒体 → 中国大陆实体金融 → 分地区实体金融 → 美国住宅、身份与风控 → Crypto 与 Web3；本仓库域名资源先于大型 Reject 域名集 |
| 3 | 域名集 | Sukka Reject 基础 → Reject Extra → Reject Phishing → `speedtest` → `cdn` → `apple_cdn`；保留 `icloud_private_relay` 官方订阅；Microsoft CDN/download 交集直连先于 `download` |
| 4 | Sukka 非 IP 集 | Reject Drop → Reject → Reject No Drop → CDN、Stream、AI、Telegram、Apple、Microsoft、Download、LAN、Domestic/Direct/Global；窄 Apple CN 先于宽 Apple Services |
| 5 | Sukka IP 与最终规则 | Blackmatrix7 Supercell 混合兼容层（`no-resolve`）→ Reject → Stream → AI → Telegram 官方 CIDR → Sukka LAN → Domestic → China IP → `FINAL` |

## 活动资源

| 文件 | 类型 | 固定策略 | 保留理由 |
| --- | --- | --- | --- |
| `supercell-direct.conf` | `DOMAIN-SET` | `DIRECT` | Supercell 登录、账户服务与各款游戏首方域统一直连 |
| `direct-cn.conf` | `DOMAIN-SET` | `DIRECT` | 中国大陆实体银行与银联 |
| `ch-finance.conf` | `DOMAIN-SET` | `Switzerland` | MEXC 的 15 条第一方/已确认资源规则，仅绑定现有瑞士策略 |
| `uk-finance.conf` | `DOMAIN-SET` | `United Kingdom` | N26、Loqbox、Kraken/Krak、Monzo、Lloyds、HSBC Expat 等既定英国出口，先于 HK |
| `hk-finance.conf` | `DOMAIN-SET` | `Hong Kong` | 香港银行、Futu/Moomoo、Longbridge 等香港账户上下文 |
| `sg-finance.conf` | `DOMAIN-SET` | `Singapore` | 新加坡实体银行与券商 |
| `jp-finance.conf` | `DOMAIN-SET` | `Japan` | 日本实体银行与券商 |
| `kr-finance.conf` | `DOMAIN-SET` | `Korea` | 韩国实体银行 |
| `us-residential.conf` | `DOMAIN-SET` | `Res-Frontier` | 美国金融、LemFi 的首方及精确专属资源、信用、X Money、Google Account/Voice、Polymarket |
| `finance-context.conf` | `DOMAIN-SET` | `Res-Frontier` | 无法仅由主机名判断地区的金融首方域 |
| `identity-context.conf` | `DOMAIN-SET` | `Res-Frontier` | KYC/身份验证共享基础设施 |
| `risk-context.conf` | `DOMAIN-SET` | `Res-Frontier` | 指纹、设备情报、反欺诈基础设施 |
| `crypto.conf` | `DOMAIN-SET` | `Crypto` | Bybit 与其余中心化交易所 |
| `web3.conf` | `DOMAIN-SET` | `Web3` | 钱包、RPC、DeFi、NFT、浏览器 |
| `microsoft-cdn-download-overlap.conf` | `DOMAIN-SET` | `DIRECT` | 修复 38 个 Microsoft 中国 CDN 下载域被香港下载集合抢先的问题 |

## 明确不加载

- Apple 全域、系统更新、iCloud、证书与 APNs 的自定义覆盖；支付/账户/账单九条住宅
  规则和设备 Private Relay 住宅绑定均已撤销；Private Relay 官方订阅保留并改绑普通美国，
  基础层共复用五个 Sukka Apple 资源。不得以去重为由删除原先已启用的 Sukka 订阅。
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

所有现有模块继续保留；只在广告平台模块的两条抢先拦截规则中排除原有五个短信主机，
不扩大白名单或改其他模块。模块所需 MITM 正向主机和金融、
iCloud、Polymarket 等保护性排除仍由 `module-compatibility.json` 与
`docs/module-baseline.md` 校验。

## 认证与运行验收

共享身份清单保持原样；N26/Loqbox/MEXC 的新增共享认证地区绑定未部署。
不能把 SDK 默认地址当成实际会话主机，也不能用供应商重合证明跨 App 主机冲突。
静态测试重点覆盖已点名的第一方业务、窄例外和反例；登录、验证码、KYC、支付与
iPhone 原生链路仍需只含域名和策略的实际记录，见 [验收说明](routing-completeness.md)。
