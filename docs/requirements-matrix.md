# Requirements matrix

本表逐项对应配置所有者提供的 555 行 Rule，避免“文件存在但内容没有落地”。

| 原始项目 | 精准版实现 | 状态 |
| --- | --- | --- |
| MTProto | `PROTOCOL,MTProto,Telegram` | 保留 |
| LAN | `RULE-SET,LAN,DIRECT,no-resolve` | 保留 |
| 全局 STUN 拒绝 | 不加载 | 有意调整：避免破坏 WebRTC、FaceTime 和视频验证 |
| Polymarket | `.polymarket.com`、`.polymarket.us`、`pmx-prod.us.auth0.com` | 已收紧，不再使用关键词 |
| iCloud Private Relay | 6 条精确本地兜底 + SKK 远程集 | 已增强，独立 `Private-Relay` |
| Apple Cash / Pay | 主 Rule 三条显式规则 | 保留，使用系统路径 |
| Apple Intelligence | `apple-ai.conf` | 全部迁移，独立 `Apple-AI` |
| 中国大陆银行 / 银联 | `direct-cn.conf` | 23/23 |
| 香港金融 | `hk-finance.conf` | 20/20 |
| 新加坡金融 | `sg-finance.conf` | 11/11 |
| 日本金融 | `jp-finance.conf` | 8/8 |
| 韩国金融 | `kr-finance.conf` | 9/9 |
| 英国金融 | `uk-finance.conf` | 14/14 |
| 美国第一方金融 | `us-residential.conf` | 全部保留；没有推测停用任何机构 |
| 跨地区金融机构 | `finance-context.conf` | 29/29 第一方域名 |
| Crypto | `crypto.conf` | 15/15 |
| Web3 | `web3.conf` | 168 条有效语义；1 条被父后缀覆盖的规则已去重 |
| 共享支付 / KYC / 指纹 / CAPTCHA | 不加载到金融出口 | 有意调整：避免共享域名造成跨地区会话分裂 |
| SYSTEM | `RULE-SET,SYSTEM,DIRECT` | 保留 |
| Emby / Telegram / AIGC / Streaming | 主 Rule 服务段 | 全部保留并提前到广告规则前 |
| Apple / Microsoft | 主 Rule 平台段 | 全部保留 |
| 下载 / CDN / Speedtest | 主 Rule 下载段 | 全部保留并提前到广告规则前 |
| 广告 / 恶意域名 | 主 Rule拒绝段 | 5/5 |
| WeChat / 国内 / 全球 | 主 Rule 基础段 | 全部保留，明确规则优先 |
| IP 规则 | 主 Rule IP 段 | 6/6，全部 `no-resolve` |
| FINAL | `FINAL,PROXY,dns-failed` | 保留且强制最后一条 |

## 精准性约束

CI 会拒绝：

- 未授权的 `DOMAIN-KEYWORD`；
- `.apple.com`、`.icloud.com`、`.auth0.com`、`.cloudflare.com` 等共享根后缀；
- `.co.uk`、`.com.cn` 等公共层级后缀；
- 重复域名、父子后缀冗余和跨策略覆盖；
- 本仓库远程集的错策略、漏引用、重复引用或顺序错误；
- 提前出现的 `SYSTEM`、`FINAL` 或缺少 `no-resolve` 的 IP 规则。

`cr18` 是当前唯一允许的关键词规则，因为原始配置没有提供可替换的完整主机名。
一旦从 Surge 请求日志确认实际域名，应将它改成精确域名并从允许列表删除。
