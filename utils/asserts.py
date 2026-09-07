import logging

import allure
import jsonpath

from config.config import DB_ENABLED
from utils.send_request import send_jdbc_request


SUPPORTED_OPERATORS = {
    "equals",
    "not_equals",
    "contains",
    "not_contains",
}


def compare_values(actual, expected, operator):
    """根据操作符比较实际值与预期值。"""
    if operator == "equals":
        passed = actual == expected

    elif operator == "not_equals":
        passed = actual != expected

    elif operator == "contains":
        try:
            passed = expected in actual
        except TypeError:
            passed = False

    elif operator == "not_contains":
        try:
            passed = expected not in actual
        except TypeError:
            passed = False

    else:
        raise ValueError(
            f"不支持的断言操作符：{operator}，"
            f"当前支持：{sorted(SUPPORTED_OPERATORS)}"
        )

    if not passed:
        raise AssertionError(
            f"断言失败：actual={actual!r}，"
            f"operator={operator}，"
            f"expected={expected!r}"
        )


def get_json_value(response, assertion):
    """根据JSONPath从响应中提取待断言字段。"""
    json_path = assertion.get("path")

    if not json_path:
        raise ValueError("JSON断言缺少path字段")

    try:
        response_json = response.json()
    except ValueError as exc:
        raise AssertionError(
            f"响应不是合法JSON：{response.text}"
        ) from exc

    results = jsonpath.jsonpath(
        response_json,
        json_path,
    )

    if not results:
        raise AssertionError(
            f"JSONPath未匹配到数据：{json_path}"
        )

    result_index = assertion.get("index", 0)

    if result_index >= len(results):
        raise AssertionError(
            f"JSONPath结果不存在索引{result_index}，"
            f"实际结果：{results}"
        )

    return results[result_index]


def execute_assertion(assertion, response):
    """执行单条断言。"""
    assertion_type = assertion.get("type")
    operator = assertion.get("operator", "equals")
    expected = assertion.get("expected")

    if assertion_type == "status_code":
        actual = response.status_code

    elif assertion_type == "json":
        actual = get_json_value(
            response,
            assertion,
        )

    elif assertion_type == "text":
        actual = response.text

    elif assertion_type == "database":
        if not DB_ENABLED:
            logging.info(
                f"数据库未启用，跳过数据库断言："
                f"{assertion.get('sql')}"
            )
            return

        sql = assertion.get("sql")

        if not sql:
            raise ValueError(
                "数据库断言缺少sql字段"
            )

        actual = send_jdbc_request(
            sql,
            index=assertion.get("index", 0),
        )

    else:
        raise ValueError(
            f"不支持的断言类型：{assertion_type}"
        )

    compare_values(
        actual=actual,
        expected=expected,
        operator=operator,
    )

    logging.info(
        f"断言成功：type={assertion_type}，"
        f"actual={actual!r}，"
        f"operator={operator}，"
        f"expected={expected!r}"
    )


@allure.step("3.执行用例断言")
def assert_case(case, response):
    """执行当前用例配置的全部断言。"""
    assertions = case.get("assertions") or []

    if not assertions:
        raise ValueError(
            f"用例ID={case.get('id')}没有配置assertions"
        )

    for index, assertion in enumerate(
        assertions,
        start=1,
    ):
        assertion_type = assertion.get(
            "type",
            "unknown",
        )

        with allure.step(
            f"断言{index}：{assertion_type}"
        ):
            execute_assertion(
                assertion,
                response,
            )