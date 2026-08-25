# Sukka 覆盖矩阵

本矩阵以 SukkaW/Surge 当前 README 和《我有特别的 Surge 配置和使用技巧》为基线，
区分“活动加载”“已被总表覆盖”和“明确不加载”。因此，可选项不会在没有说明的情况下
消失，也不会为了表面齐全重复加载同一数据。

| Sukka 类别 | 当前处理 | 原因 |
| --- | --- | --- |
| Reject Drop / 基础 / Extra / Phishing / Reject / No Drop / IP Reject | 全部活动 | 用户明确要求启用 Phishing；严格按 `domainset → non_ip → ip` 分相 |
| Reject URL-REGEX 与 Sukka MITM hostname 模块 | 不加载 | 上游明确指出 MITM 与 URL-REGEX 开销极大；现有模块也不得再叠一层 |
| Adblock4limbo Surge 外部规则源 | 不加载 | 543 条活动规则中 253 条被 Sukka 覆盖，规范化后仅余 224 条增量；删除规则源、生成文件和同步链，保留模块脚本不改 |
| 搜狗输入法 | 不加载 | 专项隐私规则会影响账号同步、词库更新和反馈，当前没有该需求 |
| Speedtest | 活动 | 固定 `PROXY` 测试出口 |
| CDN（domainset + non_ip） | 全部活动 | 使用 `PROXY` 承接高流量静态资源 |
| Stream（non_ip + ip） | 总表活动 | `stream.conf` 已包含全部地区；不重复加载 `stream_XX` 子集，统一由 `United States` 兜底 |
| AI（non_ip + ip）与 Apple Intelligence | 全部活动 | 使用 `United States` |
| Telegram（non_ip + 官方 IP CIDR） | 全部活动 | 使用 `Singapore`；不加载上游仅建议作为补充的 ASN |
| Apple CDN / Apple Services / Apple CN | 全部活动 | CDN/CN 直连，其他 Apple 服务使用 `United States`；窄 Apple CN 先于宽 Apple Services |
| Microsoft CDN / Microsoft | 全部活动 | CDN 直连，其他服务使用 `United States` |
| 网易云音乐 | 不加载 | 专项功能，不属于当前需求；普通流量仍由 Domestic/China IP 承接 |
| Download（domainset + non_ip） | 全部活动 | 放在 Apple/Microsoft CDN 之后并使用 `Hong Kong` |
| LAN（non_ip + ip） | 全部活动 | 两层均使用 Sukka 官方资源并直连 |
| Misc（domestic / direct / global + domestic IP） | 全部活动 | 保留国内、直连、海外和 Anycast 基础兜底 |
| China IP IPv4 | 活动 | 直连 |
| China IP IPv6 | 不加载 | 当前 `ipv6=false`，加载 IPv6 CIDR 不会提供有效收益 |
| iCloud Private Relay 可选表 | 不加载 | 用户后续要求 Apple 仅保留核心 Sukka 公共分流；不恢复额外 Apple 专项覆盖 |

设备 Profile 另外保留 `DEST-PORT,123,DIRECT`、`PROTOCOL,MTProto,Singapore`，并在
`[MTProto]` 使用 `https://ruleset.skk.moe/Internal/mtproto-dc-config.json`。General 采用
Sukka 的网络测试端点、UDP 不支持即拒绝和 `exclude-simple-hostnames=true`；
Local DNS Mapping、Always Real IP 与 `skip-proxy` 已由保留模块注入，不在主 Profile
重复声明。

MITM 不照搬 Sukka 的可选广告解密层，而是以现有 iRingo、WLOC 和 DualSubs 的真实依赖
建立 24 个精确正项；其后保留 Apple、iCloud、银行、券商、Crypto、KYC、风控和原始 IP
负项。iPhone iOS 27 对两个被系统证书固定的 WLOC 主机使用条件化
`hostname-disabled`，iPad 与旧系统继续保留模块能力。

这里的严格阶段顺序约束基础 Profile。Surge 会把启用模块的规则置于基础规则之前；
部分保留的第三方模块内部同时包含域名与 IP 规则。在“保留且不修改模块”的前提下，
不能声称整个修改后配置仍是全局阶段纯净，但基础规则、仓库契约和设备 Profile 的
自有规则均严格保持 `domainset → non_ip → ip → FINAL`。
