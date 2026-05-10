# module/AI/deepseek_code_generator.py

import os
import re
from openai import OpenAI


FORBIDDEN_TIMEFRAME_TOKENS = [
    '"1m"', "'1m'",
    '"5m"', "'5m'",
    '"15m"', "'15m'",
    '"1h"', "'1h'",
    '"4h"', "'4h'",
    '"1d"', "'1d'",
    '"1T"', "'1T'",
    '"5T"', "'5T'",
    '"15T"', "'15T'",
    '"1H"', "'1H'",
    '"4H"', "'4H'",
    '"1D"', "'1D'",
    "resample(",
    ".resample(",
    "timeframe",
]


def clean_python_code(content: str) -> str:
    """
    清理 DeepSeek 返回内容：
    - 去掉 ```python
    - 去掉 ```
    - 去掉前后空白
    """

    if not content:
        raise ValueError("DeepSeek 返回空内容，请重试。")

    content = content.strip()

    # 去掉 markdown 代码块
    content = re.sub(r"^```python\s*", "", content)
    content = re.sub(r"^```\s*", "", content)
    content = re.sub(r"\s*```$", "", content)

    return content.strip()


def validate_generated_code(code: str) -> None:
    """
    对 DeepSeek 生成的策略代码做基础结构检查。

    这里不是完整安全沙箱，真正执行前仍然建议由 strategy_loader.py 做进一步安全检查。
    这个函数主要拦截：
    1. 没有 generate_signals
    2. 没有 target_position
    3. 在策略代码里写死周期
    4. 在策略代码里重采样 K 线
    """

    if "def generate_signals" not in code:
        raise ValueError("DeepSeek 返回的代码中没有 generate_signals 函数。")

    if "target_position" not in code:
        raise ValueError("DeepSeek 返回的代码中没有 target_position 字段。")

    lower_code = code.lower()

    for token in FORBIDDEN_TIMEFRAME_TOKENS:
        if token.lower() in lower_code:
            raise ValueError(
                f"DeepSeek 返回的代码中出现了不允许的周期写死或重采样内容：{token}。"
                "请重新生成策略代码。策略代码只能基于传入的 df 计算，不能写死 1m/5m/15m/1h/4h/1d，也不能 resample。"
            )


def build_strategy_code_prompt(
    user_text: str,
    market: str = "加密货币",
    symbol: str = "BTCUSDT",
    timeframe: str = "4h",
    language: str = "中文",
    allow_short: bool = False,
    initial_cash: float | None = None,
    fee_rate_percent: float | None = None,
    slippage_percent: float | None = None,
) -> str:
    """
    构造给 DeepSeek 的策略代码生成 Prompt。

    注意：
    - market / symbol / timeframe 可以给 AI，作为策略上下文。
    - timeframe 只能作为上下文，不允许 AI 写进代码。
    - 手续费 / 滑点可以作为环境说明，但不允许 AI 自己写成交逻辑。
    - AI 只能生成 generate_signals(df)。
    """

    allow_short_text = (
        "允许做空。策略可以使用 target_position = -1。"
        if allow_short
        else "默认不允许做空。除非用户策略明确要求做空，否则只能使用 target_position = 1 或 0。"
    )

    env_text = f"""
当前回测环境：
- 市场类型：{market}
- 交易标的：{symbol}
- 当前 webUI 选择的 K线周期：{timeframe}
- 用户语言：{language}
- 初始资金：{initial_cash if initial_cash is not None else "由回测框架默认处理"}
- 手续费率：{fee_rate_percent if fee_rate_percent is not None else 0}%
- 滑点：{slippage_percent if slippage_percent is not None else 0}%

重要说明：
1. 手续费、滑点、初始资金由回测框架处理。
2. 你不要在策略代码中计算手续费、滑点、收益率、净值曲线或成交价格。
3. 当前 K线周期只用于理解用户策略背景，不允许写进代码。
4. 系统会根据 webUI 选择的周期，提前把对应周期的 K线 DataFrame 传入 generate_signals(df)。
"""

    timeframe_rule = """
时间周期规则，必须严格遵守：

1. 不要在代码中写死任何时间周期。
2. 不要在代码中出现 "1m"、"5m"、"15m"、"1h"、"4h"、"1d" 等字符串。
3. 不要在代码中定义 timeframe 变量。
4. 不要根据 timeframe 判断不同逻辑。
5. 不要使用 df.resample(...) 或任何重采样逻辑。
6. 不要读取其他周期数据。
7. 不要创建多周期 K线。
8. generate_signals(df) 必须只基于系统传入的 df 计算。
9. 如果用户策略描述里出现“使用 4小时K线 / 1小时K线 / 日线”等说法，只把它理解为策略背景，不要写入代码。
10. 策略代码应该对任意周期的 df 都能运行。
"""

    prompt = f"""
你是一个专业量化策略代码生成器。

你的任务：
根据用户的自然语言策略，生成一个 Python 策略函数。

你只能生成一个函数：

def generate_signals(df: pd.DataFrame) -> pd.DataFrame:

你必须遵守以下规则：

1. 只能输出 Python 代码。
2. 不要输出 markdown。
3. 不要输出解释。
4. 不要输出 JSON。
5. 不要生成完整回测系统。
6. 不要读取本地文件。
7. 不要调用网络 API。
8. 不要调用交易所接口。
9. 不要生成可视化代码。
10. 不要计算最终收益。
11. 不要计算手续费。
12. 不要计算滑点。
13. 不要生成下单代码。
14. 不要使用未来数据。
15. 只能使用 pandas 和 numpy。

代码开头必须包含：

import pandas as pd
import numpy as np

输入 df 是已经处理好的 K线 DataFrame，至少包含以下字段：

open
high
low
close
volume

你可以新增指标列，例如：

ma20
ma60
ema20
ema60
rsi14
macd
signal_line
boll_upper
boll_lower
atr14
volume_ma20

你必须新增或覆盖字段：

target_position

target_position 的含义：

1 = 应该持有多仓
0 = 应该空仓
-1 = 应该持有空仓

{allow_short_text}

{timeframe_rule}

重要时序规则：

1. 所有信号默认在当前 K 线 close 后确认。
2. 回测框架会在下一根 K 线 open 执行。
3. 所以你只需要生成 target_position，不需要处理成交价格。
4. 判断上穿 / 下穿必须使用 shift(1)。
5. 禁止使用 shift(-1)。
6. 禁止使用未来 K 线数据。
7. rolling / ewm 指标只能基于当前和历史数据。

策略输出规则：

1. 如果用户只描述做多策略：
   - 满足开多条件时 target_position = 1
   - 满足平仓条件时 target_position = 0

2. 如果用户明确描述做空或多空切换：
   - 满足做多条件时 target_position = 1
   - 满足做空条件时 target_position = -1
   - 满足空仓条件时 target_position = 0

3. 如果用户没有说止损止盈，不要自己添加止损止盈。
4. 如果用户没有说做空，不要自己添加做空。
5. 如果用户没有说加仓，不要生成加仓逻辑。
6. 如果用户说浮盈加仓、分批建仓、网格、做T、多空对冲，当前框架暂不支持，请生成最接近的单仓位 target_position 版本。
7. 如果信号没有变化，target_position 应该延续上一根 K 线的状态。
8. 最后必须处理 NaN，并确保 target_position 中只包含 -1、0、1。

推荐代码结构：

import pandas as pd
import numpy as np


def generate_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # 计算指标

    # 生成条件

    df["target_position"] = np.nan

    # 根据条件设置 target_position

    df["target_position"] = df["target_position"].ffill().fillna(0)
    df["target_position"] = df["target_position"].astype(int)

    return df

{env_text}

用户策略描述如下：

{user_text}
"""

    return prompt.strip()


def generate_strategy_code_with_deepseek(
    user_text: str,
    market: str = "加密货币",
    symbol: str = "BTCUSDT",
    timeframe: str = "4h",
    language: str = "中文",
    allow_short: bool = False,
    initial_cash: float | None = None,
    fee_rate_percent: float | None = None,
    slippage_percent: float | None = None,
) -> str:
    """
    调用 DeepSeek，把自然语言策略转换成 generate_signals(df) 策略代码。

    返回：
        Python 代码字符串
    """

    api_key = os.environ.get("DEEPSEEK_API_KEY")

    if not api_key:
        raise ValueError(
            "没有读取到 DEEPSEEK_API_KEY，请先在 PyCharm 的 Environment variables 里设置。"
        )

    client = OpenAI(
        api_key=api_key,
        base_url="https://api.deepseek.com"
    )

    system_prompt = """
你是一个量化策略代码生成器。
你只负责生成策略信号函数 generate_signals(df)。
你不能生成完整回测系统。
你不能生成 JSON。
你不能解释。
你只能输出 Python 代码。

硬性规则：
1. 不能在策略代码中写死任何 K线周期。
2. 不能在策略代码中写 "1m"、"5m"、"15m"、"1h"、"4h"、"1d"。
3. 不能使用 resample。
4. 不能读取其他周期数据。
5. 只能基于传入的 df 计算指标和 target_position。
6. 把策略详情注释在代码里面，要让使用者知道这个策略代码原理是什么，并方便让使用者比较与其描述是否相符。注释语言使用使用者输入语言注释，比如使用者使用中文输入，代码注释则使用中文，如果输入语言是英文则使用英文注释代码，其余语言同上。
"""

    user_prompt = build_strategy_code_prompt(
        user_text=user_text,
        market=market,
        symbol=symbol,
        timeframe=timeframe,
        language=language,
        allow_short=allow_short,
        initial_cash=initial_cash,
        fee_rate_percent=fee_rate_percent,
        slippage_percent=slippage_percent,
    )

    response = client.chat.completions.create(
        model="deepseek-v4-flash",
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ],
        temperature=0.1,
        max_tokens=4000,
        extra_body={
            "thinking": {"type": "disabled"}
        }
    )

    content = response.choices[0].message.content

    code = clean_python_code(content)

    validate_generated_code(code)

    return code