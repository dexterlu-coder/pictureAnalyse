# 人工精审辅助包计划

## 背景

当前 ground truth 中 63 条记录里，只有 3 条属于人工重点复核，另外 60 条来自 OpenCV 与 MCP 共识接受。若要提高后续算法评估可信度，需要把这 60 条逐步升级为真正的人工确认记录。

## 目标

生成一个本地人工精审辅助包，让用户可以逐张查看图纸、候选判断和算法证据，并记录确认或纠正结果。

## 输入

- 全量 PNG 样本：`local_data/experiment_samples/all/png/*.png`
- 候选 ground truth：`local_data/ground_truth/rotation_ground_truth.json`
- OpenCV 评估明细：`outputs/rotation-detection/evaluation/evaluation_details.csv`

## 输出

本地忽略目录：

- `outputs/rotation-detection/manual_review/review_index.html`
- `outputs/rotation-detection/manual_review/review_sheet.csv`
- `outputs/rotation-detection/manual_review/review_sheet.json`

公开仓库只提交生成脚本、计划、RPD 和 TODO，不提交图纸图片或人工复核输出。

## 复核清单字段

每张图纸至少包含：

- 样本编号。
- 图像路径。
- 当前候选标题栏位置。
- 当前候选旋转角度。
- OpenCV 预测标题栏位置。
- OpenCV 预测旋转角度。
- OpenCV 置信度。
- 是否需要复核。
- ground truth 来源等级。
- 人工确认状态，默认为空。
- 人工纠正位置，默认为空。
- 人工纠正角度，默认为空。
- 备注，默认为空。

## HTML 报告要求

- 按优先级排序：需要复核、非人工确认、低置信度优先。
- 每张图纸显示缩略图和当前候选判断。
- 明确标出 `manual_review` 与 `consensus_accepted`。
- 不直接修改 ground truth，只作为人工复核入口。

## 验收标准

- 生成 63 条复核记录。
- HTML 能在本地浏览器打开并看到图纸缩略图。
- CSV/JSON 能作为后续人工修订和回写 ground truth 的输入。
- 图纸和本地输出继续保持在 `.gitignore` 覆盖范围内。

## 执行结果

已完成：

- `scripts/build_manual_review_pack.py`
- `outputs/rotation-detection/manual_review/review_index.html`
- `outputs/rotation-detection/manual_review/review_sheet.csv`
- `outputs/rotation-detection/manual_review/review_sheet.json`

复核包包含 63 条记录。排序规则已生效：`sample_042` 作为需要复核样本排在第一位，其余样本按低置信度优先排列。
