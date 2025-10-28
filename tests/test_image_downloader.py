from src import image_downloader


def test_download_images(tmp_path, monkeypatch):
    calls = []

    def fake_download(session, url, dest, timeout):
        calls.append(url)
        dest.write_bytes(b"data")

    monkeypatch.setattr(image_downloader, "_download_single", fake_download)
    monkeypatch.setattr(image_downloader, "_validate_resolution", lambda path: True)

    result = image_downloader.download_images(
        ["https://example.com/image.png"], tmp_path
    )
    assert len(result) == 1
    assert calls == ["https://example.com/image.png"]


def test_download_images_low_resolution(tmp_path, monkeypatch):
    calls = []

    def fake_download(session, url, dest, timeout):
        calls.append(url)
        dest.write_bytes(b"data")

    state = {"count": 0}

    def fake_validate(path):
        state["count"] += 1
        return state["count"] > 1

    monkeypatch.setattr(image_downloader, "_download_single", fake_download)
    monkeypatch.setattr(image_downloader, "_validate_resolution", fake_validate)

    result = image_downloader.download_images(["https://example.com/low.png"], tmp_path)
    assert len(result) == 1
    assert calls == [
        "https://example.com/low.png",
        "https://example.com/low.png?ratio=1",
    ]
