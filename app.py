import streamlit as st
import pandas as pd

st.title("단체 급식 메뉴 구성 프로그램 (다중메뉴/단위지원)")

# 데이터 불러오기
menu_df = pd.read_csv('data/menu_items.csv')
ingr_df = pd.read_csv('data/ingredients_price.csv')

date = st.date_input("식단 날짜")
meal_type = st.selectbox("식사", ["조식", "중식", "석식"])
people = st.number_input("인원수", min_value=1, value=100)

# 다중 메뉴 선택
menu_names = st.multiselect("메뉴 선택", menu_df['음식명'])
st.write(f"선택 메뉴: {', '.join(menu_names)}")

total_kcal = 0
total_price = 0
ingredients_dict = {}

for menu_name in menu_names:
    row = menu_df[menu_df['음식명'] == menu_name].iloc[0]
    kcal = int(row['칼로리(kcal)'])
    total_kcal += kcal * people
    
    ingredients = [i.strip() for i in row['식자재(쉼표)'].split(',')]
    amounts = [float(x.strip()) for x in row['1인분량(쉼표)'].split(',')]
    units = [u.strip() for u in row['단위(쉼표)'].split(',')]
    types = [t.strip() for t in row['구분(쉼표)'].split(',')]
    
    for ingr, amt, unit, type_ in zip(ingredients, amounts, units, types):
        key = (ingr, unit, type_)
        add_amt = amt * people if unit == "g" else int(amt) * people
        if key not in ingredients_dict:
            ingredients_dict[key] = add_amt
        else:
            ingredients_dict[key] += add_amt

# 식자재별 단가 합산
total_list = []
total_price = 0

for (ingr, unit, type_), amt in ingredients_dict.items():
    # 단가 읽기 (단위 맞춤)
    row = ingr_df[(ingr_df['식자재명'] == ingr) & (ingr_df['단위'] == unit)]
    if not row.empty:
        price_per_unit = float(row.iloc[0]['단가(원/단위)'])
        price = price_per_unit * (amt / 100) if unit == "g" else price_per_unit * amt
    else:
        price = 0
    total_list.append({
        "식자재": ingr,
        "총량": amt,
        "단위": unit,
        "구분": type_,
        "총가격(원)": int(price)
    })
    total_price += price

df_result = pd.DataFrame(total_list)

st.subheader("식자재 집계표")
st.dataframe(df_result)

st.info(f"총 칼로리: {total_kcal:,} kcal")
st.info(f"총 식자재 단가: {int(total_price):,} 원")

# 결과 저장
st.download_button(
    "식자재 리스트 Excel로 저장",
    data=df_result.to_csv(index=False).encode('utf-8'),
    file_name=f"{date}_{meal_type}_식자재리스트.csv"
)
