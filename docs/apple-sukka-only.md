# Apple 基础分流回归 Sukka（2026-09-16）

按配置所有者最新澄清“保留 Sukka 全部”，原先已启用的 Sukka 订阅全部保留。撤销的是
Apple 支付、账户、账单及私密转送的住宅出口绑定，不是删除 Sukka 官方资源。上轮把
Private Relay 订阅一并移除是误解，现已恢复到两份设备 Profile 的原位置，并改绑
`United States`，不恢复 `Res-Frontier`。同时登记到主骨架的 `DOMAIN-SET` 阶段及契约，
防止后续模板再次删除。此澄清取代本页上一版“仅四个资源、不加载 Private Relay”的决定，
也取代 2026-09-15 恢复六条账户/账单自定义规则的决定；非 Apple 金融地区不变。

## 删除与保留

- `us-residential.conf` 删除 `.applecash.apple.com`、`.applepay.apple.com`、
  `apple-pay-gateway.apple.com`。
- 停用 `apple-account-payment-rules.conf` 的六条规则：`account.apple.com`、
  `appleid.cdn-apple.com`、`idmsa.apple.com`、`gsa.apple.com`、`buy.itunes.apple.com`、
  `*-buy.itunes.apple.com`。旧 URL 留为只有注释的兼容空文件；主骨架、manifest、
  contract、展开版与设备 Profile 不再引用。
- Mac 与 iCloud Profile 删除上述自有 RULE-SET 引用；
  `domainset/icloud_private_relay.conf` 官方订阅恢复并保留，只将住宅绑定改为
  `United States`。没有关闭系统私密转送，也没有新增自定义 Private Relay 主机或 Apple 全域规则。
- 非 Apple 金融规则、节点、策略组、DNS、MITM、General 和现有模块保持不变。
- 保留原先已启用的全部 Sukka 资源，不额外开启其他无关可选专项。

## 公共资源与实际含义

| Sukka 资源 | 现有策略 | 删除住宅例外后的代表主机 |
| --- | --- | --- |
| `domainset/apple_cdn.conf` | DIRECT | `appleid.cdn-apple.com`、`buy.itunes.apple.com` 及 `*-buy` 账单分片 |
| `domainset/icloud_private_relay.conf` | United States | 上游列出的 Private Relay 端点，保留独立订阅与自动更新 |
| `non_ip/apple_cn.conf` | DIRECT | Apple 中国特定服务 |
| `non_ip/apple_services.conf` | United States | Apple Pay/Cash、账户 `account/idmsa/gsa`，及未先命中 Private Relay 专表的 Apple 服务 |
| `non_ip/apple_intelligence.conf` | United States | 该上游定义的 Apple Intelligence 服务 |

Sukka 不替用户指定代理节点所在国家；上表沿用当前已配置策略，不新建或调整节点。
CDN 与中国特定域直连、其他服务代理仍是多出口，并不代表“整个 Wallet 同一 IP”。
本轮消除的是无须继续保留的额外住宅覆盖，不承诺绑卡、PayPal 付款或开户一定成功。

依据：[Sukka 官方 README](https://github.com/SukkaW/Surge)、
[Apple CDN](https://ruleset.skk.moe/List/domainset/apple_cdn.conf)、
[Apple Services](https://ruleset.skk.moe/List/non_ip/apple_services.conf)、
[Apple CN](https://ruleset.skk.moe/List/non_ip/apple_cn.conf)、
[Private Relay](https://ruleset.skk.moe/List/domainset/icloud_private_relay.conf)。
Private Relay 的端点虽也被 `.icloud.com`／`.apple-dns.net` 等公共后缀覆盖，但这不是
删除用户已启用订阅的理由。保留官方专表，不复制主机，也不再绑定住宅出口。

## 边界与验收

这是基础 Profile 规则层的调整，不是删除已保留的 iRingo/WeatherKit/Maps/News/TV
模块。它们仍可注入 Apple 精确域名和 QUIC/IP 条件，因此不能把结果描述成
“设备全部 Apple 请求只受 Sukka 控制”。未改写模块或移除金融 MITM 保护。

独立回归要求：自有活动域集不能包含 Apple 命名空间；九条旧覆盖不可重新引入；
五个 Sukka Apple 资源和既有设备顺序保持；24 个非 Apple 金融 App 的锚点与出口不得削弱。
主骨架为 54 条规则、32 个 Sukka 资源（8 个 DOMAIN-SET），自有活动资源仍为 15 个、741 条域名。
公共上游覆盖、实际有效规则、资源刷新与设备配置分别验证。iCloud 文件同步不等于
iPhone 已重载；手机仍需更新配置并刷新外部资源，且无需为验收主动进行付款或绑卡。

上一轮审计报告保留原样，记录当时已删订阅的状态，不作为恢复后的最终首命中证明。
