# 全量模块兼容基线

本基线适用于配置所有者明确保留当前全部模块的场景。目标不是让每一条重复声明都
执行一次，而是保证模块所需的路由、MITM、Rewrite 与 Script 具备真实命中条件，
同时不以放开整个 Apple 或金融域名的方式换取表面兼容。

Surge 会把模块规则放到主 Profile 规则之前；模块的启用状态、参数、缓存和有效顺序
也不会跨设备同步。因此 Mac、iPhone 和 iPad 必须分别检查“修改后配置”，不能只用
仓库主 Rule 或另一台设备的状态推断本机行为。

## 主 Profile 必须保持的边界

- `skip-server-cert-verify = false`，不得为兼容模块而关闭服务器证书校验。
- 只对实际保留模块的精确 Apple 主机开启 MITM。下列 21 项必须位于
  `-*.apple.com`、`-*.itunes.com` 等负向通配之前：

<!-- module-compatibility:positive-hosts:start -->
```text
weatherkit.apple.com
gspe1-ssl.ls.apple.com
gs-loc.apple.com
gs-loc-cn.apple.com
dispatcher.is.autonavi.com
configuration.ls.apple.com
gspe35-ssl.ls.apple.com
gspe35-ssl.ls.apple.cn
uts-api.itunes.apple.com
umc-tempo-api.apple.com
play-cdn.itunes.apple.com
play-edge-cdn.itunes.apple.com
news-edge.apple.com
news-todayconfig-edge.apple.com
news-events.apple.com
news-sports-events.apple.com
news-client.apple.com
news-client-search.apple.com
hls.itunes.apple.com
hls-svod.itunes.apple.com
vod-*.tv.apple.com
```
<!-- module-compatibility:positive-hosts:end -->

这 21 项的模块归属和负项顺序同时记录在根目录的
`module-compatibility.json`。该清单只固化当前实际模块依赖，不从脚本正则或网络请求
自动猜测新域名。仓库检查器验证清单、本文和可选“修改后配置”三者一致：

```bash
python3 scripts/check_module_compatibility.py
python3 scripts/check_module_compatibility.py --profile /path/to/effective.conf
```

- 不额外加入 `play.itunes.apple.com` 或 `play-edge.itunes.apple.com`。iRingo TV 先在
  已解密的 `play-cdn` / `play-edge-cdn` 请求上执行 URL Rewrite，DualSubs 再匹配
  改写后的 URL；目标主机不是新的 TLS 握手入口。
- Apple 精确正项之后继续保留 Apple 通配负项、金融/KYC/风控负项和
  `-<ip-address>`。`api5.futunn.com` 没有对应的活动处理脚本，不应为了广域 MITM
  清单而解除券商端点保护。
- NTP/UDP 123 必须先固定 `DIRECT`；Google Voice 的控制面和媒体例外必须位于全局 `PROTOCOL,STUN,REJECT` 之前。
  全局 STUN 拦截是隐私选择；改为 `DIRECT` 会恢复其他 WebRTC/游戏打洞，但也可能
  暴露公网地址，两种目标不能同时保证。
- 主 Profile 不再复制 Sukka/Fries 模块注入的 `[Host]`、`always-real-ip` 或
  `skip-proxy`。Apple 更新域也不加入配置级 `always-real-ip`：Surge 的 Fake-IP
  映射能保留原始域名并稳定命中前置规则，强制真实 IP 只会增加对 SNI/Host 嗅探的依赖。
  模块行优先于主 Profile，再复制只会形成第三份配置，不能消除冲突。

## 模块实际生效检查

### iRingo 与 WLOC

- WeatherKit、LocationService、Maps、News、TV 与 WLOC 的上述 MITM 主机必须在
  修改后配置中先于 Apple 负项。
- iCloud 的非 Apple 根域还必须保留 `icloud.com(.cn)`、`icloud-content.com`、
  `apple-cloudkit.com`、`apple-livephotoskit.com`、`apzones.com`、`cdn-apple.com`
  与 `apple-dns.net` 负项，避免后续模块漂移把官方同步/内容链纳入 SSL inspection。
- News 的代理参数必须引用现有的 `United States`；不能保留不存在的 emoji 策略名。
- LocationService、Maps 与 WLOC 会同时执行，但它们分别修改地区、地图供应商和
  坐标。当前常见的 US Location + CN/AutoNavi Maps + 自定义坐标是混合语义，主 Rule
  无法替模块统一，必须在每台设备的模块参数中自行保持一致。
- WeatherKit 使用第三方天气源时必须在模块参数中具备有效凭据；主 Profile 或远程
  Rule 无法补齐模块参数。
- WeatherKit 请求的 `country` 决定 `Weather.Replace` 是否处理该地区；
  `AirQuality.Calculate.Algorithm` 决定处理后采用哪套指数算法。配置级 fallback 只在
  `*-US` locale、中国坐标、`Asia/Shanghai` 且缺少 `country` 时补 `CN`，仅为当前
  深圳范围保留无时区窄兜底，不会把用户选择的美标算法改回国标或误改邻近地区。
- Maps v4.6.1 的 `Missing style` 只表示当前 Geo Resource Manifest 不含某些
  可选或历史样式；若日志仍完成 decode、Set TileSets、encode 并以
  `Script Completed` 结束，不应将这些警告判为配置或 MITM 失败。

### DualSubs

- YouTube、Spotify、Universal 与 Transcripts 的脚本主机必须出现在有效 MITM 中，
  并确认当前翻译供应商可用。当前固定基线使用 Google，避免持久化的空 Microsoft
  Token 造成连续重试。
- iRingo TV 的 CDN Rewrite 与 DualSubs Universal Apple TV 分支是配套处理链：
  `play-cdn`/`play-edge-cdn` 负责 TLS 入口，改写后由 DualSubs 匹配 `play` URL。
- 同一个 YouTube/Spotify 请求可能同时命中多个已保留模块。主 Profile 只能让它们
  都具备运行条件，不能从外部指定哪一个响应脚本最终获得修改权；应以请求详情中的
  实际脚本名和输出为准。

### BiliUniverse

- Global 的启用地区与策略名必须真实存在。当前稳定组合使用 `CHN,HKG`，HKG 对应
  `Hong Kong`；不要启用不存在的 `Taiwan` 策略。
- `bilibili-direct.conf` 只固定视频 CDN，不排除 `bilibili.com`、`biliapi.net` 等
  API 主机的 MITM/Script。DIRECT 是路由结果，不等于绕过 HTTP 引擎。
- 官方 Global/Enhanced/ADBlock/Redirect 与其他已保留 Bilibili 模块有请求重叠。
  主 Rule 无法让一个模块的 pre-matching REJECT 为后置模块让路；验证标准是播放、
  搜索、地区选择和 CDN 结果，而不是要求每条重复脚本都执行。

## 已知无法由主 Profile 修复的冲突

- WeatherKit 模块把 Apple AS714/AS6185 的 QUIC 提升为前置 `REJECT-DROP`，会让
  Private Relay 与部分 iCloud TCP/UDP 443 服务回落 TCP/H2。主 Rule 位于模块规则
  之后，无法抢先放行；在“不改模块且全部保留”的约束下不能同时保证完整 QUIC，
  但 Apple 官方为这些 iCloud 服务保留 TCP 443 路径。
- 多套 HTTPDNS 模块存在相同的 pre-matching 拒绝，Sukka 与 Fries 还会对
  `dot.pub`、`doh.pub`、`doh.360.cn` 注入不同 Host 值。主 `[Host]` 排在模块之后，
  无法删除前面的条目；添加第三份只会增加歧义。
- 广告、HTTPDNS、Bilibili、YouTube 与 Spotify 的模块规则均早于仓库主 Rule。
  被模块先行拒绝的连接不能再由 GitHub `DOMAIN-SET,DIRECT` 救回。
- 一个前置模块已经产生最终 REJECT 时，后置模块的 Rewrite/Script 不再执行。这不等于
  后置模块整体失效，但意味着“全部模块的每一条声明都执行”在逻辑上不可实现。

## 每台设备的验证顺序

1. 用 Surge 原生检查确认基础 Profile 可加载。
2. 打开“修改后配置”，确认没有未知策略；核对 21 个 Apple 精确正项均位于 Apple
   负项之前，金融负项仍在模块追加的广域正项之前。
3. 在请求详情中分别验证 WeatherKit、Location/Maps、News、TV、DualSubs、
   BiliUniverse 与 WLOC 的 Script/MITM 命中，而不是只看模块开关。
4. 用真实 App 功能测试最终效果；重复规则以首个实际结果为准。
5. Mac 与 iPhone 分别重复以上步骤。模块参数、策略选择和证书信任不得假定同步。

官方语义参考：

- [Surge 模块优先级](https://manual.nssurge.com/others/module.html)
- [MITM Host List 首条匹配](https://manual.nssurge.com/others/host-list.html)
- [HTTP Rewrite 与 Script 处理顺序](https://manual.nssurge.com/http-processing.html)
- [Surge Rule 首条匹配](https://manual.nssurge.com/rule.html)
