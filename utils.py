"""
Utility functions for FINOVA - AI Financial Chatbot
"""

import re
import json
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import streamlit as st

class FinancialCalculations:
    """Financial calculation utilities"""
    
    @staticmethod
    def calculate_compound_interest(principal: float, rate: float, time: int, 
                                  compound_frequency: int = 12) -> float:
        """Calculate compound interest"""
        return principal * (1 + rate/compound_frequency) ** (compound_frequency * time)
    
    @staticmethod
    def calculate_loan_payment(principal: float, rate: float, years: int) -> float:
        """Calculate monthly loan payment using standard loan formula"""
        monthly_rate = rate / 12
        num_payments = years * 12
        if monthly_rate == 0:
            return principal / num_payments
        return principal * (monthly_rate * (1 + monthly_rate)**num_payments) / \
               ((1 + monthly_rate)**num_payments - 1)
    
    @staticmethod
    def calculate_debt_to_income_ratio(monthly_debt_payments: float, 
                                     monthly_income: float) -> float:
        """Calculate debt-to-income ratio"""
        if monthly_income == 0:
            return float('inf')
        return monthly_debt_payments / monthly_income
    
    @staticmethod
    def calculate_emergency_fund_target(monthly_expenses: float, 
                                      months: int = 6) -> float:
        """Calculate emergency fund target"""
        return monthly_expenses * months
    
    @staticmethod
    def calculate_retirement_needs(current_age: int, retirement_age: int, 
                                 current_income: float, 
                                 replacement_ratio: float = 0.8) -> float:
        """Estimate retirement savings needed"""
        years_to_retirement = retirement_age - current_age
        annual_need = current_income * replacement_ratio
        # Simple estimation assuming 4% withdrawal rule
        return annual_need * 25

class DataValidator:
    """Data validation utilities"""
    
    @staticmethod
    def validate_financial_data(data: Dict) -> Tuple[bool, List[str]]:
        """Validate financial input data"""
        errors = []
        
        # Check for negative values where they shouldn't be
        non_negative_fields = ['income', 'savings_amount', 'age']
        for field in non_negative_fields:
            if field in data and data[field] < 0:
                errors.append(f"{field.replace('_', ' ').title()} cannot be negative")
        
        # Check age range
        if 'age' in data and (data['age'] < 18 or data['age'] > 100):
            errors.append("Age must be between 18 and 100")
        
        # Check income vs expenses relationship
        if 'income' in data and 'monthly_expenses' in data:
            monthly_income = data['income'] / 12
            if data['monthly_expenses'] > monthly_income * 2:
                errors.append("Monthly expenses seem unusually high compared to income")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def sanitize_input(text: str) -> str:
        """Sanitize user input text"""
        # Remove potentially harmful characters
        text = re.sub(r'[<>\"\'&]', '', text)
        # Limit length
        text = text[:1000]
        return text.strip()

class ExpenseAnalyzer:
    """Analyze and categorize expenses"""
    
    @staticmethod
    def categorize_expense(description: str) -> str:
        """Automatically categorize expense based on description"""
        description = description.lower()
        
        categories = {
            'housing': ['rent', 'mortgage', 'utilities', 'internet', 'phone'],
            'food': ['grocery', 'restaurant', 'food', 'dining', 'lunch', 'dinner'],
            'transportation': ['gas', 'uber', 'taxi', 'bus', 'train', 'car payment'],
            'entertainment': ['movie', 'netflix', 'spotify', 'game', 'concert'],
            'healthcare': ['doctor', 'medicine', 'hospital', 'insurance', 'dental'],
            'shopping': ['amazon', 'clothes', 'shopping', 'store']
        }
        
        for category, keywords in categories.items():
            if any(keyword in description for keyword in keywords):
                return category.title()
        
        return 'Other'
    
    @staticmethod
    def analyze_spending_pattern(expenses: Dict[str, float]) -> Dict:
        """Analyze spending patterns and return insights"""
        if not expenses:
            return {}
        
        total = sum(expenses.values())
        analysis = {
            'total_expenses': total,
            'highest_category': max(expenses, key=expenses.get),
            'lowest_category': min(expenses, key=expenses.get),
            'category_percentages': {k: (v/total)*100 for k, v in expenses.items()},
            'recommendations': []
        }
        
        # Generate recommendations
        for category, percentage in analysis['category_percentages'].items():
            if category.lower() in ['entertainment', 'shopping'] and percentage > 20:
                analysis['recommendations'].append(
                    f"Consider reducing {category} spending (currently {percentage:.1f}%)"
                )
            elif category.lower() == 'housing' and percentage > 30:
                analysis['recommendations'].append(
                    f"Housing costs are high ({percentage:.1f}%). Consider options to reduce."
                )
        
        return analysis

class ReportGenerator:
    """Generate financial reports and summaries"""
    
    @staticmethod
    def generate_financial_health_score(user_profile, expenses: Dict = None) -> Dict:
        """Calculate a financial health score out of 100"""
        score = 0
        max_score = 100
        feedback = []
        
        if user_profile:
            monthly_income = user_profile.income / 12
            
            # Emergency fund score (25 points)
            if hasattr(user_profile, 'savings_amount') and hasattr(user_profile, 'monthly_expenses'):
                emergency_months = user_profile.savings_amount / user_profile.monthly_expenses if user_profile.monthly_expenses > 0 else 0
                emergency_score = min(emergency_months / 6 * 25, 25)
                score += emergency_score
                
                if emergency_months >= 6:
                    feedback.append("✅ Excellent emergency fund coverage")
                elif emergency_months >= 3:
                    feedback.append("⚠️ Good emergency fund, consider building to 6 months")
                else:
                    feedback.append("❌ Build your emergency fund (aim for 6 months of expenses)")
            
            # Savings rate score (25 points)
            monthly_surplus = monthly_income - user_profile.monthly_expenses
            savings_rate = monthly_surplus / monthly_income if monthly_income > 0 else 0
            savings_score = min(savings_rate / 0.20 * 25, 25)  # 20% target
            score += max(savings_score, 0)  # Don't go negative
            
            if savings_rate >= 0.20:
                feedback.append("✅ Great savings rate!")
            elif savings_rate >= 0.10:
                feedback.append("⚠️ Good savings rate, try to increase if possible")
            else:
                feedback.append("❌ Focus on increasing your savings rate")
            
            # Budget management (25 points)
            expense_ratio = user_profile.monthly_expenses / monthly_income if monthly_income > 0 else 1
            budget_score = max(25 - (expense_ratio - 0.8) * 100, 0)
            score += budget_score
            
            # Diversification/Goals score (25 points)
            if hasattr(user_profile, 'financial_goals') and user_profile.financial_goals:
                goal_score = min(len(user_profile.financial_goals) * 5, 25)
                score += goal_score
                feedback.append(f"✅ You have {len(user_profile.financial_goals)} financial goals defined")
            else:
                feedback.append("❌ Consider setting specific financial goals")
        
        return {
            'score': round(score, 1),
            'grade': ReportGenerator._get_grade(score),
            'feedback': feedback
        }
    
    @staticmethod
    def _get_grade(score: float) -> str:
        """Convert score to letter grade"""
        if score >= 90: return 'A'
        elif score >= 80: return 'B'
        elif score >= 70: return 'C'
        elif score >= 60: return 'D'
        else: return 'F'
    
    @staticmethod
    def generate_monthly_report(user_profile, expenses: Dict) -> str:
        """Generate a comprehensive monthly financial report"""
        if not user_profile:
            return "User profile required for report generation."
        
        monthly_income = user_profile.income / 12
        total_expenses = sum(expenses.values()) if expenses else user_profile.monthly_expenses
        
        report = f"""
# Monthly Financial Report - {datetime.now().strftime('%B %Y')}

## Overview
- **Name:** {user_profile.name}
- **Monthly Income:** ${monthly_income:,.2f}
- **Total Expenses:** ${total_expenses:,.2f}
- **Net Cash Flow:** ${monthly_income - total_expenses:,.2f}

## Financial Health Score
"""
        
        health_score = ReportGenerator.generate_financial_health_score(user_profile, expenses)
        report += f"**Score:** {health_score['score']}/100 (Grade: {health_score['grade']})\n\n"
        
        for feedback_item in health_score['feedback']:
            report += f"- {feedback_item}\n"
        
        if expenses:
            report += "\n## Expense Analysis\n"
            analysis = ExpenseAnalyzer.analyze_spending_pattern(expenses)
            
            report += f"- **Highest Category:** {analysis['highest_category']} (${expenses[analysis['highest_category']]:,.2f})\n"
            
            if analysis['recommendations']:
                report += "\n### Recommendations:\n"
                for rec in analysis['recommendations']:
                    report += f"- {rec}\n"
        
        # Add goal progress
        if hasattr(user_profile, 'financial_goals') and user_profile.financial_goals:
            report += f"\n## Goal Progress\n"
            for goal in user_profile.financial_goals:
                report += f"- {goal}: In Progress\n"
        
        return report

class SecurityManager:
    """Handle data security and privacy"""
    
    @staticmethod
    def encrypt_sensitive_data(data: str) -> str:
        """Basic data obfuscation (implement proper encryption in production)"""
        # This is a simple example - use proper encryption in production
        import base64
        return base64.b64encode(data.encode()).decode()
    
    @staticmethod
    def decrypt_sensitive_data(encrypted_data: str) -> str:
        """Decrypt obfuscated data"""
        import base64
        return base64.b64decode(encrypted_data.encode()).decode()
    
    @staticmethod
    def mask_financial_data(value: float, mask_percentage: float = 0.5) -> str:
        """Mask financial values for display"""
        str_value = f"{value:,.2f}"
        mask_length = int(len(str_value) * mask_percentage)
        return "*" * mask_length + str_value[mask_length:]
    
    @staticmethod
    def validate_session_security() -> bool:
        """Validate session security (placeholder for real implementation)"""
        # Implement proper session validation
        return True

def format_currency(amount: float, currency: str = "USD") -> str:
    """Format currency for display"""
    symbols = {"USD": "$", "EUR": "€", "GBP": "£"}
    symbol = symbols.get(currency, "$")
    return f"{symbol}{amount:,.2f}"

def calculate_percentage_change(old_value: float, new_value: float) -> float:
    """Calculate percentage change between two values"""
    if old_value == 0:
        return 0
    return ((new_value - old_value) / old_value) * 100

def get_risk_color(risk_level: str) -> str:
    """Get color code for risk level visualization"""
    colors = {
        "conservative": "#28a745",  # Green
        "moderate": "#ffc107",      # Yellow
        "aggressive": "#dc3545"     # Red
    }
    return colors.get(risk_level.lower(), "#6c757d")

def create_expense_chart_data(expenses: Dict) -> pd.DataFrame:
    """Create DataFrame for expense visualization"""
    return pd.DataFrame([
        {"Category": category, "Amount": amount, "Percentage": (amount/sum(expenses.values()))*100}
        for category, amount in expenses.items()
    ])

def log_user_interaction(user_id: str, interaction_type: str, details: Dict):
    """Log user interactions for analytics (privacy compliant)"""
    # Implement proper logging with privacy considerations
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "user_id": user_id[:8] + "****",  # Mask user ID
        "interaction_type": interaction_type,
        "details": details
    }
    # In production, save to secure logging system
    pass