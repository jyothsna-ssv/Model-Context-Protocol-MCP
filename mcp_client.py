import os
import json
import asyncio
import aiohttp
from dotenv import load_dotenv
import google.generativeai as genai

# --- Config ---
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)
MODEL_NAME = "models/gemini-2.5-flash"

# --- Gemini helper ---
async def ask_gemini(query: str):
    model = genai.GenerativeModel(MODEL_NAME)
    prompt = f"""
You are a tool selector. Choose the correct MCP tool and its parameters in JSON.

Available tools:
get_stock_price(symbol: str)
compare_stocks(symbol1: str, symbol2: str)

User Query: "{query}"

If the query involves a single company (e.g., "price of Walmart"), 
respond exactly as:
{{ "tool_name": "get_stock_price", "args": {{"symbol": "WMT"}} }}

If the query involves comparison (e.g., "Compare Amazon and Walmart"), 
respond exactly as:
{{ "tool_name": "compare_stocks", "args": {{"symbol1": "AMZN", "symbol2": "WMT"}} }}
Only return valid JSON, no commentary.
"""
    response = model.generate_content(prompt)
    raw = response.text.strip()
    print(f"[debug] Gemini raw output: {raw}\n")

    try:
        return json.loads(raw.strip("`").replace("json", "").strip())
    except Exception:
        lower = raw.lower()
        if "compare" in lower:
            return {"tool_name": "compare_stocks", "args": {"symbol1": "AMZN", "symbol2": "WMT"}}
        elif "stock" in lower or "price" in lower:
            return {"tool_name": "get_stock_price", "args": {"symbol": "WMT"}}
        else:
            return {"tool_name": "unknown", "args": {}}

async def main():
    print("----------------------------------------------------------")
    print("Executing MCP Client")
    print("----------------------------------------------------------")
    print("What is your query? → ", end="")

    async with aiohttp.ClientSession() as session:
        while True:
            user_query = input().strip()
            if user_query.lower() in ["exit", "quit"]:
                print("Session ended. Goodbye! 👋")
                break

            print("----------------------------------------------------------")
            print(f"The User Input is : {user_query}")
            print("Connection established, creating session...")
            print("[agent] Session created, initializing...")
            print("[agent] MCP session initialized")

            decision = await ask_gemini(user_query)
            tool = decision.get("tool_name")
            args = decision.get("args", {})

            print(f"To execute the User Query: {user_query}")
            print(f"- The Identified tool is {tool}")
            print(f"- The parameters required are {args}")

            try:
                if tool == "get_stock_price":
                    url = "http://127.0.0.1:8000/get_stock_price"
                    async with session.get(url, params=args) as resp:
                        data = await resp.json()
                        if "error" in data:
                            print(f"⚠️ Server Error: {data['error']}")
                        else:
                            print(f"The current price of {args['symbol']} is {data['price']}")

                elif tool == "compare_stocks":
                    url = "http://127.0.0.1:8000/compare_stocks"
                    async with session.get(url, params=args) as resp:
                        data = await resp.json()
                        if "error" in data:
                            print(f"⚠️ Server Error: {data['error']}")
                        else:
                            print(f"{data['result']} ({data['symbol1']}: {data['price1']}, {data['symbol2']}: {data['price2']})")

                else:
                    print("⚠️ Unknown tool")

            except Exception as e:
                print(f"❌ Client Error: {e}")

            print("----------------------------------------------------------")
            print("What is your query? → ", end="")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nSession terminated by user. Goodbye! 👋")
