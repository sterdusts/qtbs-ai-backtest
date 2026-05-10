import pandas as pd
import numpy as np

def generate_signals(df: pd.DataFrame) -> pd.DataFrame:
    """
    策略名称：双均线趋势跟踪策略
    策略原理：
    - 使用两条指数移动平均线（EMA12 和 EMA26）判断趋势方向。
    - 当 EMA12 上穿 EMA26 时，视为多头趋势启动，开多仓（target_position = 1）。
    - 当 EMA12 下穿 EMA26 时，视为多头趋势结束，平多仓（target_position = 0）。
    - 本策略仅做多，不做空。
    - 信号在当前K线收盘后确认，下一根K线开盘执行。
    """
    df = df.copy()

    # 计算指标：12周期和26周期指数移动平均线
    df["ema12"] = df["close"].ewm(span=12, adjust=False).mean()
    df["ema26"] = df["close"].ewm(span=26, adjust=False).mean()

    # 生成信号条件
    # 上穿：当前ema12 > ema26 且 上一根K线ema12 <= ema26
    buy_condition = (df["ema12"] > df["ema26"]) & (df["ema12"].shift(1) <= df["ema26"].shift(1))
    # 下穿：当前ema12 < ema26 且 上一根K线ema12 >= ema26
    sell_condition = (df["ema12"] < df["ema26"]) & (df["ema12"].shift(1) >= df["ema26"].shift(1))

    # 初始化target_position
    df["target_position"] = np.nan

    # 开多信号
    df.loc[buy_condition, "target_position"] = 1
    # 平多信号
    df.loc[sell_condition, "target_position"] = 0

    # 信号延续：没有新信号时保持上一根K线的持仓状态
    df["target_position"] = df["target_position"].ffill().fillna(0)
    df["target_position"] = df["target_position"].astype(int)

    return df