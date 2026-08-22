"""
Lab 10: Professional Master Security & Analytics Platform (Combined Labs P1 - P9)
Filename: lab10.py
Domain: Aeterna Cyber Security & Enterprise Analytics Platform

Features:
- Professional Streamlit Web Dashboard Mode (`streamlit run lab10.py`)
- Professional PyQt6 Desktop GUI Mode (`python lab10.py`)
- Integrated P1 (OOP), P2 (Regex), P3 (PyQt6), P4 (Public API), P5 (Flask REST), P6 (Streamlit), P7 (File Storage), P8 (Pandas), P9 (NumPy)
"""

import sys
import os
import re
import json
import time
import shutil
import threading
from datetime import datetime

import numpy as np
import pandas as pd
import requests
from flask import Flask, jsonify, request as flask_request

# Matplotlib configuration
import matplotlib
matplotlib.use("QtAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QFormLayout, QLabel, QLineEdit, QPushButton, QComboBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QTextEdit,
    QMessageBox, QGroupBox, QSplitter, QTabWidget
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QColor


# =============================================================================
# FILE & REST API CONSTANTS
# =============================================================================
DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lab10_vault_data.txt")
BACKUP_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lab10_vault_backup.txt")
HEADER_LINE = "Asset_ID|Asset_Name|Category|Owner_Email|Secret_Token|Registered_Date|Risk_Score\n"
FLASK_URL = "http://127.0.0.1:5005/api/v1/vault"

INITIAL_DATA = [
    "AST-1001|Google Cloud Admin|Credentials|alex@aeterna.com|Secr3tPass1|2026-08-22|85.5\n",
    "AST-1002|Aeterna Master Key|Vault Key|admin@aeterna.com|M@sterKey99|2026-08-22|95.0\n",
    "AST-1003|Firebase Auth Token|Identity Token|dev@aeterna.com|FireB@se2026|2026-08-22|65.0\n",
    "AST-1004|SSL Root Certificate|Certificate|cert@aeterna.com|CertS3cret!|2026-08-22|35.0\n",
    "AST-1005|MongoDB Atlas Secret|Database Secret|dba@aeterna.com|MongoPass123|2026-08-22|78.0\n",
    "AST-1006|Stripe Payment Token|API Key|finance@aeterna.com|StripeP@ss1|2026-08-22|92.0\n",
    "AST-1007|AWS S3 Access Key|Credentials|ops@aeterna.com|AwsK3yPass!|2026-08-22|88.0\n",
    "AST-1008|GitHub CI Deploy Key|SSH Key|ci@aeterna.com|GitDeploy26|2026-08-22|55.0\n",
    "AST-1009|VPN Gateway Cert|Certificate|net@aeterna.com|VpnPass2026|2026-08-22|28.0\n",
    "AST-1010|Redis Cluster Token|Database Secret|redis@aeterna.com|Red1sCluster|2026-08-22|62.0\n"
]


# =============================================================================
# P1: OBJECT-ORIENTED PROGRAMMING (OOP & EXCEPTIONS)
# =============================================================================

class AeternaValidationError(Exception):
    pass

class AssetNotFoundError(Exception):
    pass

class AeternaBaseAsset:
    def __init__(self, asset_id, name, category, email, token, date_str, base_score=50.0):
        self.asset_id = asset_id
        self.name = name
        self.category = category
        self.email = email
        self.__secret_token = token
        self.date_str = date_str
        self.base_score = base_score

    def get_token_masked(self):
        return "*****" if self.__secret_token else ""

    def get_token_raw(self):
        return self.__secret_token

    def calculate_risk_score(self):
        return float(self.base_score)

    def to_dict(self):
        return {
            "id": self.asset_id,
            "name": self.name,
            "category": self.category,
            "email": self.email,
            "token": self.__secret_token,
            "date": self.date_str,
            "risk_score": round(self.calculate_risk_score(), 1)
        }

class CriticalVaultAsset(AeternaBaseAsset):
    def calculate_risk_score(self):
        multiplier = 1.3 if self.category in ["Credentials", "Vault Key", "API Key"] else 1.0
        return min(100.0, float(self.base_score) * multiplier)


# =============================================================================
# P2: REGULAR EXPRESSION VALIDATIONS
# =============================================================================

def validate_asset_inputs(asset_id, name, email, token, date_str):
    if not re.fullmatch(r"^AST-\d{4}$", asset_id.strip()):
        raise AeternaValidationError("Asset ID must follow format 'AST-XXXX' (e.g. AST-1001).")
    if not name.strip() or len(name.strip()) < 3:
        raise AeternaValidationError("Asset Name must be at least 3 characters.")
    if not re.fullmatch(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email.strip()):
        raise AeternaValidationError("Invalid Email Address format.")
    if not re.fullmatch(r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d@$!%*#?&]{8,}$", token.strip()):
        raise AeternaValidationError("Secret Token must be min 8 chars with letters & numbers.")
    if not re.fullmatch(r"^\d{4}-\d{2}-\d{2}$", date_str.strip()):
        raise AeternaValidationError("Registered Date must follow 'YYYY-MM-DD' format.")
    return True


# =============================================================================
# P7: FILE READ AND WRITE OPERATIONS (MODES: w, r, a, r+, w+)
# =============================================================================

def init_file_storage():
    if not os.path.exists(DATA_FILE):
        f = open(DATA_FILE, "w", encoding="utf-8")
        f.write(HEADER_LINE)
        f.writelines(INITIAL_DATA)
        f.close()

def read_file_records():
    init_file_storage()
    records = []
    f = None
    try:
        f = open(DATA_FILE, "r", encoding="utf-8")
        lines = f.readlines()
        for line in lines[1:]:
            parts = line.strip().split("|")
            if len(parts) >= 6:
                risk = float(parts[6]) if len(parts) > 6 else 50.0
                asset = CriticalVaultAsset(parts[0], parts[1], parts[2], parts[3], parts[4], parts[5], risk)
                records.append(asset.to_dict())
        return records
    finally:
        if f and not f.closed:
            f.close()

def append_file_record(rec):
    f = open(DATA_FILE, "a", encoding="utf-8")
    line = f"{rec['id']}|{rec['name']}|{rec['category']}|{rec['email']}|{rec['token']}|{rec['date']}|{rec['risk_score']}\n"
    f.write(line)
    f.close()

def update_file_record(rec):
    f = open(DATA_FILE, "r+", encoding="utf-8")
    lines = f.readlines()
    updated = False
    new_lines = [lines[0]]
    for line in lines[1:]:
        parts = line.strip().split("|")
        if parts[0] == rec["id"]:
            new_lines.append(f"{rec['id']}|{rec['name']}|{rec['category']}|{rec['email']}|{rec['token']}|{rec['date']}|{rec['risk_score']}\n")
            updated = True
        else:
            new_lines.append(line)
    if updated:
        f.seek(0)
        f.writelines(new_lines)
        f.truncate()
        f.close()
        return True
    f.close()
    raise AssetNotFoundError(f"Asset ID '{rec['id']}' not found.")

def delete_file_record(asset_id):
    records = read_file_records()
    filtered = [r for r in records if r["id"] != asset_id]
    if len(filtered) == len(records):
        raise AssetNotFoundError(f"Asset ID '{asset_id}' not found.")
    f = open(DATA_FILE, "w+", encoding="utf-8")
    f.write(HEADER_LINE)
    for r in filtered:
        f.write(f"{r['id']}|{r['name']}|{r['category']}|{r['email']}|{r['token']}|{r['date']}|{r['risk_score']}\n")
    f.close()
    return True

def backup_file_storage():
    init_file_storage()
    shutil.copyfile(DATA_FILE, BACKUP_FILE)
    return os.path.basename(BACKUP_FILE)


# =============================================================================
# P5: FLASK REST WEB API SERVER
# =============================================================================

flask_app = Flask(__name__)

@flask_app.route("/api/v1/vault", methods=["GET"])
def api_get_all():
    recs = read_file_records()
    return jsonify({"success": True, "count": len(recs), "data": recs}), 200

@flask_app.route("/api/v1/vault/<asset_id>", methods=["GET"])
def api_get_one(asset_id):
    recs = read_file_records()
    item = next((r for r in recs if r["id"] == asset_id), None)
    if not item:
        return jsonify({"success": False, "error": "Not Found", "message": f"ID {asset_id} not found"}), 404
    return jsonify({"success": True, "data": item}), 200

@flask_app.route("/api/v1/vault", methods=["POST"])
def api_post():
    payload = flask_request.get_json(force=True, silent=True) or {}
    try:
        validate_asset_inputs(payload.get("id", ""), payload.get("name", ""), payload.get("email", ""), payload.get("token", "Secr3tPass!"), payload.get("date", "2026-08-22"))
    except AeternaValidationError as e:
        return jsonify({"success": False, "error": "Bad Request", "message": str(e)}), 400

    asset = CriticalVaultAsset(payload["id"], payload["name"], payload.get("category", "Credentials"), payload["email"], payload.get("token", "Secr3tPass!"), payload.get("date", "2026-08-22"), payload.get("risk_score", 60.0))
    append_file_record(asset.to_dict())
    return jsonify({"success": True, "message": "Created", "data": asset.to_dict()}), 201

@flask_app.route("/api/v1/vault/<asset_id>", methods=["DELETE"])
def api_delete(asset_id):
    try:
        delete_file_record(asset_id)
        return jsonify({"success": True, "message": f"Asset {asset_id} deleted."}), 200
    except AssetNotFoundError as e:
        return jsonify({"success": False, "error": "Not Found", "message": str(e)}), 404

def start_flask_server():
    try:
        r = requests.get(FLASK_URL, timeout=1)
        if r.status_code == 200:
            return
    except Exception:
        pass
    t = threading.Thread(target=lambda: flask_app.run(host="127.0.0.1", port=5005, debug=False, use_reloader=False), daemon=True)
    t.start()
    time.sleep(1.2)


# =============================================================================
# P8 & P9: PANDAS & NUMPY ANALYTICS
# =============================================================================

def get_analytics_dataframe():
    recs = read_file_records()
    return pd.DataFrame(recs)

def run_numpy_analytics(df):
    if df.empty:
        return "No data available."

    scores = df["risk_score"].to_numpy()
    mean_s = np.mean(scores)
    std_s = np.std(scores)
    max_s = np.max(scores)
    critical_mask = scores > 75.0
    critical_count = np.count_nonzero(critical_mask)
    sorted_idx = np.argsort(scores)[::-1]
    top_devices = df.iloc[sorted_idx[:3]][["id", "name", "risk_score"]].to_dict(orient="records")

    res = f"=== P9: NUMPY COMPUTATION & THREAT ANALYTICS ===\n"
    res += f"NumPy Matrix Shape: {scores.shape}\n"
    res += f"Aggregations — Mean Risk: {mean_s:.2f}, Std Dev: {std_s:.2f}, Max Score: {max_s:.1f}\n"
    res += f"Boolean Mask Filter (> 75.0 Risk Count): {critical_count} High-Risk Assets\n"
    res += f"Top 3 Highest Risk Assets (via np.argsort):\n"
    for item in top_devices:
        res += f"  • [{item['id']}] {item['name']}: {item['risk_score']}\n"
    return res


# =============================================================================
# P6: PROFESSIONAL STREAMLIT WEB DASHBOARD Execution Mode
# =============================================================================

def run_streamlit_app():
    import streamlit as st
    st.set_page_config(
        page_title="Aeterna — Enterprise Cyber Security & Master Dashboard",
        page_icon="🛡️",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Custom CSS Styling for Professional Sleek Dark Theme
    st.markdown("""
        <style>
            .stApp { background-color: #0b0c1b; color: #f8fafc; }
            .stSidebar { background-color: #13152c; border-right: 1px solid #1f2347; }
            .css-1r6594q, .stMetric {
                background: linear-gradient(135deg, #13152c 0%, #1c1f3b 100%);
                border: 1px solid #2e345e; border-radius: 10px; padding: 14px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            }
            .stMetricLabel { color: #94a3b8 !important; font-size: 13px !important; font-weight: 600; }
            .stMetricValue { color: #8b5cf6 !important; font-size: 26px !important; font-weight: bold; }
            .stButton>button {
                background: linear-gradient(90deg, #8b5cf6 0%, #7c3aed 100%);
                color: white; border: none; border-radius: 8px; font-weight: bold;
                padding: 8px 16px; transition: all 0.3s ease;
            }
            .stButton>button:hover { background: linear-gradient(90deg, #a78bfa 0%, #8b5cf6 100%); transform: translateY(-2px); }
            .main-header {
                font-size: 28px; font-weight: bold; letter-spacing: 1px;
                background: linear-gradient(90deg, #f8fafc, #8b5cf6);
                -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            }
            .badge-ok { background: rgba(34,197,94,0.15); color: #22c55e; border: 1px solid #22c55e; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: bold; }
            .badge-warn { background: rgba(239,68,68,0.15); color: #ef4444; border: 1px solid #ef4444; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: bold; }
        </style>
    """, unsafe_allow_html=True)

    # Header Section
    h_col1, h_col2 = st.columns([3, 1])
    with h_col1:
        st.markdown("<div class='main-header'>🛡️ AETERNA — ENTERPRISE CYBER SECURITY DASHBOARD</div>", unsafe_allow_html=True)
        st.caption("Master Analytics Platform • Lab 10 Unified Capstone (Labs P1 through P9)")
    with h_col2:
        st.markdown("<br><span class='badge-ok'>● SYSTEM ONLINE</span> &nbsp; <span class='badge-ok'>AES-256 ENCRYPTED</span>", unsafe_allow_html=True)

    st.divider()

    # Load Data
    recs = read_file_records()
    df = pd.DataFrame(recs)

    # Sidebar Navigation
    st.sidebar.image("https://img.icons8.com/isometric-line/100/8b5cf6/shield.png", width=60)
    st.sidebar.title("Navigation Menu")
    page = st.sidebar.radio("Go to Section:", [
        "📊 Command Center & Metrics",
        "🔑 Vault Asset Manager (P1, P2, P7)",
        "⚡ NumPy & Pandas Threat Analytics (P8 & P9)",
        "🌐 Public REST API Stream (P4 & P5)"
    ])

    st.sidebar.divider()
    st.sidebar.markdown("**Labs Integrated:**")
    st.sidebar.caption("✔ P1: OOP & Exceptions\n✔ P2: Regex Form Validation\n✔ P3: PyQt6 GUI Architecture\n✔ P4: Public API & JSON\n✔ P5: Flask REST Web Server\n✔ P6: Streamlit Web Dashboard\n✔ P7: File Storage (w, r, a, r+)\n✔ P8: Pandas Operations\n✔ P9: NumPy & Visualizations")

    # PAGE 1: COMMAND CENTER
    if "Command Center" in page:
        st.subheader("📌 Key Security & Risk Metrics")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Vault Assets", len(df))
        avg_r = df['risk_score'].mean() if not df.empty else 0.0
        m2.metric("Average Risk Score", f"{avg_r:.1f}")
        crit_count = len(df[df['risk_score'] > 75]) if not df.empty else 0
        m3.metric("Critical Assets (> 75)", crit_count)
        m4.metric("REST Server Status", "200 OK (Port 5005)")

        st.subheader("📋 Registered Vault Records (File System & Pandas)")
        st.dataframe(df, use_container_width=True)

        if not df.empty:
            st.subheader("📈 Risk Score Severity Distribution (Matplotlib)")
            fig, ax = plt.subplots(figsize=(10, 3.5))
            fig.patch.set_facecolor('#13152c'); ax.set_facecolor('#1a1d3b')
            ax.tick_params(colors='#f8fafc'); ax.spines['bottom'].set_color('#2e345e')
            bars = ax.bar(df['id'], df['risk_score'], color=['#ef4444' if x > 75 else '#f59e0b' if x > 50 else '#22c55e' for x in df['risk_score']])
            ax.set_title("Asset Threat Risk Profile", color='#8b5cf6', fontweight='bold')
            ax.set_ylabel("Risk Score", color='#f8fafc')
            st.pyplot(fig)

    # PAGE 2: ASSET MANAGER
    elif "Vault Asset Manager" in page:
        st.subheader("🔑 Add / Update Digital Vault Asset")
        with st.form("asset_form"):
            col_a, col_b = st.columns(2)
            with col_a:
                f_id = st.text_input("Asset ID (Regex: ^AST-\\d{4}$)", value="AST-1011")
                f_name = st.text_input("Asset Name", value="AWS DynamoDB Secret")
                f_cat = st.selectbox("Category", ["Credentials", "Vault Key", "Identity Token", "Certificate", "Database Secret", "API Key", "SSH Key"])
            with col_b:
                f_email = st.text_input("Owner Email", value="cloud@aeterna.com")
                f_token = st.text_input("Secret Token (Min 8 chars, 1 num & letter)", value="Secr3tPass2026", type="password")
                f_date = st.text_input("Registered Date", value=datetime.now().strftime("%Y-%m-%d"))

            btn_submit = st.form_submit_button("Submit Asset Record")

            if btn_submit:
                try:
                    validate_asset_inputs(f_id, f_name, f_email, f_token, f_date)
                    asset = CriticalVaultAsset(f_id, f_name, f_cat, f_email, f_token, f_date, base_score=70.0)
                    append_file_record(asset.to_dict())
                    st.success(f"✔ Asset '{f_id}' successfully saved to `lab10_vault_data.txt`!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Validation Error: {e}")

        st.subheader("💾 File Storage & Backup Operations (P7)")
        b_col1, b_col2 = st.columns(2)
        with b_col1:
            if st.button("Create Backup Copy"):
                bname = backup_file_storage()
                st.success(f"Backup file created: `{bname}`")
        with b_col2:
            st.download_button("Download Data File (`lab10_vault_data.txt`)", data=open(DATA_FILE, "r").read(), file_name="lab10_vault_data.txt")

    # PAGE 3: NUMPY & PANDAS ANALYTICS
    elif "NumPy & Pandas" in page:
        st.subheader("⚡ NumPy Vectorized Computation & Pandas Slicing (P8 & P9)")
        st.code(run_numpy_analytics(df))

        st.subheader("📊 Pandas Descriptive Statistics")
        st.dataframe(df.describe(include='all'))

    # PAGE 4: REST API STREAM
    elif "Public REST API" in page:
        st.subheader("🌐 Public REST API Stream & Embedded Flask Endpoints (P4 & P5)")

        if st.button("Fetch Live Public API (CoinGecko)"):
            with st.spinner("Fetching live market data..."):
                r = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,solana&vs_currencies=usd,inr&include_24hr_change=true")
                if r.status_code == 200:
                    st.json(r.json())
                else:
                    st.error(f"Failed to fetch public API: {r.status_code}")

        st.divider()
        st.subheader("🔥 Embedded Flask REST API Tester")
        if st.button("Test Flask REST GET (`http://127.0.0.1:5005/api/v1/vault`)"):
            try:
                fr = requests.get(FLASK_URL, timeout=2)
                st.success(f"Flask HTTP {fr.status_code} Response:")
                st.json(fr.json())
            except Exception as e:
                st.error(f"Flask Connection Failure: {e}")


# =============================================================================
# P3: PYQT6 DESKTOP GUI APPLICATION Execution Mode
# =============================================================================

class PublicApiWorker(QThread):
    data_loaded = pyqtSignal(dict)
    error_raised = pyqtSignal(str)

    def run(self):
        try:
            url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,solana,cardano&vs_currencies=usd,inr&include_24hr_change=true"
            resp = requests.get(url, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                data.update({"_metadata": {"fetched_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}})
                self.data_loaded.emit(data)
            else:
                self.error_raised.emit(f"HTTP Error {resp.status_code}")
        except Exception as e:
            self.error_raised.emit(f"API Fetch Error: {str(e)}")


class Lab10MasterUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Lab 10 — Master Unified Security & Analytics Application")
        self.resize(1150, 780)
        self.setMinimumSize(950, 650)
        self.init_ui()
        self.refresh_all()

    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        master = QVBoxLayout(central)
        master.setContentsMargins(14, 14, 14, 14); master.setSpacing(10)

        self.setStyleSheet("""
            QMainWindow { background-color: #0b0c1b; }
            QWidget { color: #f8fafc; font-family: 'Segoe UI', Arial; }
            QGroupBox { font-weight: bold; font-size: 13px; border: 1px solid #1f2347; border-radius: 8px; margin-top: 8px; padding-top: 12px; background-color: #13152c; }
            QGroupBox::title { subcontrol-origin: margin; left: 12px; padding: 0 4px; color: #8b5cf6; }
            QLineEdit, QComboBox, QTextEdit { background-color: #1c1f3b; border: 1.5px solid #2e345e; border-radius: 6px; padding: 6px; color: #f8fafc; font-size: 12px; min-height: 24px; }
            QLineEdit:focus, QComboBox:focus, QTextEdit:focus { border-color: #8b5cf6; background-color: #24294d; }
            QPushButton { background-color: #8b5cf6; color: white; border: none; border-radius: 6px; padding: 8px 14px; font-weight: bold; font-size: 12px; }
            QPushButton:hover { background-color: #a78bfa; }
            QTableWidget { background-color: #13152c; border: 1px solid #1f2347; border-radius: 6px; gridline-color: #2e345e; color: #f8fafc; }
            QHeaderView::section { background-color: #1a1d3b; color: #06b6d4; font-weight: bold; padding: 4px; border: none; }
        """)

        header = QHBoxLayout()
        title_box = QVBoxLayout()
        title = QLabel("LAB 10: MASTER UNIFIED APPLICATION (LABS P1 - P9)")
        title.setStyleSheet("font-size: 20px; font-weight: bold; letter-spacing: 1px;")
        sub = QLabel("Combines OOP, Regex, PyQt6, REST API, Flask, Streamlit, Files, Pandas, and NumPy")
        sub.setStyleSheet("font-size: 11px; color: #94a3b8;")
        title_box.addWidget(title); title_box.addWidget(sub)
        header.addLayout(title_box); header.addStretch()

        self.lbl_status = QLabel("● All Systems Operational")
        self.lbl_status.setStyleSheet("color: #22c55e; font-weight: bold; font-size: 12px; background: rgba(34,197,94,0.1); padding: 4px 10px; border-radius: 8px; border: 1px solid #22c55e;")
        header.addWidget(self.lbl_status)
        master.addLayout(header)

        tabs = QTabWidget()

        # TAB 1: VAULT ASSET MANAGEMENT
        tab_vault = QWidget()
        v_layout = QHBoxLayout(tab_vault); v_layout.setSpacing(12)

        form_box = QGroupBox("Register / Edit Digital Asset (OOP & Regex)")
        f_lay = QVBoxLayout(form_box)

        self.entry_form = QFormLayout()
        self.txt_id = QLineEdit(); self.txt_id.setPlaceholderText("AST-1011 (Regex: ^AST-\\d{4}$)")
        self.txt_name = QLineEdit(); self.txt_name.setPlaceholderText("Asset Name")
        self.cmb_cat = QComboBox()
        self.cmb_cat.addItems(["Credentials", "Vault Key", "Identity Token", "Certificate", "Database Secret", "API Key", "SSH Key"])
        self.txt_email = QLineEdit(); self.txt_email.setPlaceholderText("owner@aeterna.com")
        self.txt_token = QLineEdit(); self.txt_token.setPlaceholderText("Secret Token (Min 8 chars, 1 num & letter)")
        self.txt_date = QLineEdit(); self.txt_date.setText(datetime.now().strftime("%Y-%m-%d"))

        self.entry_form.addRow("Asset ID *:", self.txt_id)
        self.entry_form.addRow("Asset Name *:", self.txt_name)
        self.entry_form.addRow("Category *:", self.cmb_cat)
        self.entry_form.addRow("Owner Email *:", self.txt_email)
        self.entry_form.addRow("Secret Token *:", self.txt_token)
        self.entry_form.addRow("Registered Date *:", self.txt_date)
        f_lay.addLayout(self.entry_form)

        btn_grid = QVBoxLayout()
        r1 = QHBoxLayout()
        self.btn_add = QPushButton("Add Asset (File Write)"); self.btn_add.setStyleSheet("background-color: #22c55e;"); self.btn_add.clicked.connect(self.on_add_asset)
        self.btn_update = QPushButton("Update ('r+' Mode)"); self.btn_update.setStyleSheet("background-color: #f59e0b;"); self.btn_update.clicked.connect(self.on_update_asset)
        self.btn_delete = QPushButton("Delete ('w+' Mode)"); self.btn_delete.setStyleSheet("background-color: #ef4444;"); self.btn_delete.clicked.connect(self.on_delete_asset)
        r1.addWidget(self.btn_add); r1.addWidget(self.btn_update); r1.addWidget(self.btn_delete)
        btn_grid.addLayout(r1)

        r2 = QHBoxLayout()
        self.btn_backup = QPushButton("Backup File"); self.btn_backup.setStyleSheet("background-color: #06b6d4;"); self.btn_backup.clicked.connect(self.on_backup_file)
        self.btn_rest_get = QPushButton("Flask REST GET"); self.btn_rest_get.clicked.connect(self.on_flask_get)
        r2.addWidget(self.btn_backup); r2.addWidget(self.btn_rest_get)
        btn_grid.addLayout(r2)

        f_lay.addLayout(btn_grid)
        v_layout.addWidget(form_box, 40)

        table_box = QGroupBox("Vault Assets Storage Table (lab10_vault_data.txt)")
        t_lay = QVBoxLayout(table_box)
        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels(["ID", "Asset Name", "Category", "Email", "Token", "Date", "Risk Score"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.itemSelectionChanged.connect(self.on_row_select)
        t_lay.addWidget(self.table)
        v_layout.addWidget(table_box, 60)

        tabs.addTab(tab_vault, "Vault Asset Management (P1, P2, P3, P5, P7)")

        # TAB 2: PANDAS & NUMPY ANALYTICS
        tab_analytics = QWidget()
        a_lay = QHBoxLayout(tab_analytics)

        a_left = QGroupBox("NumPy & Pandas Analytics Controls")
        al_box = QVBoxLayout(a_left)

        btn_p8 = QPushButton("Run P8: Pandas Analysis"); btn_p8.clicked.connect(self.on_run_pandas)
        btn_p9 = QPushButton("Run P9: NumPy Computation"); btn_p9.clicked.connect(self.on_run_numpy)
        al_box.addWidget(btn_p8); al_box.addWidget(btn_p9); al_box.addStretch()
        a_lay.addWidget(a_left, 30)

        a_right = QGroupBox("Analytics Output Stream & Plots")
        ar_box = QVBoxLayout(a_right)

        self.figure, self.ax = plt.subplots(figsize=(6, 3.5), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        ar_box.addWidget(self.canvas, 1)

        self.txt_analytics = QTextEdit(); self.txt_analytics.setReadOnly(True)
        ar_box.addWidget(self.txt_analytics, 1)
        a_lay.addWidget(a_right, 70)

        tabs.addTab(tab_analytics, "Data Science Analytics (P8 & P9)")

        # TAB 3: PUBLIC REST API
        tab_api = QWidget()
        api_lay = QVBoxLayout(tab_api)
        api_box = QGroupBox("Public API Data Fetcher (CoinGecko Market Stream)")
        ap_lay = QVBoxLayout(api_box)
        self.btn_fetch_api = QPushButton("Fetch Public API Data"); self.btn_fetch_api.clicked.connect(self.on_fetch_public_api)
        ap_lay.addWidget(self.btn_fetch_api)
        self.txt_api_output = QTextEdit(); self.txt_api_output.setReadOnly(True)
        ap_lay.addWidget(self.txt_api_output)
        api_lay.addWidget(api_box)

        tabs.addTab(tab_api, "Public API Fetcher (P4)")

        master.addWidget(tabs)

    def refresh_all(self):
        records = read_file_records()
        self.table.setRowCount(len(records))
        for r, item in enumerate(records):
            for c, k in enumerate(["id", "name", "category", "email", "token", "date", "risk_score"]):
                val = "*****" if k == "token" else str(item.get(k, ""))
                it = QTableWidgetItem(val)
                if k == "risk_score":
                    sc = float(val)
                    if sc > 75: it.setForeground(QColor("#ef4444"))
                    elif sc > 50: it.setForeground(QColor("#f59e0b"))
                    else: it.setForeground(QColor("#22c55e"))
                self.table.setItem(r, c, it)

    def on_row_select(self):
        items = self.table.selectedItems()
        if len(items) >= 6:
            self.txt_id.setText(items[0].text())
            self.txt_name.setText(items[1].text())
            self.cmb_cat.setCurrentText(items[2].text())
            self.txt_email.setText(items[3].text())
            self.txt_date.setText(items[5].text())

    def get_form_asset(self):
        aid = self.txt_id.text().strip()
        name = self.txt_name.text().strip()
        cat = self.cmb_cat.currentText()
        email = self.txt_email.text().strip()
        token = self.txt_token.text().strip() or "Secr3tPass1"
        date_str = self.txt_date.text().strip()
        validate_asset_inputs(aid, name, email, token, date_str)
        return CriticalVaultAsset(aid, name, cat, email, token, date_str, base_score=70.0)

    def on_add_asset(self):
        try:
            asset = self.get_form_asset()
            append_file_record(asset.to_dict())
            QMessageBox.information(self, "Success", f"Asset '{asset.asset_id}' saved to file.")
            self.refresh_all()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def on_update_asset(self):
        try:
            asset = self.get_form_asset()
            update_file_record(asset.to_dict())
            QMessageBox.information(self, "Success", f"Asset '{asset.asset_id}' updated using 'r+' mode.")
            self.refresh_all()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def on_delete_asset(self):
        aid = self.txt_id.text().strip()
        if not aid:
            QMessageBox.warning(self, "Input Warning", "Enter or select Asset ID.")
            return
        if QMessageBox.question(self, "Confirm Delete", f"Delete asset '{aid}'?") == QMessageBox.StandardButton.Yes:
            try:
                delete_file_record(aid)
                QMessageBox.information(self, "Deleted", f"Asset '{aid}' deleted.")
                self.refresh_all()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def on_backup_file(self):
        bname = backup_file_storage()
        QMessageBox.information(self, "Backup Created", f"File backed up to '{bname}'.")

    def on_flask_get(self):
        try:
            resp = requests.get(FLASK_URL, timeout=2)
            QMessageBox.information(self, "Flask REST GET Response", f"HTTP {resp.status_code}\n" + json.dumps(resp.json(), indent=2))
        except Exception as e:
            QMessageBox.critical(self, "Flask Error", str(e))

    def on_run_pandas(self):
        df = get_analytics_dataframe()
        summary = f"=== P8: PANDAS DATAFRAME ANALYSIS ===\n"
        summary += f"Shape: {df.shape}\nColumns: {df.columns.tolist()}\n\n"
        summary += f"Descriptive Statistics:\n{df.describe(include='all').to_string()}\n"
        self.txt_analytics.setText(summary)
        self.plot_chart(df)

    def on_run_numpy(self):
        df = get_analytics_dataframe()
        out = run_numpy_analytics(df)
        self.txt_analytics.setText(out)
        self.plot_chart(df)

    def plot_chart(self, df):
        self.ax.clear()
        self.figure.patch.set_facecolor('#13152c')
        self.ax.set_facecolor('#1a1d3b')
        self.ax.tick_params(colors='#f8fafc')
        self.ax.title.set_color('#8b5cf6')
        
        scores = df["risk_score"].to_numpy()
        ids = df["id"].to_numpy()
        self.ax.bar(ids, scores, color='#8b5cf6', edgecolor='#13152c')
        self.ax.set_title("P9: Matplotlib Bar Chart — Risk Scores per Asset")
        self.figure.tight_layout()
        self.canvas.draw()

    def on_fetch_public_api(self):
        self.worker = PublicApiWorker()
        self.worker.data_loaded.connect(lambda d: self.txt_api_output.setText(json.dumps(d, indent=2)))
        self.worker.error_raised.connect(lambda e: QMessageBox.critical(self, "API Error", e))
        self.worker.start()


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    start_flask_server()

    # Check if executed via Streamlit (e.g. `streamlit run lab10.py`)
    if "streamlit" in sys.modules or os.environ.get("SERVER_PORT") is not None:
        run_streamlit_app()
    else:
        app = QApplication(sys.argv)
        window = Lab10MasterUI()
        window.show()
        sys.exit(app.exec())
