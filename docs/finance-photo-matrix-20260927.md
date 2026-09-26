# 2026-09-27 照片中的 29 App 分流

这是一份配置所有者指定的出口清单，不是服务注册地、开户资格或可用国家的声明。
沿用原策略组；不修改节点、共享 KYC、DNS、MITM、模块或任何 Sukka 订阅。

| 出口/策略 | App |
| --- | --- |
| Hong Kong | AlipayHK、ANT BANK、EleBank、FSM、Futubull、Longbridge、uSMART HK、VBrokers |
| 美国住宅 Res-Frontier | Avalanche Card、BBAE Pro、Credit Karma、Firstrade、IBKR、Moomoo、myEquifax、myFICO、Neverless、Schwab |
| Singapore | dtcpay、SGB、Starryblu、uSMART SG |
| United Kingdom | iFAST GB、N26、Kraken（用户写作 karken） |
| Crypto | Bitget、Bybit |
| Web3 | Bitget Wallet |
| DIRECT | TenPayGo 已确认的协议/资讯主机；支付会话 API 尚未实测 |

## 本次变更与官方证据

- **AlipayHK**：增加 `.alipayhk.com`、`.alipay.hk`、`.alipayhk.co`。
  [官网](https://www.alipayhk.com/en/shoppers/)链接其钱包入口、文档与短链；
  [商户迁移文档](https://docs.alipay.hk/alipayhkdocs/hk/migration_project_online/en-US)
  确认 `merchant.alipay.hk`。不捕获整个 Alipay/Ant 中国平台。
- **EleBank**：增加 `.elebank.com`，保留既有 `.airstarbank.com`；
  [官方介绍](https://www.elebank.com/en-hk/about-us)确认品牌。
- **FSM**：增加 `.fsmone.com.hk`、`.fsmglobal.hk` 和精确
  `secure.fundsupermart.com.hk`。[FSM Global 官网](https://www.fsmglobal.hk/about-us)
  与 [FSMOne 旧入口](https://www.fsmone.com.hk/article/article-details/375300)
  确认新旧品牌及资源主机。不捕获全球 iFAST、Fundsupermart 平台。
- **uSMART HK / SG**：保留 `.usmart.hk` / `.usmart.sg`，分别补精确
  `hk.usmartglobal.com` / `sg.usmartglobal.com`；
  [旧香港入口](https://www.usmartsecurities.com/en)跳转香港站，因此精确
  `www.usmartsecurities.com` 在 HK 层优先，其余证券共享父域维持原住宅兜底。
  [SG 官网](https://www.usmart.sg/)还证实两个新加坡专用腾讯桶：
  `web-static-sg-prd-singapore-1437682127.cos.accelerate.myqcloud.com`、
  `jy-common-sg-prd-singapore-1437682127.cos.accelerate.myqcloud.com`。
  不捕获整个 `usmartglobal.com` 或 `myqcloud.com`。
- **SGB**：增加 `.sgb.com`。[官网](https://www.sgb.com/)与
  [官方 App](https://apps.apple.com/id/app/singapore-gulf-bank/id6702016631)
  确认 Singapore Gulf Bank；虽然受巴林监管，仍遵循用户指定 SG 出口。
- **Starryblu**：增加 `.starryblu.com`、精确 `h2static.wotransfer.com`、
  `starryblu-public.oss-accelerate.aliyuncs.com`；
  [官网](https://www.starryblu.com/en/)直接加载这些资源。
  [公司页](https://www.starryblu.com/en/company)确认 WoTransfer 主体，
  但不将整个 `wotransfer.com` 或阿里云后缀划入 SG。
- **iFAST GB**：增加 `.ifastgb.com`，覆盖 [官网](https://www.ifastgb.com/)
  和 `static.ifastgb.com`；不改变其他地区 iFAST。
- **Avalanche Card**：`.avalanchecard.com` 从 Web3 迁往美国住宅；
  [官方 App 条目](https://apps.apple.com/us/app/avalanche-card-pay-anywhere/id6737233538)
  确认是 Rain 的卡片应用，不迁 Avalanche 链的 `.avalanche.network`。
- **Neverless**：按用户要求增加 `.neverless.com` 至美国住宅，来源
  [官网 App 页](https://neverless.com/app)；不代表平台允许美国开户。
- **Moomoo**：`.moomoo.com` 及存量窄条 `.api.moomoobull.com` 从 HK 迁至美国住宅；
  增加 `.moomooapp.com`、`.moomoocn.com`。
  [官方前端兼容包](https://cdn.futustatic.com/moomoo_common/dist/moomooHeadFootMFI-055bc6a5a5730d97877e.js)
  确认这组品牌命名空间。既有 API 窄条的迁移遵循用户新地区选择，
  **不是已观察到 App 调用的证明**，也不扩大至整个 `moomoobull.com`。
- **Bitget Wallet**：增加精确 `web3.bitget.com`、`portal-web3.bitget.com`、
  `docs.bitkeep.io`、`cdn.bitkeep.vip`、`static.bitkeep.vip`、`www.bgw.live`、
  `newshare.bwb.global`，以及旧品牌后缀 `.bitkeep.com`。
  [官方钱包下载页](https://web3.bitget.com/wallet-download)可确认钱包、API Portal、
  APK 和工具链接；[旧站](https://bitkeep.com/)重定向钱包官网。
  Web3 资源放在 Crypto 前；只允许两个精确 Bitget 主机覆盖交易所父域。
  Bitget/Bybit 已有规则不重复添加，`www.bitget.com`、`api.bitget.com` 仍走 Crypto。
- **TenPayGo**：[官方商店说明](https://play.google.com/store/apps/details?id=com.tencent.wxpai&hl=en)
  明确为访华游客提供中国大陆支付。现有公开 Sukka 域名集没有命中两个已核实主机，
  因此新增精确 `gtimg.wechatpay.cn`、`posts.tenpay.com` 至 DIRECT。
  不扩大 `wechatpay.cn`、`tenpay.com`，也不迁移发卡行/3DS 共享认证。

其余已存在的 ANT BANK、Futubull、Longbridge、VBrokers、BBAE、Credit Karma、
Firstrade、IBKR、Equifax/FICO、Schwab、dtcpay、N26、Kraken 按原规则复用，不重复添加。

## 共享边界与验收

Futubull 和 Moomoo 官网都实际使用 `cdn.futustatic.com`。
`.futustatic.com`、`.futunn.com` 等共用资源仍保留 HK；
`.moomooequity.com` 的官方代码标为 SG 员工股权业务，本次不作无关迁移。
这意味着纯域名规则不能同时保证两个 App 的每个共享请求各自走不同国家。
同样，uSMART 的全球共享服务和现有 Sumsub/Veriff 等身份验证兜底保持不变。

本次增加 30 条记录，迁移 3 条既有记录，不新增规则订阅资源。
活动资源仍 15 个、主规则仍 54 条；本地记录由 743 增至 773。
新测试逐个锁定 29 App 的已证主机、主骨架/展开版首匹配、重复归属和共享父域负例。
顺序例外测试要求主机、策略及相对顺序全部吻合，不能泛化成忽略重叠。
原 24 App、LemFi、Trading 212 和全部 Sukka 保留测试继续执行。

这些是静态域名与规则验收，不是登录、开户、付款、KYC 或 iPhone 实机抓包验收；
未知/动态 App 主机、共享 CDN、裸 IP 和模块 pre-matching 仍可能影响实际请求。
用户照片和私人设备配置不进入公共仓库。
