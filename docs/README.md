# Angel One MCP Trading Assistant

A Model Context Protocol (MCP) server and client that provides natural language interface to Angel One trading APIs. This allows you to interact with your Angel One trading account using conversational commands through Claude AI.

## 🚀 Features

- **Natural Language Trading**: Ask questions in plain English about your portfolio, market data, and trading operations
- **Comprehensive API Coverage**: Access all major Angel One APIs including:
  - Portfolio management (holdings, positions, profile)
  - Order management (place, modify, cancel orders)
  - Market data (live prices, historical data, search)
  - Market analysis (option Greeks, gainers/losers, put-call ratio)
  - GTT (Good Till Triggered) orders
  - Utility functions (position conversion, charge estimation)
- **Safety Features**: Built-in safety limits and dry-run mode for testing
- **Error Handling**: Detailed error context for troubleshooting

## 📁 Project Structure

```
AngelOne/
├── src/                                    # Source code
│   ├── angel_one_mcp_server.py            # MCP Server implementation
│   └── angel_one_mcp_client.py            # MCP Client with Gemini AI
├── config/                                 # Configuration files
│   ├── config.yaml                        # Settings (safe to commit)
│   └── config_template.txt                # Environment variable template
├── scripts/                               # Scripts and utilities
│   ├── quick_start.sh                     # Automated setup script
│   └── test_setup.py                      # Setup verification script
├── docs/                                  # Documentation
│   ├── README.md                          # This file
│   ├── smartapi_python_documentation.md  # Angel One API docs
│   └── MCP_*.md                           # MCP implementation guides
├── logs/                                  # Application logs
├── .env                                   # Your secrets (never commit!)
├── .env.example                           # Environment template
└── requirements.txt                       # Python dependencies
```

## 📋 Prerequisites

1. **Angel One Account**: You need an active Angel One trading account
2. **Angel One API Access**: Register for API access at [Angel One Developer Portal](https://smartapi.angelone.in/)
3. **Google Gemini API Key**: Get your API key from [Google AI Studio](https://aistudio.google.com/app/apikey)
4. **Python 3.10+**: Make sure you have Python 3.10 or higher installed

## 🛠️ Installation

### 1. Clone or Setup Project

```bash
# Create project directory
mkdir angel-one-mcp
cd angel-one-mcp

# Copy the project structure with organized folders:
# src/ - Contains angel_one_mcp_server.py and angel_one_mcp_client.py
# config/ - Contains config.yaml and config_template.txt
# scripts/ - Contains quick_start.sh and test_setup.py
# docs/ - Contains documentation files
# requirements.txt - In root directory
```

### 2. Quick Setup (Recommended)

```bash
# Run the automated setup script
bash scripts/quick_start.sh
```

This will:

- Set up a virtual environment
- Install all dependencies
- Create configuration files from templates
- Run setup tests

### 3. Manual Setup

If you prefer manual setup:

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install required packages
pip install -r requirements.txt

# Create environment file from example template
cp .env.example .env
```

### 4. Configuration

The project uses two configuration files:

#### **Environment Template (.env.example)**

This file shows the structure of required environment variables with example values:

- **Safe to commit to git** - contains no real secrets
- **Template reference** - shows expected format for all variables
- **Always in sync** - when new variables are added, this file is updated
- **Usage**: Copy `.env.example` to `.env` and replace example values with real credentials

```bash
# Copy the template to create your .env file
cp .env.example .env
```

#### **Secrets (.env file)**

Contains API keys and sensitive information - **NEVER commit to git**:

```bash
# Angel One API Credentials  
ANGEL_ONE_API_KEY=your_api_key_here
ANGEL_ONE_CLIENT_CODE=your_client_code_here
ANGEL_ONE_PASSWORD=your_4_digit_pin_here
ANGEL_ONE_TOTP_SECRET=your_totp_secret_here

# Google Gemini API Configuration
GEMINI_API_KEY=your_gemini_api_key_here
```

#### **Settings (config/config.yaml file)**

Contains non-secret configurations - **safe to commit to git**:

```yaml
# AI Model Configuration
ai:
  provider: "gemini"
  model: "gemini-1.5-flash"  # or gemini-1.5-pro
  max_tokens: 1000
  temperature: 0.1

# Trading Safety Configuration  
trading:
  max_order_quantity: 10000
  dry_run_mode: true  # Set to false for live trading
  default_product_type: "INTRADAY"
  default_exchange: "NSE"
```

### 5. Get Your API Credentials

#### **Angel One Credentials**

1. **API Key**: Register at [Angel One Developer Portal](https://smartapi.angelone.in/)
2. **Client Code**: Your Angel One login ID  
3. **Password**: Your 4-digit PIN (not full password)
4. **TOTP Secret**: Set up 2FA and get the secret key from your authenticator app

#### **Google Gemini API Key**

1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Create a new API key
3. Copy the key and add to your `.env` file

## 🎯 Usage

### Start the Trading Assistant

```bash
# Activate virtual environment first
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows
source venv/Scripts/activate # bash

# Start the assistant
python src/angel_one_mcp_client.py src/angel_one_mcp_server.py
```

### Example Conversations

```
💬 Your Query: Show me my current holdings

💬 Your Query: What is the current price of Reliance?

💬 Your Query: Search for HDFC Bank stock details

💬 Your Query: Show me today's top gainers

💬 Your Query: Place a buy order for 10 shares of SBIN at market price

💬 Your Query: What are my open positions?

💬 Your Query: Get NIFTY option chain for this month
```

### Command Categories

#### 🔍 Market Data

- "What is the current price of [STOCK_NAME]?"
- "Show me historical data for RELIANCE for last week"
- "Search for HDFC Bank stock details"
- "Get candlestick data for NIFTY"

#### 📊 Portfolio & Account

- "Show me my current holdings"
- "What are my open positions?"
- "Show my account profile"
- "What are my RMS limits?"

#### 📈 Market Analysis

- "Show me today's top gainers"
- "What are the biggest losers today?"
- "Get NIFTY option Greeks for current month"
- "What is the current put-call ratio?"

#### 📋 Order Management

- "Show my order book"
- "Show my trade book"
- "Place a buy order for 10 shares of RELIANCE at market price"
- "Cancel order with ID [ORDER_ID]"

#### ⚡ Advanced Features

- "Show my GTT rules"
- "Create a GTT rule for SBIN"
- "Convert my INTRADAY position to DELIVERY"

## ⚙️ Configuration Options

### AI Model Settings (config/config.yaml)

```yaml
ai:
  provider: "gemini"
  model: "gemini-1.5-flash"  # Fast and cost-effective
  # model: "gemini-1.5-pro"   # More capable, higher cost
  max_tokens: 1000
  temperature: 0.1
```

### Safety Settings (config/config.yaml)

```yaml
trading:
  max_order_quantity: 10000    # Maximum shares per order
  dry_run_mode: true          # true = simulate, false = real orders
  default_product_type: "INTRADAY"
  default_exchange: "NSE"
```

### Testing vs Live Trading

- **Testing Mode**: Set `dry_run_mode: true` in config/config.yaml - orders will be simulated
- **Live Trading**: Set `dry_run_mode: false` in config/config.yaml - orders will be placed for real

⚠️ **Always test with `dry_run_mode: true` first!**

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Gemini AI     │◄──►│  MCP Client      │◄──►│  MCP Server     │
│                 │    │                  │    │                 │
│ Natural Language│    │ src/angel_one_   │    │ src/angel_one_  │
│ Processing      │    │ mcp_client.py    │    │ mcp_server.py   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                         │
                                                         ▼
                                               ┌─────────────────┐
                                               │  Angel One      │
                                               │  Smart API      │
                                               │                 │
                                               │ Trading Account │
                                               └─────────────────┘
```

1. **User Query**: You ask a question in natural language
2. **Gemini Processing**: Gemini AI decides which tools to use
3. **MCP Communication**: Client calls appropriate server tools
4. **API Execution**: Server executes Angel One API calls
5. **Response**: Results are formatted and returned to you

## 🔧 Available Tools

The MCP server exposes these Angel One API functions as tools:

### Portfolio Management

- `get_profile()` - User profile information
- `get_holdings()` - Current stock holdings
- `get_positions()` - Open positions
- `get_rms_limit()` - Risk management limits

### Trading Operations

- `place_order()` - Place buy/sell orders
- `modify_order()` - Modify existing orders
- `cancel_order()` - Cancel orders
- `get_order_book()` - View order history
- `get_trade_book()` - View trade history

### Market Data

- `get_ltp_data()` - Last traded price
- `get_candle_data()` - Historical OHLC data
- `search_scrip()` - Search for stocks/instruments

### Market Analysis

- `get_option_greek()` - Option Greeks
- `get_gainers_losers()` - Top movers
- `get_put_call_ratio()` - PCR data

### GTT Management

- `create_gtt_rule()` - Create GTT orders
- `get_gtt_list()` - List GTT rules

### Utilities

- `convert_position()` - Convert position types
- `estimate_charges()` - Calculate brokerage

## 🛡️ Security & Safety

### Built-in Safety Features

- **Quantity Limits**: Maximum order quantity restrictions
- **Dry Run Mode**: Test without real transactions
- **Authentication Management**: Secure credential handling
- **Error Context**: Detailed error reporting for troubleshooting

### Best Practices

1. **Start with Dry Run**: Always test with `DRY_RUN_MODE=true`
2. **Secure Credentials**: Never commit `.env` file to version control
3. **Review Orders**: Carefully review order parameters before execution
4. **Market Hours**: Be aware of market timing for live data
5. **Risk Management**: Set appropriate quantity limits

## 🐛 Troubleshooting

### Common Issues

#### Authentication Errors

```
Error: Authentication failed
```

**Solution**:

- Verify your Angel One credentials in `.env`
- Check if your API key is active
- Ensure TOTP secret is correct

#### Tool Execution Errors

```
Tool execution failed: [specific error]
```

**Solution**:

- Check if market is open for trading operations
- Verify stock symbols and parameters
- Review the detailed error context provided

#### Connection Issues

```
Failed to connect to server
```

**Solution**:

- Ensure all dependencies are installed
- Check Python path and file locations
- Verify MCP server starts without errors

### Debugging Tips

1. **Check Logs**: Review console output for detailed error messages
2. **Verify Credentials**: Test Angel One API credentials separately
3. **Market Hours**: Ensure market is open for live data
4. **Parameter Format**: Check date formats and required parameters

## 📚 API Documentation

- [Angel One Smart API Documentation](https://smartapi.angelone.in/docs)
- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)
- [Anthropic Claude API](https://docs.anthropic.com/)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Test your changes with `DRY_RUN_MODE=true`
4. Submit a pull request

## ⚠️ Disclaimer

- This software is for educational and personal use
- Trading involves financial risk - use at your own discretion
- Always verify trading operations before execution
- Not responsible for any financial losses
- Test thoroughly before live trading

## 📄 License

This project is for educational purposes. Please review Angel One's API terms of service and ensure compliance with their usage policies.

---

**Happy Trading! 🚀📈**

For support or questions, please check the troubleshooting section or refer to the Angel One API documentation.
