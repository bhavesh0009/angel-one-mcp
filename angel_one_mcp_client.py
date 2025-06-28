#!/usr/bin/env python3
"""
Angel One MCP Client

This client connects to the Angel One MCP server and provides a natural language
interface for trading and market data operations.
"""

import asyncio
import sys
import os
import yaml
from typing import Optional, Dict, Any
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables and configuration
load_dotenv()

def load_config() -> Dict[str, Any]:
    """Load configuration from config.yaml"""
    try:
        with open('config.yaml', 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print("⚠️  config.yaml not found, using default configuration")
        return {
            'ai': {
                'provider': 'gemini',
                'model': 'gemini-1.5-flash',
                'max_tokens': 1000,
                'temperature': 0.1
            },
            'trading': {
                'max_order_quantity': 10000,
                'dry_run_mode': True
            }
        }

class AngelOneMCPClient:
    def __init__(self):
        """Initialize the MCP client"""
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        
        # Load configuration
        self.config = load_config()
        
        # Initialize Gemini client
        gemini_key = os.getenv("GEMINI_API_KEY")
        if not gemini_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=gemini_key)
        self.model = genai.GenerativeModel(self.config['ai']['model'])
        
        print(f"🤖 Angel One MCP Client initialized with {self.config['ai']['model']}!")
        print(f"⚙️  Dry run mode: {self.config['trading']['dry_run_mode']}")

    async def connect_to_server(self, server_script_path: str):
        """Connect to the Angel One MCP server
        
        Args:
            server_script_path: Path to the Angel One MCP server script
        """
        try:
            if not server_script_path.endswith('.py'):
                raise ValueError("Server script must be a .py file")

            # Set up server parameters
            server_params = StdioServerParameters(
                command="python",
                args=[server_script_path],
                env=None
            )

            # Connect to server
            stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
            self.stdio, self.write = stdio_transport
            self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))

            # Initialize session
            await self.session.initialize()

            # List available tools
            response = await self.session.list_tools()
            tools = response.tools
            
            print(f"✅ Connected to Angel One MCP Server!")
            print(f"📊 {len(tools)} trading tools available")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to connect to server: {e}")
            return False

    async def process_query(self, query: str) -> str:
        """Process a natural language query using Claude and available tools
        
        Args:
            query: Natural language query about trading or market data
            
        Returns:
            Formatted response from Claude
        """
        try:
            # Build conversation messages
            messages = [
                {
                    "role": "user", 
                    "content": query
                }
            ]

            # Get available tools from server
            response = await self.session.list_tools()
            available_tools = [{
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.inputSchema
            } for tool in response.tools]

            # Prepare system prompt
            system_prompt = """You are an expert trading assistant for Angel One broker APIs. 

Key guidelines:
1. Always prioritize user safety - explain risks for trading operations
2. For market data queries, use appropriate tools to get real-time information
3. For trading operations, clearly explain what will happen before execution
4. When using tools, provide context about the parameters you're using
5. Format numerical data clearly (prices, quantities, percentages) - NEVER use placeholder values
6. If you need symbol tokens, always search for them first using search_scrip
7. For order placement, ensure all required parameters are provided
8. Explain any trading terminology used
9. CRITICAL: When calculating totals, profits, or any numerical summaries, use the EXACT values from the API response. Do NOT use rounded numbers, placeholders, or approximations.
10. Always sum up individual holdings to get accurate portfolio totals

CRITICAL WORKFLOW FOR STOCK PRICE QUERIES:
- When user asks for current price of a stock (e.g., "current price of TCS", "what is Reliance trading at"):
  1. FIRST call search_scrip to find available symbols
  2. AUTOMATICALLY identify the equity symbol (ends with "-EQ", e.g., "TCS-EQ", "RELIANCE-EQ") from search results
  3. IMMEDIATELY call get_ltp_data using the "-EQ" tradingsymbol and its symboltoken to get current price
  4. NEVER stop after search_scrip - ALWAYS follow through with get_ltp_data for price queries
  5. If multiple "-EQ" symbols exist, use the first one found
  6. This is a MANDATORY two-step process for any price inquiry

Available Angel One tools:
- Portfolio: get_holdings, get_positions, get_profile, get_rms_limit
- Trading: place_order, modify_order, cancel_order, get_order_book, get_trade_book
- Market Data: get_ltp_data, get_candle_data, search_scrip
- Analysis: get_option_greek, get_gainers_losers, get_put_call_ratio
- GTT: create_gtt_rule, get_gtt_list
- Utility: convert_position, estimate_charges

Respond directly to the user's question. If you need to use tools, I will call them for you."""

            # Convert tools to Gemini format
            gemini_tools = []
            for tool in available_tools:
                # Clean the input_schema for Gemini compatibility
                input_schema = tool["input_schema"]
                
                def clean_schema_recursive(schema):
                    """Recursively clean schema to remove MCP-specific fields"""
                    if not isinstance(schema, dict):
                        return schema
                    
                    cleaned = {}
                    for k, v in schema.items():
                        # Skip MCP-specific fields that Gemini doesn't expect
                        if k in ["title", "$schema", "additionalProperties", "default"]:
                            continue
                        
                        # Recursively clean nested objects
                        if isinstance(v, dict):
                            cleaned[k] = clean_schema_recursive(v)
                        elif isinstance(v, list):
                            cleaned[k] = [clean_schema_recursive(item) if isinstance(item, dict) else item for item in v]
                        else:
                            cleaned[k] = v
                    
                    return cleaned
                
                if input_schema and isinstance(input_schema, dict):
                    cleaned_schema = clean_schema_recursive(input_schema)
                    
                    # Ensure we have the required structure for Gemini
                    if "type" not in cleaned_schema:
                        cleaned_schema["type"] = "object"
                    if "properties" not in cleaned_schema:
                        cleaned_schema["properties"] = {}
                else:
                    cleaned_schema = {"type": "object", "properties": {}}
                
                gemini_tool = {
                    "function_declarations": [{
                        "name": tool["name"],
                        "description": tool["description"],
                        "parameters": cleaned_schema
                    }]
                }
                gemini_tools.append(gemini_tool)

            # Make initial Gemini API call
            full_prompt = f"{system_prompt}\n\nUser: {query}"
            
            if gemini_tools:
                response = self.model.generate_content(
                    full_prompt,
                    tools=gemini_tools,
                    generation_config=genai.types.GenerationConfig(
                        max_output_tokens=self.config['ai']['max_tokens'],
                        temperature=self.config['ai']['temperature']
                    )
                )
            else:
                response = self.model.generate_content(
                    full_prompt,
                    generation_config=genai.types.GenerationConfig(
                        max_output_tokens=self.config['ai']['max_tokens'],
                        temperature=self.config['ai']['temperature']
                    )
                )

            # Process response and handle tool calls
            final_text = []
            
            # Check if Gemini wants to use function calls
            if response.candidates[0].content.parts:
                for part in response.candidates[0].content.parts:
                    if hasattr(part, 'text') and part.text:
                        final_text.append(part.text)
                    
                    elif hasattr(part, 'function_call') and part.function_call:
                        func_call = part.function_call
                        tool_name = func_call.name
                        tool_args = dict(func_call.args)
                        
                        print(f"🔧 Calling tool: {tool_name}")
                        print(f"📋 Parameters: {tool_args}")
                        
                        try:
                            # Execute tool call
                            result = await self.session.call_tool(tool_name, tool_args)
                            
                            # Add tool execution info to response
                            final_text.append(f"\n🔧 **Tool Executed**: {tool_name}")
                            final_text.append(f"📋 **Parameters**: {tool_args}")
                            
                            # Get Gemini's interpretation of the tool result
                            follow_up_prompt = f"""Based on the tool execution result below, provide a clear analysis and explanation to the user:

Tool: {tool_name}
Parameters: {tool_args}
Result: {str(result.content)}

Please interpret this data and provide insights relevant to the user's original question: "{query}" """

                            follow_up_response = self.model.generate_content(
                                follow_up_prompt,
                                generation_config=genai.types.GenerationConfig(
                                    max_output_tokens=self.config['ai']['max_tokens'],
                                    temperature=self.config['ai']['temperature']
                                )
                            )

                            # Add Gemini's analysis of the result
                            if follow_up_response.candidates[0].content.parts:
                                for follow_part in follow_up_response.candidates[0].content.parts:
                                    if hasattr(follow_part, 'text') and follow_part.text:
                                        final_text.append(f"\n📊 **Analysis**: {follow_part.text}")
                                
                        except Exception as tool_error:
                            error_msg = f"❌ Tool execution failed: {tool_error}"
                            final_text.append(error_msg)
                            print(error_msg)
            
            else:
                final_text.append("🤔 No response generated from AI model")

            return "\n".join(final_text)
            
        except Exception as e:
            error_msg = f"❌ Error processing query: {str(e)}"
            print(error_msg)
            return error_msg

    async def chat_loop(self):
        """Run an interactive chat loop"""
        print("\n" + "="*60)
        print("🚀 Angel One Trading Assistant Started!")
        print("="*60)
        print("💡 Examples of what you can ask:")
        print("   • 'Show me my current holdings'")
        print("   • 'What is the current price of Reliance?'")
        print("   • 'Search for SBIN stock details'") 
        print("   • 'Show me today's top gainers'")
        print("   • 'What are my open positions?'")
        print("   • 'Get NIFTY option chain for this month'")
        print("   • Type 'help' for more examples")
        print("   • Type 'quit' to exit")
        print("="*60)

        while True:
            try:
                query = input("\n💬 Your Query: ").strip()

                if query.lower() in ['quit', 'exit', 'q']:
                    print("👋 Thank you for using Angel One Trading Assistant!")
                    break
                    
                if query.lower() == 'help':
                    self.show_help()
                    continue
                    
                if not query:
                    print("❓ Please enter a query or type 'help' for examples.")
                    continue

                print("\n🤔 Processing your request...")
                response = await self.process_query(query)
                print(f"\n💡 **Response:**\n{response}")

            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {str(e)}")

    def show_help(self):
        """Display help information with example queries"""
        help_text = """
📚 **Angel One Trading Assistant - Help Guide**

🔍 **Market Data Queries:**
   • "What is the current price of [STOCK_NAME]?"
   • "Show me historical data for RELIANCE for last week"
   • "Search for HDFC Bank stock details"
   • "Get candlestick data for NIFTY"

📊 **Portfolio & Account:**
   • "Show me my current holdings"
   • "What are my open positions?"
   • "Show my account profile"
   • "What are my RMS limits?"

📈 **Market Analysis:**
   • "Show me today's top gainers"
   • "What are the biggest losers today?"
   • "Get NIFTY option Greeks for current month"
   • "What is the current put-call ratio?"

📋 **Order Management:**
   • "Show my order book"
   • "Show my trade book"
   • "Place a buy order for 10 shares of RELIANCE at market price"
   • "Cancel order with ID [ORDER_ID]"

⚡ **GTT & Advanced:**
   • "Show my GTT rules"
   • "Create a GTT rule for SBIN"
   • "Convert my INTRADAY position to DELIVERY"

⚠️  **Safety Notes:**
   • All trading operations require careful consideration
   • Verify all parameters before placing real orders
   • Use DRY_RUN_MODE=true in .env for testing
   • Market data is subject to exchange delays

💡 **Tips:**
   • Be specific with stock names (use full names or symbols)
   • Include timeframes for historical data requests
   • Check market hours for live data accuracy
        """
        print(help_text)

    async def cleanup(self):
        """Clean up resources"""
        await self.exit_stack.aclose()

async def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("❌ Usage: python angel_one_mcp_client.py <path_to_server_script>")
        print("📝 Example: python angel_one_mcp_client.py angel_one_mcp_server.py")
        sys.exit(1)

    client = AngelOneMCPClient()
    try:
        server_path = sys.argv[1]
        success = await client.connect_to_server(server_path)
        
        if success:
            await client.chat_loop()
        else:
            print("❌ Failed to connect to server. Please check the server script path and try again.")
            
    except Exception as e:
        print(f"❌ Fatal error: {str(e)}")
    finally:
        await client.cleanup()

if __name__ == "__main__":
    asyncio.run(main()) 