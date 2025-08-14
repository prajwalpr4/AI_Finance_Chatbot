import streamlit as st
import json
import datetime
from typing import Dict, List, Optional
import requests
import pandas as pd
from dataclasses import dataclass
import re
import streamlit as st
import os
import requests
from dotenv import load_dotenv
load_dotenv()

HF_TOKEN = os.getenv("HUGGINGFACE_API_KEY")
if not HF_TOKEN:
    raise ValueError("❌ Hugging Face API key not found. Please check your .env file.")

# =========================
# Helper Function for Hugging Face API
# =========================
def query_huggingface(model, inputs):
    """Send a query to the Hugging Face Inference API."""
    url = f"https://api-inference.huggingface.co/models{ibm-granite/granite-speech-3.3-8b}"
    headers = {"Authorization": f"Bearer {HF_TOKEN.strip()}"}
    payload = {"inputs": inputs}

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code != 200:
        return {"error": f"{response.status_code} - {response.text}"}
    return response.json()

# =========================
# Streamlit App UI
# =========================
st.title("💬 AI Financial Chatbot")

# Model Selection
model = st.selectbox(
    "Choose a model:",
    [
        "microsoft/DialoGPT-medium",
        "cardiffnlp/twitter-roberta-base-sentiment-latest"
    ]
)

# User Input
user_input = st.text_input("You:", "")

# Send Button
if st.button("Send") and user_input.strip():
    with st.spinner("Thinking..."):
        result = query_huggingface(model, user_input)
    st.write("**Bot:**", result)


HUGGINGFACE_API_URL = "https://api-inference.huggingface.co/models"
HEADERS = {"Authorization": "Bearer "}

# Configuration
  # Replace with your actual API key

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
    user_type: str  # student, professional, retiree

class FinancialChatbot:
    def __init__(self):
        self.conversation_history = []
        self.user_profile = None
        
    def call_huggingface_api(self, model_name: str, payload: dict) -> dict:
        """Call HuggingFace API for various NLP tasks"""
        try:
            api_url = f"{HUGGINGFACE_API_URL}/{model_name}"
            response = requests.post(api_url, headers=HEADERS, json=payload)
            if response.status_code == 200:
                return response.json()
            else:
                st.error(f"API Error: {response.status_code}")
                return {}
        except Exception as e:
            st.error(f"Error calling HuggingFace API: {str(e)}")
            return {}
    
    def analyze_sentiment(self, text: str) -> str:
        """Analyze sentiment of user input"""
        payload = {"inputs": text}
        result = self.call_huggingface_api("cardiffnlp/twitter-roberta-base-sentiment-latest", payload)
        
        if result and isinstance(result, list) and len(result) > 0:
            sentiment_data = result[0]
            if isinstance(sentiment_data, list) and len(sentiment_data) > 0:
                top_sentiment = max(sentiment_data, key=lambda x: x.get('score', 0))
                return top_sentiment.get('label', 'NEUTRAL')
        return 'NEUTRAL'
    
    def classify_intent(self, text: str) -> str:
        """Classify user intent from input text"""
        # Define financial intents
        intent_keywords = {
            'budgeting': ['budget', 'expense', 'spend', 'cost', 'money management'],
            'investment': ['invest', 'stock', 'bond', 'portfolio', 'return', 'market'],
            'savings': ['save', 'saving', 'emergency fund', 'deposit'],
            'debt': ['debt', 'loan', 'credit', 'payment', 'owe'],
            'tax': ['tax', 'deduction', 'filing', 'refund'],
            'general': ['advice', 'help', 'guidance', 'financial planning']
        }
        
        text_lower = text.lower()
        for intent, keywords in intent_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                return intent
        return 'general'
    
    def generate_financial_advice(self, user_input: str, intent: str, sentiment: str) -> str:
        """Generate personalized financial advice using AI"""
        if not self.user_profile:
            return "I'd be happy to help! First, let me get to know you better. Please complete your profile setup."
        
        # Construct context for AI model
        context = f"""
        User Profile:
        - Name: {self.user_profile.name}
        - Age: {self.user_profile.age}
        - Income: ${self.user_profile.income:,.2f}
        - Occupation: {self.user_profile.occupation}
        - User Type: {self.user_profile.user_type}
        - Risk Tolerance: {self.user_profile.risk_tolerance}
        - Current Savings: ${self.user_profile.savings_amount:,.2f}
        - Monthly Expenses: ${self.user_profile.monthly_expenses:,.2f}
        - Goals: {', '.join(self.user_profile.financial_goals)}
        
        User Question: {user_input}
        Intent: {intent}
        Sentiment: {sentiment}
        
        Provide personalized financial advice considering the user's profile and current situation.
        """
        
        # Use HuggingFace text generation model
        payload = {
            "inputs": context,
            "parameters": {
                "max_length": 500,
                "temperature": 0.7,
                "do_sample": True
            }
        }
        
        result = self.call_huggingface_api("microsoft/DialoGPT-medium", payload)
        
        if result:
            # If API returns text, use it; otherwise provide rule-based advice
            return self.get_rule_based_advice(intent, user_input)
        else:
            return self.get_rule_based_advice(intent, user_input)
    
    def get_rule_based_advice(self, intent: str, user_input: str) -> str:
        """Fallback rule-based advice generation"""
        if not self.user_profile:
            return "Please complete your profile first for personalized advice."
        
        advice_templates = {
            'budgeting': self.get_budgeting_advice(),
            'investment': self.get_investment_advice(),
            'savings': self.get_savings_advice(),
            'debt': self.get_debt_advice(),
            'tax': self.get_tax_advice(),
            'general': self.get_general_advice()
        }
        
        return advice_templates.get(intent, self.get_general_advice())
    
    def get_budgeting_advice(self) -> str:
        monthly_surplus = self.user_profile.income / 12 - self.user_profile.monthly_expenses
        
        if monthly_surplus > 0:
            advice = f"Great news! You have a monthly surplus of ${monthly_surplus:,.2f}. "
            if self.user_profile.user_type == 'student':
                advice += "As a student, focus on the 50/30/20 rule: 50% needs, 30% wants, 20% savings."
            elif self.user_profile.user_type == 'professional':
                advice += "Consider increasing your savings rate to 25-30% and explore investment options."
            else:
                advice += "Focus on building your emergency fund and consider conservative investments."
        else:
            deficit = abs(monthly_surplus)
            advice = f"You're spending ${deficit:,.2f} more than you earn monthly. "
            advice += "Let's work on reducing expenses: track all spending for a month, cut unnecessary subscriptions, and look for ways to increase income."
        
        return advice
    
    def get_investment_advice(self) -> str:
        risk_advice = {
            'conservative': "Consider low-risk options like bonds, CDs, or index funds with stable returns.",
            'moderate': "A balanced portfolio of 60% stocks and 40% bonds could work well for you.",
            'aggressive': "You might benefit from growth stocks and emerging market funds, but maintain some diversification."
        }
        
        base_advice = risk_advice.get(self.user_profile.risk_tolerance.lower(), 
                                    "Consider a diversified portfolio based on your risk tolerance.")
        
        if self.user_profile.age < 30:
            base_advice += " At your age, you have time for long-term growth investments."
        elif self.user_profile.age > 50:
            base_advice += " Consider gradually shifting to more conservative investments as you approach retirement."
        
        return base_advice
    
    def get_savings_advice(self) -> str:
        emergency_fund_target = self.user_profile.monthly_expenses * 6
        current_emergency_ratio = self.user_profile.savings_amount / emergency_fund_target if emergency_fund_target > 0 else 0
        
        if current_emergency_ratio < 1:
            needed = emergency_fund_target - self.user_profile.savings_amount
            advice = f"Your emergency fund needs ${needed:,.2f} more to cover 6 months of expenses. "
            advice += "Try to save 10-20% of your monthly income until you reach this goal."
        else:
            advice = "Excellent! Your emergency fund is well-established. "
            advice += "Consider exploring high-yield savings accounts or short-term investments for additional growth."
        
        return advice
    
    def get_debt_advice(self) -> str:
        return ("Focus on high-interest debt first (credit cards). Consider the debt avalanche method: "
                "pay minimums on all debts, then put extra money toward the highest interest rate debt. "
                "If motivation is an issue, try the debt snowball: pay off smallest balances first.")
    
    def get_tax_advice(self) -> str:
        if self.user_profile.user_type == 'student':
            return ("Look into education tax credits, student loan interest deductions, and "
                   "consider a part-time job for work-study programs.")
        else:
            return ("Maximize your 401(k) contributions, consider IRA contributions, and keep track of "
                   "deductible expenses. Consider consulting a tax professional for complex situations.")
    
    def get_general_advice(self) -> str:
        return (f"Based on your profile as a {self.user_profile.user_type}, I recommend focusing on: "
               f"1) Building an emergency fund, 2) Managing debt effectively, "
               f"3) Investing according to your {self.user_profile.risk_tolerance} risk tolerance, "
               f"and 4) Regular budget reviews.")
    
    def analyze_spending_habits(self, expenses_data: Dict) -> str:
        """Analyze spending patterns and provide insights"""
        if not expenses_data:
            return "Please provide your expense data for analysis."
        
        total_expenses = sum(expenses_data.values())
        insights = ["## Spending Analysis\n"]
        
        # Find highest expense category
        highest_category = max(expenses_data, key=expenses_data.get)
        highest_amount = expenses_data[highest_category]
        highest_percentage = (highest_amount / total_expenses) * 100
        
        insights.append(f"Your highest expense category is **{highest_category}** at ${highest_amount:,.2f} ({highest_percentage:.1f}% of total)")
        
        # Recommendations based on spending patterns
        if highest_percentage > 50:
            insights.append(f"⚠️ You're spending over 50% on {highest_category}. Consider ways to reduce this expense.")
        
        # Identify optimization opportunities
        for category, amount in expenses_data.items():
            percentage = (amount / total_expenses) * 100
            if category.lower() in ['entertainment', 'dining', 'shopping'] and percentage > 15:
                insights.append(f"💡 Consider reducing {category} spending (currently {percentage:.1f}% of total)")
        
        return "\n\n".join(insights)
    
    def generate_budget_summary(self, expenses_data: Dict) -> str:
        """Generate automated budget summary"""
        if not self.user_profile or not expenses_data:
            return "Need user profile and expense data for budget summary."
        
        total_expenses = sum(expenses_data.values())
        monthly_income = self.user_profile.income / 12
        
        summary = f"""
        ## Budget Summary for {self.user_profile.name}
        
        **Monthly Income:** ${monthly_income:,.2f}
        **Total Expenses:** ${total_expenses:,.2f}
        **Net Income:** ${monthly_income - total_expenses:,.2f}
        
        **Expense Breakdown:**
        """
        
        for category, amount in sorted(expenses_data.items(), key=lambda x: x[1], reverse=True):
            percentage = (amount / total_expenses) * 100
            summary += f"\n- {category}: ${amount:,.2f} ({percentage:.1f}%)"
        
        # Add recommendations
        if monthly_income > total_expenses:
            surplus = monthly_income - total_expenses
            summary += f"\n\n✅ You have a surplus of ${surplus:,.2f}. Consider increasing savings or investments."
        else:
            deficit = total_expenses - monthly_income
            summary += f"\n\n⚠️ You have a deficit of ${deficit:,.2f}. Review expenses for reduction opportunities."
        
        return summary

def main():
    st.set_page_config(page_title="FINOVA - AI Financial Advisor", page_icon="💰", layout="wide")
    
    # Initialize chatbot
    if 'chatbot' not in st.session_state:
        st.session_state.chatbot = FinancialChatbot()
    
    st.title("🤖 FINOVA - AI Financial Advisor")
    st.markdown("Your intelligent financial companion powered by advanced AI")
    
    # Sidebar for user profile
    with st.sidebar:
        st.header("👤 User Profile")
        
        if st.session_state.chatbot.user_profile is None:
            st.markdown("**Complete your profile for personalized advice**")
            
            name = st.text_input("Name")
            age = st.number_input("Age", min_value=18, max_value=100, value=25)
            income = st.number_input("Annual Income ($)", min_value=0, value=50000)
            occupation = st.selectbox("Occupation", ["Student", "Software Engineer", "Teacher", "Doctor", "Business Owner", "Other"])
            user_type = st.selectbox("User Type", ["student", "professional", "retiree"])
            risk_tolerance = st.selectbox("Risk Tolerance", ["conservative", "moderate", "aggressive"])
            savings = st.number_input("Current Savings ($)", min_value=0, value=5000)
            monthly_expenses = st.number_input("Monthly Expenses ($)", min_value=0, value=3000)
            
            goals = st.multiselect("Financial Goals", 
                                 ["Emergency Fund", "Buy a House", "Retirement", "Pay off Debt", "Investment Growth", "Education"])
            
            if st.button("Save Profile"):
                if name:
                    st.session_state.chatbot.user_profile = UserProfile(
                        name=name, age=age, income=income, occupation=occupation,
                        financial_goals=goals, risk_tolerance=risk_tolerance,
                        savings_amount=savings, monthly_expenses=monthly_expenses,
                        user_type=user_type
                    )
                    st.success("Profile saved successfully!")
                    st.rerun()
                else:
                    st.error("Please enter your name")
        else:
            profile = st.session_state.chatbot.user_profile
            st.write(f"**Name:** {profile.name}")
            st.write(f"**Age:** {profile.age}")
            st.write(f"**Income:** ${profile.income:,.2f}")
            st.write(f"**Type:** {profile.user_type}")
            
            if st.button("Edit Profile"):
                st.session_state.chatbot.user_profile = None
                st.rerun()
    
    # Main chat interface
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("💬 Chat with AI Advisor")
        
        # Chat history
        if 'messages' not in st.session_state:
            st.session_state.messages = []
        
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # User input
        if prompt := st.chat_input("Ask me anything about your finances..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Generate response
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    sentiment = st.session_state.chatbot.analyze_sentiment(prompt)
                    intent = st.session_state.chatbot.classify_intent(prompt)
                    response = st.session_state.chatbot.generate_financial_advice(prompt, intent, sentiment)
                    st.markdown(response)
            
            st.session_state.messages.append({"role": "assistant", "content": response})
    
    with col2:
        st.header("📊 Financial Tools")
        
        # Expense tracker
        with st.expander("💳 Expense Tracker"):
            st.subheader("Add Your Monthly Expenses")
            
            if 'expenses' not in st.session_state:
                st.session_state.expenses = {}
            
            category = st.selectbox("Category", ["Housing", "Food", "Transportation", "Entertainment", "Healthcare", "Shopping", "Other"])
            amount = st.number_input("Amount ($)", min_value=0.0, step=10.0)
            
            if st.button("Add Expense"):
                if category in st.session_state.expenses:
                    st.session_state.expenses[category] += amount
                else:
                    st.session_state.expenses[category] = amount
                st.success(f"Added ${amount:.2f} to {category}")
            
            if st.session_state.expenses:
                st.write("**Current Expenses:**")
                for cat, amt in st.session_state.expenses.items():
                    st.write(f"- {cat}: ${amt:.2f}")
                
                if st.button("Analyze Spending"):
                    analysis = st.session_state.chatbot.analyze_spending_habits(st.session_state.expenses)
                    st.markdown(analysis)
                
                if st.button("Generate Budget Summary"):
                    summary = st.session_state.chatbot.generate_budget_summary(st.session_state.expenses)
                    st.markdown(summary)
        
        # Quick stats
        if st.session_state.chatbot.user_profile:
            with st.expander("📈 Quick Stats"):
                profile = st.session_state.chatbot.user_profile
                monthly_income = profile.income / 12
                
                st.metric("Monthly Income", f"${monthly_income:,.2f}")
                st.metric("Current Savings", f"${profile.savings_amount:,.2f}")
                st.metric("Monthly Expenses", f"${profile.monthly_expenses:,.2f}")
                
                if monthly_income > 0:
                    savings_rate = ((monthly_income - profile.monthly_expenses) / monthly_income) * 100
                    st.metric("Savings Rate", f"{savings_rate:.1f}%")

if __name__ == "__main__":
    main()