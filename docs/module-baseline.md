# 稳定性模块基线

Surge 模块的优先级高于主 Profile，启用状态也不会同步到其他设备。每台 Mac、
iPhone 和 iPad 都要分别核对。下面的基线面向本仓库强调的金融、Apple 连续互通、
BiliUniverse 与单一字幕处理链路。

## 保留

- BiliUniverse 官方四件套：`📺 BiliBili: 🛡️ ADBlock`、`⚙️ Enhanced`、
  `🌐 Global`、`🔀 Redirect`。四者功能边界不同，可按官方设计共存。
- `🍿️ DualSubs: ▶️ YouTube`：作为唯一的 YouTube 双语字幕实现。
- `Sub-Store`。
- `BoxJs` 与 `Script Hub(β)`：仅在确实使用其管理功能时保留。
- `YouTube去广告(>=iOS15)`：可选；启用后在修改后配置和请求日志中确认
  player、timedtext 与 browse 每个阶段只有一套处理链。
- `谷歌中国重定向`、`快捷搜索`、`流媒体解锁检测`、`节假日信息`：按需启用。
- `HTTP Download Optimization`：仅在 Mac 的 Steam、Windows Update、
  Microsoft Store 或 Xbox 下载场景保留。

## 必须停用

- `Disable HTTP Engine`：与 Rewrite、Script 和 MITM 的目标直接冲突。
- `YouTube双语翻译`：与 DualSubs YouTube 重复处理 player、timedtext 和 browse。
- `哔哩哔哩增强`、`Bilibili 1080P`：与 BiliUniverse 请求处理重叠。
- `AllInOne`、`可莉广告过滤器`、`适配可莉插件中心`、`广告平台拦截器`、
  `毒奶特供`、`通用解锁`。
- 两份 `[Sukka] Enhance Better ADBlock for Surge` 与
  `[Sukka] Surge Reject MITM`。主 Rule 已加载 SKK Reject 与本仓库补集。
- `🍟 Fries: 🌐 DNS enhanced`、`🚫 Block HTTPDNS`、`🌐 General Enhanced`、
  `🔓 MitM`，以及独立的 `拦截HTTPDNS`。其中 `Fries: Block HTTPDNS` 与独立
  `拦截HTTPDNS` 存在大量完全相同的 pre-matching；其余模块继续叠加 Host、MITM
  与 DNS 行为，使最终边界难以审计。
- `[Sukka] Always Real IP Plus` 与 `[Sukka] Local DNS Mapping`，除非有经过日志
  证实的单域名兼容问题后再按需恢复。
- 全部 iRingo 模块作为稳定基线停用；它们会在主 Apple Rule 之前插入分流或改写。

## 条件启用

- `🍿️ DualSubs: 🔣 Universal`：只在确实需要其支持的非 YouTube 平台字幕时启用。
- Akamaized AddOn：只在实际使用其对应 CDN/平台时启用。
- Microsoft Translate AddOn：只有明确选择 Microsoft 作为翻译供应商且凭据有效时
  启用；它也可能服务 YouTube，并非仅用于非 YouTube 平台。
- Spotify 相关模块只选一套，不叠加 `Spotify(>=iOS15)`、`Spotify歌词增强` 与
  DualSubs Spotify/Transcripts。
- `QX重写&规则集转化` 与 `Script Hub(β)` 二选一。
- `router.com`、`HomeKit Accessories Quirk`、`Game Console STUN`、
  `Google Home Devices`、`Fix Windows No Network Alert` 只在对应设备场景启用。

## MITM 基线

基础 Profile 必须保持：

```ini
skip-server-cert-verify = false
```

金融、身份验证和 Apple 系统域名应作为负向项放在 `hostname` 最前。负向项是
防御层，不是继续保留广域 MITM 模块的理由；最可靠的方案仍是停用上述重叠模块，
只让 BiliUniverse、DualSubs 等明确功能声明各自需要的 hostname。

模块可能通过覆盖或 `%INSERT%` 改变最终 `hostname` 顺序。每台设备完成模块清理后，
必须打开 Surge 的“修改后配置”（effective/modified profile），确认负向项仍位于所有
相关正向 hostname 之前，并在请求详情中确认银行、券商和身份验证域未启用 MITM。
