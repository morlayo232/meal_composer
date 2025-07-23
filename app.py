import streamlit as st
import pandas as pd

st.title("단체 급식 메뉴 구성 프로그램")

# 데이터 불러오기
menu_df = pd.read_csv('data/menu_items.csv')
ingr_df = pd.read_csv('data/ingredients_price.csv')

# 날짜/식사/인원수 입력
date = st.date_input("식단 날짜")
meal_type = st.selectbox("식사", ["조식", "중식", "석식"])
people = st.number_input("인원수", min_value=1, value=100)

# 메뉴 선택
menu_name = st.selectbox("음식 선택", menu_df['음식명'])
row = menu_df[menu_df['음식명'] == menu_name].iloc[0]
st.write(f"칼로리: {row['칼로리(kcal)']} kcal")
ingredients = row['식자재(쉼표)'].split(',')
weights = row['1인분중량(쉼표)'].split(',')

# 식자재별 필요량/단가 집계
total_list = []
total_price = 0
total_kcal = int(row['칼로리(kcal)']) * people

for ingr, w in zip(ingredients, weights):
    w_per = float(w) * people  # 전체 필요 중량
    price_row = ingr_df[ingr_df['식자재명'] == ingr]
    if not price_row.empty:
        price_per100g = float(price_row['단가(원/100g)'])
        price = price_per100g * (w_per / 100)
    else:
        price = 0
    total_list.append({"식자재": ingr, "총중량(g)": w_per, "총가격(원)": int(price)})
    total_price += price

st.subheader("식자재 집계표")
st.dataframe(pd.DataFrame(total_list))

st.info(f"총 칼로리: {total_kcal} kcal")
st.info(f"총 식자재 단가: {int(total_price):,} 원")

# 결과 저장
result_df = pd.DataFrame(total_list)
st.download_button(
    "식자재 리스트 Excel로 저장", 
    data=result_df.to_csv(index=False).encode('utf-8'), 
    file_name="ingredients_list.csv"
)
