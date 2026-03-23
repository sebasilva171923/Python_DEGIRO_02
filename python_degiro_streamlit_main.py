# %%
import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime
from stock_data_functions import *
from python_degiro_streamlit_calculos import obtener_datos_procesados
import plotly.graph_objects as go
import io
import zipfile

# %%
st.title("📊 Mi App Streamlit")

# ---------------------------------------------------------------
# CARGA DE DATOS
# ---------------------------------------------------------------
@st.cache_data
def cargar_datos():
    return obtener_datos_procesados()

@st.cache_data
def generar_zip_csv(dataframes_dict):
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for nombre_archivo, df in dataframes_dict.items():
            csv_bytes = df.to_csv(index=False).encode("utf-8")
            zf.writestr(nombre_archivo, csv_bytes)

    zip_buffer.seek(0)
    return zip_buffer.getvalue()

df1, df2, df3, df4, df5, df6, df7 = cargar_datos()

df_degiro = df1
df_portfolio_ticker = df2
portfolio = df3
all_stocks = df4
buy_sell_profit_df = df5
current_positions_df = df6
eur_to_usd = df7

# ---------------------------------------------------------------
# DESCARGA DE CSVs
# ---------------------------------------------------------------
csv_files = {
    "DEGIRO-CSV-ALL.csv": df_degiro,
    "DEGIRO-CSV-PORTFOLIO-DF_FINAL_TICKER.csv": df_portfolio_ticker,
    "DEGIRO-CSV-PORTFOLIO-DF_FINAL.csv": portfolio,
    "DEGIRO-CSV-ALL_STOCK_DATA.csv": all_stocks,
    "DEGIRO-CSV-BUY_SELL_PROFIT.csv": buy_sell_profit_df,
    "DEGIRO-CURRENT-PORTFOLIO-AVG-COST.csv": current_positions_df,
    "FX-RATES-DATA.csv": eur_to_usd,
}

zip_data = generar_zip_csv(csv_files)

st.download_button(
    label="📥 Descargar todos los CSV en ZIP",
    data=zip_data,
    file_name="degiro_output_csvs.zip",
    mime="application/zip"
)

# ---------------------------------------------------------------
# PALETA DE COLORES Y ESTILO
# ---------------------------------------------------------------
COLOR_PRINCIPAL = "#0046FF"  # Azul corporativo
COLOR_SECUNDARIO = "#FF9013"  # Naranja corporativo
COLOR_BORDE = "rgba(80,80,80,0.4)"  # Borde gris oscuro sutil
COLOR_AUX1 = "#73C8D2"  # Azul claro
COLOR_AUX2 = "#F5F1DC"  # Beige claro
HOVER_BG = "rgba(40,40,40,0.85)"
HOVER_FONT = dict(color="white", size=13)

# ---------------------------------------------------------------
# FUNCIONES DE GRÁFICOS
# ---------------------------------------------------------------

def plot_portfolio_trend(portfolio):
    portfolio['date'] = pd.to_datetime(portfolio['date'])
    dates_num = (portfolio['date'] - portfolio['date'].min()).dt.days
    trend_params = np.polyfit(dates_num, portfolio['acc_price'], 1)
    portfolio['trend_line'] = np.polyval(trend_params, dates_num)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=portfolio['date'],
        y=portfolio['acc_price'],
        mode='lines',
        name='Portfolio',
        line=dict(color=COLOR_PRINCIPAL, width=2.5),
        hovertemplate='<b>%{x|%d %b %Y}</b><br>Valor: %{y:,.2f} €<extra></extra>'
    ))
    fig.add_trace(go.Scatter(
        x=portfolio['date'],
        y=portfolio['trend_line'],
        mode='lines',
        name='Tendencia',
        line=dict(color=COLOR_SECUNDARIO, width=2, dash='dash'),
        hovertemplate='<b>%{x|%d %b %Y}</b><br>Tendencia: %{y:,.2f} €<extra></extra>'
    ))

    fig.update_layout(
        title=dict(text="Evolución y Tendencia LP", x=0.5, xanchor='center', font=dict(size=18)),
        xaxis=dict(title="Fecha", rangeslider=dict(visible=True), tickformat="%b %Y", tickangle=-45),
        yaxis=dict(title="Valor (€)", gridcolor='rgba(200,200,200,0.3)'),
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='center', x=0.5),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        hoverlabel=dict(bgcolor=HOVER_BG, font=HOVER_FONT),
        margin=dict(t=80, b=60, l=60, r=40),
        shapes=[dict(type="rect", xref="paper", yref="paper", x0=0, y0=0, x1=1, y1=1,
                     line=dict(color=COLOR_BORDE, width=1))]
    )
    st.plotly_chart(fig, use_container_width=True)


def plot_portfolio_data(portfolio, all_stocks):
    ticker = 'VUSA.MI'
    compare_stock = all_stocks[all_stocks['ticker'] == ticker].copy()
    compare_stock['date'] = pd.to_datetime(compare_stock['date'])
    portfolio['date'] = pd.to_datetime(portfolio['date'])

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=portfolio['date'],
        y=portfolio['acc_price'],
        name='Portfolio',
        yaxis='y1',
        line=dict(color=COLOR_PRINCIPAL, width=2.5),
        hovertemplate='<b>%{x|%d %b %Y}</b><br>Portfolio: %{y:,.2f} €<extra></extra>'
    ))
    fig.add_trace(go.Scatter(
        x=compare_stock['date'],
        y=compare_stock['Close'],
        name='S&P 500',
        yaxis='y2',
        line=dict(color=COLOR_SECUNDARIO, width=2),
        hovertemplate='<b>%{x|%d %b %Y}</b><br>S&P 500: %{y:,.2f} €<extra></extra>'
    ))

    fig.update_layout(
        title=dict(text="Comparativa versus S&P 500", x=0.5, xanchor='center', font=dict(size=18)),
        xaxis=dict(title="Fecha", rangeslider=dict(visible=True), tickformat="%b %Y", tickangle=-45),
        yaxis=dict(title="Portfolio (€)", side="left", gridcolor='rgba(200,200,200,0.3)'),
        yaxis2=dict(title="S&P 500 (€)", side="right", overlaying='y', showgrid=False),
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='center', x=0.5),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        hoverlabel=dict(bgcolor=HOVER_BG, font=HOVER_FONT),
        margin=dict(t=80, b=60, l=60, r=40),
        shapes=[dict(type="rect", xref="paper", yref="paper", x0=0, y0=0, x1=1, y1=1,
                     line=dict(color=COLOR_BORDE, width=1))]
    )
    st.plotly_chart(fig, use_container_width=True)


def plot_dividends_by_company(df_degiro):
    df_dividends = df_degiro[df_degiro['tipo_movimiento'] == 'DIVIDENDO'].copy()
    df_dividends['date'] = pd.to_datetime(df_dividends['date'])
    df_sum = df_dividends.groupby('ticker')['importe_EUR'].sum().reset_index()
    df_sum = df_sum.sort_values(by='importe_EUR', ascending=False)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df_sum['ticker'],
        y=df_sum['importe_EUR'],
        text=[f"{v:,.0f} €" for v in df_sum['importe_EUR']],
        textposition='outside',
        marker=dict(color=COLOR_PRINCIPAL, line=dict(color=COLOR_PRINCIPAL, width=1.2)),
        hovertemplate='<b>%{x}</b><br>Dividendos: %{y:,.2f} €<extra></extra>',
        name="Dividendos"
    ))
    fig.update_layout(
        title=dict(text="Dividendos por Compañía (Euros)", x=0.5, xanchor='center', font=dict(size=18)),
        xaxis=dict(title="Ticker", tickangle=-60, tickfont=dict(size=10), showgrid=False),
        yaxis=dict(title="Total Importe (€)", gridcolor='rgba(200,200,200,0.3)'),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        hoverlabel=dict(bgcolor=HOVER_BG, font=HOVER_FONT),
        margin=dict(t=80, b=100, l=60, r=40),
        shapes=[dict(type="rect", xref="paper", yref="paper", x0=0, y0=0, x1=1, y1=1,
                     line=dict(color=COLOR_BORDE, width=1))]
    )
    st.plotly_chart(fig, use_container_width=True)


def plot_dividends_evolution(df_degiro):
    df_dividends = df_degiro[df_degiro['tipo_movimiento'] == 'DIVIDENDO'].copy()
    df_dividends['date'] = pd.to_datetime(df_dividends['date'])
    df_dividends['year_quarter'] = df_dividends['date'].dt.to_period('Q').astype(str)
    df_grouped = df_dividends.groupby('year_quarter', as_index=False)['importe_EUR'].sum()
    df_grouped['acc_importe'] = df_grouped['importe_EUR'].cumsum()

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df_grouped['year_quarter'],
        y=df_grouped['importe_EUR'],
        name='Dividendos',
        marker=dict(color=COLOR_PRINCIPAL, line=dict(color=COLOR_PRINCIPAL, width=1.2)),
        hovertemplate='<b>%{x}</b><br>Dividendos: %{y:,.2f} €<extra></extra>'
    ))
    fig.add_trace(go.Scatter(
        x=df_grouped['year_quarter'],
        y=df_grouped['acc_importe'],
        name='Acumulado',
        mode='lines+markers',
        line=dict(color=COLOR_SECUNDARIO, width=2),
        marker=dict(size=6),
        hovertemplate='<b>%{x}</b><br>Acumulado: %{y:,.2f} €<extra></extra>'
    ))
    fig.update_layout(
        title=dict(text="Dividendos por Trimestre y Acumulados", x=0.5, xanchor='center', font=dict(size=18)),
        xaxis=dict(title="Año - Trimestre", tickangle=-45, tickfont=dict(size=10)),
        yaxis=dict(title="Dividendos / Acumulado (€)", gridcolor='rgba(200,200,200,0.3)'),
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='center', x=0.5),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        hoverlabel=dict(bgcolor=HOVER_BG, font=HOVER_FONT),
        margin=dict(t=80, b=80, l=60, r=60),
        shapes=[dict(type="rect", xref="paper", yref="paper", x0=0, y0=0, x1=1, y1=1,
                     line=dict(color=COLOR_BORDE, width=1))]
    )
    st.plotly_chart(fig, use_container_width=True)


# -------- NUEVO: GRÁFICO PRECIO + COMPRAS/VENTAS ----------------
def plot_price_with_trades(selected_ticker, df_prices, df_ops):
    # --- Normalizar ticker seleccionado ---
    selected_norm = str(selected_ticker).strip().upper()

    # --- Copia y normalización de df_prices ---
    df_prices = df_prices.copy()
    df_prices['ticker_norm'] = (
        df_prices['ticker']
        .astype(str)
        .str.strip()
        .str.upper()
    )

    # --- Filtrar datos del ticker en histórico de precios ---
    px = df_prices[df_prices['ticker_norm'] == selected_norm].copy()
    if px.empty:
        st.error(f"No hay histórico de precios para el ticker '{selected_ticker}'.")
        st.write("Algunos tickers disponibles en df_prices:",
                 df_prices['ticker'].drop_duplicates().sort_values().head(20).tolist())
        return

    px['date'] = pd.to_datetime(px['date'])
    px.sort_values('date', inplace=True)

    # --- Operaciones (ya filtradas por empresa/ticker desde fuera) ---
    ops = df_ops.copy()
    if ops.empty:
        st.info("No hay operaciones para este valor.")
        return

    ops['date'] = pd.to_datetime(ops['date']).dt.normalize()
    ops['tipo_movimiento'] = ops['tipo_movimiento'].str.upper().str.strip()

    # Derivamos cantidad e importe (por si no hay columnas específicas)
    ops['cantidad'] = ops['num_acciones'].abs()
    ops['importe'] = ops['importe_EUR'].abs()
    ops['precio_op'] = np.where(
        ops['cantidad'] > 0,
        ops['importe'] / ops['cantidad'],
        np.nan
    )

    # Agregamos por día y tipo (por si hay varias órdenes en el mismo día)
    agg_ops = (
        ops
        .groupby(['date', 'tipo_movimiento'], as_index=False)
        .agg({'cantidad': 'sum', 'precio_op': 'mean', 'importe': 'sum'})
    )

    # Traer el cierre de ese día
    px_day = px[['date', 'Close']].copy()
    px_day.rename(columns={'Close': 'close'}, inplace=True)
    agg_ops = pd.merge(agg_ops, px_day, on='date', how='left')

    # Separar compras / ventas
    buys = agg_ops[agg_ops['tipo_movimiento'].str.contains('COMPRA')].copy()
    sells = agg_ops[agg_ops['tipo_movimiento'].str.contains('VENTA')].copy()

    fig = go.Figure()

    # Línea de precios
    fig.add_trace(go.Scatter(
        x=px['date'], y=px['Close'],
        mode='lines',
        name='Precio cierre',
        line=dict(width=2)
    ))

    # Compras
    if not buys.empty:
        fig.add_trace(go.Scatter(
            x=buys['date'],
            y=buys['close'].fillna(buys['precio_op']),
            mode='markers',
            name='Compra',
            marker=dict(color='rgba(220,0,0,0.95)',
                        size=14,
                        line=dict(color='white', width=1)),
            hovertemplate=(
                "<b>%{x|%Y-%m-%d}</b><br>"
                "Tipo: Compra<br>"
                "Precio op: %{customdata[0]:,.2f} €<br>"
                "Cierre: %{y:,.2f} €<br>"
                "Cantidad total: %{customdata[1]:,.2f}<br>"
                "Importe: %{customdata[2]:,.2f} €<extra></extra>"
            ),
            customdata=np.stack(
                [buys['precio_op'], buys['cantidad'], buys['importe']], axis=1
            )
        ))

    # Ventas
    if not sells.empty:
        fig.add_trace(go.Scatter(
            x=sells['date'],
            y=sells['close'].fillna(sells['precio_op']),
            mode='markers',
            name='Venta',
            marker=dict(color='rgba(0,180,0,0.95)',
                        size=14,
                        line=dict(color='white', width=1)),
            hovertemplate=(
                "<b>%{x|%Y-%m-%d}</b><br>"
                "Tipo: Venta<br>"
                "Precio op: %{customdata[0]:,.2f} €<br>"
                "Cierre: %{y:,.2f} €<br>"
                "Cantidad total: %{customdata[1]:,.2f}<br>"
                "Importe: %{customdata[2]:,.2f} €<extra></extra>"
            ),
            customdata=np.stack(
                [sells['precio_op'], sells['cantidad'], sells['importe']], axis=1
            )
        ))

    fig.update_layout(
        xaxis=dict(title="Fecha"),
        yaxis=dict(title="Precio (€)", gridcolor='rgba(200,200,200,0.2)'),
        legend=dict(orientation='h', yanchor='bottom', y=1.02,
                    xanchor='center', x=0.5),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        hoverlabel=dict(
            bgcolor='rgba(40,40,40,0.85)',
            font=dict(color='white', size=13),
            bordercolor='rgba(255,255,255,0.2)'
        ),
        margin=dict(t=80, b=60, l=60, r=40)
    )

    st.plotly_chart(fig, use_container_width=True)


# ---------------------------------------------------------------
# NUEVA FUNCIÓN: ANÁLISIS POR POSICIÓN
# ---------------------------------------------------------------
def analysis_by_position(df_degiro, all_stocks):
    st.subheader("📊 Análisis por Acción")

    # --- Filtramos movimientos válidos ---
    df_valid = df_degiro[
        ~df_degiro["movimiento"].str.upper().isin(["DEPOSITOS", "GASTOS"])
        & ~df_degiro["ticker"].astype(str).str.upper().isin(["DEPOSITOS", "GASTOS"])
    ].copy()
    empresas = sorted(df_valid["movimiento"].dropna().unique().tolist())
    empresa_sel = st.selectbox("Selecciona una empresa", empresas)

    df_emp = df_valid[df_valid["movimiento"] == empresa_sel].copy()

    # --- Corregir el signo de las ventas ---
    df_emp["ajuste_acciones"] = df_emp.apply(
        lambda x: -x["num_acciones"] if x["tipo_movimiento"] == "VENTA ACCIONES" else x["num_acciones"], axis=1
    )

    # --- Cálculos principales ---
    acciones_actuales = df_emp["ajuste_acciones"].sum()
    moneda = df_emp["moneda"].dropna().max()
    compras = df_emp.loc[df_emp["tipo_movimiento"] == "COMPRA ACCIONES", "importe_EUR"].sum()
    ventas = df_emp.loc[df_emp["tipo_movimiento"] == "VENTA ACCIONES", "importe_EUR"].sum()
    dividendos = df_emp.loc[df_emp["tipo_movimiento"] == "DIVIDENDO", "importe_EUR"].sum()

    resultado = ventas + compras if acciones_actuales == 0 else None

    # --- Color dinámico para la moneda ---
    if moneda == "EUR":
        moneda_bg = "#0046FF"
        moneda_text = "white"
    elif moneda == "USD":
        moneda_bg = "#73C8D2"
        moneda_text = "black"
    else:
        moneda_bg = "#AE75DA"
        moneda_text = "white"

    # --- Mostrar KPIs ---
    col1, col2, col3 = st.columns(3)
    col1.metric("Acciones en Cartera", f"{acciones_actuales:,.0f}")
    
    with col2:
        st.markdown(
            f"""
            <div style='background-color:rgba(40,40,40,0.2);padding:10px;border-radius:8px;text-align:center;'>
                <div style='font-size:0.8rem;color:gray;font-weight:600;margin-bottom:4px;'>Moneda</div>
                <div style='background-color:{moneda_bg};color:{moneda_text};
                            padding:6px 14px;border-radius:6px;display:inline-block;
                            font-weight:700;font-size:1.2rem;'>
                    {moneda}
                </div>
            </div>
            """, unsafe_allow_html=True
        )
    
    col3.metric("Dividendos Recibidos", f"{dividendos:,.2f} €" if dividendos != 0 else "N/A")

    col4, col5, col6 = st.columns(3)
    # Compras (rojo)
    with col4:
        st.markdown(
            f"<div style='background-color:rgba(255,0,0,0.1);padding:10px;border-radius:8px;'>"
            f"<b>Importe Total Compras (€)</b><br>"
            f"<span style='color:#FF4B4B;font-weight:bold'>{compras:,.2f}</span>"
            f"</div>", unsafe_allow_html=True)
    # Ventas (verde)
    with col5:
        st.markdown(
            f"<div style='background-color:rgba(0,255,0,0.05);padding:10px;border-radius:8px;'>"
            f"<b>Importe Total Ventas (€)</b><br>"
            f"<span style='color:#00CC66;font-weight:bold'>{ventas:,.2f}</span>"
            f"</div>", unsafe_allow_html=True)
    # Resultado posición cerrada
    with col6:
        if resultado is not None:
            color = "#00CC66" if resultado > 0 else "#FF4B4B"
            st.markdown(
                f"<div style='background-color:{COLOR_AUX2};padding:10px;border-radius:8px;'>"
                f"<b style='color:#333333;'>Resultado Posición Cerrada:</b> "
                f"<span style='color:{color};font-weight:bold'>{resultado:,.2f} €</span>"
                f"</div>", unsafe_allow_html=True)
        else:
            st.markdown(
                f"<div style='background-color:{COLOR_AUX2};padding:10px;border-radius:8px;'>"
                f"<b style='color:#333333;'>Resultado Posición Cerrada:</b> "
                f"<span style='color:gray;font-weight:bold'>N/A (posición abierta)</span>"
                f"</div>", unsafe_allow_html=True)

    st.divider()

    # --- NUEVO GRÁFICO: PRECIO + OPERACIONES ---
    st.subheader("📈 Evolución del Precio y Operaciones")

    if 'ticker' in df_emp.columns and df_emp['ticker'].notna().any():
        ticker_sel = df_emp['ticker'].dropna().iloc[0]
        plot_price_with_trades(ticker_sel, all_stocks, df_emp)
    else:
        st.info("No se encontró el ticker para esta empresa, no se puede dibujar el gráfico de precio.")


# ---------------------------------------------------------------
# PESTAÑAS PRINCIPALES
# ---------------------------------------------------------------
tab1, tab2, tab3 = st.tabs(["📈 Evolución Portafolio", "💶 Análisis de Dividendos", "📊 Análisis por Posición"])

with tab1:
    plot_portfolio_trend(portfolio)
    plot_portfolio_data(portfolio, all_stocks)

with tab2:
    plot_dividends_by_company(df_degiro)
    plot_dividends_evolution(df_degiro)

with tab3:
    analysis_by_position(df_degiro, all_stocks)
