"""A patient cbBTC holder with a safety stop.

The replay charges about 26 bps for a full-size round trip, and a minute of cbBTC moves about 6 bps, so
trading in and out loses to costs: the bot makes one decision only. It waits ENTRY_BARS bars after the
window opens (a first price is rarely the best one), spends all its cash on cbBTC, and holds. Its one
exit is a trailing stop: if the close falls STOP_FRACTION below the highest close since entry it sells
everything and stays in cash for the rest of the window, which caps the damage of a sharp drop.

Deterministic by construction: no clock, no randomness, only the bars the harness sends.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "vendor"))
import makefun_bars  # noqa: E402

SYMBOL = "CBBTC"
ENTRY_BARS = 17
STOP_FRACTION = 0.03
BUY_SLIPPAGE_BPS = 100
SELL_SLIPPAGE_BPS = 500

memory = {"bought": False, "peak": 0, "stopped": False}


def on_batch(state, batch):
    if state.warming_up or memory["stopped"]:
        return None
    close = state.close(SYMBOL)
    if close is None:
        return None
    position = state.positions.get(SYMBOL)
    scored_bar = state.seq - state.warmup_bars

    if position is None or position.qty == 0:
        if memory["bought"] or scored_bar < ENTRY_BARS:
            return None
        spend = min(state.cash, state.equity)
        if spend < int(state.hello["fees"]["min_notional_quote_units"]):
            return None
        memory["bought"] = True
        memory["peak"] = close
        return [{"side": "buy", "symbol": SYMBOL, "notional_quote_units": spend, "max_slippage_bps": BUY_SLIPPAGE_BPS}]

    memory["peak"] = max(memory["peak"], close)
    if close * 10_000 < memory["peak"] * int((1 - STOP_FRACTION) * 10_000):
        return [{"side": "sell", "symbol": SYMBOL, "qty": position.qty, "max_slippage_bps": SELL_SLIPPAGE_BPS}]
    return None


def on_done(state, done):
    memory["stopped"] = True


makefun_bars.run(on_batch, on_done=on_done)
