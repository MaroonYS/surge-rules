# Source parity

配置所有者提供的 555 行 Rule 中共有 471 条 `DOMAIN` / `DOMAIN-SUFFIX`。
精准版的数量变化如下：

| 项目 | 数量 | 说明 |
| --- | ---: | --- |
| 来源域名规则 | 471 | 原始 Rule 中的 DOMAIN 与 DOMAIN-SUFFIX |
| 共享第三方规则不加载 | -52 | 支付聚合、KYC、验证码、指纹和反欺诈供应商 |
| Web3 等价去重 | -1 | `.moonbeam.moonscan.io` 已被 `.moonscan.io` 覆盖 |
| Polymarket 精准补充 | +2 | 新增 `.polymarket.com` 与 `.polymarket.us` |
| 最终活动域名规则 | 420 | 全部位于 11 个 DOMAIN-SET |

[surge-expanded.conf](../surge-expanded.conf) 将 420 条自维护域名全部内联。
Private Relay、SKK、WeChat、Emby 和广告等资源仍按 17 段契约引用上游。

## 两个版本为何行数不同

- `surge-main.conf`：约 100 行，通过 11 个远程文件加载 420 条域名。
- `surge-expanded.conf`：约 520 行，将同样的 420 条域名全部展开。

两者的自维护活动域名语义一致，不能同时加载。
CI 会重新生成展开版并逐字比较；任意 DOMAIN-SET 修改后未更新展开版，提交将失败。
