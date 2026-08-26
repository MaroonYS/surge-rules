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

1. 协议与模块资源；
2. 固定地区与高风控业务；
3. Sukka `DOMAIN-SET`；
4. Sukka `non_ip`；
5. Sukka `ip` 与 `FINAL`。

所有自定义 `DOMAIN`、`DOMAIN-SUFFIX`、`DOMAIN-WILDCARD` 和远程
`DOMAIN-SET` 均位于 IP 阶段之前。校验器会拒绝任何把域名或 `non_ip` 规则放到
IP 阶段之后的修改。

Apple CN 是有意放在宽泛 `apple_services` 之前的窄规则例外；否则
`apple_services` 中的 Apple 广义后缀会先命中，Apple CN 的 `DIRECT` 将失效。
Microsoft CDN 同理位于 Microsoft 广义规则之前。Supercell 首方域名位于域名阶段，
Blackmatrix7 现成混合集在 IP 阶段以 `no-resolve` 加载；两者统一使用
`DIRECT`，避免登录、资源与对战混用出口。

## Reject 边界

基础规则加载 Sukka 的 7 个 Reject 资源：3 个 `domainset`、3 个 `non_ip`
和 1 个 `ip`。上游对性能的警告针对 MITM 与 `URL-REGEX` 拦截，不等于应删除
所有 Reject 域名/IP 规则。这里同时启用基础、额外和钓鱼域名集，但不加入
`reject-url-regex.conf` 或新的 MITM 拦截层；全局 STUN 拒绝与 `RULE-SET,SYSTEM`
同样不在基础规则中激活。设备上已保留的模块不会被
这次规则更改删除或改写。

不再加载 Adblock4limbo 外部规则集：当前源 543 条活动规则中有 253 条已被 Sukka
覆盖，剔除 Keyword、重复、无效和内部冗余后仅剩 224 条增量。相对已启用的 Sukka 基础、Extra
与 Phishing 大型域集，收益不足以抵消额外第三方供应链和维护复杂度。已保留模块中的
同名网页处理脚本不属于基础分流规则，按“模块不改”约束继续保留。

## Apple 与系统链路

Apple 不再使用任何本仓库自定义域名、付款、Private Relay、iCloud、证书或系统更新
例外。基础规则只加载 Sukka README 明确列出的四个 Apple 资源：

- `domainset/apple_cdn.conf` → `DIRECT`；
- `non_ip/apple_intelligence.conf` → `United States`；
- `non_ip/apple_cn.conf` → `DIRECT`；
- `non_ip/apple_services.conf` → `United States`。

软件更新由 Sukka `download` 与上述 Apple 资源承接；Apple Account、Private Relay、
iCloud 等则按 Sukka Apple Services 的公共语义处理。现有 iRingo、WeatherKit、Maps、
News、TV 等模块仍保留，模块 MITM 边界不等于基础分流例外。GitHub 与
`githubusercontent.com` 固定香港出口，仅用于保留模块的发布资源更新。

## 本仓库活动资源

主规则通过 14 个远程本仓库资源加载 683 条域名，另外直接引用
Blackmatrix7 的 Supercell 混合规则（当前 2 条 Brawl Stars 域名与 22 条服务器 IP）：

该上游头部最后更新日期为 2025-06-06，因此 22 个云服务器 `/32` 只作为当前社区基线，
不扩大为 AWS、Tencent Cloud 或其他共享云 CIDR。上游健康检查会锁定两个
Brawl Stars 域名、仅 IPv4 `/32`、最多 64 条且必须携带 `no-resolve`；出现宽域名、宽 CIDR
或其他规则类型时 CI 直接失败。主站、商店、创作者和跳转追踪域不是游戏联网必需，
故未加入直连集。

其中 `microsoft-cdn-download-overlap.conf` 精确承接 Microsoft 中国 CDN 与香港下载集合的 38 条交集。

| 文件 | 策略 | 作用 |
| --- | --- | --- |
| `supercell-direct.conf` | `DIRECT` | Supercell ID、账户服务与各款游戏首方域 |
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

主规则的第 2 段按“Supercell 直连 → 固定媒体 → 中国大陆实体金融 →
分地区实体金融 → 美国住宅、身份与风控 → Crypto 与 Web3”细分。
所有定向域名资源都早于 Sukka 的大型 Reject `DOMAIN-SET`。Blackmatrix7 混合集
则位于所有 non_ip 之后、Sukka IP 资源之前；其两条域名已由前置自有集覆盖，
该兼容层主要承接 `no-resolve` 的 IP 匹配。Sukka 公共资源仍严格保持
`domainset → non_ip → ip` 的作者顺序。

同一策略下原有的小文件已经合并：X、Google Account/Voice、Polymarket 合入
`us-residential.conf`；香港账户上下文合入 `hk-finance.conf`；Bybit 合入
`crypto.conf`。旧文件仍保留在仓库供历史追踪，但不再被主规则引用。

共享 KYC 和风控供应商无法仅根据域名判断调用它的是哪家银行；Surge iOS 也无法按
请求来源 App 为同一共享域名动态选择地区。因此这两层只保留经过审计的窄后缀，并按
当前账户使用场景固定住宅出口，不加入 `.auth0.com`、`.cloudflare.com`、
`.medallia.com` 等宽泛共享后缀。

## Sukka 公共分流

当前使用的官方资源均来自统一基址 `https://ruleset.skk.moe/List/`：

- `domainset/reject`、`reject_extra` 与 `reject_phishing` → `REJECT`；
- `non_ip/reject-drop` → `REJECT-DROP` + `pre-matching`，`reject` → `REJECT`，
  `reject-no-drop` → `REJECT-NO-DROP`；
- `ip/reject` → `REJECT-DROP`；
- `speedtest`、`cdn` → `PROXY`；
- `stream`、`ai`、`apple_intelligence` → `United States`；
- Telegram 域名、MTProto 协议与官方 CIDR → `Singapore`；
- `apple_cdn`、`apple_cn`、`microsoft_cdn`、`non_ip/lan`、`ip/lan`、`domestic`、
  `direct` → `DIRECT`；
- `apple_services`、`microsoft` → `United States`；
- `download` → `Hong Kong`；
- `global` 与 `FINAL` → `PROXY`；
- 中国 IP → `DIRECT`。

Telegram 同时加载 Sukka 的域名规则和作者推荐的官方 CIDR，并由 `PROTOCOL,MTProto`
补足 MTProto 识别；不加载可选 ASN。设备 Profile 的 `[MTProto]` 使用 Sukka 每日构建的
DC JSON。IPv6 当前未启用，因此不加载 China IPv6 资源。`nano.cr18.eu.org` 是唯一保留
的 Emby 精确例外，固定新加坡，不再加载整个第三方 Emby 总表。

完整的上游资源取舍与覆盖状态见 [Sukka 覆盖矩阵](docs/sukka-parity.md)。

## 接入与校验

`surge-main.conf` 是远程资源版；`surge-expanded.conf` 仅用于审计和整段复制，
由生成器维护。接入前应确认策略组存在：`Res-Frontier`、`PROXY`、`Hong Kong`、
`Singapore`、`Japan`、`Korea`、`United Kingdom`、`United States`、`Crypto`、
`Web3`。

在 Surge 的外部资源页面刷新，并确认 14 个本仓库规则文件与 Supercell 外部混合集均成功加载。随后执行：

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
- 严格的 `domainset → non_ip → ip` 保证针对基础 Profile。Surge 会把保留模块的
  规则前置；若第三方模块内部混合域名与 IP 规则，在“不改模块”的约束下不能把整个
  修改后配置重新排序，但不会改变本仓库基础规则自身的阶段正确性。

迁移详情见 [migration-notes](docs/migration-notes.md)，需求映射见
[requirements-matrix](docs/requirements-matrix.md)，数量对账见
[source-parity](docs/source-parity.md)。

## 官方参考

- [SukkaW/Surge README](https://github.com/SukkaW/Surge/blob/master/README.md)
- [Sukka Ruleset 服务](https://ruleset.skk.moe/)
- [Surge Ruleset](https://manual.nssurge.com/rule/ruleset.html)
- [Surge Domain-based Rule](https://manual.nssurge.com/rule/domain-based.html)
- [Apple Software Updates network requirements](https://support.apple.com/en-us/101555)
