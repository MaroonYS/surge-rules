# Source Parity

| 指标 | 当前值 | 来源 |
| --- | ---: | --- |
| 主规则条数 | 52 | `surge-main.conf` 的有效规则 |
| 当前 DOMAIN-SET 条目 | 683 | 14 个本仓库 `DOMAIN-SET` |
| 当前 RULE-SET 条目 | 0 | 本仓库不复制第三方 IP 规则 |
| 当前活动条目 | 683 | `rules-manifest.json` 的 14 个活动文件 |
| 活动本仓库资源 | 14 | Supercell 域名、地区金融、住宅风控、Crypto、Web3 与 Microsoft CDN/download 精确交集 |
| Supercell 外部混合集 | 24 | Blackmatrix7 现成 2 域名 + 22 IP，以 `no-resolve` 自动更新 |
| Sukka DOMAIN-SET | 7 | Reject 基础/额外/钓鱼、speedtest、cdn、apple_cdn、download |
| Sukka non_ip | 17 | Reject Drop/Reject/No Drop、CDN、Stream、AI、Telegram、Apple、Microsoft、Download、LAN、Misc |
| Sukka ip | 7 | Reject、Stream、AI、Telegram、LAN、Domestic、China IP |

`surge-expanded.conf` 仅展开上述 683 条本仓库规则，Sukka 与 Blackmatrix7 远程资源保持远程引用，
以避免复制其大型规则和制造重复真相层。
外部 Supercell 混合集的上游元数据日期为 2025-06-06；健康检查只允许已知两个域名、
IPv4 `/32,no-resolve` 且最多 64 条 IP，防止可变上游引入宽域名或宽 CIDR。
三个自定义高风控子层及其他定向业务 `DOMAIN-SET` 全部早于三个 Sukka
Reject `DOMAIN-SET`；随后才进入 `non_ip` 和 `ip` Reject，保持严格阶段顺序。

数量由以下命令验证：

```bash
python3 scripts/validate.py --strict
python3 scripts/build_expanded.py --check
```

历史文件仍在版本库中，但未出现在 `rules-manifest.json` 的 `active` 列表，也不会被
`surge-main.conf` 或展开版加载。
