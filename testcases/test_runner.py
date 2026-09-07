import logging

import jsonpath
import pymysql
import pytest
import requests
from jinja2 import Template

from utils.allure_utils import allure_init
from utils.analyse_case import analyse_case
from utils.asserts import *
# from utils.excel_utils import read_excel
from config.config import CASE_FILE, SHEET_NAME
from utils.case_loader import load_cases
from utils.extractor import *
from utils.send_request import *
from utils.template_utils import render_data


class TestRunner:
    # 读测试用例文件中的全部数据，用属性保存即可
    data = load_cases(
        file_path=CASE_FILE,
        sheet_name=SHEET_NAME,)
    # 提取后的数据需要初始化一个全局的属性来保存，可以使用（空字典


    @pytest.mark.parametrize("case", data)
    def test_case(self, case, case_context, api_client):
        # 获取当前用例需要的前置变量
        required_variables = case.get("requires") or []

        # 检查变量是否已经被前面用例提取
        missing_variables = [
            variable
            for variable in required_variables
            if variable not in case_context
        ]

        # 前置变量不存在时跳过当前用例
        if missing_variables:
            pytest.skip(
                f"缺少前置变量：{missing_variables}"
            )

        # 使用上下文渲染Token、用户ID等变量
        case = render_data(case, case_context)

        allure_init(case)

        logging.info(f"0.用例ID：{case['id']} 模块：{case['feature']} 场景：{case['story']} 标题：{case['title']}" )

        # 核心步骤1：解析请求数据
        request_data = analyse_case(case)

        # 核心步骤2：发起请求，得到响应结果
        res = send_http_request(api_client, **request_data)

        # 核心步骤3：执行当前用例配置的全部断言
        assert_case(case, res)

        # 核心步骤4：提取
        # JSON提取
        json_extractor(case, case_context, res)

        #数据库提取
        jdbc_extractor(case, case_context)
