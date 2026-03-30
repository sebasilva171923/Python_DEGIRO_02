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

# -------------------------------------------------------------------------------------------------------------------------- #

# ------------------------------------------------------- PESTAÑA 01 ------------------------------------------------------- #

# -------------------------------------------------------------------------------------------------------------------------- #

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

def plot_annual_returns_table(portfolio):
    st.subheader("📅 Rentabilidad Anual de la Cartera")

    df = portfolio.copy()
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date').copy()

    # -----------------------------------------------------------
    # 1) ELEGIR LA SERIE DE VALOR DE CARTERA
    # -----------------------------------------------------------
    # Usamos "posiciones" como valor real de la cuenta/inversión
    if 'posiciones' not in df.columns:
        st.info("No existe la columna 'posiciones' en portfolio para calcular rentabilidades.")
        return

    df = df[['date', 'posiciones', 'depositos']].copy()
    df['depositos'] = df['depositos'].fillna(0)

    # Evitar divisiones por cero o valores inválidos
    df = df[df['posiciones'].notna()].copy()

    if len(df) < 2:
        st.info("No hay suficientes datos para calcular la rentabilidad anual.")
        return

    # -----------------------------------------------------------
    # 2) RENTABILIDAD DIARIA AJUSTADA POR FLUJOS (TWR simplificado)
    # -----------------------------------------------------------
    df['valor_prev'] = df['posiciones'].shift(1)

    df['daily_return'] = np.where(
        (df['valor_prev'].notna()) & (df['valor_prev'] != 0),
        (df['posiciones'] - df['valor_prev'] - df['depositos']) / df['valor_prev'],
        np.nan
    )

    # Primer año disponible
    df['year'] = df['date'].dt.year

    # -----------------------------------------------------------
    # 3) RENTABILIDAD POR AÑO NATURAL
    # -----------------------------------------------------------
    annual_rows = []

    for year, g in df.groupby('year'):
        g = g.sort_values('date').copy()

        valid_returns = g['daily_return'].dropna()

        if len(valid_returns) == 0:
            annual_return = np.nan
        else:
            annual_return = (1 + valid_returns).prod() - 1

        valor_inicio = g.iloc[0]['posiciones']
        valor_fin = g.iloc[-1]['posiciones']
        depositos_ano = g['depositos'].sum()

        annual_rows.append({
            'Año': year,
            'Valor inicio (€)': valor_inicio,
            'Valor fin (€)': valor_fin,
            'Depósitos año (€)': depositos_ano,
            'Rentabilidad anual': annual_return
        })

    df_annual = pd.DataFrame(annual_rows)

    # -----------------------------------------------------------
    # 4) RENTABILIDAD ANUALIZADA DESDE INICIO
    # -----------------------------------------------------------
    all_valid_returns = df['daily_return'].dropna()

    if len(all_valid_returns) > 0:
        total_return = (1 + all_valid_returns).prod() - 1

        start_date = df.loc[df['daily_return'].notna(), 'date'].min()
        end_date = df['date'].max()

        years_elapsed = (end_date - start_date).days / 365.25

        if years_elapsed > 0 and (1 + total_return) > 0:
            annualized_return = (1 + total_return) ** (1 / years_elapsed) - 1
        else:
            annualized_return = np.nan
    else:
        annualized_return = np.nan

    # -----------------------------------------------------------
    # 5) KPI SUPERIOR
    # -----------------------------------------------------------
    col1, col2 = st.columns(2)

    col1.metric(
        "Rentabilidad anualizada",
        f"{annualized_return:.2%}" if pd.notna(annualized_return) else "N/A"
    )

    if not df_annual.empty and df_annual['Rentabilidad anual'].notna().any():
        best_year_row = df_annual.loc[df_annual['Rentabilidad anual'].idxmax()]
        best_year_text = f"{int(best_year_row['Año'])} ({best_year_row['Rentabilidad anual']:.2%})"
    else:
        best_year_text = "N/A"

    col2.metric("Mejor año", best_year_text)

    # -----------------------------------------------------------
    # 6) TABLA FORMATEADA
    # -----------------------------------------------------------
    df_show = df_annual.copy()

    df_show['Valor inicio (€)'] = df_show['Valor inicio (€)'].map(lambda x: f"{x:,.2f} €")
    df_show['Valor fin (€)'] = df_show['Valor fin (€)'].map(lambda x: f"{x:,.2f} €")
    df_show['Depósitos año (€)'] = df_show['Depósitos año (€)'].map(lambda x: f"{x:,.2f} €")
    df_show['Rentabilidad anual'] = df_show['Rentabilidad anual'].map(
        lambda x: f"{x:.2%}" if pd.notna(x) else "N/A"
    )

    st.dataframe(df_show, use_container_width=True)

    # -----------------------------------------------------------
    # 7) ACLARACIÓN METODOLÓGICA
    # -----------------------------------------------------------
    with st.expander("Ver metodología del cálculo"):
        st.markdown(
            """
            **Cómo se calcula esta rentabilidad:**

            - Se usa la columna **`posiciones`** como valor de la cartera.
            - Se ajusta por los **depósitos** para no confundir aportaciones de capital con rendimiento.
            - La rentabilidad anual se calcula encadenando las rentabilidades diarias ajustadas por flujos.
            - La **rentabilidad anualizada** es la tasa compuesta anual desde el inicio hasta la fecha más reciente.
            """
        )

# -------------------------------------------------------------------------------------------------------------------------- #

# ------------------------------------------------------- PESTAÑA 02 ------------------------------------------------------- #

# -------------------------------------------------------------------------------------------------------------------------- #


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

# -------------------------------------------------------------------------------------------------------------------------- #

# ------------------------------------------------------- PESTAÑA 03 ------------------------------------------------------- #

# -------------------------------------------------------------------------------------------------------------------------- #

# ---------------------------------------------------------------
# NUEVA FUNCIÓN: ANÁLISIS POR POSICIÓN
# ---------------------------------------------------------------
def analysis_by_position(df_degiro, all_stocks, df_portfolio_ticker):
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

        # --- Obtener valor actual de la posición desde df_portfolio_ticker ---
    valor_actual_posicion = 0.0

    if 'ticker' in df_emp.columns and df_emp['ticker'].notna().any():
        ticker_sel = df_emp['ticker'].dropna().iloc[0]

        df_pt = df_portfolio_ticker.copy()
        df_pt['date'] = pd.to_datetime(df_pt['date'])

        df_pt_ticker = df_pt[df_pt['ticker'] == ticker_sel].copy()

        if not df_pt_ticker.empty:
            last_date_pt = df_pt_ticker['date'].max()
            df_pt_last = df_pt_ticker[df_pt_ticker['date'] == last_date_pt].copy()

            if 'importe_EUR' in df_pt_last.columns:
                valor_actual_posicion = df_pt_last['importe_EUR'].sum()

    # --- Ganancia/Pérdida por posición ---
    # Cerrada: ventas + compras
    # Abierta: valor actual + ventas + compras
    ganancia_posicion = (ventas + compras) if acciones_actuales == 0 else (valor_actual_posicion + ventas + compras)

    # --- Ganancia/Pérdida total incluyendo dividendos ---
    ganancia_total = ganancia_posicion + dividendos

    # --- Rentabilidad total (%) ---
    base_inversion = abs(compras)
    rentabilidad_total_pct = (ganancia_total / base_inversion) if base_inversion > 0 else np.nan

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
            
    # --- Tercera fila: rentabilidad total de la posición ---
    col7, col8, col9 = st.columns(3)

    color_gp = "#00CC66" if ganancia_posicion >= 0 else "#FF4B4B"
    color_gt = "#00CC66" if ganancia_total >= 0 else "#FF4B4B"
    color_rt = "#00CC66" if (pd.notna(rentabilidad_total_pct) and rentabilidad_total_pct >= 0) else "#FF4B4B"

    with col7:
        st.markdown(
            f"<div style='background-color:rgba(245,245,245,0.7);padding:10px;border-radius:8px;'>"
            f"<b>Ganancia/Pérdida por Posición</b><br>"
            f"<span style='color:{color_gp};font-weight:bold'>{ganancia_posicion:,.2f} €</span>"
            f"</div>",
            unsafe_allow_html=True
        )

    with col8:
        st.markdown(
            f"<div style='background-color:rgba(245,245,245,0.7);padding:10px;border-radius:8px;'>"
            f"<b>Ganancia/Pérdida Incl. Dividendos</b><br>"
            f"<span style='color:{color_gt};font-weight:bold'>{ganancia_total:,.2f} €</span>"
            f"</div>",
            unsafe_allow_html=True
        )

    with col9:
        rent_text = f"{rentabilidad_total_pct:,.2%}" if pd.notna(rentabilidad_total_pct) else "N/A"
        st.markdown(
            f"<div style='background-color:rgba(245,245,245,0.7);padding:10px;border-radius:8px;'>"
            f"<b>Rentabilidad Total (%)</b><br>"
            f"<span style='color:{color_rt};font-weight:bold'>{rent_text}</span>"
            f"</div>",
            unsafe_allow_html=True
        )

    st.divider()

    # --- NUEVO GRÁFICO: PRECIO + OPERACIONES ---
    st.subheader("📈 Evolución del Precio y Operaciones")

    if 'ticker' in df_emp.columns and df_emp['ticker'].notna().any():
        ticker_sel = df_emp['ticker'].dropna().iloc[0]
        plot_price_with_trades(ticker_sel, all_stocks, df_emp)
    else:
        st.info("No se encontró el ticker para esta empresa, no se puede dibujar el gráfico de precio.")

# -------------------------------------------------------------------------------------------------------------------------- #

# ------------------------------------------------------- PESTAÑA 04 ------------------------------------------------------- #

# -------------------------------------------------------------------------------------------------------------------------- #



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

# CONTRIBUCION AL RIESGO ---------------------------------------

def plot_risk_contribution(df_portfolio_ticker, all_stocks):
    st.subheader("⚠️ Contribución al Riesgo")

    # -----------------------------------------------------------
    # 1) OBTENER CARTERA ACTUAL
    # -----------------------------------------------------------
    df_pos = df_portfolio_ticker.copy()
    df_pos['date'] = pd.to_datetime(df_pos['date'])

    last_date = df_pos['date'].max()
    df_last = df_pos[df_pos['date'] == last_date].copy()
    df_last = df_last[df_last['importe_EUR'].fillna(0) > 0].copy()

    if df_last.empty:
        st.info("No hay posiciones válidas en la última fecha para calcular contribución al riesgo.")
        return

    df_last = df_last.groupby('ticker', as_index=False)['importe_EUR'].sum()
    df_last['peso'] = df_last['importe_EUR'] / df_last['importe_EUR'].sum()

    tickers = df_last['ticker'].tolist()

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

    prices = df_prices.pivot_table(index='date', columns='ticker', values='Close', aggfunc='last')
    prices = prices.sort_index()

    # Mantener solo tickers comunes
    common_tickers = [t for t in tickers if t in prices.columns]
    if len(common_tickers) < 2:
        st.info("No hay suficientes activos con histórico de precios para calcular contribución al riesgo.")
        return

    prices = prices[common_tickers].copy()
    df_last = df_last[df_last['ticker'].isin(common_tickers)].copy()
    df_last['peso'] = df_last['importe_EUR'] / df_last['importe_EUR'].sum()

    tickers = df_last['ticker'].tolist()
    weights = df_last['peso'].values
    prices = prices[tickers]

    # Limpiar
    valid_ratio = prices.notna().mean()
    keep_cols = valid_ratio[valid_ratio >= 0.7].index.tolist()

    if len(keep_cols) < 2:
        st.info("No hay suficientes activos con datos históricos consistentes para calcular contribución al riesgo.")
        return

    prices = prices[keep_cols].copy()
    df_last = df_last[df_last['ticker'].isin(keep_cols)].copy()
    df_last['peso'] = df_last['importe_EUR'] / df_last['importe_EUR'].sum()

    tickers = df_last['ticker'].tolist()
    weights = df_last['peso'].values
    prices = prices[tickers]

    prices = prices.ffill().dropna(how='all')
    returns = prices.pct_change().dropna()

    if returns.shape[0] < 30 or returns.shape[1] < 2:
        st.info("No hay suficientes retornos para calcular contribución al riesgo.")
        return

    # -----------------------------------------------------------
    # 3) MATRIZ DE COVARIANZAS Y RIESGO
    # -----------------------------------------------------------
    cov_matrix = returns.cov() * 252  # anualizada

    portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))

    if portfolio_vol <= 0:
        st.info("No se pudo calcular la volatilidad de la cartera.")
        return

    # Contribución marginal al riesgo
    marginal_risk = np.dot(cov_matrix, weights) / portfolio_vol

    # Contribución total al riesgo
    risk_contribution = weights * marginal_risk

    # % contribución al riesgo
    risk_contribution_pct = risk_contribution / risk_contribution.sum()

    # -----------------------------------------------------------
    # 4) DATAFRAME FINAL
    # -----------------------------------------------------------
    df_risk = pd.DataFrame({
        'ticker': tickers,
        'peso': weights,
        'contrib_riesgo': risk_contribution_pct
    })

    df_risk['diff'] = df_risk['contrib_riesgo'] - df_risk['peso']
    df_risk = df_risk.sort_values('contrib_riesgo', ascending=False)

    # KPIs
    top_risk_ticker = df_risk.iloc[0]['ticker']
    top_risk_pct = df_risk.iloc[0]['contrib_riesgo']
    max_weight_ticker = df_risk.sort_values('peso', ascending=False).iloc[0]['ticker']

    col1, col2, col3 = st.columns(3)
    col1.metric("Mayor contribuidor al riesgo", f"{top_risk_ticker}")
    col2.metric("% riesgo aportado", f"{top_risk_pct:.1%}")
    col3.metric("Mayor peso actual", f"{max_weight_ticker}")

    # Diagnóstico
    if top_risk_pct > 0.35:
        diag_text = f"{top_risk_ticker} domina claramente el riesgo total de la cartera."
        diag_color = "#D62728"
    elif top_risk_pct > 0.20:
        diag_text = f"{top_risk_ticker} es el principal foco de riesgo, aunque no de forma extrema."
        diag_color = "#FFB000"
    else:
        diag_text = "El riesgo parece relativamente repartido entre varios activos."
        diag_color = "#00AA55"

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
    # 5) GRÁFICO COMPARATIVO: PESO VS RIESGO
    # -----------------------------------------------------------
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=df_risk['peso'] * 100,
        y=df_risk['ticker'],
        orientation='h',
        name='Peso actual',
        marker=dict(
            color=COLOR_PRINCIPAL,
            line=dict(color=COLOR_PRINCIPAL, width=1.0)
        ),
        hovertemplate='<b>%{y}</b><br>Peso: %{x:.2f}%<extra></extra>'
    ))

    fig.add_trace(go.Bar(
        x=df_risk['contrib_riesgo'] * 100,
        y=df_risk['ticker'],
        orientation='h',
        name='Contribución al riesgo',
        marker=dict(
            color=COLOR_SECUNDARIO,
            line=dict(color=COLOR_SECUNDARIO, width=1.0)
        ),
        hovertemplate='<b>%{y}</b><br>Riesgo aportado: %{x:.2f}%<extra></extra>'
    ))

    fig.update_layout(
        title=dict(
            text=f"Peso vs Contribución al Riesgo (foto actual: {last_date.strftime('%d/%m/%Y')})",
            x=0.5,
            xanchor='center',
            font=dict(size=18)
        ),
        xaxis=dict(
            title="% sobre el total",
            gridcolor='rgba(200,200,200,0.3)'
        ),
        yaxis=dict(
            title="Ticker",
            autorange='reversed'
        ),
        barmode='group',
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
    # 6) TABLA DETALLE
    # -----------------------------------------------------------
    with st.expander("Ver detalle de contribución al riesgo"):
        df_risk_show = df_risk.copy()
        df_risk_show['peso'] = df_risk_show['peso'].map(lambda x: f"{x:.1%}")
        df_risk_show['contrib_riesgo'] = df_risk_show['contrib_riesgo'].map(lambda x: f"{x:.1%}")
        df_risk_show['diff'] = df_risk['diff'].map(lambda x: f"{x:+.1%}")

        st.dataframe(
            df_risk_show.rename(columns={
                'peso': 'Peso actual',
                'contrib_riesgo': 'Contribución al riesgo',
                'diff': 'Diferencia'
            }),
            use_container_width=True
        )

# MAXIMO DRAWDOWN Y RECUPERACION --------------------------------

def plot_drawdown_analysis(portfolio):
    st.subheader("📉 Drawdown Histórico")

    df = portfolio.copy()
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date').copy()

    # Serie base: valor de la cartera
    df = df[['date', 'acc_price']].dropna().copy()

    if df.empty or len(df) < 2:
        st.info("No hay suficientes datos para calcular el drawdown histórico.")
        return

    # -----------------------------------------------------------
    # 1) CÁLCULO DE DRAWDOWN
    # -----------------------------------------------------------
    df['rolling_max'] = df['acc_price'].cummax()
    df['drawdown'] = df['acc_price'] / df['rolling_max'] - 1

    max_dd = df['drawdown'].min()
    trough_idx = df['drawdown'].idxmin()
    trough_date = df.loc[trough_idx, 'date']

    # Pico previo al máximo drawdown
    df_until_trough = df[df['date'] <= trough_date].copy()
    peak_value = df_until_trough['rolling_max'].max()

    peak_candidates = df_until_trough[df_until_trough['acc_price'] == peak_value]
    if not peak_candidates.empty:
        peak_date = peak_candidates.iloc[0]['date']
    else:
        peak_date = pd.NaT

    # Recuperación: primera fecha posterior al trough en que vuelve al máximo anterior
    recovery_candidates = df[
        (df['date'] > trough_date) &
        (df['acc_price'] >= peak_value)
    ]

    if not recovery_candidates.empty:
        recovery_date = recovery_candidates.iloc[0]['date']
        recovery_days = (recovery_date - peak_date).days if pd.notna(peak_date) else np.nan
        recovered_text = recovery_date.strftime('%d/%m/%Y')
    else:
        recovery_date = pd.NaT
        recovery_days = np.nan
        recovered_text = "No recuperado"

    # Drawdown actual
    current_dd = df.iloc[-1]['drawdown']

    # -----------------------------------------------------------
    # 2) KPIs
    # -----------------------------------------------------------
    col1, col2, col3 = st.columns(3)
    col1.metric("Max Drawdown", f"{max_dd:.1%}")
    col2.metric("Drawdown actual", f"{current_dd:.1%}")
    col3.metric("Recuperación", f"{int(recovery_days)} días" if pd.notna(recovery_days) else "Pendiente")

    # Diagnóstico
    if max_dd <= -0.30:
        diag_text = "La cartera ha sufrido caídas históricas severas."
        diag_color = "#D62728"
    elif max_dd <= -0.15:
        diag_text = "La cartera ha sufrido correcciones relevantes, pero no extremas."
        diag_color = "#FFB000"
    else:
        diag_text = "La cartera ha mostrado un perfil de caídas relativamente contenido."
        diag_color = "#00AA55"

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
    # 3) GRÁFICO DE DRAWDOWN
    # -----------------------------------------------------------
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['drawdown'],
        mode='lines',
        name='Drawdown',
        fill='tozeroy',
        line=dict(color=COLOR_SECUNDARIO, width=2),
        hovertemplate='<b>%{x|%d %b %Y}</b><br>Drawdown: %{y:.2%}<extra></extra>'
    ))

    # Punto de máximo drawdown
    fig.add_trace(go.Scatter(
        x=[trough_date],
        y=[max_dd],
        mode='markers',
        name='Máximo drawdown',
        marker=dict(
            size=12,
            color='red',
            line=dict(color='white', width=1.2)
        ),
        hovertemplate='<b>Máximo drawdown</b><br>%{x|%d %b %Y}<br>%{y:.2%}<extra></extra>'
    ))

    fig.update_layout(
        title=dict(
            text="Evolución del Drawdown de la Cartera",
            x=0.5,
            xanchor='center',
            font=dict(size=18)
        ),
        xaxis=dict(
            title="Fecha",
            tickangle=-45
        ),
        yaxis=dict(
            title="Drawdown",
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
    # 4) TABLA RESUMEN
    # -----------------------------------------------------------
    with st.expander("Ver detalle del episodio de máximo drawdown"):
        summary_df = pd.DataFrame({
            'Concepto': [
                'Pico previo',
                'Mínimo del drawdown',
                'Recuperación',
                'Máximo drawdown'
            ],
            'Valor': [
                peak_date.strftime('%d/%m/%Y') if pd.notna(peak_date) else 'N/A',
                trough_date.strftime('%d/%m/%Y'),
                recovered_text,
                f"{max_dd:.1%}"
            ]
        })

        st.dataframe(summary_df, use_container_width=True)

# GRAFICO DE CORRELACIONES ENTRE POSICIONES ---------------------

def plot_correlation_heatmap(df_portfolio_ticker, all_stocks):
    st.subheader("🧠 Correlación entre Activos")

    # -----------------------------------------------------------
    # 1) OBTENER CARTERA ACTUAL
    # -----------------------------------------------------------
    df_pos = df_portfolio_ticker.copy()
    df_pos['date'] = pd.to_datetime(df_pos['date'])

    last_date = df_pos['date'].max()
    df_last = df_pos[df_pos['date'] == last_date].copy()
    df_last = df_last[df_last['importe_EUR'].fillna(0) > 0].copy()

    if df_last.empty:
        st.info("No hay posiciones válidas en la última fecha para calcular correlaciones.")
        return

    df_last = df_last.groupby('ticker', as_index=False)['importe_EUR'].sum()
    tickers = df_last['ticker'].tolist()

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

    prices = df_prices.pivot_table(index='date', columns='ticker', values='Close', aggfunc='last')
    prices = prices.sort_index()

    # Mantener solo tickers comunes
    common_tickers = [t for t in tickers if t in prices.columns]
    if len(common_tickers) < 2:
        st.info("No hay suficientes activos con histórico de precios para calcular correlaciones.")
        return

    prices = prices[common_tickers].copy()

    # Filtrar columnas con suficiente cobertura
    valid_ratio = prices.notna().mean()
    keep_cols = valid_ratio[valid_ratio >= 0.7].index.tolist()

    if len(keep_cols) < 2:
        st.info("No hay suficientes activos con datos históricos consistentes para calcular correlaciones.")
        return

    prices = prices[keep_cols].copy()
    prices = prices.ffill().dropna(how='all')

    returns = prices.pct_change().dropna()

    if returns.shape[0] < 30 or returns.shape[1] < 2:
        st.info("No hay suficientes retornos para construir el heatmap de correlación.")
        return

    # -----------------------------------------------------------
    # 3) MATRIZ DE CORRELACIÓN
    # -----------------------------------------------------------
    corr_matrix = returns.corr()

    # KPI auxiliar: correlación media fuera de diagonal
    corr_values = corr_matrix.values
    upper_vals = corr_values[np.triu_indices_from(corr_values, k=1)]

    avg_corr = np.nanmean(upper_vals) if len(upper_vals) > 0 else np.nan
    max_corr = np.nanmax(upper_vals) if len(upper_vals) > 0 else np.nan
    min_corr = np.nanmin(upper_vals) if len(upper_vals) > 0 else np.nan

    col1, col2, col3 = st.columns(3)
    col1.metric("Correlación media", f"{avg_corr:.2f}" if pd.notna(avg_corr) else "N/A")
    col2.metric("Correlación máxima", f"{max_corr:.2f}" if pd.notna(max_corr) else "N/A")
    col3.metric("Correlación mínima", f"{min_corr:.2f}" if pd.notna(min_corr) else "N/A")

    # Diagnóstico simple
    if pd.notna(avg_corr):
        if avg_corr >= 0.70:
            diag_text = "La cartera muestra una correlación media alta: la diversificación real es limitada."
            diag_color = "#D62728"
        elif avg_corr >= 0.40:
            diag_text = "La cartera tiene una correlación media moderada: existe diversificación, pero con bloques similares."
            diag_color = "#FFB000"
        else:
            diag_text = "La cartera presenta una correlación media contenida: la diversificación real parece buena."
            diag_color = "#00AA55"
    else:
        diag_text = "No se pudo calcular un diagnóstico de correlación."
        diag_color = "#777777"

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
    # 4) HEATMAP
    # -----------------------------------------------------------
    fig = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=corr_matrix.columns,
        y=corr_matrix.index,
        zmin=-1,
        zmax=1,
        colorscale='RdBu',
        reversescale=True,
        colorbar=dict(title="Corr"),
        text=np.round(corr_matrix.values, 2),
        texttemplate="%{text}",
        textfont={"size": 10},
        hovertemplate=(
            "<b>%{y}</b> vs <b>%{x}</b><br>"
            "Correlación: %{z:.2f}<extra></extra>"
        )
    ))

    fig.update_layout(
        title=dict(
            text=f"Heatmap de Correlación (foto actual: {last_date.strftime('%d/%m/%Y')})",
            x=0.5,
            xanchor='center',
            font=dict(size=18)
        ),
        xaxis=dict(
            title="Ticker",
            tickangle=-45
        ),
        yaxis=dict(
            title="Ticker",
            autorange='reversed'
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        hoverlabel=dict(bgcolor=HOVER_BG, font=HOVER_FONT),
        margin=dict(t=90, b=90, l=80, r=60),
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
    # 5) TABLA DE PARES MÁS Y MENOS CORRELACIONADOS
    # -----------------------------------------------------------
    pairs = []
    cols = corr_matrix.columns.tolist()

    for i in range(len(cols)):
        for j in range(i + 1, len(cols)):
            pairs.append({
                'activo_1': cols[i],
                'activo_2': cols[j],
                'correlacion': corr_matrix.iloc[i, j]
            })

    df_pairs = pd.DataFrame(pairs).sort_values('correlacion', ascending=False)

    with st.expander("Ver pares más y menos correlacionados"):
        col_a, col_b = st.columns(2)

        with col_a:
            st.markdown("**Más correlacionados**")
            st.dataframe(
                df_pairs.head(5).assign(
                    correlacion=lambda x: x['correlacion'].map(lambda v: f"{v:.2f}")
                ),
                use_container_width=True
            )

        with col_b:
            st.markdown("**Menos correlacionados**")
            st.dataframe(
                df_pairs.tail(5).sort_values('correlacion', ascending=True).assign(
                    correlacion=lambda x: x['correlacion'].map(lambda v: f"{v:.2f}")
                ),
                use_container_width=True
            )

# ---------------------------------------------------------------
# PESTAÑAS PRINCIPALES
# ---------------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs(["📈 Evolución Portafolio", "💶 Análisis de Dividendos", "📊 Análisis por Posición", "📊 Análisis de la Cartera"])

with tab1:
    plot_portfolio_trend(portfolio)
    st.divider()
    plot_portfolio_data(portfolio, all_stocks)
    st.divider()
    plot_semester_snapshots(portfolio)
    st.divider()
    plot_annual_returns_table(portfolio)

with tab2:
    plot_dividends_by_company(df_degiro)
    st.divider()
    plot_dividends_evolution(df_degiro)
    st.divider()
    plot_dividends_yearly_growth(df_degiro)

with tab3:
    analysis_by_position(df_degiro, all_stocks, df_portfolio_ticker)

with tab4:
    plot_structural_diversification(df_portfolio_ticker)
    st.divider()
    plot_markowitz_analysis(df_portfolio_ticker, all_stocks)
    st.divider()
    plot_risk_contribution(df_portfolio_ticker, all_stocks)
    st.divider()
    plot_drawdown_analysis(portfolio)
    st.divider()
    plot_correlation_heatmap(df_portfolio_ticker, all_stocks)
