"""
Configuration file for FINOVA - AI Financial Chatbot
"""

import os

# HuggingFace API Configuration
HUGGINGFACE_API_KEY = os.getenv('HUGGINGFACE_API_KEY', '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')
HUGGINGFACE_API_URL = "https://api-inference.huggingface.co/models"

# Model configurations
MODELS = {
    'sentiment_analysis': 'cardiffnlp/twitter-roberta-base-sentiment-latest',
    'text_generation': 'microsoft/DialoGPT-medium',
    'summarization': 'facebook/bart-large-cnn',
    'question_answering': 'deepset/roberta-base-squad2'
}

# Financial advice templates and rules
FINANCIAL_RULES = {
    'emergency_fund_months': 6,
    'max_debt_to_income_ratio': 0.36,
    'recommended_savings_rate': 0.20,
    'high_expense_threshold': 0.15  # 15% of total expenses
}

# User type configurations
USER_TYPES = {
    'student': {
        'savings_rate': 0.10,
        'risk_tolerance': 'moderate',
        'priorities': ['emergency_fund', 'education', 'debt_management']
    },
    'professional': {
        'savings_rate': 0.25,
        'risk_tolerance': 'moderate',
        'priorities': ['retirement', 'investment', 'house_purchase']
    },
    'retiree': {
        'savings_rate': 0.05,
        'risk_tolerance': 'conservative',
        'priorities': ['income_preservation', 'healthcare', 'estate_planning']
    }
}

# Expense categories
EXPENSE_CATEGORIES = [
    'Housing', 'Food', 'Transportation', 'Healthcare',
    'Insurance', 'Entertainment', 'Shopping', 'Education',
    'Debt Payments', 'Savings', 'Other'
]

# Financial advice prompts
ADVICE_PROMPTS = {
    'budgeting': """
    Provide budgeting advice for a {user_type} with income ${income} and monthly expenses ${expenses}.
    Focus on practical, actionable steps they can take immediately.
    """,
    
    'investment': """
    Suggest investment strategies for a {age}-year-old {user_type} with {risk_tolerance} risk tolerance.
    Consider their income of ${income} and current savings of ${savings}.
    """,
    
    'debt': """
    Provide debt management advice for someone with {user_type} status.
    Give specific strategies for debt reduction and prevention.
    """,
    
    'savings': """
    Recommend savings strategies for a {user_type} earning ${income} annually.
    Consider their current savings of ${savings} and financial goals: {goals}.
    """
}