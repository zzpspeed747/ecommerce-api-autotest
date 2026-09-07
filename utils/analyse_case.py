import logging

import allure

from config.config import BASE_URL


@allure.step("1.解析请求数据")
def analyse_case(case):
    request_data = {
        "method": case["method"],
        "url": BASE_URL + case["path"],
        "headers": case.get("headers"),
        "params": case.get("params"),
        "data": case.get("data"),
        "json": case.get("json"),
        "files": case.get("files"),
    }

    logging.info(f"1.解析请求数据，请求数据为：{request_data}")
    allure.attach(f"1.解析请求数据，请求数据为：{request_data}", name="解析数据结果")
    return request_data