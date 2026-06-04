# Test Fixture Privacy Rules｜真实测试资料处理规则

## 1. 规则目的

本项目开发过程中可以使用真实 PDF / PPT / 长图测试解析、转写、审核页和 Context Asset Index。但这些文件只是本地测试材料，不是正式 Skill 内置 demo。

正式 Skill 包、README、PRD、prompt 示例、schema 示例、`examples/` 目录和对外说明中，不应包含真实测试 PDF 里的可识别品牌信息和商业数据。

## 2. 真实测试材料可以放在哪里

真实测试材料只能放在本地私有目录，例如：

```text
_private_test_runs/
```

该目录用于本机开发验证，不作为 Skill 发布内容。

## 3. 不能写入正式 Skill 包的信息

如果要把测试材料沉淀为正式 demo、样例输出或文档说明，必须删除或改写：

| 类型 | 处理方式 |
|---|---|
| 真实品牌名 | 改为虚构品牌或泛化名称 |
| 真实竞品名 | 改为虚构竞品或泛化名称 |
| 产品线 / SKU / 规格 | 改为假 SKU 或泛化结构 |
| 价格 / 促销价 / EDLP / S+ | 删除或改成区间/占位信息 |
| 预算 / 费用 / 激励金额 | 删除或改成虚构示例 |
| 销量 / 曝光 / 搜索增长 / ROI / 转化数据 | 删除或改成虚构示例 |
| 渠道 / 经销商 / KA / 供应商 / 部门 | 删除或泛化 |
| 内部策略 / 货盘 / 渠道治理机制 | 仅保留抽象方法，不保留真实执行表 |
| 原始 PDF / 页面截图 | 不进入正式 examples，除非已授权公开 |

## 4. 可保留的内容

正式 Skill 可以保留从真实测试中抽象出的通用方法：

- 需要保留页码锚点。
- 视觉页和复杂表格需要低置信度标注。
- 品牌 BPM 资料应归入品牌、项目、素材、网络、案例等上下文，而不是强行产品化。
- Context Asset Index 应记录来源、状态、风险和下游调用限制。

## 5. 当前本地测试样本

`_private_test_runs/private_product_training_sample/` 是本机私有产品培训测试样本。`_private_test_runs/private_brand_bpm_sample/` 是本机私有品牌 BPM / channel strategy 测试样本。它们都不属于正式 Skill 内置 demo，并应被 `.gitignore` 排除。

如果未来需要把这个样本转成正式 demo，应另建匿名化版本，例如：

```text
examples/anonymous_brand_bpm/
```
