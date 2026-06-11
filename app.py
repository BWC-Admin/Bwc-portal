import streamlit as st
import sqlite3
import pandas as pd
import os
import base64
import requests
from datetime import datetime

# --- DATABASE ENGINE ---
def get_db_connection():
    return sqlite3.connect("church_funeral.db")

# --- ARKESEL API V2 ---
def send_arkesel_sms(api_key, sender_id, phone, message):
    # Force the app to use your Streamlit secrets automatically if none are typed
    if not api_key:
        api_key = st.secrets.get("ARKESEL_API_KEY", "")
    if not sender_id or sender_id == "BWC":
        sender_id = st.secrets.get("SENDER_ID", "BWC")

    phone_str = str(phone).strip().replace(" ", "")
    if phone_str.startswith('0'):
        phone_str = '233' + phone_str[1:]
    phone_str = str(phone).strip().replace(" ", "")
    if phone_str.startswith('0'):
        phone_str = '233' + phone_str[1:]
    elif not phone_str.startswith('233') and not phone_str.startswith('+'):
        phone_str = '233' + phone_str

    url = "https://sms.arkesel.com/api/v2/sms/send"
    headers = {
        "api-key": api_key,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    payload = {
        "sender": sender_id,
        "message": message,
        "recipients": [phone_str]
    }
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        return response.json()
    except Exception as e:
        return {"status": "error", "message": str(e)}

# --- INITIALIZE TABLES ---
def init_db():
    conn = get_db_connection()
    conn.execute("CREATE TABLE IF NOT EXISTS members (member_code TEXT PRIMARY KEY, member_name TEXT, phone_number TEXT)")
    conn.execute("CREATE TABLE IF NOT EXISTS contributions (id INTEGER PRIMARY KEY AUTOINCREMENT, member_code TEXT, amount_paid REAL)")
    conn.execute("CREATE TABLE IF NOT EXISTS funerals (id INTEGER PRIMARY KEY AUTOINCREMENT, funeral_name TEXT, levy_amount REAL)")
    conn.commit()
    conn.close()

init_db()

# --- CONFIGURATION LAYER ---
st.set_page_config(page_title="BWC Philadelphia Portal", layout="wide", page_icon="⛪")

# --- CUSTOM FONTS & PREMIUM DESIGN ENGINE ---
st.markdown("""
    <link rel='preconnect' href='https://fonts.googleapis.com'>
    <link rel='preconnect' href='https://fonts.gstatic.com' crossorigin>
    <link href='https://fonts.googleapis.com/css2?family=Cinzel:wght@600;700&family=Inter:wght@300;400;600;700&display=swap' rel='stylesheet'>
    
    <style>
    /* Global Font Overrides */
    html, body, [class*="css"], .stMarkdown p, label {
        font-family: 'Inter', sans-serif !important;
    }
    
    /* Luxury Header Typography */
    h1, h2, h3, .church-title {
        font-family: 'Cinzel', serif !important;
        letter-spacing: 1px;
    }

    /* Premium Content Cards */
    .premium-card {
        background: rgba(255, 255, 255, 0.95) !important;
        padding: 30px;
        border-radius: 16px;
        box-shadow: 0 10px 30px rgba(9, 26, 51, 0.08);
        margin-bottom: 25px;
        border-top: 4px solid #d4af37 !important;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #091a33 !important;
        border-right: 3px solid #d4af37 !important;
    }
    section[data-testid="stSidebar"] h3, section[data-testid="stSidebar"] label, section[data-testid="stSidebar"] p {
        color: #ffffff !important;
    }

    /* Custom Premium Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        padding-bottom: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: rgba(255, 255, 255, 0.8) !important;
        border: 1px solid #e2e8f0 !important;
        padding: 12px 28px !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        color: #091a33 !important;
        transition: all 0.3s ease;
    }
    .stTabs [aria-selected="true"] {
        background: #091a33 !important;
        color: #d4af37 !important;
        border: 1px solid #d4af37 !important;
        box-shadow: 0 4px 15px rgba(9, 26, 51, 0.15);
    }

    /* Injection to make form elements look great inside the login frame */
    div[data-testid="stForm"] {
        border: none !important;
        padding: 0 !important;
    }

    /* Print Formatting */
    @media print {
        section[data-testid="stSidebar"], header, footer, button, .stTabs [data-baseweb="tab-list"] { display: none !important; }
        .stApp::before { display: none !important; }
        .premium-card { border: 1px solid #000 !important; background: #fff !important; box-shadow: none !important; }
    }
    </style>
""", unsafe_allow_html=True)

# --- BACKDROP WATERMARK SYSTEM ---
image_folder = "church_photos"
b64_slides = []
if os.path.exists(image_folder):
    found_files = sorted([f for f in os.listdir(image_folder) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
    for img_name in found_files[:8]:
        try:
            with open(os.path.join(image_folder, img_name), "rb") as f:
                b64_slides.append(f"data:image/jpg;base64,{base64.b64encode(f.read()).decode()}")
        except Exception:
            continue

if b64_slides:
    duration = len(b64_slides) * 7
    keyframes = "".join([f"{(i/len(b64_slides))*100:.2f}% {{ background-image: linear-gradient(rgba(244,246,249,0.85), rgba(244,246,249,0.85)), url('{url}'); }}" for i, url in enumerate(b64_slides)])
    st.markdown(f"<style>.stApp::before {{ content: ''; display: block; position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background-size: cover; background-position: center; background-repeat: no-repeat; z-index: 0; animation: bwcAnim {duration}s infinite ease-in-out; }} .stMainBlockContainer, [data-testid='stSidebarContent'] {{ position: relative; z-index: 1; }} @keyframes bwcAnim {{ {keyframes} }}</style>", unsafe_allow_html=True)

# --- SECURE PORTAL GATEHOUSE ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
    st.session_state['role'] = None

if not st.session_state['logged_in']:
    _, col_center, _ = st.columns([1, 1.2, 1])
    with col_center:
        st.markdown("<div style='height: 60px;'></div>", unsafe_allow_html=True)
        
        # HTML Header Wrapper block
        st.markdown("""
            <div style='background: rgba(255, 255, 255, 0.98); padding: 35px 35px 5px 35px; border-radius: 20px 20px 0 0; box-shadow: 0 15px 35px rgba(9, 26, 51, 0.15); border-top: 6px solid #091a33; text-align: center;'>
                <h2 style='color: #091a33; margin-bottom: 5px; font-size: 24px; margin-top:0;'>⛪ BWC PHILADELPHIA</h2>
                <p style='color: #d4af37; font-weight: bold; margin-top: 0; font-size: 13px; letter-spacing: 2px;'>SECURE ACCESS GATEWAY</p>
                <hr style='border: 0; border-top: 1px solid #eee; margin-bottom: 10px;'>
            </div>
        """, unsafe_allow_html=True)
        
        # The form fields are nested directly inside the matching white background wrapper block
        with st.form("portal_login_form"):
            st.markdown("<div style='background: rgba(255, 255, 255, 0.98); padding: 0 35px 35px 35px; box-shadow: 0 15px 35px rgba(9, 26, 51, 0.15); border-radius: 0 0 20px 20px; border-bottom: 4px solid #d4af37;'>", unsafe_allow_html=True)
            username = st.text_input("Access Account ID", placeholder="e.g. admin1")
            password = st.text_input("Security Passphrase", type="password", placeholder="••••••••")
            st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
            submit_login = st.form_submit_button("Authorize & Open Ledger", use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
            if submit_login:
                # 📝 MANAGE/CHANGE SYSTEM CREDENTIALS RIGHT HERE:
                if username.lower() in ["admin1", "admin2"] and password == "2000@Philip@19":
                    st.session_state['logged_in'] = True
                    st.session_state['role'] = "Admin"
                    st.rerun()
                elif username.lower() in ["secretary", "sec1", "sec2"] and password == "bwcsec2026":
                    st.session_state['logged_in'] = True
                    st.session_state['role'] = "Secretary"
                    st.rerun()
                else:
                    st.error("🔒 Identity verification mismatch. Please try again.")
        st.stop()

# --- GOLD & NAVY BRANDING BANNER ---
st.markdown(f"""
    <div style='background: linear-gradient(135deg, #091a33 0%, #132e59 100%); padding: 35px; border-radius: 16px; margin-bottom: 30px; border-bottom: 5px solid #d4af37; box-shadow: 0 10px 25px rgba(9,26,51,0.15);'>
        <div style='display: flex; justify-content: space-between; align-items: center;'>
            <div>
                <h1 style='color: white; margin: 0; font-size: 26px; font-weight: 700;'>BELIEVERS WORSHIP CENTER</h1>
                <p style='color: #d4af37; margin: 4px 0 0 0; font-weight: 600; font-size: 13px; letter-spacing: 2px;'>PHILADELPHIA MOVEMENT • FINANCIAL LEDGER</p>
            </div>
            <div style='background: rgba(212, 175, 55, 0.15); border: 1px solid #d4af37; padding: 6px 16px; border-radius: 30px; color: #d4af37; font-weight: bold; font-size: 12px;'>
                Active Profile: {st.session_state['role']}
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

# --- SIDEBAR CONTROL TOWER ---
st.sidebar.markdown(f"<div style='text-align: center; padding: 10px; border-radius: 10px; background: rgba(255,255,255,0.05); margin-bottom: 20px;'><h3 style='margin:0; font-size:16px; color:#d4af37;'>{st.session_state['role']} Console</h3></div>", unsafe_allow_html=True)
if st.sidebar.button("🚪 Close System Session", use_container_width=True):
    st.session_state['logged_in'] = False
    st.session_state['role'] = None
    st.rerun()

ark_api_key = ""
ark_sender_id = "BWC"
sms_toggle = False

if st.session_state['role'] == "Admin":
    st.sidebar.markdown("<br><h3 style='font-size:14px; color:#d4af37;'>⚙️ LEDGER CONTROL TOWER</h3>", unsafe_allow_html=True)
    with st.sidebar.expander("➕ Register Funeral Ledger Case", expanded=True):
        with st.form("funeral_form", clear_on_submit=True):
            fun_name = st.text_input("Deceased Member Description")
            fun_levy = st.number_input("Assessment Levy (GH₵)", min_value=0.0, format="%.2f")
            if st.form_submit_button("Publish Case"):
                if fun_name:
                    conn = get_db_connection()
                    conn.execute("INSERT INTO funerals (funeral_name, levy_amount) VALUES (?, ?)", (fun_name, fun_levy))
                    conn.commit(); conn.close(); st.rerun()

    st.sidebar.markdown("<br><h3 style='font-size:14px; color:#d4af37;'>📲 ARKESEL TRANSMISSION ENGINE</h3>", unsafe_allow_html=True)
    default_key = st.secrets.get("ARKESEL_API_KEY", "")
default_sender = st.secrets.get("SENDER_ID", "BWC")

ark_api_key = st.sidebar.text_input("Arkesel Key (v2)", value=default_key, type="password")
ark_sender_id = st.sidebar.text_input("Sender ID Label", value=default_sender)
    sms_toggle = st.sidebar.checkbox("Live Dispatch Mode", value=False)

# --- LEDGER CALCULATIONS ---
conn = get_db_connection()
df_m = pd.read_sql_query("SELECT * FROM members", conn)
total_req_levy = conn.execute("SELECT SUM(levy_amount) FROM funerals").fetchone()[0] or 0.0
total_paid_ledger = conn.execute("SELECT SUM(amount_paid) FROM contributions").fetchone()[0] or 0.0
funeral_count = conn.execute("SELECT COUNT(*) FROM funerals").fetchone()[0] or 0
member_count = len(df_m)
conn.close()

# --- PRIVILEGE-BASED NAVIGATION TABS ---
if st.session_state['role'] == "Admin":
    tabs = st.tabs(["📥 Receipt Entry Desk", "👥 Roster Synchronization", "📋 Case Profiles", "📜 Audit & Ledger Invoices"])
else:
    tabs = st.tabs(["📥 Receipt Entry Desk"])

# --- TAB 1: RECEIPT ENTRY DESK ---
with tabs[0]:
    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.markdown(f"<div style='background: white; padding: 20px; border-radius: 12px; border-left: 4px solid #091a33; box-shadow: 0 4px 15px rgba(0,0,0,0.02);'><b>Congregation Size</b><h2 style='margin:0; color:#091a33;'>{member_count} Profiles</h2></div>", unsafe_allow_html=True)
    kpi2.markdown(f"<div style='background: white; padding: 20px; border-radius: 12px; border-left: 4px solid #d4af37; box-shadow: 0 4px 15px rgba(0,0,0,0.02);'><b>Tracked Events</b><h2 style='margin:0; color:#d4af37;'>{funeral_count} Events</h2></div>", unsafe_allow_html=True)
    kpi3.markdown(f"<div style='background: white; padding: 20px; border-radius: 12px; border-left: 4px solid #28a745; box-shadow: 0 4px 15px rgba(0,0,0,0.02);'><b>Total Funds Deposited</b><h2 style='margin:0; color:#28a745;'>GH₵ {total_paid_ledger:,.2f}</h2></div>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if df_m.empty:
        st.info("👋 Master directory is empty. An administrator must upload the master Excel workbook in the 'Roster Synchronization' tab.")
    else:
        st.markdown("<div class='premium-card'><h3>Log Financial Contribution Receipt</h3>", unsafe_allow_html=True)
        df_m['dropdown_label'] = df_m['member_code'].astype(str) + " — " + df_m['member_name']
        selected_profile = st.selectbox("Search Member Profile", df_m['dropdown_label'])
        
        member_row = df_m[df_m['dropdown_label'] == selected_profile].iloc[0]
        m_code, m_name, m_phone = member_row['member_code'], member_row['member_name'], member_row['phone_number']
        
        conn = get_db_connection()
        already_paid = conn.execute("SELECT SUM(amount_paid) FROM contributions WHERE member_code = ?", (m_code,)).fetchone()[0] or 0.0
        conn.close()
        
        current_balance = total_req_levy - already_paid
        
        mc1, mc2, mc3 = st.columns(3)
        st.markdown(f"**Cumulative Assessment Owed:** GH₵ {total_req_levy:,.2f}")
        st.markdown(f"**Total Contributed:** GH₵ {already_paid:,.2f}")
        st.markdown(f"**Outstanding Balance:** GH₵ {current_balance:,.2f}")
        st.markdown("<br>", unsafe_allow_html=True)

        with st.form("payment_form", clear_on_submit=True):
            cash_amount = st.number_input("Amount Deposited Today (GH₵)", min_value=0.0, format="%.2f")
            if st.form_submit_button("Post Transaction Receipt") and cash_amount > 0:
                conn = get_db_connection()
                conn.execute("INSERT INTO contributions (member_code, amount_paid) VALUES (?, ?)", (m_code, cash_amount))
                conn.commit(); conn.close()
                
                updated_paid = already_paid + cash_amount
                updated_balance = total_req_levy - updated_paid
                
                sms_message = f"BWC Philadelphia: Hello {m_name}, we have acknowledged your contribution of GH₵{cash_amount:,.2f}. Total Paid: GH₵{updated_paid:,.2f}. Balance: GH₵{updated_balance:,.2f}. God bless you."
                st.success(f"🎉 Secure ledger update successful for {m_name}!")
                
                if st.session_state['role'] == "Admin" and sms_toggle:
                    if ark_api_key:
                        api_response = send_arkesel_sms(ark_api_key, ark_sender_id, m_phone, sms_message)
                        st.success("🚀 Arkesel live delivery confirmation received!")
                    else:
                        st.error("❌ Key mismatch error on Admin configuration module.")
                else:
                    st.info("📊 Transaction Notification Log Preview:")
                    st.code(sms_message, language="text")
        st.markdown("</div>", unsafe_allow_html=True)

# --- ADMINISTRATIVE MODULES ---
if st.session_state['role'] == "Admin":
    # TAB 2: ROSTER WORKBOOK INGESTION
    with tabs[1]:
        st.markdown("<div class='premium-card'><h3>Synchronize Roster Workbook</h3>", unsafe_allow_html=True)
        uploaded_file = st.file_uploader("Upload Congregation Excel Spreadsheet (.xlsx)", type=["xlsx"])
        if uploaded_file is not None:
            try:
                df_upload = pd.read_excel(uploaded_file)
                df_upload.columns = [str(c).strip().lower().replace(" ", "_") for c in df_upload.columns]
                df_upload = df_upload.rename(columns={
                    'member_id': 'member_code', 'id': 'member_code', 'code': 'member_code',
                    'name': 'member_name', 'phone': 'phone_number', 'phone_no': 'phone_number'
                })
                conn = get_db_connection()
                df_upload[['member_code', 'member_name', 'phone_number']].to_sql('members', conn, if_exists='replace', index=False)
                conn.close()
                st.success("Roster synchronized and indexed perfectly into the database system layer!")
                st.rerun()
            except Exception as e:
                st.error(f"Spreadsheet compilation error: {e}")
        st.markdown("</div>", unsafe_allow_html=True)

    # TAB 3: FUNERAL CASE MANAGEMENT (EDIT/DELETE DESK)
    with tabs[2]:
        st.markdown("<div class='premium-card'><h3>Active Philadelphia Case Profiles</h3>", unsafe_allow_html=True)
        conn = get_db_connection()
        df_funerals = pd.read_sql_query("SELECT id, funeral_name, levy_amount FROM funerals ORDER BY id DESC", conn)
        conn.close()
        
        if not df_funerals.empty:
            for idx, row in df_funerals.iterrows():
                col_name, col_levy, col_action = st.columns([3, 1, 1])
                col_name.write(f"🏷️ **{row['funeral_name']}**")
                col_levy.write(f"GH₵ {row['levy_amount']:,.2f}")
                
                if col_action.button("🗑️ Void Profile", key=f"del_{row['id']}", use_container_width=True):
                    conn = get_db_connection()
                    conn.execute("DELETE FROM funerals WHERE id = ?", (row['id'],))
                    conn.commit(); conn.close()
                    st.success("Profile safely removed from ledger indexes.")
                    st.rerun()
                st.markdown("<hr style='margin:10px 0; border:0; border-top:1px solid #f1f5f9;'>", unsafe_allow_html=True)
        else:
            st.info("No active profiles tracked inside the database index.")
        st.markdown("</div>", unsafe_allow_html=True)

    # TAB 4: AUDIT HISTORY TRAILS & INVOICING EXPORTS
    with tabs[3]:
        st.markdown("<div class='premium-card'><h3>Master Ledger Audit & Exports</h3>", unsafe_allow_html=True)
        st.markdown("<button onclick='window.print()' style='background: linear-gradient(135deg, #091a33 0%, #132e59 100%); color: white; padding: 12px 24px; border: none; border-radius: 8px; font-weight: bold; cursor: pointer; margin-bottom: 20px;'>🖨️ Export Financial Report to PDF</button>", unsafe_allow_html=True)
        
        conn = get_db_connection()
        df_audit = pd.read_sql_query("""
            SELECT c.id as [Receipt ID], c.member_code as [Member Code], m.member_name as [Full Name], c.amount_paid as [Amount Paid (GH₵)]
            FROM contributions c
            LEFT JOIN members m ON c.member_code = m.member_code
            ORDER BY c.id DESC
        """, conn)
        conn.close()
        
        if not df_audit.empty:
            st.dataframe(df_audit, use_container_width=True)
        else:
            st.info("No logs found inside the audit matrix.")
        st.markdown("</div>", unsafe_allow_html=True)
