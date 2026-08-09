# Source parity

配置所有者提供的 555 行 Rule 中共有 471 条 `DOMAIN` / `DOMAIN-SUFFIX`。
精准版的数量变化如下：

| 项目 | 数量 | 说明 |
| --- | ---: | --- |
| 来源域名规则 | 471 | 原始 Rule 中的 DOMAIN 与 DOMAIN-SUFFIX |
| 共享第三方规则不加载 | -52 | 支付聚合、KYC、验证码、指纹和反欺诈供应商 |
| Web3 等价去重 | -1 | `.moonbeam.moonscan.io` 已被 `.moonscan.io` 覆盖 |
| Polymarket 精准补充 | +2 | 新增 `.polymarket.com` 与 `.polymarket.us` |
| 精准版基础规则 | 420 | 原始迁移后的 11 个 DOMAIN-SET |

在此基础上，本轮做了以下可核对变化：

| 项目 | 净变化 | 说明 |
| --- | ---: | --- |
| Polymarket 独立文件 | 0 | 3 条从美国文件移动，语义收窄且数量不变 |
| 中国大陆金融精修 | +2 | 增加 3 个别名、把平安根域替换为银行子域，并迁出跨地区 BOC 根域 |
| 香港金融补充 | +8 | 8 个高置信第一方机构域 |
| 新加坡金融补充 | +4 | 4 个高置信第一方机构域 |
| 日本金融补充 | +6 | 6 个高置信第一方机构域 |
| 韩国金融补充 | +1 | K Bank 第一方域 |
| 英国金融补充 | +4 | 4 个高置信第一方机构域 |
| 美国住宅精修 | -2 | 移除 13 个共享基础设施，增加 11 个第一方区域银行 |
| 跨地区 BOC 根域 | +1 | `bankofchina.com` 移入 `Finance` |
| 第一方自维护小计 | 444 | 12 个业务 DOMAIN-SET |
| Adblock4limbo 精准补集 | +226 | 旧版清洗补集 |
| 1.3.0 活动规则 | 670 | 13 个本仓库 DOMAIN-SET |

1.4.0 在此基础上继续调整：

| 项目 | 净变化 | 说明 |
| --- | ---: | --- |
| ICBC 根域收窄 | -1 | 删除 `.icbc.com`，保留 `.icbc.com.cn` |
| 美国身份与清算补充 | +4 | Apex、Early Warning、ID.me、Login.gov |
| Identity 层 | +21 | KYC 与身份验证 |
| Risk 层 | +15 | 设备指纹与反欺诈 |
| Adblock 二级去重 | -2 | 删除伪域 `.ingest.sentry` 与已由 SKK non_ip 覆盖的 `.histats.com` |
| 金融/身份/风控自维护小计 | 483 | 14 个业务 DOMAIN-SET |
| Adblock4limbo 精准补集 | +224 | 同时减去 SKK domainset 与 non_ip reject 覆盖 |
| 最终活动规则 | 707 | 15 个本仓库 DOMAIN-SET |

1.5.0 将共享服务进一步收窄，并补入实测 Polymarket 主机：

| 项目 | 净变化 | 说明 |
| --- | ---: | --- |
| Polymarket S3 上传主机 | +1 | 精确加入 `polymarket-upload.s3.us-east-2.amazonaws.com` |
| Persona 根域收窄 | -1 | 删除 `.persona.com`，保留 `.withpersona.com` |
| Risk 保守活动集 | -7 | 删除 7 个通用反欺诈 SaaS，保留 8 个设备情报与指纹域 |
| 金融/身份/风控自维护小计 | 476 | 14 个业务 DOMAIN-SET |
| Adblock4limbo 精准补集 | +224 | 同时减去 SKK domainset 与 non_ip reject 覆盖 |
| 最终活动规则 | 700 | 15 个本仓库 DOMAIN-SET |

1.6.0 恢复原配置中的 Bilibili 视频 CDN 直连语义：

| 项目 | 净变化 | 说明 |
| --- | ---: | --- |
| 同期主分支金融更新 | +62 | 合入最新 Finance/HK/SG/JP/UK 活动条目后的净增量 |
| Bilibili 精确直连 | +3 | 用 `.bilivideo.com`、`.bilivideo.cn`、`.bilivideo.net` 替代原宽泛关键词 |
| 业务自维护小计 | 541 | 15 个业务 DOMAIN-SET |
| Adblock4limbo 精准补集 | +224 | 同时减去 SKK domainset 与 non_ip reject 覆盖 |
| 最终活动规则 | 765 | 16 个本仓库 DOMAIN-SET |

[surge-expanded.conf](../surge-expanded.conf) 将当前自维护活动规则全部内联。
当前远程版共加载 24 个本仓库文件：22 个域名 `DOMAIN-SET`，以及承载
Google Voice 5 条和 APNs 10 条逻辑规则的 2 个无策略列 `RULE-SET`。
Private Relay、SKK、WeChat 与 Emby 等资源仍按 17 段契约引用上游。

## 两个版本为何行数不同

- `surge-main.conf`：通过 24 个远程文件加载当前活动规则。
- `surge-expanded.conf`：由生成器将同样的活动规则全部展开。

两者的自维护活动规则语义一致，不能同时加载。
CI 会重新生成展开版并逐字比较；任意活动 `DOMAIN-SET` 或 `RULE-SET` 修改后
未更新展开版，提交将失败。
Adblock4limbo 的活动数量允许随上游和 SKK 基线变化，因此当前总数以严格校验器及
`surge-expanded.conf` 的自动生成标头为准；上表中的数字保留为对应版本快照。
