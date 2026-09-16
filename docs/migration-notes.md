# Migration Notes

## 2026-09-16 最新澄清：保留原先全部 Sukka 订阅

用户明确“我要的是保留 Sukka 全部”。上轮把 Private Relay 官方订阅与住宅绑定一并
删除是误解，现已在两份设备 Profile 原位置恢复 `icloud_private_relay.conf`，并改绑
`United States`；主骨架和契约也登记此资源，防止模板再次遗漏。Apple 共五个 Sukka
资源，Sukka 总计 32 个；不新增其他无关可选集，不恢复九条自定义住宅规则。
本节取代下述“仅四个资源”及删除 Private Relay 订阅的决定；旧审计报告不改写。

## 2026-09-16 Apple 回归 Sukka（历史步骤，以上节澄清为准）

按最新要求撤销 Apple 支付三条住宅域和账户/账单六条 RULE-SET，移除设备上的
Private Relay 住宅专项。复用四个现有 Sukka 资源，非 Apple 金融和模块保持不变。
本节取代下述 9 月 15 日恢复 Apple 窄规则的决定，见 [完整说明](apple-sukka-only.md)。

## 2026-09-15 完整性修复

- 将已部署的 MEXC 瑞士清单纳入 manifest、主骨架和生成流程，防止旧展开版恢复 Crypto 归属。
- 对齐实际金融顺序 CH → UK → HK → SG → JP → KR，给 HSBC Expat 建立精确、策略和顺序均受约束的重叠例外。
- 恢复 Apple 账户/账单六条窄 RULE-SET，与 PayPal 使用同一住宅策略，不恢复历史 Apple 全域/更新/iCloud 例外。
- 同步文档和展开版，增加点名业务、共享边界、窄例外反例和未验收认证项的自动检查。
- 广告平台模块只排除原有五个短信白名单主机，其他内容及模块状态保留；上游更新后必须重新检查补丁是否被覆盖。
- `identity-context.conf`、General、DNS、MITM、节点、策略组和兼容性开关不变。iPhone 的配置源同步不等于设备已加载，模块也须逐设备检查。

下文为历史迁移记录；Apple 当前状态以最上方 2026-09-16 最新澄清为准。

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
合并后的业务资源。Supercell 后续以自有精确域名集补齐账户与各款游戏域，
战斗服务器则直接引用 Blackmatrix7 的现成混合集，避免复制 GPL 内容和制造静态快照。

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
