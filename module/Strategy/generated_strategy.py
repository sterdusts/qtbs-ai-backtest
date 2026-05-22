import pandas as pd
import numpy as np

def generate_signals(df: pd.DataFrame) -> pd.DataFrame:
    """
    策略名称：双均线金叉死叉趋势跟踪策略
    策略原理：
    - 使用两条指数移动平均线（EMA），一条快线（EMA12）和一条慢线（EMA26）。
    - 当快线上穿慢线时（金叉），视为上涨趋势启动，开多仓（target_position = 1）。
    - 当快线下穿慢线时（死叉），视为下跌趋势启动，平多仓（target_position = 0）。
    - 本策略仅做多，不做空，不设止损止盈，不设加仓。
    - 信号在当前K线收盘后确认，下一根K线开盘执行。
    """
    df = df.copy()

    # 计算快线EMA12和慢线EMA26
    df["ema_fast"] = df["close"].ewm(span=12, adjust=False).mean()
    df["ema_slow"] = df["close"].ewm(span=26, adjust=False).mean()

    # 判断金叉和死叉（使用shift(1)避免未来数据）
    df["golden_cross"] = (df["ema_fast"] > df["ema_slow"]) & (df["ema_fast"].shift(1) <= df["ema_slow"].shift(1))
    df["death_cross"] = (df["ema_fast"] < df["ema_slow"]) & (df["ema_fast"].shift(1) >= df["ema_slow"].shift(1))

    # 初始化target_position
    df["target_position"] = np.nan

    # 金叉时开多仓
    df.loc[df["golden_cross"], "target_position"] = 1
    # 死叉时平多仓（空仓）
    df.loc[df["death_cross"], "target_position"] = 0

    # 信号延续：未触发新信号时保持上一根K线的持仓状态
    df["target_position"] = df["target_position"].ffill().fillna(0)
    df["target_position"] = df["target_position"].astype(int)

    return df