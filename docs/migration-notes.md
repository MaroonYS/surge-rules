# Migration Notes

## 2026-08 Sukka-first rebuild

旧规则层按业务历史逐次增补，出现了三个问题：同一策略拆成多个远程文件、一度将
上游对 MITM/URL-REGEX 的性能提示扩大为整体删除 Reject、以及 IP 类规则过早出现。
此次迁移只替换基础 `[Rule]`，策略组、
节点、订阅、General、MITM、Rewrite 与模块均保持不变。

### 合并

- `x-residential.conf`、`google-account.conf`、`google-voice.conf`、
  `polymarket-global.conf`、`polymarket.conf` → `us-residential.conf`。
- `hk-finance-context.conf` → `hk-finance.conf`。
- `bybit.conf` → `crypto.conf`。

旧文件不再活动，但保留在仓库历史中，避免破坏已有链接；主规则与 manifest 只加载
合并后的 13 个业务资源。

### Apple 回归 Sukka 公共语义

此前建立的 Software Updates、Apple Account/付款、Private Relay、iCloud 同步、
证书验证与 APNs 自定义例外全部从主规则移除。Apple 只保留 Sukka README 明确列出的
`apple_cdn`、`apple_intelligence`、`apple_cn`、`apple_services`；系统更新由 Sukka
`download` 与 Apple 公共规则共同承接。相关旧文件仍保留历史，但不再活动。

### 调整后的基础拦截边界

- 恢复 Sukka 基础、额外与 Phishing 三个 Reject `DOMAIN-SET`，恢复 Reject Drop、
  Reject 和 Reject No Drop 三个 `non_ip` 资源，并恢复 IP Reject。
- 不加载 `reject-url-regex.conf` 或新的 MITM 拦截层。Adblock4limbo 当前源 543 条
  活动规则中有 253 条被 Sukka 覆盖，规范化后仅剩 224 条增量，因此连同生成文件和
  定时同步任务一并移除；设备已保留的模块不受改动。
- Bilibili、淘宝、Brawl Stars 等旧反向放行不会仅因 Reject 恢复就无证据回加；
  若出现误杀，应先从 Surge 请求日志确认精确主机名。
- 全局 STUN 拒绝及其 Google Voice 例外；不再人为阻断正常 WebRTC/Voice。
- APNs 代理覆盖与 `SYSTEM`；当前设备明确使用 `include-apns=false`。
- 第三方 WeChat、Emby 总表及 GitHub API 特例；分别由 Sukka 国内/全局规则、精确 Emby
  主机与普通 CDN/全局策略承接。

### Sukka 顺序

新结构严格为：自定义精确域名与本仓库 `DOMAIN-SET` → Sukka Reject 与公共
`DOMAIN-SET` → Sukka Reject 与公共 `non_ip` → Sukka Reject 与公共 `ip` → `FINAL`。
第 2 段再细分为固定媒体、中国大陆实体金融、分地区实体金融、美国住宅、身份与风控及
Crypto 与 Web3；其中定向性强的自定义域集全部先于大型 Reject 域集。Mac 的 VoHive
`PROCESS-NAME` 与域名例外留在前段，
其 `IP-CIDR` 被移动到 IP 阶段，避免破坏 DNS 污染防护顺序。

Apple CN 在广义 Apple Services 前是有意的窄规则优先；这是首匹配语义所必需，并不
改变 `domainset → non_ip → ip` 总体约束。
