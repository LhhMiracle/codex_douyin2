import json

from src import cli


def test_cli_main(monkeypatch, tmp_path, capsys):
    def fake_run_pipeline(raw_text, output_dir):
        output_path = tmp_path / "123" / "processed"
        output_path.mkdir(parents=True, exist_ok=True)
        path = output_path / "img1.png"
        path.touch()
        return {
            "product_id": "123",
            "processed_images": [path],
        }

    monkeypatch.setattr(cli, "run_pipeline", fake_run_pipeline)

    exit_code = cli.main(
        ["--input", "test", "--output", str(tmp_path), "--select", "1"]
    )
    assert exit_code == 0

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert payload["product_id"] == "123"
    assert len(payload["processed_images"]) == 1
