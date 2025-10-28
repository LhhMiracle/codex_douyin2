# codex_douyin2

AI 编程-商品详情页抠图+高清处理

## 安装依赖

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 使用 CLI

```bash
python -m src.cli --input "分享文案或链接" --output output_dir
```

可选参数 `--select` 用于指定希望查看的图片序号（1 开始）。

执行过程中会在 `logs/pipeline.log` 写入操作日志，便于排查问题。

示例输入（App 分享文案）：

```
复制整段话打开抖音，超值好物等你来！https://v.douyin.com/xxxxxxx/
```

示例输出（终端打印）：

```
{
  "product_id": "1234567890",
  "processed_images": [
    "output_dir/1234567890/processed/image_01_transparent.png"
  ]
}
```

## FastAPI 服务（可选）

当前仓库提供完整的 Python 模块，可基于 `src.pipeline.run_pipeline` 自行封装为 Web 服务。

## 测试

```bash
pytest
```
