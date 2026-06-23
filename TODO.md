# TODO

## 当前审核点

- [ ] 用户审核阶段一详细计划。

## 阶段零：公开仓库整理

- [x] 新增 `.gitignore`，排除图纸原件、拆分页、渲染图和临时目录。
- [x] 将 `docs/*.pdf` 移入 `local_data/source_pdfs/`。
- [x] 将 `output/pdf/*.pdf` 移入 `local_data/split_pdfs/`。
- [x] 将 `tmp/pdfs/preview/*.png` 移入 `local_data/previews/preview/`。
- [x] 将 `tmp/pdfs/rotation_check/*.png` 移入 `local_data/previews/rotation_check/`。
- [x] 检查 `git status --short`，确认没有图纸资料待提交。
- [ ] 用 GitHub CLI 创建 public 仓库并推送。

## 阶段一：OpenCV 原型

- [ ] 确认输入来源：优先使用 `local_data/previews/rotation_check/*.png`。
- [ ] 创建脚本目录和阶段一脚本。
- [ ] 实现 PNG 读取和预处理。
- [ ] 实现水平线、垂直线检测。
- [ ] 实现表格候选区域合并。
- [ ] 实现标题栏候选侧判断。
- [ ] 实现旋转角度映射。
- [ ] 输出 JSON 结果。
- [ ] 输出 CSV 结果。
- [ ] 输出调试图。
- [ ] 用前 5 张图纸验证识别结果。
- [ ] 对照 RPD 验收标准复核。

## 后续阶段

- [ ] 评估是否加入 OCR。
- [ ] 设计低置信度视觉 MCP 兜底流程。
- [ ] 批量处理完整 PDF。
- [ ] 生成校正后的 PDF 输出方案。
