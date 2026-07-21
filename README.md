# ChainLens

ChainLens is an explainable options decision auditor that turns a verified historical market replay into a human-readable sequence of market structure, signal, and decision states. This public Build Week submission demonstrates how an analyst can inspect the progression of a bearish pre-break setup without connecting to a broker or placing an order.

The included artifact is a verified NIFTY replay for **2026-07-08**. It is historical replay data, not a live feed, forecast, recommendation, or claim of trading performance.

## Architecture

The repository is deliberately small and auditable:

- `demo_result.json` is the read-only replay artifact and source of all values shown in the demo.
- `chainlens_demo.py` validates the paper-only safety flags, serves the replay at `/api/state`, and serves a dependency-free browser interface at `/`.
- The browser renders the timeline locally. Unavailable fields are shown as `N/A`; they are not estimated or inferred.

No broker SDK, credential handling, external API, database, trading engine, or order route is included.

## Verified replay sequence

The 2026-07-08 replay contains these three states, in order:

1. `13:21:35` — `ARMED_PREBREAK_EARLY` (`BEARISH_STRUCTURE_BUILDING`), spot `24219.2`, India VIX `12.22`
2. `13:38:11` — `ARMED_PREBREAK_STRONG` (`BEARISH_PREBREAK_STRONG`), spot `24206.5`, India VIX `12.27`
3. `13:47:15` — `CONFIRMED_MOMENTUM_ADDON` (`BEARISH_MOMENTUM_CONFIRMED`), spot `24146.15`, India VIX `12.55`

The support/gate remains `24200.0` throughout. Pin risk, confidence, bearish pressure, and bullish pressure are unavailable in the verified artifact and display as `N/A`. Resistance and target are also `N/A`. These missing values are intentionally not reconstructed.

## Run locally

Requirements: Python 3 with no third-party packages.

```bash
python3 chainlens_demo.py
```

Open `http://localhost:8898`. Stop the server with `Ctrl+C`.

For a quick syntax and artifact check:

```bash
python3 -m py_compile chainlens_demo.py
python3 -m json.tool demo_result.json >/dev/null
```

## Safety and limitations

- Historical replay and paper-trading research only; this is not investment advice.
- Real-order execution is disabled. Startup fails unless `paper_only` is `true` and `real_orders_allowed` is `false`.
- The repository contains no broker credentials, API tokens, live trading code, or real-order execution path.
- The interface only explains the supplied replay artifact. It does not fetch live prices, generate new market data, backtest returns, or establish profitability.
- Missing values remain `N/A`; the demo does not fabricate values.
- Historical observations do not predict future results. Options involve substantial risk, including loss of capital.

## Submission refinement disclosure

Codex using **GPT-5.6 Sol** was used to audit and refine this public submission repository. Its work was limited to code and documentation quality, missing-value handling, safety review, and integrity checks; it did not create or alter the verified 2026-07-08 replay values.
