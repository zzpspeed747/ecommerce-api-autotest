import logging
from contextlib import ExitStack
from pathlib import Path

import allure
import pymysql
import requests

from config.config import (
    DB_HOST,
    DB_PORT,
    DB_NAME,
    DB_USER,
    DB_PASSWORD,
    HTTP_CONNECT_TIMEOUT,
    HTTP_READ_TIMEOUT,
)


class ApiRequestError(RuntimeError):
    """HTTP请求过程中发生的框架级异常。"""


class ApiClient:
    """封装Requests Session和统一请求配置。"""

    def __init__(self):
        self.session = requests.Session()
        self.timeout = (
            HTTP_CONNECT_TIMEOUT,
            HTTP_READ_TIMEOUT,
        )

    def request(self, **request_data):
        file_configs = request_data.pop("files", None)

        with ExitStack() as stack:
            upload_files = build_upload_files(
                file_configs,
                stack,
            )

            request_data["files"] = upload_files

            method = request_data.get("method")
            url = request_data.get("url")

            logging.info(
                f"准备发送HTTP请求："
                f"method={method}, url={url}"
            )

            try:
                response = self.session.request(
                    timeout=self.timeout,
                    **request_data,
                )

            except requests.Timeout as exc:
                logging.exception(
                    f"HTTP请求超时：method={method}, url={url}"
                )
                raise ApiRequestError(
                    f"HTTP请求超时：{method} {url}"
                ) from exc

            except requests.ConnectionError as exc:
                logging.exception(
                    f"HTTP连接失败：method={method}, url={url}"
                )
                raise ApiRequestError(
                    f"HTTP连接失败：{method} {url}"
                ) from exc

            except requests.RequestException as exc:
                logging.exception(
                    f"HTTP请求异常：method={method}, url={url}"
                )
                raise ApiRequestError(
                    f"HTTP请求异常：{method} {url}"
                ) from exc

        logging.info(
            f"HTTP响应：status_code={response.status_code}, "
            f"body={response.text}"
        )

        return response

    def close(self):
        self.session.close()


def build_upload_files(file_configs, stack):
    """
    把测试数据中的文件配置转换成Requests上传格式。
    """
    if not file_configs:
        return None

    upload_files = {}

    for field_name, config in file_configs.items():
        file_path = config["path"]

        file_object = stack.enter_context(
            open(file_path, "rb")
        )

        upload_files[field_name] = (
            config.get(
                "filename",
                Path(file_path).name,
            ),
            file_object,
            config.get(
                "content_type",
                "application/octet-stream",
            ),
        )

    return upload_files


@allure.step("2.发送HTTP请求")
def send_http_request(api_client, **request_data):
    """
    保留原有函数入口，内部改为调用ApiClient。
    """
    return api_client.request(**request_data)


def send_jdbc_request(sql, index=0):
    """
    执行数据库查询并返回第一行中指定位置的字段。
    """
    conn = pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        charset="utf8",
    )

    try:
        with conn.cursor() as cur:
            cur.execute(sql)
            result = cur.fetchone()
    finally:
        conn.close()

    if result is None:
        raise AssertionError(
            f"数据库查询结果为空，SQL：{sql}"
        )

    if index >= len(result):
        raise IndexError(
            f"数据库结果不存在索引{index}，查询结果：{result}"
        )

    return result[index]