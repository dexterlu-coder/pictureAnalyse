# Labelme 标注 YOLO/OBB 标题栏操作流程

## 一、你要做什么

你只需要给 16 张冒烟样本各画一个标题栏四点 polygon。

类别名固定为：

```text
title_block
```

## 二、推荐工具

推荐使用 Labelme。

安装方式二选一：

```powershell
pip install labelme
```

或者使用 Labelme 官方独立应用。

当前我不会替你安装，等你确认安装方式后再执行。

## 三、输入图片

图片路径在：

```text
local_data/yolo_obb_annotation_pack/smoke/smoke_manifest.csv
```

查看顺序入口：

```text
local_data/yolo_obb_annotation_pack/smoke/smoke_review_index.html
```

## 四、保存位置

Labelme JSON 请保存到：

```text
local_data/yolo_obb_annotation_pack/smoke/labelme_json/
```

每张图一个 JSON，文件名建议和样本名一致：

```text
sample_009.json
aug90_002_from_sample_010.json
```

## 五、标注规则

1. 每张图只标一个 `title_block`。
2. 使用 polygon 画四个角点。
3. 只框标题栏主体，不把整张明细表一起框入。
4. 点的顺序保持顺时针或逆时针都可以，转换脚本会按几何顺序整理。
5. 如果标题栏被裁切，按可见标题栏边界标注。

## 六、标注后我来做什么

你标完后告诉我。我会运行：

```powershell
python scripts\convert_labelme_to_yolo_obb.py
python scripts\validate_obb_dataset.py
python scripts\visualize_obb_labels.py
```

然后我会给你 overlay 图检查入口。
