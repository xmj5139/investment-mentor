# 环境与适配范围

0.4.6 使用标准 SKILL.md、name/description、UTF-8、ASCII 文件名和相对引用。共同规则支持中英文。宿主可直接加载技能，普通聊天可复制完整独立提示词或按任务生成的提示词。生成和程序检查为可选的本地维护工具，使用 Python 标准库。

以下记录属于 0.4.5 的历史行为测试。0.4.6 的新增行为用例待运行，实际程序检查见[本版测试记录](tests/TEST_REPORT.md)。

| 环境 | 0.4.5 实际范围 | 限制 |
|---|---|---|
| Codex | 一次J05文件输入子Agent行为测试；主Agent另做包/算术/定向内容复核 | 未测原生自动发现，精确后端与Token未知 |
| DSH | CLI0.2.1-rc.2，候选三组 | 配置deepseek-flash为别名，无工具全文输入 |
| Kimi | CLI2.3.0，候选三组 | moonshot-cn/kimi-k3为配置别名，无工具ACP文本 |
| 用户指定WorkBuddy通道 | 当前全局CodeBuddy Code CLI2.177.0，配对计划及额外尝试见测试报告 | 返回Hy4 preview别名；不等同WorkBuddy桌面内置CLI或原生技能加载 |

历史各环境的完成、超时和内容缺陷见[行为记录](tests/behavior-review.md)。纯文本测试仅覆盖当轮输入和能力条件。
