import ast
import importlib.util
import os
import uuid


GENERATED_STRATEGY_PATH = os.path.join(
    "module",
    "Strategy",
    "generated_strategy.py"
)


FORBIDDEN_KEYWORDS = [
    "import os",
    "import sys",
    "import subprocess",
    "import requests",
    "import socket",
    "import shutil",
    "import pathlib",
    "open(",
    "eval(",
    "exec(",
    "__import__",
    "compile(",
    "globals(",
    "locals(",
]


def validate_strategy_code(code: str) -> None:
    """
    对 AI 生成的策略代码做最基础安全检查。
    不是绝对安全沙箱，但足够作为课程项目第一层防线。
    """

    for keyword in FORBIDDEN_KEYWORDS:
        if keyword in code:
            raise ValueError(f"策略代码包含禁止内容: {keyword}")

    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        raise ValueError(f"策略代码语法错误: {e}")

    has_generate_signals = False

    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            if node.name == "generate_signals":
                has_generate_signals = True

        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name not in ["pandas", "numpy"]:
                    raise ValueError(f"禁止导入模块: {alias.name}")

        if isinstance(node, ast.ImportFrom):
            if node.module not in ["pandas", "numpy"]:
                raise ValueError(f"禁止 from {node.module} import ...")

    if not has_generate_signals:
        raise ValueError("策略代码必须包含 generate_signals(df) 函数")


def save_strategy_code(code: str, file_path: str = GENERATED_STRATEGY_PATH) -> str:
    validate_strategy_code(code)

    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(code)

    return file_path


def load_strategy_func(file_path: str = GENERATED_STRATEGY_PATH):
    """
    动态加载 generated_strategy.py。
    每次使用唯一 module 名，避免 Python import 缓存导致加载旧代码。
    """

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"策略文件不存在: {file_path}")

    module_name = f"generated_strategy_{uuid.uuid4().hex}"

    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)

    spec.loader.exec_module(module)

    if not hasattr(module, "generate_signals"):
        raise ValueError("策略文件中没有 generate_signals 函数")

    return module.generate_signals