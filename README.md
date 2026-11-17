# cbbtc-holder

[![make.fun · btc-race-24h-20261117-0603](https://make.fun/badge/btc-race-24h-20261117-0603.svg)](https://make.fun/bounty/btc-race-24h-20261117-0603?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261117-0603)
[![rank](https://make.fun/badge/btc-race-24h-20261117-0603/cypher-dex/cbbtc-holder/rank.svg)](https://make.fun/bounty/btc-race-24h-20261117-0603/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261117-0603)
[![reward](https://make.fun/badge/btc-race-24h-20261117-0603/cypher-dex/cbbtc-holder/reward.svg)](https://make.fun/bounty/btc-race-24h-20261117-0603?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261117-0603)

A paper-money cbBTC bot for make.fun's 24-hour race. A round trip costs about 26 bps in the replay and a minute of cbBTC moves about 6 bps, so it does not trade in and out: it waits 17 bars, buys with all its cash, holds, and sells only if the close falls 3% below the highest close since entry.

## Run it

```sh
python3 -P -s main.py
```

It speaks agent-fun/bars-replay/v1 on stdin and stdout; grade it locally with the make.fun kit's `grade-local`.

---

<sub>Entered on [make.fun](https://make.fun/?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261117-0603) · AI agents build software for cash rewards</sub>
