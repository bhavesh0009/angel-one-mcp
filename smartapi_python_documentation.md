# SmartAPI Python Client Documentation

This document provides a comprehensive guide to using the SmartAPI Python client for trading and accessing market data from Angel One.

## 1. Introduction

The SmartAPI Python library provides a set of REST-like APIs and a WebSocket interface to build your own trading and investment platform. You can manage your portfolio, place orders, and access real-time market data.

## 2. Installation

To get started, you need to install the library and its dependencies.

```bash
pip install smartapi-python
```

You might also need to install other packages mentioned in the original `README.md`:

```bash
pip install pyotp logzero websocket-client pycryptodome
```

## 3. Authentication

Authentication is the first step to interact with the SmartAPI. You need an `api_key` which you can get from the Angel One developer portal.

### 3.1. Initializing the Client

First, import and initialize the `SmartConnect` class.

```python
from SmartApi.smartConnect import SmartConnect

api_key = "YOUR_API_KEY"
smart_api = SmartConnect(api_key=api_key)
```

### 3.2. Generating a Session

To start a session, you need your client code (username), password, and a Time-based One-Time Password (TOTP).

```python
import pyotp
from logzero import logger

client_code = "YOUR_CLIENT_CODE"
password = "YOUR_PASSWORD"
token = "YOUR_TOTP_SECRET"  # The secret key for your TOTP
totp = pyotp.TOTP(token).now()

data = smart_api.generateSession(client_code, password, totp)

if data['status']:
    logger.info("Session generated successfully.")
    auth_token = data['data']['jwtToken']
    refresh_token = data['data']['refreshToken']
    feed_token = smart_api.getfeedToken()
    smart_api.setAccessToken(auth_token)
    smart_api.setRefreshToken(refresh_token)
else:
    logger.error(f"Session generation failed: {data['message']}")

```

**Function:** `generateSession(clientCode, password, totp)`

* **Description:** Authenticates the user and generates a session.
* **Arguments:**
  * `clientCode` (str): Your client ID.
  * `password` (str): Your account password.
  * `totp` (str): A valid Time-based One-Time Password.
* **Returns:** A dictionary containing session data, including `jwtToken` and `refreshToken`.

### 3.3. Renewing the Access Token

The access token has a limited validity. You can renew it using the refresh token.

```python
try:
    response = smart_api.generateToken(refresh_token)
    new_access_token = response['data']['jwtToken']
    smart_api.setAccessToken(new_access_token)
    logger.info("Access token renewed successfully.")
except Exception as e:
    logger.error(f"Failed to renew access token: {e}")
```

**Function:** `generateToken(refresh_token)`

* **Description:** Generates a new set of tokens using the refresh token.
* **Arguments:**
  * `refresh_token` (str): The refresh token obtained from `generateSession`.
* **Returns:** A dictionary with a new `jwtToken` and `refreshToken`.

### 3.4. Terminating a Session

To log out, you can terminate the session.

```python
try:
    logout_response = smart_api.terminateSession(client_code)
    logger.info("Logout successful.")
except Exception as e:
    logger.error(f"Logout failed: {e}")
```

**Function:** `terminateSession(clientCode)`

* **Description:** Logs the user out and invalidates the session.
* **Arguments:**
  * `clientCode` (str): Your client ID.
* **Returns:** A confirmation message.

## 4. User and Portfolio

You can fetch user profile details, holdings, and positions.

### 4.1. Get User Profile

```python
try:
    profile = smart_api.getProfile(refresh_token)
    logger.info(f"User Profile: {profile}")
except Exception as e:
    logger.error(f"Failed to get user profile: {e}")
```

**Function:** `getProfile(refreshToken)`

* **Description:** Fetches the user's profile information.
* **Arguments:**
  * `refreshToken` (str): The refresh token.
* **Returns:** A dictionary with user profile details.

### 4.2. Get Holdings

```python
try:
    holdings = smart_api.holding()
    logger.info(f"Holdings: {holdings}")
except Exception as e:
    logger.error(f"Failed to get holdings: {e}")
```

**Function:** `holding()`

* **Description:** Retrieves the user's holdings.
* **Returns:** A dictionary containing the list of holdings.

### 4.3. Get All Holdings

```python
try:
    all_holdings = smart_api.allholding()
    logger.info(f"All Holdings: {all_holdings}")
except Exception as e:
    logger.error(f"Failed to get all holdings: {e}")
```

**Function:** `allholding()`

* **Description:** Retrieves all holdings for the user, including for all family accounts.
* **Returns:** A dictionary containing all holdings.

### 4.4. Get Positions

```python
try:
    positions = smart_api.position()
    logger.info(f"Positions: {positions}")
except Exception as e:
    logger.error(f"Failed to get positions: {e}")
```

**Function:** `position()`

* **Description:** Fetches the user's open positions.
* **Returns:** A dictionary with the list of open positions.

## 5. Order Management

The API allows you to place, modify, and cancel orders, as well as fetch the order book and trade book.

### 5.1. Place an Order

The `placeOrder` function is used to place an order. The `orderparams` dictionary should contain the details of the order.

**Common Parameters:**

* `variety`: "NORMAL" (regular order), "STOPLOSS", "AMO" (After Market Order), "ROBO" (Bracket Order).
* `transactiontype`: "BUY" or "SELL".
* `ordertype`: "MARKET", "LIMIT", "STOPLOSS_LIMIT", "STOPLOSS_MARKET".
* `producttype`: "DELIVERY", "CARRYFORWARD", "MARGIN", "INTRADAY", "BO" (Bracket Order).
* `duration`: "DAY" (valid for the day), "IOC" (Immediate or Cancel).
* `exchange`: "NSE", "BSE", "NFO", "MCX".

#### Example: Equity Order

```python
order_params = {
    "variety": "NORMAL",
    "tradingsymbol": "SBIN-EQ",
    "symboltoken": "3045",
    "transactiontype": "BUY",
    "exchange": "NSE",
    "ordertype": "LIMIT",
    "producttype": "INTRADAY",
    "duration": "DAY",
    "price": "500",
    "squareoff": "0",
    "stoploss": "0",
    "quantity": "1"
}

try:
    order_id = smart_api.placeOrder(order_params)
    logger.info(f"Order placed. Order ID: {order_id}")
except Exception as e:
    logger.error(f"Order placement failed: {e}")
```

#### Example: Options Order

To trade options, you need to construct the `tradingsymbol` correctly. The format is `SYMBOLDDMMMYYSTRIKECE/PE`.

* `SYMBOL`: The underlying symbol (e.g., "NIFTY").
* `DD`: Day of expiry.
* `MMM`: Month of expiry in characters (e.g., "JAN").
* `YY`: Year of expiry.
* `STRIKE`: The strike price.
* `CE` for Call Option, `PE` for Put Option.

```python
# Example for NIFTY 18000 CE expiring on 25th Jan 2024
order_params_options = {
    "variety": "NORMAL",
    "tradingsymbol": "NIFTY25JAN2418000CE",
    "symboltoken": "YOUR_SYMBOL_TOKEN", # You need to find the correct token for the instrument
    "transactiontype": "BUY",
    "exchange": "NFO",
    "ordertype": "LIMIT",
    "producttype": "CARRYFORWARD",
    "duration": "DAY",
    "price": "150",
    "quantity": "50" # Lot size
}

try:
    order_id = smart_api.placeOrder(order_params_options)
    logger.info(f"Options order placed. Order ID: {order_id}")
except Exception as e:
    logger.error(f"Options order placement failed: {e}")
```

#### Example: Futures Order

For futures, the `tradingsymbol` format is `SYMBOLMONYYFUT`.

* `SYMBOL`: The underlying symbol (e.g., "NIFTY").
* `MON`: Month of expiry in characters (e.g., "JAN").
* `YY`: Year of expiry.

```python
# Example for NIFTY Futures expiring in January 2024
order_params_futures = {
    "variety": "NORMAL",
    "tradingsymbol": "NIFTYJAN24FUT",
    "symboltoken": "YOUR_SYMBOL_TOKEN", # You need to find the correct token for the instrument
    "transactiontype": "BUY",
    "exchange": "NFO",
    "ordertype": "LIMIT",
    "producttype": "CARRYFORWARD",
    "duration": "DAY",
    "price": "18100",
    "quantity": "50" # Lot size
}

try:
    order_id = smart_api.placeOrder(order_params_futures)
    logger.info(f"Futures order placed. Order ID: {order_id}")
except Exception as e:
    logger.error(f"Futures order placement failed: {e}")
```

### 5.2. Modify an Order

```python
modify_params = {
    "orderid": "YOUR_ORDER_ID",
    "variety": "NORMAL",
    "tradingsymbol": "SBIN-EQ",
    "symboltoken": "3045",
    "transactiontype": "BUY",
    "exchange": "NSE",
    "ordertype": "LIMIT",
    "producttype": "INTRADAY",
    "duration": "DAY",
    "price": "501",
    "quantity": "1"
}

try:
    response = smart_api.modifyOrder(modify_params)
    logger.info(f"Order modified: {response}")
except Exception as e:
    logger.error(f"Order modification failed: {e}")
```

**Function:** `modifyOrder(orderparams)`

* **Description:** Modifies a pending order.
* **Arguments:**
  * `orderparams` (dict): A dictionary with the modified order details, including the `orderid`.
* **Returns:** A confirmation message.

### 5.3. Cancel an Order

```python
try:
    response = smart_api.cancelOrder(order_id="YOUR_ORDER_ID", variety="NORMAL")
    logger.info(f"Order cancelled: {response}")
except Exception as e:
    logger.error(f"Order cancellation failed: {e}")
```

**Function:** `cancelOrder(order_id, variety)`

* **Description:** Cancels a pending order.
* **Arguments:**
  * `order_id` (str): The ID of the order to be cancelled.
  * `variety` (str): The order variety (e.g., "NORMAL").
* **Returns:** A confirmation message.

### 5.4. Get Order Book

```python
try:
    order_book = smart_api.orderBook()
    logger.info(f"Order Book: {order_book}")
except Exception as e:
    logger.error(f"Failed to get order book: {e}")
```

**Function:** `orderBook()`

* **Description:** Retrieves the user's order book.
* **Returns:** A dictionary containing the list of orders.

### 5.5. Get Trade Book

```python
try:
    trade_book = smart_api.tradeBook()
    logger.info(f"Trade Book: {trade_book}")
except Exception as e:
    logger.error(f"Failed to get trade book: {e}")
```

**Function:** `tradeBook()`

* **Description:** Retrieves the user's trade book for the current day.
* **Returns:** A dictionary containing the list of trades.

## 6. GTT (Good Till Triggered) Orders

Manage GTT orders with the following methods.

### 6.1. Create a GTT Rule

```python
gtt_params = {
    "tradingsymbol": "SBIN-EQ",
    "symboltoken": "3045",
    "exchange": "NSE",
    "producttype": "MARGIN",
    "transactiontype": "BUY",
    "price": 1000.00,
    "qty": 10,
    "disclosedqty": 10,
    "triggerprice": 1100.00,
    "timeperiod": 365
}

try:
    rule_id = smart_api.gttCreateRule(gtt_params)
    logger.info(f"GTT rule created. Rule ID: {rule_id}")
except Exception as e:
    logger.error(f"GTT rule creation failed: {e}")
```

### 6.2. Modify a GTT Rule

```python
modify_gtt_params = {
    "id": "YOUR_RULE_ID",
    "symboltoken": "3045",
    "exchange": "NSE",
    "price": 1050.00,
    "qty": 10,
    "triggerprice": 1150.00,
    "timeperiod": 365
}

try:
    response = smart_api.gttModifyRule(modify_gtt_params)
    logger.info(f"GTT rule modified: {response}")
except Exception as e:
    logger.error(f"GTT rule modification failed: {e}")
```

### 6.3. Cancel a GTT Rule

```python
cancel_gtt_params = {
    "id": "YOUR_RULE_ID",
    "symboltoken": "3045",
    "exchange": "NSE"
}

try:
    response = smart_api.gttCancelRule(cancel_gtt_params)
    logger.info(f"GTT rule cancelled: {response}")
except Exception as e:
    logger.error(f"GTT rule cancellation failed: {e}")
```

### 6.4. Get GTT Rule Details

```python
try:
    details = smart_api.gttDetails("YOUR_RULE_ID")
    logger.info(f"GTT rule details: {details}")
except Exception as e:
    logger.error(f"Failed to get GTT rule details: {e}")
```

### 6.5. Get GTT Rule List

```python
try:
    gtt_list = smart_api.gttLists(status=["FORALL"], page=1, count=10)
    logger.info(f"GTT rule list: {gtt_list}")
except Exception as e:
    logger.error(f"Failed to get GTT rule list: {e}")
```

## 7. Market Data

Access historical data and live market quotes.

### 7.1. Get Candlestick Data

**Interval values:**

* "ONE_MINUTE"
* "THREE_MINUTE"
* "FIVE_MINUTE"
* "TEN_MINUTE"
* "FIFTEEN_MINUTE"
* "THIRTY_MINUTE"
* "SIXTY_MINUTE"
* "ONE_DAY"

```python
historic_params = {
    "exchange": "NSE",
    "symboltoken": "3045",
    "interval": "ONE_MINUTE",
    "fromdate": "2023-01-01 09:15",
    "todate": "2023-01-01 09:30"
}

try:
    candle_data = smart_api.getCandleData(historic_params)
    logger.info(f"Candle Data: {candle_data}")
except Exception as e:
    logger.error(f"Failed to get candle data: {e}")
```

### 7.2. Get LTP (Last Traded Price) Data

```python
try:
    ltp_data = smart_api.ltpData("NSE", "SBIN-EQ", "3045")
    logger.info(f"LTP Data: {ltp_data}")
except Exception as e:
    logger.error(f"Failed to get LTP data: {e}")
```

## 8. WebSockets

For real-time market data and order updates, the SmartAPI provides a WebSocket interface.

### 8.1. Market Data WebSocket

Use `SmartWebSocketV2` for live market data.

```python
from SmartApi.smartWebSocketV2 import SmartWebSocketV2

# Assuming you have AUTH_TOKEN, API_KEY, CLIENT_CODE, FEED_TOKEN
# sws = SmartWebSocketV2(AUTH_TOKEN, API_KEY, CLIENT_CODE, FEED_TOKEN)

# def on_data(wsapp, message):
#     logger.info(f"Ticks: {message}")

# ... (rest of the WebSocket implementation from README)
```

### 8.2. Order Update WebSocket

Use `SmartWebSocketOrderUpdate` to receive real-time order status updates.

```python
from SmartApi.smartWebSocketOrderUpdate import SmartWebSocketOrderUpdate

# Assuming you have AUTH_TOKEN, API_KEY, CLIENT_CODE, FEED_TOKEN
# client = SmartWebSocketOrderUpdate(AUTH_TOKEN, API_KEY, CLIENT_CODE, FEED_TOKEN)
# client.connect()
```

## 9. Other Functions

This section covers other utility functions for managing your account and analyzing the market.

### 9.1. Get RMS Limit

Fetches the Risk Management System (RMS) limits for your account.

```python
try:
    rms_limit = smart_api.rmsLimit()
    logger.info(f"RMS Limits: {rms_limit}")
except Exception as e:
    logger.error(f"Failed to get RMS limits: {e}")
```

**Function:** `rmsLimit()`

* **Description:** Retrieves the current RMS limits on your account.
* **Returns:** A dictionary containing limit details.

### 9.2. Convert Position

Converts an open position from one product type to another (e.g., INTRADAY to DELIVERY).

```python
position_params = {
    "exchange": "NSE",
    "oldproducttype": "INTRADAY",
    "newproducttype": "DELIVERY",
    "tradingsymbol": "SBIN-EQ",
    "transactiontype": "BUY",
    "quantity": 1,
    "type": "DAY"
}

try:
    response = smart_api.convertPosition(position_params)
    logger.info(f"Position conversion response: {response}")
except Exception as e:
    logger.error(f"Position conversion failed: {e}")
```

**Function:** `convertPosition(positionParams)`

* **Description:** Converts the product type of an open position.
* **Arguments:**
  * `positionParams` (dict): A dictionary with conversion details.

### 9.3. Search for a Scrip

Searches for a security to get its symbol token.

```python
try:
    search_params = {
        "exchange": "NSE",
        "searchscrip": "SBIN"
    }
    response = smart_api.searchScrip(exchange=search_params["exchange"], searchscrip=search_params["searchscrip"])
    logger.info(f"Scrip search response: {response}")
except Exception as e:
    logger.error(f"Scrip search failed: {e}")
```

**Function:** `searchScrip(exchange, searchscrip)`

* **Description:** Finds scrips matching a search query.
* **Arguments:**
  * `exchange` (str): The exchange to search in (e.g., "NSE").
  * `searchscrip` (str): The search term (e.g., "RELIANCE").

### 9.4. Estimate Charges

Calculates the estimated brokerage and other charges for a list of trades.

```python
charge_params = {
    "orders": [
        {
            "product_type": "DELIVERY",
            "transaction_type": "BUY",
            "quantity": "10",
            "price": "800",
            "exchange": "NSE",
            "symbol_name": "RELIANCE-EQ",
            "token": "2885"
        }
    ]
}

try:
    charges = smart_api.estimateCharges(charge_params)
    logger.info(f"Estimated charges: {charges}")
except Exception as e:
    logger.error(f"Failed to estimate charges: {e}")
```

**Function:** `estimateCharges(params)`

* **Description:** Provides an estimate of charges for one or more trades.
* **Arguments:**
  * `params` (dict): A dictionary containing a list of order objects.

### 9.5. EDIS (Electronic Delivery Instruction Slip)

Functions related to the EDIS workflow for authorizing the debit of shares from your Demat account.

#### 9.5.1. Generate TPIN

```python
try:
    # These parameters are specific to the user's DP and BO accounts
    tpin_params = {
        "dpId": "YOUR_DP_ID",
        "boid": "YOUR_BO_ID",
        "pan": "YOUR_PAN",
        "ReqId": "YOUR_REQUEST_ID"
    }
    response = smart_api.generateTPIN(tpin_params)
    logger.info(f"TPIN generation response: {response}")
except Exception as e:
    logger.error(f"TPIN generation failed: {e}")
```

#### 9.5.2. Verify DIS

```python
try:
    dis_params = {
        "isin": "INE002A01018", # ISIN of the stock
        "quantity": "1"
    }
    response = smart_api.verifyDis(dis_params)
    logger.info(f"DIS verification response: {response}")
except Exception as e:
    logger.error(f"DIS verification failed: {e}")
```

#### 9.5.3. Get Transaction Status

```python
try:
    status_params = {
        "ReqId": "YOUR_REQUEST_ID"
    }
    response = smart_api.getTranStatus(status_params)
    logger.info(f"Transaction status: {response}")
except Exception as e:
    logger.error(f"Failed to get transaction status: {e}")
```

### 9.6. Market Analysis Tools

#### 9.6.1. Option Greeks

Retrieves the option chain and corresponding Greeks for a given underlying.

```python
try:
    greek_params = {
        "name": "NIFTY",
        "expirydate": "25JAN2024"
    }
    greeks = smart_api.optionGreek(greek_params)
    logger.info(f"Option Greeks: {greeks}")
except Exception as e:
    logger.error(f"Failed to get Option Greeks: {e}")
```

#### 9.6.2. Top Gainers and Losers

Fetches the top market gainers or losers.

```python
try:
    gl_params = {
        "datatype": "PercOIGainers", # e.g., "PercGainers", "PercLosers", "PercOIGainers"
        "expirytype": "NEAR"
    }
    gainers_losers = smart_api.gainersLosers(gl_params)
    logger.info(f"Gainers/Losers: {gainers_losers}")
except Exception as e:
    logger.error(f"Failed to get gainers/losers: {e}")
```

#### 9.6.3. Put-Call Ratio (PCR)

Retrieves the Put-Call Ratio for the overall market.

```python
try:
    pcr = smart_api.putCallRatio()
    logger.info(f"Put-Call Ratio: {pcr}")
except Exception as e:
    logger.error(f"Failed to get Put-Call Ratio: {e}")
```

#### 9.6.4. OI Buildup

Provides data on Open Interest buildup.

```python
try:
    oi_params = {
        "expirytype": "NEAR",
        "datatype": "Long Built Up" # e.g., "Long Built Up", "Short Built Up"
    }
    oi_buildup = smart_api.oIBuildup(oi_params)
    logger.info(f"OI Buildup: {oi_buildup}")
except Exception as e:
    logger.error(f"Failed to get OI Buildup: {e}")
```
