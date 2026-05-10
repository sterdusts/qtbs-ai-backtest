import os
from datetime import datetime, timezone

from pyecharts.charts import Line, Grid
from pyecharts import options as opts


def plot_generic_equity_curves(
    result: dict,
    output_dir: str = "Past_data",
    file_prefix: str = "generic_strategy",
    title: str = "通用策略净值曲线",
    auto_open: bool = True
):
    """
    绘制通用策略引擎双净值曲线：
    1. 实时权益曲线：包含持仓浮盈浮亏
    2. 已实现权益曲线：只在平仓后变化
    """

    os.makedirs(output_dir, exist_ok=True)

    utc_now = datetime.now(timezone.utc)
    utc_timestamp_str = utc_now.strftime("%Y-%m-%d_%H-%M-%S_UTC")

    output_html_name = os.path.join(
        output_dir,
        f"{file_prefix}_{utc_timestamp_str}.html"
    )

    equity_curve = result["equity_curve"]
    realized_equity_curve = result.get("realized_equity_curve", [])

    x_data = [item["time"] for item in equity_curve]
    floating_equity = [round(float(item["equity"]), 4) for item in equity_curve]

    if realized_equity_curve:
        realized_equity = [
            round(float(item["equity"]), 4)
            for item in realized_equity_curve
        ]
    else:
        realized_equity = []

    line = Line(
        init_opts=opts.InitOpts(
            width="1400px",
            height="850px"
        )
    )

    line.add_xaxis(x_data)

    line.add_yaxis(
        series_name="实时权益（含浮盈浮亏）",
        y_axis=floating_equity,
        is_smooth=False,
        is_symbol_show=False,
        label_opts=opts.LabelOpts(is_show=False),
    )

    if realized_equity:
        line.add_yaxis(
            series_name="已实现权益（平仓后更新）",
            y_axis=realized_equity,
            is_smooth=False,
            is_step=True,
            is_symbol_show=False,
            label_opts=opts.LabelOpts(is_show=False),
        )

    # 调标题大小、颜色、位置
    line.set_global_opts(
        title_opts=opts.TitleOpts(
            title=title,
            pos_left="center",
            pos_top="2%"
        ),

        legend_opts=opts.LegendOpts(
            pos_left="center",
            pos_top="8%"
        ),

        tooltip_opts=opts.TooltipOpts(
            trigger="axis"
        ),

        datazoom_opts=[
            opts.DataZoomOpts(
                type_="inside"
            ),
            opts.DataZoomOpts(
                type_="slider",
                pos_bottom="3%"
            ),
        ],

        xaxis_opts=opts.AxisOpts(
            type_="category",
            boundary_gap=False,
            axislabel_opts=opts.LabelOpts(
                rotate=0,
                margin=12
            )
        ),

        yaxis_opts=opts.AxisOpts(
            type_="value"
        ),
    )
    # 图表大小
    grid = Grid(
        init_opts=opts.InitOpts(
            width="1400px",
            height="850px"
        )
    )

    #pos_top      = 曲线区域距离顶部多远
    # pos_bottom  = 曲线区域距离底部多远
    # pos_left    = 曲线区域距离左边多远
    # pos_right   = 曲线区域距离右边多远
    grid.add(
        line,
        grid_opts=opts.GridOpts(
            pos_top="16%",
            pos_bottom="15%",
            pos_left="7%",
            pos_right="4%",
            is_contain_label=True
        )
    )

    grid.render(output_html_name)

    print(f"双净值曲线图已生成：{output_html_name}")

    if auto_open:
        import webbrowser
        webbrowser.open(output_html_name)

    return output_html_name