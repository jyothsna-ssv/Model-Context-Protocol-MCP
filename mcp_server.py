import yfinance as yf
from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/get_stock_price")
async def get_stock_price(symbol: str):
    """Return current stock price for the given symbol."""
    try:
        stock = yf.Ticker(symbol)
        hist = stock.history(period="1d")

        if hist.empty:
            return {"error": f"No data found for symbol '{symbol}'"}

        price = round(hist["Close"].iloc[-1], 2)
        return {"symbol": symbol, "price": f"${price}"}

    except Exception as e:
        return {"error": f"Failed to fetch stock data: {str(e)}"}


@app.get("/compare_stocks")
async def compare_stocks(symbol1: str, symbol2: str):
    """Compare two stock prices."""
    try:
        s1 = yf.Ticker(symbol1)
        s2 = yf.Ticker(symbol2)

        h1 = s1.history(period="1d")
        h2 = s2.history(period="1d")

        if h1.empty or h2.empty:
            return {"error": f"Invalid symbols or no data for '{symbol1}' or '{symbol2}'"}

        p1 = round(h1["Close"].iloc[-1], 2)
        p2 = round(h2["Close"].iloc[-1], 2)

        if p1 > p2:
            result = f"{symbol1} is higher than {symbol2} in stock price."
        elif p2 > p1:
            result = f"{symbol2} is higher than {symbol1} in stock price."
        else:
            result = f"{symbol1} and {symbol2} have equal stock prices."

        return {
            "result": result,
            "symbol1": symbol1, "price1": f"${p1}",
            "symbol2": symbol2, "price2": f"${p2}"
        }

    except Exception as e:
        return {"error": f"Failed to compare stocks: {str(e)}"}


if __name__ == "__main__":
    print("[server] Starting MCP server on http://127.0.0.1:8000 ...")
    uvicorn.run(app, host="127.0.0.1", port=8000)
