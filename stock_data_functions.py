import pandas as pd
import numpy as np

import yfinance as yf
#import mplfinance as mpf

from datetime import datetime

# FUNCION REEMPLAZAR TIPOS DE MOVIMIENTO

replace_dict = {
	"Venta": "VENTA ACCIONES",
	"Compra": "COMPRA ACCIONES",
	"Tax": "IMPUESTO",
	"Retención del dividendo": "IMPUESTO",
	"Costes": "COMISION",
	"Comisión": "COMISION",
	"Fee": "COMISION",
	"Deposit": "DEPOSITOS",
	"Dividendo": "DIVIDENDO",
	"Interest": "INTERESES",
	"Interés": "INTERESES"
}

def reemplazar_tipos(df):
					
	for key, value in replace_dict.items():																	
	  ventas_stocks = df['description'].str.contains(key)
	  df.loc[ventas_stocks, ["tipo_movimiento"]] = value
	
	replace_depositos_mov = df['description'].str.contains("Deposit")
	df.loc[replace_depositos_mov, ["movimiento"]] = "Deposito"

	replace_depositos_tick = df['description'].str.contains("Deposit")
	df.loc[replace_depositos_tick, ["ticker"]] = "Deposito"

	replace_gastos = df['tipo_movimiento'].str.contains("COMISION")
	df.loc[replace_gastos, ["ticker"]] = "Gastos"

	replace_gastos = df['tipo_movimiento'].str.contains("INTERESES")
	df.loc[replace_gastos, ["ticker"]] = "Gastos"

	replace_gastos = df['tipo_movimiento'].str.contains("IMPUESTO")
	df.loc[replace_gastos, ["ticker"]] = "Gastos"

	return df

#------------------------------------------------------------------------------------------------------------------------------------------


def acciones_venta_compra(row):					# <----------------- FUNCION PARA USAR DENTRO DE LOOP
    if row['tipo_movimiento'] == "VENTA ACCIONES":
        return row['num_acciones'] * -1
    elif row['tipo_movimiento'] == "COMPRA ACCIONES":
    	return row['num_acciones'] * 1
    else:
        return 0


#------------------------------------------------------------------------------------------------------------------------------------------

def acciones_fxrate(row):									# <----------------- FUNCION PARA USAR DENTRO DE LOOP
    if row['moneda'] == "EUR":
        return row['pos_portfolio'] * row['Close']
    elif row['moneda'] == "USD":
    	return row['pos_portfolio'] * row['Close'] * row['fx_rate']
    else:
        return 0


#------------------------------------------------------------------------------------------------------------------------------------------

def acciones_fxrate(row):
    if row["moneda"] == "EUR":
        return row["importe"]
    elif row["moneda"] in ["USD", "DKK"]:
        return row["importe"] / row["fx_rate"]
    else:
        return np.nan

#------------------------------------------------------------------------------------------------------------------------------------------

def price_acciones_fx(row):					# <----------------- FUNCION PARA USAR DENTRO DE LOOP
    if row['moneda'] == "EUR":
        return row['price'] * 1
    elif row['moneda'] == "USD":
    	return row['price'] * row['fx_rate']
    else:
        return 0

#------------------------------------------------------------------------------------------------------------------------------------------

def compra_venta_fxrate(row):									# <----------------- FUNCION PARA USAR DENTRO DE LOOP
    if row['moneda'] == "EUR":
        return row['importe']
    elif row['moneda'] == "USD":
    	return row['importe'] * row['fx_rate']
    else:
        return 0

#------------------------------------------------------------------------------------------------------------------------------------------

def calculo_acciones(df):
    for i in range(1, len(df)):
        if df.at[i, 'depositos'] == 0:
            df.at[i, 'acciones'] = df.at[i-1, 'acciones']
        else:
            if df.at[i-1, 'acciones'] == 0:
                df.at[i, 'acciones'] = df.at[i-1, 'acciones']
            else:
                if df.at[i, 'date'] == pd.to_datetime('2021-07-27'):
                    value_per_share = (df.at[i, 'posiciones'] + df.at[i, 'saldo_diario_acc']) / 50
                    new_shares = df.at[i, 'depositos'] / value_per_share
                    df.at[i, 'acciones'] = new_shares
                else:
                    value_per_share = (df.at[i-1, 'posiciones'] + df.at[i-1, 'saldo_diario_acc']) / df.at[i-1, 'acciones']
                    new_shares = df.at[i, 'depositos'] / value_per_share
                    df.at[i, 'acciones'] = df.at[i-1, 'acciones'] + new_shares
    return df

#------------------------------------------------------------------------------------------------------------------------------------------

def acciones_price(row):									# <----------------- FUNCION PARA USAR DENTRO DE LOOP
	if row['posiciones'] == 0:
	    return 0
	else:
		return (row['posiciones'] + row['saldo_diario_acc']) / row['acciones']


#------------------------------------------------------------------------------------------------------------------------------------------

def round_columns(df, round_cols):
	
	for column in round_cols:
		df[column] = df[column].apply(lambda x: round(x, 2))

	return df