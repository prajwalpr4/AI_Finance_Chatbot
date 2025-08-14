import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import requests
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import hashlib

# Import our custom modules
from config import *
from utils import *

# Set page config
st.set_page_config(
    page_title="FINOVA - AI Financial Advisor",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    .chat-message {
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
    }
    .expense-category {
        background-color: #e8f4ff;
        padding: 0.5rem;
        margin: 0.25rem 0;
        border-radius: 5px;
    }
    .financial-tip {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

@dataclass
class UserProfile:
    name: str
    age: int
    income: float
    occupation: str
    financial_goals: List[str]
    risk_tolerance: str
    savings_amount: float
    monthly_expenses: float
    user_type: str
    created_at: str = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()

class EnhancedFinancialChatbot:
    def __init__(self):
        self.conversation_history = []
        self.user_profile = None
        self.session_id = self._generate_session_id()
        
    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        return hashlib.md5(str(datetime.now()).encode()).hexdigest()[:8]
    
    def call_huggingface_api(self, model_name: str, payload: dict) -> dict:
        """Enhanced API call with better error handling"""
        try:
            headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}
            api_url = f"{HUGGINGFACE_API_URL}/{model_name}"
            
            response = requests.post(api_url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 503:
                st.warning("AI model is loading. Please try again in a moment.")
                return {}
            else:
                st.error(f"API Error: {response.status_code} - {response.text}")
                return {}
                
        except requests.exceptions.Timeout:
            st.error("Request timed out. Please try again.")
            return {}
        except Exception as e:
            st.error(f"Error calling API: {str(e)}")
            return {}
    
    def analyze_sentiment(self, text: str) -> str:
        """Analyze sentiment with fallback"""
        payload = {"inputs": text}
        result = self.call_huggingface_api(MODELS['sentiment_analysis'], payload)
        
        if result and isinstance(result, list) and len(result) > 0:
            sentiment_data = result[0]
            if isinstance(sentiment_data, list) and len(sentiment_data) > 0:
                top_sentiment = max(sentiment_data, key=lambda x: x.get('score', 0))
                label = top_sentiment.get('label', 'NEUTRAL')
                # Map labels to standard format
                label_mapping = {'LABEL_0': 'NEGATIVE', 'LABEL_1': 'NEUTRAL', 'LABEL_2': 'POSITIVE'}
                return label_mapping.get(label, label)
        
        # Fallback sentiment analysis
        return self._simple_sentiment_analysis(text)
    
    def _simple_sentiment_analysis(self, text: str) -> str:
        """Simple rule-based sentiment analysis as fallback"""
        text = text.lower()
        positive_words = ['good', 'great', 'excellent', 'happy', 'satisfied', 'love', 'amazing']
        negative_words = ['bad', 'terrible', 'awful', 'hate', 'worried', 'concerned', 'problem']
        
        positive_count = sum(1 for word in positive_words if word in text)
        negative_count = sum(1 for word in negative_words if word in text)
        
        if positive_count > negative_count:
            return 'POSITIVE'
        elif negative_count > positive_count:
            return 'NEGATIVE'
        else:
            return 'NEUTRAL'
    
    def classify_intent(self, text: str) -> str:
        """Enhanced intent classification"""
        text_lower = text.lower()
        
        # Use more sophisticated keyword matching
        intent_patterns = {
            'budgeting': [
                'budget', 'expense', 'spend', 'cost', 'money management',
                'track spending', 'monthly budget', 'expense tracking'
            ],
            'investment': [
                'invest', 'stock', 'bond', 'portfolio', 'return', 'market',
                'mutual fund', '401k', 'retirement account', 'dividend'
            ],
            'savings': [
                'save', 'saving', 'emergency fund', 'deposit', 'savings account',
                'high yield', 'cd', 'certificate of deposit'
            ],
            'debt': [
                'debt', 'loan', 'credit', 'payment', 'owe', 'mortgage',
                'student loan', 'credit card', 'refinance'
            ],
            'tax': [
                'tax', 'deduction', 'filing', 'refund', 'irs',
                'tax return', 'withholding', 'tax planning'
            ],
            'insurance': [
                'insurance', 'health insurance', 'life insurance',
                'auto insurance', 'coverage', 'premium'
            ],
            'retirement': [
                'retirement', 'retire', 'pension', '401k', 'ira',
                'retirement planning', 'social security'
            ]
        }
        
        # Calculate match scores for each intent
        intent_scores = {}
        for intent, keywords in intent_patterns.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                intent_scores[intent] = score
        
        if intent_scores:
            return max(intent_scores, key=intent_scores.get)
        
        return 'general'
    
    def generate_personalized_response(self, user_input: str, intent: str, sentiment: str) -> str:
        """Generate comprehensive personalized response"""
        if not self.user_profile:
            return self._get_onboarding_message()
        
        # Get base advice
        base_advice = self._get_intent_specific_advice(intent, user_input, sentiment)
        
        # Add personalization based on user profile
        personalized_advice = self._personalize_advice(base_advice, intent, sentiment)
        
        # Add dynamic tips
        tips = self._get_contextual_tips(intent)
        
        response = f"{personalized_advice}\n\n💡 **Quick Tip:** {tips}"
        
        return response
    
    def _get_onboarding_message(self) -> str:
        """Get onboarding message for new users"""
        return """
Welcome to FINOVA - Your AI Financial Advisor! 🎉

I'm here to help you make smarter financial decisions and achieve your financial goals. To provide you with personalized advice, I need to learn about your financial situation first.

Please complete your profile in the sidebar, and then I can help you with:
- 📊 Budget planning and expense tracking
- 💰 Investment strategies
- 🏦 Savings optimization  
- 💳 Debt management
- 📈 Financial goal setting

Once your profile is set up, ask me anything about your finances!
        """
    
    def _get_intent_specific_advice(self, intent: str, user_input: str, sentiment: str) -> str:
        """Get specific advice based on intent"""
        advice_generators = {
            'budgeting': self._get_budgeting_advice,
            'investment': self._get_investment_advice,
            'savings': self._get_savings_advice,
            'debt': self._get_debt_advice,
            'tax': self._get_tax_advice,
            'insurance': self._get_insurance_advice,
            'retirement': self._get_retirement_advice,
            'general': self._get_general_advice
        }
        
        generator = advice_generators.get(intent, self._get_general_advice)
        return generator(user_input, sentiment)
    
    def _get_budgeting_advice(self, user_input: str, sentiment: str) -> str:
        """Enhanced budgeting advice"""
        monthly_income = self.user_profile.income / 12
        monthly_surplus = monthly_income - self.user_profile.monthly_expenses
        
        advice = "## 📊 Budgeting Advice\n\n"
        
        if monthly_surplus > 0:
            savings_rate = (monthly_surplus / monthly_income) * 100
            advice += f"Great news! You have a monthly surplus of **${monthly_surplus:,.2f}** ({savings_rate:.1f}% savings rate).\n\n"
            
            if savings_rate < 10:
                advice += "**Recommendation:** Try to increase your savings rate to at least 10-15% of income.\n"
            elif savings_rate < 20:
                advice += "**Recommendation:** You're doing well! Consider pushing towards a 20% savings rate.\n"
            else:
                advice += "**Excellent!** You're exceeding the recommended 20% savings rate.\n"
        else:
            deficit = abs(monthly_surplus)
            advice += f"⚠️ You're spending **${deficit:,.2f}** more than you earn monthly.\n\n"
            advice += "**Immediate Actions:**\n"
            advice += "1. Track every expense for 30 days\n"
            advice += "2. Identify your top 3 expense categories\n"
            advice += "3. Find ways to reduce spending by 10-15%\n"
        
        # Add user-type specific advice
        if self.user_profile.user_type == 'student':
            advice += "\n**Student-Specific Tips:**\n"
            advice += "- Use the 50/30/20 rule: 50% needs, 30% wants, 20% savings\n"
            advice += "- Take advantage of student discounts\n"
            advice += "- Consider part-time work or freelancing\n"
        elif self.user_profile.user_type == 'professional':
            advice += "\n**Professional Tips:**\n"
            advice += "- Automate your savings and investments\n"
            advice += "- Review and optimize subscription services\n"
            advice += "- Consider meal prepping to reduce food costs\n"
        
        return advice
    
    def _get_investment_advice(self, user_input: str, sentiment: str) -> str:
        """Enhanced investment advice"""
        advice = "## 💰 Investment Advice\n\n"
        
        # Risk-based recommendations
        risk_strategies = {
            'conservative': {
                'allocation': '20% stocks, 80% bonds/CDs',
                'instruments': 'Treasury bonds, high-grade corporate bonds, CDs',
                'expected_return': '3-5% annually'
            },
            'moderate': {
                'allocation': '60% stocks, 40% bonds',
                'instruments': 'Index funds, target-date funds, balanced funds',
                'expected_return': '6-8% annually'
            },
            'aggressive': {
                'allocation': '80-90% stocks, 10-20% bonds',
                'instruments': 'Growth stocks, small-cap funds, international funds',
                'expected_return': '8-12% annually (with higher volatility)'
            }
        }
        
        risk_profile = risk_strategies.get(self.user_profile.risk_tolerance.lower(), risk_strategies['moderate'])
        
        advice += f"Based on your **{self.user_profile.risk_tolerance}** risk tolerance:\n\n"
        advice += f"**Recommended Allocation:** {risk_profile['allocation']}\n"
        advice += f"**Investment Types:** {risk_profile['instruments']}\n"
        advice += f"**Expected Returns:** {risk_profile['expected_return']}\n\n"
        
        # Age-based advice
        if self.user_profile.age < 30:
            advice += "**Age Advantage:** You have time for aggressive growth. Consider:\n"
            advice += "- Maximum 401(k) employer match\n"
            advice += "- Roth IRA for tax-free growth\n"
            advice += "- Growth-focused index funds\n"
        elif self.user_profile.age > 50:
            advice += "**Pre-Retirement Focus:** Start shifting towards preservation:\n"
            advice += "- Gradually reduce stock allocation\n"
            advice += "- Increase bond/stable investments\n"
            advice += "- Consider catch-up contributions\n"
        
        # Calculate potential growth
        current_savings = self.user_profile.savings_amount
        monthly_surplus = (self.user_profile.income / 12) - self.user_profile.monthly_expenses
        
        if monthly_surplus > 0 and current_savings > 0:
            # Simple compound interest calculation
            years = 10
            rate = 0.07  # 7% average return
            future_value = FinancialCalculations.calculate_compound_interest(
                current_savings + (monthly_surplus * 12 * years), rate, years, 1
            )
            advice += f"\n**Growth Projection:** If you invest ${monthly_surplus:,.2f}/month for {years} years at 7% return, "
            advice += f"you could have approximately **${future_value:,.2f}**\n"
        
        return advice
    
    def _get_savings_advice(self, user_input: str, sentiment: str) -> str:
        """Enhanced savings advice"""
        advice = "## 🏦 Savings Strategy\n\n"
        
        # Emergency fund analysis
        emergency_target = self.user_profile.monthly_expenses * 6
        current_coverage = self.user_profile.savings_amount / emergency_target if emergency_target > 0 else 0
        
        advice += "**Emergency Fund Status:**\n"
        if current_coverage >= 1:
            advice += f"✅ Excellent! You have {current_coverage:.1f} months of expenses covered.\n"
            advice += "Consider high-yield savings accounts or short-term CDs for this money.\n\n"
        elif current_coverage >= 0.5:
            deficit = emergency_target - self.user_profile.savings_amount
            advice += f"⚠️ You're halfway there! Need ${deficit:,.2f} more for full 6-month coverage.\n"
            advice += "Priority: Complete your emergency fund before aggressive investing.\n\n"
        else:
            advice += f"❌ Emergency fund needs attention. Target: ${emergency_target:,.2f}\n"
            advice += f"Current: ${self.user_profile.savings_amount:,.2f}\n"
            advice += "**Action Plan:** Save $500-1000/month until you reach your target.\n\n"
        
        # Savings vehicles
        advice += "**Best Savings Options:**\n"
        advice += "1. **High-Yield Savings Account** (4-5% APY) - Emergency fund\n"
        advice += "2. **Certificate of Deposits** (4-6% APY) - Short-term goals\n"
        advice += "3. **Money Market Account** (3-4% APY) - Medium liquidity needs\n\n"
        
        # Goal-based savings
        if hasattr(self.user_profile, 'financial_goals') and self.user_profile.financial_goals:
            advice += "**Goal-Based Savings:**\n"
            for goal in self.user_profile.financial_goals:
                if goal.lower() == 'buy a house':
                    advice += f"🏠 **{goal}:** Save 20% down payment + closing costs\n"
                elif goal.lower() == 'retirement':
                    advice += f"🏖️ **{goal}:** Target 25x annual expenses by retirement\n"
                else:
                    advice += f"🎯 **{goal}:** Create specific savings timeline\n"
        
        return advice
    
    def _get_debt_advice(self, user_input: str, sentiment: str) -> str:
        """Enhanced debt management advice"""
        advice = "## 💳 Debt Management Strategy\n\n"
        
        advice += "**Debt Elimination Methods:**\n\n"
        advice += "**1. Debt Avalanche (Mathematically Optimal):**\n"
        advice += "- Pay minimums on all debts\n"
        advice += "- Put extra money toward highest interest rate debt\n"
        advice += "- Saves most money long-term\n\n"
        
        advice += "**2. Debt Snowball (Psychologically Motivating):**\n"
        advice += "- Pay minimums on all debts\n"
        advice += "- Put extra money toward smallest balance\n"
        advice += "- Builds momentum and motivation\n\n"
        
        # Debt prioritization
        advice += "**Priority Order (Avalanche Method):**\n"
        advice += "1. Credit Cards (15-25% interest)\n"
        advice += "2. Personal Loans (8-15% interest)\n"
        advice += "3. Auto Loans (3-7% interest)\n"
        advice += "4. Student Loans (3-6% interest)\n"
        advice += "5. Mortgage (3-5% interest)\n\n"
        
        # Debt prevention
        advice += "**Prevention Strategies:**\n"
        advice += "- Build emergency fund to avoid new debt\n"
        advice += "- Use credit cards only if you can pay full balance\n"
        advice += "- Consider debt consolidation for multiple high-interest debts\n"
        advice += "- Negotiate with creditors for better rates\n"
        
        return advice
    
    def _get_tax_advice(self, user_input: str, sentiment: str) -> str:
        """Tax optimization advice"""
        advice = "## 📋 Tax Optimization\n\n"
        
        if self.user_profile.user_type == 'student':
            advice += "**Student Tax Benefits:**\n"
            advice += "- American Opportunity Tax Credit (up to $2,500)\n"
            advice += "- Student loan interest deduction\n"
            advice += "- Tax-free scholarships and grants\n\n"
        else:
            advice += "**Key Tax Strategies:**\n"
            advice += "- Maximize 401(k) contributions ($23,000 limit for 2024)\n"
            advice += "- Contribute to Traditional or Roth IRA ($7,000 limit)\n"
            advice += "- Use HSA if eligible (triple tax advantage)\n"
            advice += "- Track deductible expenses throughout the year\n\n"
        
        # Income-based advice
        if self.user_profile.income > 100000:
            advice += "**Higher Income Strategies:**\n"
            advice += "- Consider backdoor Roth IRA conversion\n"
            advice += "- Maximize pre-tax retirement contributions\n"
            advice += "- Look into tax-loss harvesting\n"
        
        return advice
    
    def _get_insurance_advice(self, user_input: str, sentiment: str) -> str:
        """Insurance recommendations"""
        advice = "## 🛡️ Insurance Protection\n\n"
        
        advice += "**Essential Insurance Types:**\n\n"
        
        if self.user_profile.user_type == 'student':
            advice += "**Student Priorities:**\n"
            advice += "1. Health insurance (stay on parents' plan if possible)\n"
            advice += "2. Renter's insurance (very affordable)\n"
            advice += "3. Auto insurance (if you have a car)\n\n"
        else:
            advice += "**Professional Priorities:**\n"
            advice += "1. Health insurance (employer or marketplace)\n"
            advice += "2. Life insurance (10x annual income if dependents)\n"
            advice += "3. Disability insurance (60% of income replacement)\n"
            advice += "4. Auto insurance (appropriate coverage limits)\n"
            advice += "5. Homeowner's/Renter's insurance\n\n"
        
        advice += "**Money-Saving Tips:**\n"
        advice += "- Shop around annually for better rates\n"
        advice += "- Increase deductibles to lower premiums\n"
        advice += "- Bundle policies with same company for discounts\n"
        advice += "- Maintain good credit score for better rates\n"
        
        return advice
    
    def _get_retirement_advice(self, user_input: str, sentiment: str) -> str:
        """Retirement planning advice"""
        advice = "## 🏖️ Retirement Planning\n\n"
        
        # Calculate retirement needs
        retirement_age = 65
        years_to_retirement = max(retirement_age - self.user_profile.age, 0)
        
        if years_to_retirement > 0:
            retirement_needs = FinancialCalculations.calculate_retirement_needs(
                self.user_profile.age, retirement_age, self.user_profile.income
            )
            
            advice += f"**Retirement Timeline:** {years_to_retirement} years to go\n"
            advice += f"**Estimated Need:** ${retirement_needs:,.2f} (using 4% withdrawal rule)\n\n"
            
            # Monthly savings needed
            monthly_needed = retirement_needs / (years_to_retirement * 12)
            advice += f"**Monthly Savings Target:** ${monthly_needed:,.2f}\n\n"
        else:
            advice += "**Already at retirement age!** Focus on:\n"
            advice += "- Optimizing withdrawal strategies\n"
            advice += "- Healthcare planning\n"
            advice += "- Estate planning\n\n"
        
        advice += "**Retirement Accounts Priority:**\n"
        advice += "1. 401(k) up to employer match (free money!)\n"
        advice += "2. Roth IRA (tax-free growth)\n"
        advice += "3. Max out 401(k) contribution\n"
        advice += "4. Taxable investment accounts\n\n"
        
        # Age-specific advice
        if self.user_profile.age < 30:
            advice += "**20s Advantage:** Time is your biggest asset!\n"
            advice += "- Start with any amount, even $50/month\n"
            advice += "- Take advantage of compound growth\n"
            advice += "- Focus on growth investments\n"
        elif self.user_profile.age < 50:
            advice += "**Peak Earning Years:** Accelerate savings\n"
            advice += "- Increase contributions with raises\n"
            advice += "- Diversify investment portfolio\n"
            advice += "- Consider professional financial advice\n"
        else:
            advice += "**Pre-Retirement:** Catch-up mode\n"
            advice += "- Use catch-up contributions ($7,500 extra for 401k)\n"
            advice += "- Shift towards more conservative investments\n"
            advice += "- Plan for healthcare costs\n"
        
        return advice
    
    def _get_general_advice(self, user_input: str = "", sentiment: str = "NEUTRAL") -> str:
        """General financial advice"""
        advice = "## 💼 General Financial Guidance\n\n"
        
        # Financial health assessment
        health_score = ReportGenerator.generate_financial_health_score(self.user_profile)
        advice += f"**Your Financial Health Score:** {health_score['score']}/100 (Grade: {health_score['grade']})\n\n"
        
        # Personalized recommendations based on profile
        monthly_income = self.user_profile.income / 12
        monthly_surplus = monthly_income - self.user_profile.monthly_expenses
        
        advice += "**Personalized Action Plan:**\n"
        
        # Priority 1: Emergency Fund
        emergency_target = self.user_profile.monthly_expenses * 6
        if self.user_profile.savings_amount < emergency_target:
            deficit = emergency_target - self.user_profile.savings_amount
            advice += f"1. **Build Emergency Fund:** Save ${deficit:,.2f} more (${deficit/6:,.2f}/month for 6 months)\n"
        else:
            advice += "1. ✅ **Emergency Fund Complete:** Well done!\n"
        
        # Priority 2: High-Interest Debt
        advice += "2. **Eliminate High-Interest Debt:** Pay off credit cards and personal loans first\n"
        
        # Priority 3: Retirement Savings
        if self.user_profile.age < 65:
            advice += "3. **Retirement Savings:** Aim for 10-15% of income in retirement accounts\n"
        
        # Priority 4: Investment Growth
        if monthly_surplus > 0:
            advice += f"4. **Investment Growth:** With ${monthly_surplus:,.2f} monthly surplus, consider diversified investing\n"
        
        advice += "\n**Key Financial Principles:**\n"
        advice += "- Pay yourself first (automate savings)\n"
        advice += "- Live below your means\n"
        advice += "- Diversify investments\n"
        advice += "- Review and adjust regularly\n"
        
        return advice
    
    def _personalize_advice(self, base_advice: str, intent: str, sentiment: str) -> str:
        """Add personalization based on user profile and sentiment"""
        personalization = ""
        
        # Sentiment-based personalization
        if sentiment == 'NEGATIVE':
            personalization += "I understand you might be feeling stressed about your finances. Take it one step at a time - small improvements add up! 💪\n\n"
        elif sentiment == 'POSITIVE':
            personalization += "Great to see your positive attitude about finances! Let's build on that momentum. 🚀\n\n"
        
        # User type personalization
        if self.user_profile.user_type == 'student':
            personalization += f"As a student, focus on building good financial habits now - they'll serve you well throughout your career.\n\n"
        elif self.user_profile.user_type == 'professional':
            personalization += f"With your professional status, you're in a great position to accelerate your financial goals.\n\n"
        elif self.user_profile.user_type == 'retiree':
            personalization += f"In retirement, focus on preservation and sustainable income strategies.\n\n"
        
        return personalization + base_advice
    
    def _get_contextual_tips(self, intent: str) -> str:
        """Get contextual tips based on intent"""
        tips = {
            'budgeting': "Try the 24-hour rule: wait a day before making non-essential purchases over $100.",
            'investment': "Dollar-cost averaging reduces the impact of market volatility - invest the same amount regularly.",
            'savings': "Automate your savings by setting up automatic transfers to your savings account on payday.",
            'debt': "Consider the debt avalanche method: pay minimums on all debts, then attack the highest interest rate first.",
            'tax': "Keep receipts and documents organized throughout the year - don't wait until tax season!",
            'insurance': "Review your insurance coverage annually, especially after major life events.",
            'retirement': "Every year you delay retirement saving, you need to save roughly twice as much to catch up.",
            'general': "Track your net worth monthly - it's the best single metric of financial progress."
        }
        
        return tips.get(intent, tips['general'])

def create_expense_visualization(expenses: Dict) -> go.Figure:
    """Create interactive expense visualization"""
    if not expenses:
        return go.Figure()
    
    # Create pie chart
    fig = go.Figure(data=[
        go.Pie(
            labels=list(expenses.keys()),
            values=list(expenses.values()),
            hole=0.3,
            textinfo='label+percent',
            textposition='outside',
            marker_colors=px.colors.qualitative.Set3
        )
    ])
    
    fig.update_layout(
        title="Monthly Expense Breakdown",
        font_size=12,
        showlegend=True,
        height=400
    )
    
    return fig

def create_savings_projection_chart(user_profile, monthly_savings: float) -> go.Figure:
    """Create savings projection visualization"""
    if not user_profile or monthly_savings <= 0:
        return go.Figure()
    
    months = list(range(0, 121))  # 10 years
    savings_balance = []
    current_savings = user_profile.savings_amount
    
    for month in months:
        balance = current_savings + (monthly_savings * month)
        # Add compound interest (assuming 4% annual return)
        if month > 0:
            annual_return = 0.04
            monthly_return = annual_return / 12
            balance = current_savings * ((1 + monthly_return) ** month) + \
                     monthly_savings * (((1 + monthly_return) ** month - 1) / monthly_return)
        savings_balance.append(balance)
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=[m/12 for m in months],  # Convert to years
        y=savings_balance,
        mode='lines',
        name='Projected Savings',
        line=dict(color='#1f77b4', width=3)
    ))
    
    fig.update_layout(
        title="Savings Growth Projection (10 Years)",
        xaxis_title="Years",
        yaxis_title="Savings Balance ($)",
        height=400,
        showlegend=True
    )
    
    return fig

def main():
    # Initialize session state
    if 'chatbot' not in st.session_state:
        st.session_state.chatbot = EnhancedFinancialChatbot()
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'expenses' not in st.session_state:
        st.session_state.expenses = {}
    
    # Header
    st.markdown('<h1 class="main-header">🤖 FINOVA - AI Financial Advisor</h1>', unsafe_allow_html=True)
    st.markdown("### Your intelligent financial companion powered by advanced AI")
    
    # Sidebar - User Profile Management
    with st.sidebar:
        st.header("👤 User Profile")
        
        if st.session_state.chatbot.user_profile is None:
            st.markdown("**Complete your profile for personalized advice**")
            
            with st.form("profile_form"):
                name = st.text_input("Full Name *")
                age = st.number_input("Age *", min_value=18, max_value=100, value=25)
                income = st.number_input("Annual Income ($) *", min_value=0, value=50000, step=1000)
                occupation = st.selectbox("Occupation", 
                    ["Student", "Software Engineer", "Teacher", "Doctor", "Nurse", 
                     "Business Owner", "Sales", "Marketing", "Finance", "Other"])
                
                user_type = st.selectbox("User Type", ["student", "professional", "retiree"])
                risk_tolerance = st.selectbox("Risk Tolerance", ["conservative", "moderate", "aggressive"])
                
                col1, col2 = st.columns(2)
                with col1:
                    savings = st.number_input("Current Savings ($)", min_value=0, value=5000, step=500)
                with col2:
                    monthly_expenses = st.number_input("Monthly Expenses ($)", min_value=0, value=3000, step=100)
                
                goals = st.multiselect("Financial Goals", 
                    ["Emergency Fund", "Buy a House", "Retirement", "Pay off Debt", 
                     "Investment Growth", "Education", "Travel", "Start Business"])
                
                submitted = st.form_submit_button("💾 Save Profile")
                
                if submitted:
                    if name and age and income:
                        # Validate data
                        is_valid, errors = DataValidator.validate_financial_data({
                            'name': name, 'age': age, 'income': income,
                            'savings_amount': savings, 'monthly_expenses': monthly_expenses
                        })
                        
                        if is_valid:
                            st.session_state.chatbot.user_profile = UserProfile(
                                name=name, age=age, income=income, occupation=occupation,
                                financial_goals=goals, risk_tolerance=risk_tolerance,
                                savings_amount=savings, monthly_expenses=monthly_expenses,
                                user_type=user_type
                            )
                            st.success("✅ Profile saved successfully!")
                            st.rerun()
                        else:
                            for error in errors:
                                st.error(f"❌ {error}")
                    else:
                        st.error("❌ Please fill in all required fields marked with *")
        
        else:
            # Display existing profile
            profile = st.session_state.chatbot.user_profile
            st.markdown(f"**👋 Welcome back, {profile.name}!**")
            
            with st.expander("📊 Profile Summary"):
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Age", f"{profile.age}")
                    st.metric("Income", f"${profile.income:,.0f}")
                with col2:
                    st.metric("Savings", f"${profile.savings_amount:,.0f}")
                    st.metric("Monthly Expenses", f"${profile.monthly_expenses:,.0f}")
                
                st.write(f"**Type:** {profile.user_type.title()}")
                st.write(f"**Risk Tolerance:** {profile.risk_tolerance.title()}")
                if profile.financial_goals:
                    st.write(f"**Goals:** {', '.join(profile.financial_goals)}")
            
            if st.button("✏️ Edit Profile"):
                st.session_state.chatbot.user_profile = None
                st.rerun()
            
            # Financial Health Score
            health_score = ReportGenerator.generate_financial_health_score(profile, st.session_state.expenses)
            
            st.markdown("### 🏥 Financial Health")
            score_color = "green" if health_score['score'] >= 80 else "orange" if health_score['score'] >= 60 else "red"
            st.markdown(f"**Score:** <span style='color: {score_color}; font-size: 1.2em;'>{health_score['score']}/100 ({health_score['grade']})</span>", 
                       unsafe_allow_html=True)
            
            with st.expander("📋 Feedback Details"):
                for feedback in health_score['feedback']:
                    st.write(f"• {feedback}")
    
    # Main Content Area
    col1, col2 = st.columns([2, 1])
    
    # Left Column - Chat Interface
    with col1:
        st.header("💬 Chat with FINOVA")
        
        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # Chat input
        if prompt := st.chat_input("Ask me anything about your finances..."):
            # Add user message
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Generate AI response
            with st.chat_message("assistant"):
                with st.spinner("Analyzing your question..."):
                    # Sanitize input
                    clean_prompt = DataValidator.sanitize_input(prompt)
                    
                    # Analyze sentiment and intent
                    sentiment = st.session_state.chatbot.analyze_sentiment(clean_prompt)
                    intent = st.session_state.chatbot.classify_intent(clean_prompt)
                    
                    # Generate response
                    response = st.session_state.chatbot.generate_personalized_response(
                        clean_prompt, intent, sentiment
                    )
                    
                    st.markdown(response)
                    
                    # Show analysis details in expander
                    with st.expander("🔍 Analysis Details"):
                        col_a, col_b = st.columns(2)
                        with col_a:
                            st.write(f"**Sentiment:** {sentiment}")
                        with col_b:
                            st.write(f"**Intent:** {intent.title()}")
            
            # Add assistant message
            st.session_state.messages.append({"role": "assistant", "content": response})
    
    # Right Column - Financial Tools and Visualizations
    with col2:
        st.header("🔧 Financial Tools")
        
        # Expense Tracker
        with st.expander("💳 Expense Tracker", expanded=True):
            st.subheader("Track Your Expenses")
            
            with st.form("expense_form"):
                col_a, col_b = st.columns(2)
                with col_a:
                    category = st.selectbox("Category", EXPENSE_CATEGORIES)
                with col_b:
                    amount = st.number_input("Amount ($)", min_value=0.0, step=10.0)
                
                description = st.text_input("Description (optional)")
                add_expense = st.form_submit_button("➕ Add Expense")
                
                if add_expense and amount > 0:
                    if category in st.session_state.expenses:
                        st.session_state.expenses[category] += amount
                    else:
                        st.session_state.expenses[category] = amount
                    st.success(f"Added ${amount:.2f} to {category}")
                    st.rerun()
            
            # Display current expenses
            if st.session_state.expenses:
                st.write("**Current Expenses:**")
                total = sum(st.session_state.expenses.values())
                
                for cat, amt in sorted(st.session_state.expenses.items(), key=lambda x: x[1], reverse=True):
                    percentage = (amt / total) * 100
                    st.markdown(f"<div class='expense-category'>{cat}: ${amt:.2f} ({percentage:.1f}%)</div>", 
                               unsafe_allow_html=True)
                
                st.write(f"**Total: ${total:.2f}**")
                
                # Action buttons
                col_x, col_y, col_z = st.columns(3)
                with col_x:
                    if st.button("📊 Analyze"):
                        analysis = ExpenseAnalyzer.analyze_spending_pattern(st.session_state.expenses)
                        st.write("**Analysis:**")
                        st.write(f"Highest: {analysis['highest_category']}")
                        for rec in analysis.get('recommendations', []):
                            st.warning(rec)
                
                with col_y:
                    if st.button("📋 Report"):
                        if st.session_state.chatbot.user_profile:
                            report = ReportGenerator.generate_monthly_report(
                                st.session_state.chatbot.user_profile, st.session_state.expenses
                            )
                            st.markdown(report)
                
                with col_z:
                    if st.button("🗑️ Clear"):
                        st.session_state.expenses = {}
                        st.rerun()
        
        # Financial Calculator
        with st.expander("🧮 Financial Calculator"):
            calc_type = st.selectbox("Calculator Type", 
                ["Compound Interest", "Loan Payment", "Retirement Needs"])
            
            if calc_type == "Compound Interest":
                principal = st.number_input("Initial Amount ($)", value=1000, step=100)
                rate = st.number_input("Annual Interest Rate (%)", value=7.0, step=0.1) / 100
                years = st.number_input("Years", value=10, step=1)
                
                if st.button("Calculate"):
                    result = FinancialCalculations.calculate_compound_interest(principal, rate, years)
                    st.success(f"Future Value: ${result:,.2f}")
                    st.write(f"Total Growth: ${result - principal:,.2f}")
            
            elif calc_type == "Loan Payment":
                principal = st.number_input("Loan Amount ($)", value=200000, step=1000)
                rate = st.number_input("Annual Interest Rate (%)", value=4.0, step=0.1) / 100
                years = st.number_input("Loan Term (Years)", value=30, step=1)
                
                if st.button("Calculate"):
                    payment = FinancialCalculations.calculate_loan_payment(principal, rate, years)
                    st.success(f"Monthly Payment: ${payment:,.2f}")
                    total_paid = payment * years * 12
                    st.write(f"Total Interest: ${total_paid - principal:,.2f}")
        
        # Quick Stats
        if st.session_state.chatbot.user_profile:
            profile = st.session_state.chatbot.user_profile
            monthly_income = profile.income / 12
            monthly_surplus = monthly_income - profile.monthly_expenses
            
            st.subheader("📈 Quick Stats")
            
            col_i, col_ii = st.columns(2)
            with col_i:
                st.metric("Monthly Income", f"${monthly_income:,.0f}")
                st.metric("Monthly Expenses", f"${profile.monthly_expenses:,.0f}")
            
            with col_ii:
                st.metric("Current Savings", f"${profile.savings_amount:,.0f}")
                surplus_delta = "↗️" if monthly_surplus > 0 else "↘️"
                st.metric("Monthly Surplus", f"${monthly_surplus:,.0f}", delta=surplus_delta)
            
            # Savings rate
            if monthly_income > 0:
                savings_rate = (monthly_surplus / monthly_income) * 100
                rate_color = "green" if savings_rate >= 20 else "orange" if savings_rate >= 10 else "red"
                st.markdown(f"**Savings Rate:** <span style='color: {rate_color};'>{savings_rate:.1f}%</span>", 
                           unsafe_allow_html=True)
    
    # Bottom Section - Visualizations
    st.header("📊 Financial Visualizations")
    
    viz_col1, viz_col2 = st.columns(2)
    
    with viz_col1:
        if st.session_state.expenses:
            fig_expenses = create_expense_visualization(st.session_state.expenses)
            st.plotly_chart(fig_expenses, use_container_width=True)
    
    with viz_col2:
        if (st.session_state.chatbot.user_profile and 
            st.session_state.chatbot.user_profile.income > st.session_state.chatbot.user_profile.monthly_expenses * 12):
            
            profile = st.session_state.chatbot.user_profile
            monthly_surplus = (profile.income / 12) - profile.monthly_expenses
            
            if monthly_surplus > 0:
                fig_projection = create_savings_projection_chart(profile, monthly_surplus)
                st.plotly_chart(fig_projection, use_container_width=True)

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p>🔒 Your financial data is handled securely and never stored permanently.</p>
        <p>💡 FINOVA provides educational guidance only. Consult with a licensed financial advisor for personalized investment advice.</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()