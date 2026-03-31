from broker_exness.adapter import TradeOrder

def validate_order(order: TradeOrder):
    # Sanity checks
    if order.volume <= 0:
        return "Volume must be greater than 0"
    if order.volume > 100.0: # Set your own max cap for safety
        return "Volume exceeds safety limit (10.0)"
    if order.symbol.upper() not in ["EURUSD", "GBPUSD", "BTCUSD", "XAUUSD"]: # Example list
        # You could fetch the actual list from MT5 later
        pass
    return None
