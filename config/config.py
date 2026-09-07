import os
from pathlib import Path

from dotenv import load_dotenv


# 项目根目录
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# 明确读取项目根目录下的.env
ENV_FILE = PROJECT_ROOT / ".env"
load_dotenv(ENV_FILE)


def get_bool(name, default=False):
    """读取布尔类型环境变量。"""
    value = os.getenv(
        name,
        str(default),
    )

    return value.strip().lower() in {
        "true",
        "1",
        "yes",
        "on",
    }


def get_int(name, default):
    """读取整数类型环境变量。"""
    value = os.getenv(name, str(default))

    try:
        return int(value)
    except ValueError as exc:
        raise ValueError(
            f"环境变量{name}必须是整数，实际值：{value}"
        ) from exc


def get_float(name, default):
    """读取浮点数类型环境变量。"""
    value = os.getenv(name, str(default))

    try:
        return float(value)
    except ValueError as exc:
        raise ValueError(
            f"环境变量{name}必须是数字，实际值：{value}"
        ) from exc


def resolve_project_path(path_value):
    """将相对路径转换为基于项目根目录的绝对路径。"""
    path = Path(path_value)

    if not path.is_absolute():
        path = PROJECT_ROOT / path

    return str(path.resolve())


# 当前测试环境
TEST_ENV = os.getenv(
    "TEST_ENV",
    "local",
)

# 接口配置
BASE_URL = os.getenv(
    "BASE_URL",
    "http://127.0.0.1:8888/api/private/v1",
).rstrip("/")

# 用例文件配置
CASE_FILE = resolve_project_path(
    os.getenv(
        "CASE_FILE",
        "./data/test_cases.yaml",
    )
)

EXCEL_FILE = resolve_project_path(
    "./data/测试数据.xlsx"
)

SHEET_NAME = os.getenv(
    "SHEET_NAME",
    "Sheet1",
)

# HTTP超时配置
HTTP_CONNECT_TIMEOUT = get_float(
    "HTTP_CONNECT_TIMEOUT",
    3.05,
)

HTTP_READ_TIMEOUT = get_float(
    "HTTP_READ_TIMEOUT",
    10,
)

# 数据库开关
DB_ENABLED = get_bool(
    "DB_ENABLED",
    False,
)

# 数据库配置
DB_HOST = os.getenv(
    "DB_HOST",
    "127.0.0.1",
)

DB_PORT = get_int(
    "DB_PORT",
    3306,
)

DB_NAME = os.getenv(
    "DB_NAME",
    "mydb",
)

DB_USER = os.getenv(
    "DB_USER",
    "root",
)

DB_PASSWORD = os.getenv(
    "DB_PASSWORD",
    "",
)

# 仅在启用数据库时校验必要配置
if DB_ENABLED and not DB_PASSWORD:
    raise ValueError(
        "DB_ENABLED=true时必须配置DB_PASSWORD"
    )

# 原有清理SQL暂时保留，后面重构数据清理
SQL1 = (
    'delete from sp_category '
    'where cat_name = "大码服装"'
)

SQL2 = (
    'delete from sp_attribute '
    'where attr_name = "VIP尺码"'
)

SQL3 = (
    'delete from sp_goods '
    'where goods_name = "大码牛仔裤+"'
)