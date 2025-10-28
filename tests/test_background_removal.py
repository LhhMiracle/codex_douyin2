from src import background_removal


def test_process_batch(monkeypatch, tmp_path):
    def fake_remove(data):
        # return same data to simulate removal
        return data

    monkeypatch.setattr(background_removal, "remove", fake_remove)

    source = tmp_path / "source"
    source.mkdir()
    image_path = source / "img.png"
    image_path.write_bytes(b"dummy")

    output_dir = tmp_path / "output"
    processed = background_removal.process_batch([image_path], output_dir)
    assert len(processed) == 1
    assert processed[0].exists()
