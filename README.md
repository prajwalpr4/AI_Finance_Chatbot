# AI-Powered Financial Chatbot

A comprehensive AI-powered financial advisor built with Streamlit and HuggingFace models, providing personalized financial guidance, expense tracking, and investment advice.

## 🚀 Features

- **Personalized AI Financial Advice**: Get tailored recommendations based on your profile
- **Real-time Expense Tracking**: Track and categorize your expenses with smart analysis
- **Financial Health Scoring**: Comprehensive scoring system with actionable feedback
- **Interactive Visualizations**: Charts and graphs for better financial insights
- **Multiple AI Models**: Sentiment analysis, intent classification, and text generation
- **Secure Data Handling**: Privacy-focused design with no permanent data storage
- **Responsive Design**: Works on desktop and mobile devices

## 🛠️ Technology Stack

- **Frontend**: Streamlit with custom CSS styling
- **AI/ML**: HuggingFace Transformers API
- **Data Processing**: Pandas, NumPy
- **Visualizations**: Plotly
- **Backend**: Python with modular architecture

## 📋 Prerequisites

- Python 3.8 or higher
- HuggingFace API key (free account)
- VS Code or Windsurf IDE (recommended)

## 🔧 Installation

### 1. Clone or Download the Project

Create a new folder for your project:

```bash
mkdir ai-financial-chatbot
cd ai-financial-chatbot
```

### 2. Create the Project Files

Create the following files in your project directory:

- `app.py` (Main application - use the first artifact)
- `enhanced_app.py` (Enhanced version - use the enhanced artifact)
- `config.py` (Configuration file)
- `utils.py` (Utility functions)
- `requirements.txt` (Dependencies)

### 3. Set up Python Environment

```bash
# Create virtual environment
python -m venv financial_chatbot_env

# Activate virtual environment
# On Windows:
financial_chatbot_env\Scripts\activate
# On macOS/Linux:
source financial_chatbot_env/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 4. Get HuggingFace API Key

1. Go to [HuggingFace](https://huggingface.co/)
2. Create a free account
3. Go to Settings → Access Tokens
4. Create a new token with "Read" permissions
5. Copy the token

### 5. Configure API Key

**Option A: Environment Variable (Recommended)**
```bash
# On Windows:
set HUGGINGFACE_API_KEY=your_api_key_here

# On macOS/Linux:
export HUGGINGFACE_API_KEY=your_api_key_here
```

**Option B: Direct Configuration**
Edit the `config.py` file and replace `YOUR_API_KEY_HERE` with your actual API key.

### 6. Run the Application

```bash
# Run basic version
streamlit run app.py

# OR run enhanced version (recommended)
streamlit run enhanced_app.py
```

The application will open in your browser at `http://localhost:8501`

## 🎯 Usage Guide

### 1. Complete Your Profile
- Fill out the user profile in the sidebar
- Provide accurate financial information for better advice
- Select appropriate risk tolerance and user type

### 2. Chat with AI Advisor
- Ask questions about budgeting, investing, savings, debt management
- Get personalized advice based on your profile
- Receive contextual tips and recommendations

### 3. Track Expenses
- Add your monthly expenses by category
- View spending analysis and recommendations
- Generate comprehensive financial reports

### 4. Use Financial Tools
- Calculate compound interest, loan payments
- View financial health score
- Analyze spending patterns with visualizations

## 📊 Available AI Models

The chatbot uses these HuggingFace models:

- **Sentiment Analysis**: `cardiffnlp/twitter-roberta-base-sentiment-latest`
- **Text Generation**: `microsoft/DialoGPT-medium`
- **Summarization**: `facebook/bart-large-cnn`
- **Question Answering**: `deepset/roberta-base-squad2`

## 🔒 Security Features

- No permanent data storage
- Input sanitization and validation
- Session-based user data
- Privacy-focused design
- Secure API key handling

## 🎨 Customization

### Modify Financial Rules
Edit `config.py` to adjust:
- Emergency fund target months
- Recommended savings rates
- Expense category thresholds
- User type configurations

### Add New Expense Categories
Update `EXPENSE_CATEGORIES` in `config.py`:
```python
EXPENSE_CATEGORIES = [
    'Housing', 'Food', 'Transportation', 'Healthcare',
    'Your_Custom_Category', 'Another_Category'
]
```

### Customize AI Responses
Modify the advice templates in the chatbot class methods:
- `_get_budgeting_advice()`
- `_get_investment_advice()`
- `_get_savings_advice()`
- etc.

## 🚀 Advanced Features

### Financial Health Scoring
The system calculates a comprehensive score based on:
- Emergency fund coverage (25 points)
- Savings rate (25 points)
- Budget management (25 points)
- Goal diversification (25 points)

### Expense Analysis
Automatic categorization and analysis including:
- Spending pattern identification
- Optimization recommendations
- Category-based insights
- Monthly trend analysis

### Visualization Types
- Interactive pie charts for expense breakdown
- Savings growth projections
- Financial health dashboards
- Goal progress tracking

## 🛠️ Development Setup (VS Code)

### Recommended Extensions
- Python
- Pylance
- Streamlit (for syntax highlighting)
- GitLens (for version control)

### VS Code Configuration
Create `.vscode/settings.json`:
```json
{
    "python.defaultInterpreterPath": "./financial_chatbot_env/Scripts/python.exe",
    "python.terminal.activateEnvironment": true,
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true
}
```

### Debug Configuration
Create `.vscode/launch.json`:
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Streamlit App",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/financial_chatbot_env/Scripts/streamlit",
            "args": ["run", "enhanced_app.py"],
            "console": "integratedTerminal"
        }
    ]
}
```

## 📈 Future Enhancements

Potential improvements you can implement:

1. **Database Integration**
   - PostgreSQL or MongoDB for data persistence
   - User account management
   - Historical data tracking

2. **Advanced AI Features**
   - Custom fine-tuned models
   - Multiple language support
   - Voice interface integration

3. **Financial API Integration**
   - Real-time stock prices
   - Bank account connectivity
   - Cryptocurrency tracking

4. **Advanced Analytics**
   - Machine learning predictions
   - Trend analysis
   - Risk assessment models

5. **Mobile App**
   - React Native or Flutter app
   - Push notifications
   - Offline functionality

## 🐛 Troubleshooting

### Common Issues

**1. API Key Not Working**
```bash
# Check if environment variable is set
echo $HUGGINGFACE_API_KEY  # macOS/Linux
echo %HUGGINGFACE_API_KEY%  # Windows
```

**2. Module Import Errors**
```bash
# Ensure all files are in the same directory
# Check virtual environment is activated
which python  # Should point to your venv
```

**3. Streamlit Port Issues**
```bash
# Run on different port
streamlit run enhanced_app.py --server.port 8502
```

**4. Model Loading Errors**
- HuggingFace models may take time to load initially
- Check internet connection
- Verify API key permissions

### Performance Optimization

**1. Caching**
```python
@st.cache_data
def expensive_calculation():
    # Add caching to slow functions
    pass
```

**2. Session State Management**
```python
# Clear unused session data periodically
if len(st.session_state.messages) > 50:
    st.session_state.messages = st.session_state.messages[-30:]
```

## 📄 License

This project is open source and available under the MIT License.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📞 Support

For questions or issues:
1. Check the troubleshooting section
2. Review the code comments
3. Create an issue with detailed description

## 🌟 Acknowledgments

- HuggingFace for providing free AI model APIs
- Streamlit for the excellent web framework
- Plotly for interactive visualizations
- The open-source community for inspiration and tools