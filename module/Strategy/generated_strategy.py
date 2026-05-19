import pandas as pd
import numpy as np

def generate_signals(df: pd.DataFrame) -> pd.DataFrame:
    """
    策略名称：DPO + ER + TII 三重过滤趋势跟踪策略

    策略原理：
    本策略将 DPO、ER、TII 三个指标组合成一个三层过滤系统，用于识别方向明确、力量支持、趋势增强的行情。
    只有当三个指标同时发出多头信号时，才建立多头仓位；当多头信号消失时，平仓空仓。

    三层过滤逻辑：
    第一层（DPO - 方向判断）：
        DPO = 当前价格 - 延迟均线（N周期移动平均，再向前偏移N/2+1周期）
        DPO > 0 表示市场短期偏强，环境有利于做多。
        DPO < 0 表示市场短期偏弱，环境不利于做多。

    第二层（ER - 多空力量判断）：
        BullPower = HIGH - EMA(CLOSE, N)
        BearPower = LOW - EMA(CLOSE, N)
        BearPower > 0 表示空头力量减弱，多头开始接管市场。
        BearPower 上穿 0 线是重要的多头确认信号。

    第三层（TII - 趋势强度判断）：
        TII 基于价格相对于均线的偏离程度计算，类似RSI的变体。
        TII 上穿 TII_SIGNAL（TII的移动平均）表示趋势强度正在增强，具备延续性。

    入场条件（做多）：
        DPO > 0 且 BearPower > 0 且 TII > TII_SIGNAL

    出场条件（平多）：
        当上述三个条件中任意一个不满足时，平仓出场。

    注意：本策略仅做多，不做空。target_position 只取 1 或 0。
    """

    df = df.copy()

    # ========== 参数设置 ==========
    # DPO参数：周期
    dpo_period = 20
    # ER参数：EMA周期
    er_period = 13
    # TII参数：周期和信号线周期
    tii_period = 14
    tii_signal_period = 7

    # ========== 1. 计算 DPO ==========
    # DPO = 当前价格 - 延迟均线
    # 延迟均线 = SMA(close, N) 向前偏移 N/2 + 1 个周期
    sma_dpo = df['close'].rolling(window=dpo_period).mean()
    shift_period = dpo_period // 2 + 1
    # 延迟均线：将SMA向前偏移
    delayed_ma = sma_dpo.shift(shift_period)
    df['DPO'] = df['close'] - delayed_ma

    # ========== 2. 计算 ER (BullPower / BearPower) ==========
    ema_er = df['close'].ewm(span=er_period, adjust=False).mean()
    df['BullPower'] = df['high'] - ema_er
    df['BearPower'] = df['low'] - ema_er

    # ========== 3. 计算 TII ==========
    # TII 计算：基于价格相对于均线的偏离
    # 先计算价格相对于均线的偏离值
    sma_tii = df['close'].rolling(window=tii_period).mean()
    # 计算偏离值：close - sma
    deviation = df['close'] - sma_tii
    # 计算正偏离和负偏离
    positive_deviation = deviation.copy()
    negative_deviation = deviation.copy()
    positive_deviation[positive_deviation < 0] = 0
    negative_deviation[negative_deviation > 0] = 0
    negative_deviation = negative_deviation.abs()
    # 计算TII
    sum_positive = positive_deviation.rolling(window=tii_period).sum()
    sum_negative = negative_deviation.rolling(window=tii_period).sum()
    # 避免除零
    denominator = sum_positive + sum_negative
    denominator = denominator.replace(0, np.nan)
    df['TII'] = 100 * (sum_positive / denominator)
    # TII信号线
    df['TII_SIGNAL'] = df['TII'].rolling(window=tii_signal_period).mean()

    # ========== 4. 生成信号条件 ==========
    # 入场条件：DPO > 0 且 BearPower > 0 且 TII > TII_SIGNAL
    long_entry_condition = (
        (df['DPO'] > 0) &
        (df['BearPower'] > 0) &
        (df['TII'] > df['TII_SIGNAL'])
    )

    # 出场条件：上述三个条件中任意一个不满足
    long_exit_condition = (
        (df['DPO'] <= 0) |
        (df['BearPower'] <= 0) |
        (df['TII'] <= df['TII_SIGNAL'])
    )

    # ========== 5. 设置 target_position ==========
    df['target_position'] = np.nan

    # 入场时设置为1
    df.loc[long_entry_condition, 'target_position'] = 1

    # 出场时设置为0
    df.loc[long_exit_condition, 'target_position'] = 0

    # 延续上一根K线的状态
    df['target_position'] = df['target_position'].ffill()

    # 处理NaN：初始状态为空仓
    df['target_position'] = df['target_position'].fillna(0)

    # 确保只包含0和1
    df['target_position'] = df['target_position'].astype(int)
    df['target_position'] = df['target_position'].clip(0, 1)

    return df