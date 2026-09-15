# 广告平台拦截器：原有短信白名单的窄范围补丁

## 目标与边界

当前模块自带五条 `DIRECT,extended-matching` 精确主机规则，但 `.mob.com`、`.jiguang.cn` 的无条件 `REJECT,pre-matching` 会先于普通规则执行。这是可确定的规则冲突，不等于已经观测到短信发送失败。[Surge 规则优先级](https://manual.nssurge.com/rules/overview.html)

补丁仅把这两条后缀拒绝改为 `AND(原后缀, NOT(原精确白名单))`，继续保留 `pre-matching`，并在每个域名叶子保留 `extended-matching`。原五条 DIRECT 不变：

| 后缀 | 排除的精确主机 |
| --- | --- |
| mob.com | init.sms.mob.com、sdkapi.sms.mob.com、code.sms.mob.com |
| jiguang.cn | smartop-sdkapi.jiguang.cn、sdk.verification.jiguang.cn |

后缀根、其他子域、五个主机的更深层子域继续被原范围拒绝；不放行整个供应商，不更改 jpush 拒绝、模块名称、顺序、启用状态、URL Rewrite、MITM、DNS、General、Bili 或 WeatherKit。补丁只解决该模块的这两条冲突；其他模块/网络条件仍需单独验收。

## 只读补丁工具

`scripts/patch_advertiser_sms.py` 只读取明确给定的现有模块，默认向标准输出生成 `apply_patch` 格式的两行替换，**不会写文件、联网或重载 Surge**。标准错误仅输出状态和输入/候选 SHA-256，不输出配置、模块参数或凭据。

```sh
python3 scripts/patch_advertiser_sms.py /absolute/path/to/installed.sgmodule --check
python3 scripts/patch_advertiser_sms.py /absolute/path/to/installed.sgmodule --expect-sha256 REVIEWED_SHA256
python3 -m unittest discover -s tests -p test_advertiser_sms.py -v
```

`--check`：0 = 两条已修复；1 = 两条仍为原规则、需要补丁；2 = 输入或目标契约漂移，拒绝自动处理。默认生成模式：0 = 已输出补丁或已修复无需输出；2 = 拒绝。

安全约束：要求原模块身份、单一 `[Rule]`、原五条精确白名单及目标后缀规则唯一；拒绝缺失、重复、变更、半修复、非 UTF-8、CRLF/空字节及符号链接。无关上游更新不要求匹配整个旧文件，更新内容逐字保留。可用 `--expect-sha256` 锁定本次已经审查的字节；生成后如文件再变化，必须重新检查，不能盲用旧补丁。

## 部署与验收

1. 在目标设备分别确认**当前启用的原模块**及实际文件，不导入历史完整修复版替代当前上游。记录文件哈希、模块名称、顺序与启用状态；保存该文件的可恢复备份。
2. 运行 `--check`，审阅默认输出的两行补丁，再由已获授权的操作者使用 `apply_patch` 应用至原路径。保持名称和启用状态不变，不同时启用原版及第二个副本。
3. 再运行 `--check`，确认状态为 PATCHED、文件哈希等于生成时的 candidate_sha256。将原始文件与候选逐行比较，应恰好只有两条差异。
4. 执行 Surge 语法检查并重载；从实际有效规则确认：五个精确主机不命中两条新 guard，原 DIRECT 仍存在，其他同后缀主机仍命中 guard。仅检查源码不代表运行引擎已经加载。
5. 真正短信收发、App 登录及 iPhone 上的生效情况需要设备端验证；离线测试不作该保证。

## 当前设备定位与更新维护

2026-09-15 只读定位到 Mac 已启用原模块：

实际文件位于 Mac 的 Surge `Installed Modules` 目录；文件名由本机安装元数据确定，不能从其他设备照抄。

名称 `广告平台拦截器`；模块声明日期 `2026-08-22 10:20:51`；修复前 SHA-256 为 `541091087e79e7d7d411f004e17bc27e159085072f86806d2341b7f102766d6e`。第 71/74 行是两条原始目标规则。这个哈希仅记录审计输入，不是永久要求固定整个模块版本。

当前可访问的 iCloud Surge `Documents` 中未找到对应广告模块文件，因此**不能从 Mac 安装路径或 iCloud 配置同步推断 iPhone 已安装、启用或已修复**。需在 iPhone 模块列表定位实际安装实例，再单独完成部署/验收，不往 iCloud 根目录臆造一个同名文件来宣称完成。

官方定义 Installed Modules 是通过 URL 安装，Local Modules 是配置目录的 `.sgmodule`；模块启用状态不跨设备同步。[Surge 模块文档](https://manual.nssurge.com/profile/module.html)

本次安全限定的文件检查未确定原始安装 URL，也未证实自动更新周期；安装模块的后续更新可能覆盖原位补丁。每次更新该模块后重新运行 `--check`：原冲突回来时返回 1，目标规则/白名单变形时返回 2，均应重新审查。工具本身不设置定时任务、不关闭上游更新。

若以后选择长期自维护本地模块，应从**届时当前完整上游文件**生成候选、核对全部差异，并分别授权两设备切换实例及启用状态；不能把现有旧整文件直接作为长期上游，也不能仅新增普通白名单来覆盖 `pre-matching`。
