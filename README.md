# pictureAnalyse

机械图纸扫描件处理实验项目。

目标是识别扫描版机械图纸的页面旋转方向，并逐步形成可复核、可解释、可回滚的标题栏检测工作流。判断依据是：符合机械制图规范的图纸，其标题栏在正确方向下应位于页面下方或右下方。

## 文档入口

- [项目协作规则](AGENTS.md)
- [TODO](TODO.md)
- [文档索引](docs/README.md)
- [参考资料索引](references/README.md)
- [规则索引](rules/README.md)
- [报告索引](reports/README.md)

## 当前重点

已完成 OpenCV 方向识别基线、全量人工确认 ground truth、顺时针 90 度增强样本、YOLO/OBB 标题栏标注、40 张 OBB overlay 人工复查，以及第二轮 YOLO/OBB 分组数据集构建。

当前下一步是决定是否安装 Ultralytics 并启动小样本 YOLO/OBB 标题栏 detector 训练。训练结果只用于链路验证和证据分支探索，不直接宣称工业级泛化能力。

## 数据与隐私

图纸原件、拆分 PDF、渲染 PNG、临时输出和个人草稿不进入公开仓库。

本地私有资料统一放在 `local_data/`，并由 `.gitignore` 排除。

当前本地私有目录约定：

- `local_data/source_pdfs/`：原始 PDF。
- `local_data/experiment_samples/all/pdf/`：全量单页 PDF 实验样本。
- `local_data/experiment_samples/all/png/`：全量 PNG 实验样本。
- `local_data/experiment_samples/first20/pdf/`：前 20 张单页 PDF 实验样本。
- `local_data/experiment_samples/first20/png/`：前 20 张 PNG 实验样本。
- `local_data/review_inbox/current/`：固定人工审核入口。
- `local_data/yolo_obb_dataset_round2/`：第二轮人工确认 YOLO/OBB 本地训练数据集。

## 阶段一运行方式

安装依赖：

```powershell
python -m pip install -r requirements.txt
```

运行全量实验样本识别：

```powershell
python .\scripts\detect_rotation_stage1.py
```

输出会写入本地忽略目录：

- `outputs/rotation-detection/stage1/results.json`
- `outputs/rotation-detection/stage1/results.csv`
- `outputs/rotation-detection/stage1/debug/*.png`
