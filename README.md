# photo_sort

基于 `yolo26n`（Ultralytics YOLO）按图片内容标签自动整理相册。

## 功能

- 递归扫描源目录中的常见图片格式（jpg/png/webp/bmp/heic）。
- 使用 YOLO 检测图片目标并按首个标签分类。
- 对 `scenery` 类别图片，按 EXIF 自动细分到 `scenery/相机型号/镜头型号/`。
- 支持复制模式（默认）和移动模式。
- 未检测到目标时进入 `unknown` 文件夹（可自定义）。
- 首次运行会自动下载 `yolo26n.pt` 到项目根目录，后续复用。
- 支持图形化界面（默认）和命令行交互（`--cli`）。

## 快速开始

```bash
cd /Users/hualaiwu/Documents/photo_sort
pip install -r requirements.txt
pip install -e .
```

## 运行

推荐直接运行独立入口（默认启动图形界面）：

```bash
python main.py
```

如果你希望在终端输入路径并运行：

```bash
python main.py --cli
```

如果网络环境无法自动下载模型，请手动把 `yolo26n.pt` 放到项目根目录：

```bash
cp /your/model/path/yolo26n.pt /Users/hualaiwu/Documents/photo_sort/yolo26n.pt
```

或使用安装后的命令：

```bash
photo-sort /path/to/source_album /path/to/output_album --model yolo26n.pt --conf 0.35
```

使用移动模式：

```bash
photo-sort /path/to/source_album /path/to/output_album --model yolo26n.pt --move
```

## 开发测试

```bash
pytest -q
```
