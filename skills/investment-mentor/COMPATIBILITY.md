# 四环境与本版适配

本版使用标准SKILL.md、name/description、UTF-8、ASCII文件名和相对引用。关键规则中英双语，执行不要求指定模型、MCP、代码执行器或多Agent。

| 环境 | 本版实际范围 | 限制 |
|---|---|---|
| Codex | 一次J05文件输入子Agent行为测试；主Agent另做包/算术/定向内容复核 | 未测原生自动发现，精确后端与Token未知 |
| DSH | CLI0.2.1-rc.2，候选三组 | 配置deepseek-flash为别名，无工具全文输入 |
| Kimi | CLI2.3.0，候选三组 | moonshot-cn/kimi-k3为配置别名，无工具ACP文本 |
| 用户指定WorkBuddy通道 | 当前全局CodeBuddy Code CLI2.177.0，配对计划及额外尝试见测试报告 | 返回Hy4 preview别名；不等同WorkBuddy桌面内置CLI或原生技能加载 |

具体完成、超时、未运行和内容缺陷见[测试记录](tests/TEST_REPORT.md)。不同输入模式和采样设置不作模型排名；纯文本测试不证明description发现效果，也不证明默认联网。历史0.4.4成绩不继承为本版通过。不承诺所有模型表现相同或英文必然更快。
