from jinja2 import Environment, StrictUndefined


jinja_environment = Environment(
    undefined=StrictUndefined,
    autoescape=False,
)


def render_data(data, context):
    """
    递归渲染字符串、字典和列表中的Jinja2变量。
    """
    if isinstance(data, str):
        template = jinja_environment.from_string(data)
        return template.render(**context)

    if isinstance(data, dict):
        return {
            key: render_data(value, context)
            for key, value in data.items()
        }

    if isinstance(data, list):
        return [
            render_data(item, context)
            for item in data
        ]

    return data