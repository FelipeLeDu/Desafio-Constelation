import yfinance as yf 
import bcb as sgs 
import pandas as pd
from functools import reduce
from datetime import timedelta, datetime

def df_yf(ticker_datas: dict, variacao=True) -> pd.DataFrame: #vai receber um dicionário com os tickers e as datas de início e fim
    frames = []
    for ticker, (start, end) in ticker_datas.items(): # loop por cada ativo e suas datas
        df = yf.download(ticker, start=start, end=end) # baixar os dados do yahoo finance
        if df.empty: # pular ativos sem dados
            print(f"Nenhum dado encontrado para {ticker}")
            continue
        df = df[["Close"]].copy() # trabalhar com o preço de fechamento
        df.rename(columns={"Close": f"{ticker}_preco"}, inplace=True) # renomear a coluna para o ticker_preço
        if variacao: # calcular a variação percentual se solicitado (true)
            df[f"{ticker}_var_pct"] = df[f"{ticker}_preco"].pct_change() * 100
        df["Ticker"] = ticker
        df.reset_index(inplace=True)
        frames.append(df) #adicionar o DataFrame à lista de frames

    result = reduce(lambda left, right: pd.merge(left, right, on="Date", how="outer"), frames)
    return result

def baixar_variaveis_bcb(series: dict, start: str, end: str) -> pd.DataFrame: # API só aceita 10 anos de dados por vez

    start_date = pd.to_datetime(start)
    end_date = pd.to_datetime(end)
    max_range = timedelta(days=365 * 10 - 1)  # 10 anos menos 1 dia

    dfs = []

    while start_date < end_date:
        next_end = min(start_date + max_range, end_date)
        df_parcial = sgs.get(series, start=start_date.strftime('%Y-%m-%d'), end=next_end.strftime('%Y-%m-%d'))
        dfs.append(df_parcial)
        start_date = next_end + timedelta(days=1)

    df_final = pd.concat(dfs)
    df_final.reset_index(inplace=True)
    return df_final
