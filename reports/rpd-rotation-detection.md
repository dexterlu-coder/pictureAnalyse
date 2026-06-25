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
