def evaluate_backtest_results(
    equity_timestamps,
    equity_curve,
    trades=None,
    trade_records=None,
    output_dir="Past_data",
    file_prefix="净值曲线图",
    title="净值曲线图（阶梯）",
    auto_open=True,
    risk_free_rate=0.0
):
    import os
    import math
    import webbrowser
    from datetime import datetime, timezone
    import numpy as np
    import pandas as pd
    from pyecharts.charts import Line
    from pyecharts import options as opts
    from pyecharts.globals import ThemeType

    # ========= 0. 自动生成输出文件路径（UTC+0，不覆盖） =========
    os.makedirs(output_dir, exist_ok=True)

    utc_now = datetime.now(timezone.utc)
    utc_timestamp_str = utc_now.strftime("%Y-%m-%d_%H-%M-%S_UTC")
    output_html_name = os.path.join(output_dir, f"{file_prefix}_{utc_timestamp_str}.html")

    # ========= 1. 基础输入校验 =========
    if equity_timestamps is None or equity_curve is None:
        raise ValueError("equity_timestamps 和 equity_curve 不能为空")

    if len(equity_timestamps) == 0 or len(equity_curve) == 0:
        raise ValueError("equity_timestamps 和 equity_curve 不能为空序列")

    if len(equity_timestamps) != len(equity_curve):
        raise ValueError("equity_timestamps 和 equity_curve 长度必须一致")

    # ========= 2. 净值数据整理 =========
    df_equity = pd.DataFrame({
        "time": pd.to_datetime(equity_timestamps, errors="coerce"),
        "equity": pd.to_numeric(equity_curve, errors="coerce")
    })

    if df_equity["time"].isna().any():
        raise ValueError("equity_timestamps 中存在无法解析为 datetime 的值")

    if df_equity["equity"].isna().any():
        raise ValueError("equity_curve 中存在无法解析为数值的值")

    df_equity = (
        df_equity
        .drop_duplicates(subset=["time"], keep="last")
        .sort_values("time")
        .reset_index(drop=True)
    )

    if len(df_equity) < 2:
        raise ValueError("净值序列至少需要 2 个点，才能计算收益和回撤")

    start_time = df_equity["time"].iloc[0]
    end_time = df_equity["time"].iloc[-1]
    initial_equity = float(df_equity["equity"].iloc[0])
    final_equity = float(df_equity["equity"].iloc[-1])

    if initial_equity <= 0:
        raise ValueError("初始净值必须大于 0，否则总收益率和年化收益率没有意义")

    # ========= 3. 收益序列 =========
    equity_series = pd.Series(df_equity["equity"].values, index=df_equity["time"])
    returns = equity_series.pct_change().dropna()

    time_diffs = df_equity["time"].diff().dropna().dt.total_seconds()
    median_step_seconds = time_diffs.median() if len(time_diffs) > 0 else np.nan

    if pd.notna(median_step_seconds) and median_step_seconds > 0:
        periods_per_year = (365 * 24 * 3600) / median_step_seconds
    else:
        periods_per_year = np.nan

    # ========= 4. 核心绩效指标 =========
    total_return = final_equity / initial_equity - 1

    total_seconds = (end_time - start_time).total_seconds()
    years = total_seconds / (365 * 24 * 3600)

    if years > 0 and final_equity > 0:
        annual_return = (final_equity / initial_equity) ** (1 / years) - 1
    else:
        annual_return = np.nan

    running_max = equity_series.cummax()
    drawdown_series = equity_series / running_max - 1
    max_drawdown = float(drawdown_series.min())

    if len(returns) > 1 and returns.std(ddof=1) > 0 and pd.notna(periods_per_year):
        rf_per_period = (1 + risk_free_rate) ** (1 / periods_per_year) - 1
        excess_returns = returns - rf_per_period
        sharpe = (excess_returns.mean() / excess_returns.std(ddof=1)) * math.sqrt(periods_per_year)
    else:
        sharpe = np.nan

    downside_returns = returns[returns < 0]
    if len(downside_returns) > 0 and pd.notna(periods_per_year):
        rf_per_period = (1 + risk_free_rate) ** (1 / periods_per_year) - 1
        excess_returns = returns - rf_per_period
        negative_excess = excess_returns[excess_returns < 0]
        if len(negative_excess) > 1 and negative_excess.std(ddof=1) > 0:
            sortino = (excess_returns.mean() / negative_excess.std(ddof=1)) * math.sqrt(periods_per_year)
        else:
            sortino = np.nan
    else:
        sortino = np.nan

    calmar = annual_return / abs(max_drawdown) if max_drawdown < 0 and pd.notna(annual_return) else np.nan

    # ========= 5. 交易统计 =========
    if trades is None:
        trades = []

    trade_series = pd.Series(pd.to_numeric(list(trades), errors="coerce")).dropna()
    trade_count = int(len(trade_series))

    if trade_count > 0:
        win_rate = float((trade_series > 0).sum() / trade_count)

        profits = trade_series[trade_series > 0]
        losses = -trade_series[trade_series < 0]

        avg_profit = float(profits.mean()) if not profits.empty else 0.0
        avg_loss = float(losses.mean()) if not losses.empty else 0.0
        profit_factor = float(profits.sum() / losses.sum()) if losses.sum() > 0 else np.inf
        r_r_ratio = float(avg_profit / avg_loss) if avg_loss > 0 else np.inf

        max_win_streak = max_loss_streak = 0
        current_win = current_loss = 0

        for t in trade_series:
            if t > 0:
                current_win += 1
                current_loss = 0
                max_win_streak = max(max_win_streak, current_win)
            elif t < 0:
                current_loss += 1
                current_win = 0
                max_loss_streak = max(max_loss_streak, current_loss)
    else:
        win_rate = np.nan
        avg_profit = 0.0
        avg_loss = 0.0
        profit_factor = np.nan
        r_r_ratio = np.nan
        max_win_streak = 0
        max_loss_streak = 0

    # ========= 6. 图表数据 =========
    x_data = df_equity["time"].dt.strftime("%Y-%m-%d %H:%M").tolist()
    y_data = df_equity["equity"].tolist()

    # ========= 7. 绘图 =========
    line_equity = (
        Line(init_opts=opts.InitOpts(width="1400px", height="650px", theme=ThemeType.LIGHT))
        .add_xaxis(x_data)
        .add_yaxis(
            series_name="净值曲线",
            y_axis=y_data,
            is_smooth=False,
            is_step=True,
            symbol="none",
            linestyle_opts=opts.LineStyleOpts(width=2),
            label_opts=opts.LabelOpts(is_show=False),
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(title=title),
            tooltip_opts=opts.TooltipOpts(trigger="axis"),
            xaxis_opts=opts.AxisOpts(type_="category", axislabel_opts=opts.LabelOpts(rotate=45)),
            yaxis_opts=opts.AxisOpts(is_scale=True),
            datazoom_opts=[
                opts.DataZoomOpts(type_="slider", xaxis_index=0),
                opts.DataZoomOpts(type_="inside", xaxis_index=0)
            ],
            toolbox_opts=opts.ToolboxOpts(),
            legend_opts=opts.LegendOpts(pos_top="5%"),
        )
    )

    line_equity.render(output_html_name)

    if auto_open:
        try:
            webbrowser.open("file://" + os.path.abspath(output_html_name))
        except Exception:
            pass

    # ========= 8. 指标汇总 =========
    metrics = {
        "start_time": start_time,
        "end_time": end_time,
        "duration_days": total_seconds / 86400,
        "initial_equity": initial_equity,
        "final_equity": final_equity,
        "total_return": total_return,
        "annual_return": annual_return,
        "max_drawdown": max_drawdown,
        "sharpe": sharpe,
        "sortino": sortino,
        "calmar": calmar,
        "trade_count": trade_count,
        "win_rate": win_rate,
        "avg_profit": avg_profit,
        "avg_loss": avg_loss,
        "profit_factor": profit_factor,
        "r_r_ratio": r_r_ratio,
        "max_win_streak": max_win_streak,
        "max_loss_streak": max_loss_streak,
        "periods_per_year": periods_per_year,
        "output_html": os.path.abspath(output_html_name),
        "utc_file_timestamp": utc_timestamp_str,
    }

    def fmt_pct(x):
        return "nan" if pd.isna(x) else f"{x:.2%}"

    def fmt_num(x):
        return "nan" if pd.isna(x) else f"{x:.4f}"

    print("\n========== 回测评估结果 ==========")
    print(f"回测时间: {start_time} ~ {end_time}")
    print(f"回测天数: {metrics['duration_days']:.2f}")
    print(f"起始净值: {initial_equity:.4f}")
    print(f"结束净值: {final_equity:.4f}")
    print(f"总收益率: {fmt_pct(total_return)}")
    print(f"年化收益率: {fmt_pct(annual_return)}")
    print(f"最大回撤: {fmt_pct(max_drawdown)}")
    print(f"夏普比率: {fmt_num(sharpe)}")
    print(f"Sortino比率: {fmt_num(sortino)}")
    print(f"Calmar比率: {fmt_num(calmar)}")
    print(f"交易次数: {trade_count}")
    print(f"胜率: {fmt_pct(win_rate)}")
    print(f"平均盈利金额: {avg_profit:.4f}")
    print(f"平均亏损金额: {avg_loss:.4f}")
    print(f"盈亏比: {fmt_num(r_r_ratio)}")
    print(f"Profit Factor: {fmt_num(profit_factor)}")
    print(f"最大连续盈利次数: {max_win_streak}")
    print(f"最大连续亏损次数: {max_loss_streak}")
    print(f"图表文件: {os.path.abspath(output_html_name)}")
    print("================================\n")

    return metrics