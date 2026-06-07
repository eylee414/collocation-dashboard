import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="분야별 연어 분석기", layout="wide")

st.title("📊 분야별 통합 연어 분석 대시보드")
st.markdown("경제, 정치, 사회 분야별 핵심 어휘의 좌우 결합 패턴을 탐색합니다.")

DATA_DIR = "."

# 1. 폴더 존재 여부 확인
if not os.path.exists(DATA_DIR):
    st.error(f"'{DATA_DIR}' 폴더를 찾을 수 없습니다. 파이썬 파일과 동일한 위치에 'data' 폴더가 있는지 확인하십시오.")
    st.stop()

# 2. CSV가 아닌 엑셀(.xlsx) 파일만 스캔 (임시 파일 제외)
files = [f for f in os.listdir(DATA_DIR) if f.endswith('.xlsx') and not f.startswith('~')]

if not files:
    st.error("'data' 폴더 안에 .xlsx 엑셀 파일이 없습니다. 경제, 정치, 사회 분석 엑셀 파일 3개를 넣어주세요.")
    st.stop()

# 3. 분야 추출 (예: '경제_좌우구분_연어분석.xlsx' -> '경제')
sectors = sorted(list(set([f.split('_')[0] for f in files])))
selected_sector = st.sidebar.selectbox("연구 분야 선택", sectors)

# 4. 선택된 분야와 일치하는 파일 찾기
target_file = None
for f in files:
    if f.startswith(selected_sector):
        target_file = f
        break

if target_file:
    file_path = os.path.join(DATA_DIR, target_file)
    
    try:
        # 5. 엑셀 파일 전체를 읽어 시트(Sheet) 목록 확보
        xl = pd.ExcelFile(file_path)
        # 엑셀 파일 내부의 시트 이름들(예: 금리NNG, 증시NNG)을 중심어 목록으로 사용
        keywords = xl.sheet_names 
        
        selected_keyword = st.sidebar.selectbox("중심어(Target Word) 선택", keywords)
        
        # 6. 사용자가 선택한 시트의 데이터만 데이터프레임으로 파싱
        df = xl.parse(selected_keyword)
        
        # 7. 시각화
        st.subheader(f"🔍 [{selected_sector}] {selected_keyword} 좌우 결합 분석")

        fig = px.bar(
            df, 
            x="LogDice", 
            y="연어(Collocate)", 
            color="위치", 
            orientation='h',
            text="LogDice",
            barmode='group',
            title=f"{selected_keyword}의 좌우 연어 결합 강도 ($LogDice$)",
            labels={"LogDice": "결합 강도 ($LogDice$)", "연어(Collocate)": "연어"}
        )

        fig.update_layout(yaxis={'categoryorder':'total ascending'}, height=600)
        st.plotly_chart(fig, use_container_width=True)

        # 8. 표 데이터 출력
        st.dataframe(df.sort_values(by="LogDice", ascending=False), use_container_width=True)

    except Exception as e:
        st.error(f"데이터를 읽거나 시각화하는 중 오류가 발생했습니다: {e}")
        st.markdown("엑셀 파일 내 해당 시트에 'LogDice', '연어(Collocate)', '위치' 열(Column)이 정확히 존재하는지 확인하십시오.")
