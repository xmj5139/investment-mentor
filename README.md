# Investment Mentor

面向中国机构一级市场股权投资的 Agent Skill，当前版本 **0.4.5 候选版**。用于未上市企业初筛、BP分析、尽调、财务测算、估值条款、投委会、投后退出，以及按行业和实际活动开展的ESG判断。

Private-company investment research with traceable evidence, conditional financial analysis, industry-specific ESG review, and Chinese-first reports. Key execution rules include concise English equivalents.

## 使用

- 支持技能文件的Agent：将整个 [`skills/investment-mentor`](skills/investment-mentor) 文件夹放入宿主支持的技能目录，按宿主规则发现或显式调用。
- 普通聊天：使用完整的[独立提示词](skills/investment-mentor/STANDALONE_PROMPT.md)，再提供任务和可读材料。它不依赖外部引用文件。
- 示例任务：`请用 investment-mentor 分析这份匿名BP的跟进价值，采用详细版。先读材料，默认核验会改变判断的公开命题；缺参数时提出具体问题，暂停依赖判断。`

不绑定指定模型、MCP、代码执行器或多Agent。核心按可用能力运行；没有联网或无法读取附件时必须如实说明。Python脚本是可选的算术、维护与机械格式辅助。

## 方法与输出

保留CD（价值识别）、DP（问题驱动的五层验证）、CI（条件触发的重新定价分析），以及9个投资人视角和12个认知维度。区分事实、企业主张、线索、预测、推断和未知。

完整报告保留“报告信息—投资判断简报—结构化项目画像—专家附录”。简版正文5节；详细及全面版15节，第9节ESG含6子节。短问直接答，明确专项按相应结构输出，不强制生成长报告。

ESG优先覆盖半导体与电子、装备与新材料、能源与环保、软件与AI、医疗健康；其他行业采用通用框架并识别实际活动。规则与市场参数须在使用时核验时点。

## 当前状态

这是可继续测试的候选版，**没有四通道全部通过的结论**。目录检查通过不能证明模型行为、事实或投资判断正确。双语也没有被证实能提升准确率或效率。

- [近期版本更新](CHANGELOG.md)
- [测试范围与已知问题](docs/TESTING.md)
- [待实施改进](docs/ROADMAP.md)
- [发布内容与隐私边界](docs/PACKAGING.md)
- [通用技能内的历史测试](skills/investment-mentor/tests/TEST_REPORT.md)

本次公开整理没有实施新的投资判断规则，不冒充0.4.6。真实项目PDF、财务数据、原始分析、私有测试输入/运行器、机器路径和凭据均不在本仓库。未新增许可证文件。

目录与元数据按[Agent Skills规范](https://agentskills.io/specification)组织；不据此承诺各宿主原生发现和所有模型表现相同。

## 本地复核

```shell
python -X utf8 -B skills/investment-mentor/scripts/validate.py skills/investment-mentor
python -X utf8 -B skills/investment-mentor/scripts/test_output.py
python -X utf8 -B scripts/check_publication.py
```

第一条执行包结构、生成一致性及计算器用例检查；第二条测试Markdown结构检查器；第三条检查仓库相对链接、文件白名单、常见私有路径/凭据形态和校验清单。均不启动模型服务，不代替事实审阅。
