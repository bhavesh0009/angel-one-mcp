#!/usr/bin/env python3
"""
Angel One MCP Server

This server exposes Angel One trading and market data APIs as MCP tools.
It handles authentication automatically and provides comprehensive trading functionality.
"""

import os
import asyncio
import logging
from typing import Any, Dict, List, Optional
from contextlib import asynccontextmanager

import pyotp
from SmartApi.smartConnect import SmartConnect
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP("angel-one-trading")

# Global SmartConnect instance
smart_api: Optional[SmartConnect] = None
is_authenticated = False

# Configuration from environment
API_KEY = os.getenv("ANGEL_ONE_API_KEY")
CLIENT_CODE = os.getenv("ANGEL_ONE_CLIENT_CODE") 
PASSWORD = os.getenv("ANGEL_ONE_PASSWORD")
TOTP_SECRET = os.getenv("ANGEL_ONE_TOTP_SECRET")

# Safety configurations
MAX_ORDER_QUANTITY = int(os.getenv("MAX_ORDER_QUANTITY", "10000"))
DRY_RUN_MODE = os.getenv("DRY_RUN_MODE", "false").lower() == "true"

def validate_environment():
    """Validate required environment variables"""
    required_vars = ["ANGEL_ONE_API_KEY", "ANGEL_ONE_CLIENT_CODE", "ANGEL_ONE_PASSWORD", "ANGEL_ONE_TOTP_SECRET"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {missing_vars}")

async def ensure_authenticated():
    """Ensure the API client is authenticated"""
    global smart_api, is_authenticated
    
    if smart_api is None:
        validate_environment()
        smart_api = SmartConnect(api_key=API_KEY)
    
    if not is_authenticated:
        try:
            # Generate TOTP
            totp = pyotp.TOTP(TOTP_SECRET).now()
            
            # Generate session
            data = smart_api.generateSession(CLIENT_CODE, PASSWORD, totp)
            
            if data['status']:
                auth_token = data['data']['jwtToken']
                refresh_token = data['data']['refreshToken']
                feed_token = smart_api.getfeedToken()
                
                # Remove 'Bearer ' prefix if present - Angel One API expects raw JWT
                if auth_token.startswith('Bearer '):
                    auth_token = auth_token[7:]
                    
                smart_api.setAccessToken(auth_token)
                smart_api.setRefreshToken(refresh_token)
                
                is_authenticated = True
                logger.info("Successfully authenticated with Angel One API")
                return True
            else:
                error_msg = f"Authentication failed: {data.get('message', 'Unknown error')}"
                logger.error(error_msg)
                raise Exception(error_msg)
                
        except Exception as e:
            error_msg = f"Authentication error: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
    
    return True

def handle_api_error(func_name: str, error: Exception) -> str:
    """Handle and format API errors with context"""
    error_context = {
        "function": func_name,
        "error_type": type(error).__name__,
        "error_message": str(error),
        "suggestion": "Check parameters and try again. Verify market hours for trading operations."
    }
    
    logger.error(f"API Error in {func_name}: {error}")
    return f"Error in {func_name}: {error_context}"

# =============================================================================
# AUTHENTICATION & PROFILE TOOLS
# =============================================================================

@mcp.tool()
async def get_profile() -> str:
    """Get user profile information"""
    try:
        await ensure_authenticated()
        profile = smart_api.getProfile(smart_api.getRefreshToken())
        return f"User Profile: {profile}"
    except Exception as e:
        return handle_api_error("get_profile", e)

# =============================================================================
# PORTFOLIO TOOLS  
# =============================================================================

@mcp.tool()
async def get_holdings() -> str:
    """Get user's stock holdings"""
    try:
        await ensure_authenticated()
        holdings = smart_api.holding()
        return f"Holdings: {holdings}"
    except Exception as e:
        return handle_api_error("get_holdings", e)

@mcp.tool()
async def get_all_holdings() -> str:
    """Get all holdings including family accounts"""
    try:
        await ensure_authenticated()
        all_holdings = smart_api.allholding()
        return f"All Holdings: {all_holdings}"
    except Exception as e:
        return handle_api_error("get_all_holdings", e)

@mcp.tool()
async def get_positions() -> str:
    """Get user's open positions"""
    try:
        await ensure_authenticated()
        positions = smart_api.position()
        return f"Positions: {positions}"
    except Exception as e:
        return handle_api_error("get_positions", e)

@mcp.tool()
async def get_rms_limit() -> str:
    """Get Risk Management System limits"""
    try:
        await ensure_authenticated()
        rms_limit = smart_api.rmsLimit()
        return f"RMS Limits: {rms_limit}"
    except Exception as e:
        return handle_api_error("get_rms_limit", e)

# =============================================================================
# TRADING TOOLS
# =============================================================================

@mcp.tool()
async def place_order(
    variety: str,
    tradingsymbol: str, 
    symboltoken: str,
    transactiontype: str,
    exchange: str,
    ordertype: str,
    producttype: str,
    duration: str,
    price: str,
    quantity: str,
    squareoff: str = "0",
    stoploss: str = "0"
) -> str:
    """Place a trading order
    
    Args:
        variety: Order variety (NORMAL, STOPLOSS, AMO, ROBO)
        tradingsymbol: Trading symbol (e.g., SBIN-EQ)
        symboltoken: Symbol token for the instrument
        transactiontype: BUY or SELL
        exchange: Exchange (NSE, BSE, NFO, MCX)
        ordertype: Order type (MARKET, LIMIT, STOPLOSS_LIMIT, STOPLOSS_MARKET)
        producttype: Product type (DELIVERY, CARRYFORWARD, MARGIN, INTRADAY, BO)
        duration: Order duration (DAY, IOC)
        price: Order price
        quantity: Order quantity
        squareoff: Square off price (for bracket orders)
        stoploss: Stop loss price (for bracket orders)
    """
    try:
        await ensure_authenticated()
        
        # Safety check
        if int(quantity) > MAX_ORDER_QUANTITY:
            return f"Error: Order quantity {quantity} exceeds maximum allowed {MAX_ORDER_QUANTITY}"
        
        order_params = {
            "variety": variety,
            "tradingsymbol": tradingsymbol,
            "symboltoken": symboltoken,
            "transactiontype": transactiontype,
            "exchange": exchange,
            "ordertype": ordertype,
            "producttype": producttype,
            "duration": duration,
            "price": price,
            "quantity": quantity,
            "squareoff": squareoff,
            "stoploss": stoploss
        }
        
        if DRY_RUN_MODE:
            return f"DRY RUN - Order would be placed with params: {order_params}"
        
        order_id = smart_api.placeOrder(order_params)
        return f"Order placed successfully. Order ID: {order_id}"
        
    except Exception as e:
        return handle_api_error("place_order", e)

@mcp.tool()
async def modify_order(
    orderid: str,
    variety: str,
    tradingsymbol: str,
    symboltoken: str, 
    transactiontype: str,
    exchange: str,
    ordertype: str,
    producttype: str,
    duration: str,
    price: str,
    quantity: str
) -> str:
    """Modify an existing order
    
    Args:
        orderid: Order ID to modify
        variety: Order variety
        tradingsymbol: Trading symbol
        symboltoken: Symbol token
        transactiontype: BUY or SELL
        exchange: Exchange
        ordertype: Order type
        producttype: Product type
        duration: Order duration
        price: New price
        quantity: New quantity
    """
    try:
        await ensure_authenticated()
        
        modify_params = {
            "orderid": orderid,
            "variety": variety,
            "tradingsymbol": tradingsymbol,
            "symboltoken": symboltoken,
            "transactiontype": transactiontype,
            "exchange": exchange,
            "ordertype": ordertype,
            "producttype": producttype,
            "duration": duration,
            "price": price,
            "quantity": quantity
        }
        
        if DRY_RUN_MODE:
            return f"DRY RUN - Order would be modified with params: {modify_params}"
        
        response = smart_api.modifyOrder(modify_params)
        return f"Order modified successfully: {response}"
        
    except Exception as e:
        return handle_api_error("modify_order", e)

@mcp.tool()
async def cancel_order(order_id: str, variety: str) -> str:
    """Cancel an existing order
    
    Args:
        order_id: Order ID to cancel
        variety: Order variety (NORMAL, STOPLOSS, AMO, ROBO)
    """
    try:
        await ensure_authenticated()
        
        if DRY_RUN_MODE:
            return f"DRY RUN - Order {order_id} would be cancelled"
        
        response = smart_api.cancelOrder(order_id=order_id, variety=variety)
        return f"Order cancelled successfully: {response}"
        
    except Exception as e:
        return handle_api_error("cancel_order", e)

@mcp.tool()
async def get_order_book() -> str:
    """Get the order book with all orders"""
    try:
        await ensure_authenticated()
        order_book = smart_api.orderBook()
        return f"Order Book: {order_book}"
    except Exception as e:
        return handle_api_error("get_order_book", e)

@mcp.tool()
async def get_trade_book() -> str:
    """Get the trade book with all executed trades"""
    try:
        await ensure_authenticated()
        trade_book = smart_api.tradeBook()
        return f"Trade Book: {trade_book}"
    except Exception as e:
        return handle_api_error("get_trade_book", e)

# =============================================================================
# MARKET DATA TOOLS
# =============================================================================

@mcp.tool()
async def get_ltp_data(exchange: str, tradingsymbol: str, symboltoken: str) -> str:
    """Get Last Traded Price (LTP) data
    
    Args:
        exchange: Exchange (NSE, BSE, NFO, MCX)
        tradingsymbol: Trading symbol (e.g., SBIN-EQ)
        symboltoken: Symbol token
    """
    try:
        await ensure_authenticated()
        ltp_data = smart_api.ltpData(exchange, tradingsymbol, symboltoken)
        return f"LTP Data: {ltp_data}"
    except Exception as e:
        return handle_api_error("get_ltp_data", e)

@mcp.tool()
async def get_candle_data(
    exchange: str,
    symboltoken: str,
    interval: str,
    fromdate: str,
    todate: str
) -> str:
    """Get historical candlestick data
    
    Args:
        exchange: Exchange (NSE, BSE, NFO, MCX)
        symboltoken: Symbol token
        interval: Time interval (ONE_MINUTE, FIVE_MINUTE, FIFTEEN_MINUTE, THIRTY_MINUTE, SIXTY_MINUTE, ONE_DAY)
        fromdate: Start date (YYYY-MM-DD HH:MM format)
        todate: End date (YYYY-MM-DD HH:MM format)
    """
    try:
        await ensure_authenticated()
        
        historic_params = {
            "exchange": exchange,
            "symboltoken": symboltoken,
            "interval": interval,
            "fromdate": fromdate,
            "todate": todate
        }
        
        candle_data = smart_api.getCandleData(historic_params)
        return f"Candle Data: {candle_data}"
        
    except Exception as e:
        return handle_api_error("get_candle_data", e)

@mcp.tool()
async def search_scrip(exchange: str, searchscrip: str) -> str:
    """Search for securities to get symbol details
    
    Args:
        exchange: Exchange to search in (NSE, BSE, NFO, MCX)
        searchscrip: Search term (e.g., RELIANCE, SBIN)
    """
    try:
        await ensure_authenticated()
        response = smart_api.searchScrip(exchange=exchange, searchscrip=searchscrip)
        return f"Search Results: {response}"
    except Exception as e:
        return handle_api_error("search_scrip", e)

# =============================================================================
# GTT (Good Till Triggered) TOOLS
# =============================================================================

@mcp.tool()
async def create_gtt_rule(
    tradingsymbol: str,
    symboltoken: str,
    exchange: str,
    producttype: str,
    transactiontype: str,
    price: float,
    qty: int,
    disclosedqty: int,
    triggerprice: float,
    timeperiod: int
) -> str:
    """Create a GTT (Good Till Triggered) rule
    
    Args:
        tradingsymbol: Trading symbol
        symboltoken: Symbol token
        exchange: Exchange
        producttype: Product type
        transactiontype: BUY or SELL
        price: Order price
        qty: Quantity
        disclosedqty: Disclosed quantity
        triggerprice: Trigger price
        timeperiod: Time period in days
    """
    try:
        await ensure_authenticated()
        
        gtt_params = {
            "tradingsymbol": tradingsymbol,
            "symboltoken": symboltoken,
            "exchange": exchange,
            "producttype": producttype,
            "transactiontype": transactiontype,
            "price": price,
            "qty": qty,
            "disclosedqty": disclosedqty,
            "triggerprice": triggerprice,
            "timeperiod": timeperiod
        }
        
        if DRY_RUN_MODE:
            return f"DRY RUN - GTT rule would be created with params: {gtt_params}"
        
        rule_id = smart_api.gttCreateRule(gtt_params)
        return f"GTT rule created successfully. Rule ID: {rule_id}"
        
    except Exception as e:
        return handle_api_error("create_gtt_rule", e)

@mcp.tool()
async def get_gtt_list(status: List[str], page: int = 1, count: int = 10) -> str:
    """Get list of GTT rules
    
    Args:
        status: List of status filters (e.g., ["FORALL"])
        page: Page number
        count: Number of records per page
    """
    try:
        await ensure_authenticated()
        gtt_list = smart_api.gttLists(status=status, page=page, count=count)
        return f"GTT Rule List: {gtt_list}"
    except Exception as e:
        return handle_api_error("get_gtt_list", e)

# =============================================================================
# MARKET ANALYSIS TOOLS
# =============================================================================

@mcp.tool()
async def get_option_greek(name: str, expirydate: str) -> str:
    """Get option Greeks for an underlying
    
    Args:
        name: Underlying name (e.g., NIFTY)
        expirydate: Expiry date (e.g., 25JAN2024)
    """
    try:
        await ensure_authenticated()
        
        greek_params = {
            "name": name,
            "expirydate": expirydate
        }
        
        greeks = smart_api.optionGreek(greek_params)
        return f"Option Greeks: {greeks}"
        
    except Exception as e:
        return handle_api_error("get_option_greek", e)

@mcp.tool()
async def get_gainers_losers(datatype: str, expirytype: str = "NEAR") -> str:
    """Get top gainers/losers
    
    Args:
        datatype: Data type (PercGainers, PercLosers, PercOIGainers)
        expirytype: Expiry type (NEAR, NEXT, FAR)
    """
    try:
        await ensure_authenticated()
        
        gl_params = {
            "datatype": datatype,
            "expirytype": expirytype
        }
        
        gainers_losers = smart_api.gainersLosers(gl_params)
        return f"Gainers/Losers: {gainers_losers}"
        
    except Exception as e:
        return handle_api_error("get_gainers_losers", e)

@mcp.tool()
async def get_put_call_ratio() -> str:
    """Get Put-Call Ratio for the market"""
    try:
        await ensure_authenticated()
        pcr = smart_api.putCallRatio()
        return f"Put-Call Ratio: {pcr}"
    except Exception as e:
        return handle_api_error("get_put_call_ratio", e)

# =============================================================================
# UTILITY TOOLS
# =============================================================================

@mcp.tool()
async def convert_position(
    exchange: str,
    oldproducttype: str,
    newproducttype: str,
    tradingsymbol: str,
    transactiontype: str,
    quantity: int,
    type: str
) -> str:
    """Convert position from one product type to another
    
    Args:
        exchange: Exchange
        oldproducttype: Current product type
        newproducttype: Target product type
        tradingsymbol: Trading symbol
        transactiontype: BUY or SELL
        quantity: Quantity to convert
        type: Conversion type (DAY)
    """
    try:
        await ensure_authenticated()
        
        position_params = {
            "exchange": exchange,
            "oldproducttype": oldproducttype,
            "newproducttype": newproducttype,
            "tradingsymbol": tradingsymbol,
            "transactiontype": transactiontype,
            "quantity": quantity,
            "type": type
        }
        
        if DRY_RUN_MODE:
            return f"DRY RUN - Position would be converted with params: {position_params}"
        
        response = smart_api.convertPosition(position_params)
        return f"Position conversion response: {response}"
        
    except Exception as e:
        return handle_api_error("convert_position", e)

@mcp.tool()
async def estimate_charges(orders: List[Dict[str, Any]]) -> str:
    """Estimate brokerage and charges for trades
    
    Args:
        orders: List of order dictionaries with keys: product_type, transaction_type, quantity, price, exchange, symbol_name, token
    """
    try:
        await ensure_authenticated()
        
        charge_params = {"orders": orders}
        charges = smart_api.estimateCharges(charge_params)
        return f"Estimated charges: {charges}"
        
    except Exception as e:
        return handle_api_error("estimate_charges", e)

# =============================================================================
# SERVER STARTUP
# =============================================================================

if __name__ == "__main__":
    # Validate environment variables on startup
    try:
        validate_environment()
        logger.info("Angel One MCP Server starting...")
        logger.info(f"DRY RUN MODE: {DRY_RUN_MODE}")
        logger.info(f"MAX ORDER QUANTITY: {MAX_ORDER_QUANTITY}")
        
        # Run the FastMCP server
        mcp.run(transport='stdio')
        
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        exit(1) 