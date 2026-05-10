import pandas as pd
from module.modules.kline_builder import KlineBuilder
import os

def load_real_kline(symbol: str):
    """
    复用 main.py 的逻辑：
    1. 检查本地是否有 1min K线
    2. 没有就拉取
    3. 读取 CSV
    4. 构造多周期 K线
    """

    symbol = normalize_symbol(symbol)

    if has_kline_data(symbol):
        print(f"已获取 {symbol} 数据")
    else:
        print(f"正在拉取 {symbol} 数据")
        Obtain_K(symbol)

    file_path = get_kline_file_path(symbol)
    raw_df = pd.read_csv(file_path)

    print("原始数据读取完成")
    print(raw_df.head())
    print(raw_df.tail())

    builder = KlineBuilder(raw_df)

    print("正在构造K线")

    df_1m = builder.get_1m()
    df_5m = builder.build("5min")
    df_15m = builder.build("15min")
    df_1h = builder.build("1h")
    df_4h = builder.build("4h")
    df_1d = builder.build("1d")

    print("K线构造完成")

    return {
        "1m": df_1m,
        "5m": df_5m,
        "15m": df_15m,
        "1h": df_1h,
        "4h": df_4h,
        "1d": df_1d,
    }


def get_kline_file_path(
    symbol: str,
    interval: str = "1MIN",
    data_dir: str = "cryptocurrency_data/kline_data"
) -> str:
    symbol = normalize_symbol(symbol)

    file_name = f"{symbol}_{interval}_data.csv"
    file_path = os.path.join(data_dir, file_name)

    return file_path


def normalize_symbol(user_input: str, quote: str = "USDT") -> str:
    """
    把用户输入统一转换成交易对格式。
    btc      -> BTCUSDT
    BTC      -> BTCUSDT
    btcusdt  -> BTCUSDT
    BTCUSDT  -> BTCUSDT
    """

    symbol = user_input.strip().upper()

    if not symbol:
        raise ValueError("币种不能为空，请输入 BTC、ETH 这类币种。")

    if symbol.endswith(quote):
        return symbol

    return symbol + quote


def get_base_asset(symbol: str, quote: str = "USDT") -> str:
    """
    BTCUSDT -> BTC
    ETHUSDT -> ETH
    """

    symbol = normalize_symbol(symbol, quote)

    if symbol.endswith(quote):
        return symbol[:-len(quote)]

    return symbol


def Obtain_K(symbol: str):
    """
    拉取K线数据。

    注意：
    data_acquisition(stock=...) 接收 BTC / ETH 这种基础币种。
    如果它内部会自己拼接 USDT，这里就传 base_asset。
    """

    from cryptocurrency_data.obtain_K_data import data_acquisition

    base_asset = get_base_asset(symbol)
    data_acquisition(stock=base_asset)


def has_kline_data(
    symbol: str,
    interval: str = "1MIN",
    data_dir: str = "cryptocurrency_data/kline_data"
) -> bool:
    """
    检查本地是否存在某个币种的K线数据文件。
    """

    symbol = normalize_symbol(symbol)

    file_name = f"{symbol}_{interval}_data.csv"
    file_path = os.path.join(data_dir, file_name)

    return os.path.exists(file_path)
