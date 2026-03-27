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

def plot_semester_snapshots(portfolio):
    # -----------------------------------------------------------
    # 1) PREPARAR DATOS
    # -----------------------------------------------------------
    df = portfolio.copy()
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date').copy()

    # Acumulado real de depósitos hasta cada fecha
    df['depositos_acum'] = df['depositos'].fillna(0).cumsum()

    # Fecha máxima disponible
    max_date = df['date'].max()

    # -----------------------------------------------------------
    # 2) CREAR FECHAS FOTO
    #    Primera: 31/12/2021
    #    Luego: 30/06 y 31/12 de cada año
    # -----------------------------------------------------------
    snapshots = [pd.Timestamp("2021-12-31")]

    for year in range(2022, max_date.year + 1):
        for month_day in ["06-30", "12-31"]:
            snap = pd.Timestamp(f"{year}-{month_day}")
            if snap <= max_date:
                snapshots.append(snap)

    df_snap = pd.DataFrame({'snapshot_date': snapshots}).sort_values('snapshot_date')

    # -----------------------------------------------------------
    # 3) PARA CADA FOTO, TOMAR EL ÚLTIMO REGISTRO DISPONIBLE <= FECHA
    # -----------------------------------------------------------
    df_base = df[['date', 'depositos_acum', 'posiciones']].copy()

    df_snap = pd.merge_asof(
        df_snap.sort_values('snapshot_date'),
        df_base.sort_values('date'),
        left_on='snapshot_date',
        right_on='date',
        direction='backward'
    )

    # -----------------------------------------------------------
    # 4) CÁLCULOS PRINCIPALES
    # -----------------------------------------------------------
    df_snap['saldo_cuenta'] = df_snap['posiciones']
    df_snap['neto'] = df_snap['saldo_cuenta'] - df_snap['depositos_acum']

    # Variación % vs foto anterior
    df_snap['pct_dep'] = df_snap['depositos_acum'].pct_change() * 100
    df_snap['pct_saldo'] = df_snap['saldo_cuenta'].pct_change() * 100
    df_snap['pct_neto'] = df_snap['neto'].pct_change() * 100

    # Etiquetas eje X
    df_snap['label'] = df_snap['snapshot_date'].dt.strftime('%d/%m/%Y')

    # -----------------------------------------------------------
    # 5) CREAR GRÁFICO
    # -----------------------------------------------------------
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=df_snap['label'],
        y=df_snap['depositos_acum'],
        name='Depósitos acumulados',
        marker=dict(
            color=COLOR_PRINCIPAL,
            line=dict(color=COLOR_PRINCIPAL, width=1.2)
        ),
        hovertemplate='<b>%{x}</b><br>Depósitos acumulados: %{y:,.2f} €<extra></extra>'
    ))

    fig.add_trace(go.Bar(
        x=df_snap['label'],
        y=df_snap['saldo_cuenta'],
        name='Saldo cuenta',
        marker=dict(
            color=COLOR_AUX1,
            line=dict(color=COLOR_AUX1, width=1.2)
        ),
        hovertemplate='<b>%{x}</b><br>Saldo cuenta: %{y:,.2f} €<extra></extra>'
    ))

    fig.add_trace(go.Bar(
        x=df_snap['label'],
        y=df_snap['neto'],
        name='Neto',
        marker=dict(
            color=COLOR_SECUNDARIO,
            line=dict(color=COLOR_SECUNDARIO, width=1.2)
        ),
        hovertemplate='<b>%{x}</b><br>Neto: %{y:,.2f} €<extra></extra>'
    ))

    # -----------------------------------------------------------
    # 6) ANOTACIONES / TARJETAS
    # -----------------------------------------------------------
    annotations = []

    # xshift para colocar cada tarjeta sobre su barra correspondiente
    series_info = [
        ('depositos_acum', 'pct_dep', -55),
        ('saldo_cuenta', 'pct_saldo', 0),
        ('neto', 'pct_neto', 55),
    ]

    for val_col, pct_col, xshift in series_info:
        for _, row in df_snap.iterrows():
            x = row['label']
            y = row[val_col]
            pct = row[pct_col]

            if pd.isna(y):
                continue

            # Tarjeta superior: valor absoluto
            annotations.append(dict(
                x=x,
                y=y,
                xshift=xshift,
                yshift=62,
                text=f"<b>{y:,.2f} €</b>",
                showarrow=False,
                font=dict(size=11, color="black"),
                align="center",
                bgcolor="rgba(245,245,245,0.95)",
                bordercolor="rgba(180,180,180,0.9)",
                borderwidth=1,
                borderpad=4
            ))

            # Tarjeta inferior: variación %
            if pd.notna(pct):
                pct_color = "#00AA55" if pct >= 0 else "#D62728"
                pct_text = f"<b>{pct:+.1f}%</b>"
            else:
                pct_color = "gray"
                pct_text = "<b>—</b>"

            annotations.append(dict(
                x=x,
                y=y,
                xshift=xshift,
                yshift=24,
                text=pct_text,
                showarrow=False,
                font=dict(size=10, color=pct_color),
                align="center",
                bgcolor="rgba(245,245,245,0.95)",
                bordercolor="rgba(180,180,180,0.9)",
                borderwidth=1,
                borderpad=3
            ))

    # -----------------------------------------------------------
    # 7) LAYOUT
    # -----------------------------------------------------------
    fig.update_layout(
        title=dict(
            text="Fotos Semestrales: Depósitos, Saldo y Neto",
            x=0.5,
            xanchor='center',
            font=dict(size=18)
        ),
        xaxis=dict(
            title="Fecha foto",
            tickangle=-45
        ),
        yaxis=dict(
            title="Importe (€)",
            gridcolor='rgba(200,200,200,0.3)'
        ),
        barmode='group',
        annotations=annotations,
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='center',
            x=0.5
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        hoverlabel=dict(bgcolor=HOVER_BG, font=HOVER_FONT),
        margin=dict(t=130, b=90, l=60, r=40),
        shapes=[dict(
            type="rect",
            xref="paper",
            yref="paper",
            x0=0, y0=0, x1=1, y1=1,
            line=dict(color=COLOR_BORDE, width=1)
        )]
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

def plot_dividends_yearly_growth(df_degiro):
    # --- Filtrar dividendos ---
    df_dividends = df_degiro[df_degiro['tipo_movimiento'] == 'DIVIDENDO'].copy()
    df_dividends['date'] = pd.to_datetime(df_dividends['date'])
    df_dividends['year'] = df_dividends['date'].dt.year

    # --- Agrupar por año ---
    df_grouped = df_dividends.groupby('year', as_index=False)['importe_EUR'].sum()
    df_grouped = df_grouped.sort_values('year')

    # --- Calcular crecimiento vs año anterior ---
    df_grouped['pct_change'] = df_grouped['importe_EUR'].pct_change() * 100

    fig = go.Figure()

    # --- Barras de dividendos anuales ---
    fig.add_trace(go.Bar(
        x=df_grouped['year'],
        y=df_grouped['importe_EUR'],
        name='Dividendos anuales',
        marker=dict(
            color=COLOR_PRINCIPAL,
            line=dict(color=COLOR_PRINCIPAL, width=1.2)
        ),
        hovertemplate='<b>%{x}</b><br>Dividendos: %{y:,.2f} €<extra></extra>'
    ))

    # --- Crear anotaciones tipo "tarjeta" sobre cada barra ---
    annotations = []

    for _, row in df_grouped.iterrows():
        year = row['year']
        value = row['importe_EUR']
        pct = row['pct_change']

        # Tarjeta superior: total dividendos
        annotations.append(dict(
            x=year,
            y=value,
            yshift=28,
            text=f"<b>{value:,.2f} €</b>",
            showarrow=False,
            font=dict(size=12, color="black"),
            align="center",
            bgcolor="rgba(245,245,245,0.95)",
            bordercolor="rgba(180,180,180,0.9)",
            borderwidth=1,
            borderpad=4
        ))

        # Tarjeta inferior: crecimiento %
        if pd.notna(pct):
            pct_color = "#00AA55" if pct >= 0 else "#D62728"
            pct_text = f"<b>{pct:+.1f}%</b>"
        else:
            pct_color = "gray"
            pct_text = "<b>—</b>"

        annotations.append(dict(
            x=year,
            y=value,
            yshift=6,
            text=pct_text,
            showarrow=False,
            font=dict(size=11, color=pct_color),
            align="center",
            bgcolor="rgba(245,245,245,0.95)",
            bordercolor="rgba(180,180,180,0.9)",
            borderwidth=1,
            borderpad=3
        ))

    # --- Layout ---
    fig.update_layout(
        title=dict(
            text="Dividendos Anuales y Crecimiento",
            x=0.5,
            xanchor='center',
            font=dict(size=18)
        ),
        xaxis=dict(
            title="Año",
            tickmode='linear'
        ),
        yaxis=dict(
            title="Dividendos (€)",
            gridcolor='rgba(200,200,200,0.3)'
        ),
        annotations=annotations,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        hoverlabel=dict(bgcolor=HOVER_BG, font=HOVER_FONT),
        margin=dict(t=100, b=80, l=60, r=40),
        shapes=[dict(
            type="rect",
            xref="paper",
            yref="paper",
            x0=0, y0=0, x1=1, y1=1,
            line=dict(color=COLOR_BORDE, width=1)
        )]
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

def plot_structural_diversification(df_portfolio_ticker):
    st.subheader("🧩 Diversificación Estructural")

    df = df_portfolio_ticker.copy()
    df['date'] = pd.to_datetime(df['date'])

    # --- Tomar última foto disponible ---
    last_date = df['date'].max()
    df_last = df[df['date'] == last_date].copy()

    # Filtrar posiciones con valor real
    df_last = df_last[df_last['importe_EUR'].fillna(0) > 0].copy()

    if df_last.empty:
        st.info("No hay posiciones disponibles para analizar en la última fecha.")
        return

    # --- Pesos ---
    total_value = df_last['importe_EUR'].sum()
    df_last['peso'] = df_last['importe_EUR'] / total_value
    df_last = df_last.sort_values('peso', ascending=False)

    # --- Métricas ---
    n_positions = df_last['ticker'].nunique()
    max_weight = df_last['peso'].max()
    hhi = (df_last['peso'] ** 2).sum()
    n_eff = 1 / hhi if hhi > 0 else np.nan

    # Score simple orientativo
    if n_eff >= 10:
        div_label = "Muy diversificada"
        div_color = "#00AA55"
    elif n_eff >= 6:
        div_label = "Diversificación aceptable"
        div_color = "#FFB000"
    else:
        div_label = "Concentrada"
        div_color = "#D62728"

    # --- KPIs ---
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Nº posiciones", f"{n_positions}")
    col2.metric("Mayor peso", f"{max_weight:.1%}")
    col3.metric("HHI", f"{hhi:.3f}")
    col4.metric("Nº efectivo", f"{n_eff:.2f}")

    st.markdown(
        f"""
        <div style='background-color:rgba(245,245,245,0.9);
                    padding:10px 14px;
                    border-radius:8px;
                    border:1px solid rgba(180,180,180,0.8);
                    margin-top:8px;
                    margin-bottom:14px;'>
            <span style='font-weight:700; color:#333;'>Diagnóstico:</span>
            <span style='font-weight:700; color:{div_color}; margin-left:8px;'>{div_label}</span>
        </div>
        """,
        unsafe_allow_html=True
    )

    # --- Gráfico de pesos por ticker ---
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=df_last['peso'] * 100,
        y=df_last['ticker'],
        orientation='h',
        text=[f"{v:.1%}" for v in df_last['peso']],
        textposition='outside',
        marker=dict(
            color=COLOR_PRINCIPAL,
            line=dict(color=COLOR_PRINCIPAL, width=1.2)
        ),
        hovertemplate='<b>%{y}</b><br>Peso: %{x:.2f}%<br>Valor: %{customdata:,.2f} €<extra></extra>',
        customdata=df_last['importe_EUR']
    ))

    fig.update_layout(
        title=dict(
            text=f"Pesos por Posición (foto actual: {last_date.strftime('%d/%m/%Y')})",
            x=0.5,
            xanchor='center',
            font=dict(size=18)
        ),
        xaxis=dict(
            title="Peso en cartera (%)",
            gridcolor='rgba(200,200,200,0.3)'
        ),
        yaxis=dict(
            title="Ticker",
            autorange='reversed'
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        hoverlabel=dict(bgcolor=HOVER_BG, font=HOVER_FONT),
        margin=dict(t=80, b=60, l=60, r=60),
        shapes=[dict(
            type="rect",
            xref="paper",
            yref="paper",
            x0=0, y0=0, x1=1, y1=1,
            line=dict(color=COLOR_BORDE, width=1)
        )]
    )

    st.plotly_chart(fig, use_container_width=True)

    # --- Tabla opcional ---
    with st.expander("Ver detalle de pesos"):
        st.dataframe(
            df_last[['ticker', 'importe_EUR', 'peso']].rename(columns={
                'importe_EUR': 'Valor (€)',
                'peso': 'Peso'
            }),
            use_container_width=True
        )

# CARTERA DE MARKOWITZ -----------------------------------------------------------------------

def plot_markowitz_analysis(df_portfolio_ticker, all_stocks, n_portfolios=3000, risk_free_rate=0.0):
    st.subheader("📈 Optimización de Cartera (Markowitz)")

    # -----------------------------------------------------------
    # 1) OBTENER CARTERA ACTUAL (ÚLTIMA FOTO)
    # -----------------------------------------------------------
    df_pos = df_portfolio_ticker.copy()
    df_pos['date'] = pd.to_datetime(df_pos['date'])

    last_date = df_pos['date'].max()
    df_last = df_pos[df_pos['date'] == last_date].copy()
    df_last = df_last[df_last['importe_EUR'].fillna(0) > 0].copy()

    if df_last.empty:
        st.info("No hay posiciones válidas en la última fecha para calcular Markowitz.")
        return

    df_last = df_last.groupby('ticker', as_index=False)['importe_EUR'].sum()
    total_value = df_last['importe_EUR'].sum()
    df_last['peso'] = df_last['importe_EUR'] / total_value

    tickers = df_last['ticker'].tolist()
    weights_current = df_last['peso'].values

    # -----------------------------------------------------------
    # 2) PREPARAR PRECIOS HISTÓRICOS
    # -----------------------------------------------------------
    df_prices = all_stocks.copy()
    df_prices['date'] = pd.to_datetime(df_prices['date'])
    df_prices['ticker'] = df_prices['ticker'].astype(str).str.strip()

    df_prices = df_prices[df_prices['ticker'].isin(tickers)].copy()

    if df_prices.empty:
        st.info("No hay histórico de precios para los tickers actuales de la cartera.")
        return

    # Usamos columna Close
    prices = df_prices.pivot_table(index='date', columns='ticker', values='Close', aggfunc='last')
    prices = prices.sort_index()

    # Nos quedamos solo con columnas que existan de verdad
    common_tickers = [t for t in tickers if t in prices.columns]
    if len(common_tickers) < 2:
        st.info("No hay suficientes activos con histórico de precios para calcular Markowitz.")
        return

    prices = prices[common_tickers].copy()

    # Ajustar pesos actuales a los tickers realmente disponibles en precios
    df_last = df_last[df_last['ticker'].isin(common_tickers)].copy()
    df_last['peso'] = df_last['importe_EUR'] / df_last['importe_EUR'].sum()

    tickers = df_last['ticker'].tolist()
    weights_current = df_last['peso'].values
    prices = prices[tickers]

    # Eliminar columnas con demasiados NaN y limpiar
    valid_ratio = prices.notna().mean()
    keep_cols = valid_ratio[valid_ratio >= 0.7].index.tolist()

    if len(keep_cols) < 2:
        st.info("No hay suficientes activos con datos históricos consistentes para calcular Markowitz.")
        return

    prices = prices[keep_cols].copy()
    df_last = df_last[df_last['ticker'].isin(keep_cols)].copy()
    df_last['peso'] = df_last['importe_EUR'] / df_last['importe_EUR'].sum()

    tickers = df_last['ticker'].tolist()
    weights_current = df_last['peso'].values
    prices = prices[tickers]

    # Relleno suave y cálculo de retornos
    prices = prices.ffill().dropna(how='all')
    returns = prices.pct_change().dropna()

    if returns.shape[0] < 30 or returns.shape[1] < 2:
        st.info("No hay suficientes datos de retornos para construir el análisis de Markowitz.")
        return

    # -----------------------------------------------------------
    # 3) ESTADÍSTICAS ANUALIZADAS
    # -----------------------------------------------------------
    mean_returns = returns.mean() * 252
    cov_matrix = returns.cov() * 252

    # -----------------------------------------------------------
    # 4) MÉTRICAS DE LA CARTERA ACTUAL
    # -----------------------------------------------------------
    port_return = np.dot(weights_current, mean_returns)
    port_vol = np.sqrt(np.dot(weights_current.T, np.dot(cov_matrix, weights_current)))
    port_sharpe = (port_return - risk_free_rate) / port_vol if port_vol > 0 else np.nan

    # -----------------------------------------------------------
    # 5) SIMULACIÓN DE CARTERAS ALEATORIAS
    # -----------------------------------------------------------
    results = np.zeros((4, n_portfolios))
    weights_list = []

    n_assets = len(tickers)

    for i in range(n_portfolios):
        weights = np.random.random(n_assets)
        weights /= np.sum(weights)

        sim_return = np.dot(weights, mean_returns)
        sim_vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
        sim_sharpe = (sim_return - risk_free_rate) / sim_vol if sim_vol > 0 else np.nan

        results[0, i] = sim_return
        results[1, i] = sim_vol
        results[2, i] = sim_sharpe
        results[3, i] = i
        weights_list.append(weights)

    sim_df = pd.DataFrame({
        'return': results[0],
        'volatility': results[1],
        'sharpe': results[2]
    })

    # Cartera de máximo Sharpe
    idx_max_sharpe = sim_df['sharpe'].idxmax()
    best_port = sim_df.loc[idx_max_sharpe]
    best_weights = weights_list[idx_max_sharpe]

    # Percentil de tu cartera por Sharpe
    sharpe_percentile = (sim_df['sharpe'] < port_sharpe).mean() * 100 if pd.notna(port_sharpe) else np.nan

    # -----------------------------------------------------------
    # 6) KPIs
    # -----------------------------------------------------------
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Retorno esperado", f"{port_return:.2%}")
    col2.metric("Volatilidad", f"{port_vol:.2%}")
    col3.metric("Sharpe", f"{port_sharpe:.2f}" if pd.notna(port_sharpe) else "N/A")
    col4.metric("Percentil eficiencia", f"{sharpe_percentile:.0f}" if pd.notna(sharpe_percentile) else "N/A")

    # Diagnóstico simple
    if pd.isna(port_sharpe):
        diag_text = "No se pudo calcular correctamente el ratio Sharpe."
        diag_color = "#777777"
    elif sharpe_percentile >= 75:
        diag_text = "Tu cartera está bien posicionada frente a las combinaciones simuladas."
        diag_color = "#00AA55"
    elif sharpe_percentile >= 40:
        diag_text = "Tu cartera es razonable, pero hay margen de mejora en eficiencia."
        diag_color = "#FFB000"
    else:
        diag_text = "Tu cartera parece poco eficiente frente a combinaciones alternativas."
        diag_color = "#D62728"

    st.markdown(
        f"""
        <div style='background-color:rgba(245,245,245,0.9);
                    padding:10px 14px;
                    border-radius:8px;
                    border:1px solid rgba(180,180,180,0.8);
                    margin-top:8px;
                    margin-bottom:14px;'>
            <span style='font-weight:700; color:#333;'>Diagnóstico:</span>
            <span style='font-weight:700; color:{diag_color}; margin-left:8px;'>{diag_text}</span>
        </div>
        """,
        unsafe_allow_html=True
    )

    # -----------------------------------------------------------
    # 7) GRÁFICO MARKOWITZ
    # -----------------------------------------------------------
    fig = go.Figure()

    # Nube de carteras simuladas
    fig.add_trace(go.Scatter(
        x=sim_df['volatility'],
        y=sim_df['return'],
        mode='markers',
        name='Carteras simuladas',
        marker=dict(
            size=5,
            color=sim_df['sharpe'],
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title="Sharpe"),
            opacity=0.65
        ),
        hovertemplate=(
            "Volatilidad: %{x:.2%}<br>"
            "Retorno: %{y:.2%}<br>"
            "Sharpe: %{marker.color:.2f}<extra></extra>"
        )
    ))

    # Tu cartera actual
    fig.add_trace(go.Scatter(
        x=[port_vol],
        y=[port_return],
        mode='markers',
        name='Tu cartera actual',
        marker=dict(
            size=16,
            color='red',
            line=dict(color='white', width=1.5)
        ),
        hovertemplate=(
            "<b>Tu cartera actual</b><br>"
            "Volatilidad: %{x:.2%}<br>"
            "Retorno: %{y:.2%}<extra></extra>"
        )
    ))

    # Cartera de máximo Sharpe
    fig.add_trace(go.Scatter(
        x=[best_port['volatility']],
        y=[best_port['return']],
        mode='markers',
        name='Máximo Sharpe',
        marker=dict(
            size=16,
            color='green',
            line=dict(color='white', width=1.5)
        ),
        hovertemplate=(
            "<b>Cartera máxima Sharpe</b><br>"
            "Volatilidad: %{x:.2%}<br>"
            "Retorno: %{y:.2%}<extra></extra>"
        )
    ))

    fig.update_layout(
        title=dict(
            text=f"Frontera simulada de Markowitz (foto actual: {last_date.strftime('%d/%m/%Y')})",
            x=0.5,
            xanchor='center',
            font=dict(size=18)
        ),
        xaxis=dict(
            title="Volatilidad anualizada",
            tickformat=".0%",
            gridcolor='rgba(200,200,200,0.3)'
        ),
        yaxis=dict(
            title="Retorno esperado anualizado",
            tickformat=".0%",
            gridcolor='rgba(200,200,200,0.3)'
        ),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='center',
            x=0.5
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        hoverlabel=dict(bgcolor=HOVER_BG, font=HOVER_FONT),
        margin=dict(t=80, b=60, l=60, r=60),
        shapes=[dict(
            type="rect",
            xref="paper",
            yref="paper",
            x0=0, y0=0, x1=1, y1=1,
            line=dict(color=COLOR_BORDE, width=1)
        )]
    )

    st.plotly_chart(fig, use_container_width=True)

    # -----------------------------------------------------------
    # 8) TABLA DE PESOS ÓPTIMOS
    # -----------------------------------------------------------
    df_opt = pd.DataFrame({
        'ticker': tickers,
        'peso_actual': weights_current,
        'peso_max_sharpe': best_weights
    }).sort_values('peso_max_sharpe', ascending=False)

    with st.expander("Ver comparación de pesos: actual vs máximo Sharpe"):
        df_opt_show = df_opt.copy()
        df_opt_show['peso_actual'] = df_opt_show['peso_actual'].map(lambda x: f"{x:.1%}")
        df_opt_show['peso_max_sharpe'] = df_opt_show['peso_max_sharpe'].map(lambda x: f"{x:.1%}")

        st.dataframe(
            df_opt_show.rename(columns={
                'peso_actual': 'Peso actual',
                'peso_max_sharpe': 'Peso máximo Sharpe'
            }),
            use_container_width=True
        )


# ---------------------------------------------------------------
# PESTAÑAS PRINCIPALES
# ---------------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs(["📈 Evolución Portafolio", "💶 Análisis de Dividendos", "📊 Análisis por Posición", "📊 Análisis de la Cartera"])

with tab1:
    plot_portfolio_trend(portfolio)
    plot_portfolio_data(portfolio, all_stocks)
    plot_semester_snapshots(portfolio)

with tab2:
    plot_dividends_by_company(df_degiro)
    plot_dividends_evolution(df_degiro)
    plot_dividends_yearly_growth(df_degiro)

with tab3:
    analysis_by_position(df_degiro, all_stocks)

with tab4:
    plot_structural_diversification(df_portfolio_ticker)
    st.divider()
    plot_markowitz_analysis(df_portfolio_ticker, all_stocks)
