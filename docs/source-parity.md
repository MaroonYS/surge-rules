# Source Parity

| 指标 | 当前值 | 来源 |
| --- | ---: | --- |
| 主规则条数 | 97 | `surge-main.conf` 的有效规则 |
| 当前 DOMAIN-SET 条目 | 630 | 12 个本仓库 `DOMAIN-SET` |
| 当前 RULE-SET 条目 | 0 | 本仓库不再维护远程 `RULE-SET` |
| 当前活动条目 | 630 | `rules-manifest.json` 的 12 个活动文件 |
| 活动本仓库资源 | 12 | 仅保留地区金融、住宅风控、Crypto、Web3 |
| Sukka DOMAIN-SET | 4 | speedtest、cdn、apple_cdn、download |
| Sukka non_ip | 13 | CDN、Stream、AI、Apple、Microsoft、Download、LAN、Misc |
| Sukka ip | 5 | Stream、AI、Telegram、Domestic、China IP |

`surge-expanded.conf` 仅展开上述 630 条本仓库域名，Sukka 官方远程资源保持远程引用，
以避免复制其大型规则和制造重复真相层。

数量由以下命令验证：

```bash
python3 scripts/validate.py --strict
python3 scripts/build_expanded.py --check
```

历史文件仍在版本库中，但未出现在 `rules-manifest.json` 的 `active` 列表，也不会被
`surge-main.conf` 或展开版加载。
