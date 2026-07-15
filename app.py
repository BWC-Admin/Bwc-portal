import streamlit as st
import sqlite3
import pandas as pd
import os
import base64
import requests
from datetime import datetime

# --- DATABASE INITIALIZATION ---
def init_db():
    conn = sqlite3.connect("church_database.db")
    c = conn.cursor()
    # Ensure members table exists
    c.execute('''CREATE TABLE IF NOT EXISTS members 
                 (member_name TEXT, phone_number TEXT, branch_name TEXT, member_code TEXT, member_group TEXT)''')
    
    # Ensure funerals table exists with the columns your query likely expects
    c.execute('''CREATE TABLE IF NOT EXISTS funerals 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  funeral_name TEXT, 
                  levy_amount REAL, 
                  group_name TEXT)''')
    
    conn.commit()
    conn.close()

# Always call this at the top of your script
init_db()
# --- CLEAN BRANDING HIDER ---
st.markdown("""
<style>
footer {visibility: hidden;}
.stDeployButton {display:none;}
[data-testid="stHeader"] {background: transparent !important;}
</style>
""", unsafe_allow_html=True)

# --- INDESTRUCTIBLE SIDEBAR TOGGLE TRIGGER ---
st.markdown("""
    <div style="position: fixed; top: 15px; left: 15px; z-index: 9999999;">
        <button onclick="
            var nativeBtn = window.parent.document.querySelector('button[data-testid=\\'collapsedSidebarCollapsedControl\\']');
            if (nativeBtn) { 
                nativeBtn.click(); 
            } else { 
                alert('Sidebar controls are currently unavailable in this layout.'); 
            }
        " style="
            background-color: #1e3a8a;
            color: white;
            border: none;
            padding: 10px 16px;
            font-size: 13px;
            font-weight: 700;
            border-radius: 8px;
            cursor: pointer;
            box-shadow: 0 4px 15px rgba(0,0,0,0.4);
            display: flex;
            align-items: center;
            gap: 8px;
        ">
            ⚙️ Open API Keys Panel
        </button>
    </div>
""", unsafe_allow_html=True)
# --- DATABASE ENGINE ---
def get_db_connection():
    return sqlite3.connect("church_funeral.db")

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Create Funerals table with group categorization
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS funerals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            funeral_name TEXT NOT NULL,
            levy_amount REAL NOT NULL,
            group_name TEXT NOT NULL
        )
    ''')
    
    # 2. Create Members table to hold rosters for both groups
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS members (
            member_code TEXT PRIMARY KEY,
            member_name TEXT NOT NULL,
            phone_number TEXT,
            member_group TEXT NOT NULL
        )
    ''')
    
    # 3. Safety checks to protect old data while migrating columns
    try:
        cursor.execute("ALTER TABLE funerals ADD COLUMN group_name TEXT DEFAULT 'Adom'")
    except sqlite3.OperationalError:
        pass
        
    try:
        cursor.execute("ALTER TABLE members ADD COLUMN member_group TEXT DEFAULT 'Adom'")
    except sqlite3.OperationalError:
        pass
        
    conn.commit()
    conn.close()

init_db()

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
    # 1. Inject Premium CSS Styling for BWC Philadelphia Movement
    st.markdown("""
        <style>
        .stApp {
            background-color: #050a14 !important;
            color: white !important;
        }
        [data-testid="stHeader"] {
            background: transparent !important;
        }
        .hero-container {
            text-align: center;
            padding: 40px 20px 20px 20px;
        }
        .official-badge {
            background: #1e3a8a;
            color: #93c5fd;
            padding: 5px 15px;
            border-radius: 50px;
            font-size: 11px;
            letter-spacing: 2px;
            font-weight: 700;
            display: inline-block;
            margin-bottom: 15px;
            text-transform: uppercase;
        }
        .main-title {
            font-size: 42px;
            font-weight: 800;
            letter-spacing: -1px;
            line-height: 1.2;
            margin-bottom: 10px;
            color: white;
        }
        .main-subtitle {
            font-size: 14px;
            color: #94a3b8;
            max-width: 500px;
            margin: 0 auto 25px auto;
        }
        .login-card {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            padding: 30px;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.5);
            text-align: center;
        }
        .lock-icon-circle {
            width: 65px;
            height: 65px;
            background: #2563eb;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 15px auto;
            font-size: 28px;
            box-shadow: 0 0 20px rgba(37, 99, 235, 0.4);
        }
        div[data-testid="stTextInput"] label {
            color: #94a3b8 !important;
            font-size: 11px !important;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        div[data-testid="stTextInput"] input {
            background: rgba(0, 0, 0, 0.3) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            color: white !important;
            border-radius: 10px !important;
        }
        .stButton > button {
            width: 100% !important;
            background: #2563eb !important;
            color: white !important;
            border: none !important;
            padding: 12px !important;
            border-radius: 10px !important;
            font-weight: 700 !important;
            margin-top: 15px !important;
        }
        .stButton > button:hover {
            background: #1d4ed8 !important;
            box-shadow: 0 0 15px rgba(37, 99, 235, 0.5) !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # 2. Top Header / Lander Content
    st.markdown("""
        <div class="hero-container">
            <div class="official-badge">Official Administrative Standard</div>
            <div class="main-title">BWC PHILADELPHIA<br>MOVEMENT</div>
            <p class="main-subtitle">
                The definitive Movement framework for managing Events, Fiscal Liquidity, and Member Welfare with absolute precision.
            </p>
        </div>
    """, unsafe_allow_html=True)

    # 3. Centered Layout Column Split
    _, col_center, _ = st.columns([1, 2, 1])
    with col_center:
        st.markdown("""
            <div class="login-card">
                <div class="lock-icon-circle">🔐</div>
                <h4 style='color: white; margin-bottom: 5px; font-weight:700;'>SECURE EXECUTIVE ACCESS</h4>
                <p style='color: #64748b; font-size: 12px; margin-bottom: 20px;'>VERIFIED MOVEMENT CREDENTIAL REQUIRED</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Safe form wrap to handle your existing multiple admin list cleanly
        with st.form("portal_login_form"):
            username = st.text_input("Access Account ID", placeholder="e.g. admin1")
            password = st.text_input("Security Passphrase", type="password", placeholder="••••••••")
            submit_login = st.form_submit_button("Authorize & Open Ledger →")
            
            if submit_login:
                if username in ["admin1", "admin2", "admin"] and password in ["admin123", "password123"]: 
                    st.session_state['logged_in'] = True
                    st.session_state['role'] = 'Admin'
                    st.success("Access Granted!")
                    st.rerun()
                else:
                    st.error("Invalid credentials, please try again.")

        if submit_login:
            # 1. MAIN MOTHER BRANCH (ADMIN)
            if username.lower() in ["admin1", "admin2", "admin"] and password in ["2000@Philip@19", "NUNGUA@2026"]:
                st.session_state['logged_in'] = True
                st.session_state['role'] = 'Admin'
                st.session_state['branch'] = 'NUNGUA MAIN (Mother)'
                st.success("🟢 Nungua Main Administration Portal Activated!")
                st.rerun()
                
            # 2. LASHIBI SUB-BRANCH
            elif username.lower() == "lashibi" and password in ["lashibi2026", "LASHIBI@2026"]:
                st.session_state['logged_in'] = True
                st.session_state['role'] = 'Branch User'
                st.session_state['branch'] = 'LASHIBI'
                st.success("🟢 Lashibi Branch Terminal Activated!")
                st.rerun()
                
            # 3. TESHIE SUB-BRANCH
            elif username.lower() == "teshie" and password in ["teshie2026", "TESHIE@2026"]:
                st.session_state['logged_in'] = True
                st.session_state['role'] = 'Branch User'
                st.session_state['branch'] = 'TESHIE'
                st.success("🟢 Teshie Branch Terminal Activated!")
                st.rerun()
                
            # 4. LABADI SUB-BRANCH
            elif username.lower() == "labadi" and password in ["labadi2026", "LABADI@2026"]:
                st.session_state['logged_in'] = True
                st.session_state['role'] = 'Branch User'
                st.session_state['branch'] = 'LABADI'
                st.success("🟢 Labadi Branch Terminal Activated!")
                st.rerun()
                
            # 5. BURMA CAMP SUB-BRANCH
            elif username.lower() == "burmacamp" and password in ["burma2026", "BURMA@2026"]:
                st.session_state['logged_in'] = True
                st.session_state['role'] = 'Branch User'
                st.session_state['branch'] = 'BURMA CAMP'
                st.success("🟢 Burma Camp Branch Terminal Activated!")
                st.rerun()
                
            # 6. GENERAL SECRETARY
            elif username.lower() in ["secretary", "sec1", "sec2"] and password == "bwcsec2026":
                st.session_state['logged_in'] = True
                st.session_state['role'] = 'Secretary'
                st.session_state['branch'] = 'NUNGUA MAIN (Mother)'
                st.success("🟢 Secretarial Access Granted!")
                st.rerun()
                
            # 7. GENERAL DATA ENTRY ROLE
            elif username.lower() in ["entry", "dataentry"] and password == "bwcdata2026":
                st.session_state['logged_in'] = True
                st.session_state['role'] = 'Data Entry'
                st.session_state['branch'] = 'NUNGUA MAIN (Mother)'
                st.success("🟢 General Data Entry Access Granted!")
                st.rerun()
                
            else:
                st.error("🔴 Identity verification mismatch. Please try again.")
                st.stop()
        
        # Stop everything else from showing until they log in
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
            fun_levy = st.number_input("Assessment Levy (GHS)", min_value=0.0, format="%.2f")
            
            # This dropdown allows you to separate Adom and Second Chance
            fun_group = st.selectbox("Assign to Group", ["Adom", "Second Chance"])

            if st.form_submit_button("Publish Case"):
                if fun_name:
                    conn = get_db_connection()
                    # This saves the funeral name, amount, and the group selection
                    conn.execute(
                        "INSERT INTO funerals (funeral_name, levy_amount, group_name) VALUES (?, ?, ?)",
                        (fun_name, fun_levy, fun_group)
                    )
                    
                    # --- AUTOMATED MEMBERS BALANCE CALCULATION & ALERTS ENGINE ---
                    try:
                        # 1. Fetch all previous funeral levies to calculate initial historical balance
                        cursor = conn.cursor()
                        cursor.execute("SELECT SUM(levy_amount) FROM funerals WHERE group_name = ?", (fun_group,))
                        result = cursor.fetchone()
                        
                        # The current case is already inserted, so previous balance subtracts it
                        total_historical_with_new = result[0] if result[0] is not None else 0.0
                        previous_balance = total_historical_with_new - float(fun_levy)
                        new_balance = total_historical_with_new
                        
                        # 2. Get active branch context name from session state
                        active_branch = st.session_state.get('branch', 'NUNGUA MAIN (Mother)')
                        
                        # 3. Pull all registered members from the target group roster
                        cursor.execute("SELECT member_name, phone_number FROM members WHERE member_group = ?", (fun_group,))
                        group_members = cursor.fetchall()
                        
                        # 4. Generate custom real-time alert logs
                        alert_count = 0
                        for member in group_members:
                            # 1. Calculate/Get the balance for this specific member
                            # (Assuming you have a way to get member_balance, like: member_balance = member['balance'])
                            
                            # 2. Define the sms_text INSIDE the loop
                            sms_text = (
                                f"BWC PHILADELPHIA ({active_branch}), "
                                f"NEW FUNERAL ALERT !!!!!!!!!, "
                                f"ADOM 0000!!! ({m_name}) "
                                f"NEW FUNERAL UPDATE FOR ({fun_name}) OF GHC{float(fun_levy):.2f} "
                                f"(TOTAL FUNERAL BALANCE IS GHC{new_balance:.2f}), THANK YOU"
                            )
                                                
                            # 3. Then send it
                            try:
                                clean_phone = str(member['m_phone']).strip()
                                if clean_phone.startswith('0'):
                                    clean_phone = '233' + clean_phone[1:]
                                
                                send_arkesel_sms(None, None, clean_phone, sms_text)
                                st.toast(f"Notification sent to {member['m_name']}", icon="✉️")
                                alert_count += 1
                            except Exception as e:
                                st.error(f"Failed to send to {member['m_name']}: {e}")
                        st.success(f"Success: Processed updates and compiled alerts for {alert_count} '{fun_group}' members.")
                        
                    except Exception as alert_err:
                        st.warning(f"Ledger updated, but notifications failed to calculate: {alert_err}")

                    conn.commit()
                    conn.close()
                    st.rerun()

st.sidebar.markdown("<br><h3 style='font-size:14px; color:#d4af37;'>🔱 ARKESEL TRANSMISSION ENGINE</h3>", unsafe_allow_html=True)
default_key = st.secrets.get("ARKESEL_API_KEY", "")
default_sender = st.secrets.get("SENDER_ID", "BWC")

ark_api_key = st.sidebar.text_input("Arkesel Key (v2)", value=default_key, type="password")
ark_sender_id = st.sidebar.text_input("Sender ID Label", value=default_sender)
sms_toggle = st.sidebar.checkbox("Live Dispatch Mode", value=False)

# --- LEDGER CALCULATIONS (FAIL-SAFE FILTER) ---
conn = get_db_connection()
current_branch = st.session_state.get('branch', 'NUNGUA MAIN (Mother)')
current_role = st.session_state.get('role', 'Branch User')

# --- AUTOMATIC DATABASE COLUMN REPAIR ---
try:
    cursor = conn.cursor()
    cursor.execute("ALTER TABLE members ADD COLUMN branch_name TEXT DEFAULT 'NUNGUA MAIN (Mother)'")
    cursor.execute("ALTER TABLE funerals ADD COLUMN branch_name TEXT DEFAULT 'NUNGUA MAIN (Mother)'")
    cursor.execute("ALTER TABLE contributions ADD COLUMN branch_name TEXT DEFAULT 'NUNGUA MAIN (Mother)'")
    conn.commit()
except Exception:
    pass  # Automatically skips if columns already exist safely

# --- LOAD THE DATA SAFELY BASED ON BRANCH PERMISSIONS ---
if current_role == 'Admin':
    # Mother Branch pulls the entire global dataset
    df_m = pd.read_sql_query("SELECT * FROM members", conn)
    df_funerals = pd.read_sql_query("SELECT * FROM funerals", conn)
    df_contribs = pd.read_sql_query("SELECT * FROM contributions", conn)
else:
    # Sub-branches only pull data tagged with their branch name
    df_m = pd.read_sql_query("SELECT * FROM members WHERE branch_name = ?", conn, params=(current_branch,))
    df_funerals = pd.read_sql_query("SELECT * FROM funerals WHERE branch_name = ?", conn, params=(current_branch,))
    df_contribs = pd.read_sql_query("SELECT * FROM contributions WHERE branch_name = ?", conn, params=(current_branch,))

# Close the database connection ONLY ONCE after all queries are finished
conn.close()
# 2. Dynamic Pandas Filter based on role
if current_role not in ['Admin', 'Secretary', 'Data Entry']:
    # Determine which column name exists in your members table
    branch_col_m = 'branch_name' if 'branch_name' in df_m.columns else ('branch' if 'branch' in df_m.columns else None)
    if branch_col_m:
        df_m = df_m[df_m[branch_col_m].astype(str).str.upper() == str(current_branch).upper()]

    # Filter funerals data
    branch_col_f = 'branch_name' if 'branch_name' in df_funerals.columns else ('branch' if 'branch' in df_funerals.columns else None)
    if branch_col_f and not df_funerals.empty:
        df_funerals = df_funerals[df_funerals[branch_col_f].astype(str).str.upper() == str(current_branch).upper()]

    # Filter contributions data
    branch_col_c = 'branch_name' if 'branch_name' in df_contribs.columns else ('branch' if 'branch' in df_contribs.columns else None)
    if branch_col_c and not df_contribs.empty:
        df_contribs = df_contribs[df_contribs[branch_col_c].astype(str).str.upper() == str(current_branch).upper()]

# 3. Calculate final metric values from the filtered DataFrames
member_count = len(df_m)

try:
    total_req_levy = float(df_funerals['levy_amount'].sum()) if 'levy_amount' in df_funerals.columns else 0.0
except Exception:
    total_req_levy = 0.0

try:
    total_paid_ledger = float(df_contribs['amount_paid'].sum()) if 'amount_paid' in df_contribs.columns else 0.0
except Exception:
    total_paid_ledger = 0.0

funeral_count = len(df_funerals)

# --- PRIVILEGE-BASED NAVIGATION TABS ---
if st.session_state['role'] == "Admin":
    tabs = st.tabs(["📥 Receipt Entry Desk", "👥 Roster Synchronization", "📋 Case Profiles", "📜 Audit & Ledger Invoices"])
else:
    tabs = st.tabs(["📥 Receipt Entry Desk"])

# --- TAB 1: RECEIPT ENTRY DESK ---
with tabs[0]:
   
    # --- KEEP YOUR EXISTING CODE BELOW THIS ---
    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.markdown(f"<div style='background: white; padding: 20px; border-radius: 12px; border-left: 4px solid #091a33; box-shadow: 0 4px 15px rgba(0,0,0,0.02);'><b>Congregation Size</b><h2 style='margin:0; color:#091a33;'>{member_count} Profiles</h2></div>", unsafe_allow_html=True)
    kpi2.markdown(f"<div style='background: white; padding: 20px; border-radius: 12px; border-left: 4px solid #d4af37; box-shadow: 0 4px 15px rgba(0,0,0,0.02);'><b>Tracked Events</b><h2 style='margin:0; color:#d4af37;'>{funeral_count} Events</h2></div>", unsafe_allow_html=True)
    kpi3.markdown(f"<div style='background: white; padding: 20px; border-radius: 12px; border-left: 4px solid #28a745; box-shadow: 0 4px 15px rgba(0,0,0,0.02);'><b>Total Funds Deposited</b><h2 style='margin:0; color:#28a745;'>GH₵ {total_paid_ledger:,.2f}</h2></div>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    # --- ADMIN BRANCH SUMMARY TABLE ---
    if current_role == 'Admin' and not df_m.empty:
        st.write("### 🏢 Branch Performance Breakdown")
        st.dataframe(df_m['branch_name'].value_counts().reset_index(name='Total Members').rename(columns={'index': 'Branch Location'}), use_container_width=True, hide_index=True)
        st.write("---")
            
    if df_m.empty:
        st.info("ℹ️ No registered members found for this branch profile.")
    else:
        st.markdown("<div class='premium-card'><h3>Log Financial Contribution Receipt</h3></div>", unsafe_allow_html=True)
        # --- DYNAMIC BRANCH CONTACT DETAILS FOR RECEIPTS ---
        current_branch = st.session_state.get('branch', 'NUNGUA MAIN (Mother)')
        
        if current_branch == 'NUNGUA MAIN (Mother)':
            st.markdown("<p style='text-align: center; color: gray;'>🏢 Headquarters: Nungua, Accra | 📞 Phone: +233 24 000 0001</p>", unsafe_allow_html=True)
        elif current_branch == 'LABADI':
            st.markdown("<p style='text-align: center; color: gray;'>🏢 Labadi Assembly Location | 📞 Phone: +233 24 000 0002</p>", unsafe_allow_html=True)
        else:
            st.markdown(f"<p style='text-align: center; color: gray;'>🏢 {current_branch} Assembly | 📞 Contact Admin for details</p>", unsafe_allow_html=True)
            
        st.write("---")
        df_m['dropdown_label'] = df_m['member_code'].astype(str) + " - " + df_m['member_name']
        selected_profile = st.selectbox("Search Member Profile", df_m['dropdown_label'].unique())
        
        member_row = df_m[df_m['dropdown_label'] == selected_profile].iloc[0]
        m_code = member_row['member_code']
        m_name = member_row['member_name']
        m_phone = member_row['phone_number']
        
        conn = get_db_connection()
        clean_code = str(m_code).strip()
        
        already_paid_res = conn.execute(
            "SELECT SUM(amount_paid) FROM contributions WHERE TRIM(CAST(member_code AS TEXT)) = ?", 
            (clean_code,)
        ).fetchone()
        already_paid = already_paid_res[0] if already_paid_res and already_paid_res[0] is not None else 0.0
        conn.close()
        
        current_balance = float(total_req_levy) - float(already_paid)
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
             
            st.markdown("<div class='premium-card'><h3>👥 Roster Synchronization Desk</h3></div>", unsafe_allow_html=True)
            
            # Selectors for Group and Branch tracking
            col_grp, col_br = st.columns(2)
            with col_grp:
                upload_group = st.selectbox("🎯 Target Allocation Group", ["Adom", "Second Chance"])
            with col_br:
                upload_branch = st.selectbox("🏢 Originating Data Branch", [
                    "NUNGUA MAIN (Mother)", 
                    "LASHIBI", 
                    "TESHIE", 
                    "LABADI", 
                    "BURMA CAMP"
                ])
           # --- INSERT THIS CODE HERE ---
            st.markdown("---") # Adds a visual separator
            
            # This uploader uses the values from the dropdowns above
            uploaded_file = st.file_uploader(f"Upload Excel for {upload_group} - {upload_branch}", type=["xlsx", "csv"])
            
    
    if uploaded_file is not None:
        try:
            # 1. Read the Excel file
            df_new = pd.read_excel(uploaded_file)
            
            # 2. Add the Branch and Group columns 
            df_new['branch_name'] = upload_branch
            df_new['group_name'] = upload_group
            
            # 3. CRITICAL: Only keep columns that the database expects 
            # Modify these names to match your EXACT database column names
            # You can see your column names by looking at where you defined your table
            required_columns = ['member_code', 'member_name', 'phone_number', 'branch_name', 'group_name']
            df_new = df_new[[col for col in required_columns if col in df_new.columns]]
            
            # 4. Save to database
            conn = get_db_connection()
            df_new.to_sql('members', conn, if_exists='append', index=False)
            conn.close()
            
            st.success(f"Successfully synced {len(df_new)} members to {upload_branch}!")
            st.rerun()
            
        except Exception as e:
            st.error(f"Actual error: {e}")
            st.write("Please ensure your Excel column names match the system requirements.")
    # TAB 3: FUNERAL CASE MANAGEMENT (EDIT/DELETE DESK)
    with tabs[2]:
        st.markdown("<div class='premium-card'><h3>Active Philadelphia Case Profiles</h3>", unsafe_allow_html=True)
        conn = get_db_connection()
        df_funerals = pd.read_sql_query("SELECT id, funeral_name, levy_amount, group_name FROM funerals ORDER BY id DESC", conn)
        conn.close()

        if not df_funerals.empty:
            for idx, row in df_funerals.iterrows():
                col_name, col_levy, col_action = st.columns([3, 1, 1])
                col_name.write(f"🏷️ **{row['group_name']}**: {row['funeral_name']}")
                col_levy.write(f"GHS {row['levy_amount']:.2f}")
                
                if col_action.button("🗑️ Void Profile", key=f"del_{row['id']}", use_container_width=True):
                    conn = get_db_connection()
                    conn.execute("DELETE FROM funerals WHERE id = ?", (row['id'],))
                    conn.commit()
                    conn.close()
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
        
        # 1. Group Selector Filter Dropdown
        selected_group = st.selectbox("🎯 Filter Ledger View By Group", ["All Groups", "Adom", "Second Chance"])
    
        conn = get_db_connection()
    
    # 2. Build Query based on chosen group filter
        query = """
        SELECT c.id as [Receipt ID], c.member_code as [Member Code],
        m.member_name as [Full Name], c.amount_paid as [Amount Paid (GH₵)],
        m.member_group as [Group]
        FROM contributions c
        LEFT JOIN members m ON c.member_code = m.member_code
        """
        if selected_group != "All Groups":
            query += f" WHERE m.member_group = '{selected_group}'"
        
        query += " ORDER BY c.id DESC"
    
        # Replace your existing pd.read_sql_query lines with this pattern
        try:
            conn = sqlite3.connect("church_database.db")
            df_audit = pd.read_sql_query(query, conn)
            conn.close()

        # Check if the dataframe is empty or missing the expected column
            if not df_audit.empty and "Receipt ID" in df_audit.columns:
                st.dataframe(df_audit, use_container_width=True)
            else:
                st.info("No records found in this category.")
                
        except Exception as e:
                st.warning("Database records are currently unavailable.")
                df_audit = pd.DataFrame() # Create empty DF to prevent downstream errors
            
        if not df_audit.empty:
                # Display the filtered dataframe table
                st.dataframe(df_audit, use_container_width=True)
        
        st.markdown("---")
        ### 🛠️ ADMINISTRATIVE DELETION DESK ###
        st.markdown("### 🗑️ Void / Delete a Receipt Record")
        
        # Pull list of active receipt IDs for selection drop down
        if "Receipt ID" in df_audit.columns:
            receipt_list = df_audit["Receipt ID"].tolist()
        else:
            receipt_list = []
        
        receipt_to_delete = st.selectbox("Select Receipt ID to permanently remove:", receipt_list)
        
        if st.button("❌ Confirm Permanent Deletion", type="primary"):
            try:
                conn.execute("DELETE FROM contributions WHERE id = ?", (receipt_to_delete,))
                conn.commit()
                st.success(f"Receipt ID #{receipt_to_delete} successfully wiped from ledger records!")
                st.rerun()
            except Exception as e:
                st.error(f"Error handling deletion execution: {e}")
        else:
            st.info(f"No financial entries found in the database matching the '{selected_group}' matrix filter.")
        
        conn.close()
        st.markdown("</div>", unsafe_allow_html=True)
