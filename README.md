# AI 漫剧生产 Skill

一个经过真实 Lovart 生产验证的 AI 漫剧工作流：从剧本、资产圣经和静态关键帧，到付费任务账本、I2V 时序 QA 与最终交付。

核心原则：

- Hermes 管理事实、状态、审批、成本、QA 和交付；Lovart 只负责媒体生成。
- 生成成功不等于可用；每份媒体都必须下载、校验并验收。
- 用户批准不覆盖真实缺陷，豁免必须保留原始 QA。
- 已提交任务先 collect，禁止因等待而重复扣费。
- I2V 一次只做一个主要因果动作；复杂动作拆镜头。

## 仓库内容

- `skills/media/ai-comic-drama-pipeline/SKILL.md`：可复用 Hermes Skill。
- `comic_pipeline/`：合约、任务状态机、Prompt IR 和 Pilot 检查器。
- `schemas/`：生产数据 JSON Schema。
- `tests/`：状态机与合约测试。
- `docs/`：权威模型、付费审批和 Lovart-only 架构决策。
- `productions/throne-ledger-reversal/`：真实制作案例《我在朝堂直播抄家》的结构化生产记录。

## 快速验证

```bash
python3 -m pytest -q
```

该命令不会提交任何付费生成任务。

## 安装 Skill

将目录复制到 Hermes Skills 目录：

```text
skills/media/ai-comic-drama-pipeline/
```

运行时还需要配合负责 Windows Chrome、WSL 与 Lovart CDP 操作的 `lovart-windows-chrome` Skill。

## 当前成熟度

- 静态资产与关键帧生产链路：已在真实 Lovart 项目中验证。
- 任务状态、预览哈希、collect-before-retry、QA 与 manifest：已验证。
- I2V：已验证技术采集和严格时序 QA；复杂多阶段动作仍需拆镜头或使用确定性后期。
- 最终 80 秒成片交付：仍在进行中。

## 安全与成本

- 不包含 Cookie、密码、Token 或 API Key。
- 不自动购买积分或升级套餐。
- 所有价格以提交前 Lovart 实时显示为准。
- 失败和被拒素材保留为审计证据，不能静默进入正式交付。
