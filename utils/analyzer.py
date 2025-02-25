import pandas as pd
import numpy as np

def analyze_data(df):
    """
    Проводит комплексный анализ данных тикетов.
    
    Args:
        df: DataFrame с данными тикетов
    
    Returns:
        Dict с результатами анализа
    """
    analysis_results = {}

    # Time-based analysis
    analysis_results['hourly_distribution'] = df['date'].dt.hour.value_counts().sort_index().to_dict()
    analysis_results['daily_distribution'] = df['date'].dt.day_name().value_counts().to_dict()
    analysis_results['monthly_distribution'] = df['date'].dt.month.value_counts().sort_index().to_dict()

    # Ticket type analysis
    analysis_results['ticket_type_distribution'] = df['ticket_type'].value_counts().to_dict()
    
    # Status analysis
    analysis_results['status_distribution'] = df['status'].value_counts().to_dict()

    # Response time analysis
    if 'response_time' in df.columns:
        analysis_results['avg_response_time'] = df['response_time'].mean()
        analysis_results['max_response_time'] = df['response_time'].max()
        analysis_results['min_response_time'] = df['response_time'].min()

    # Client analysis
    analysis_results['tickets_per_client'] = df.groupby('client').size().describe().to_dict()

    # Time series analysis
    daily_tickets = df.groupby(df['date'].dt.date).size()
    analysis_results['daily_ticket_counts'] = daily_tickets.to_dict()
    
    # Calculate trends
    analysis_results['trend'] = {
        'total_tickets': len(df),
        'avg_daily_tickets': daily_tickets.mean(),
        'peak_day': daily_tickets.idxmax(),
        'peak_day_count': daily_tickets.max()
    }

    return analysis_results
