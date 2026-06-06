import streamlit as st
import pandas as pd
from datetime import datetime
import io

# ==========================================
# 1. Style & Config (Classic Luxury White)
# ==========================================
st.set_page_config(page_title="Hermès Store 96 - OT & CO Portal", page_icon="🍊", layout="centered")

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
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 數據庫初始化
# ==========================================
if 'balance_database' not in st.session_state:
    st.session_state.balance_database = {
        "Tom Chan": 120,
        "Tiko Poon": 60,
        "Alex Wong": 0
    }

if 'ot_database' not in st.session_state:
    st.session_state.ot_database = pd.DataFrame([
        {
            "Submission ID": "OTCO-2026-0001",
            "Date": "2026-06-05",
            "Employee Name": "Tom Chan",
            "Department": "Leather Goods",
            "OT / CO Type": "OT",
            "Duration (Minutes)": 90,
            "Reason / Details": "VIP Client Service Extension",
            "Approved By": "Store Manager",
            "Approval Status": "Approved",
            "Current Balance (Mins)": 120,
            "Submission Time": "2026-06-05 21:00"
        }
    ])

if 'selected_staff' not in st.session_state:
    st.session_state.selected_staff = ""

# ==========================================
# 3. 導航介面
# ==========================================
st.title("🍊 HERMÈS STORE 96 - OT & CO PORTAL")
st.caption("Elegant Name List Integration & Auto-Complete OT / CO System")
st.write("---")

role = st.sidebar.radio("Please Select Role / 請選擇身份:", ["Staff Portal (前線同事申報)", "Manager Portal (經理審批管理)"])

# ==========================================
# 4. 前線同事端
# ==========================================
if role == "Staff Portal (前線同事申報)":
    st.subheader("📝 OT / CO Submission (快速申報加班/補鐘放假)")
    
    # 生成包含負數和正數、以15分鐘為單位的選單
    negative_options = list(range(-450, 0, 15))
    positive_options = list(range(15, 510, 15))
    if positive_options[-1] > 500:
        positive_options[-1] = 500
        
    minute_options = negative_options + positive_options
    
    # 🌟 滿足需求：極簡顯示格式，只保留 「+數字 Mins (OT)」與「-數字 Mins (CO)」
    display_labels = {}
    for mins in minute_options:
        if mins > 0:
            display_labels[mins] = f"+{mins} Mins (OT)"
        else:
            display_labels[mins] = f"{mins} Mins (CO)"

    registered_staff_list = sorted(list(st.session_state.balance_database.keys()))
    
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
            ot_date = st.date_input("OT / CO Date (日期):", max_value=datetime.today())
            
            # 簡潔版選單
            selected_mins = st.selectbox(
                "OT / CO 申請 (下拉往上滑可選擇負數補鐘):", 
                options=minute_options, 
                index=len(negative_options), # 預設停在第一個正數（+15 Mins (OT)）
                format_func=lambda x: display_labels[x]
            )
            
        if staff_name in st.session_state.balance_database:
            current_bal = st.session_state.balance_database[staff_name]
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
            if not staff_name or staff_name not in st.session_state.balance_database or ("Others" in reason_preset and not custom_reason):
                st.error("❌ Please input or click a valid employee name. / 請確保姓名正確。")
            else:
                st.session_state.balance_database[staff_name] += selected_mins
                updated_bal = st.session_state.balance_database[staff_name]
                
                submission_type = "OT" if selected_mins > 0 else "CO"
                new_id = f"OTCO-2026-{len(st.session_state.ot_database) + 1:04d}"
                new_data = {
                    "Submission ID": new_id,
                    "Date": str(ot_date),
                    "Employee Name": staff_name,
                    "Department": dept,
                    "OT / CO Type": submission_type,
                    "Duration (Minutes)": selected_mins,
                    "Reason / Details": custom_reason,
                    "Approved By": "Pending Approval",
                    "Approval Status": "Pending",
                    "Current Balance (Mins)": updated_bal,
                    "Submission Time": datetime.now().strftime("%Y-%m-%d %H:%M")
                }
                st.session_state.ot_database = pd.concat([st.session_state.ot_database, pd.DataFrame([new_data])], ignore_index=True)
                
                st.session_state.selected_staff = ""
                st.success(f"🎉 Submitted successfully! ({submission_type}: {selected_mins} Mins). Your updated Balance is: {updated_bal} Mins.")
                st.rerun()
                
        st.write('</div>', unsafe_allow_html=True)

# ==========================================
# 5. 經理管理端 (密碼: hermes96)
# ==========================================
else:
    st.subheader("🔑 Manager Operations & HR Export Portal")
    password = st.text_input("Enter Manager Password / 輸入經理密碼:", type="password")
    
    if password == "hermes96":
        st.success("🔓 Authenticated Successfully - Store 96 Operations")
        
        st.write("---")
        st.write("### 📥 Bulk Import Staff Name List")
        
        uploaded_excel = st.file_uploader("Upload Store Staff List Excel (.xlsx):", type=["xlsx"])
        if uploaded_excel is not None:
            try:
                input_df = pd.read_excel(uploaded_excel)
                if "Employee" in input_df.columns and "Initial Balance (Mins)" in input_df.columns:
                    new_balances = {}
                    for _, row in input_df.iterrows():
                        name = str(row["Employee"]).strip()
                        bal = int(row["Initial Balance (Mins)"])
                        if name and name != "nan":
                            new_balances[name] = bal
                    st.session_state.balance_database = new_balances
                    st.success(f"🎉 Successfully imported {len(new_balances)} employees!")
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
            if target_staff:
                st.session_state.balance_database[target_staff] = new_balance_input
                st.success(f"✅ Successfully updated {target_staff}'s balance!")
                st.rerun()
                
        st.write("**Current Store 96 Directory & Balances:**")
        balance_df_show = pd.DataFrame([{"Employee": k, "Total Balance (Mins)": v, "In Hours": f"{v/60:.1f} Hrs"} for k, v in st.session_state.balance_database.items()])
        st.dataframe(balance_df_show, use_container_width=True)
        
        st.write("---")
        st.write("### 📥 Pending Requests List")
        df = st.session_state.ot_database
        pending_df = df[df["Approval Status"] == "Pending"]
        
        if pending_df.empty:
            st.info("Perfect! No pending OT/CO approvals at the moment.")
        else:
            for index, row in pending_df.iterrows():
                type_color = "🔴" if row['Duration (Minutes)'] < 0 else "🟢"
                st.write(f"""
                <div class="luxury-card">
                    <strong>👤 Employee:</strong> {row['Employee Name']} ({row['Department']})<br>
                    <strong>📋 Type:</strong> {type_color} {row['OT / CO Type']} <br>
                    <strong>⏰ Duration:</strong> {row['Duration (Minutes)']} Mins <br>
                    <strong>💡 Details:</strong> {row['Reason / Details']}
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"✓ Approve {row['Employee Name']} ({row['Submission ID']})", key=f"app_{row['Submission ID']}"):
                    st.session_state.ot_database.loc[st.session_state.ot_database["Submission ID"] == row['Submission ID'], "Approval Status"] = "Approved"
                    st.session_state.ot_database.loc[st.session_state.ot_database["Submission ID"] == row['Submission ID'], "Approved By"] = "Store Manager"
                    st.rerun()
                    
        st.write("---")
        st.write("### 📊 Master Database")
        st.dataframe(st.session_state.ot_database)
        
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            st.session_state.ot_database.to_excel(writer, sheet_name="OT_CO_Summary", index=False)
            balance_df_show.to_excel(writer, sheet_name="Employee_Balances", index=False)
                
        st.download_button(
            label="📥 Export English Excel Report for HR",
            data=buffer.getvalue(),
            file_name=f"Hermes_Store96_OTCO_Master.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
    elif password != "":
        st.error("❌ Invalid authorization code.")
