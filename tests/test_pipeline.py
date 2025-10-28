from src import pipeline


class DummyClient:
    def __init__(self, *_, **__):
        pass

    def fetch_product_detail(self, product_id: str):
        return {
            "product_id": product_id,
            "title": "测试",
            "images": ["https://example.com/a.png", "https://example.com/b.png"],
        }


def test_run_pipeline(monkeypatch, tmp_path):
    monkeypatch.setattr(pipeline, "extract_product_id", lambda text: "555")
    monkeypatch.setattr(pipeline, "DouyinClient", DummyClient)

    def fake_download(images, dest_dir):
        dest_dir.mkdir(parents=True, exist_ok=True)
        path = dest_dir / "img1.png"
        path.touch()
        return [path]

    def fake_process(paths, out_dir):
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / "img1_transparent.png"
        path.touch()
        return [path]

    monkeypatch.setattr(pipeline, "download_images", fake_download)
    monkeypatch.setattr(pipeline, "process_batch", fake_process)

    result = pipeline.run_pipeline("dummy", tmp_path)
    assert result["product_id"] == "555"
    assert result["download_dir"].exists()
    assert result["processed_dir"].exists()
    assert len(result["processed_images"]) == 1
