import streamlit as st
import pandas as pd
from datetime import datetime
import io

# ==========================================
# 1. 奢華視覺風格設定 (Hermès Orange & Luxury Tone)
# ==========================================
st.set_page_config(page_title="Hermès Store 96 - OT Portal", page_icon="🍊", layout="centered")

# 用 CSS 注入愛馬仕專屬配色與高級網頁字體
st.markdown("""
    <style>
    .stApp { background-color: #F8F9FA; }
    h1, h2, h3 { color: #F37021 !important; font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; }
    
    /* 按鈕樣式：愛馬仕橙底白字 */
    div.stButton > button:first-child {
        background-color: #F37021;
        color: white;
        border-radius: 4px;
        border: none;
        font-weight: bold;
        padding: 10px 20px;
        transition: 0.3s;
        width: 100%;
    }
    div.stButton > button:first-child:hover { background-color: #D65A18; color: white; }
    
    /* 下載按鈕特別樣式 */
    .stDownloadButton > button {
        background-color: #333333 !important;
        color: white !important;
        border-radius: 4px !important;
        font-weight: bold !important;
    }
    .stDownloadButton > button:hover { background-color: #F37021 !important; }

    /* 卡片式容器 */
    .luxury-card {
        background-color: white;
        padding: 25px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        border-left: 5px solid #F37021;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_style_html=True)

# ==========================================
# 2. 數據庫初始化 (全英文底層欄位，方便後勤導出)
# ==========================================
if 'ot_database' not in st.session_state:
    st.session_state.ot_database = pd.DataFrame([
        {
            "Submission ID": "OT-2026-0001",
            "Date": "2026-06-05",
            "Employee Name": "Tom Chan",
            "Department": "Leather Goods",
            "OT Duration (Minutes)": 90,
            "Reason / Details": "VIP Client Service Extension (Hermes Kelly Order)",
            "Approved By": "Store Manager (Alex W.)",
            "Approval Status": "Approved",
            "Submission Time": "2026-06-05 21:00"
        },
        {
            "Submission ID": "OT-2026-0002",
            "Date": "2026-06-04",
            "Employee Name": "Mary Wong",
            "Department": "Ready-to-Wear",
            "OT Duration (Minutes)": 30,
            "Reason / Details": "Late Counter Closing & Daily Stock Handover",
            "Approved By": "Duty Manager (Sarah L.)",
            "Approval Status": "Approved",
            "Submission Time": "2026-06-04 19:45"
        }
    ])

# ==========================================
# 3. 導航介面 (Role Switcher)
# ==========================================
st.title("🍊 HERMÈS STORE 96 - O.T. PORTAL")
st.caption("Elegant Workforce Efficiency Management System")
st.write("---")

role = st.sidebar.radio("Please Select Role / 請選擇身份:", ["Staff Portal (前線同事申報)", "Manager Portal (經理審批管理)"])

# ==========================================
# 4. 介面一：前線同事快速申報端（分鐘制）
# ==========================================
if role == "Staff Portal (前線同事申報)":
    st.subheader("📝 OT Submission / 快速申報加班")
    
    # 手機打開即用的智能提示 (Time-based Notification Trigger)
    current_hour = datetime.now().hour
    if 18 <= current_hour <= 23:
        st.info("🍊 Good evening! Finished your shift? Don't forget to submit your OT if you served a late VIP today!")
        
    with st.container():
        st.markdown('<div class="luxury-card">', unsafe_style_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            staff_name = st.text_input("Employee Name (英文全名):", placeholder="e.g. Tom Chan")
            dept = st.selectbox("Department (所屬部門):", ["Leather Goods", "Ready-to-Wear", "Silk & Accessories", "Watches & Fine Jewelry", "Operations/Stock"])
        with col2:
            ot_date = st.date_input("OT Date (加班日期):", max_value=datetime.today())
            # 改為更加實用的分鐘選擇制
            ot_mins = st.selectbox("OT Duration (加班分鐘):", [15, 30, 45, 60, 75, 90, 120, 150, 180], index=1)
        
        # 快捷原因選擇（後台自動轉為英文細節）
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
            if not staff_name or ("Others" in reason_preset and not custom_reason):
                st.error("❌ Please fill in all fields before submission. / 請填妥所有欄位。")
            else:
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
                    "Submission Time": datetime.now().strftime("%Y-%m-%d %H:%M")
                }
                st.session_state.ot_database = pd.concat([st.session_state.ot_database, pd.DataFrame([new_data])], ignore_index=True)
                st.success(f"🎉 Submitted successfully! Your Duty Manager will review it tonight. / 提交成功！")
                
        st.markdown('</div>', unsafe_style_html=True)

# ==========================================
# 5. 介面二：經理管理/一鍵審批與全英文 Excel 匯出
# ==========================================
else:
    st.subheader("🔑 Manager Operations & HR Export Portal")
    password = st.text_input("Enter Manager Password / 輸入經理密碼:", type="password")
    
    if password == "hermes96":
        st.success("🔓 Authenticated Successfully - Store 96 Operations")
        
        df = st.session_state.ot_database
        pending_count = len(df[df["Approval Status"] == "Pending"])
        total_mins = df[df["Approval Status"] == "Approved"]["OT Duration (Minutes)"].sum()
        
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.metric(label="⏳ Pending Approval / 待處理審批", value=f"{pending_count} Requests")
        with col_m2:
            st.metric(label="📊 Approved OT This Month / 本月已批出總時數", value=f"{total_mins} Mins ({total_mins/60:.1f} Hours)")
            
        st.write("---")
        st.write("### 📥 Pending Requests List")
        
        pending_df = df[df["Approval Status"] == "Pending"]
        
        if pending_df.empty:
            st.info("Perfect! No pending OT approvals at the moment.")
        else:
            for index, row in pending_df.iterrows():
                st.markdown(f"""
                <div class="luxury-card">
                    <strong>👤 Employee:</strong> {row['Employee Name']} ({row['Department']}) <br>
                    <strong>📅 Date:</strong> {row['Date']} | <strong>⏰ Duration:</strong> {row['OT Duration (Minutes)']} Mins <br>
                    <strong>💡 Details:</strong> {row['Reason / Details']} <br>
                    <span style="color:#757575; font-size:12px;">Submitted at: {row['Submission Time']}</span>
                </div>
                """, unsafe_style_html=True)
                
                if st.button(f"✓ Approve {row['Employee Name']}'s Request", key=f"app_{row['Submission ID']}"):
                    st.session_state.ot_database.loc[st.session_state.ot_database["Submission ID"] == row['Submission ID'], "Approval Status"] = "Approved"
                    st.session_state.ot_database.loc[st.session_state.ot_database["Submission ID"] == row['Submission ID'], "Approved By"] = "Store Manager"
                    st.toast(f"Request {row['Submission ID']} Approved!")
                    st.rerun()
                    
        # 🌟 核心功能：一鍵導出全英文、經排版設計的高級 Excel 檔案
        st.write("---")
        st.write("### 📊 Master Database (HR & Backoffice Export)")
        st.dataframe(st.session_state.ot_database)
        
        # 利用 openpyxl 將 Excel 排版優化（背景會自動生成記憶體流，完美支援手機點擊下載）
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            st.session_state.ot_database.to_excel(writer, sheet_name="OT_Summary", index=False)
            
            # 此處可加入 openpyxl 格式化，Streamlit 輸出時會保留精美外觀
            workbook = writer.book
            worksheet = writer.sheets["OT_Summary"]
            for col in worksheet.columns:
                max_len = max(len(str(cell.value or '')) for cell in col)
                col_letter = col[0].column_letter
                worksheet.column_dimensions[col_letter].width = max(max_len + 3, 12)
                
        st.download_button(
            label="📥 Export English Excel Report for HR (一按匯出計糧 Excel)",
            data=buffer.getvalue(),
            file_name=f"Hermes_Store96_OT_Export_{datetime.today().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
    elif password != "":
        st.error("❌ Invalid authorization code.")
