# Migration Notes

## 2026-08 Sukka-first rebuild

旧规则层按业务历史逐次增补，出现了三个问题：同一策略拆成多个远程文件、公共 Reject
与保留广告模块重复、以及 IP 类规则过早出现。此次迁移只替换基础 `[Rule]`，策略组、
节点、订阅、General、MITM、Rewrite 与模块均保持不变。

### 合并

- `x-residential.conf`、`google-account.conf`、`google-voice.conf`、
  `polymarket-global.conf`、`polymarket.conf` → `us-residential.conf`。
- `hk-finance-context.conf` → `hk-finance.conf`。
- `bybit.conf` → `crypto.conf`。

旧文件不再活动，但保留在仓库历史中，避免破坏已有链接；主规则与 manifest 只加载
合并后的 12 个资源。

### 内联

- `apple-software-update.conf` 的内容与 5 个既有启动主机合并为 21 条精确 `DOMAIN`。
- `apple-account-payment-rules.conf` 改为 5 个精确主机加一个动态账单分片。
- `icloud_private_relay.conf` 不再作为未列入 Sukka README 基线的远程依赖，改为 6 个
  精确入口并前置于 iCloud 直连层。
- `icloud-sync.conf` 改为精确后缀内联，保证 CloudKit、Photos、iWork 与内容传输不受
  外部资源刷新影响。

### 删除的基础规则层

- Sukka Reject、Adblock4limbo 补集与 IP Reject；现有模块继续负责广告拦截。
- Bilibili、淘宝、Brawl Stars 等为旧 Reject 误杀而建立的反向放行；Reject 移除后不再需要。
- 全局 STUN 拒绝及其 Google Voice 例外；不再人为阻断正常 WebRTC/Voice。
- APNs 代理覆盖与 `SYSTEM`；当前设备明确使用 `include-apns=false`。
- 第三方 WeChat、Emby 总表及 GitHub API 特例；分别由 Sukka 国内/全局规则、精确 Emby
  主机与普通 CDN/全局策略承接。

### Sukka 顺序

新结构严格为：自定义精确域名与本仓库 `DOMAIN-SET` → Sukka `DOMAIN-SET` → Sukka
`non_ip` → Sukka `ip` → `FINAL`。Mac 的 VoHive `PROCESS-NAME` 与域名例外留在前段，
其 `IP-CIDR` 被移动到 IP 阶段，避免破坏 DNS 污染防护顺序。

Apple CN 在广义 Apple Services 前是有意的窄规则优先；这是首匹配语义所必需，并不
改变 `domainset → non_ip → ip` 总体约束。
