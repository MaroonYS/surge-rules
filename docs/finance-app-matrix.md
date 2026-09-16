# 2026-09-16：配置所有者的 24 个 App 地区清单

本清单是个人账户上下文，不是按照机构总部、App Store 地区或开户资格自动推导。
美国沿用 `Res-Frontier` 美国家宽，其余沿用现有策略，不新建节点或策略组。

| 策略 | App |
| --- | --- |
| Hong Kong | BOCHK 中银香港、ZA Bank、HSBC Reward+、Futubull、HSBC HK、Longbridge |
| Res-Frontier | IBKR、Kalshi、SoFi、Wise、Revolut、Capital One、Coinbase、ether.fi、LemFi、PayPal、Polymarket |
| DIRECT | 中国银行、招商银行、UnionPay／云闪付 |
| United Kingdom | HSBC UK、Krak／Kraken、Lloyds、Monzo |

Wallet 不在此次清单，不扩大已有 Apple 六条账户/账单规则。MEXC、N26、Loqbox、
OnePay、其他银行/券商及共享身份/风控层保留原策略。

## 已有覆盖、迁移与去重

- IBKR 的 21 条既有域名集中到 `us-residential.conf`，从旧文件删除原项。
  其中 UK 2、HK 2、SG 2、JP 1 共 7 条改变出口；另外 14 条原本已是住宅出口。
- `.bankofchina.com` 从通用 Finance 的住宅出口移至 DIRECT，包括其全球共用站点；
  `.boc.cn` 保持 DIRECT。中银香港 `.bochk.com` 是独立域，仍固定 HK。
- `.longbridge.sg` 从 SG 移到 HK，与其余 Longbridge 第一方域一致。
  Futu SG、Moomoo Trustee 等其他 App/实体专用域不因同属一家集团而迁移。
- `.wise.com`、`.revolut.com` 已由 `finance-context.conf` 绑定 `Res-Frontier`，保留原位，
  不在美国文件重复添加。SoFi 和其余既有美国专项同理。
- BOCHK 的 `mb`/`mba.bochk.com`、ZA 的 `bank`/`athena.za.group`、Reward+ 的
  HSBC HK 网站、云闪付的 `yunshanfu.unionpay.com`/`youhui.95516.com` 已有后缀覆盖，
  不为每个页面另加重复规则。Reward+ 身份见 [HSBC 官方介绍](https://www.hsbc.com.hk/credit-cards/rewards/app/)。

## 仅补 12 条缺失记录

| 策略 | 新增记录 | 证据与用途 |
| --- | --- | --- |
| HK | `za.onelink.me`（精确） | [ZA 官网](https://bank.za.group/en/)应用链接；[AASA](https://za.onelink.me/.well-known/apple-app-site-association)绑定 `F89UW68G76.group.za.bank` |
| HK | `cdn.zaticdn.com`、`alicdn.zaticdn.com`（精确） | [ZA 官方下载页](https://bank.za.group/en/app-download)实际引用的脚本/样式/图片资源 |
| DIRECT | `cmbt.cn`（精确） | [招商银行 App 页](https://www.cmbchina.com/MBankWeb/Products/?submenu=android)与其[前端脚本](https://s3gw.cmbimg.cn/srd-a2549394cd7491f-1255000101/script/app.3c941a81.js)确认 Android 下载入口；不将下载入口误称为 iOS API |
| UK | `forms.hsbc.gb`（精确） | [HSBC UK 官网](https://www.hsbc.co.uk/ways-to-bank/mobile/)链接的英国表单入口；主 App 的 `hsbc.co.uk` 已有规则，[AASA](https://www.hsbc.co.uk/.well-known/apple-app-site-association)确认 UK App |
| US | `.kalshi.com` | [Kalshi API 环境](https://docs.kalshi.com/getting_started/api_environments)的正式 REST/WebSocket，覆盖 `external-api` 与 `api.elections` |
| US | `.ibllc.com.cn` | [IBKR 官方连接说明](https://www.interactivebrokers.com/docs/third-party-integrations/tws-settings/best-practice-configure-tws-ib-gateway/connected-ib-server-location-in-tws)列出的中国网关；既有 `.ibllc.com` 无法覆盖此独立域 |
| US | `.transferwise.com` | Wise 正式 [mTLS API](https://docs.wise.com/guides/developer/environments)及 [Open Banking](https://docs.wise.com/guides/developer/open-banking)仍使用旧品牌域 |
| US | `wise-app.sng.link`（精确） | [Wise 官网](https://wise.com/)下载链接；[AASA](https://wise-app.sng.link/.well-known/apple-app-site-association)绑定 `W53MTDV45J.com.transferwise.Transferwise` |
| US | `.revolut.me` | [Revolut 官方付款条款](https://www.revolut.com/legal/payment-terms-revme/)确认付款/收款链接 |
| US | `sofi.app.link`、`sofi-alternate.app.link`（精确） | [SoFi 官方客服深链](https://www.sofi.com/press/sofi-invest-launches-the-sofi-enhanced-yield-etf-to-offer-investors-a-new-income-source/)；两者 AASA 均绑定 `2ZBHHJ9456.com.sofi.mobile` |

招商资源 `s3gw.cmbimg.cn` 已由当前 [Sukka domestic](https://ruleset.skk.moe/List/non_ip/domestic.conf)
中的 `DOMAIN-SUFFIX,cmbimg.cn` 正确直连，公共/模块检查未发现更早的域名冲突，故不再
重复收录。它的验收属于公共资源检查，不伪装成自有离线矩阵可直接证明的首命中。

已确认但不作为生产 App 必需项加入：Kalshi demo `.kalshi.co`；未取得完整交叉证据的
`kalshi.onelink.me`；仅猜测的 `kalshicdn.com`；Wise 网页配置中的服务端 `*.envoy.tw.ee`、
仅营销用途的 CloudFront 图片与遥测域。不增加共享云、KYC、广告或 App Store 后缀。

## 不能由静态域名分流解决的边界

HSBC UK 与 HSBC HK 使用各自专属主机时可分别 UK/HK，但官网公开代码也会出现跨地区
链接和共享 WAF 主机 `hsbc.edge.sdk.awswaf.com`。页面出现链接不等于 App 必须请求，
也不能把共享主机认作 UK 独占并从 HK 抢走。`.hsbc.com` 沿用 HK，现有 Expat 窄例外
仍在它之前；未证实的共享银行主机不擅自改归属。

Reward+ 也提供银联二维码支付。若它与云闪付实际请求同一银联主机，该主机不能仅凭
域名同时走 HK 与 DIRECT。当前银联域按此次明确要求 DIRECT；跨 App 共享支付步骤、
共享身份/风控供应商及 iPhone 登录后链路仍需设备记录，不声称整个 App 的每个请求都
已固定到单一区域。不为验收主动触发登录、开户、证件上传或付款，不开启金融 MITM。

`tests/test_owner_finance_matrix.py` 独立锁定 24 App、迁移唯一性、专属精确域边界及反例；
`routing-acceptance.json` 和既有首命中测试同步更新。所有自有活动域集进行跨文件重复、
后缀包含和优先级校验。公共订阅的同域记录可能必须保留：其出口若不同，由较早的个人
定向规则覆盖，不能为了字面去重而删除个人出口需求或复制/改写上游大型资源。

静态通过不代替模块 `pre-matching`、IP/DNS、节点可用性和手机同步验收。
