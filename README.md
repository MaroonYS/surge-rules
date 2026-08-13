# Surge Rules

一套面向 Surge 的模块化规则仓库。主配置只保留有顺序意义的规则骨架，
大量域名按“最终策略”拆成远程 `DOMAIN-SET`，IP/端口组合拆成远程
`RULE-SET`，从而减少重复、顺序错误和后续维护成本。

## 设计目标

- 保留地区第一方金融域名的既有分流语义。
- 用精确后缀恢复 Bilibili 视频 CDN 的前置直连，避免被共享 Reject/CDN 规则抢先命中。
- 仅恢复淘宝/天猫品牌互动页依赖的 mini-app 运行时，不对整个淘宝广告域放行。
- 将 Crypto 与 Web3 拆开，避免一个策略切换影响另一类服务。
- 在全局 STUN 拦截前精确放行 Google Voice 的控制与媒体通道。
- 将 Google Account 登录、账户管理与 OAuth 控制面收口到稳定住宅出口。
- 将 Bybit 的已确认 App/API 域名从通用 Crypto 余量中拆出。
- 为 APNs 提供 SYSTEM 之前的精确、可选稳定出口。
- 将 Google Voice 与 APNs 的逻辑 `AND` 规则移入独立、无策略列的远程 `RULE-SET`。
- 将跨地区金融、KYC/身份验证、设备指纹/反欺诈拆成独立策略层。
- 将当前账户使用的 HSBC HK、Futu/Moomoo HK 与 Longbridge HK 共享基础设施固定到香港金融上下文。
- 通过零依赖校验器和 GitHub Actions 阻止格式错误、重复、跨策略覆盖和主规则顺序回归。
- 用机器可读模块兼容清单固定全部保留模块所需的 21 个 Apple MITM 前置主机，
  不从第三方脚本自动扩域。
- 分别记录 [Mac 与 iPhone 的模块有效顺序](docs/module-order.md)，仅按作者硬约束
  调整优先级，不对无依据的模块做推测性重排。
- 禁止未经批准的宽泛共享后缀和 `DOMAIN-KEYWORD`，让自定义规则保持可审计。

Surge 按从上到下的顺序匹配，首条命中生效。`DOMAIN-SET` 适合大量域名：

- `example.com` 只匹配精确域名；
- `.example.com` 匹配根域名及其子域名。

`DOMAIN-SET` 文件中只写域名，不写 `DOMAIN-SUFFIX`、策略名或逗号。
`RULE-SET` 文件每行写一条完整规则声明，但不写策略列；策略由主 Rule 的外层
`RULE-SET` 统一指定。

## 文件与策略

| 文件 | 目标策略 | 用途 |
| --- | --- | --- |
| `google-account.conf` | `Res-Frontier` | Google Account 登录、账户管理与 OAuth 控制面 |
| `google-voice.conf` | `Res-Frontier` | Google Voice 页面、信令与呼叫控制 |
| `google-voice-media.conf` | `DIRECT` | Google Voice STUN 主机 |
| `google-voice-media-rules.conf` | `DIRECT` | Google Voice UDP 媒体 IP/端口逻辑规则 |
| `bilibili-direct.conf` | `DIRECT` | Bilibili 视频 CDN 精确前置直连 |
| `taobao-functional.conf` | `DIRECT` | 淘宝/天猫品牌互动小程序运行时，优先于共享 Reject |
| `polymarket.conf` | `Res-Frontier` | Polymarket 官方域、精确 Auth0 租户及实测 S3 上传主机 |
| `apple-ai.conf` | `United States` | Apple Intelligence、Siri、PCC |
| `direct-cn.conf` | `DIRECT` | 中国大陆银行与银联 |
| `hk-finance.conf` | `Hong Kong` | 香港金融 |
| `hk-finance-context.conf` | `Hong Kong` | 当前账户的香港汇丰及香港券商共享基础设施 |
| `sg-finance.conf` | `Singapore` | 新加坡金融 |
| `jp-finance.conf` | `Japan` | 日本金融 |
| `kr-finance.conf` | `Korea` | 韩国金融 |
| `uk-finance.conf` | `United Kingdom` | 英国金融 |
| `apple-account-payment-rules.conf` | `Res-Frontier` | Apple Account 登录控制面、App Store 账单根域与动态 `*-buy` 分片 |
| `us-residential.conf` | `Res-Frontier` | 美国第一方金融、Apple Cash/Pay 与 PayPal |
| `finance-context.conf` | `Res-Frontier` | 无法仅按域名判断地区的金融服务 |
| `identity-context.conf` | `Verification` | KYC 与身份验证服务 |
| `risk-context.conf` | `Verification` | 保守的设备情报与指纹服务活动集 |
| `bybit.conf` | `Bybit` | Bybit 官方 App/API 域名，独立受支持地区策略 |
| `crypto.conf` | `Crypto` | 中心化交易所 |
| `web3.conf` | `Web3` | 钱包、RPC、DeFi、NFT、浏览器 |
| `apple-push.conf` | `United States` | APNs 长连接，优先于内建 `SYSTEM` |
| `apple-push-rules.conf` | `United States` | Apple 公布网段上的 APNs TCP 5223 逻辑规则 |
| `adblock4limbo-supplement.conf` | `REJECT` | Adblock4limbo 经清洗、去重并减去 SKK 覆盖后的补集 |

`archive/` 中的文件永远不被主规则加载。当前没有任何被确认停用的域名。

## 接入

1. 确认现有配置已经定义主 Rule 使用的固定策略：`Res-Frontier`、`PROXY`、
   `Hong Kong`、`Singapore`、`Japan`、`Korea`、`United Kingdom`、
   `United States`、`Bybit`、`Crypto`、`Web3` 与 `Verification`。
2. 地区组和住宅出口只使用固定代理或手动 `select`，不得自动切换账户出口。
3. 在以下两种 Rule 中选择一种，不要同时加载：
   - 推荐：[surge-main.conf](surge-main.conf)，通过 26 个远程本仓库规则文件（23 个 `DOMAIN-SET`、3 个 `RULE-SET`）加载当前活动规则；
   - 展开：[surge-expanded.conf](surge-expanded.conf)，把同样的活动规则全部写回 `[Rule]`，可整段复制。
4. 在 Surge 的外部资源页面刷新，确认 26 个本仓库规则文件均成功加载。

展开版由 `scripts/build_expanded.py` 自动生成，与远程版的活动规则语义一致。
它用于检查和整段复制，不应手工编辑。修改对应外部规则文件后运行：

```bash
python3 scripts/build_expanded.py --write
```

原始 Rule 到各文件的覆盖和有意调整记录在
[docs/migration-notes.md](docs/migration-notes.md)。
与 BiliUniverse Global 的域名边界、模块参数及持续兼容检查见
[docs/biliuniverse-global.md](docs/biliuniverse-global.md)。
逐项完成状态见 [docs/requirements-matrix.md](docs/requirements-matrix.md)。
原始 Rule、Bilibili 精确恢复、金融/身份/风控扩充及广告补集的版本数量对账见
[docs/source-parity.md](docs/source-parity.md)。
本轮金融域名的来源与边界见
[docs/domain-sources.md](docs/domain-sources.md)。

主规则使用以下公开 Raw 基址：

```text
https://raw.githubusercontent.com/MaroonYS/surge-rules/main/
```

Private Relay 与 Apple Intelligence 固定使用普通 `United States` 节点；住宅
SOCKS5 不参与 Private Relay 的 UDP/QUIC 路径。
Apple Cash/Pay 与 PayPal 按配置所有者的明确账户地区选择收录在
`us-residential.conf`；Apple Account 的 4 个精确登录控制主机、账单根域与动态
`*-buy.itunes.apple.com` 分片单独收录在
`apple-account-payment-rules.conf`。两层均命中
`Res-Frontier`，但不扩大到整个 Apple/iTunes 或共享 Braintree 基础设施。
这些服务本身并非天然只属于美国。

## 维护

新增服务时，先确认其最终策略，再把域名加入对应文件。不要按银行创建新文件。
只有你明确确认停用的域名才应移入 `archive/`，需要时可再移回正式文件。

优先从 Surge 请求日志取得真实主机名，再添加 `DOMAIN` 或足够窄的后缀。
不要为了“兜底”添加 `.apple.com`、`.auth0.com`、`.cloudflare.com` 或公共后缀；
这种规则看似覆盖更多，实际会吞掉无关服务。

本地检查：

```bash
python3 scripts/validate.py --strict
python3 scripts/build_expanded.py --check
python3 -m unittest discover -s tests -v
python3 scripts/check_biliuniverse.py --timeout 30
python3 scripts/check_module_compatibility.py
python3 scripts/check_upstreams.py --timeout 15 --retries 2
```

核对完整 Surge 配置中的策略是否存在，并确认地区、住宅与加密资产策略使用固定代理
或手动 `select`。APNs 是 TCP 5223 长连接，普通 HTTP
健康检查不能证明该端口可用，所以仓库不再使用自动 `fallback`：

```bash
python3 scripts/check_profile_policies.py \
  --profile /path/to/profile.conf \
  --require-stable \
  Res-Frontier PROXY "Hong Kong" Singapore Japan Korea \
  "United Kingdom" "United States" Bybit Crypto Web3 Verification
```

该检查器也可将 Surge 导出的“修改后配置”同时作为 `--profile` 和
`--rules`；它会识别模块的 `#!FROM-MODULE`、逻辑规则与 `pre-matching`，
避免把嵌套条件或选项误报为策略名。

生成机器可读报告：

```bash
python3 scripts/validate.py \
  --strict \
  --json-out validation-report.json
```

重新生成或核对 Adblock4limbo 补集：

```bash
python3 scripts/sync_adblock4limbo.py --write
python3 scripts/sync_adblock4limbo.py --check
```

同步器只在补集的有效规则发生变化时重写文件。上游与两个 SKK 基线的 SHA-256
属于易变来源元数据，不再写入受版本控制的规则头；自动化会把它们写入 Actions
Summary，避免“只有来源哈希变化”触发无意义提交。

`check_upstreams.py` 会读取完整正文并检查 HTTPS、内容类型、UTF-8、
Deprecated 标记、空文件、SKK 哨兵占位及外部 RULE-SET 的策略列，不再只探测 URL。
Adblock4limbo 原文件把 `reject` 写进了每一条外部规则；生成器会移除策略列、
排除宽泛关键词、去重并减去 SKK 已覆盖项。许可归属见
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。

`.github/workflows/sync-adblock4limbo.yml` 每天香港时间 02:37 轮询一次
Adblock4limbo 及两个 SKK Reject 基线，也可以从 Actions 手动运行。它会依次重新生成
`adblock4limbo-supplement.conf` 与 `surge-expanded.conf`、运行全部单元测试和严格
校验。只有这两个生成文件确实变化且全部检查通过时，才会由 GitHub Actions 机器人
直接创建提交并以普通非强制推送快进 `main`，无需人工确认或合并。

没有有效变化时不会创建提交；上游下载、生成、测试或校验失败时不会发布任何变更。
若同步期间 `main` 出现其他提交，工作流会拒绝推送并由下一次计划任务重新执行，避免
覆盖并发修改。瞬时下载错误会在当前运行中短暂重试，整个工作流失败时还会自动从最新
`main` 重新排队最多两次，不需要人工重新运行。GitHub 定时任务是轮询而不是上游
Webhook，因此临时人工更新最多约延迟 24 小时，实际执行时间还可能受 GitHub 调度
影响。仓库需要允许工作流写入内容和重新调度 Actions。

### SKK 兼容性边界

SKK 的资源类型、各非 IP 资源内部顺序和 `domainset → non_ip → ip` 总体结构均保留。
本配置有两项经过测试的有意例外，不能描述成对其示例的逐字复制：

- `reject-drop.conf` 不加 `pre-matching`。Surge 会把带该参数的拒绝规则提升到所有
  普通规则之前，导致 Bilibili 视频 CDN 与淘宝互动运行时无法由更精确的前置规则放行。
- Google Voice 与 APNs 的端口约束规则必须先于全局 STUN / `SYSTEM` 生效；其所有
  IP 子规则均带 `no-resolve`，不会为域名触发本地 DNS 查询。Blackmatrix7 的 WeChat
  文件按其 README 作为一个混合 `RULE-SET` 原样加载，其中 IP 子规则同样自带
  `no-resolve`。

这是对多个上游约束和本配置实测例外的显式取舍，不应删除 `no-resolve`，也不应在
未重新验证 Bilibili、淘宝、Google Voice 与 APNs 前恢复 `pre-matching`。

## Identity 与 Risk 的边界

跨地区第一方金融、KYC/身份验证、设备情报与指纹服务仍分别保留 Finance、Identity、
Risk 三个语义层。Finance 继续固定到 `Res-Frontier`；Identity 与 Risk 在运行时统一
进入手动 `Verification` 组，以便与当次 Bybit、Crypto 或 Web3 业务保持同一合规地区出口。
`Verification` 默认保持 `Res-Frontier`，以延续现有美国金融流程；进行 Bybit、Crypto
或 Web3 的登录、实名与高风险操作前，应手动选择对应业务组，也可用 `REJECT` 暂停共享
验证域。它不能自动判断调用 App，也不应用于伪装账户地区。
`rules-manifest.json` 的 `semantic_role` 继续让校验器按原边界检查。宽泛 Persona 根域和
通用反欺诈 SaaS 不在活动文件中；
验证码等未列入活动文件的共享服务仍按实际日志精确补充。

本仓库只负责分流结构与规则数据，不包含节点、代理凭据或订阅。
它不能保证银行或支付服务不触发风控；稳定、固定的账户地区和正常使用行为
比持续扩大共享验证规则更重要。

## 实时通信与 Apple 连续互通

Google Account 的 6 个精确登录、管理与 OAuth 主机在 Google Voice 之前固定到
`Res-Frontier`。Google Voice 的页面、信令和呼叫控制同样固定到
`Res-Frontier`；5 个精确 STUN 主机以及
Google Workspace Voice 官方公布的 UDP 端口和专用 IP 段固定到 `DIRECT`，其他
STUN 仍保持拒绝。该配置基于当前用户网络已完成的直连拨号 A/B；它会形成
美国控制面与本地媒体面的出口分离。若直连媒体异常，只切换
对应三条媒体规则的策略到已实测支持 UDP Relay 的固定美国节点，无需改变页面与
账户控制出口。官方媒体 IP 明确限定为 Workspace Voice；个人 Voice 必须用
实际拨号日志确认命中，不能把策略类型检查当作 UDP 可用性证明。

两个 `apple-push` 规则文件只在 Surge iOS 实际接管 APNs 时生效。蜂窝网络需要
同时开启 `include-all-networks` 与 `include-apns`。将
[snippets/ios-apns-capture.conf](snippets/ios-apns-capture.conf) 中的键合并到现有
`[General]`，不要新建第二个同名段；改动后开启飞行模式数秒，让原有 APNs
长连接断开并重建。主规则覆盖 `*.push.apple.com`、其 CNAME、Apple 公布的窄网段，
并以 Apple 建议的整个 `17.0.0.0/8` 作为仅限 TCP 5223 的 IPv4 兜底。它不会代理
17/8 上的普通 HTTPS 或整个 Apple 规则集。

Surge 官方明确警告 `include-all-networks=true` 可能影响 AirDrop。不要使用
`include-all-networks=true`、`include-apns=false` 这个中间态：它承担 Continuity
副作用，却没有让 APNs 进入规则系统。仓库提供两个互斥片段：

- [ios-continuity.conf](snippets/ios-continuity.conf)：AirDrop/Handoff 优先，APNs 直连。
- [ios-apns-capture.conf](snippets/ios-apns-capture.conf)：接管 APNs，用于多款国际 App
  的推送均无法直连时；该模式在受影响的 iOS 版本上仍可能妨碍 AirDrop。

先用 Continuity 模式确认 AirDrop/Handoff；只有在多款国际 App 都不能推送时才切换
APNs 模式。若其他推送正常，仅 Telegram 官方客户端无横幅/声音或打开 App 后才出现，
则属于 Telegram/iOS 独立故障，不应继续扩大 Apple 代理范围。

`RULE-SET,SYSTEM,DIRECT` 保留在 Private Relay、Apple Intelligence/Siri 与 APNs
三个精确例外之后、宽泛 Apple Services 之前。Surge 的内建 `SYSTEM` 覆盖大多数
iOS/macOS 自身请求，但不包含 App Store、iTunes 等内容服务；这个位置既让三个例外
按指定策略接管，也避免后面的 `.apple.com` / `.icloud.com` 聚合规则代理过多系统流量。

Bybit 规则只修复官方 `.bytick.com` API 落入 `FINAL` 的漏匹配，并进入独立
`Bybit` 组。该组只能加入与账户本人真实且受支持地区一致的策略；
不得复用包含受限地区的宽泛 `Crypto` 组。

模块会覆盖主 Profile，且启用状态不会跨设备同步。保留全部模块时的实际命中条件、
已知不可覆盖冲突与逐设备检查见 [docs/module-baseline.md](docs/module-baseline.md)。

## 官方参考

- [Surge Ruleset](https://manual.nssurge.com/rule/ruleset.html)
- [Surge Logical Rule](https://manual.nssurge.com/rule/logical-rule.html)
- [Surge Domain-based Rule](https://manual.nssurge.com/rule/domain-based.html)
- [Surge Policy Group](https://manual.nssurge.com/policy/group.html)
- [Surge Modules](https://manual.nssurge.com/others/module.html)
- [Surge iOS Miscellaneous Options](https://manual.nssurge.com/others/misc-options.html)
- [Apple APNs network requirements](https://support.apple.com/102266)
- [Google Voice connectivity requirements](https://knowledge.workspace.google.com/admin/voice/voice-connectivity-requirements)
- [Bybit Service Restricted Countries](https://www.bybit.com/en/help-center/article/Service-Restricted-Countries)
- [SukkaW/Surge 使用说明](https://github.com/SukkaW/Surge)
- [blackmatrix7 WeChat 规则说明](https://github.com/blackmatrix7/ios_rule_script/tree/master/rule/Surge/WeChat)
- [ddgksf2013/Filter](https://github.com/ddgksf2013/Filter)
