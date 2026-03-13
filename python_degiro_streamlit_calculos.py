# %%
import pandas as pd
import numpy as np

import yfinance as yf
#import mplfinance as mpf

from datetime import datetime

from stock_data_functions import *	# ESTE ES EL OTRO ARCHIVO PY CON LAS FUNCIONES	

def obtener_datos_procesados():
    # %%
    # CARGAR EL FICHERO CSV DE DEGIRO Y CAMBIAR NOMBRES DE COLUMNAS

    path_hist = "INPUT/DEGIRO-CSV-ALL-HISTORY-2021-2024.csv"		# CARGA DE FICHERO HISTORICO
    path_new  = "INPUT/DEGIRO-CSV-2025.csv"		# CARGA DE FICHERO CON NUEVOS DATOS

    col_names = ["date", "col1", "col2", "movimiento", "col3", "description", "col4", "moneda", "importe", "col5", "col6", "col7"]

    df_hist = pd.read_csv(path_hist, sep=',', skiprows=1, names=col_names, decimal=".")
    df_new = pd.read_csv(path_new, sep=',', skiprows=1, names=col_names, decimal=",")

    # %%
    # SELECCIONAR COLUMNAS Y CAMBIAR DESCRIPCIONES POR NOMBRES DE STOCKS

    select_cols = ["date", "movimiento", "description", "importe", "moneda"]

    df_hist = df_hist[select_cols]
    df_new = df_new[select_cols]

    df_concat = [df_hist, df_new]

    df = pd.concat(df_concat, ignore_index=True)

    text_filters = ["Transferir desde su Cuenta de Efectivo",
                    "Ingreso Cambio de Divisa",
                    "Degiro Cash Sweep Transfer",
                    "Retirada Cambio de Divisa"
                    ]

    df = df[~df['description'].isnull()]
    df = df[~df['importe'].isnull()]

    for text in text_filters:								# <----------------- ACA HAY UN LOOP QUE PUEDE SER FUNCION
        df = df[~df['description'].str.contains(text)]

    # %%
    # AGREGAR LOS STOCKNAMES DE CADA MOVIMIENTO

    path_stocknames = "INPUT/stocknames.csv"		# CARGA DE FICHERO

    df_stocknames = pd.read_csv(path_stocknames, sep=";")

    values_stocks_names = df_stocknames["Producto"]
    values_stocks_newNames = df_stocknames["StockName"]

    map_stocks_name = values_stocks_names.tolist()
    map_stocks_newName = values_stocks_newNames.tolist()

    df["movimiento"].replace(map_stocks_name, map_stocks_newName, inplace=True)

    # %%
    # AGREGAR LOS STOCK TICKERS DE CADA MOVIMIENTO

    path_stockTickers = "INPUT/stock-tickers.csv"		# CARGA DE FICHERO

    df_stockTickers = pd.read_csv(path_stockTickers, sep=";")

    values_stockNames = df_stockTickers["StockName"]
    values_stocksTickers = df_stockTickers["Ticker_EV"]

    map_stockNames = values_stockNames.tolist()
    map_stockTickers = values_stocksTickers.tolist()

    df["ticker"] = df["movimiento"]

    df["ticker"].replace(map_stockNames, map_stockTickers, inplace=True)

    # %%
    # AGREGAR LOS TIPOS DE MOVIMIENTO Y NUEVAS COLUMNAS

    df = reemplazar_tipos(df)

    df['num_acciones'] = df['description'].str.extract(r'(Compra|Venta)\s+(\d+)')[1]
    df['price'] = df['description'].str.extract(r'@([\d,]+(?:\.\d{1,3})?)')[0]
    df['price'] = df['price'].str.replace(',', '.')

    # %%
    # CAMBIAR TIPOS DE COLUMNAS

    df['date'] = pd.to_datetime(df['date'], dayfirst=True, errors='coerce')

    df['importe'] = pd.to_numeric(df['importe'], errors='coerce')
    df['num_acciones'] = pd.to_numeric(df['num_acciones'], errors='coerce')
    df['price'] = pd.to_numeric(df['price'], errors='coerce')

    # %%
    # AGRUPAR MOVIMINETOS POR FECHA

    df = df.groupby(['date', 'ticker', 'tipo_movimiento']).agg({
        'movimiento': 'max',
        'importe': 'sum',
        'num_acciones': 'sum',
        'price': 'mean',
        'moneda': 'max',
        'description': 'max'
    }).reset_index()

    df_degiro = df.copy()

    # %%
    # CREAR DF'S DE COMPRA-VENTAS E IMPUESTOS-INTERESES

    df_compra_venta = df

    df_compra_venta = df_compra_venta[(df_compra_venta['tipo_movimiento'] == "VENTA ACCIONES") | (df_compra_venta['tipo_movimiento'] == "COMPRA ACCIONES")]

    df_comis_imp_int = df

    df_comis_imp_int = df_comis_imp_int[(df_comis_imp_int['tipo_movimiento'] == "COMISION") | (df_comis_imp_int['tipo_movimiento'] == "IMPUESTO") | (df_comis_imp_int['tipo_movimiento'] == "INTERESES")]

    # %%
    # DOWNLOAD DATA FROM WEB

    # GENERAL PARAMETERS

    # Get today's date
    today = datetime.today()
    date_today = today.strftime('%Y-%m-%d')
    date_start = '2021-07-01'

    ticker_list = df['ticker'].unique().tolist()
    ticker_list.remove("Deposito")
    ticker_list.remove("Gastos")

    # %%
    # DOWNLOAD YAHOO FINANCE DATA
    # DESCARGO LOS DATOS DE YF PARA TODAS LAS STOCKS DESDE 07/2021 HASTA FECHA DE HOY

    all_stock_data = pd.DataFrame()

    select_cols = ["date", "ticker", "Close", "Dividends", "Volume"]

    for ticker in ticker_list:				# <----------------- ACA HAY UN LOOP QUE PUEDE SER FUNCION								
        data = yf.Ticker(ticker)
        data_hist = data.history(start=date_start, end=date_today)
        data_hist['ticker'] = ticker
        data_hist['date'] = data_hist.index
        data_hist['date'] = pd.to_datetime(data_hist['date'])
        data_hist['date'] = data_hist['date'].dt.strftime('%Y-%m-%d')
        data_hist = data_hist[select_cols]
        all_stock_data = pd.concat([all_stock_data, data_hist], ignore_index=True)

    all_stock_data['date'] = pd.to_datetime(all_stock_data['date'])

    # %%
    # CALCULAR POSICIONES
    # CALCULO CUANTAS ACCIONES TENGO CADA DIA PARA CADA TICKER

    portfolio_data = pd.DataFrame()

    df_new = df

    for ticker in ticker_list:				# <----------------- ACA HAY UN LOOP QUE PUEDE SER FUNCION
        df = df_new
        df = df[df['ticker'] == ticker]
        df = df[df['num_acciones'] != 0]

        df['cambio_acciones'] = df.apply(acciones_venta_compra, axis=1)
        df['pos_portfolio'] = df['cambio_acciones'].cumsum()

        select_cols = ["date", "ticker", "movimiento", "cambio_acciones", "pos_portfolio"]
        df = df[select_cols]

        date_range = pd.date_range(start=date_start, end=date_today, freq='D')
        date_range = pd.DataFrame(date_range, columns=['date'])

        merged_df = pd.merge(date_range, df, on='date', how='left')

        merged_df['pos_portfolio'] = merged_df['pos_portfolio'].fillna(method='ffill')
        merged_df['pos_portfolio'] = merged_df['pos_portfolio'].fillna(0)

        merged_df['ticker'] = merged_df['ticker'].fillna(method='ffill')

        portfolio_data = pd.concat([portfolio_data, merged_df], ignore_index=True)


    date_range = pd.date_range(start=date_start, end=date_today, freq='D')		
    date_range = pd.DataFrame(date_range, columns=['date'])		

    # %%
    # UNIR YAHOO DATA CON LAS POSICIONES
    # PARA CADA POSICION LE UNO LOS DATOS DE LA COTIZACION DE ESE DIA PARA CADA TICKER

    merged_df = pd.merge(portfolio_data, all_stock_data, on=['date', 'ticker'], how='left')

    df_currency = df_new[(df_new['tipo_movimiento'] == "VENTA ACCIONES") | (df_new['tipo_movimiento'] == "COMPRA ACCIONES")]

    df_currency = df_currency.groupby(['ticker']).agg({
        'moneda': 'max'
    }).reset_index()

    merged_df_final = pd.merge(merged_df, df_currency, on=['ticker'], how='left')
    merged_df_final['Close'] = merged_df_final['Close'].fillna(method='ffill')

    # %%
    # GET FX INFO
    # DESCARGO LOS DATOS DE FX DESDE YAHOO

    ticker_eur = ["EUR=X"]

    eur_to_usd = pd.DataFrame()

    select_cols = ["date", "Close"]

    for ticker in ticker_eur:			# <----------------- ACA HAY UN LOOP QUE PUEDE SER FUNCION
        data = yf.Ticker(ticker)
        data_hist = data.history(start=date_start, end=date_today)
        data_hist['ticker'] = ticker
        data_hist['date'] = data_hist.index
        data_hist['date'] = pd.to_datetime(data_hist['date'])
        data_hist['date'] = data_hist['date'].dt.strftime('%Y-%m-%d')
        data_hist = data_hist[select_cols]
        data_hist = data_hist.rename(columns={"Close": "fx_rate"})
        eur_to_usd = pd.concat([eur_to_usd, data_hist], ignore_index=True)

    eur_to_usd['date'] = pd.to_datetime(eur_to_usd['date'])

    # %%
    # AL ULTIMO DF LE UNO TAMBIEN LA TABLA CON EL FX
    # TAMBIEN CALCULO EL IMPORTE EN EUROS PARA CADA POSICION Y PARA CADA DIA

    merged_df_final_FX = pd.merge(merged_df_final, eur_to_usd, on=['date'], how='left')

    merged_df_final_FX['fx_rate'] = merged_df_final_FX['fx_rate'].fillna(method='ffill')

    merged_df_final_FX['importe_EUR'] = merged_df_final_FX.apply(acciones_fxrate, axis=1)

    #print(merged_df_final_FX.head())

    merged_df_final_FX = merged_df_final_FX.groupby(['date', 'ticker', 'movimiento'], dropna=False).agg({
        'pos_portfolio': 'max',
        'Close': 'max',
        'moneda': 'max',
        'fx_rate': 'max',
        'importe_EUR': 'sum'
    }).reset_index()

    round_cols = ['Close', 'fx_rate', 'importe_EUR']

    merged_df_final_FX = round_columns(merged_df_final_FX, round_cols)

    # %%
    # -----------------------------------------------------------------------------------------------------------------
    # --------------------------------------CONSTRUIR DF CON TODOS LOS DATOS DE POSICION ------------------------------
    # -----------------------------------------------------------------------------------------------------------------

    # GET DIVIDENDOS 	-----------------------------------------------------------------------------------------------

    df_dividendos = df_new[(df_new['tipo_movimiento'] == "DIVIDENDO")]

    df_dividendos = pd.merge(df_dividendos, eur_to_usd, on=['date'], how='left')

    df_dividendos['importe_EUR'] = df_dividendos.apply(dividendos_fxrate, axis=1)

    select_cols = ["date", "ticker", "tipo_movimiento", "moneda", "importe_EUR"]

    df_dividendos = df_dividendos[select_cols]


    # GET DEPOSITOS --------------------------------------------------------------------------------------------------

    df_depositos = df_new[(df_new['tipo_movimiento'] == "DEPOSITOS")]

    df_depositos = df_depositos.rename(columns={"importe": "importe_EUR"})

    select_cols = ["date", "ticker", "tipo_movimiento", "moneda", "importe_EUR"]

    df_depositos = df_depositos[select_cols]

    df_dividendos = df_dividendos.groupby(["date", "tipo_movimiento"]).agg({
        'importe_EUR': 'sum'
    }).reset_index()


    # GET SALDOS DIARIOS --------------------------------------------------------------------------------------------------

    df_saldos_diarios = df_new

    df_saldos_diarios = pd.merge(df_saldos_diarios, eur_to_usd, on=['date'], how='left')

    df_saldos_diarios['importe_EUR'] = df_saldos_diarios.apply(dividendos_fxrate, axis=1)

    df_saldos_diarios = df_saldos_diarios.groupby(['date']).agg({
        'importe_EUR': 'sum'
    }).reset_index()

    df_saldos_diarios['saldo'] = df_saldos_diarios['importe_EUR'].cumsum()
    df_saldos_diarios['tipo_movimiento'] = 'saldo_diario'

    select_cols = ["date", "tipo_movimiento", "importe_EUR", "saldo"]

    df_saldos_diarios = df_saldos_diarios[select_cols]

    # ------------------------------------------------------------------------------------------------------

    df_posiciones = merged_df_final_FX

    df_posiciones['tipo_movimiento'] = 'POSICION'

    df_posiciones = df_posiciones.groupby(['date', 'tipo_movimiento']).agg({
        'importe_EUR': 'sum'
    }).reset_index()

    # ------------------------------------------------------------------------------------------------------

    df_compra_venta = pd.merge(date_range, df_compra_venta, on=['date'], how='left')
    df_compra_venta = pd.merge(df_compra_venta, eur_to_usd, on=['date'], how='left')
    df_compra_venta['importe_EUR'] = df_compra_venta.apply(compra_venta_fxrate, axis=1)

    df_compras = df_compra_venta[df_compra_venta['tipo_movimiento'] == "COMPRA ACCIONES"]
    df_compras = df_compras.groupby(["date", "tipo_movimiento"]).agg({
        'importe_EUR': 'sum'
    }).reset_index()

    df_ventas = df_compra_venta[df_compra_venta['tipo_movimiento'] == "VENTA ACCIONES"]
    df_ventas = df_ventas.groupby(["date", "tipo_movimiento"]).agg({
        'importe_EUR': 'sum'
    }).reset_index()

    # ------------------------------------------------------------------------------------------------------

    df_comis_imp_int = pd.merge(date_range, df_comis_imp_int, on=['date'], how='left')
    df_comis_imp_int = pd.merge(df_comis_imp_int, eur_to_usd, on=['date'], how='left')
    df_comis_imp_int['importe_EUR'] = df_comis_imp_int.apply(compra_venta_fxrate, axis=1)

    df_comision = df_comis_imp_int[df_comis_imp_int['tipo_movimiento'] == "COMISION"]
    df_comision = df_comision.groupby(["date", "tipo_movimiento"]).agg({
        'importe_EUR': 'sum'
    }).reset_index()

    df_impuestos = df_comis_imp_int[df_comis_imp_int['tipo_movimiento'] == "IMPUESTO"]
    df_impuestos = df_impuestos.groupby(["date", "tipo_movimiento"]).agg({
        'importe_EUR': 'sum'
    }).reset_index()

    df_intereses = df_comis_imp_int[df_comis_imp_int['tipo_movimiento'] == "INTERESES"]
    df_intereses = df_intereses.groupby(["date", "tipo_movimiento"]).agg({
        'importe_EUR': 'sum'
    }).reset_index()

    # %%
    #------------------------------------------------------------------------------------------------------
    #------------------------ PREPARACION ULTIMO DF CON TODAS LAS TABLAS DE DATOS -------------------------
    #------------------------------------------------------------------------------------------------------

    df_final = pd.DataFrame()

    all_df = [df_depositos, df_compras, df_ventas, df_dividendos, df_comision, df_impuestos, df_intereses, df_posiciones, df_saldos_diarios]

    count = 0

    for df in all_df:
        col = 'col' + str(count)
        df = df.rename(columns={"importe_EUR": col})
        select_cols = ['date', col]
        df = df[select_cols]
        #df_final = pd.concat([df_final, df], axis=0, ignore_index=True)
        date_range = pd.merge(date_range, df, on='date', how='left')
        count += 1

    cols_dict = {'col0': 'depositos',
                'col1': 'compras',
                'col2': 'ventas',
                'col3': 'dividendos',
                'col4': 'comisiones',
                'col5': 'impuestos',
                'col6': 'intereses',
                'col7': 'posiciones'}
    
    date_range.rename(columns=cols_dict,
            inplace=True)

    # %%
    #--------------- CALCULO DE SALDOS -------------------------

    date_range = date_range.fillna(0)
    date_range['saldo_diario_raw'] = date_range['depositos'] + date_range['compras'] + date_range['ventas'] + date_range['dividendos'] + date_range['comisiones'] + date_range['impuestos'] + date_range['intereses']
    date_range['saldo_diario_acc'] = date_range['saldo_diario_raw'].cumsum()


    table_acc = {
        'date': ['2021-07-01'],
        'acciones': [0.0001],
    }

    df_acciones = pd.DataFrame(data=table_acc)
    df_acciones['date'] = pd.to_datetime(df_acciones['date'])

    # %%
    #-------------------- CALCULO DE ACCIONES -----------------------------------------------------------------------

    date_range = pd.merge(date_range, df_acciones, on='date', how='left')
    date_range['acciones'] = date_range['acciones'].fillna(0)

    date_range = calculo_acciones(date_range)
    date_range['acc_price'] = date_range.apply(acciones_price, axis=1)

    date_range = date_range[date_range['acc_price'] > 0]

    date_range['saldo'] = date_range['posiciones'] + date_range['saldo_diario_acc']

    date_range['saldo_change'] = date_range['saldo'].diff()
    date_range['saldo_change_perc'] = date_range['saldo'].pct_change() * 100

    date_range['saldo_pos_change'] = date_range['posiciones'].diff()
    date_range['saldo_pos_change_perc'] = date_range['posiciones'].pct_change() * 100

    round_cols = ['saldo_diario_acc', 'acciones', 'acc_price', 'saldo', 'saldo_change', 'saldo_change_perc', 'saldo_pos_change', 'saldo_pos_change_perc']

    date_range = round_columns(date_range, round_cols)

    # %%
    # DATOS DEGIRO CON COLUMNA IMPORTE CON FX RATE CORRESPONDIENTE

    df_degiro['date'] = pd.to_datetime(df_degiro['date'])

    df_degiro = pd.merge(df_degiro, eur_to_usd, on=['date'], how='left')

    df_degiro['fx_rate'] = df_degiro['fx_rate'].fillna(method='ffill')

    df_degiro['importe_EUR'] = df_degiro.apply(dividendos_fxrate, axis=1)
    df_degiro['price_EUR'] = df_degiro.apply(price_acciones_fx, axis=1)

    round_cols = ['fx_rate', 'importe_EUR', 'price_EUR']

    df_degiro = round_columns(df_degiro, round_cols)

    # %%
    #CALCULO DE PROFIT POR COMPRA-VENTAS DE ACCIONES

    df_compra_venta = df_degiro[(df_degiro['tipo_movimiento'] == "VENTA ACCIONES") | (df_degiro['tipo_movimiento'] == "COMPRA ACCIONES")]

    df = df_compra_venta

    # Ensure Date column is datetime
    df['date'] = pd.to_datetime(df['date'])

    # Initialize an empty DataFrame for the new table
    result = []

    # Dictionary to track inventory
    inventory = {}

    # Process each transaction
    for _, row in df.iterrows():
        stock = row['ticker']
        t_type = row['tipo_movimiento']
        date = row['date']
        quantity = row['num_acciones']
        price = row['price_EUR']

        if t_type == 'COMPRA ACCIONES':
            # Add to inventory
            if stock not in inventory:
                inventory[stock] = []
            inventory[stock].append({'Quantity': quantity, 'Price': price})
        elif t_type == 'VENTA ACCIONES':
            # Match the sell with inventory
            remaining = quantity
            profit = 0
            while remaining > 0 and inventory[stock]:
                batch = inventory[stock][0]
                if batch['Quantity'] <= remaining:
                    # Use the entire batch
                    profit += batch['Quantity'] * (price - batch['Price'])
                    remaining -= batch['Quantity']
                    inventory[stock].pop(0)  # Remove the used batch
                else:
                    # Partially use the batch
                    profit += remaining * (price - batch['Price'])
                    batch['Quantity'] -= remaining
                    remaining = 0

            # Add a row to the result table
            result.append({
                'Stock': stock,
                'Date': date,
                'Quantity Sold': quantity,
                'Profit': profit
            })

    # Create the result DataFrame
    buy_sell_profit_df = pd.DataFrame(result)

    # %%
    # CALCULO MIS POSICIONES ACTUALES CON SUS RESPECTIVOS COSTOS MEDIOS PONDERADOS

    df_compra_venta = df_degiro[(df_degiro['tipo_movimiento'] == "VENTA ACCIONES") | (df_degiro['tipo_movimiento'] == "COMPRA ACCIONES")]

    df = df_compra_venta

    # Ensure Date column is datetime
    df['date'] = pd.to_datetime(df['date'])

    # Dictionary to track inventory
    inventory = {}

    # Process each transaction
    for _, row in df.iterrows():
        stock = row['ticker']
        t_type = row['tipo_movimiento']
        quantity = row['num_acciones']
        price = row['price']

        if stock not in inventory:
            inventory[stock] = {'total_quantity': 0, 'total_cost': 0, 'closed': False}

        if t_type == 'COMPRA ACCIONES':
            # If the position was previously closed, reopen it
            inventory[stock]['closed'] = False
            # Update total cost and quantity
            inventory[stock]['total_quantity'] += quantity
            inventory[stock]['total_cost'] += quantity * price

        elif t_type == 'VENTA ACCIONES':
            remaining = quantity
            avg_cost = inventory[stock]['total_cost'] / inventory[stock]['total_quantity'] \
                if inventory[stock]['total_quantity'] > 0 else 0

            # Deduct sold quantity and adjust cost
            if remaining <= inventory[stock]['total_quantity']:
                inventory[stock]['total_quantity'] -= remaining
                inventory[stock]['total_cost'] -= remaining * avg_cost

            # If all positions are closed, mark the position as closed
            if inventory[stock]['total_quantity'] == 0:
                inventory[stock]['total_cost'] = 0
                inventory[stock]['closed'] = True

    # Create a DataFrame with only open positions
    current_positions = [
        {
            'Stock': stock,
            'Total Quantity': info['total_quantity'],
            'Average Cost': round(info['total_cost'] / info['total_quantity'], 2) if info['total_quantity'] > 0 else 0
        }
        for stock, info in inventory.items()
        if not info['closed'] and info['total_quantity'] > 0
    ]

    current_positions_df = pd.DataFrame(current_positions)

    # %%
    # EXPORT CSV FILES ----------------------------------------------

    #path_out_01 = "OUTPUT/DEGIRO-CSV-ALL.csv"		# EXPORTAR FICHERO
    #df_degiro.to_csv(path_out_01)

    path_out_01 = df_degiro.copy()

    #path_out_02 = "OUTPUT/DEGIRO-CSV-PORTFOLIO-DF_FINAL_TICKER.csv"
    #merged_df_final_FX.to_csv(path_out_02)

    path_out_02 = merged_df_final_FX.copy()

    #path_out_03 = "OUTPUT/DEGIRO-CSV-PORTFOLIO-DF_FINAL.csv"
    #date_range.to_csv(path_out_03)

    path_out_03 = date_range.copy()

    #path_out_04 = "OUTPUT/DEGIRO-CSV-ALL_STOCK_DATA.csv"
    #all_stock_data.to_csv(path_out_04)

    path_out_04 = all_stock_data.copy()

    #path_out_05 = "OUTPUT/DEGIRO-CSV-BUY_SELL_PROFIT.csv"
    #buy_sell_profit_df.to_csv(path_out_05)

    path_out_05 = buy_sell_profit_df.copy()

    #path_out_06 = "OUTPUT/DEGIRO-CURRENT-PORTFOLIO-AVG-COST.csv"
    #current_positions_df.to_csv(path_out_06)

    path_out_06 = current_positions_df.copy()

    #path_out_07 = "OUTPUT/FX-RATES-DATA.csv"
    #eur_to_usd.to_csv(path_out_07)

    path_out_07 = eur_to_usd.copy()

    return path_out_01, path_out_02, path_out_03, path_out_04, path_out_05, path_out_06, path_out_07

if __name__ == "__main__":
    obtener_datos_procesados()


