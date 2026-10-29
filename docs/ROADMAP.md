# 待实施改进

本页来自近期测试的一般性问题整理，**尚未实施为新版本**。0.4.5内已有多数边界规则，重点是减少重复、改善交付核对和增加可检查的匿名反例。

| 优先项 | 拟做内容 | 验收方式 |
|---|---|---|
| 执行证据 | 在宿主支持时对照实际动作账本；没有账本则如实说明记录层级，不制造强制工具依赖 | 没有调用、返回失败及工具样式文本均不能写已核验 |
| 图表与口径 | 保留标题、图例、类别、期间、单位、主体与指标；下限不能当精确数，不同指标先对齐 | 匿名图例、时间轴、累计/当月、产值/收入和人员口径反例 |
| 财务桥与计算用途 | 输入属性、利润到现金、共同成本到产品成本、内转到合并收入分开；替代量受实际需要与可供量约束 | 复算及检查成本/数量是否重复使用，条件数不转成现实结论 |
| 跨轮纠错 | 明确错误、依赖、修正和剩余未知；保留仍成立的事实，不因提问就虚构旧错 | 同时查新增错误、过度撤回、状态迁移与占位符 |
| ESG与权利 | 按实际义务决定前置/投后安排；区分所有权、有效许可及其他合法使用安排 | 无据的统一整改安排、专利必须自有及评分门槛应被拒绝 |
| 人读与效率 | 保留三层、15节与三档，控制简报重复，短追问只更新受影响内容 | 篇幅提示及人工审阅，不为缩短删除重要条件 |

关键中英文维护继续使用一套规则，不扩展为两套工作流：

- **Execution:** Match execution claims to actual actions when records exist; tool-shaped text and registration are not completion.
- **Evidence:** Preserve claim type, scope, date, and uncertainty across summaries, risks, and actions.
- **Finance:** Reconcile cash, profit, cost pools, quantities, and internal transfers; conditional arithmetic is not a project fact.
- **Correction:** Retract actual errors, repair dependencies, preserve valid evidence, and review new claims.
- **Applicability:** Determine obligations and rights from actual activities and valid arrangements, not blanket labels.

这些短句是待整理方向，不能据本页声称已经在SKILL中增加或通过回归。真实案例只用来识别通用错误模式，后续用新的匿名合成题复现，公开库不存真实案例变体或专有数据。
