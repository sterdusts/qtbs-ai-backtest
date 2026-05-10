import pandas as pd
import numpy as np


class CodeBacktestCore:
    """
    新版代码策略回测核心。

    它不理解 MA、RSI、MACD、布林带。
    它只看 strategy_func(df) 生成的 target_position。

    target_position:
        1  = 做多
        0  = 空仓
        -1 = 做空

    当前支持：
        initial_cash   初始资金
        fee_rate       手续费率，小数形式，例如 0.0005 = 万分之五
        slippage       滑点，小数形式，例如 0.0001 = 万分之一
        leverage       杠杆倍数，整数，最小按 1 倍计算
        position_size  仓位比例，小数形式，例如 1.0 = 满仓，0.5 = 半仓

    注意：
        这里是简化版合约回测模型。
        支持杠杆名义仓位、手续费、滑点。
        暂不模拟强平、维持保证金、资金费率。
    """

    def __init__(
        self,
        strategy_func,
        initial_cash: float = 1000,
        fee_rate: float = 0.0,
        slippage: float = 0.0,
        leverage: int = 1,
        position_size: float = 1.0,
    ):
        self.strategy_func = strategy_func
        self.initial_cash = float(initial_cash)
        self.fee_rate = float(fee_rate)
        self.slippage = float(slippage)

        self.leverage = int(leverage)
        if self.leverage <= 0:
            self.leverage = 1

        self.position_size = float(position_size)
        self.position_size = min(max(self.position_size, 0.0), 1.0)

    def run(self, df: pd.DataFrame) -> dict:
        df = df.copy()

        df = self.strategy_func(df)

        if "target_position" not in df.columns:
            raise ValueError("策略函数必须生成 target_position 字段")

        df["target_position"] = df["target_position"].fillna(0).astype(int)

        cash = self.initial_cash
        position = 0.0
        position_side = 0

        entry_price = None
        entry_raw_price = None
        entry_time = None
        entry_equity = None
        entry_margin = None
        entry_notional = None
        entry_open_fee = None

        trades = []
        equity_curve = []
        realized_equity_curve = []

        realized_equity = self.initial_cash

        for i in range(1, len(df) - 1):
            current_time = df.index[i]
            next_time = df.index[i + 1]

            current_target = int(df["target_position"].iloc[i])
            previous_target = int(df["target_position"].iloc[i - 1])

            close_price = float(df["close"].iloc[i])
            next_open = float(df["open"].iloc[i + 1])

            # =========================
            # 1. 计算实时权益
            # =========================

            if position_side == 0:
                floating_equity = cash

            elif position_side == 1:
                unrealized_pnl = position * (close_price - entry_price)
                floating_equity = cash + unrealized_pnl

            elif position_side == -1:
                unrealized_pnl = position * (entry_price - close_price)
                floating_equity = cash + unrealized_pnl

            else:
                raise ValueError("未知仓位方向")

            equity_curve.append({
                "time": str(current_time),
                "equity": float(floating_equity),
            })

            realized_equity_curve.append({
                "time": str(current_time),
                "equity": float(realized_equity),
            })

            # =========================
            # 2. target_position 没变化，不交易
            # =========================

            if current_target == previous_target:
                continue

            # =========================
            # 3. 下一根 K 线 open 执行
            # =========================

            execute_time = next_time
            exit_raw_price = next_open

            # =========================
            # 4. 先平旧仓
            # =========================

            if position_side != 0:
                if position_side == 1:
                    exit_price = next_open * (1 - self.slippage)

                    raw_return = exit_raw_price / entry_raw_price - 1
                    gross_pnl = entry_notional * raw_return
                    gross_pnl_pct = gross_pnl / entry_equity * 100 if entry_equity else 0.0

                    net_pnl_before_close_fee = position * (exit_price - entry_price)
                    close_notional = abs(position * exit_price)
                    close_fee = close_notional * self.fee_rate

                    cash = cash + net_pnl_before_close_fee - close_fee

                    net_pnl = cash - entry_equity
                    net_pnl_pct = net_pnl / entry_equity * 100 if entry_equity else 0.0

                elif position_side == -1:
                    exit_price = next_open * (1 + self.slippage)

                    raw_return = (entry_raw_price - exit_raw_price) / entry_raw_price
                    gross_pnl = entry_notional * raw_return
                    gross_pnl_pct = gross_pnl / entry_equity * 100 if entry_equity else 0.0

                    net_pnl_before_close_fee = position * (entry_price - exit_price)
                    close_notional = abs(position * exit_price)
                    close_fee = close_notional * self.fee_rate

                    cash = cash + net_pnl_before_close_fee - close_fee

                    net_pnl = cash - entry_equity
                    net_pnl_pct = net_pnl / entry_equity * 100 if entry_equity else 0.0

                else:
                    raise ValueError("未知仓位方向")

                holding_hours = self._calculate_holding_hours(entry_time, execute_time)

                trades.append({
                    "entry_time": str(entry_time),
                    "exit_time": str(execute_time),
                    "side": "long" if position_side == 1 else "short",

                    "entry_price": float(entry_price),
                    "exit_price": float(exit_price),
                    "entry_raw_price": float(entry_raw_price),
                    "exit_raw_price": float(exit_raw_price),

                    "leverage": int(self.leverage),
                    "position_size": float(self.position_size),
                    "entry_margin": float(entry_margin),
                    "entry_notional": float(entry_notional),
                    "open_fee": float(entry_open_fee),
                    "close_fee": float(close_fee),

                    "gross_pnl": float(gross_pnl),
                    "gross_pnl_pct": float(gross_pnl_pct),

                    # pnl 保持兼容旧代码，含义是净盈亏
                    "pnl": float(net_pnl),
                    "pnl_pct": float(net_pnl_pct),
                    "net_pnl": float(net_pnl),
                    "net_pnl_pct": float(net_pnl_pct),

                    "holding_hours": float(holding_hours),
                    "equity_after": float(cash),
                })

                realized_equity = cash

                position = 0.0
                position_side = 0
                entry_price = None
                entry_raw_price = None
                entry_time = None
                entry_equity = None
                entry_margin = None
                entry_notional = None
                entry_open_fee = None

            # =========================
            # 5. 再开新仓
            # =========================

            if current_target == 1:
                if cash <= 0:
                    continue

                entry_raw_price = next_open
                entry_price = next_open * (1 + self.slippage)
                entry_equity = cash

                entry_margin = entry_equity * self.position_size
                entry_notional = entry_margin * self.leverage

                if entry_notional <= 0:
                    continue

                entry_open_fee = entry_notional * self.fee_rate

                position = entry_notional / entry_price
                cash = entry_equity - entry_open_fee

                position_side = 1
                entry_time = execute_time

            elif current_target == -1:
                if cash <= 0:
                    continue

                entry_raw_price = next_open
                entry_price = next_open * (1 - self.slippage)
                entry_equity = cash

                entry_margin = entry_equity * self.position_size
                entry_notional = entry_margin * self.leverage

                if entry_notional <= 0:
                    continue

                entry_open_fee = entry_notional * self.fee_rate

                position = entry_notional / entry_price
                cash = entry_equity - entry_open_fee

                position_side = -1
                entry_time = execute_time

            elif current_target == 0:
                pass

            else:
                raise ValueError("target_position 只能是 -1, 0, 1")

        final_equity = equity_curve[-1]["equity"] if equity_curve else self.initial_cash

        metrics = self._calculate_metrics(
            equity_curve=equity_curve,
            trades=trades,
            initial_cash=self.initial_cash,
            final_equity=final_equity,
        )

        metrics["leverage"] = self.leverage
        metrics["position_size"] = self.position_size

        return {
            "df": df,
            "trades": trades,
            "equity_curve": equity_curve,
            "realized_equity_curve": realized_equity_curve,
            "metrics": metrics,
        }

    def _calculate_holding_hours(self, entry_time, exit_time) -> float:
        if entry_time is None or exit_time is None:
            return 0.0

        entry_dt = pd.to_datetime(entry_time)
        exit_dt = pd.to_datetime(exit_time)

        return (exit_dt - entry_dt).total_seconds() / 3600

    def _max_consecutive_count(self, values, condition_func) -> int:
        max_count = 0
        current_count = 0

        for value in values:
            if condition_func(value):
                current_count += 1
                max_count = max(max_count, current_count)
            else:
                current_count = 0

        return max_count

    def _calculate_metrics(
        self,
        equity_curve,
        trades,
        initial_cash,
        final_equity,
    ):
        # =========================
        # 基础收益
        # =========================

        total_return_pct = (final_equity / initial_cash - 1) * 100

        # =========================
        # 最大回撤
        # =========================

        equity_values = np.array([x["equity"] for x in equity_curve], dtype=float)

        if len(equity_values) > 0:
            peak = np.maximum.accumulate(equity_values)
            drawdown = (equity_values - peak) / peak
            max_drawdown_pct = drawdown.min() * 100
        else:
            max_drawdown_pct = 0.0

        # =========================
        # 年化收益 & 夏普比率
        # =========================

        annual_return_pct = 0.0
        sharpe_ratio = 0.0

        if len(equity_curve) >= 2:
            equity_df = pd.DataFrame(equity_curve)
            equity_df["time"] = pd.to_datetime(equity_df["time"])
            equity_df = equity_df.sort_values("time")

            start_time = equity_df["time"].iloc[0]
            end_time = equity_df["time"].iloc[-1]
            duration_days = (end_time - start_time).total_seconds() / 86400

            if duration_days > 0 and initial_cash > 0 and final_equity > 0:
                annual_return_pct = ((final_equity / initial_cash) ** (365.25 / duration_days) - 1) * 100

            returns = equity_df["equity"].pct_change().replace([np.inf, -np.inf], np.nan).dropna()

            time_diffs = equity_df["time"].diff().dropna()
            if len(time_diffs) > 0:
                median_period_days = time_diffs.median().total_seconds() / 86400

                if median_period_days > 0 and len(returns) > 1:
                    periods_per_year = 365.25 / median_period_days
                    return_std = returns.std()

                    if return_std and return_std > 0:
                        sharpe_ratio = returns.mean() / return_std * np.sqrt(periods_per_year)

        # =========================
        # 交易统计
        # =========================

        trade_count = len(trades)

        if trade_count == 0:
            return {
                "initial_cash": initial_cash,
                "final_equity": final_equity,
                "total_return_pct": total_return_pct,
                "max_drawdown_pct": max_drawdown_pct,
                "annual_return_pct": annual_return_pct,
                "sharpe_ratio": sharpe_ratio,

                "trade_count": 0,
                "gross_win_rate": 0.0,
                "net_win_rate": 0.0,
                "win_rate": 0.0,

                "avg_profit": 0.0,
                "avg_loss": 0.0,
                "payoff_ratio": 0.0,
                "profit_factor": 0.0,

                "max_consecutive_wins": 0,
                "max_consecutive_losses": 0,
                "avg_holding_hours": 0.0,
            }

        gross_pnls = np.array([t.get("gross_pnl", 0.0) for t in trades], dtype=float)
        net_pnls = np.array([t.get("pnl", 0.0) for t in trades], dtype=float)
        holding_hours = np.array([t.get("holding_hours", 0.0) for t in trades], dtype=float)

        gross_win_rate = np.sum(gross_pnls > 0) / trade_count * 100
        net_win_rate = np.sum(net_pnls > 0) / trade_count * 100

        profit_trades = net_pnls[net_pnls > 0]
        loss_trades = net_pnls[net_pnls < 0]

        avg_profit = float(profit_trades.mean()) if len(profit_trades) > 0 else 0.0
        avg_loss = float(loss_trades.mean()) if len(loss_trades) > 0 else 0.0

        if avg_loss < 0:
            payoff_ratio = avg_profit / abs(avg_loss)
        else:
            payoff_ratio = float("inf") if avg_profit > 0 else 0.0

        gross_profit_sum = float(profit_trades.sum()) if len(profit_trades) > 0 else 0.0
        gross_loss_sum = float(loss_trades.sum()) if len(loss_trades) > 0 else 0.0

        if gross_loss_sum < 0:
            profit_factor = gross_profit_sum / abs(gross_loss_sum)
        else:
            profit_factor = float("inf") if gross_profit_sum > 0 else 0.0

        max_consecutive_wins = self._max_consecutive_count(
            net_pnls,
            lambda x: x > 0,
        )

        max_consecutive_losses = self._max_consecutive_count(
            net_pnls,
            lambda x: x < 0,
        )

        avg_holding_hours = float(holding_hours.mean()) if len(holding_hours) > 0 else 0.0

        return {
            "initial_cash": initial_cash,
            "final_equity": final_equity,
            "total_return_pct": total_return_pct,
            "max_drawdown_pct": max_drawdown_pct,
            "annual_return_pct": annual_return_pct,
            "sharpe_ratio": sharpe_ratio,

            "trade_count": trade_count,
            "gross_win_rate": gross_win_rate,
            "net_win_rate": net_win_rate,

            # 兼容旧 webUI 里的 win_rate
            "win_rate": net_win_rate,

            "avg_profit": avg_profit,
            "avg_loss": avg_loss,
            "payoff_ratio": payoff_ratio,
            "profit_factor": profit_factor,

            "max_consecutive_wins": max_consecutive_wins,
            "max_consecutive_losses": max_consecutive_losses,
            "avg_holding_hours": avg_holding_hours,
        }