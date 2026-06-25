# OCR + VLM 工作流取经样本索引

本目录记录 OCR、OpenCV、视觉大模型和人工复核混合工作流的外部参照。

## 样本索引

| 样本 | 类型 | 来源 | 一句话价值 | 不适合照搬 |
| --- | --- | --- | --- | --- |
| Multi-Stage Field Extraction of Financial Documents with OCR and Compact VLMs | 论文 | https://arxiv.org/abs/2510.23066 | 支持“预处理/OCR/检索/小范围 VLM”的多阶段管线，强调成本、延迟、可解释性 | 目标是字段抽取，不是机械图纸方向识别 |
| DISCO: Document Intelligence Suite for Comparative Evaluation | 论文 | https://arxiv.org/abs/2603.23511 | 强调 OCR 与 VLM 应按文档类型和任务复杂度选择，而不是单一替代 | 它是评测框架，不直接给生产路由策略 |
| HYCEDIS: Hybrid Confidence Engine | 论文 | https://arxiv.org/abs/2206.02628 | 说明文档智能系统需要独立置信度层，不能只相信模型自带分数 | 方法较重，不适合作为当前阶段实现 |
| Can VLMs Replace OCR-Based VQA Pipelines in Production? | 论文 | https://arxiv.org/abs/2408.15626 | 说明 VLM 在生产场景中任务差异很大，不宜直接替代传统多步骤管线 | 零售 VQA 场景与机械图纸不同 |
| Qwen-VL | 模型论文 | https://arxiv.org/abs/2308.12966 | 视觉定位和图中文字理解能力适合作为疑难样本兜底 | 不能保证稳定输出结构化方向标签 |
| CogVLM2 / GLM-4V | 模型论文 | https://arxiv.org/abs/2408.16500 | 智谱系 VLM 有图像理解和文本视觉能力，可作为供应商候选 | 模型能力不等于流程设计，仍需本地验证 |
| AI-assisted decision making confidence/explanation | 人机协作论文 | https://arxiv.org/abs/2001.02114 | 说明置信度有助于校准人对 AI 的信任，但解释和置信度不能自动保证更好决策 | 人类实验结论不能直接等同于图纸处理准确率 |
| Document orientation detection for OCR | 论文 | https://arxiv.org/abs/2511.04161 | 说明可以训练专用 4 类方向分类器，作为独立方向证据 | 通用文档方向不等同于机械标题栏方向 |
| Engineering drawing hybrid VLM framework | 论文 | https://arxiv.org/abs/2510.21862 | 使用 YOLO 检测 layout/title block，再用 VLM 做语义解析，支持“专用检测 + VLM”分工 | 需要标注数据和训练成本 |
| Engineering drawing parsing with OBB + Donut | 论文 | https://arxiv.org/abs/2505.01530 | 用 oriented bounding box 检测标题栏等区域，说明专用 detector 是可行第三路 | 目标是信息抽取，不只是方向识别 |

## 当前结论

外部样本支持我们的方向：不要把 OpenCV、OCR、VLM 做成无条件全量并行投票；更稳妥的是 OpenCV 主流程、置信度/冲突门控、疑难样本触发 OCR、专用标题栏/方向模型、VLM 条件并行，再做证据融合和人工复核。

重要修正：OCR 和 VLM 不等价。OCR 是文字证据，VLM 是视觉语义证据；若需要第三类“方向识别”证据，应优先考虑专用标题栏检测器或专用方向分类器。
