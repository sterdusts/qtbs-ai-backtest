def adapt_generic_result_to_old_visualizer(result: dict):
    """
    把 GenericStrategyEngine 的结果转换成旧 evaluate_backtest_results 可用格式。

    重点：
    evaluate_backtest_results 里的 trades 参数需要的是“数值列表”，
    不是交易记录字典列表。

    所以：
    - trades = [每笔交易的 pnl_pct]
    - trade_records = 完整交易记录
    """

    equity_timestamps = [
        item["time"] for item in result["equity_curve"]
    ]

    equity_curve = [
        item["equity"] for item in result["equity_curve"]
    ]

    # 旧可视化函数统计交易次数、胜率、盈亏比时，需要数值序列
    trades = [
        float(trade["pnl_pct"])
        for trade in result["trades"]
        if trade.get("pnl_pct") is not None
    ]

    # 完整交易记录保留给后续图表标注 / 表格展示
    trade_records = []

    for trade in result["trades"]:
        trade_records.append({
            "entry_signal_time": trade.get("entry_signal_time"),
            "entry_time": trade.get("entry_time"),
            "entry_price": trade.get("entry_price"),
            "exit_signal_time": trade.get("exit_signal_time"),
            "exit_time": trade.get("exit_time"),
            "exit_price": trade.get("exit_price"),
            "pnl_pct": trade.get("pnl_pct"),
            "exit_reason": trade.get("exit_reason")
        })

    return equity_timestamps, equity_curve, trades, trade_records