import pandas as pd
import numpy as np

def generate_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # 计算快线 EMA12 和慢线 EMA26
    df["ema12"] = df["close"].ewm(span=12, adjust=False).mean()
    df["ema26"] = df["close"].ewm(span=26, adjust=False).mean()

    # 判断金叉：当前快线 > 慢线 且 上一根K线快线 <= 慢线
    df["golden_cross"] = (df["ema12"] > df["ema26"]) & (df["ema12"].shift(1) <= df["ema26"].shift(1))

    # 判断死叉：当前快线 < 慢线 且 上一根K线快线 >= 慢线
    df["death_cross"] = (df["ema12"] < df["ema26"]) & (df["ema12"].shift(1) >= df["ema26"].shift(1))

    # 初始化 target_position
    df["target_position"] = np.nan

    # 金叉开多仓
    df.loc[df["golden_cross"], "target_position"] = 1

    # 死叉平多仓
    df.loc[df["death_cross"], "target_position"] = 0

    # 信号延续：未产生新信号时保持上一根K线的持仓状态
    df["target_position"] = df["target_position"].ffill().fillna(0)

    # 确保只包含 0 或 1（本策略仅做多）
    df["target_position"] = df["target_position"].astype(int)
    df["target_position"] = df["target_position"].clip(0, 1)

    return df