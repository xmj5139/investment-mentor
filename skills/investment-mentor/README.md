# Investment Mentor 0.4.5 候选版

面向中国机构的未上市企业股权投资研究。本版保留0.4.4结构与ESG模块，主要增量为description的英文任务词，以及14组关键规则中英双语表达。中文主体和默认中文报告保持；不强制内部推理语言，不要求思维链展示。

完整项目详细/全面正文15节，第9节ESG含6子节；简版正文5节，第4节有ESG子节。报告信息、三层、六简报、9视角、12维和DP五层保留。任务与证据边界见入口，正式格式见[输出要求](references/output.md)，人读语言见[写作要求](references/writing.md)。短问直接答，明确专项和用户模板按既定规则映射。

普通聊天使用[独立提示词](STANDALONE_PROMPT.md)，无外部依赖；运行包按入口读取必要引用。维护时依次运行build_rules.py、build_output.py、build_prompt.py，再validate.py .。三种生成器的--check核对同源一致，不评事实或翻译质量。

[双语审阅](BILINGUAL_REVIEW.md)、[本版测试](tests/TEST_REPORT.md)、[适配边界](COMPATIBILITY.md)分别记录语言维护、真实行为与能力限制。完整包含维护与测试摘要；运行包不含原始模型答案、私有路径或运行器。旧版保留，不自动安装替换、发布或新增许可。
