# Surge Rules

一套面向 Surge 的模块化规则仓库。主配置只保留有顺序意义的规则骨架，
大量域名按“最终策略”拆成远程 `DOMAIN-SET`，从而减少重复、顺序错误和后续维护成本。

## 设计目标

- 保留地区第一方金融域名的既有分流语义。
- 将 Apple Private Relay、Apple Intelligence 与普通 Apple 服务解耦。
- 将 Crypto 与 Web3 拆开，避免一个策略切换影响另一类服务。
- 不全局接管共享支付、KYC、验证码、设备指纹和反欺诈供应商，避免不同站点的会话被拆到不同出口。
- 通过零依赖校验器和 GitHub Actions 阻止格式错误、重复、跨策略覆盖和主规则顺序回归。

Surge 按从上到下的顺序匹配，首条命中生效。`DOMAIN-SET` 适合大量域名：

- `example.com` 只匹配精确域名；
- `.example.com` 匹配根域名及其子域名。

规则文件中只写域名，不写 `DOMAIN-SUFFIX`、策略名或逗号。

## 文件与策略

| 文件 | 目标策略 | 用途 |
| --- | --- | --- |
| `apple-ai.conf` | `Apple-AI` | Apple Intelligence、Siri、PCC |
| `direct-cn.conf` | `DIRECT` | 中国大陆银行与银联 |
| `hk-finance.conf` | `HK-FINANCE` | 香港金融 |
| `sg-finance.conf` | `SG-FINANCE` | 新加坡金融 |
| `jp-finance.conf` | `JP-FINANCE` | 日本金融 |
| `kr-finance.conf` | `KR-FINANCE` | 韩国金融 |
| `uk-finance.conf` | `UK-FINANCE` | 英国金融 |
| `us-residential.conf` | `Res-Frontier` | 美国第一方金融服务 |
| `finance-context.conf` | `Finance` | 无法仅按域名判断地区的金融服务 |
| `crypto.conf` | `Crypto` | 中心化交易所 |
| `web3.conf` | `Web3` | 钱包、RPC、DeFi、NFT、浏览器 |

`archive/` 中的文件永远不被主规则加载。当前没有任何被确认停用的域名。

## 接入

1. 将 [policy-groups.example.conf](policy-groups.example.conf) 中的两个策略组条目合并到现有 `[Proxy Group]`。
2. 确认现有配置已经定义表格中的其他策略名。
3. 用 [surge-main.conf](surge-main.conf) 的 `[Rule]` 段替换现有规则段。
4. 在 Surge 的外部资源页面刷新，确认 11 个本仓库规则集均成功加载。

原始 Rule 到各文件的覆盖和有意调整记录在
[docs/migration-notes.md](docs/migration-notes.md)。

主规则使用以下公开 Raw 基址：

```text
https://raw.githubusercontent.com/MaroonYS/surge-rules/main/
```

Private Relay 使用独立的 `Private-Relay` 组，不再复用普通 `Apple` 组。
Apple Intelligence 使用独立的 `Apple-AI` 组，不再随通用 `AIGC` 组切换。
Apple Cash/Pay 的三个 Apple 域名保持 `DIRECT`，避免与 Wallet、APNs、证书验证及发卡行请求形成出口分裂。

## 维护

新增服务时，先确认其最终策略，再把域名加入对应文件。不要按银行创建新文件。
只有你明确确认停用的域名才应移入 `archive/`，需要时可再移回正式文件。

本地检查：

```bash
python3 scripts/validate.py --strict
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
