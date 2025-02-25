import streamlit as st
import pandas as pd
from utils.data_processor import process_excel_file
from utils.analyzer import analyze_data
from utils.visualizer import create_visualizations
import plotly.express as px
from datetime import timedelta

st.set_page_config(
    page_title="Анализ тикетов из ТП",
    page_icon="📊",
    layout="wide"
)

# Load custom CSS
with open('assets/style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

st.title("Анализ тикетов из ТП")

# File upload section
uploaded_file = st.file_uploader("Загрузите Excel файл", type=['xls', 'xlsx'])

if uploaded_file is not None:
    try:
        # Process the uploaded file
        df = process_excel_file(uploaded_file)

        # Basic statistics
        st.header("Общая статистика")
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Всего тикетов", len(df))
        with col2:
            st.metric("Уникальных клиентов", df['client'].nunique())
        with col3:
            st.metric("Среднее время ответа", f"{df['response_time'].mean():.2f} ч")

        # Analysis section
        st.header("Анализ данных")

        # Period comparison
        st.subheader("Сравнение периодов")
        num_periods = st.number_input("Количество периодов для сравнения", min_value=1, max_value=3, value=2)

        periods = []
        period_names = ["Первый период", "Второй период", "Третий период"]

        for i in range(num_periods):
            st.subheader(period_names[i])
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input(
                    f"Начало периода {i+1}",
                    value=df['date'].min().date() + timedelta(days=i*30),
                    min_value=df['date'].min().date(),
                    max_value=df['date'].max().date()
                )
            with col2:
                end_date = st.date_input(
                    f"Конец периода {i+1}",
                    value=df['date'].min().date() + timedelta(days=(i+1)*30-1),
                    min_value=df['date'].min().date(),
                    max_value=df['date'].max().date()
                )
            periods.append((start_date, end_date))

        # Additional filters
        st.subheader("Дополнительные фильтры")
        selected_types = st.multiselect(
            "Тип обращения",
            options=df['ticket_type'].unique(),
            default=df['ticket_type'].unique()
        )

        # Create filtered dataframes for each period
        filtered_dfs = []
        for start_date, end_date in periods:
            mask = (
                (df['date'].dt.date >= start_date) &
                (df['date'].dt.date <= end_date) &
                (df['ticket_type'].isin(selected_types))
            )
            filtered_dfs.append(df[mask])

        # Get analysis results for each period
        analysis_results = [analyze_data(filtered_df) for filtered_df in filtered_dfs]

        # Display visualizations
        st.header("Визуализация")
        create_visualizations(filtered_dfs, analysis_results, period_names[:num_periods])

    except Exception as e:
        st.error(f"Ошибка при обработке файла: {str(e)}")