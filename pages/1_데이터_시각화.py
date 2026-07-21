import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import io

st.set_page_config(
    page_title='데이터 시각화',
    page_icon='📈',
    layout='wide'
)

st.title('📈 데이터 시각화')

st.markdown("""
CSV 파일을 업로드하여 데이터의 기술통계 시각화를 확인하세요.
""")

# 파일 업로드
uploaded_file = st.file_uploader("CSV 파일을 선택해주세요", type=['csv'])

if uploaded_file is not None:
    # 파일 내용을 메모리에 로드
    file_content = uploaded_file.getvalue()
    
    # 데이터 읽기 (다양한 인코딩 지원) - 백그라운드 처리
    encodings = ['utf-8', 'euc-kr', 'cp949', 'latin-1']
    raw_df = None
    encoding = None
    delimiter = None
    
    # 인코딩 자동 감지
    for enc in encodings:
        try:
            raw_df = pd.read_csv(
                io.BytesIO(file_content), 
                encoding=enc, 
                engine='python',
                on_bad_lines='warn'
            )
            if len(raw_df) > 0:
                encoding = enc
                break
        except Exception:
            continue
    
    if raw_df is None or len(raw_df) == 0:
        st.error("❌ 파일을 읽을 수 없습니다. 파일의 형식을 확인해주세요.")
        st.stop()
    
    # 처리된 데이터프레임 저장
    df = raw_df
    
    st.success("✅ 파일이 성공적으로 업로드되었습니다!")
    
    # 데이터 정보
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("행(Rows)", len(df))
    with col2:
        st.metric("열(Columns)", len(df.columns))
    with col3:
        st.metric("파일 크기", f"{uploaded_file.size / 1024:.2f} KB")
    
    st.divider()
    
    # 데이터 미리보기
    st.subheader("📋 데이터 미리보기")
    st.dataframe(df.head(10), use_container_width=True)
    
    st.divider()
    
    # 변수 정보
    st.subheader("📊 변수 정보")
    
    # 데이터 타입별 분류
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
    datetime_cols = df.select_dtypes(include=['datetime64']).columns.tolist()
    
    # 변수 정보 표시
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📈 수치형 변수", len(numeric_cols))
    with col2:
        st.metric("📝 범주형 변수", len(categorical_cols))
    with col3:
        st.metric("📅 시간형 변수", len(datetime_cols))
    
    # 상세 변수 정보
    st.write("**각 변수의 상세 정보:**")
    
    var_info_data = []
    for col in df.columns:
        dtype = str(df[col].dtype)
        if col in numeric_cols:
            var_type = "수치형 (Numeric)"
        elif col in categorical_cols:
            var_type = "범주형 (Categorical)"
        elif col in datetime_cols:
            var_type = "시간형 (Datetime)"
        else:
            var_type = "기타 (Other)"
        
        missing = df[col].isna().sum()
        missing_pct = (missing / len(df)) * 100
        
        var_info_data.append({
            "변수명": col,
            "타입": var_type,
            "결측값": f"{missing} ({missing_pct:.1f}%)",
            "고유값": df[col].nunique()
        })
    
    var_info_df = pd.DataFrame(var_info_data)
    st.dataframe(var_info_df, use_container_width=True)
    
    st.divider()
    
    if len(numeric_cols) == 0:
        st.warning("⚠️ 숫자형 데이터가 없습니다. 다른 파일을 업로드해주세요.")
    else:
        # 1. 일변수 분석
        st.subheader("📊 1. 일변수 분석")
        
        selected_var = st.selectbox(
            "분석할 변수를 선택하세요",
            numeric_cols,
            key="univariate_var"
        )
        
        # 기본 통계정보 표시
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("평균", f"{df[selected_var].mean():.2f}")
        with col2:
            st.metric("중앙값", f"{df[selected_var].median():.2f}")
        with col3:
            st.metric("표준편차", f"{df[selected_var].std():.2f}")
        with col4:
            st.metric("최솟값", f"{df[selected_var].min():.2f}")
        with col5:
            st.metric("최댓값", f"{df[selected_var].max():.2f}")
        
        st.divider()
        
        # 시각화 유형 선택 (히스토그램, 막대그래프, 박스플롯)
        viz_type = st.radio(
            "시각화 유형을 선택하세요",
            ["히스토그램", "막대그래프", "박스플롯"],
            horizontal=True
        )
        
        if viz_type == "히스토그램":
            fig = px.histogram(
                df,
                x=selected_var,
                nbins=30,
                title=f"'{selected_var}' 분포도",
                labels={selected_var: selected_var},
                color_discrete_sequence=['#636EFA']
            )
            st.plotly_chart(fig, use_container_width=True)
        
        elif viz_type == "막대그래프":
            # 막대그래프는 카테고리별 개수 또는 그룹별 평균값 표시
            value_counts = df[selected_var].value_counts().head(20)
            fig = px.bar(
                x=value_counts.index,
                y=value_counts.values,
                title=f"'{selected_var}' 막대그래프",
                labels={'x': selected_var, 'y': '빈도'},
                color_discrete_sequence=['#636EFA']
            )
            st.plotly_chart(fig, use_container_width=True)
            
        elif viz_type == "박스플롯":
            fig = px.box(
                df,
                y=selected_var,
                title=f"'{selected_var}' 박스플롯",
                labels={selected_var: selected_var},
                color_discrete_sequence=['#636EFA']
            )
            st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
        
        # 2. 이변수 분석
        if len(df.columns) >= 2:
            st.subheader("📊 2. 이변수 분석")
            
            all_cols = df.columns.tolist()
            
            col1, col2 = st.columns(2)
            with col1:
                var_x = st.selectbox(
                    "첫 번째 변수를 선택하세요",
                    all_cols,
                    key="bivariate_x"
                )
            with col2:
                var_y = st.selectbox(
                    "두 번째 변수를 선택하세요",
                    [v for v in all_cols if v != var_x],
                    key="bivariate_y"
                )
            
            if var_x != var_y:
                # 변수의 타입 확인
                def get_var_type(var):
                    if var in numeric_cols:
                        return 'numeric'
                    elif var in categorical_cols:
                        return 'categorical'
                    elif var in datetime_cols:
                        return 'datetime'
                    else:
                        return 'other'
                
                type_x = get_var_type(var_x)
                type_y = get_var_type(var_y)
                
                # 변수 타입 표시
                st.info(f"📊 변수 타입: **{var_x}** ({type_x}) vs **{var_y}** ({type_y})")
                
                # 타입 조합에 따른 그래프 생성
                try:
                    if type_x == 'numeric' and type_y == 'numeric':
                        # 수치 vs 수치: 산점도
                        fig = px.scatter(
                            df,
                            x=var_x,
                            y=var_y,
                            title=f"'{var_x}' vs '{var_y}' 산점도",
                            labels={var_x: var_x, var_y: var_y}
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        
                    elif (type_x == 'numeric' and type_y == 'categorical') or \
                         (type_x == 'categorical' and type_y == 'numeric'):
                        # 수치 vs 범주: 박스플롯
                        if type_x == 'categorical':
                            var_x, var_y = var_y, var_x
                        
                        fig = px.box(
                            df,
                            x=var_y,
                            y=var_x,
                            title=f"'{var_x}' vs '{var_y}' 박스플롯",
                            labels={var_x: var_x, var_y: var_y}
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        
                    elif type_x == 'categorical' and type_y == 'categorical':
                        # 범주 vs 범주: 크로스탭 히트맵
                        crosstab = pd.crosstab(df[var_x], df[var_y])
                        
                        fig = px.imshow(
                            crosstab,
                            labels=dict(x=var_y, y=var_x, color="빈도"),
                            title=f"'{var_x}' vs '{var_y}' 교차표",
                            color_continuous_scale='Blues'
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        
                    elif (type_x == 'datetime' and type_y == 'numeric') or \
                         (type_x == 'numeric' and type_y == 'datetime'):
                        # 시간 vs 수치: 선그래프
                        if type_y == 'datetime':
                            var_x, var_y = var_y, var_x
                        
                        fig = px.line(
                            df.sort_values(var_x),
                            x=var_x,
                            y=var_y,
                            title=f"'{var_x}' vs '{var_y}' 시계열 그래프",
                            labels={var_x: var_x, var_y: var_y}
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        
                    elif (type_x == 'datetime' and type_y == 'categorical') or \
                         (type_x == 'categorical' and type_y == 'datetime'):
                        # 시간 vs 범주: 라인 차트
                        if type_y == 'datetime':
                            var_x, var_y = var_y, var_x
                        
                        df_sorted = df.sort_values(var_x)
                        fig = px.line(
                            df_sorted,
                            x=var_x,
                            y=var_y,
                            color=var_y,
                            title=f"'{var_x}' vs '{var_y}' 시계열 그래프",
                            labels={var_x: var_x, var_y: var_y}
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        
                    else:
                        # 기타 조합: 산점도 시도
                        fig = px.scatter(
                            df,
                            x=var_x,
                            y=var_y,
                            title=f"'{var_x}' vs '{var_y}'",
                            labels={var_x: var_x, var_y: var_y}
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        
                except Exception as e:
                    st.error(f"❌ 그래프를 그릴 수 없습니다: {str(e)}")
            else:
                st.warning("⚠️ 두 변수를 서로 다르게 선택해주세요.")
else:
    st.info("👆 위에서 CSV 파일을 업로드하여 시작하세요!")
