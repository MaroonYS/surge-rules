# 模块有效顺序

本页记录当前两台设备的模块优先级基线。列表均对应 Surge 的
**Adjust Effective Order** 界面，从上到下排列；越靠下优先级越高。
模块启用状态与顺序不会在 Mac 和 iPhone 间同步，因此两端必须分别维护。

只调整有作者说明或实际冲突证据的关系，其他模块保持设备原有相对顺序：

- `广告平台拦截器` 的“顶部”要求来自 Loon；换算为 Surge 后应放在 UI 最底，
  才会在修改后配置中最先执行。
- DualSubs 官方要求 Surge 的 YouTube 去广告模块位于 DualSubs YouTube 下方；
  `YouTube双语翻译` 自身又要求位于去广告模块下方。
- BiliUniverse 四个官方模块互无依赖，保留当前顺序。
- iRingo TV 与 DualSubs Universal 只要求同时启用，没有硬性前后关系。
- Mac 内置 `Disable HTTP Engine` 必须保持关闭。它会让 VIF 接管的明文 HTTP
  跳过 HTTP Engine，因而无法仅靠 `force-http-engine-hosts` 恢复相关 Script、
  Rewrite、URL-REGEX 与 Map Local；HTTPS MITM 和显式系统 HTTP Proxy 不受这一
  限制。关闭该开关是让下列功能模块完整工作的前提，不代表删除模块。
- 同一请求/响应只能执行一个匹配的 Script。YouTube、Spotify 与 Bili 的重叠脚本
  无法靠排序全部同时执行；下面的顺序只确定高优先实现，未重叠功能仍可工作。

## Mac

```text
HomeKit Accessories Quirk
Game Console STUN
Fix Windows No Network Alert
HTTP Download Optimization
router.com
Google Home Devices
AllInOne
BoxJs
Github Private
Script Hub(β): 重写 & 规则集转换
[Sukka] Always Real IP Plus
[Sukka] Local DNS Mapping
[Sukka] Surge Reject MITM
Spotify(>=iOS15)
毒奶特供
谷歌中国重定向
流媒体解锁检测
节假日信息
Sub-Store
🍟 Fries: 🚫 Block HTTPDNS
🍟 Fries: 🔓 MitM
🍟 Fries: 🌐 General Enhanced
🍟 Fries: 🌐 DNS enhanced
 iRingo: 🌤 WeatherKit
 iRingo: 📍 LocationService
 iRingo: 📰 News
 iRingo: 📺 TV app
 iRingo: 🗺️ Maps
🍿️ DualSubs: ▶️ YouTube
YouTube去广告(>=iOS15)
🍿️ DualSubs: ➕ AddOn (Akamaized)
🍿️ DualSubs: ➕ AddOn (Microsoft Translate)
🍿️ DualSubs: 🎵 Spotify
🍿️ DualSubs: 🎵 Spotify Transcripts
🍿️ DualSubs: 🔣 Universal
[Sukka] Enhance Better ADBlock for Surge
通用解锁
YouTube双语翻译
Spotify歌词增强
拦截HTTPDNS
QX重写&规则集转化
适配可莉插件中心
可莉广告过滤器
快捷搜索
Bilibili 1080P
哔哩哔哩增强
📺 BiliBili: ⚙️ Enhanced
📺 BiliBili: 🌐 Global
📺 BiliBili: 🔀 Redirect
📺 BiliBili: 🛡️ ADBlock
广告平台拦截器
```

Mac 的 DNS 顺序有意保持 `Sukka Local DNS Mapping` 在上、
`Fries DNS enhanced` 在下，因此重复 Host 由 Fries 获得更高有效优先级。

## iPhone

```text
[Sukka] Enhance Better ADBlock for Surge
毒奶特供
可莉广告过滤器
[Sukka] Surge Reject MITM
[Sukka] Always Real IP Plus
🍟 Fries: 🌐 DNS enhanced
[Sukka] Local DNS Mapping
🍟 Fries: 🌐 General Enhanced
🍟 Fries: 🔓 MitM
🍟 Fries: 🚫 Block HTTPDNS
HTTPDNS拦截器
BoxJs
Github Private
Script Hub(β): 重写 & 规则集转换
QX重写&规则集转化
适配可莉插件中心
Sub-Store
router.com
Google人机验证
应用安装
应用调试
流媒体解锁检测
节假日信息
快捷搜索
谷歌中国重定向
🔫 Jump2Forward
Emby分流
Trakt 增强
Vvebo 个人页修复
X(Twitter)网页版去广告
Line去广告
Reddit 去广告
京东去广告
大麦去广告
小红书去广告
微信公众号去广告
拼多多去广告
淘宝去广告
滴滴出行去广告
百度网盘去广告
百度网页去广告
网易云音乐去广告
航旅纵横去广告
酷安去广告
闲鱼去广告
阿里云盘
阿里云盘去广告
阿里云盘定时签到
飞猪旅行去广告
高德地图去广告
🍿️ DualSubs: 🎵 Spotify
🍿️ DualSubs: 🎵 Spotify Transcripts
Spotify去广告
Spotify(>=iOS15)
Spotify歌词增强
🍿️ DualSubs: ▶️ YouTube
YouTube去广告隐藏Shorts版@Aioneas
Apple WLOC 定位修改
 iRingo: 🌤 WeatherKit
 iRingo: 📍 LocationService
 iRingo: 🗺️ Maps
 iRingo: 📰 News
 iRingo: 📺 TV app
🍿️ DualSubs: 🔣 Universal
哔哩哔哩增强
📺 BiliBili: ⚙️ Enhanced
📺 BiliBili: 🌐 Global
📺 BiliBili: 🔀 Redirect
📺 BiliBili: 🛡️ ADBlock
广告平台拦截器
```

iPhone 的 DNS 顺序有意与 Mac 不同：`Fries DNS enhanced` 在上、
`Sukka Local DNS Mapping` 在下，因此重复 Host 由 Sukka 获得更高有效优先级。
