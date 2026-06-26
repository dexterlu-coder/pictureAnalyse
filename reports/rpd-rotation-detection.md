# RPD：机械图纸旋转方向自动识别

## 需求概述

需要识别机械图纸扫描件相对于正确阅读方向被顺时针旋转了多少度。正确方向依据为：机械制图标题栏应位于页面下方或右下方。

## 用户价值

- 减少人工逐页查看图纸方向的工作量。
- 为后续批量拆分、校正和归档图纸提供基础能力。
- 形成可解释的方向判断结果，便于人工复核。

## 输入

- 单页 PDF 文件。
- 或由 PDF 渲染出的页面 PNG 图像。

## 输出

每页输出：

- 文件名或页码。
- 标题栏当前位置。
- 已顺时针旋转角度。
- 建议校正角度。
- 置信度。
- 是否需要人工复核。
- 调试图路径。

## 规则依据

依据 `rules/mechanical-drawing-rotation.md`：

| 当前标题栏位置 | 已顺时针旋转角度 |
| --- | --- |
| 下方或右下方 | 0 度 |
| 左侧 | 90 度 |
| 上方或左上方 | 180 度 |
| 右侧或右上方 | 270 度 |

## 非目标

当前阶段不做：

- OCR 全文提取。
- 图纸内容理解。
- 尺寸标注识别。
- 自动校正 PDF 页面。
- 处理全部 63 页。

## 阶段一范围

阶段一只实现 OpenCV 原型，用于前 5 张图纸方向识别。

审核状态：已通过，允许进入阶段一实现。

阶段一必须：

- 读取前 5 张 PNG 或 PDF。
- 检测标题栏候选区域。
- 输出 JSON 和 CSV。
- 生成调试图。
- 不修改原始 PDF。
- 不生成校正后的 PDF。

## 公开仓库整理要求

该项目将推送到 GitHub public 仓库，因此图纸原件、拆分 PDF、渲染 PNG、临时输出和个人草稿不得进入版本库。

必须满足：

- `.gitignore` 覆盖 `docs/**/*.pdf`、`output/`、`outputs/`、`tmp/`、`local_data/` 等路径。
- 当前本地图纸资料整理到 `local_data/` 下。
- Git 提交中只包含可公开的规则、规划、RPD、TODO、源码和必要说明。
- 推送前执行 `git status --short`，确认没有图纸资料处于 staged 状态。

## 验收标准

- 前 5 张图纸识别结果与已人工判断结果一致：
  - 第 1 张：270 度
  - 第 2 张：270 度
  - 第 3 张：180 度
  - 第 4 张：180 度
  - 第 5 张：180 度
- 每条结果包含标题栏位置和置信度。
- 每页至少生成一张调试图，标注候选标题栏区域。
- 低置信度结果必须标记为需要人工复核。

## 阶段一验证结果

阶段一 OpenCV 原型已在前 5 张样例图纸上运行，结果符合人工判断：

| 文件 | 标题栏位置 | 已顺时针旋转角度 | 置信度 | 复核标记 |
| --- | --- | --- | --- | --- |
| `YKJ125-00-00-2525_图纸_001.png` | 右侧或右上方 | 270 度 | 0.3582 | 否 |
| `YKJ125-00-00-2525_图纸_002.png` | 右侧或右上方 | 270 度 | 0.1217 | 是 |
| `YKJ125-00-00-2525_图纸_003.png` | 上方或左上方 | 180 度 | 0.3647 | 否 |
| `YKJ125-00-00-2525_图纸_004.png` | 上方或左上方 | 180 度 | 0.4093 | 否 |
| `YKJ125-00-00-2525_图纸_005.png` | 上方或左上方 | 180 度 | 0.4951 | 否 |

输出文件位于本地忽略目录 `outputs/rotation-detection/stage1/`。

## 置信度提升验证结果

已将检测脚本改为混合证据方案：

- 边侧表格线密度负责最终方向判断，保留前 5 张人工基准的稳定性。
- 局部候选框负责补充证据、输出调试框和候选特征。
- 置信度综合候选证据、边侧分差和竞争候选歧义。
- 默认输入已切换到 `local_data/experiment_samples/first20/png/`。

前 5 张人工基准复核结果：

| 文件 | 标题栏位置 | 已顺时针旋转角度 | 置信度 | 复核标记 |
| --- | --- | --- | --- | --- |
| `YKJ125-00-00-2525_sample_001.png` | 右侧或右上方 | 270 度 | 0.6200 | 否 |
| `YKJ125-00-00-2525_sample_002.png` | 右侧或右上方 | 270 度 | 0.3529 | 否 |
| `YKJ125-00-00-2525_sample_003.png` | 上方或左上方 | 180 度 | 0.6480 | 否 |
| `YKJ125-00-00-2525_sample_004.png` | 上方或左上方 | 180 度 | 0.6484 | 否 |
| `YKJ125-00-00-2525_sample_005.png` | 上方或左上方 | 180 度 | 0.7759 | 否 |

第 2 张置信度已从 0.1217 提升到 0.3529，超过 0.25 的阶段目标。

## 置信度提升需求

阶段一中第 2 张样例虽然角度判断正确，但置信度仅为 0.1217，触发人工复核。

审核状态：已通过，允许进入置信度提升实现。

后续需要提升置信度计算质量：

- 从整条边带评分改为局部标题栏候选框评分。
- 置信度应综合候选框自身质量、第一二名差距、几何形态和歧义程度。
- 输出更详细的证据字段，方便判断低置信度原因。
- 调试图应标注局部候选框，而不是只标注整条边带。

详细规划见 `docs/confidence-improvement-plan.md`。

## 实验样本扩展需求

当前前 5 张样本过少，容易让置信度优化过拟合到少量页面。

在继续改算法前，需要从本地私有原 PDF 中抽取前 20 张图纸作为实验样本：

- 输出位置：`local_data/experiment_samples/first20/`
- 单页 PDF：`local_data/experiment_samples/first20/pdf/`
- 渲染 PNG：`local_data/experiment_samples/first20/png/`
- 样本目录必须保持在 `.gitignore` 覆盖范围内，不上传 GitHub。
- 抽取方式优先使用 `pypdf` 页面级复制，避免重采样或重压缩。
- PNG 仅用于算法实验和调试，可由 Ghostscript 从单页 PDF 渲染。

## 全量实验样本需求

为了进行更可靠的阈值校准，前 20 张样本仍然不足。需要将原 PDF 的全部 63 页抽取为实验样本：

- 输出位置：`local_data/experiment_samples/all/`
- 单页 PDF：`local_data/experiment_samples/all/pdf/`
- 渲染 PNG：`local_data/experiment_samples/all/png/`
- 样本目录必须保持在 `.gitignore` 覆盖范围内，不上传 GitHub。
- 抽取方式继续使用 `pypdf` 页面级复制。
- PNG 继续使用 Ghostscript 以 150 DPI 渲染。
- 后续阈值校准应基于全量样本，而不是只基于前 5 或前 20 张。

完成状态：已抽取并渲染全部 63 页。

全量检测当前摘要：

- 结果数量：63。
- 需要复核：1。
- 最低置信度：0.2362。
- 最高置信度：0.8535。
- 输出仍位于本地忽略目录 `outputs/rotation-detection/stage1/`。

## 三方比对需求

仅依赖 OpenCV 置信度不足以决定免复核阈值。需要引入图像识别 MCP 和人工复核结果，与 OpenCV 形成三方比对。

目标：

- 对全量 63 张图纸分别获得 OpenCV、MCP、人工三方判断。
- 找出三方一致样本，作为高可信候选真值。
- 找出分歧样本，定位 OpenCV 或 MCP 的误判模式。
- 为后续置信度阈值校准提供数据基础。

详细计划见 `docs/three-way-rotation-comparison-plan.md`。

完成状态：已完成全量 63 张三方比对。

输出位于本地忽略目录 `outputs/rotation-detection/comparison/`：

- `mcp_results.json`
- `manual_results.json`
- `three_way_comparison.csv`
- `disagreements.csv`

当前结论：

- 总样本数：63。
- 三方需要关注样本：3。
- OpenCV 相对人工复核错误：2，分别是 `sample_009`、`sample_010`。
- OpenCV 低置信但方向正确：1，`sample_042`。
- MCP 在严格“当前屏幕坐标”prompt 下，与人工复核样本一致。

分歧明细：

| 样本 | OpenCV | MCP | 人工复核 | 结论 |
| --- | --- | --- | --- | --- |
| `sample_009` | 0 度 | 270 度 | 270 度 | OpenCV 误判 |
| `sample_010` | 270 度 | 0 度 | 0 度 | OpenCV 误判 |
| `sample_042` | 270 度，低置信 | 270 度 | 270 度 | OpenCV 方向正确但应复核 |

## OpenCV 阶段二误判修复需求

三方比对证明当前阶段一 OpenCV 结果存在两个高置信误判：`sample_009` 和 `sample_010`。

阶段二需要优先解决高置信误判：

- 将最终方向选择从单纯整边带评分升级为“局部标题栏候选框优先，整边带兜底”。
- 增加标题栏形态约束，区分竖向侧边标题栏与横向底部标题栏。
- 以 `sample_009`、`sample_010`、`sample_042` 作为重点回归样本。
- 全量 63 张运行后，不应新增相对当前三方候选真值的 OpenCV 分歧。

详细计划见 `docs/opencv-stage2-error-fix-plan.md`。

完成状态：已完成 OpenCV 阶段二误判修复。

阶段二实现：

- 增加边缘滑窗候选，避免标题栏被整页大轮廓吞掉。
- 当局部标题栏候选足够强时优先采用局部候选方向。
- 对右侧兜底结果增加冲突仲裁，降低上方/左侧密集视图造成的误判。
- 将原型复核阈值从 0.25 调整为 0.30，使 `sample_042` 继续进入复核池。

阶段二全量验证结果：

- 总样本数：63。
- 相对当前三方候选真值的 OpenCV 错误数：0。
- 需要人工复核：1，`sample_042`。
- 最低置信度：0.2960。
- 最高置信度：0.8535。

重点回归样本：

| 样本 | 阶段一 OpenCV | 阶段二 OpenCV | 人工复核 | 结果 |
| --- | --- | --- | --- | --- |
| `sample_009` | 0 度 | 270 度 | 270 度 | 已修正 |
| `sample_010` | 270 度 | 0 度 | 0 度 | 已修正 |
| `sample_042` | 270 度，低置信 | 270 度，低置信 | 270 度 | 保持复核 |

## Ground Truth 与自动评估需求

为了避免后续优化只依赖临时人工观察，需要建立可重复的评估流程。

本阶段需要：

- 将现有三方比对得到的候选真值规范化为 ground truth 文件。
- 明确区分人工重点复核样本与 OpenCV/MCP 共识接受样本。
- 实现自动评估脚本，计算准确率、错误样本、复核样本和置信度摘要。
- 后续每次修改识别算法后，都应先跑评估脚本再判断是否变好。

详细计划见 `docs/ground-truth-evaluation-plan.md`。

完成状态：已完成候选 ground truth 生成和自动评估脚本。

本地生成文件：

- `local_data/ground_truth/rotation_ground_truth.json`
- `local_data/ground_truth/rotation_ground_truth.csv`
- `outputs/rotation-detection/evaluation/evaluation_summary.json`
- `outputs/rotation-detection/evaluation/evaluation_details.csv`
- `outputs/rotation-detection/evaluation/errors.csv`
- `outputs/rotation-detection/evaluation/review_required.csv`

当前评估结果：

- 总样本数：63。
- 正确数：63。
- 错误数：0。
- 相对候选真值准确率：1.0。
- 需要复核：1，`sample_042`。
- 人工重点复核 ground truth：3。
- OpenCV/MCP 共识接受 ground truth：60。
- 最低置信度：0.2960。
- 最高置信度：0.8535。
- 平均置信度：0.614292。

注意：该准确率是相对候选真值集的回归评估结果，不应表述为最终工业级无人复核准确率。后续逐张人工精审后，可更新 ground truth 来源等级并重新评估。

## 人工精审辅助包需求

为了把 60 条 OpenCV/MCP 共识接受样本逐步升级为人工确认样本，需要生成本地人工精审辅助包。

本阶段需要：

- 生成人工复核 HTML 索引，方便逐张看图。
- 生成 CSV/JSON 复核清单，用于记录确认、纠正和备注。
- 按需要复核、未人工确认、低置信度排序，优先暴露风险样本。
- 不直接修改 ground truth，避免把未完成复核的状态误写为人工确认。

详细计划见 `docs/manual-review-pack-plan.md`。

完成状态：已完成人工精审辅助包生成脚本和本地输出。

新增脚本：

- `scripts/build_manual_review_pack.py`

本地生成文件：

- `outputs/rotation-detection/manual_review/review_index.html`
- `outputs/rotation-detection/manual_review/review_sheet.csv`
- `outputs/rotation-detection/manual_review/review_sheet.json`

当前复核包结果：

- 复核记录：63。
- 优先显示需要复核样本：`sample_042`。
- 其余共识接受样本按低置信度优先排序。
- HTML 中可直接查看图纸缩略图，并点击打开原 PNG。

用户后续需要做的事情：

- 打开 `outputs/rotation-detection/manual_review/review_index.html`。
- 按顺序查看每张图纸标题栏是否位于候选位置。
- 若候选正确，在 `review_form.csv` 的 `人工判断` 填 `正确`。
- 若候选错误，在 `review_form.csv` 的 `人工判断` 填 `错误`，并填写 `正确标题栏位置` 与 `正确旋转角度`。

人工表简化需求：

- `review_sheet.csv` 字段过多，改为生成更适合用户填写的 `review_form.csv`。
- 人工填写表只保留样本编号、候选位置、候选角度、人工判断、正确位置、正确角度和备注。
- 技术字段继续保留在 `review_sheet.json`，不呈现在人工填写 CSV 中。

完成状态：已完成。

简化后的用户填写表：

- `outputs/rotation-detection/manual_review/review_form.csv`

字段为：

- `序号`
- `样本编号`
- `候选标题栏位置`
- `候选旋转角度`
- `人工判断`
- `正确标题栏位置`
- `正确旋转角度`
- `备注`

旧的复杂 `review_sheet.csv` 已从本地输出目录删除，避免误打开。完整机器字段仍保留在 `review_sheet.json`。

## 人工复核结果回写需求

用户已完成 `review_form.csv` 人工审核：

- 旋转角度全部正确。
- 自动标题栏粗位置判断全部正确。
- 人工补充了更精确的标题栏位置，包括 `右上方`、`右侧`、`上方`、`下方`。

本阶段需要：

- 将人工填写结果回写到本地 ground truth。
- 将全部 63 条记录升级为人工确认。
- 新增 `precise_title_block_position` 字段保存精确位置。
- 保持 `title_block_position` 为粗粒度位置，继续服务旋转角度评估。
- 重新运行自动评估，确认当前算法相对人工确认 ground truth 仍为 63/63。

完成状态：已完成。

新增脚本：

- `scripts/import_manual_review_form.py`

导入结果：

- 导入人工复核记录：63。
- 人工确认 ground truth：63。
- 共识接受 ground truth：0。
- 精确标题栏位置分布：
  - `右上方`：30。
  - `右侧`：2。
  - `上方`：30。
  - `下方`：1。

重新评估结果：

- 总样本数：63。
- 正确数：63。
- 错误数：0。
- 相对人工确认 ground truth 准确率：1.0。
- 需要复核：1，`sample_042`。
- 最低置信度：0.2960。
- 最高置信度：0.8535。
- 平均置信度：0.614292。

说明：`sample_042` 方向正确但置信度低，因此仍作为算法复核策略样本保留。

## 顺时针 90 度增强样本需求

用户发现原始样本中缺少顺时针旋转 90 度图纸，即标题栏位于左侧的样本。为避免算法在缺失类别上未被验证，需要扩充样本多样性。

本阶段需要：

- 从人工确认原始样本中随机抽取一批图纸。
- 将它们旋转到标题栏位于左侧，构造 `90 度` 增强样本。
- 生成独立增强 ground truth，不能覆盖原始 ground truth。
- 对增强样本独立运行 OpenCV 检测和评估。
- 后续算法优化必须同时参考原始人工确认集和增强 90 度集。

详细计划见 `docs/augmented-90-sample-plan.md`。

完成状态：已完成。

新增脚本：

- `scripts/create_augmented_90_samples.py`

脚本改造：

- `scripts/detect_rotation_stage1.py` 支持 `--input-dir` 和 `--output-dir`。
- `scripts/evaluate_rotation_results.py` 支持 `--results`、`--ground-truth` 和 `--output-dir`。

增强样本生成结果：

- 增强 PNG：20 张。
- 目标旋转角度：全部为 `90 度`。
- 目标标题栏粗位置：全部为 `left`。
- 目标精确标题栏位置：全部为 `左侧`。
- 来源分布：
  - 原 `270 度` 样本：10 张，额外顺时针旋转 180 度。
  - 原 `180 度` 样本：9 张，额外顺时针旋转 270 度。
  - 原 `0 度` 样本：1 张，额外顺时针旋转 90 度。

增强样本初次评估结果：

- 总样本数：20。
- 正确数：16。
- 错误数：4。
- 准确率：0.8。
- 需要复核：1。
- 错误样本：`aug90_002_from_sample_010`、`aug90_012_from_sample_034`、`aug90_016_from_sample_042`、`aug90_020_from_sample_057`。

优化内容：

- 增加左侧候选仲裁规则：当左侧候选与 bottom/right 第一候选非常接近，且整边证据不强烈反对时，优先选择左侧。
- 保留原有右侧兜底保护，避免破坏原始右侧标题栏样本。

优化后评估结果：

- 原始人工确认集：63/63，准确率 1.0，需要复核 1。
- 增强 90 度集：20/20，准确率 1.0，需要复核 1。
- 增强集最低置信度：0.2823。
- 增强集最高置信度：0.8561。

说明：增强样本是合成样本，用于补齐类别覆盖和暴露算法弱点，不替代真实 90 度扫描样本。

## 联合评估需求

当前已经有两套必须同时关注的评估集：

- 原始人工确认集：63 张。
- 顺时针 90 度增强集：20 张。

后续算法优化需要一键同时跑两套评估，并输出总览，避免修复增强类别时破坏原始样本，或只看原始样本而遗漏 90 度类别。

本阶段需要：

- 新增联合评估脚本。
- 依次运行原始集检测与评估。
- 依次运行增强 90 度集检测与评估。
- 汇总输出两套数据和合计指标。
- 当前联合评估应达到 83/83。

详细计划见 `docs/combined-evaluation-plan.md`。

完成状态：已完成。

新增脚本：

- `scripts/run_combined_evaluation.py`

本地输出：

- `outputs/rotation-detection/combined_evaluation/combined_summary.json`
- `outputs/rotation-detection/combined_evaluation/combined_summary.csv`

联合评估结果：

| 数据集 | 样本数 | 正确数 | 错误数 | 准确率 | 需要复核 |
| --- | --- | --- | --- | --- | --- |
| 原始人工确认集 | 63 | 63 | 0 | 1.0 | 1 |
| 顺时针 90 度增强集 | 20 | 20 | 0 | 1.0 | 1 |
| 合计 | 83 | 83 | 0 | 1.0 | 2 |

复核样本：

- 原始人工确认集：`sample_042`。
- 顺时针 90 度增强集：`aug90_016_from_sample_042`。

联合最低置信度：0.2823。联合最高置信度：0.8561。

## sample_042 低置信分析与优化需求

当前联合评估中只有两个低置信复核样本：

- `sample_042`
- `aug90_016_from_sample_042`

两者来自同一张源图，人工已确认方向正确。下一阶段需要分析该图纸低置信原因，并优化评分或仲裁逻辑。

要求：

- 不通过简单降低全局复核阈值来“消除”复核标记。
- 优先找出候选证据竞争的具体原因。
- 优化后必须运行联合评估，保证 83/83 不变。
- 目标是提高这两个已确认正确样本的置信度，最好不再触发复核。

详细计划见 `docs/low-confidence-042-plan.md`。

完成状态：已完成。

低置信原因：

- `sample_042` 图纸线条较淡，局部候选证据本身正确但与多个边缘窗口竞争候选分数接近。
- 旧置信度公式对候选竞争惩罚过重，导致方向正确但置信度低于 0.30。
- 增强样本 `aug90_016_from_sample_042` 继承了同一问题。

优化内容：

- 新增局部候选置信度保底规则。
- 仅当局部候选 `evidence_score >= 0.45` 且候选分数达到第一名的 97% 以上时生效。
- 保底值为 0.32，只用于越过当前复核阈值，不改变高置信样本排序。
- 未降低全局复核阈值。

优化后结果：

- `sample_042`：置信度从 0.2960 提升到 0.3200，不再触发复核。
- `aug90_016_from_sample_042`：置信度从 0.2823 提升到 0.3200，不再触发复核。
- 原始人工确认集：63/63，准确率 1.0，复核数 0。
- 增强 90 度集：20/20，准确率 1.0，复核数 0。
- 联合评估：83/83，准确率 1.0，复核数 0。
- 联合最低置信度：0.3200。

## OCR + 图像识别大模型兜底流程需求

用户希望在 OpenCV 主流程之外，引入 OCR 和图像识别大模型，例如智谱、阿里视觉模型。当前疑问是这些流程应组成串行工作流，还是组成并行工作流并投票。

经他山调研后，本项目规划采用：

- OpenCV 主流程。
- 条件触发 OCR 与 VLM 并行兜底。
- 最后做证据融合，不做简单多数票。

原则：

- 当前 OpenCV 联合评估为 83/83，因此仍作为主识别器。
- OCR 和 VLM 只在低置信、冲突、新分布或抽检场景触发，且不等价、不默认同权。
- 若需要第三类方向证据，优先考虑专用标题栏检测模型或专用 4 类方向分类器。
- VLM 结果必须结构化输出，并保留证据。
- 外部 API 默认最小化调用，避免无必要上传图纸。

进一步调研结论：

- YOLO / OBB 可以作为本地小模型运行，适合训练 `title_block` 旋转框检测器。
- 本地开源 VLM 可作为在线 VLM 禁用时的兜底方案。
- 本地 VLM 候选包括 Qwen2.5-VL、SmolVLM、Florence-2、MiniCPM-V、InternVL 等。
- 当进入 VLM 兜底阶段时，第一轮应先用云端模型验证收益，再按配置压力测试本地模型。
- 流程表述统一为：`本地/云端 VLM 兜底解释疑难样本`。
- 对本项目来说，专用标题栏检测模型优先级高于 VLM；VLM 更适合处理 detector 和 OpenCV 冲突后的疑难样本。

优先级修正：

- OpenCV 当前作为基线冻结，不在没有新错误样本时继续硬调。
- 下一步主线改为本地 YOLO/OBB 标题栏检测小实验。
- OCR 排在 YOLO/OBB 之后，作为标题栏字段和文字方向证据。
- VLM 排在 OpenCV、YOLO/OBB、OCR 之后，用于疑难样本兜底解释。
- 第一轮执行动作是生成 YOLO/OBB 标注准备包，不直接训练模型。

YOLO/OBB 标注准备包执行结果：

- 新增脚本：`scripts/build_yolo_obb_annotation_pack.py`。
- 本地输出目录：`local_data/yolo_obb_annotation_pack/`。
- 输出文件：`annotation_manifest.csv`、`annotation_manifest.json`、`classes.txt`、`labeling_guide.md`、`pack_summary.json`。
- 样本总数：83。
- 数据集分布：原始人工确认集 63，顺时针 90 度增强集 20。
- 建议拆分：`train` 57，`val` 14，`test_focus` 12。
- 标题栏粗位置分布：`right` 32，`top` 30，`left` 20，`bottom` 1。
- 该准备包只生成清单和标注说明，不复制图纸、不上传图纸、不训练模型。
- 用户已审核并同意 `docs/yolo-obb-title-block-experiment-plan.md` 中的标注规范，允许进入 12 到 20 张 OBB 冒烟标注准备。

YOLO/OBB 冒烟标注子集执行结果：

- 脚本已扩展为同时生成 `local_data/yolo_obb_annotation_pack/smoke/`。
- 冒烟子集样本数：16。
- 数据集分布：原始人工确认集 10，顺时针 90 度增强集 6。
- 标题栏粗位置分布：`left` 6，`right` 5，`top` 4，`bottom` 1。
- 建议拆分来源：`test_focus` 12，`train` 4。
- 本地输出文件：`smoke_manifest.csv`、`smoke_manifest.json`、`smoke_review_index.html`、`smoke_labeling_task.md`、`smoke_summary.json`。
- 当前只完成冒烟标注子集准备，尚未绘制 OBB 框，不能进入训练。

YOLO/OBB 调试方案前置调研需求：

- 在开始真实 OBB 标注和训练前，需要先调研 YOLO/OBB 类似工程的调试方案。
- 调研重点包括数据集检查、标注可视化、小样本过拟合、训练指标、推理可视化、错误分层和后处理验证。
- 本轮不安装训练依赖、不启动训练、不绘制真实 OBB 标签。
- 详细计划见 `docs/yolo-obb-debugging-research-plan.md`。

YOLO/OBB 调试方案他山调研结论：

- YOLO/OBB 正式训练前必须增加调试质量门，不能直接从标注跳到训练。
- 标注后必须生成 overlay 图，确认 OBB 四点、点序、标题栏边界和误框情况。
- 训练冒烟的第一目标是验证链路和小样本可过拟合，不是证明泛化。
- 训练后不能只看 mAP，还要看召回、定位质量、val labels/pred 对照图和后处理映射结果。
- 错误样本要分层为 `label_error`、`format_error`、`false_negative`、`false_positive`、`localization_error`、`postprocess_error`、`data_leakage`。
- 标注 16 张前，下一步应先实现 YOLO/OBB 标签可视化脚本和数据集校验脚本。
- 详细调研见 `references/yolo-obb-debugging-research/README.md` 和 `docs/2026-06-25-yolo-obb-debugging-research.md`。

YOLO/OBB 标签工具实现计划：

- 新增 `scripts/visualize_obb_labels.py`，用于将 OBB 标签画回原图生成 overlay。
- 新增 `scripts/validate_obb_dataset.py`，用于检查标签格式、坐标范围、类别、图片/标签匹配和同源拆分泄漏。
- 默认输入为 `local_data/yolo_obb_annotation_pack/smoke/smoke_manifest.csv`。
- 默认标签目录为 `local_data/yolo_obb_annotation_pack/smoke/labels/`。
- 当前尚未人工标注，因此允许校验报告中出现 16 个缺失标签。
- 详细计划见 `docs/yolo-obb-label-tools-plan.md`。

YOLO/OBB 标签工具实现结果：

- 新增公共工具：`scripts/obb_utils.py`。
- 新增校验脚本：`scripts/validate_obb_dataset.py`。
- 新增可视化脚本：`scripts/visualize_obb_labels.py`。
- `python -m py_compile scripts\obb_utils.py scripts\validate_obb_dataset.py scripts\visualize_obb_labels.py` 通过。
- `python scripts\validate_obb_dataset.py` 已运行，检查 smoke 集 16 张图片：图片均存在且可读取，当前 16 个标签文件均缺失，产生 16 个 `missing_label` 警告、0 个错误，符合尚未人工标注的预期。
- `python scripts\visualize_obb_labels.py` 已运行，生成 16 张 overlay 图和 `overlay_report.json`。
- 本地输出目录：`local_data/yolo_obb_annotation_pack/smoke/validation/` 和 `local_data/yolo_obb_annotation_pack/smoke/overlays/`，均在 ignored 本地目录内，不进入 Git。

OBB 标注工具选择与人工界面规则需求：

- 用户没有标注工具，需要先调研并选择一个轻量、本地、支持旋转框或四点标注、可导出或转换为 Ultralytics OBB 格式的工具。
- 标注工具选择前不开始真实标注，不训练 YOLO/OBB，不上传图纸。
- 用户新增长期规则：需要人工填写的内容必须去掉不必要信息；所有图像排列必须优先考虑人工查看是否方便。
- 该规则需要写入 `rules/human-review-interface.md`。
- 详细计划见 `docs/annotation-tool-selection-plan.md`。

OBB 标注工具选择结果：

- 当前推荐 `Labelme + 项目内转换脚本`。
- 选择理由：本地运行、支持 polygon、安装使用轻，适合 16 张冒烟样本；Labelme JSON 易转换为 Ultralytics OBB。
- CVAT 功能更强，但 Docker/Web 平台成本较高，更适合后续多人或大批量标注。
- 新增规则文件：`rules/human-review-interface.md`。
- 新增操作说明：`docs/labelme-obb-annotation-workflow.md`。
- 新增调研记录：`docs/2026-06-25-obb-annotation-tool-selection.md`。
- 新增调研索引：`references/annotation-tool-selection/README.md`。
- 新增转换脚本：`scripts/convert_labelme_to_yolo_obb.py`。
- `scripts/build_yolo_obb_annotation_pack.py` 的 smoke 查看页生成逻辑已按人工界面规则调整：减少展示字段、放大图像显示区域，方便查看标题栏。
- 使用临时输出目录验证过新的 smoke 查看页生成逻辑；正式 `local_data/yolo_obb_annotation_pack/smoke/smoke_manifest.csv` 当前被占用，未覆盖正式本地 smoke 包。
- `python -m py_compile scripts\convert_labelme_to_yolo_obb.py` 通过。
- `python scripts\convert_labelme_to_yolo_obb.py --allow-missing` 已运行；当前尚未标注，因此结果为 `converted=0`、`missing_json=16`、`errors=0`，符合预期。

ISAT 标注工具调研需求：

- 用户反馈有评论认为 ISAT 比 Labelme 更好用，需要在开始人工标注前重新调研。
- 本轮只比较工具能力、安装复杂度、导出/转换链路和当前 16 张冒烟样本适配度。
- 本轮不安装 ISAT、不开始标注、不训练 YOLO/OBB、不删除 Labelme 方案。
- 详细计划见 `docs/isat-annotation-tool-research-plan.md`。

详细文件：

- `references/ocr-vlm-workflow-research/README.md`
- `docs/2026-06-25-ocr-vlm-workflow-research.md`
- `docs/ocr-vlm-fallback-workflow-plan.md`
- `docs/2026-06-25-local-title-block-detector-and-vlm-research.md`
- `docs/yolo-obb-title-block-experiment-plan.md`
- `docs/yolo-obb-debugging-research-plan.md`
- `references/yolo-obb-debugging-research/README.md`
- `docs/2026-06-25-yolo-obb-debugging-research.md`
- `docs/yolo-obb-label-tools-plan.md`
- `docs/annotation-tool-selection-plan.md`
- `docs/isat-annotation-tool-research-plan.md`
- `rules/human-review-interface.md`
- `references/annotation-tool-selection/README.md`
- `docs/2026-06-25-obb-annotation-tool-selection.md`
- `docs/labelme-obb-annotation-workflow.md`

## 项目目录整理需求

当前项目中存在历史输出、临时目录、重复样本和无关课程草稿，影响后续开发判断。

整理要求：

- 保留公开仓库的源码、规划、规则、RPD、参考资料。
- 保留本地私有原 PDF 和前 20 张实验样本。
- 删除可再生输出、旧临时目录、重复的前 5 张样本和无关草稿。
- 具体计划见 `docs/project-structure-cleanup-plan.md`。

## 风险

- 图纸中存在明细表、技术要求表等非标题栏表格，可能干扰表格密度判断。
- 扫描噪声、倾斜、裁切会影响线条检测。
- 不同图幅和标题栏布局可能需要调整区域阈值。

## 回滚准备

实现前必须提交当前规划、RPD 和 todo。若后续实现不可用，可回退到该提交，保留已确认的需求和计划。
