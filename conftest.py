import logging

import pymysql
import pytest

from config.config import *
from utils.send_request import ApiClient


@pytest.fixture(scope="session")
def case_context():
    """
    保存本轮测试过程中提取的Token、用户ID等关联数据。
    """
    return {}

@pytest.fixture(scope="session")
def api_client():
    """
    整个测试会话共用一个HTTP客户端。
    测试结束后自动关闭Session。
    """
    client = ApiClient()

    yield client

    client.close()

@pytest.fixture(scope='session', autouse=True)
def destroy_data():

    yield

    if not DB_ENABLED:
        logging.info(
            "数据库功能未启用，跳过测试数据清理"
        )
        return
    sqls = [SQL1, SQL2, SQL3]

    conn = pymysql.Connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        charset="utf8",
        autocommit=True
    )
    cur = conn.cursor()
    for sql in sqls:
        cur.execute(sql)
    cur.close()
    conn.close()
    print("资源销毁")