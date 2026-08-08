# Surge Rules

一套面向 Surge 的模块化规则仓库。主配置只保留有顺序意义的规则骨架，
大量域名按“最终策略”拆成远程 `DOMAIN-SET`，从而减少重复、顺序错误和后续维护成本。

## 设计目标

- 保留地区第一方金融域名的既有分流语义。
- 用精确后缀恢复 Bilibili 视频 CDN 的前置直连，避免被共享 Reject/CDN 规则抢先命中。
- 仅恢复淘宝/天猫品牌互动页依赖的 mini-app 运行时，不对整个淘宝广告域放行。
- 将 Crypto 与 Web3 拆开，避免一个策略切换影响另一类服务。
- 在全局 STUN 拦截前精确放行 Google Voice 的控制与媒体通道。
- 将 Bybit 的已确认 App/API 域名从通用 Crypto 余量中拆出。
- 为 APNs 提供 SYSTEM 之前的精确、可选稳定出口。
- 将跨地区金融、KYC/身份验证、设备指纹/反欺诈拆成独立策略层。
- 通过零依赖校验器和 GitHub Actions 阻止格式错误、重复、跨策略覆盖和主规则顺序回归。
- 禁止未经批准的宽泛共享后缀和 `DOMAIN-KEYWORD`，让自定义规则保持可审计。

Surge 按从上到下的顺序匹配，首条命中生效。`DOMAIN-SET` 适合大量域名：

- `example.com` 只匹配精确域名；
- `.example.com` 匹配根域名及其子域名。

规则文件中只写域名，不写 `DOMAIN-SUFFIX`、策略名或逗号。

## 文件与策略

| 文件 | 目标策略 | 用途 |
| --- | --- | --- |
| `google-voice.conf` | `GoogleVoice-Control` | Google Voice 页面、信令与呼叫控制 |
| `google-voice-media.conf` | `GoogleVoice-Media` | Google Voice STUN；UDP 媒体 IP/端口保留在主 Rule |
| `bilibili-direct.conf` | `DIRECT` | Bilibili 视频 CDN 精确前置直连 |
| `taobao-functional.conf` | `DIRECT` | 淘宝/天猫品牌互动小程序运行时，优先于共享 Reject |
| `polymarket.conf` | `Res-Frontier` | Polymarket 官方域、精确 Auth0 租户及实测 S3 上传主机 |
| `apple-ai.conf` | `AIGC` | Apple Intelligence、Siri、PCC |
| `direct-cn.conf` | `DIRECT` | 中国大陆银行与银联 |
| `hk-finance.conf` | `HK-FINANCE` | 香港金融 |
| `sg-finance.conf` | `SG-FINANCE` | 新加坡金融 |
| `jp-finance.conf` | `JP-FINANCE` | 日本金融 |
| `kr-finance.conf` | `KR-FINANCE` | 韩国金融 |
| `uk-finance.conf` | `UK-FINANCE` | 英国金融 |
| `us-residential.conf` | `Res-Frontier` | 美国第一方金融、Apple Cash/Pay 与 PayPal |
| `finance-context.conf` | `Finance` | 无法仅按域名判断地区的金融服务 |
| `identity-context.conf` | `Identity` | KYC 与身份验证服务 |
| `risk-context.conf` | `Identity` | 保守的设备情报与指纹服务活动集 |
| `bybit.conf` | `Crypto` | Bybit 官方 App/API 域名，优先于通用 Crypto |
| `crypto.conf` | `Crypto` | 中心化交易所 |
| `web3.conf` | `Web3` | 钱包、RPC、DeFi、NFT、浏览器 |
| `apple-push.conf` | `Apple-Push` | APNs 长连接，优先于内建 `SYSTEM` |
| `adblock4limbo-supplement.conf` | `REJECT` | Adblock4limbo 经清洗、去重并减去 SKK 覆盖后的补集 |

`archive/` 中的文件永远不被主规则加载。当前没有任何被确认停用的域名。

## 接入

1. 确认现有配置已经定义表格及主 Rule 使用的所有策略名。
2. 确认 `Apple`、`AIGC`、`Res-Frontier`、`Identity`、
   `GoogleVoice-Control`、`GoogleVoice-Media`、`Apple-Push` 和各地区金融组
   已选中所需出口。
   `Identity` 的稳定 `select` 定义可直接使用
   [snippets/identity-policy-groups.conf](snippets/identity-policy-groups.conf)；
   实时通信组见
   [snippets/service-policy-groups.conf](snippets/service-policy-groups.conf)。
3. 在以下两种 Rule 中选择一种，不要同时加载：
   - 推荐：[surge-main.conf](surge-main.conf)，通过 21 个远程 DOMAIN-SET 加载当前活动规则；
   - 展开：[surge-expanded.conf](surge-expanded.conf)，把同样的活动规则全部写回 `[Rule]`，可整段复制。
4. 在 Surge 的外部资源页面刷新，确认 21 个本仓库规则集均成功加载。

展开版由 `scripts/build_expanded.py` 自动生成，与远程版的活动域名语义一致。
它用于检查和整段复制，不应手工编辑。修改对应 DOMAIN-SET 后运行：

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

Private Relay 严格按 17 段契约使用 `Apple`。
Apple Intelligence 严格使用 `AIGC`。
Apple Cash/Pay 与 PayPal 按配置所有者的明确账户地区选择收录在
`us-residential.conf`，命中 `Res-Frontier`；这些服务本身并非天然只属于美国。

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
python3 scripts/check_upstreams.py --timeout 15 --retries 2
```

核对完整 Surge 配置中的策略是否存在，并确认敏感金融策略及 Google Voice
使用固定代理或手动 `select`。`Apple-Push` 只要求存在；仓库提供的定义刻意使用
`fallback` 自动切换可用 APNs 出口：

```bash
python3 scripts/check_profile_policies.py \
  --profile /path/to/profile.conf \
  --supplement snippets/identity-policy-groups.conf \
  --supplement snippets/service-policy-groups.conf \
  --require-stable \
  Finance HK-FINANCE SG-FINANCE JP-FINANCE KR-FINANCE UK-FINANCE \
  Res-Frontier "United States" Identity GoogleVoice-Control GoogleVoice-Media
```

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

## Identity 与 Risk 的边界

跨地区第一方金融仍进入 `Finance`。KYC/身份验证进入
`identity-context.conf`，设备情报与指纹服务进入 `risk-context.conf`，两者统一使用
稳定的手动 `Identity` 策略。宽泛 Persona 根域和通用反欺诈 SaaS 不在活动文件中；
验证码等未列入活动文件的共享服务仍按实际日志精确补充。

本仓库只负责分流结构与规则数据，不包含节点、代理凭据或订阅。
它不能保证银行或支付服务不触发风控；稳定、固定的账户地区和正常使用行为
比持续扩大共享验证规则更重要。

## 实时通信与 Apple 连续互通

Google Voice 的页面、信令和呼叫控制进入 `GoogleVoice-Control`，默认可选择
`Res-Frontier`；精确 STUN 主机以及 Google Workspace Voice 官方公布的 UDP
端口和专用 IP 段进入 `GoogleVoice-Media`，其他 STUN 仍保持拒绝。仓库把
`DIRECT` 放在媒体组首位，是基于当前用户网络已完成的直连拨号 A/B；它会形成
美国控制面与本地媒体面的出口分离。若直连媒体异常，只切换
`GoogleVoice-Media` 到已实测支持 UDP Relay 的固定美国节点，无需改变页面
与账户控制出口。官方媒体 IP 明确限定为 Workspace Voice；个人 Voice 必须用
实际拨号日志确认命中，不能把策略类型检查当作 UDP 可用性证明。

`apple-push.conf` 只在 Surge iOS 实际接管 APNs 时生效。论坛的 Surge 实测中，
Wi-Fi 下仅代理 `*.push.apple.com` 可能已足够；蜂窝网络还需要同时开启
`include-all-networks` 与 `include-apns`。将
[snippets/ios-apns-capture.conf](snippets/ios-apns-capture.conf) 中的键合并到
`[General]`，不要新建第二个同名段；改动后开启飞行模式数秒，让原有
APNs 长连接断开并重建。主规则仅覆盖 `*.push.apple.com`、其 APNs CNAME
和 Apple 公开网段上的 TCP 5223，不代理整个 `17.0.0.0/8`或整个 Apple
规则集，以避免论坛已反馈的 iCloud 照片同步异常。

`include-all-networks=true` 可能影响 AirDrop/Continuity，因此保持
`include-local-networks=false` 和 `include-cellular-services=false`，并在同一 Wi-Fi 上做
开/关 Surge 对照。APNs 链路恢复后，若仅 Telegram 官方客户端仍无横幅/
声音，而其他推送或第三方 Telegram 客户端正常，则属于官方客户端的独立故障，
不应再扩大 Apple 代理范围。

Bybit 规则只修复官方 `.bytick.com` API 落入 `FINAL` 的漏匹配。
`Crypto` 的最终出口必须与账户本人真实、获支持的地区一致；不应使用
规则去规避服务商的地区与合规限制。

## 官方参考

- [Surge Ruleset](https://manual.nssurge.com/rule/ruleset.html)
- [Surge Domain-based Rule](https://manual.nssurge.com/rule/domain-based.html)
- [Surge Policy Group](https://manual.nssurge.com/policy/group.html)
- [Google Voice connectivity requirements](https://knowledge.workspace.google.com/admin/voice/voice-connectivity-requirements)
- [SukkaW/Surge 使用说明](https://github.com/SukkaW/Surge)
- [blackmatrix7 WeChat 规则说明](https://github.com/blackmatrix7/ios_rule_script/tree/master/rule/Surge/WeChat)
- [ddgksf2013/Filter](https://github.com/ddgksf2013/Filter)
