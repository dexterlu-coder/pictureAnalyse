# TODO

## 当前审核点

- [x] 用户审核阶段一详细计划。

## 阶段零：公开仓库整理

- [x] 新增 `.gitignore`，排除图纸原件、拆分页、渲染图和临时目录。
- [x] 将 `docs/*.pdf` 移入 `local_data/source_pdfs/`。
- [x] 将 `output/pdf/*.pdf` 移入 `local_data/split_pdfs/`。
- [x] 将 `tmp/pdfs/preview/*.png` 移入 `local_data/previews/preview/`。
- [x] 将 `tmp/pdfs/rotation_check/*.png` 移入 `local_data/previews/rotation_check/`。
- [x] 检查 `git status --short`，确认没有图纸资料待提交。
- [x] 用 GitHub CLI 创建 public 仓库并推送。

## 阶段一：OpenCV 原型

- [x] 确认输入来源：优先使用 `local_data/previews/rotation_check/*.png`。
- [x] 创建脚本目录和阶段一脚本。
- [x] 实现 PNG 读取和预处理。
- [x] 实现水平线、垂直线检测。
- [x] 实现表格候选区域合并。
- [x] 实现标题栏候选侧判断。
- [x] 实现旋转角度映射。
- [x] 输出 JSON 结果。
- [x] 输出 CSV 结果。
- [x] 输出调试图。
- [x] 用前 5 张图纸验证识别结果。
- [x] 对照 RPD 验收标准复核。

## 后续阶段

- [x] 查找类似工程图纸方向识别、标题栏检测和表格定位方案。
- [x] 沉淀取经样本索引和横向学习笔记。
- [ ] 从原 PDF 抽取前 20 张图纸作为实验样本。
- [ ] 为前 20 张实验样本渲染 PNG。
- [ ] 检查前 20 张实验样本不进入 Git 跟踪。
- [ ] 用户审核置信度提升规划。
- [ ] 将整边评分升级为局部标题栏候选框评分。
- [ ] 增加候选框几何特征评分。
- [ ] 增加多证据置信度字段。
- [ ] 增强调试图，标注候选标题栏框。
- [ ] 重新验证前 5 张结果，并重点提升第 2 张置信度。
- [ ] 评估是否加入 OCR。
- [ ] 设计低置信度视觉 MCP 兜底流程。
- [ ] 批量处理完整 PDF。
- [ ] 生成校正后的 PDF 输出方案。
