import allure
import jsonpath

from config.config import DB_ENABLED
from utils.send_request import *

def json_extractor(case,all,res):
    if case["jsonExData"]:
        with allure.step("4.JSON提取"):
            # 首先要把jsonExData的key，value拆开
            for key, value in case["jsonExData"].items():
                value = jsonpath.jsonpath(res.json(), value)[0]
                all[key] = value
            logging.info(f"4.JSON提取，根据{case['jsonExData']}提取数据，此时全局变量为:{all}")

def jdbc_extractor(case, all_data):
    extract_rules = case.get("sqlExData")

    if not extract_rules:
        return

    if not DB_ENABLED:
        logging.info(
            f"数据库功能未启用，跳过数据库提取：{extract_rules}"
        )
        return

    with allure.step("4.数据库提取"):
        for key, sql in extract_rules.items():
            all_data[key] = send_jdbc_request(sql)

        logging.info(
            f"数据库提取规则：{extract_rules}，"
            f"当前上下文：{all_data}"
        )