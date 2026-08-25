# Surge Rules

这是一套以 [SukkaW/Surge](https://github.com/SukkaW/Surge) 为基础骨架、
面向当前 iPhone 与 Mac 配置的精简规则层。主配置只保留两类内容：

1. Sukka 官方公开 `List` 资源及其严格顺序；
2. 无法由公共规则表达的固定地区银行、住宅风控、Crypto、Web3 与少量系统例外。

模块、节点、策略组、MITM、Rewrite 和订阅不属于本仓库的规则重建范围；现有模块继续
保留并由 Surge 在各设备上独立叠加。

## 核心原则

Sukka 官方要求所有域名规则与 `DOMAIN-SET` 先于全部 `non_ip`，全部 `non_ip`
再先于任何 IP 类规则，最后才是 `FINAL`。本仓库把这个约束固化为五段契约：

1. 精确系统、Apple 与账户链路；
2. 固定地区与高风控业务；
3. Sukka `DOMAIN-SET`；
4. Sukka `non_ip`；
5. Sukka `ip` 与 `FINAL`。

所有自定义 `DOMAIN`、`DOMAIN-SUFFIX`、`DOMAIN-WILDCARD` 和远程
`DOMAIN-SET` 均位于 IP 阶段之前。校验器会拒绝任何把域名或 `non_ip` 规则放到
IP 阶段之后的修改。

Apple CN 是有意放在宽泛 `apple_services` 之前的窄规则例外；否则
`apple_services` 中的 Apple 广义后缀会先命中，Apple CN 的 `DIRECT` 将失效。
Microsoft CDN 同理位于 Microsoft 广义规则之前。

## 为什么不在基础规则重复广告拦截

Sukka README 明确只建议在 Surge for Mac 使用其大型 Reject 集，移动端建议使用专门
工具。当前配置已经保留多套广告与 MITM 模块，因此基础规则不再加载 Sukka Reject、
Adblock4limbo 补集、全局 STUN 拒绝或 URL-REGEX 拦截。这样可以避免同一请求同时经过
多层拦截、降低误杀与资源开销；这不是删减现有模块。

## Apple 与系统链路

- Apple 官方 Software Updates 的 21 个精确主机直接内联为 `DIRECT`，系统更新不再
  依赖 GitHub 外部资源先刷新成功。
- Apple Account 与 App Store 账单只固定 5 个精确主机及动态 `*-buy` 分片到
  `Res-Frontier`，不扩大到整个 Apple/iTunes。
- Private Relay 的 6 个精确入口固定普通 `United States`，并置于 iCloud 直连层前。
- iCloud、CloudKit、Photos、iWork 与内容传输域精确直连；Apple CN/CDN 继续直连。
- GitHub 与 `githubusercontent.com` 固定香港出口，保证保留模块的发布资源可更新。
- `include-apns=false` 的设备模式保持不变，基础规则不再加载不会生效的 APNs 专用覆盖。

## 本仓库活动资源

主规则通过 12 个远程本仓库 `DOMAIN-SET` 加载 630 条当前活动域名：

| 文件 | 策略 | 作用 |
| --- | --- | --- |
| `direct-cn.conf` | `DIRECT` | 中国大陆银行与银联 |
| `hk-finance.conf` | `Hong Kong` | 香港银行、券商及当前香港账户共享首方基础设施 |
| `sg-finance.conf` | `Singapore` | 新加坡金融 |
| `jp-finance.conf` | `Japan` | 日本金融 |
| `kr-finance.conf` | `Korea` | 韩国金融 |
| `uk-finance.conf` | `United Kingdom` | 英国金融 |
| `us-residential.conf` | `Res-Frontier` | 美国金融、X、Google Account/Voice 与 Polymarket |
| `finance-context.conf` | `Res-Frontier` | 地区无法从主机名可靠判断的金融首方域 |
| `identity-context.conf` | `Res-Frontier` | KYC 与身份验证共享基础设施 |
| `risk-context.conf` | `Res-Frontier` | 设备情报、指纹与反欺诈基础设施 |
| `crypto.conf` | `Crypto` | Bybit 与其他中心化交易所 |
| `web3.conf` | `Web3` | 钱包、RPC、DeFi、NFT 与区块浏览器 |

同一策略下原有的小文件已经合并：X、Google Account/Voice、Polymarket 合入
`us-residential.conf`；香港账户上下文合入 `hk-finance.conf`；Bybit 合入
`crypto.conf`。旧文件仍保留在仓库供历史追踪，但不再被主规则引用。

共享 KYC 和风控供应商无法仅根据域名判断调用它的是哪家银行；Surge iOS 也无法按
请求来源 App 为同一共享域名动态选择地区。因此这两层只保留经过审计的窄后缀，并按
当前账户使用场景固定住宅出口，不加入 `.auth0.com`、`.cloudflare.com`、
`.medallia.com` 等宽泛共享后缀。

## Sukka 公共分流

当前使用的官方资源均来自统一基址 `https://ruleset.skk.moe/List/`：

- `speedtest`、`cdn` → `PROXY`；
- `stream`、`ai`、`apple_intelligence` → `United States`；
- `apple_cdn`、`apple_cn`、`microsoft_cdn`、`lan`、`domestic`、`direct` → `DIRECT`；
- `apple_services`、`microsoft` → `United States`；
- `download` → `Hong Kong`；
- Telegram 官方 CIDR → `Singapore`；
- `global` 与 `FINAL` → `PROXY`；
- 中国 IP → `DIRECT`。

Telegram 仅加载作者推荐的官方 CIDR，不加载可选 ASN 或重复的域名列表。IPv6 当前未
启用，因此不加载 China IPv6 资源。`nano.cr18.eu.org` 是唯一保留的 Emby 精确例外，
固定新加坡，不再加载整个第三方 Emby 总表。

## 接入与校验

`surge-main.conf` 是远程资源版；`surge-expanded.conf` 仅用于审计和整段复制，
由生成器维护。接入前应确认策略组存在：`Res-Frontier`、`PROXY`、`Hong Kong`、
`Singapore`、`Japan`、`Korea`、`United Kingdom`、`United States`、`Crypto`、
`Web3`。

在 Surge 的外部资源页面刷新，并确认 12 个本仓库规则文件均成功加载。随后执行：

```bash
python3 scripts/validate.py --strict
python3 scripts/build_expanded.py --check
python3 -m unittest discover -s tests -v
python3 scripts/check_upstreams.py --timeout 15 --retries 2
python3 scripts/check_module_compatibility.py
```

完整配置还可以用 Surge 自带检查器验证：

```bash
/Applications/Surge.app/Contents/Applications/surge-cli --check /path/to/Sukka.conf
```

## 维护边界

- 优先从 Surge 请求日志取得真实主机名，再加入足够窄的精确域或后缀。
- 地区银行必须进入对应地区文件，不应因 App Store 下载地区而统一改成美国出口。
- Crypto 与 Web3 使用不同策略，避免交易所地区限制与链上服务可用性互相牵连。
- 不添加 Gate 专用覆盖；Gate 未命中自定义 Crypto 时按 Sukka/最终规则正常分流。
- 不使用 `DOMAIN-KEYWORD` 或公共云、KYC、CDN 的宽泛根域做“兜底”。
- 模块顺序与 MITM 保护边界分别见 [module-order](docs/module-order.md) 和
  [module-baseline](docs/module-baseline.md)，规则重建不会删除或改写模块。

迁移详情见 [migration-notes](docs/migration-notes.md)，需求映射见
[requirements-matrix](docs/requirements-matrix.md)，数量对账见
[source-parity](docs/source-parity.md)。

## 官方参考

- [SukkaW/Surge README](https://github.com/SukkaW/Surge/blob/master/README.md)
- [Sukka Ruleset 服务](https://ruleset.skk.moe/)
- [Surge Ruleset](https://manual.nssurge.com/rule/ruleset.html)
- [Surge Domain-based Rule](https://manual.nssurge.com/rule/domain-based.html)
- [Apple Software Updates network requirements](https://support.apple.com/en-us/101555)
