# pictureAnalyse

机械图纸扫描件处理实验项目。

当前重点是识别扫描版机械图纸的页面旋转方向。判断依据是：符合机械制图规范的图纸，其标题栏在正确方向下应位于页面下方或右下方。

## 当前内容

- `rules/mechanical-drawing-rotation.md`：机械图纸旋转角度判断规则。
- `docs/rotation-detection-plan.md`：旋转方向识别技术路线和阶段规划。
- `reports/rpd-rotation-detection.md`：需求与产品定义文档。
- `TODO.md`：当前任务清单。
- `AGENTS.md`：项目协作流程规则。

## 数据与隐私

图纸原件、拆分 PDF、渲染 PNG、临时输出和个人草稿不进入公开仓库。

本地私有资料统一放在 `local_data/`，并由 `.gitignore` 排除。

## 当前阶段

已完成：

- 前 5 张样例图纸的人工方向判断。
- 判断规则沉淀。
- OpenCV + OCR + 视觉 MCP 混合路线规划。
- public 仓库发布前的数据隔离整理。

下一步：

- 审核阶段一 OpenCV 原型计划。
- 实现仅识别前 5 张图纸方向的 OpenCV 原型。
