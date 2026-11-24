# Investment Mentor 0.5.0（人读表达优化版）

面向中国机构的未上市企业股权投资研究。分析指定基金时分别给出项目判断和基金适配，按已确认且适用的约束填基金条件卡。项目单独研究沿用 CD／DP／CI 和证据规则。中文为默认报告语言，14组共同规则由同一份中英文数据维护。

完整项目详细/全面正文15节，第9节ESG含6子节；简版正文5节，第4节有ESG子节。报告信息、三层、六简报、9视角、12维和DP五层保留。任务与证据边界见入口，正式格式见[输出要求](references/output.md)，人读语言见[写作要求](references/writing.md)。短问直接答，明确专项和用户模板按既定规则映射。

普通聊天可直接使用[完整独立提示词](STANDALONE_PROMPT.md)。安装技能的宿主从 [SKILL.md](SKILL.md) 按需读取引用。完整包还可按任务生成独立提示词。在技能目录执行以下示例。

```shell
python -X utf8 -B scripts/build_prompt.py --task screening --depth brief --output screening-prompt.md
python -X utf8 -B scripts/build_prompt.py --task follow-up
```

正式报告任务支持 project、screening、diligence、valuation 和 monitoring，档位选 brief、detailed 或 comprehensive。finance、esg、follow-up 用于单项问题，直接回答当前问题。生成的任务提示词只适用于所选任务。范围扩大时使用对应任务提示词或完整版本。

报告交付前按[复核规则](references/review.md)检查。可选检查器核对格式、明确占位符、证据引用和已声明的数值核对项。证据原文、适用条件和投资判断仍由实际核查确认。

维护时依次运行 build_rules.py、build_output.py、build_prompt.py 和 validate.py .。三个生成器的 --check 用于核对同源一致。[测试记录](tests/TEST_REPORT.md)区分本次程序验证与历史模型行为，[适配说明](COMPATIBILITY.md)记录支持范围。
