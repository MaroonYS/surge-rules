# Surge Rules

一套面向 Surge 的模块化规则仓库。主配置只保留有顺序意义的规则骨架，
大量域名按“最终策略”拆成远程 `DOMAIN-SET`，从而减少重复、顺序错误和后续维护成本。

## 设计目标

- 保留地区第一方金融域名的既有分流语义。
- 将 Crypto 与 Web3 拆开，避免一个策略切换影响另一类服务。
- 不全局接管共享支付、KYC、验证码、设备指纹和反欺诈供应商，避免不同站点的会话被拆到不同出口。
- 通过零依赖校验器和 GitHub Actions 阻止格式错误、重复、跨策略覆盖和主规则顺序回归。
- 禁止宽泛共享后缀和未经批准的 `DOMAIN-KEYWORD`，让自定义规则保持精准。

Surge 按从上到下的顺序匹配，首条命中生效。`DOMAIN-SET` 适合大量域名：

- `example.com` 只匹配精确域名；
- `.example.com` 匹配根域名及其子域名。

规则文件中只写域名，不写 `DOMAIN-SUFFIX`、策略名或逗号。

## 文件与策略

| 文件 | 目标策略 | 用途 |
| --- | --- | --- |
| `apple-ai.conf` | `AIGC` | Apple Intelligence、Siri、PCC |
| `direct-cn.conf` | `DIRECT` | 中国大陆银行与银联 |
| `hk-finance.conf` | `HK-FINANCE` | 香港金融 |
| `sg-finance.conf` | `SG-FINANCE` | 新加坡金融 |
| `jp-finance.conf` | `JP-FINANCE` | 日本金融 |
| `kr-finance.conf` | `KR-FINANCE` | 韩国金融 |
| `uk-finance.conf` | `UK-FINANCE` | 英国金融 |
| `us-residential.conf` | `Res-Frontier` | 美国第一方金融、Apple Cash/Pay 与 PayPal |
| `finance-context.conf` | `Finance` | 无法仅按域名判断地区的金融服务 |
| `crypto.conf` | `Crypto` | 中心化交易所 |
| `web3.conf` | `Web3` | 钱包、RPC、DeFi、NFT、浏览器 |

`archive/` 中的文件永远不被主规则加载。当前没有任何被确认停用的域名。

## 接入

1. 确认现有配置已经定义表格及主 Rule 使用的所有策略名。
2. 确认 `Apple`、`AIGC`、`Res-Frontier` 和各地区金融组已选中所需出口。
3. 在以下两种 Rule 中选择一种，不要同时加载：
   - 推荐：[surge-main.conf](surge-main.conf)，通过 11 个远程 DOMAIN-SET 加载 420 条域名；
   - 展开：[surge-expanded.conf](surge-expanded.conf)，把同样的 420 条域名全部写回 `[Rule]`，可整段复制。
4. 在 Surge 的外部资源页面刷新，确认 11 个本仓库规则集均成功加载。

展开版由 `scripts/build_expanded.py` 自动生成，与远程版的活动域名语义一致。
它用于检查和整段复制，不应手工编辑。修改对应 DOMAIN-SET 后运行：

```bash
python3 scripts/build_expanded.py --write
```

原始 Rule 到各文件的覆盖和有意调整记录在
[docs/migration-notes.md](docs/migration-notes.md)。
逐项完成状态见 [docs/requirements-matrix.md](docs/requirements-matrix.md)。
原始 471 条域名到最终 420 条活动规则的数量对账见
[docs/source-parity.md](docs/source-parity.md)。

主规则使用以下公开 Raw 基址：

```text
https://raw.githubusercontent.com/MaroonYS/surge-rules/main/
```

Private Relay 严格按 17 段契约使用 `Apple`。
Apple Intelligence 严格使用 `AIGC`。
Apple Cash/Pay 与 PayPal 收录在 `us-residential.conf`，命中 `Res-Frontier`。

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
```

生成机器可读报告：

```bash
python3 scripts/validate.py \
  --strict \
  --json-out validation-report.json
```

手动检查所有远程依赖是否可访问：

```bash
python3 scripts/check_upstreams.py --timeout 15
```

## 为什么不加载共享验证基础设施

Stripe、Plaid、KYC、验证码、设备指纹和反欺诈域名会被大量不同地区、甚至非金融网站共用。
将整类供应商固定到一个地区，会使第一方页面和验证请求出口不一致，并扩大误匹配范围。
如果正常登录被广告规则误拦，应根据 Surge 请求日志增加具体主机名例外，而不是重新加载整类供应商。

本仓库只负责分流结构与规则数据，不包含节点、代理凭据或订阅。

## 官方参考

- [Surge Ruleset](https://manual.nssurge.com/rule/ruleset.html)
- [Surge Domain-based Rule](https://manual.nssurge.com/rule/domain-based.html)
- [Surge Policy Group](https://manual.nssurge.com/policy/group.html)
