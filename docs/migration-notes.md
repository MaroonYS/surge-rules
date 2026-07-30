# Migration notes

本仓库的规则数据来自配置所有者提供的 555 行 `[Rule]` 清单，并按最终策略拆分。

## 已迁移覆盖

| 来源策略 | 仓库位置 | 处理 |
| --- | --- | --- |
| `DIRECT` | `direct-cn.conf` | 全部迁移 |
| `HK-FINANCE` | `hk-finance.conf` | 全部迁移 |
| `SG-FINANCE` | `sg-finance.conf` | 全部迁移 |
| `JP-FINANCE` | `jp-finance.conf` | 全部迁移 |
| `KR-FINANCE` | `kr-finance.conf` | 全部迁移 |
| `UK-FINANCE` | `uk-finance.conf` | 全部迁移 |
| `Res-Frontier` | `us-residential.conf` | 所有美国第一方金融域名迁移；Apple Cash/Pay 在主规则显式处理 |
| `Finance` | `finance-context.conf` | 跨地区金融机构自身域名迁移 |
| `Crypto` | `crypto.conf` | 全部迁移 |
| `Web3` | `web3.conf` | 全部有效语义迁移 |
| `AIGC` | `apple-ai.conf` | 全部迁移，并改用独立 `Apple-AI` 策略 |

没有任何金融机构因为“推测未使用”而被删除或归档。

## 等价去重

来源中的：

```text
.moonbeam.moonscan.io
.moonscan.io
```

前者已经被后者完整覆盖，因此仓库只保留 `.moonscan.io`。实际匹配范围不变。

## 有意调整

- 删除全局 `PROTOCOL,STUN,REJECT`，避免破坏 WebRTC、FaceTime 和视频验证。
- Private Relay 改用独立 `Private-Relay` 策略，不与普通 Apple 服务共用选择状态。
- Apple Intelligence 改用独立 `Apple-AI` 策略，不随通用 AIGC 切换。
- Apple Cash/Pay 三条 Apple 域名在主规则中显式 `DIRECT`，不进入住宅域名集。
- 共享支付聚合、KYC、验证码、设备指纹和反欺诈供应商不进入 `Finance`。

最后一项涉及 52 个共享第三方域名。它们被不同地区和非金融站点共同使用，
全局绑定到一个金融出口会造成会话路径分裂和大范围误匹配。正常站点若被广告规则误拦，
应按 Surge 命中日志添加具体主机名例外。
