import json
from pathlib import Path

import yaml

from utils.excel_utils import read_excel


STRUCTURED_FIELDS = {
    "headers",
    "params",
    "data",
    "json",
    "files",
    "jsonExData",
    "sqlExData",
    "requires",
    "assertions",
}


def read_yaml(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        cases = yaml.safe_load(file)

    if not isinstance(cases, list):
        raise ValueError("YAML测试用例的最外层必须是列表")

    return cases


def read_json(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        cases = json.load(file)

    if not isinstance(cases, list):
        raise ValueError("JSON测试用例的最外层必须是列表")

    return cases


def normalize_case(case):
    """
    将Excel中的JSON字符串转换为字典或列表。

    YAML和JSON读取出的字段已经是字典或列表，
    因此不会被重复转换。
    """
    normalized_case = case.copy()
    case_id = normalized_case.get("id", "未知")

    for field in STRUCTURED_FIELDS:
        value = normalized_case.get(field)

        if value is None or value == "":
            normalized_case[field] = None
            continue

        if isinstance(value, str):
            try:
                normalized_case[field] = json.loads(value)
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"用例ID={case_id}的字段{field}不是合法JSON：{value}"
                ) from exc

    return normalized_case


def load_cases(file_path, sheet_name="Sheet1"):
    suffix = Path(file_path).suffix.lower()

    if suffix == ".xlsx":
        cases = read_excel(
            file_path=file_path,
            sheet_name=sheet_name,
        )
    elif suffix in {".yaml", ".yml"}:
        cases = read_yaml(file_path)
    elif suffix == ".json":
        cases = read_json(file_path)
    else:
        raise ValueError(f"暂不支持该用例文件格式：{suffix}")

    enabled_cases = [
        case
        for case in cases
        if case.get("is_true", True)
    ]

    return [normalize_case(case) for case in enabled_cases]