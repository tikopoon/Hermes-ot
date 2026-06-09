import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import io
from streamlit_gsheets import GSheetsConnection

# ==========================================
# 1. Style & Config (Classic Luxury White)
# ==========================================
st.set_page_config(page_title="Hermès Store 96 - OT & CO Cloud Portal", page_icon="🍊", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #F8F9FA; }
    h1, h2, h3 { color: #F37021 !important; font-family: 'Helvetica Neue', Arial, sans-serif; }
    div.stButton > button:first-child {
        background-color: #F37021;
        color: white;
        border-radius: 4px;
        border: none;
        font-weight: bold;
        padding: 10px 20px;
        width: 100%;
    }
    div.stButton > button:first-child:hover { background-color: #D65A18; }
    .luxury-card {
        background-color: white;
        padding: 20px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        border-left: 5px solid #F37021;
        margin-bottom: 15px;
    }
    div.element-container:has(button[key="clear_success_btn"]) button {
        background-color: #28A745 !important;
        color: white !important;
    }
    div.element-container:has(button[key="clear_success_btn"]) button:hover {
        background-color: #218838 !important;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 建立 Google Sheet 雲端實時連線
# ==========================================
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception:
    st.error("⚠️ Cloud Database Connection Waiting. Please ensure Streamlit Secrets are set up correctly.")
    st.stop()

# 實時從 Google Sheet 載入最新數據
try:
    balance_df = conn.read(worksheet="Balances", ttl="0s")
    ot_database = conn.read(worksheet="History", ttl="0s")
except Exception as e:
    st.error(f"❌ 讀取雲端資料庫失敗。請確保 Google Sheet 欄位正確且已設定為公開檢視。錯誤: {str(e)}")
    st.stop()

# 將雲端餘額轉換為 dict 方便代碼操作
balance_database = {}
for _, row in balance_df.dropna(subset=["Employee"]).iterrows():
    balance_database[str(row["Employee"]).strip()] = int(row["Initial Balance (Mins)"])

if 'selected_staff' not in st.session_state:
    st.session_state.selected_staff = ""
if 'show_success_block' not in st.session_state:
    st.session_state.show_success_block = False
if 'last_submit_msg' not in st.session_state:
    st.session_state.last_submit_msg = ""

# ==========================================
# 3. 導航介面
# ==========================================
st.title("🍊 HERMÈS STORE 96 - CLOUD PORTAL")
st.caption("Permanent Cloud Storage & Auto-Complete OT / CO System")
st.write("---")

role = st.sidebar.radio("Please Select Role / 請選擇身份:", ["Staff Portal (前線同事申報)", "Manager Portal (經理審批管理)"])

# ==========================================
# 4. 前線同事端
# ==========================================
if role == "Staff Portal (前線同事申報)":
    st.subheader("📝 OT / CO Submission (快速申報加班/補鐘放假)")
    
    if st.session_state.show_success_block:
        st.write('<div class="luxury-card" style="border-left: 5px solid #28A745;">', unsafe_allow_html=True)
        st.success(st.session_state.last_submit_msg)
        st.markdown("<h4 style='color: #28A745; text-align: center;'>🎉 雲端儲存成功！請點擊下方按鈕以進行下一次申報</h4>", unsafe_allow_html=True)
        st.write("<br>", unsafe_allow_html=True)
        
        if st.button("OK / 確定", key="clear_success_btn"):
            st.session_state.show_success_block = False
            st.session_state.last_submit_msg = ""
            st.rerun()
        st.write('</div>', unsafe_allow_html=True)
        
    else:
        negative_options = list(range(-450, 0, 15))
        positive_options = list(range(15, 510, 15))
        if positive_options[-1] > 500:
            positive_options[-1] = 500
            
        minute_options = negative_options + positive_options
        
        display_labels = {}
        for mins in minute_options:
            if mins > 0:
                display_labels[mins] = f"+{mins} Mins (OT)"
            else:
                display_labels[mins] = f"{mins} Mins (CO)"

        registered_staff_list = sorted(list(balance_database.keys()))
        
        with st.container():
            st.write('<div class="luxury-card">', unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                if not registered_staff_list:
                    st.error("⚠️ No staff database found. Please ask Manager to upload Name List Excel first.")
                    staff_name = ""
                else:
                    typed_name = st.text_input(
                        "Employee Name / 姓名 (在此輸入字母，下方會自動跳出對應人名):", 
                        value=st.session_state.selected_staff,
                        placeholder="Type to search (e.g. T)"
                    )
                    
                    if typed_name:
                        matches = [name for name in registered_staff_list if typed_name.lower() in name.lower()]
                        if matches and (len(matches) > 1 or matches[0] != typed_name):
                            st.caption("🎯 點擊下方名字快速填入 / Click name below to auto-complete:")
                            cols = st.columns(min(len(matches), 4))
                            for idx, match in enumerate(matches[:4]):
                                with cols[idx % 4]:
                                    if st.button(f"👤 {match}", key=f"suggest_{match}"):
                                        st.session_state.selected_staff = match
                                        st.rerun()
                        elif not matches:
                            st.warning("❌ 沒有找到相符的同事名字。")
                    
                    staff_name = typed_name
                    
                dept = st.selectbox("Department (所屬部門):", ["Leather Goods", "Ready-to-Wear", "Silk & Accessories", "Watches & Fine Jewelry", "Operations/Stock"])
            
            with col2:
                # 🌟 滿足新需求：加入「7天之內申請」限制邊界
                today = datetime.today()
                seven_days_ago = today - timedelta(days=7)
                
                ot_date = st.date_input(
                    "OT / CO Date (日期 - 限7天內申報):", 
                    value=today,
                    min_value=seven_days_ago,  # 鎖死7天前
                    max_value=today            # 鎖死未來
                )
                
                selected_mins = st.selectbox(
                    "OT / CO 申請 (下拉往上滑可選擇負數補鐘):", 
                    options=minute_options, 
                    index=len(negative_options), 
                    format_func=lambda x: display_labels[x]
                )
                
            if staff_name in balance_database:
                current_bal = balance_database[staff_name]
                st.info(f"💡 Hello {staff_name}! Your current Balance before this submission is: **{current_bal} Mins** ({current_bal/60:.1f} Hours)")
                if selected_mins < 0 and current_bal + selected_mins < 0:
                    st.warning(f"⚠️ Warning: 餘額將會變成負數")
            
            reason_preset = st.radio(
                "Quick Reason Select / 原因快捷鍵:", 
                [
                    "VIP Client Service Extension (接待大客延時 OT)", 
                    "Late Counter Closing & Handover (店舖收尾交更 OT)", 
                    "Compensation Leave (申請放補鐘假 CO)", 
                    "Others (請在下方以英文或中文輸入具體原因)"
                ]
            )
            
            custom_reason = ""
            if "Others" in reason_preset:
                custom_reason = st.text_input("Please enter details / 請填寫具體原因:")
            else:
                custom_reason = reason_preset

            submit_btn = st.button("Submit Request / 確認提交")
            
            if submit_btn:
                if not staff_name or staff_name not in balance_database or ("Others" in reason_preset and not custom_reason):
                    st.error("❌ Please input or click a valid employee name. / 請確保姓名正確。")
                else:
                    new_bal = balance_database[staff_name] + selected_mins
                    submission_type = "OT" if selected_mins > 0 else "CO"
                    new_id = f"OTCO-2026-{len(ot_database) + 1:04d}"
                    
                    new_row = {
                        "Submission ID": new_id,
                        "Date": str(ot_date),
                        "Employee Name": staff_name,
                        "Department": dept,
                        "OT / CO Type": submission_type,
                        "Duration (Minutes)": int(selected_mins),
                        "Reason / Details": custom_reason,
                        "Approved By": "Pending Approval",
                        "Approval Status": "Pending",
                        "Current Balance (Mins)": int(new_bal),
                        "Submission Time": datetime.now().strftime("%Y-%m-%d %H:%M")
                    }
                    
                    # 1. 更新 History 雲端工作表
                    updated_ot_df = pd.concat([ot_database, pd.DataFrame([new_row])], ignore_index=True)
                    conn.update(worksheet="History", data=updated_ot_df)
                    
                    # 2. 更新 Balances 雲端工作表
                    balance_df.loc[balance_df["Employee"] == staff_name, "Initial Balance (Mins)"] = int(new_bal)
                    conn.update(worksheet="Balances", data=balance_df)
                    
                    st.session_state.selected_staff = ""
                    st.session_state.last_submit_msg = f"### 📬 雲端儲存成功！\n* **員工姓名:** {staff_name}\n* **申請日期:** {str(ot_date)}\n* **申請類別:** {submission_type}\n* **申請時數:** {selected_mins} 分鐘\n* **最新餘額 (預計):** {new_bal} 分鐘"
                    st.session_state.show_success_block = True
                    st.rerun()
                    
            st.write('</div>', unsafe_allow_html=True)

# ==========================================
# 5. 經理管理端
# ==========================================
else:
    st.subheader("🔑 Manager Operations & HR Export Portal")
    password = st.text_input("Enter Manager Password / 輸入經理密碼:", type="password")
    
    if password == "hermes96":
        st.success("🔓 Authenticated Successfully - Store 96 Cloud Operations")
        
        st.write("---")
        st.write("### 📥 Bulk Import Staff Name List")
        
        uploaded_excel = st.file_uploader("Upload Store Staff List Excel (.xlsx):", type=["xlsx"])
        if uploaded_excel is not None:
            try:
                input_df = pd.read_excel(uploaded_excel)
                if "Employee" in input_df.columns and "Initial Balance (Mins)" in input_df.columns:
                    save_df = input_df[["Employee", "Initial Balance (Mins)"]].dropna()
                    conn.update(worksheet="Balances", data=save_df)
                    st.success(f"🎉 Successfully uploaded list to Google Cloud!")
                    st.rerun()
                else:
                    st.error("❌ Excel columns must be 'Employee' and 'Initial Balance (Mins)'")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

        st.write("---")
        st.write("### ⚙️ Adjust Single Balance")
        col_b1, col_b2 = st.columns(2)
        with col_b1:
            target_staff = st.text_input("Enter Employee Name:").strip()
        with col_b2:
            new_balance_input = st.number_input("Set New Balance (Minutes):", min_value=-1000, value=0, step=15)
            
        if st.button("💾 Update / 儲存更新"):
            if target_staff in balance_database:
                balance_df.loc[balance_df["Employee"] == target_staff, "Initial Balance (Mins)"] = int(new_balance_input)
                conn.update(worksheet="Balances", data=balance_df)
                st.success(f"✅ Successfully updated {target_staff}'s cloud balance!")
                st.rerun()
            elif target_staff:
                new_emp_row = pd.DataFrame([{"Employee": target_staff, "Initial Balance (Mins)": int(new_balance_input)}])
                balance_df = pd.concat([balance_df, new_emp_row], ignore_index=True)
                conn.update(worksheet="Balances", data=balance_df)
                st.success(f"✅ Created new employee {target_staff} on cloud!")
                st.rerun()
                
        st.write("**Current Store 96 Directory & Balances (Real-time Cloud):**")
        st.dataframe(balance_df, use_container_width=True)
        
        st.write("---")
        st.write("### 📥 Pending Requests List")
        pending_df = ot_database[ot_database["Approval Status"] == "Pending"]
        
        if pending_df.empty:
            st.info("Perfect! No pending OT/CO approvals at the moment.")
        else:
            for index, row in pending_df.iterrows():
                type_color = "🔴" if int(row['Duration (Minutes)']) < 0 else "🟢"
                st.write(f"""
                <div class="luxury-card">
                    <strong>👤 Employee:</strong> {row['Employee Name']} <br>
                    <strong>📋 Type:</strong> {type_color} {row['OT / CO Type']} | <strong>⏰ Duration:</strong> {row['Duration (Minutes)']} Mins <br>
                    <strong>💡 Details:</strong> {row['Reason / Details']}
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"✓ Approve {row['Employee Name']} ({row['Submission ID']})", key=f"app_{row['Submission ID']}"):
                    ot_database.loc[ot_database["Submission ID"] == row['Submission ID'], "Approval Status"] = "Approved"
                    ot_database.loc[ot_database["Submission ID"] == row['Submission ID'], "Approved By"] = "Store Manager"
                    conn.update(worksheet="History", data=ot_database)
                    st.rerun()
                    
        st.write("---")
        st.write("### 📊 Cloud Master Database (History)")
        st.dataframe(ot_database)
        
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            ot_database.to_excel(writer, sheet_name="OT_CO_Summary", index=False)
            balance_df.to_excel(writer, sheet_name="Employee_Balances", index=False)
                
        st.download_button(
            label="📥 Export English Excel Report for HR",
            data=buffer.getvalue(),
            file_name=f"Hermes_Store96_OTCO_CloudMaster.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
    elif password != "":
        st.error("❌ Invalid authorization code.")
