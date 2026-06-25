# OBB 标注工具选择调研索引

本目录记录本地 OBB 标注工具选择的外部参照。

## 样本索引

| 工具 | 类型 | 来源 | 优点 | 不适合当前点 |
| --- | --- | --- | --- | --- |
| Labelme | 本地桌面 GUI | https://github.com/wkentaro/labelme | Python/Qt 本地工具，支持 polygon/rectangle/circle/line/point，安装和使用轻，适合 16 张冒烟样本 | 不直接导出 Ultralytics OBB，需要项目内转换脚本 |
| CVAT Community | 自托管 Web 平台 | https://github.com/cvat-ai/cvat | 功能强，支持图像/视频/3D 标注、任务管理、导入导出多种格式、团队协作 | Docker 部署较重，不适合当前单人 16 张快速冒烟 |
| Label Studio | Web 标注平台 | https://labelstud.io/ | 可本地部署，适合多类型数据和项目管理 | 对当前 OBB 四点导出链路不如 Labelme 直接，配置复杂度较高 |

## 选择结论

当前推荐：`Labelme + 项目内转换脚本`。

原因：

1. 当前只需要标注 16 张图，工具越轻越好。
2. Labelme 支持 polygon，人工可以直接给标题栏画四点多边形。
3. Labelme 本地运行，不上传图纸。
4. Labelme JSON 简单，容易转换为 Ultralytics OBB 标签。
5. 后续若扩展到多人或大批量，再考虑 CVAT。

## 当前流程

```text
Labelme 画四点 polygon
  -> 保存 Labelme JSON
  -> scripts/convert_labelme_to_yolo_obb.py 转换为 YOLO OBB txt
  -> scripts/validate_obb_dataset.py 校验
  -> scripts/visualize_obb_labels.py 生成 overlay
  -> 人工看 overlay
```
