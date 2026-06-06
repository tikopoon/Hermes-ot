import streamlit as st
import pandas as pd
from datetime import datetime
import io

# ==========================================
# 1. Style & Config (Classic Luxury White)
# ==========================================
st.set_page_config(page_title="Hermès Store 96 - OT & Balance Portal", page_icon="🍊", layout="centered")

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
# 2. 數據庫初始化 (與 Session State 綁定)
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
            "Submission ID": "OT-2026-0001",
            "Date": "2026-06-05",
            "Employee Name": "Tom Chan",
            "Department": "Leather Goods",
            "OT Duration (Minutes)": 90,
            "Reason / Details": "VIP Client Service Extension",
            "Approved By": "Store Manager",
            "Approval Status": "Approved",
            "Current OT Balance (Mins)": 120,
            "Submission Time": "2026-06-05 21:00"
        }
    ])

# ==========================================
# 3. 導航介面
# ==========================================
st.title("🍊 HERMÈS STORE 96 - O.T. PORTAL")
st.caption("Elegant Name List Integration & Auto-Complete OT System")
st.write("---")

role = st.sidebar.radio("Please Select Role / 請選擇身份:", ["Staff Portal (前線同事申報)", "Manager Portal (經理審批管理)"])

# ==========================================
# 4. 前線同事端：100% 穩定單一欄位、點擊流暢輸入過濾
# ==========================================
if role == "Staff Portal (前線同事申報)":
    st.subheader("📝 OT Submission / 快速申報加班")
    
    minute_options = [
        15, 30, 45, 60, 75, 90, 105, 120, 135, 150, 165, 180, 195, 210, 225, 240, 
        255, 270, 285, 300, 315, 330, 345, 360, 375, 390, 405, 420, 435, 450, 465, 480, 495, 500
    ]
    
    # 動態抓取經理匯入的 Excel 名冊
    registered_staff_list = sorted(list(st.session_state.balance_database.keys()))
    
    with st.container():
        st.write('<div class="luxury-card">', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            if not registered_staff_list:
                st.error("⚠️ No staff database found. Please ask Manager to upload Name List Excel first.")
                staff_name = ""
            else:
                # 🌟 官方最完美原生方案：只有單一欄位！
                # 點擊後手機會流暢彈出鍵盤，打字（例如打 T）下面會原地過濾出名字。
                staff_name = st.selectbox(
                    "Employee Name / 姓名 (點擊直接輸入英文字母搜尋):", 
                    options=["-- Please Select Your Name --"] + registered_staff_list
                )
                
            dept = st.selectbox("Department (所屬部門):", ["Leather Goods", "Ready-to-Wear", "Silk & Accessories", "Watches & Fine Jewelry", "Operations/Stock"])
        with col2:
            ot_date = st.date_input("OT Date (加班日期):", max_value=datetime.today())
            ot_mins = st.selectbox("OT Duration (加班分鐘):", minute_options, index=1)
            
        # 實時顯示選中同事目前的 Balance 狀況
        if staff_name and staff_name != "-- Please Select Your Name --":
            current_bal = st.session_state.balance_database[staff_name]
            st.info(f"💡 Hello {staff_name}! Your current OT Balance before this submission is: **{current_bal} Mins** ({current_bal/60:.1f} Hours)")
        
        reason_preset = st.radio(
            "Quick Reason Select / 加班原因快捷鍵:", 
            [
                "VIP Client Service Extension (接待大客延時)", 
                "Late Counter Closing & Handover (店舖收尾及交更)", 
                "Ad-hoc Stock Take / Inventory (臨時不定期盤點)", 
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
            if not staff_name or staff_name == "-- Please Select Your Name --" or ("Others" in reason_preset and not custom_reason):
                st.error("❌ Please select your name and fill in all fields. / 請選取姓名。")
            else:
                # 自動累加分鐘
                st.session_state.balance_database[staff_name] += ot_mins
                updated_bal = st.session_state.balance_database[staff_name]
                
                new_id = f"OT-2026-{len(st.session_state.ot_database) + 1:04d}"
                new_data = {
                    "Submission ID": new_id,
                    "Date": str(ot_date),
                    "Employee Name": staff_name,
                    "Department": dept,
                    "OT Duration (Minutes)": ot_mins,
                    "Reason / Details": custom_reason,
                    "Approved By": "Pending Approval",
                    "Approval Status": "Pending",
                    "Current OT Balance (Mins)": updated_bal,
                    "Submission Time": datetime.now().strftime("%Y-%m-%d %H:%M")
                }
                st.session_state.ot_database = pd.concat([st.session_state.ot_database, pd.DataFrame([new_data])], ignore_index=True)
                st.success(f"🎉 Submitted successfully! Your updated OT Balance is now: {updated_bal} Mins.")
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
        st.write("### 📥 Bulk Import Staff Name List / 批次上傳全店名冊 Excel")
        
        with st.expander("💡 View Excel File Template / 查看 Excel 製作格式說明"):
            st.write("請製作一個包含兩行欄位的 Excel 檔案（格式如下），即可一鍵匯入全店名冊：")
            template_df = pd.DataFrame([
                {"Employee": "Tiko Poon", "Initial Balance (Mins)": 60},
                {"Employee": "Angelababy Wong", "Initial Balance (Mins)": 0}
            ])
            st.dataframe(template_df)

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
                    st.error("❌ Excel 格式不對，必須包含 'Employee' 和 'Initial Balance (Mins)' 欄位。")
            except Exception as e:
                st.error(f"❌ 讀取失敗: {str(e)}")

        # 手動單個修改 Balance
        st.write("---")
        st.write("### ⚙️ Adjust Single Balance / 手動個別修正餘額")
        
        col_b1, col_b2 = st.columns(2)
        with col_b1:
            target_staff = st.text_input("Enter Employee Name (手動更新此人餘額):").strip()
        with col_b2:
            new_balance_input = st.number_input("Set New OT Balance (Minutes):", min_value=0, value=0, step=15)
            
        if st.button("💾 Update / 儲存更新"):
            if target_staff:
                st.session_state.balance_database[target_staff] = new_balance_input
                st.success(f"✅ Successfully updated {target_staff}'s balance!")
                st.rerun()
                
        # 展示目前所有人的假總數
        st.write("**Current Store 96 Employee & Balance Directory:**")
        balance_df_show = pd.DataFrame([{"Employee": k, "OT Balance (Mins)": v, "In Hours": f"{v/60:.1f} Hrs"} for k, v in st.session_state.balance_database.items()])
        st.dataframe(balance_df_show, use_container_width=True)
        
        # 審批明細與 Excel 匯出
        st.write("---")
        st.write("### 📥 Pending Requests List")
        
        df = st.session_state.ot_database
        pending_df = df[df["Approval Status"] == "Pending"]
        
        if pending_df.empty:
            st.info("Perfect! No pending OT approvals at the moment.")
        else:
            for index, row in pending_df.iterrows():
                st.write(f"""
                <div class="luxury-card">
                    <strong>👤 Employee:</strong> {row['Employee Name']} <br>
                    <strong>⏰ Duration:</strong> {row['OT Duration (Minutes)']} Mins
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"✓ Approve {row['Employee Name']}", key=f"app_{row['Submission ID']}"):
                    st.session_state.ot_database.loc[st.session_state.ot_database["Submission ID"] == row['Submission ID'], "Approval Status"] = "Approved"
                    st.rerun()
                    
        st.write("---")
        st.write("### 📊 Master Database")
        st.dataframe(st.session_state.ot_database)
        
        # 匯出綜合 Excel
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            st.session_state.ot_database.to_excel(writer, sheet_name="OT_Summary", index=False)
            balance_df_show.to_excel(writer, sheet_name="Employee_Balances", index=False)
                
        st.download_button(
            label="📥 Export English Excel Report for HR",
            data=buffer.getvalue(),
            file_name=f"Hermes_Store96_OT_Master.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
    elif password != "":
        st.error("❌ Invalid authorization code.")
