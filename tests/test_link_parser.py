from unittest import mock

import pytest

from src.link_parser import extract_product_id, LinkParserError


def test_extract_from_pc_url():
    url = "https://haohuo.jinritemai.com/views/product/item2?id=1234567890&source=pc"
    assert extract_product_id(url) == "1234567890"


def test_extract_from_app_share(monkeypatch):
    short_url = "https://v.douyin.com/xxxx/"
    resolved = "https://haohuo.jinritemai.com/views/product/item2?product_id=987654321"

    response = mock.Mock()
    response.is_redirect = True
    response.status_code = 302
    response.headers = {"Location": resolved}
    response.history = []

    monkeypatch.setattr("requests.get", lambda *args, **kwargs: response)

    share_text = f"复制打开抖音搜索，{short_url} 超值好物等你来！"
    assert extract_product_id(share_text) == "987654321"


def test_extract_from_backend_text():
    backend_text = '商品信息： {"product_id": "123123", "name": "测试商品"}'
    assert extract_product_id(backend_text) == "123123"


def test_extract_failure():
    with pytest.raises(LinkParserError):
        extract_product_id("无效的输入")
