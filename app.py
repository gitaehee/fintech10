import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import numpy as np
import datetime

# y축 한글 깨짐 해결
plt.rcParams['font.family'] ='AppleGothic'
plt.rcParams['axes.unicode_minus'] =False


from collections import Counter
from wordcloud import WordCloud

# 데이터 불러오기
@st.cache
def load_data():
    df = pd.read_csv("top200_movies_v1.csv")

    df['매출액'] = df['매출액'].str.replace(',', '').astype(int)
    df['관객수'] = df['관객수'].str.replace(',', '').astype(int)
    df['스크린수'] = df['스크린수'].str.replace(',', '').astype(int)
    df['상영횟수'] = df['상영횟수'].str.replace(',', '').astype(int)
    df['러닝타임'] = df['러닝타임'].str.replace('분', '').astype(int)
    df['배우목록'] = df['cast'].apply(lambda x: x.split(', ') if isinstance(x, str) else [])
    df['감독목록'] = df['감독'].apply(lambda x: x.split(', ') if isinstance(x, str) else [])


    return df


df = load_data()

# 타이틀
st.title("🎬 Top 200 Movies by Audience")

# 데이터 미리보기
st.dataframe(df)





# 배우 출연 횟수 카운트
actor_list = sum(df["배우목록"], [])  # 리스트 안의 리스트 풀기
actor_counts = Counter(actor_list)  # 빈도수 계산

# 📌 워드 클라우드 생성
st.subheader("🎭 Word Cloud: 많이 출연한 배우")

wordcloud = WordCloud(
    width=800, 
    height=400, 
    background_color="white", 
    colormap="coolwarm", 
    font_path="/System/Library/Fonts/Supplemental/AppleGothic.ttf"
).generate_from_frequencies(actor_counts)

fig, ax = plt.subplots(figsize=(12, 6))
ax.imshow(wordcloud, interpolation="bilinear")
ax.axis("off")
st.pyplot(fig)




# 감독 횟수 카운트
director_list = sum(df["감독목록"], [])  # 리스트 안의 리스트 풀기
director_counts = Counter(director_list)  # 빈도수 계산

# 📌 워드 클라우드 생성
st.subheader("🎭 Word Cloud: 많이 디렉팅한 감독")

wordcloud = WordCloud(
    width=800, 
    height=400, 
    background_color="white", 
    colormap="coolwarm", 
    font_path="/System/Library/Fonts/Supplemental/AppleGothic.ttf"
).generate_from_frequencies(director_counts)

fig, ax = plt.subplots(figsize=(12, 6))
ax.imshow(wordcloud, interpolation="bilinear")
ax.axis("off")
st.pyplot(fig)




# 📌 **산점도: 순위 vs. 상영시간**
st.subheader("📊 Scatter Plot: 순위 vs. 상영시간")

fig_scatter = px.scatter(
    df, x=df.index + 1, y="러닝타임", 
    title="영화 순위 vs. 상영시간",
    labels={"x": "순위", "러닝타임": "상영시간 (분)"},
    hover_name="영화명",
    color="러닝타임",
    color_continuous_scale="Viridis"
)

st.plotly_chart(fig_scatter)





# 📌 **스트립플롯: 개별 영화 상영시간**
st.subheader("📊 Strip Plot: 개별 영화 상영시간")

fig_strip = px.strip(
    df, x=df.index + 1, y="러닝타임",
    title="개별 영화 상영시간",
    labels={"x": "영화 순위", "러닝타임": "상영시간 (분)"},
    hover_name="영화명",
    stripmode="overlay"  # 점들이 겹치지 않도록 겹쳐서 표시
)

st.plotly_chart(fig_strip)





# 📌 **박스플롯: 개별 영화 상영시간 분포**
st.subheader("📊 Box Plot: 전체 영화 상영시간 분포")

fig_box = px.box(
    df, y="러닝타임",
    title="전체 영화 상영시간 분포",
    labels={"러닝타임": "상영시간 (분)"},
    points="all"  # 모든 데이터 점도 표시
)

st.plotly_chart(fig_box)









# 📌 **Treemap (장르별 관객수)**
st.subheader("📊 Treemap: 관객수 기준 장르별 비중")
fig_treemap = px.treemap(df, path=["장르"], values="관객수", title="장르별 관객수 비율", color="장르")
st.plotly_chart(fig_treemap)









# 📌 **장르별 영화 개수 계산**
genre_counts = df["장르"].value_counts()

# 📌 **기타 기준 설정**
threshold = 0.02  # 2% 이하인 항목을 "기타"로 묶기
total_count = genre_counts.sum()
genre_counts_percent = genre_counts / total_count  # 비율 계산

# "기타"로 묶을 항목 찾기
small_genres = genre_counts_percent[genre_counts_percent < threshold]
large_genres = genre_counts_percent[genre_counts_percent >= threshold]

# "기타" 값 계산 (최소한 가장 작은 개별 항목보다 작게 만들기)
if not small_genres.empty:
    other_count = small_genres.sum() * total_count
    min_large_value = large_genres.min() * total_count  # 기타보다 작은 최소한의 값 설정
    other_count = min(other_count, min_large_value * 0.9)  # 기타가 너무 크지 않도록 조정
    large_genres["기타"] = other_count / total_count  # 최종 기타 값 추가

# 📌 **파이 차트 (기타 포함)**
st.subheader("📊 Pie Chart: 장르별 영화 개수 (기타 포함)")

fig_pie = px.pie(
    names=large_genres.index,
    values=large_genres.values * total_count,  # 비율을 다시 개수로 변환
    title="장르별 영화 개수 (상위 + 기타)",
    color=large_genres.index,
    color_discrete_sequence=px.colors.qualitative.Set3
)

# 글씨 겹침 해결 & 기타 크기 조정
fig_pie.update_traces(
    textposition="outside",
    textinfo="percent+label",
    marker=dict(line=dict(color='black', width=1))
)

# 📌 **여백 조정 (글씨 짤림 방지)**
fig_pie.update_layout(
    margin=dict(t=50, b=100, l=50, r=50)  # 아래쪽 여백 추가
)

st.plotly_chart(fig_pie)














# 📌 **년도별 평균 관객수 데이터 가공**
df["개봉연도"] = df["개봉일"].astype(str).str[:4]  # 개봉연도 추출
yearly_avg_audience = df.groupby("개봉연도")["관객수"].mean().reset_index()

# 📌 **꺾은선 그래프 (년도별 평균 관객수 변화)**
st.subheader("📈 Line Chart: 년도별 평균 관객수 변화")

fig_line = px.line(
    yearly_avg_audience, x="개봉연도", y="관객수", 
    title="년도별 평균 관객수 변화",
    labels={"개봉연도": "연도", "관객수": "평균 관객수"},
    markers=True
)

st.plotly_chart(fig_line)


# 📌 **막대그래프 (년도별 평균 관객수 비교)**
st.subheader("📊 Bar Chart: 년도별 평균 관객수 비교")

fig_bar = px.bar(
    yearly_avg_audience, x="개봉연도", y="관객수", 
    title="년도별 평균 관객수 비교",
    labels={"개봉연도": "연도", "관객수": "평균 관객수"},
    color="관객수",  # 색상을 관객수에 따라 변화
    color_continuous_scale="Blues"
)

st.plotly_chart(fig_bar)









# 📌 **산점도: 관객수 vs. 매출액**
st.subheader("📊 Scatter Plot: 관객수 vs. 매출액")

fig_scatter = px.scatter(
    df, x="관객수", y="매출액", 
    title="관객수 vs. 매출액",
    labels={"관객수": "관객수", "매출액": "매출액 (원)"},
    hover_name="영화명",
    color="매출액",  # 매출액에 따라 색상을 다르게
    color_continuous_scale="Viridis",
    #size="매출액",  # 매출액이 클수록 점 크기 증가
)

st.plotly_chart(fig_scatter)









# 📌 **막대그래프: 배급사별 매출액 (가독성 개선)**
st.subheader("📊 Bar Chart: 배급사별 매출액 (가독성 개선)")

# 배급사별 총 매출액 계산
distributor_revenue = df.groupby("배급사")["매출액"].sum().reset_index()

# 매출액이 높은 순으로 정렬
distributor_revenue = distributor_revenue.sort_values(by="매출액", ascending=False)

fig_bar_distributor = px.bar(
    distributor_revenue, x="배급사", y="매출액",
    title="배급사별 총 매출액",
    labels={"배급사": "배급사", "매출액": "총 매출액 (원)"},
    color="매출액",
    color_continuous_scale="Blues"
)

# 📌 X축 레이블 회전 & 간격 조정
fig_bar_distributor.update_layout(
    xaxis=dict(
        tickangle=-45,  # X축 레이블을 45도 회전
        tickfont=dict(size=10)  # 글자 크기 줄이기
    ),
    margin=dict(l=20, r=20, t=30, b=150),  # 아래 여백 확장
    showlegend=False  # 📌 범례 제거 (중복 방지)
)

st.plotly_chart(fig_bar_distributor)











# 📌 **개봉일별 매출액 산점도 & 연도별 평균 매출액 라인 추가**
st.subheader("📊 Scatter Plot: 개봉일별 매출액 + 연도별 평균 매출액")

# 개봉 연도(YYYY) 추출
df["개봉연도"] = df["개봉일"].astype(str).str[:4]  # YYYY 형식

# 연도별 평균 매출액 계산
yearly_avg_revenue = df.groupby("개봉연도")["매출액"].mean().reset_index()

# 산점도: 개별 영화 개봉일별 매출액
fig_scatter_release = px.scatter(
    df, x="개봉일", y="매출액",
    title="개봉일별 매출액 (연도별 평균 매출 포함)",
    labels={"개봉일": "개봉일", "매출액": "매출액 (원)"},
    hover_name="영화명",
    color="매출액",
    #size="매출액",
    color_continuous_scale="Reds"
)

# 연도별 평균 매출액 추가 (라인 그래프)
fig_line_avg = px.line(
    yearly_avg_revenue, x="개봉연도", y="매출액",
    labels={"개봉연도": "개봉 연도", "매출액": "평균 매출액 (원)"},
    markers=True
)

# 평균 매출액 라인을 기존 산점도에 추가
for trace in fig_line_avg.data:
    fig_scatter_release.add_trace(trace)

st.plotly_chart(fig_scatter_release)














# 📌 **산점도: 월/일 기준 관객수 (1월~12월)**
st.subheader("📊 Scatter Plot: 월/일별 개봉 영화의 관객수")

# 개봉일에서 월-일(MM-DD) 값만 추출 & datetime 형식으로 변환
df["개봉월일"] = df["개봉일"].astype(str).str[5:10]  # YYYY-MM-DD → MM-DD 추출
df["개봉월일"] = pd.to_datetime(df["개봉월일"], format="%m-%d")  # 날짜형 변환

# X축을 1월 1일부터 12월 31일까지 연속적인 날짜로 설정
fig_scatter_monthly = px.scatter(
    df, x="개봉월일", y="관객수",
    title="월/일별 관객수 산점도 (1월 1일 ~ 12월 31일)",
    labels={"개봉월일": "개봉 월-일 (MM-DD)", "관객수": "관객수"},
    hover_name="영화명",
    color="관객수",
    #size="관객수",
    color_continuous_scale="Magma"
)

# X축을 날짜 형식으로 변경하여 1월 1일부터 12월 31일까지 연속적으로 표시
fig_scatter_monthly.update_xaxes(
    tickformat="%m-%d",  # MM-DD 형식으로 표시
    dtick="M1",  # 한 달 간격으로 눈금 설정
    ticklabelmode="period"
)

st.plotly_chart(fig_scatter_monthly)












# 📌 시각화: TOP 10 영화
st.subheader("📊 Chart: top 10")

top_movies = df.nlargest(10, "관객수")

fig, ax = plt.subplots(figsize=(10, 5))
ax.barh(top_movies["영화명"], top_movies["관객수"], color="skyblue")
ax.set_xlabel("관객수")
ax.set_ylabel("영화명")
ax.set_title("Top 10 Movies by Audience")
ax.invert_yaxis()  # y축 뒤집기 (가장 인기 있는 영화가 위쪽에 오도록)
st.pyplot(fig)