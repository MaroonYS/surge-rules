# Requirements Matrix

| 阶段 | 目标 | 落地规则 |
| --- | --- | --- |
| 1 | NTP、MTProto 与模块资源 | NTP 直连、MTProto 新加坡、GitHub 模块资源香港；不含 Apple 自定义例外 |
| 2 | 地区银行、住宅风控、Crypto、Web3 | 12 个本仓库 `DOMAIN-SET`，按固定地区或业务策略分流 |
| 3 | Sukka 域名集 | `speedtest` → `cdn` → `apple_cdn` → `download` |
| 4 | Sukka 非 IP 集 | CDN、Stream、AI、Apple、Microsoft、Download、LAN、Domestic/Direct/Global；窄 Apple CN 先于宽 Apple Services |
| 5 | Sukka IP 与最终规则 | Stream → AI → Telegram 官方 CIDR → LAN → Domestic → China IP → `FINAL` |

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
- Sukka Reject 与 Adblock4limbo 补集：移动端作者不推荐，且保留模块已负责广告拦截。
- 全局 `PROTOCOL,STUN,REJECT`：会破坏 Voice、WebRTC 和部分验证流程。
- `RULE-SET,SYSTEM` 与 APNs 专用覆盖：当前 `include-apns=false`，系统关键链路改由精确规则处理。
- Telegram `non_ip` 与 ASN：只保留作者推荐的官方 CIDR。
- 第三方 Emby 总表：仅保留 `nano.cr18.eu.org` → `Singapore`。
- Gate 专用分流：不创建无明确 App/账户用途的覆盖。

## 模块边界

所有现有模块继续保留；本次只重建基础 `[Rule]`。模块所需 MITM 正向主机和金融、
iCloud、Polymarket 等保护性排除仍由 `module-compatibility.json` 与
`docs/module-baseline.md` 校验。
