# Surge Rules

一套面向 Surge 的模块化规则仓库。主配置只保留有顺序意义的规则骨架，
大量域名按“最终策略”拆成远程 `DOMAIN-SET`，从而减少重复、顺序错误和后续维护成本。

## 设计目标

- 保留地区第一方金融域名的既有分流语义。
- 将 Crypto 与 Web3 拆开，避免一个策略切换影响另一类服务。
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
| `crypto.conf` | `Crypto` | 中心化交易所 |
| `web3.conf` | `Web3` | 钱包、RPC、DeFi、NFT、浏览器 |
| `adblock4limbo-supplement.conf` | `REJECT` | Adblock4limbo 经清洗、去重并减去 SKK 覆盖后的补集 |

`archive/` 中的文件永远不被主规则加载。当前没有任何被确认停用的域名。

## 接入

1. 确认现有配置已经定义表格及主 Rule 使用的所有策略名。
2. 确认 `Apple`、`AIGC`、`Res-Frontier`、`Identity` 和各地区金融组已选中所需出口。
   `Identity` 的稳定 `select` 定义可直接使用
   [snippets/identity-policy-groups.conf](snippets/identity-policy-groups.conf)。
3. 在以下两种 Rule 中选择一种，不要同时加载：
   - 推荐：[surge-main.conf](surge-main.conf)，通过 15 个远程 DOMAIN-SET 加载 700 条规则；
   - 展开：[surge-expanded.conf](surge-expanded.conf)，把同样的 700 条规则全部写回 `[Rule]`，可整段复制。
4. 在 Surge 的外部资源页面刷新，确认 15 个本仓库规则集均成功加载。

展开版由 `scripts/build_expanded.py` 自动生成，与远程版的活动域名语义一致。
它用于检查和整段复制，不应手工编辑。修改对应 DOMAIN-SET 后运行：

```bash
python3 scripts/build_expanded.py --write
```

原始 Rule 到各文件的覆盖和有意调整记录在
[docs/migration-notes.md](docs/migration-notes.md)。
逐项完成状态见 [docs/requirements-matrix.md](docs/requirements-matrix.md)。
原始 Rule、金融/身份/风控扩充及广告补集到最终 700 条活动规则的数量对账见
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
python3 scripts/check_upstreams.py --timeout 15 --retries 2
```

核对完整 Surge 配置中的策略是否存在，并确认敏感金融策略使用固定代理或手动
`select`：

```bash
python3 scripts/check_profile_policies.py \
  --profile /path/to/profile.conf \
  --supplement snippets/identity-policy-groups.conf \
  --require-stable \
  Finance HK-FINANCE SG-FINANCE JP-FINANCE KR-FINANCE UK-FINANCE \
  Res-Frontier "United States" Identity
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

## Identity 与 Risk 的边界

跨地区第一方金融仍进入 `Finance`。KYC/身份验证进入
`identity-context.conf`，设备情报与指纹服务进入 `risk-context.conf`，两者统一使用
稳定的手动 `Identity` 策略。宽泛 Persona 根域和通用反欺诈 SaaS 不在活动文件中；
验证码等未列入活动文件的共享服务仍按实际日志精确补充。

本仓库只负责分流结构与规则数据，不包含节点、代理凭据或订阅。
它不能保证银行或支付服务不触发风控；稳定、固定的账户地区和正常使用行为
比持续扩大共享验证规则更重要。

## 官方参考

- [Surge Ruleset](https://manual.nssurge.com/rule/ruleset.html)
- [Surge Domain-based Rule](https://manual.nssurge.com/rule/domain-based.html)
- [Surge Policy Group](https://manual.nssurge.com/policy/group.html)
- [SukkaW/Surge 使用说明](https://github.com/SukkaW/Surge)
- [blackmatrix7 WeChat 规则说明](https://github.com/blackmatrix7/ios_rule_script/tree/master/rule/Surge/WeChat)
- [ddgksf2013/Filter](https://github.com/ddgksf2013/Filter)
