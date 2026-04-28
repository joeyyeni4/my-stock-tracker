
import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="個人股票追蹤工具", layout="wide")

st.title("📈 您的個人股票追蹤儀表板")
st.info("請在左側輸入您的股票代號（台股請加 .TW，如 2330.TW）")

if 'portfolio' not in st.session_state:
    st.session_state.portfolio = []

with st.sidebar:
    st.header("➕ 新增股票")
    symbol = st.text_input("股票代號", placeholder="例如: 2330.TW")
    buy_price = st.number_input("買入單價", min_value=0.0, step=0.1)
    quantity = st.number_input("持有數量", min_value=0, step=1)
    
    if st.button("新增至清單"):
        if symbol:
            st.session_state.portfolio.append({
                "Symbol": symbol.upper(),
                "Buy Price": buy_price,
                "Quantity": quantity
            })
            st.success(f"已新增 {symbol}")
    
    if st.button("清空所有資料"):
        st.session_state.portfolio = []
        st.rerun()

if st.session_state.portfolio:
    results = []
    total_cost = 0.0
    total_market_value = 0.0
    
    for item in st.session_state.portfolio:
        try:
            ticker = yf.Ticker(item['Symbol'])
            current_price = ticker.history(period="1d")['Close'].iloc[-1]
            
            cost = item['Buy Price'] * item['Quantity']
            market_value = current_price * item['Quantity']
            profit = market_value - cost
            pct = (profit / cost * 100) if cost != 0 else 0
            
            total_cost += cost
            total_market_value += market_value
            
            results.append({
                "代號": item['Symbol'],
                "買入價": item['Buy Price'],
                "現價": round(current_price, 2),
                "數量": item['Quantity'],
                "投資成本": round(cost, 2),
                "目前市值": round(market_value, 2),
                "損益": round(profit, 2),
                "漲跌幅%": f"{pct:+.2f}%"
            })
        except:
            st.warning(f"無法抓取 {item['Symbol']} 的資料")

    df = pd.DataFrame(results)
    
    # KPI
    c1, c2, c3 = st.columns(3)
    total_profit = total_market_value - total_cost
    total_pct = (total_profit / total_cost * 100) if total_cost != 0 else 0
    
    c1.metric("總成本", f"${total_cost:,.2f}")
    c2.metric("總市值", f"${total_market_value:,.2f}")
    c3.metric("總盈虧", f"${total_profit:,.2f}", f"{total_pct:+.2f}%")
    
    st.divider()
    st.subheader("📊 持股明細")
    st.dataframe(df, use_container_width=True)
    
    fig = px.pie(df, values='目前市值', names='代號', title='投資權重分布')
    st.plotly_chart(fig)
else:
    st.write("目前清單為空，請從側邊欄新增股票。")
