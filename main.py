"""cbBTC paper-money bot for agent-fun/bars-replay/v1.

A full round trip costs about 26 bps in fees, slippage and price impact, so frequent
trading only feeds the costs. The bot therefore buys once, a few bars into the scored
window, and holds. One trailing stop protects it: when a close lands 3% under the best
close since the entry, the whole position is sold and the bot stays in cash for good.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "vendor"))
import makefun_bars  # noqa: E402

# --- tunables -------------------------------------------------------------------------
SYMBOL = "CBBTC"
# Wait 17 scored bars before entering: lets the opening minutes settle so the single
# entry is not taken on the first, noisiest prints of the window.
ENTRY_BARS = 17
# Trailing stop at 3% below the peak close (in bps of the peak): wide enough to sit
# through ordinary intraday BTC noise, tight enough to keep drawdown far below 25%.
STOP_KEEP_BPS = 9_700
BPS = 10_000
BUY_MAX_SLIPPAGE_BPS = 100
SELL_MAX_SLIPPAGE_BPS = 500
# ---------------------------------------------------------------------------------------


class Plan:
    """What the bot has done so far: entered once, and possibly stopped out."""

    def __init__(self):
        self.entered = False
        self.done = False
        self.peak_close = 0


plan = Plan()


def held_qty(state):
    holding = state.positions.get(SYMBOL)
    return holding.qty if holding is not None else 0


def on_batch(state, batch):
    if state.warming_up or plan.done:
        return None
    close = state.close(SYMBOL)
    if close is None:
        return None
    qty = held_qty(state)

    if qty > 0:
        plan.peak_close = max(plan.peak_close, close)
        if close * BPS < plan.peak_close * STOP_KEEP_BPS:
            # Sell everything; if the market refuses, the next bar retries while the
            # close stays under the stop line.
            return [{"side": "sell", "symbol": SYMBOL, "qty": qty,
                     "max_slippage_bps": SELL_MAX_SLIPPAGE_BPS}]
        return None

    if plan.entered:
        # Flat after having entered: the stop sold the position. Never buy again.
        plan.done = True
        return None

    if state.seq - state.warmup_bars < ENTRY_BARS:
        return None
    spend = min(state.cash, state.equity)
    if spend < int(state.hello["fees"]["min_notional_quote_units"]):
        return None
    plan.entered = True
    plan.peak_close = close
    return [{"side": "buy", "symbol": SYMBOL, "notional_quote_units": spend,
             "max_slippage_bps": BUY_MAX_SLIPPAGE_BPS}]


makefun_bars.run(on_batch)
