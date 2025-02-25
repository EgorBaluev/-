import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from utils.anomaly_detector import analyze_anomalies

def create_visualizations(dfs, analysis_results, period_names):
    """Create and display various visualizations with period comparison."""

    # Create tabs for different visualization categories
    tab1, tab2, tab3, tab4 = st.tabs(["Временной анализ", "Распределение тикетов", "Статистика ответов", "Аномалии"])

    with tab1:
        # Time-based visualizations
        st.subheader("Распределение тикетов по времени")

        # Daily trend comparison
        fig_daily = go.Figure()
        for i, df in enumerate(dfs):
            daily_tickets = df.groupby(df['date'].dt.date).size().reset_index()
            daily_tickets.columns = ['date', 'count']
            fig_daily.add_trace(go.Scatter(
                x=daily_tickets['date'],
                y=daily_tickets['count'],
                name=period_names[i],
                mode='lines'
            ))
        fig_daily.update_layout(title="Сравнение количества тикетов по дням")
        st.plotly_chart(fig_daily, use_container_width=True)

        # Hourly distribution comparison
        fig_hourly = go.Figure()
        for i, df in enumerate(dfs):
            hourly_dist = df['date'].dt.hour.value_counts().sort_index()
            fig_hourly.add_trace(go.Bar(
                x=hourly_dist.index,
                y=hourly_dist.values,
                name=period_names[i],
            ))
        fig_hourly.update_layout(
            title="Сравнение распределения тикетов по часам",
            barmode='group'
        )
        st.plotly_chart(fig_hourly, use_container_width=True)

    with tab2:
        # Ticket type distribution
        st.subheader("Распределение по типам тикетов")

        col1, col2 = st.columns(2)

        with col1:
            # Compare ticket types across periods
            fig_types = go.Figure()
            for i, df in enumerate(dfs):
                type_counts = df['ticket_type'].value_counts()
                fig_types.add_trace(go.Bar(
                    x=type_counts.index,
                    y=type_counts.values,
                    name=period_names[i]
                ))
            fig_types.update_layout(
                title="Сравнение распределения по типам обращений",
                barmode='group'
            )
            st.plotly_chart(fig_types, use_container_width=True)

        with col2:
            # Compare status distribution across periods
            fig_status = go.Figure()
            for i, df in enumerate(dfs):
                status_counts = df['status'].value_counts()
                fig_status.add_trace(go.Bar(
                    x=status_counts.index,
                    y=status_counts.values,
                    name=period_names[i]
                ))
            fig_status.update_layout(
                title="Сравнение распределения по статусам",
                barmode='group'
            )
            st.plotly_chart(fig_status, use_container_width=True)

    with tab3:
        # Response time analysis
        st.subheader("Анализ времени ответа")

        if all('response_time' in df.columns for df in dfs):
            # Compare response time distributions
            fig_response = go.Figure()
            for i, df in enumerate(dfs):
                fig_response.add_trace(go.Histogram(
                    x=df['response_time'],
                    name=period_names[i],
                    opacity=0.7
                ))
            fig_response.update_layout(
                title="Сравнение распределения времени ответа",
                barmode='overlay'
            )
            st.plotly_chart(fig_response, use_container_width=True)

            # Compare average response time by ticket type
            fig_avg_response = go.Figure()
            for i, df in enumerate(dfs):
                avg_response = df.groupby('ticket_type')['response_time'].mean().reset_index()
                fig_avg_response.add_trace(go.Bar(
                    x=avg_response['ticket_type'],
                    y=avg_response['response_time'],
                    name=period_names[i]
                ))
            fig_avg_response.update_layout(
                title="Сравнение среднего времени ответа по типам тикетов",
                barmode='group'
            )
            st.plotly_chart(fig_avg_response, use_container_width=True)

    with tab4:
        # Anomaly detection
        st.subheader("Обнаружение аномалий")

        for i, df in enumerate(dfs):
            st.write(f"### Анализ аномалий для {period_names[i]}")

            anomalies = analyze_anomalies(df)

            # Визуализация аномалий во временном ряду
            if anomalies['daily_tickets']['values'] is not None and len(anomalies['daily_tickets']['values']) > 0:
                fig_anomalies = go.Figure()

                # Добавляем основной временной ряд
                daily_counts = df.groupby(df['date'].dt.date).size()
                fig_anomalies.add_trace(go.Scatter(
                    x=daily_counts.index,
                    y=daily_counts.values,
                    name='Количество тикетов',
                    mode='lines'
                ))

                # Добавляем аномальные точки
                fig_anomalies.add_trace(go.Scatter(
                    x=anomalies['daily_tickets']['dates'],
                    y=anomalies['daily_tickets']['values'],
                    mode='markers',
                    name='Аномалии',
                    marker=dict(
                        size=10,
                        color='red',
                        symbol='circle-open'
                    )
                ))

                fig_anomalies.update_layout(
                    title="Аномалии в количестве тикетов по дням",
                    showlegend=True
                )
                st.plotly_chart(fig_anomalies, use_container_width=True)

                st.write(f"Обнаружено {len(anomalies['daily_tickets']['values'])} аномальных дней")
                st.write(f"Среднее количество тикетов в день: {anomalies['daily_tickets']['mean']:.2f}")

            # Визуализация аномалий во времени ответа
            if anomalies['response_time_anomalies'] is not None:
                resp_anomalies = anomalies['response_time_anomalies']
                if len(resp_anomalies['values']) > 0:
                    st.write("#### Аномалии во времени ответа")
                    st.write(f"Обнаружено {len(resp_anomalies['values'])} аномальных значений")
                    st.write(f"Среднее время ответа: {resp_anomalies['mean']:.2f} часов")

                    fig_resp_anomalies = go.Figure()
                    fig_resp_anomalies.add_trace(go.Box(
                        y=df['response_time'].dropna(),
                        name='Распределение',
                        boxpoints='outliers'
                    ))
                    st.plotly_chart(fig_resp_anomalies, use_container_width=True)

            # Вывод необычных паттернов
            if anomalies['unusual_patterns']:
                st.write("#### Необычные паттерны")
                for pattern in anomalies['unusual_patterns']:
                    st.write(f"- {pattern['description']}")
                    st.write(f"  Часы с необычной активностью: {', '.join(map(str, pattern['hours']))}")

    # Add period comparison metrics
    st.subheader("Сравнительные метрики по периодам")
    metrics_cols = st.columns(len(dfs))
    for i, (df, results) in enumerate(zip(dfs, analysis_results)):
        with metrics_cols[i]:
            st.metric(f"{period_names[i]}", f"{len(df)} тикетов")
            st.metric("Среднее время ответа", f"{df['response_time'].mean():.2f} ч")
            st.metric("Количество клиентов", df['client'].nunique())