import streamlit as st
import pandas as pd
import pickle
import plotly.graph_objects as go
import smtplib
import random
from email.mime.text import MIMEText

# ================= CONFIG =================
st.set_page_config(page_title="QuantTrade RL", layout="wide")

# ================= HEADER =================
col1, col2 = st.columns([1,5])

with col1:
    st.image("images/OMNIQUANT RL.png", width=130)

with col2:
    st.markdown("<h1 style='color:#00ffcc; font-size:60px; margin-top:10px;'>OmniQuant RL</h1>", unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)
# ================= LOGIN SYSTEM =================
if "credentials" not in st.session_state:
    st.session_state.credentials = {"username":"admin","password":"1234"}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 Login")

    u = st.text_input("Username")
    p = st.text_input("Password", type="password")

    if st.button("Login"):
        if u == st.session_state.credentials["username"] and p == st.session_state.credentials["password"]:
            st.session_state.logged_in = True
            st.success("Login Success")
            st.rerun()
        else:
            st.error("Invalid Credentials")

    st.stop()

phone = "User"

# ================= EMAIL CONFIG =================
EMAIL = "p.v.sasikumar4623@gmail.com"
APP_PASSWORD = "pikkehschtiamkci"

def send_email_otp(to_email, otp, purpose):
    try:
        msg = MIMEText(f"Your {purpose} OTP is: {otp}")
        msg["Subject"] = f"{purpose} OTP Verification"
        msg["From"] = EMAIL
        msg["To"] = to_email

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL, APP_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        st.error(f"Email Error: {e}")
        return False

# ================= LOAD DATA =================
results = pd.read_pickle("results.pkl")
buyhold = pickle.load(open("buyhold.pkl","rb"))
portfolio = pickle.load(open("portfolio.pkl","rb"))
full_df = pd.read_csv("nifty50_2016_2026.csv")

# ================= STOCK IMAGES =================
stock_images = {
    "INFY.NS": "images/INFY.png",
    "SHREECEM.NS": "images/SHREECEM.png",
    "APOLLOHOSP.NS": "images/APOLLOHOSP.png",
    "ICICIBANK.NS": "images/ICICIBANK.png",
    "ULTRACEMCO.NS": "images/ULTRACEMCO.png",
    "TCS.NS": "images/TCS.png",
    "SUNPHARMA.NS": "images/SUNPHARMA.png",
    "HCLTECH.NS": "images/HCLTECH.png",
    "LT.NS": "images/LT.png",
    "AXISBANK.NS": "images/AXISBANK.png"
}
DEFAULT_IMG = "images/default.png"

def show_stock_image(stock, size=60):
    st.image(stock_images.get(stock, DEFAULT_IMG), width=size)

def get_price(stock):
    return round(full_df[full_df["Name"]==stock]["close"].iloc[-1],2)

# ================= SESSION =================
if "users" not in st.session_state:
    st.session_state.users = {}

if "wallets" not in st.session_state:
    st.session_state.wallets = {}

if "transactions" not in st.session_state:
    st.session_state.transactions = []

if phone not in st.session_state.wallets:
    st.session_state.wallets[phone] = 100000

wallet_balance = st.session_state.wallets[phone]
rl_total = results["RL Return"].sum()
total_balance = wallet_balance + rl_total

# ================= SIDEBAR =================
st.sidebar.success(f"👤 {phone}")

if st.sidebar.button("🚪 Logout"):
    st.session_state.logged_in = False
    st.rerun()

page = st.sidebar.radio("MENU",
["Home","Market","Stock","Portfolio","Orders","Wallet","Profile","Signup","Settings"])

# ================= HOME =================
if page=="Home":
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Wallet Limit","₹200000")
    c2.metric("Wallet Balance",f"₹{wallet_balance}")
    c3.metric("RL Returns",f"₹{round(rl_total,2)}")
    c4.metric("Total Balance",f"₹{round(total_balance,2)}")

# ================= MARKET =================
elif page=="Market":

    st.title("📊 Market Dashboard")
    cols = st.columns(3)

    for i, (_, row) in enumerate(results.iterrows()):
        with cols[i % 3]:
            show_stock_image(row["Stock"], 60)
            st.subheader(row["Stock"])
            st.metric("Price", f"₹{get_price(row['Stock'])}")

            if row["Signal"]=="BUY":
                st.success("BUY 📈")
            elif row["Signal"]=="SELL":
                st.error("SELL 📉")
            else:
                st.warning("HOLD ⏳")

            # 🔥 GRAPH ADDED
            df_stock = full_df[full_df["Name"]==row["Stock"]].tail(30)
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df_stock["date"], y=df_stock["close"], name="Price"))
            st.plotly_chart(fig, use_container_width=True)

# ================= STOCK =================
elif page=="Stock":

    stock = st.selectbox("Select Stock", results["Stock"])
    row = results[results["Stock"]==stock].iloc[0]
    price = get_price(stock)

    col1,col2 = st.columns([1,4])
    with col1:
        show_stock_image(stock, 80)

    with col2:
        st.title(stock)
        st.metric("Price", price)
        st.success(f"RL Signal: {row['Signal']}")

    df = full_df[full_df["Name"]==stock].copy()
    df["date"] = pd.to_datetime(df["date"])
    df = df.tail(100)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["date"], y=df["close"], name="Price"))
    fig.add_trace(go.Scatter(x=df["date"], y=df["close"].rolling(20).mean(), name="MA20"))
    fig.add_trace(go.Scatter(x=df["date"], y=df["close"].ewm(span=20).mean(), name="EMA20"))
    st.plotly_chart(fig, use_container_width=True)

    # 🔥 FIXED RL vs BUYHOLD GRAPH
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=list(results["Stock"]), y=list(results["RL Return"]), name="RL"))
    fig2.add_trace(go.Scatter(x=list(results["Stock"]), y=list(buyhold.values()), name="BuyHold"))
    st.plotly_chart(fig2, use_container_width=True)

    qty = st.number_input("Qty",1)
    col1,col2 = st.columns(2)

    if col1.button("🟢 BUY"):
        cost = qty*price
        if wallet_balance >= cost:
            st.session_state.wallets[phone] -= cost
            st.session_state.transactions.append({"Type":"BUY","Stock":stock,"Amount":cost})
            st.success(f"🟢 Bought {stock} successfully!")

    if col2.button("🔴 SELL"):
        st.session_state.wallets[phone] += qty*price
        st.session_state.transactions.append({"Type":"SELL","Stock":stock,"Amount":qty*price})
        st.error(f"🔴 Sold {stock} successfully!")

# ================= PORTFOLIO =================
elif page=="Portfolio":

    st.title("📊 Portfolio Overview")
    st.dataframe(results)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=results["Stock"], y=results["RL Return"], name="RL"))
    fig.add_trace(go.Scatter(x=results["Stock"], y=list(buyhold.values()), name="BuyHold"))
    st.plotly_chart(fig)

# ================= ORDERS =================
elif page=="Orders":
    st.title("📜 Transaction History")
    st.dataframe(pd.DataFrame(st.session_state.transactions))

# ================= WALLET =================
elif page=="Wallet":

    st.title("💰 Wallet")
    st.metric("Wallet Balance", f"₹{wallet_balance}")
    st.metric("Total Balance", f"₹{round(total_balance,2)}")

    amt = st.number_input("Amount",100)

    if st.button("Add Funds"):
        st.session_state.wallets[phone] += amt
        st.success("💰 Added via PhonePe")

    if st.button("Withdraw"):
        st.session_state.wallets[phone] -= amt
        st.warning("📤 Sent to PhonePe")

# ================= PROFILE =================
elif page=="Profile":

    st.title("👤 Profile")

    user = st.session_state.users.get(phone, {})

    if "edit_profile" not in st.session_state:
        st.session_state.edit_profile = False

    if st.button("✏️ Edit Profile"):
        st.session_state.edit_profile = True

    name = st.text_input("Name", user.get("name",""), disabled=not st.session_state.edit_profile)
    email = st.text_input("Email", user.get("email",""), disabled=not st.session_state.edit_profile)
    pan = st.text_input("PAN", user.get("pan",""), disabled=not st.session_state.edit_profile)
    phone_no = st.text_input("Phone", user.get("phone",""), disabled=not st.session_state.edit_profile)

    client_id = user.get("client_id","QT1001")
    st.write(f"Client ID: {client_id}")

    if st.button("Save"):
        st.session_state.users[phone] = {
            "name":name,
            "email":email,
            "pan":pan,
            "phone":phone_no,
            "client_id":client_id
        }
        st.success("Saved")

    if st.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.rerun()

# ================= SIGNUP =================
elif page=="Signup":

    st.title("📝 Register")

    name = st.text_input("Name")
    email = st.text_input("Email")
    pan = st.text_input("PAN Number")
    phone_input = st.text_input("Phone Number")   # ✅ NEW

    if "email_otp" not in st.session_state:
        st.session_state.email_otp = None
    if "pan_otp" not in st.session_state:
        st.session_state.pan_otp = None
    if "email_verified" not in st.session_state:
        st.session_state.email_verified = False
    if "pan_verified" not in st.session_state:
        st.session_state.pan_verified = False

    col1,col2 = st.columns([3,1])
    with col1:
        email_otp_input = st.text_input("Enter Email OTP")
    with col2:
        if st.button("Send OTP (Email)"):
            otp = str(random.randint(100000,999999))
            st.session_state.email_otp = otp
            send_email_otp(email, otp, "Email")

    if st.button("Verify Email OTP"):
        if email_otp_input == st.session_state.email_otp:
            st.session_state.email_verified = True
            st.success("Email Verified")

    col3,col4 = st.columns([3,1])
    with col3:
        pan_otp_input = st.text_input("Enter PAN OTP")
    with col4:
        if st.button("Send OTP (PAN)"):
            otp = str(random.randint(100000,999999))
            st.session_state.pan_otp = otp
            send_email_otp(email, otp, "PAN")

    if st.button("Verify PAN OTP"):
        if pan_otp_input == st.session_state.pan_otp:
            st.session_state.pan_verified = True
            st.success("PAN Verified")

    if st.button("Register"):
        if st.session_state.email_verified and st.session_state.pan_verified:
            st.session_state.users[phone] = {
                "name": name,
                "email": email,
                "pan": pan,
                "phone": phone_input,
                "client_id":"QT1001"
            }
            st.success("Registered Successfully 🎉")
        else:
            st.error("Verify Email & PAN first")

# ================= SETTINGS =================
elif page=="Settings":

    st.title("⚙ Change Login")

    new_user = st.text_input("New Username")
    new_pass = st.text_input("New Password")

    if st.button("Update Login"):
        st.session_state.credentials = {
            "username": new_user,
            "password": new_pass
        }
        st.success("Updated")