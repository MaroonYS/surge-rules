# 重点业务的分流完整性与验收边界

本轮固定已确认的域名归属、先后顺序和生成契约，不把静态规则通过当成完整登录证据。
`surge-main.conf` 是规则参考骨架，不是设备完整配置；接入时只合并本次变更，不能覆盖
设备已有的进程例外、Private Relay 选择、DNS、MITM、节点或策略组。

## 优先保护的业务

| 策略 | 点名业务 | 不应发生的回退 |
| --- | --- | --- |
| Switzerland | MEXC 的 15 条既有第一方/专属资源 | 旧 UK 或 Crypto、模板遗漏 CH |
| United Kingdom | N26、Loqbox、Kraken/Krak、Monzo、Lloyds、HSBC Expat | Expat 被 HK 的 `.hsbc.com` 抢先、未登记窄辅助域 |
| Res-Frontier | LemFi、Coinbase/Base、ether.fi、OnePay、Capital One、Equifax、PayPal、X、Google Account/Voice、Polymarket | 业务域回落普通 PROXY、Apple 账户/账单与 PayPal 分离 |
| Hong Kong | 已指定的香港银行、Futu/Moomoo、Longbridge | 将共享香港账户基础设施重新推断为 SG |
| Singapore | 其他新加坡专属域，如 Futu SG、Moomoo Trustee；Longbridge/IBKR 以最新个人清单为准 | 未经要求改变其他 App 的归属 |
| Crypto / Web3 | 既有 Bybit 等交易所、钱包和链上业务 | 擅自更改手动选择，或把 MEXC 再塞回 Crypto |

N26 的英国出口是现有用户选择，不代表银行所在地。域名路由也不改变各平台对
实际居住地、身份、账户或产品的资格要求。

2026-09-16 新增的 [24 App 清单](finance-app-matrix.md)是这些业务的最新要求；
IBKR 区域域统一美国住宅、Longbridge SG 域统一 HK、中国银行全球域直连，
并补齐新点名 App 的已证实缺失记录。共享银行/WAF/银联主机的边界仍明确待验收。

LemFi 的两条首方后缀及五个精确租户单独纳入首命中、子域覆盖、反例和唯一归属回归。
官网/API/邮箱验证入口/支持与已确认深链同走美国住宅；公开资源证据不等于原生 App
完整登录、KYC 或支付链路实测，也不要求为了验证路由而新触发任何交易或开户。

## 共享认证明确待验收

2026-09-15 保持 `identity-context.conf` 逐字不变。不添加以下候选，也不改变现有
`.sumsub.com`、`.veriff.com` 等共享供应商策略：

| 项目 | 公开证据 | 本轮处理 |
| --- | --- | --- |
| N26 Keyless 精确主机 | [当前认证代码](https://app.n26.com/build/js/banking-features-auth-biometric-LoginPage.60e488b5.js)配置 N26 认证/登记路径；[官方用途](https://support.n26.com/en-eu/security/account-protection/keyless-authentication)为生物认证、设备关联 | UK 精确规则仍为候选，未部署 |
| Loqbox Veriff | [公开配置](https://app.uk.loqbox.com/api/config)指定 API，主脚本加载公共 SDK | 共享 API/CDN 不认作 Loqbox 独享；未新增域名或改地区 |
| MEXC / ether.fi / Bybit Sumsub | 供应商重合，但 [SDK 文档](https://docs.sumsub.com/docs/get-started-with-web-sdk)说明实际地址可由地区令牌决定 | 默认 `api.sumsub.com` 不当成用户已观测会话；不整段改瑞士 |

在已核查公开证据中，尚未确认这些不同地区 App 实际共用同一个认证主机的冲突。
这不等于证明没有冲突；第一方核验页面也可能继续调用第三方 SDK。Surge iOS 的
[进程规则限制](https://manual.nssurge.com/rules/process.html)意味着真正相同的共享
主机不能仅靠域名规则自动跟随调用 App。

## 发布前静态门禁

```sh
python3 -m unittest discover -s tests -v
python3 scripts/validate.py --strict
python3 scripts/build_expanded.py --check
python3 scripts/check_module_compatibility.py
```

测试包括点名业务首命中、主骨架/展开版一致、CH 缺失、MEXC 错投 Crypto、HSBC
具体重叠的策略/顺序约束、Apple 窄规则边界，以及公共共享后缀不被扩大归属。
外部动态资源、模块、IP、DNS、原生 App 和实际会话不是这些离线测试的模拟范围；
未知外部匹配不得被悄悄跳过后报告为通过。

短信补丁另用 [精确排除检查器](advertiser-sms-patch.md)验证，普通主配置白名单无法
覆盖模块中的 `pre-matching` 拒绝。模块更新后须复查补丁，不能声称原位编辑永久保留。

## 设备验收

1. 确认设备已重载包含 CH 和 Apple 窄规则引用的配置，目标外部资源下载就绪。
2. Mac 检查实际有效规则，而非只检查源文件；iPhone 必须独立确认配置及模块启用状态。
3. 正常使用时记录登录、验证码、主要 API、支付，以及确有业务需要时的 KYC/人脸流程。
   不为网络测试重新开户或提交证件，不主动触发不必要的安全验证。
4. 仅记录 App、步骤、时间窗口、hostname、命中规则/策略和是否失败；不采集 Cookie、
   令牌、验证码、证件、URL 查询串或正文，不要求开启金融 MITM。
5. 已观察必要主机命中预期策略或明确例外才通过；非预期 DIRECT/FINAL/REJECT、
   未分类主机或模板回退均不能通过。未观察到的步骤继续标为待验收。

`include-all-networks=false`、`include-apns=false` 及既有 UDP 拒绝降级保持不变。
资源 ready、语法 OK 或 Mac 通过，不是 iPhone 零绕过或全部登录链路通过的保证。
