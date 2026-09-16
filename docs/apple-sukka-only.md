# Apple 基础分流回归 Sukka（2026-09-16）

按配置所有者最新要求，Apple 基础域名分流只使用已有 Sukka 公共资源，撤销 Apple
支付、账户、账单及私密转送的住宅出口例外。此决定取代 2026-09-15 恢复六条账户/
账单规则以及随后保留它们的决定；不改变非 Apple 金融 App 的地区选择。

## 删除与保留

- `us-residential.conf` 删除 `.applecash.apple.com`、`.applepay.apple.com`、
  `apple-pay-gateway.apple.com`。
- 停用 `apple-account-payment-rules.conf` 的六条规则：`account.apple.com`、
  `appleid.cdn-apple.com`、`idmsa.apple.com`、`gsa.apple.com`、`buy.itunes.apple.com`、
  `*-buy.itunes.apple.com`。旧 URL 留为只有注释的兼容空文件；主骨架、manifest、
  contract、展开版与设备 Profile 不再引用。
- Mac 与 iCloud Profile 删除上述 RULE-SET 引用，以及
  `domainset/icloud_private_relay.conf → Res-Frontier` 的额外绑定。没有关闭系统私密
  转送功能，也没有新增其他 Private Relay 或 Apple 全域规则。
- 非 Apple 金融规则、节点、策略组、DNS、MITM、General 和现有模块保持不变。

## 公共资源与实际含义

| Sukka 资源 | 现有策略 | 删除住宅例外后的代表主机 |
| --- | --- | --- |
| `domainset/apple_cdn.conf` | DIRECT | `appleid.cdn-apple.com`、`buy.itunes.apple.com` 及 `*-buy` 账单分片 |
| `non_ip/apple_cn.conf` | DIRECT | Apple 中国特定服务 |
| `non_ip/apple_services.conf` | United States | Apple Pay/Cash、账户 `account/idmsa/gsa`、Private Relay 已知主机 |
| `non_ip/apple_intelligence.conf` | United States | 该上游定义的 Apple Intelligence 服务 |

Sukka 不替用户指定代理节点所在国家；上表沿用当前已配置策略，不新建或调整节点。
CDN 与中国特定域直连、其他服务代理仍是多出口，并不代表“整个 Wallet 同一 IP”。
本轮消除的是无须继续保留的额外住宅覆盖，不承诺绑卡、PayPal 付款或开户一定成功。

依据：[Sukka 官方 README](https://github.com/SukkaW/Surge)、
[Apple CDN](https://ruleset.skk.moe/List/domainset/apple_cdn.conf)、
[Apple Services](https://ruleset.skk.moe/List/non_ip/apple_services.conf)、
[Apple CN](https://ruleset.skk.moe/List/non_ip/apple_cn.conf)。
Private Relay 的可选表端点已被 `.icloud.com`／`.apple-dns.net` 等公共后缀承接，
不需要再复制域名或绑定住宅出口。

## 边界与验收

这是基础 Profile 规则层的调整，不是删除已保留的 iRingo/WeatherKit/Maps/News/TV
模块。它们仍可注入 Apple 精确域名和 QUIC/IP 条件，因此不能把结果描述成
“设备全部 Apple 请求只受 Sukka 控制”。未改写模块或移除金融 MITM 保护。

独立回归要求：自有活动域集不能包含 Apple 命名空间；九条旧覆盖不可重新引入；
四个既有 Sukka 资源和顺序保持；24 个非 Apple 金融 App 的锚点与出口不得削弱。
公共上游覆盖、实际有效规则、资源刷新与设备配置分别验证。iCloud 文件同步不等于
iPhone 已重载；手机仍需更新配置并刷新外部资源，且无需为验收主动进行付款或绑卡。
