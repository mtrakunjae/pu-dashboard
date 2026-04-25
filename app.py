import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 1. การตั้งค่าหน้าจอ
st.set_page_config(page_title="Pressure injury Monitoring in ward Dashboard", layout="wide")

# ปรับแต่ง CSS เพิ่มเติม
st.markdown("""
    <style>
    [data-testid="stMetricValue"] { font-size: 28px; color: #1f77b4; }
    .stMetric { background-color: #ffffff; padding: 20px; border-radius: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); border-top: 4px solid #ff4b4b; }
    .main { background-color: #f0f2f6; }
    </style>
    """, unsafe_allow_html=True)

# 2. ข้อมูลสรุป (ใช้ข้อมูลเดิมของคุณ)
years = ['2563', '2564', '2565', '2566', '2567', '2568']
bed_days = [6769, 7030, 6934, 7059, 6391, 7131]
stage1_counts = [2, 5, 3, 2, 3, 4]
stage2plus_counts = [38, 16, 24, 17, 19, 16]

df_yearly = pd.DataFrame({
    'ปี พ.ศ.': years,
    'จำนวนวันนอน': bed_days,
    'ระดับ 1': stage1_counts,
    'ระดับ 2 ขึ้นไป': stage2plus_counts
})

# คำนวณอัตราส่วนรวมต่อ 1,000 วันนอน
df_yearly['Total Cases'] = df_yearly['ระดับ 1'] + df_yearly['ระดับ 2 ขึ้นไป']
df_yearly['อัตราการเกิดรวม'] = (df_yearly['Total Cases'] / df_yearly['จำนวนวันนอน']) * 1000

# 3. Sidebar
st.sidebar.image("https://img.icons8.com/fluency/96/hospital.png", width=80)
st.sidebar.title("PU Navigation")
selected_year = st.sidebar.selectbox("📅 เลือกปีงบประมาณวิเคราะห์:", years, index=len(years)-1)

st.title("🏥 ระบบวิเคราะห์และเฝ้าระวังแผลกดทับ (Pressure Ulcer)")
st.caption(f"อัปเดตล่าสุด: ปี พ.ศ. {years[-1]} | ข้อมูลเปรียบเทียบย้อนหลัง 6 ปี")

# 4. KPI รายปี
year_data = df_yearly[df_yearly['ปี พ.ศ.'] == selected_year].iloc[0]
target_val = 0.9

c1, c2, c3, c4 = st.columns(4)
with c1:
    delta_val = f"{year_data['อัตราการเกิดรวม'] - target_val:.2f}"
    st.metric("อัตราการเกิดรวม", f"{year_data['อัตราการเกิดรวม']:.2f}", 
              delta=f"{delta_val} จากเป้าหมาย", delta_color="inverse")
with c2:
    st.metric("จำนวนเคสทั้งหมด", f"{int(year_data['Total Cases'])} ราย")
with c3:
    st.metric("ความรุนแรงระดับ 1", f"{int(year_data['ระดับ 1'])} ราย")
with c4:
    st.metric("ความรุนแรงระดับ 2 ขึ้นไป", f"{int(year_data['ระดับ 2 ขึ้นไป'])} ราย")

# 5. การใช้ Tabs เพื่อแยกการแสดงผล
tab1, tab2 = st.tabs(["📈 แนวโน้มและภาพรวม", "🔍 วิเคราะห์ตำแหน่งและสาเหตุ"])

with tab1:
    col_a, col_b = st.columns([3, 2])
    
    with col_a:
        # กราฟเส้นแสดงอัตราการเกิดเทียบกับ Target
        fig_rate = px.line(df_yearly, x='ปี พ.ศ.', y='อัตราการเกิดรวม', 
                           title="แนวโน้มอัตราการเกิดแผลกดทับต่อ 1,000 วันนอน",
                           markers=True, text=df_yearly['อัตราการเกิดรวม'].apply(lambda x: f'{x:.2f}'))
        fig_rate.add_hline(y=0.9, line_dash="dash", line_color="red", 
                           annotation_text="เป้าหมาย (≤ 0.9)", annotation_position="bottom right")
        fig_rate.update_traces(textposition="top center")
        st.plotly_chart(fig_rate, use_container_width=True)

    with col_b:
        # กราฟวงกลมปีที่เลือก
        pie_data = pd.DataFrame({
            'Level': ['ระดับ 1', 'ระดับ 2 ขึ้นไป'],
            'Value': [year_data['ระดับ 1'], year_data['ระดับ 2 ขึ้นไป']]
        })
        fig_pie = px.pie(pie_data, values='Value', names='Level', 
                         title=f"สัดส่วนความรุนแรง ปี {selected_year}",
                         color_discrete_sequence=['#FFCC00', '#FF4B4B'], hole=0.5)
        st.plotly_chart(fig_pie, use_container_width=True)

with tab2:
    # วิเคราะห์ตามตำแหน่ง
    bone_prominence = [20, 10, 12, 7, 4, 7]
    medical_device = [20, 11, 15, 12, 18, 13]
    
    df_loc = pd.DataFrame({'ปี พ.ศ.': years, 'ปุ่มกระดูก': bone_prominence, 'อุปกรณ์การแพทย์': medical_device})
    
    fig_loc = go.Figure()
    fig_loc.add_trace(go.Bar(x=years, y=bone_prominence, name='บริเวณปุ่มกระดูก', marker_color='#1f77b4'))
    fig_loc.add_trace(go.Bar(x=years, y=medical_device, name='ใต้อุปกรณ์การแพทย์', marker_color='#e377c2'))
    fig_loc.update_layout(title="เปรียบเทียบสาเหตุ: ปุ่มกระดูก vs อุปกรณ์การแพทย์", barmode='group')
    st.plotly_chart(fig_loc, use_container_width=True)

# 6. ส่วนข้อมูลดิบและปุ่มดาวน์โหลด
st.divider()
with st.expander("📝 ตรวจสอบข้อมูลดิบและดาวน์โหลด"):
    st.dataframe(df_yearly, use_container_width=True)
    csv = df_yearly.to_csv(index=False).encode('utf-8-sig')
    st.download_button("📥 ดาวน์โหลดข้อมูลเป็น CSV", data=csv, file_name="pu_data_summary.csv", mime="text/csv")
