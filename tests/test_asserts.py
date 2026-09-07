import json

import pytest
from requests import Response

from utils.asserts import assert_case


def create_response(status_code, json_data):
    response = Response()
    response.status_code = status_code
    response._content = json.dumps(
        json_data,
        ensure_ascii=False,
    ).encode("utf-8")
    response.encoding = "utf-8"
    return response


def test_multiple_assertions_pass():
    response = create_response(
        200,
        {
            "msg": "登录成功",
            "token": "test-token",
        },
    )

    case = {
        "id": "unit_001",
        "assertions": [
            {
                "type": "status_code",
                "operator": "equals",
                "expected": 200,
            },
            {
                "type": "json",
                "path": "$..msg",
                "operator": "equals",
                "expected": "登录成功",
            },
            {
                "type": "text",
                "operator": "contains",
                "expected": "test-token",
            },
        ],
    }

    assert_case(case, response)


def test_status_code_assertion_fails():
    response = create_response(
        500,
        {"msg": "服务器错误"},
    )

    case = {
        "id": "unit_002",
        "assertions": [
            {
                "type": "status_code",
                "operator": "equals",
                "expected": 200,
            }
        ],
    }

    with pytest.raises(
        AssertionError,
        match="断言失败",
    ):
        assert_case(case, response)


def test_json_path_not_found():
    response = create_response(
        200,
        {"msg": "登录成功"},
    )

    case = {
        "id": "unit_003",
        "assertions": [
            {
                "type": "json",
                "path": "$..token",
                "operator": "equals",
                "expected": "test-token",
            }
        ],
    }

    with pytest.raises(
        AssertionError,
        match="JSONPath未匹配到数据",
    ):
        assert_case(case, response)