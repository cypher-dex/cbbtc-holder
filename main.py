"""cbBTC paper-money bot for agent-fun/bars-replay/v1.

Every round trip pays roughly 26 bps in fees, slippage and impact, so trading in and
out bleeds money. This bot makes one entry shortly after the scored window opens and
then simply holds, guarded by a single trailing stop: if the close falls 3% below the
highest close seen since the entry, it sells everything and stays in cash for good.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "vendor"))
import makefun_bars  # noqa: E402

SYMBOL = "CBBTC"
ENTRY_BARS = 17
STOP_NUM = 9700
STOP_DEN = 10000
BUY_SLIPPAGE_BPS = 100
SELL_SLIPPAGE_BPS = 500

bought = False
stopped = False
peak = 0


def on_batch(state, batch):
    global bought, stopped, peak
    if state.warming_up or stopped:
        return None
    close = state.close(SYMBOL)
    if close is None:
        return None
    holding = state.positions.get(SYMBOL)
    qty = holding.qty if holding is not None else 0

    if qty > 0:
        if close > peak:
            peak = close
        if close * STOP_DEN < peak * STOP_NUM:
            return [{"side": "sell", "symbol": SYMBOL, "qty": qty,
                     "max_slippage_bps": SELL_SLIPPAGE_BPS}]
        return None

    if bought:
        # We held and the position is now gone: the stop filled, never re-enter.
        stopped = True
        return None

    scored_bar = state.seq - state.warmup_bars
    if scored_bar < ENTRY_BARS:
        return None
    spend = min(state.cash, state.equity)
    min_notional = int(state.hello["fees"]["min_notional_quote_units"])
    if spend < min_notional:
        return None
    bought = True
    peak = close
    return [{"side": "buy", "symbol": SYMBOL, "notional_quote_units": spend,
             "max_slippage_bps": BUY_SLIPPAGE_BPS}]


makefun_bars.run(on_batch)
