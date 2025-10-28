from src.douyin_client import DouyinClient


class DummyResponse:
    def __init__(self, json_data):
        self._json = json_data

    def raise_for_status(self):
        return None

    def json(self):
        return self._json


class DummySession:
    def __init__(self, json_data):
        self.json_data = json_data
        self.headers = {}

    def get(self, url, params=None, timeout=None):
        self.last_request = {"url": url, "params": params, "timeout": timeout}
        return DummyResponse(self.json_data)


def test_fetch_product_detail():
    product_id = "123"
    payload = {
        "data": {
            "product_info": {
                "title": "测试商品",
                "detail_images": [
                    {"url": "https://example.com/img1"},
                    {"url": "//example.com/img2"},
                ],
            }
        }
    }

    session = DummySession(payload)
    client = DouyinClient(session=session)
    detail = client.fetch_product_detail(product_id)
    assert detail["product_id"] == product_id
    assert len(detail["images"]) == 2
    assert all("ratio=1" in img for img in detail["images"])
