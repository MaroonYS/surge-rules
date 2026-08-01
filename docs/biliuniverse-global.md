# BiliUniverse Global compatibility

核对对象：BiliUniverse Global `v0.8.21`，发布日期 2026-05-22。

官方 Global Surge 模块没有 `[Rule]`。它只对 `www.bilibili.com`、
`search.bilibili.com`、`app.bilibili.com`、`app.biliapi.net`、
`api.bilibili.com`、`api.biliapi.net` 与 `grpc.biliapi.net` 执行脚本和 MITM，
并通过 `ability=http-client-policy` 为番剧/API 请求动态选择地区策略。

`bilibili-direct.conf` 只包含以下媒体 CDN 后缀：

```text
.bilivideo.com
.bilivideo.cn
.bilivideo.net
```

两组主机没有交集，因此 CDN 的前置 `DIRECT` 不会抢走 Global 的 API 请求，
也不会阻止它自动识别 CHN/HKG/TWN 并选择地区策略。不要把
`.bilibili.com`、`.biliapi.com`、`.biliapi.net` 或 `.biliimg.com` 加入该文件。

## 与当前配置匹配的模块参数

配置所有者提供的 Surge 配置定义了 `Hong Kong`，没有定义官方默认使用的
`🇭🇰香港`、`🇹🇼台湾` 或 `🇲🇴澳门`。因此 Global 参数至少应调整为：

```text
ForceHost = 1
Locales = CHN,HKG
Proxies.CHN = DIRECT
Proxies.HKG = Hong Kong
Storage = Argument
LogLevel = WARN
```

只有在配置中建立对应的稳定策略后，才应把 `TWN` 或 `MAC` 加入 `Locales`。
`ForceHost=1` 必须保留；官方说明返回 IP 会严重影响域名分流和 CDN 重定向，
也会使本仓库的 DOMAIN-SET 无法匹配媒体地址。

## PCDN/MCDN 边界

前置 `.bilivideo.cn` 会延续旧
`DOMAIN-KEYWORD,bilivideo,DIRECT,extended-matching` 的强制直连语义，并覆盖
后续 SKK 对 `mcdn.bilivideo.cn` 的处理。这不影响 Global 模块，但如果以后同时
安装 BiliUniverse Redirect 或希望恢复 PCDN/MCDN 拦截，应重新评估该后缀，不能
同时要求其无条件前置直连。

CI 每次推送及每周健康检查都会下载官方最新 Global Surge 模块，确认：

- 默认仍为 `ForceHost=1`；
- 仍提供 `http-client-policy` 动态地区选择；
- Script/MITM 没有开始接管 `bilivideo` CDN；
- 模块 MITM 主机没有与本仓库的前置 DIRECT 后缀重叠。

官方来源：

- [Global 使用指南](https://biliuniverse.github.io/guide/global)
- [Global 最新 Surge 模块](https://github.com/BiliUniverse/Global/releases/latest/download/BiliBili.Global.sgmodule)
- [Global 动态策略源码](https://github.com/BiliUniverse/Global/blob/main/src/request.js)
