# MicroFlow-L2 — Evaluation Demo

Windows x86-64 / Linux x86-64 · AVX2/FMA · C++ engine · Python / NumPy

Documentation revision: 2 November 2026 · Commercial license: v1.0.0

Contact: microflowl2@proton.me

Independent project. Not affiliated with, endorsed by, or supported by Binance.

## Part A — Free Evaluation Demo

This restricted evaluation package lets you inspect live market-data publication and local Python integration before buying the full source-code product. It is not the full product.

### Demo Scope — Read This First

| Item | Evaluation package |
| --- | --- |
| Price | Free evaluation; no payment required |
| Session | 15 minutes per launch; engine terminates automatically |
| Instruments | BTCUSDT and ETHUSDT, fixed |
| Published features | `mid_price`, `wobi`, `fast_ofi`, `flow_toxicity`, fixed |
| Matrix | 4 feature rows × 64 symbol slots; NumPy `float64` |
| Intended columns | Column 0: BTCUSDT; column 1: ETHUSDT |
| Other columns | Not additional instruments; not intended for use |
| Publication | Nominal 100 ms schedule, not a hard real-time guarantee |
| Configuration | No `config.json`; symbols and outputs are fixed |
| C++ source | Not included in the public demo |
| Python examples | `client.py` and `print_feats.py` |
| Order execution | Not included |

The demo performs a reduced calculation workload and processes only two instruments. It is not performance-equivalent to the full product. No separate demo microbenchmark figures are provided. The benchmark numbers in Part B belong to the reported full-product workloads, not this demo. Do not extrapolate full-product CPU cost or throughput from this restricted build.

Each launch starts a new evaluation session. Restarting resets in-memory calculation state; it does not resume the previous history or filter state. The limit is per session, not a single lifetime trial. Startup values and initialization behavior still matter after every restart.

### No API Keys, Account Credentials, or Wallet

The engine connects automatically to Binance USD-M Futures public market-data streams at `fstream.binance.com`, using TLS on port 443. No Binance API keys, exchange account credentials, trading permissions, wallet connection, or remote license activation are required by the supplied package.

Internet access is required. Regional restrictions, exchange outages, firewall/DNS failures, and certificate problems can prevent reception. Do not provide private keys, seed phrases, or trading API credentials to evaluate the software.

### Folder Layout

```text
MicroFlow-L2-Demo/
├── linux_demo/
│   └── FuturesMicrostructureEngine_linux_demo
├── windows_demo/
│   ├── FuturesMicrostructureEngine_windows_demo.exe
│   ├── libcrypto-3-x64.dll
│   ├── libssl-3-x64.dll
│   └── simdjson.dll
├── client.py
├── print_feats.py
├── README.md
├── LICENSE
└── third_party_licenses/
```

### Requirements and Platform Status

- x86-64 CPU supporting AVX2 and FMA. An unsupported instruction can terminate the program.
- Windows: Windows 11 is the documented local test platform. Keep the three supplied DLLs beside the executable. A compatible Microsoft Visual C++ v14 x64 runtime may also be required. Obtain it from Microsoft's official supported-download page, not a DLL download website.
- Linux: this binary was built and exercised on Ubuntu 24.04 x86-64 in GitHub Actions. It is dynamically linked, not a universal standalone Linux executable. Arch and other distributions have not been verified with the supplied package.
- Python 3.9 or newer for the supplied reader syntax and a compatible NumPy installation. The Linux tests used the runner's system Python/NumPy; every combination is not verified.
- Run the engine and readers in the same OS environment with appropriate local shared-memory permissions. Running a Windows engine and a Linux reader is not the tested arrangement.

Microsoft runtime information: https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist

### Windows — Start the Demo

Open PowerShell in the package root. Install NumPy into the Python environment you will use, if necessary:

```powershell
python -m pip install numpy
```

Start the engine and leave the terminal open:

```powershell
.\windows_demo\FuturesMicrostructureEngine_windows_demo.exe
```

In a second terminal, also in the package root:

```powershell
python print_feats.py
```

Do not pass a configuration file. Moving only the `.exe` away from its DLLs is not a complete installation. If Windows reports a missing Microsoft C++ runtime, install the appropriate supported x64 Redistributable from Microsoft.

### Ubuntu 24.04 — Start the Demo

The binary requires compatible runtime libraries including `libssl.so.3`, `libcrypto.so.3`, `libsimdjson.so.19`, `libstdc++.so.6`, and glibc. These runtime libraries are not bundled in `linux_demo/`.

On Ubuntu 24.04:

```bash
sudo apt-get update
sudo apt-get install -y \
  libssl3t64 libsimdjson19 libstdc++6 \
  ca-certificates python3 python3-numpy
```

These are execution requirements, not C++ source-build instructions. Tests ran on a runner with build dependencies installed, not a separately verified minimal clean machine.

From the package root:

```bash
chmod +x ./linux_demo/FuturesMicrostructureEngine_linux_demo
./linux_demo/FuturesMicrostructureEngine_linux_demo
```

Leave the engine running. In a second terminal from the package root:

```bash
python3 print_feats.py
```

For a missing-library error, inspect the requirements:

```bash
ldd ./linux_demo/FuturesMicrostructureEngine_linux_demo
```

A newer distribution package named `simdjson` does not necessarily provide the exact binary interface requested here. Do not rename incompatible libraries or replace system libraries to force a match. ARM and Apple Silicon builds are not supplied.

### One Engine per Shared-Memory Name

The demo and the default full-product implementation use the same shared-memory name: `Local\microflow_shm` on Windows or `/dev/shm/microflow_shm` on Linux.

Run only one engine instance per mapping name. Do not run the demo and full product simultaneously with that default name. Stop the previous engine and close its readers before switching builds. After an engine restart, close and recreate the Python client. An existing mapping or an old matrix is not evidence of current live data.

The demo reader takes no configuration argument. The paid configurable reader is not interchangeable with it. Layout checks are configuration checks, not security signatures or proof of calculation correctness.

### The Four Outputs

These are documented implementation measurements, not calibrated predictions or trading recommendations. Part B retains their complete definitions and guards.

#### `mid_price`

\[
M=(P_b+P_a)/2.
\]

The midpoint of the latest accepted best bid and ask. It is not necessarily executable and excludes fees, execution impact, and depth. It can become stale.

#### `wobi`

The quantity weights for the five parsed levels are `(1, 0.5, 0.25, 0.125, 0.0625)`:

\[
B=\sum_{\ell=1}^{5}w_\ell Q_\ell^b,\quad
A=\sum_{\ell=1}^{5}w_\ell Q_\ell^a,\quad
W=\operatorname{clip}((B-A)/(B+A),-1,1)
\]

when the denominator is positive. This is weighted shallow-book quantity imbalance, not full-book liquidity. The fixed weights are implementation choices, not calibrated predictive coefficients.

#### `fast_ofi`

\[
d_k=\sum_{j\in\mathcal J_k}(W_j-W_{j-1}),\qquad
f_k=0.10d_k+0.90f_{k-1}.
\]

It filters accumulated signed WOBI changes, not the WOBI level. Opposing changes can cancel; zero input causes decay. It is not canonical Level-1 OFI.

#### `flow_toxicity`

\[
T_k=\left|\operatorname{clip}(F_k/\max(V_k,10^{-8}),-1,1)\right|.
\]

`F` and `V` are the implementation's decayed signed processed trade notional and volume measures. Initialization and per-evaluation decay affect interpretation. This is not VPIN, an adverse-selection probability, or a calibrated toxicity estimator.

### Example Output

```text
==================================================
   MicroFlow-L2 EVALUATION DEMO  (Seq: 18000 )
==================================================
 mid_price        : BTC [  77029.9500] | ETH [   2253.7650]
 wobi             : BTC [      0.9749] | ETH [      0.9697]
 fast_ofi         : BTC [      0.0923] | ETH [      0.0290]
 flow_toxicity    : BTC [      0.3321] | ETH [      0.9087]
--------------------------------------------------
 Session timer: Max 15 minutes. Press Ctrl+C to exit.
==================================================
```

Recorded illustrative values, not current prices or signals. Sequence numbers are publication metadata, not precise timers.

### Session End and Stale Warnings

At the session limit, the engine reports:

```text
[DEMO] 15-minute evaluation session ended. Engine shutting down.
```

Python remains open and can report:

```text
[STALE] Engine offline or 15-min timeout reached (Lag: 1506.7 ms)
```

Press Ctrl+C to stop the inspector. A stale warning also covers an offline engine or an old heartbeat; it does not prove the timer expired. A healthy global heartbeat does not establish freshness of each symbol. Last-published values are not necessarily live data.

The session is limited to 15 minutes; shutdown is not guaranteed at a millisecond-exact instant. Scheduling and shutdown work affect observed exit time.

### What Was Tested

- Windows: author-built MSVC `/O2`, AVX2 demo, with demonstrated live reader output and evaluation-end behavior. Documented local hardware: AMD Ryzen 7 5700G.
- Ubuntu: the demo compiled and passed a short integration test for BTC/ETH, the fixed feature layout, a 4 × 64 matrix, advancing publications, finite sampled active outputs, healthy positive mid-prices, and output from the actual `print_feats.py`.
- A second Ubuntu test waited for natural process exit, required exit code zero and the evaluation-end message, and checked that Python remained open and produced a new stale warning with a stale heartbeat after exit. The acceptance window was 895–960 seconds from process launch. The exact observed time is in the run log; total workflow duration is not engine session duration.
- The successful combined demo workflow shown by the author used commit prefix `0fa938b`.

These are limited integration checks, not an independent audit, exhaustive mathematical validation, a guarantee of per-symbol freshness, or long-running endurance evidence. The demo does not validate the full product's other features.

### Sharing and Python Examples

Please share the official demo repository/download link rather than re-uploading the engine or repackaging the demo. Redistribution permissions are defined in `LICENSE` and do not limit independent third-party rights.

The reader sources illustrate how to open and inspect the shared-memory interface. You may inspect and adapt them for your own private evaluation under Part A of `LICENSE`; purchasers may use and modify the supplied clients internally under the commercial license. They have not been assigned a separate general-purpose open-source license. Visibility of source is not a blanket permission to redistribute it.

### Third-Party Components

OpenSSL, simdjson, Boost, and other third-party components retain their own licenses. See `third_party_licenses/` and the component-specific notices accompanying the package. MicroFlow-L2 restrictions apply to the Author's original work, not to independently granted third-party rights. Python and NumPy are installed separately, not bundled by this layout.

### Before Buying

Read all of Part B and `LICENSE` before payment. Part A of `LICENSE` authorizes free evaluation; Part B governs the paid product. Running the demo does not constitute a purchase or an obligation to pay.

The paid additional compilation/linking remedy covers the specified Windows and Ubuntu environments under commercial Section 5. Other distributions or configurations are not automatically included. This is a source-code developer component, not a turnkey strategy or promise of financial results.

---

## Part B — Full Product: Technical Reference and Purchase Terms

The following sections describe the paid source-code product, not the restricted evaluation executable. They are provided before purchase so prospective buyers can inspect all 42 feature definitions, limitations, performance evidence, platform coverage, price, support, license scope, and refund terms.

Full-product outputs and configuration below are not unlocked in the demo. Source-compilation and repository-cloning commands, and the unverified long Python example, are omitted from this public copy. Complete Windows and Ubuntu build instructions are supplied in the paid private repository. The full commercial license is in the separate `LICENSE` file.

## Full Product Overview

Binance USD-M Futures Market-Data Ingestion and Feature Engine

C++23 · AVX2 / AVX-512 · Local Shared Memory · Python / NumPy

MicroFlow-L2 connects to Binance USD-M Futures public WebSocket streams, processes top-five order-book snapshots and aggregate trade messages, and calculates market-data features in C++.

Selected features are published to local operating-system shared memory on a nominal 100 ms evaluation schedule. Python consumers copy the published matrix into NumPy arrays.

This is source-code developer software. It does not execute trades, manage accounts, recommend transactions, or promise financial results.

Contact: microflowl2@proton.me

Independent project. Not affiliated with, endorsed by, or supported by Binance.

---

## At a Glance

| Item | Scope |
| --- | --- |
| Price | USD 350, one-time |
| License | One purchaser entity; internal commercial use by its authorized personnel |
| Data source | Binance USD-M Futures public WebSockets |
| Depth input | Top-five partial-depth stream requested with `@depth5@100ms` |
| Trade input | Aggregate trade stream, `@aggTrade` |
| Evaluation and publication | Nominal 100 ms schedule |
| Covered builds | Specified Windows 11/MSVC and Ubuntu 24.04/GCC environments below; LICENSE Section 5 |
| Documented live CPU | AMD Ryzen 7 5700G, AVX2 |
| Python interface | Local shared memory; NumPy `float64` matrix |
| Not included | Execution, backtesting, replay, hosting, investment advice |

During a feed interruption, the client can continue returning the last published matrix. A global health indicator is available, but it does not establish freshness of every symbol.

Read the documented limitations and the commercial license v1.0.0 in `LICENSE` before paying.

---

## What You Receive

- C++23 engine source.
- Python shared-memory client.
- Configuration and CMake build files.
- Included benchmark and verification material.
- Feature definitions and implementation limitations.
- Private GitHub repository access.
- Available v1.x corrective releases without an additional license fee.
- Asynchronous, text-based support within the stated scope.

The implementation provides:

- 64 symbol slots.
- 42 documented selectable feature identifiers.
- An export-pointer array with capacity for 48 entries.

The extra pointer capacity does not mean six additional features are supplied.

The exported matrix has shape:

```text
number_of_enabled_features × 64
```

Values use NumPy `float64`. With 42 enabled rows, the matrix payload is 21,504 bytes, excluding the 64-byte header.

Only configured symbol columns are intended for use. Unused columns are not additional instruments.

---

## What the Engine Does

1. Connects to the configured Binance host over TLS.
2. Uses separate depth and aggregate-trade connections.
3. Parses supported messages.
4. Updates fixed-capacity market-data structures.
5. Calculates the documented features.
6. Publishes selected rows to shared memory.
7. Provides a Python reader that copies the matrix and uses sequence-counter checks to detect overlapping writes and retry.

SIMD selection occurs at compile time. The supplied build does not automatically switch between AVX2 and AVX-512 at runtime.

---

## What It Does Not Do

The project does not include:

- Order submission, modification, cancellation, routing, or execution.
- Brokerage or account management.
- Custody of funds.
- Portfolio or execution-risk management.
- Personalized investment advice.
- A ready-to-run strategy or validated trading signals.
- Historical datasets, recording infrastructure, backtesting, or replay.
- Full incremental order-book reconstruction.
- Individual order or queue-position tracking.
- Multi-exchange support.
- Native ARM or Apple Silicon support.
- Managed deployment or hosting.
- Guaranteed uptime or support response times.

Top-five depth messages do not provide the complete exchange order book or every intervening event.

Aggregate trade messages are not a guaranteed unaggregated record of every individual fill.

---

## Intended Use

For developers, researchers and internal teams who want:

- A C++ ingestion and feature-calculation component.
- Processing outside their Python strategy process.
- A local feed accessible to multiple Python processes.
- Source inspection and permitted internal modification.
- Explicit implementation definitions.

You must evaluate whether the outputs are appropriate for your application.

A purchasing company, fund or other organization may use the Software internally
and permit its employees, contractors and collaborators to use it for that
organization's internal purposes.

No strategy horizon, profitability, predictive accuracy, or trading advantage is promised.

### Why Use This Instead of Python Alone?

The product focuses on implementation and integration:

- C++ ingestion and calculation.
- SIMD kernels.
- Fixed-capacity structures.
- Shared-memory publication.
- A Python client.
- Included benchmark and verification code.

The formulas are not claimed to be unique. Python can calculate these quantities.

No controlled comparison against an equivalent Python-only implementation is presented.

### When Another Tool May Fit Better

Consider another approach if you require:

- Turnkey trading.
- Full-depth event reconstruction.
- Historical replay.
- Managed infrastructure.
- Independently audited financial models.
- Native ARM execution.
- Use for the benefit of another entity or client.
- Commercial distribution of calculated outputs.

---

## Video

> Video: https://streamable.com/jqx3qo

---

## Anchor Instrument: Symbol Index 0

Anchor: `symbols[0]` is the reference instrument for cross-asset calculations.

For BTC-relative results, put `"btcusdt"` first:

```json
"symbols": [
  "btcusdt",
  "ethusdt",
  "solusdt"
]
```

The implementation uses column 0. It does not automatically locate BTC by name.

Changing the first symbol changes the reference instrument. Descriptions referring to BTC assume that BTC occupies column 0.

The anchor column uses these conventions:

| Feature | Anchor-column value |
| --- | ---: |
| `dynamic_beta` | 1.0 |
| `beta_confidence` | 1.0 |
| `idiosyncratic_return` | 0.0 |
| `idiosyncratic_ofi` | 0.0 |

These are assigned conventions, not measurements of confidence or certainty.

---

<details>
<summary>Feature reference: all 42 identifiers, formulas, interpretation, and current implementation limitations</summary>


## Reading the Feature Reference

The definitions below describe the supplied implementation, including guards, initialization, and update clocks. They are implementation documentation, not an independent mathematical or financial audit.

Documentation numbers are not exported matrix-row indices. Obtain row indices from:

```python
features = client.get_active_features()
```

All examples describe technical inspection and research. None instructs the user to buy, sell, hold, size a position, or execute a strategy.

### Notation

| Symbol | Meaning |
| --- | --- |
| $i$ | Instrument index |
| $0$ | Anchor instrument |
| $k$ | Calculation/evaluation cycle |
| $j$ | Accepted depth-message index |
| $s$ | Exchange-time history slot, obtained from depth timestamp divided by 100 ms |
| $P_b,P_a$ | Best bid and ask |
| $Q_b,Q_a$ | Best-level base quantities |
| $Q_\ell^b,Q_\ell^a$ | Parsed quantity at book level $\ell$ |
| $M_{i,s}$ | Stored mid-price in history slot $s$ |
| $\text{clip}(x,a,b)$ | Clamp $x$ to $[a,b]$ |

Prices use quote units per base unit. For USDT-quoted instruments, calculated quote notional is USDT, not a guaranteed equivalent amount of sovereign USD.

Identifiers containing `_usd` retain their code names.

The export format is `float64`, but some parser-derived values use narrower intermediate floating-point storage before export.

---

## Price and Depth: Features 1–21

### 1. `best_bid_price`

Latest accepted best visible bid price.

```math
P_b=P^b_1
```

Purpose: inspect the displayed buying quote and provide inputs to mid-price and spread calculations.

Limitations: this is a stored quote from the most recent accepted depth message, not a guaranteed executable price. It can become stale.

### 2. `best_bid_qty`

Latest accepted base quantity at the best bid.

```math
Q_b=Q^b_1
```

Purpose: inspect displayed best-bid size.

Limitations: excludes hidden liquidity and deeper levels. Changes do not identify whether orders were executed, cancelled, or replaced.

### 3. `best_ask_price`

Latest accepted best visible ask price.

```math
P_a=P^a_1
```

Purpose: inspect the displayed selling quote.

Limitations: not a guaranteed executable price; may be stale by the time the consumer reads it.

### 4. `best_ask_qty`

Latest accepted base quantity at the best ask.

```math
Q_a=Q^a_1
```

Purpose: inspect displayed best-ask size.

Limitations: excludes hidden and deeper liquidity and does not provide queue position.

### 5. `prev_bid_price`

Before replacing the current accepted bid state, the previous stored bid price is copied here.

```math
P^{b,\mathrm{prev}}_j=P^b_{j-1}
```

Purpose: compare successive accepted depth states.

Limitations: “previous” means the previous accepted message, not a fixed-duration lag or every exchange event. Before sufficient updates, initialization values may remain.

### 6. `prev_bid_qty`

Previous stored best-bid quantity.

```math
Q^{b,\mathrm{prev}}_j=Q^b_{j-1}
```

Purpose: inspect changes in displayed bid size.

Limitations: a difference cannot distinguish cancellations from executions or newly posted orders. The two observations may have different timestamps.

### 7. `prev_ask_price`

Previous stored best-ask price.

```math
P^{a,\mathrm{prev}}_j=P^a_{j-1}
```

Purpose: compare successive accepted ask states.

Limitations: not a fixed-time lag or complete quote-event history.

### 8. `prev_ask_qty`

Previous stored best-ask quantity.

```math
Q^{a,\mathrm{prev}}_j=Q^a_{j-1}
```

Purpose: inspect displayed ask-size changes.

Limitations: no attribution to individual orders or event types.

### 9. `mid_price`

Arithmetic midpoint of best bid and ask.

```math
M=\frac{P_b+P_a}{2}
```

Purpose: a common reference for returns and cross-asset calculations.

Limitations: not necessarily tradable and does not account for depth, fees, or execution impact.

### 10. `micro_price`

Top-of-book quantity-weighted price:

```math
P_{\mathrm{micro}}=
\frac{P_bQ_a+P_aQ_b}{Q_b+Q_a}.
```

It is updated when $Q_b+Q_a>0$.

Purpose: compare a quantity-weighted reference with the midpoint.

Limitations: uses only best-level quantities. This is a particular weighted-price formula, not a validated future-price estimate or every model called “microprice.” If the quantity condition fails, the assignment is skipped rather than producing a newly validated estimate.

### 11. `current_spread_bps`

Quoted spread normalized by the bid price:

```math
S=10{,}000\frac{P_a-P_b}{P_b}.
```

Purpose: inspect the quoted relative spread.

Limitations: the denominator is bid, not mid. It excludes fees, slippage, market impact, and execution uncertainty.

### 12. `avg_spread_bps`

Spread EWMA updated on accepted depth messages:

```math
\bar S_j=0.05S_j+0.95\bar S_{j-1}.
```

When the stored average is zero, the implementation initializes it to the current spread.

Purpose: provide a smoothed spread reference.

Limitations: smoothing runs on depth updates, not elapsed time. Instruments with different update frequencies have different effective wall-clock smoothing.

### 13. `tobi`

Top-of-book quantity imbalance:

```math
T=\text{clip}
\left(
\frac{Q_b-Q_a}{Q_b+Q_a},-1,1
\right)
```

when total best-level quantity is positive.

Purpose: describe relative displayed quantity at the best quotes.

Limitations: not a directional forecast, order-arrival model, or measure of hidden liquidity. The parsed value remains at its initialization convention when the denominator condition fails.

### 14. `wobi`

Weighted quantity imbalance across parsed levels, using:

```math
(w_1,w_2,w_3,w_4,w_5)
=(1,0.5,0.25,0.125,0.0625).
```

```math
B=\sum_{\ell=1}^{5}w_\ell Q_\ell^b,
\qquad
A=\sum_{\ell=1}^{5}w_\ell Q_\ell^a.
```

```math
W=\text{clip}
\left(
\frac{B-A}{B+A},-1,1
\right)
```

when $B+A>0$.

Purpose: inspect weighted shallow-book quantity balance.

Limitations: fixed weights are an implementation choice, not calibrated predictive coefficients. It is not full-book imbalance.

### 15. `prev_wobi`

WOBI stored before the latest accepted depth update:

```math
W^{\mathrm{prev}}_j=W_{j-1}.
```

Purpose: compare accepted imbalance states.

Limitations: not a fixed-duration lag. First-observation handling assigns the current WOBI as the reference to avoid treating startup as a real imbalance change.

### 16. `delta_wobi`

Signed WOBI differences are accumulated between evaluations:

```math
d_k=\sum_{j\in\mathcal J_k}(W_j-W_{j-1}).
```

The accumulator is copied into the exported calculation state and reset during evaluation.

Purpose: inspect the net change in weighted imbalance.

Limitations: this is not absolute variation, trading volume, or canonical Level-1 order-flow imbalance. Opposing changes can cancel. With no accumulated changes, the input is zero.

### 17. `depth_ratio_5`

Let:

```math
D_b=\sum_{\ell=2}^{5}Q_\ell^b,
\qquad
D_a=\sum_{\ell=2}^{5}Q_\ell^a.
```

Then:

```math
D=\frac{D_b+D_a}{\max(Q_b+Q_a,10^{-6})}.
```

Purpose: compare deeper displayed quantity with best-level quantity.

Limitations: quantity-based, not notional-based. A small guarded denominator can produce a large value. It does not describe the entire book.

### 18. `slope_bid`

```math
L_b=
\frac{D_b}
{\max(P_b-P_{b,\mathrm{last}},10^{-6})}.
```

Here $P_{b,\mathrm{last}}$ is the deepest parsed bid price used by the calculation.

Purpose: summarize quantity per visible price distance.

Limitations: nominal slope, not a fitted regression or structural liquidity model. The denominator floor dominates when distance is very small.

### 19. `slope_ask`

```math
L_a=
\frac{D_a}
{\max(P_{a,\mathrm{last}}-P_a,10^{-6})}.
```

Purpose: the equivalent quantity-per-distance measure for asks.

Limitations: same floor and model limitations as the bid measure. Incomplete parsed depth affects the distance and summed quantities.

### 20. `slope_asymmetry`

```math
A_L=
\text{clip}
\left(
\frac{L_b-L_a}{\max(L_b+L_a,10^{-6})},
-1,1
\right).
```

Purpose: compare the two nominal slopes on a normalized scale.

Limitations: not independent of the underlying quantities and distances. When both sides have equal price-distance denominators, it can coincide with deep quantity imbalance.

### 21. `micro_skew`

```math
K=
\frac{D_b-D_a}{D_b+D_a}
```

when $D_b+D_a>0$, otherwise zero.

Purpose: inspect quantity balance at levels 2–5.

Limitations: despite its name, this is not statistical skewness and does not measure a distribution's third moment.

---

## Returns and Trade Flow: Features 22–31

### 22. `return_2s`

```math
R_{2s}=
\frac{M_{i,s}-M_{i,s-20}}{M_{i,s-20}}.
```

Purpose: inspect a simple return against a 20-slot history reference.

Limitations: history slots are based on exchange depth timestamps. The value is recomputed on accepted depth updates, not continuously as wall-clock time passes. Initialization-filled and gap-filled references are possible.

### 23. `return_30s`

```math
R_{30s}=
\frac{M_{i,s}-M_{i,s-300}}{M_{i,s-300}}.
```

Purpose: provide the return reference used by cross-sectional and adjusted-return calculations.

Limitations: not a forecast. Before a complete history is observed, the reference can come from initialization. During inactivity, the exported value can remain unchanged.

### 24. `return_90s`

```math
R_{90s}=
\frac{M_{i,s}-M_{i,s-900}}{M_{i,s-900}}.
```

Purpose: inspect a longer history-grid return.

Limitations: the engine does not possess 90 seconds of observed history at startup. Gap filling is not recovery of historical market events.

All three return features are simple fractional returns, not logarithmic returns.

### 25. `current_price`

Price from the latest accepted aggregate trade message.

Purpose: inspect the last processed transaction price.

Limitations: may differ from current bid, ask, and mid. “Latest” refers to accepted local state, not a guarantee of exchange freshness.

### 26. `recent_volume_usd`

For each processed trade:

```math
n=pq.
```

Cumulative quote notional $N$ is updated, and the calculation uses its interval difference:

```math
V_k=0.95V_{k-1}+\Delta N_k.
```

Purpose: inspect decayed processed trade notional.

Limitations: not a fixed-duration volume window. The decay is per evaluation. The implementation treats a zero previous cumulative value as initialization and suppresses that corresponding first difference.

For USDT-quoted instruments, this is USDT notional despite the `_usd` identifier.

### 27. `signed_flow_usd`

Signed trade notional is:

```math
g=
\begin{cases}
-pq,&\text{buyer is maker},\\
+pq,&\text{buyer is taker}.
\end{cases}
```

With cumulative signed notional $G$:

```math
F_k=0.95F_{k-1}+\Delta G_k.
```

Purpose: inspect decayed taker-direction notional.

Limitations: not evidence of informed trading. The previous-cumulative-zero initialization rule can also activate if cumulative signed notional later returns to exactly zero, suppressing a subsequent difference.

### 28. `avg_volume_usd`

```math
A_k=0.02V_k+0.98A_{k-1}.
```

If the previous baseline is zero, it is first initialized from current $V_k$.

Purpose: a smoothed reference for the decayed volume measure.

Limitations: this smooths an already decayed quantity. It is not raw average volume over a fixed time window. Startup and zero-state handling affect early values.

### 29. `signed_flow_ratio`

```math
F^{\mathrm{ratio}}_k=
\text{clip}
\left(
\frac{F_k}{\max(V_k,10^{-8})},
-1,1
\right).
```

Purpose: normalize directional flow by the internal volume measure.

Limitations: clipping can hide discrepancies between the underlying accumulators. It is not a probability, predictive confidence, or recommendation.

### 30. `volume_burst_ratio`

```math
B_k=\frac{V_k}{\max(A_k,10^{-8})}.
```

Purpose: compare current decayed activity with its smoothed baseline.

Limitations: dependent on initialization, nested smoothing, and the denominator floor. A large value does not establish an actionable event.

### 31. `flow_toxicity`

```math
T_k=\left|F^{\mathrm{ratio}}_k\right|.
```

Purpose: inspect the magnitude of directional imbalance in the processed flow.

Limitations: not VPIN, adverse-selection probability, or a calibrated toxicity estimator.

---

## Filters and Cross-Asset Features: Features 32–40

### 32. `fast_ofi`

```math
f_k=0.10d_k+0.90f_{k-1},
\qquad d_k=\text{delta_wobi}_k.
```

Purpose: a faster exponentially weighted filter of changes in weighted book imbalance.

Limitations: not an EWMA of the imbalance level itself and not canonical Level-1 OFI. With zero input, it decays each evaluation.

### 33. `slow_ofi`

```math
g_k=0.01d_k+0.99g_{k-1}.
```

Purpose: a slower reference filter of the same net WOBI-change input.

Limitations: it does not measure “slow book imbalance” directly. It filters changes, not the WOBI level. With no new accumulated change:

```math
g_k=0.99g_{k-1}.
```

It is not canonical Level-1 OFI or a trading signal.

### 34. `delta_ofi`

```math
D^{\mathrm{filter}}_k=f_k-g_k.
```

Purpose: compare faster and slower responses to the same imbalance-change sequence.

Limitations: a difference of related filters, not an independent information source or validated momentum estimator.

### 35. `idiosyncratic_ofi`

```math
I^{\mathrm{ofi}}_{i,k}
=f_{i,k}-\beta_{i,k}f_{0,k}.
```

Purpose: explore an anchor-adjusted imbalance-filter value.

Limitations: $\beta$ is estimated from returns, not from a regression of OFI-like variables. The result is not guaranteed to be statistically orthogonal to anchor flow.

### Shared Definitions for Features 36–38

The beta calculation uses evaluation-to-evaluation stored mid-price changes:

```math
r_{i,k}=
\frac{M_{i,k}-L_{i,k}}
{\max(L_{i,k},10^{-6})}.
```

Here $L$ is the previous calculation's stored mid, with first-observation and rebase handling that can substitute the current mid and suppress a jump.

With $\lambda=0.999$:

```math
C_{i,k}=
\lambda C_{i,k-1}
+(1-\lambda)r_{i,k}r_{0,k},
```

```math
U_{i,k}=
\lambda U_{i,k-1}
+(1-\lambda)r_{i,k}^{2}.
```

These are uncentered moments: estimated means are not subtracted.

### 36. `dynamic_beta`

```math
\beta_{i,k}=
\frac{C_{i,k}}
{\max(U_{0,k},10^{-16})}.
```

Purpose: inspect the implementation's short-cadence relationship to the anchor.

Limitations: not a centered regression coefficient without further assumptions, not an optimal hedge, and not guaranteed valid at another horizon. Asynchronous updates, unchanged prices, and denominator floors influence it.

The anchor value is set to 1.0.

### 37. `beta_confidence`

Let:

```math
\widetilde U_{0,k}=\max(U_{0,k},10^{-16}).
```

Then:

```math
H_{i,k}=
\text{clip}
\left(
\frac{C_{i,k}^{2}}
{\max(U_{i,k}\widetilde U_{0,k},10^{-30})},
0,1
\right).
```

Purpose: inspect a normalized squared uncentered cross-moment diagnostic.

Limitations: not a confidence level, p-value, probability of prediction success, or generally valid centered-regression $R^2$.

Non-anchor values are suppressed while the evaluation count is below 600. The anchor is assigned 1.0 even during that period.

### 38. `beta_cov`

Exports $C_{i,k}$:

```math
C_{i,k}=0.999C_{i,k-1}+0.001r_{i,k}r_{0,k}.
```

Purpose: inspect the internal cross-moment used by beta.

Limitations: despite the name, it is not mean-centered covariance. It should not be interpreted as one without examining the assumptions.

### 39. `idiosyncratic_return`

```math
I^{\mathrm{return}}_{i,k}
=R_{30s,i}-\beta_{i,k}R_{30s,0}.
```

Purpose: inspect a heuristic anchor-adjusted return.

Limitations: applies a short-cadence coefficient to 30-second returns. It does not guarantee market neutrality, a regression residual, or a superior forecast.

The anchor value is set to zero.

### 40. `z_score_transversal`

Eligible symbols have stored mid-price greater than $10^{-6}$.

For eligible 30-second returns $R_i$:

```math
\mu=\frac{1}{n}\sum_i R_i,
```

```math
v=\frac{1}{n}\sum_i(R_i-\mu)^2,
\qquad
\sigma=\sqrt{\max(v,10^{-12})},
```

```math
z_i=\frac{R_i-\mu}{\sigma}.
```

The implementation guards the count with a minimum of one; ineligible slots receive zero.

Purpose: inspect relative return position within the configured cross-section.

Limitations: includes the anchor and can include initialized or stale returns. It is not a time-series z-score, normal-distribution probability, or calibrated outlier test. Small universes severely limit interpretation.

---

## CUSUM-Style Features: Features 41–42

Let:

- $I_{i,k}=1$ if a new accepted depth tick is available for the evaluation, otherwise 0.
- $q_{i,k}$ be the stored 100 ms history-grid return.
- $\sigma_{i,k}=\sqrt{\max(U_{i,k},10^{-12})}$.

After the initial suppression period:

### 41. `cusum_pos`

```math
S^+_{i,k}=
\max\left(
0,\,
0.985S^+_{i,k-1}
+I_{i,k}q_{i,k}
-0.5I_{i,k}\sigma_{i,k}
\right).
```

Purpose: visualize positive accumulation under this recurrence.

Limitations: not a confirmed trend, calibrated significance test, or instruction to buy.

### 42. `cusum_neg`

```math
S^-_{i,k}=
\max\left(
0,\,
0.985S^-_{i,k-1}
-I_{i,k}q_{i,k}
-0.5I_{i,k}\sigma_{i,k}
\right).
```

Purpose: visualize negative accumulation under this recurrence.

Limitations: not a prediction, calibrated significance test, or instruction to sell.

### Shared CUSUM Limitations

- Values use fractional-return units, not standard-deviation multiples.
- Existing state decays even without a new depth tick.
- New return and slack contributions are tick-gated.
- Outputs are suppressed while evaluation count is below 600.
- Detected depth-time gaps of at least 50 slots suppress the corresponding history jump return.
- The history-grid return and evaluation-to-evaluation beta return are different inputs and need not coincide.
- If multiple depth updates arrive before evaluation, the stored return is not promised to represent their complete cumulative path.

---

## Separate Header Value: `market_dispersion`

```math
\mathrm{dispersion}
=10{,}000\sqrt{\max(v,10^{-12})},
```

where $v$ is the population-style cross-sectional variance used above.

Purpose: inspect the spread of stored 30-second returns across eligible symbols.

Limitations:

- Numerical floor of approximately 0.01 bps.
- Same universe and freshness limitations as the transversal z-score.
- Read separately from the matrix, without a guarantee that it belongs to a previously returned matrix sequence.

</details>

---

## Timing, Initialization, and Statistical Limits

### Update Clocks

| Calculation | Clock |
| --- | --- |
| Quote state and spread EWMA | Accepted depth updates |
| History slots | Exchange depth timestamps divided into 100 ms slots |
| Volume and flow decay | Calculation evaluations |
| Fast and slow imbalance filters | Calculation evaluations |
| Beta moments | Calculation evaluations |
| CUSUM state decay | Calculation evaluations |

A coefficient such as 0.95 or 0.999 is per evaluation where stated, not per second.

### Startup

| Family | Startup interpretation |
| --- | --- |
| Quotes | Require accepted messages |
| Previous quotes | Require successive accepted states |
| Return history | Initially filled with the first accepted mid-price |
| Return horizons | Before the horizon is observed, references can include initialization-filled prices |
| Volume and flow | Use zero-state difference handling |
| EWMAs | Initialization-dependent; no universal convergence time |
| Non-anchor `beta_confidence` | Suppressed below 600 evaluations |
| CUSUM | Suppressed below 600 evaluations |
| Cross-sectional statistics | No separate full-history or per-symbol freshness gate |

Evaluation counts are not precise wall-clock timers.

### Gaps and Asynchronous Inputs

Missing history slots are filled using stored prices, with special handling of long gaps. This is not historical event recovery.

Asynchronous updates and unchanged values affect short-cadence cross-asset estimates.

The 42 identifiers are not 42 statistically independent information sources.

---

## Performance and Evidence — Full Product

### Author-Reported Windows Observation

Windows 11, Ryzen 7 5700G, AVX2, four symbols, approximately 35 seconds.

| Metric | Reported observation |
| --- | --- |
| Overall CPU-utilization figure | Approximately 0.1% |
| Private Working Set | Approximately 3.8 MB |
| Concurrent Python consumers exercised | Two |

These are coarse observations, not resource limits.

Private Working Set is not total process or system memory. Private Bytes are not reported.

The short observation does not establish endurance or validate every feature after its complete history horizon.

### Author-Reported Windows Microbenchmarks

Reported measurement environment: Ryzen 7 5700G, Windows 11, MSVC 19.51, `/O2 /arch:AVX2`, simdjson 3.6.3.

This historical measurement environment is distinct from the current build configuration below.

| Operation | Reported result |
| --- | ---: |
| Parse depth | Approximately 800 ns |
| Parse trade | Approximately 300 ns |
| Depth ingestion | Below 10 ns |
| Trade ingestion | Below 5 ns |
| Calculation loop | Approximately 200 ns |
| Python snapshot | Median approximately 2.7 µs; p99 approximately 4.9 µs |

The microbenchmarks use in-memory hot-cache inputs and exclude external network transit and TLS establishment.

The 200 ns result traversed 64 slots with four populated symbols and 60 zeroed slots.

Very short timings depend on timer overhead, compiler optimization, and workload.

### Existing Verification Reports

The author reports exercised cases covering:

- SIMD parity over 5,000 synthetic steps with 41 active slots and 23 zeroed slots.
- No ASan / UBSan reports in the exercised synthetic and startup/shutdown cases.
- No recorded `operator new` / `malloc` calls over 200,000 exercised synthetic hot-path iterations.
- Simulated 30-second gaps and +20 / +100 bp changes.

These reports do not establish universal correctness or independent certification.

Non-Windows verification reports do not establish a covered Linux build or equivalent Windows instrumentation.

No 24–72 hour endurance result, exhaustive finite-output validation, or completed exchange-forced 24-hour reconnection test is presented.

### Read Time Versus Data Age

Snapshot-read time is not exchange-to-consumer latency.

Data age includes exchange emission, transit, buffering, processing, evaluation scheduling, and consumer polling.

Under a uniform arrival-phase assumption, a nominal 100 ms evaluation adds approximately 50 ms on average from scheduling alone. This is illustrative, not a measured bound.

Scheduling stalls and disconnections can produce much older data.

---

## Covered Windows Build Configuration

| Component | Configuration |
| --- | --- |
| OS | Windows 11 |
| Compiler | MSVC 19.51.36260.0 |
| CMake | 4.3.4 |
| Generator | Visual Studio 18 2026 |
| Boost | 1.92.0 |
| OpenSSL | 3.6.3 |
| simdjson | 4.6.7 |
| vcpkg triplet | `x64-windows` |
| Covered target | AVX2 with FMA |
| Observed CPU | AMD Ryzen 7 5700G |

This defines the Windows configuration in the additional compilation commitment in `LICENSE`; the Ubuntu configuration is specified below.

Other Windows versions/toolchains and AVX-512 execution are outside this specified Windows configuration. The separately defined Ubuntu configuration is also covered under LICENSE Section 5.

Linux verification and the additional covered Ubuntu configuration are described below. Other Linux environments are not automatically covered.

Complete Windows and Ubuntu build instructions are supplied with the paid source-code product. Source-compilation commands are omitted from this public demo README; the covered configurations and remedy are disclosed before payment.

## Covered Ubuntu Build Configuration

| Component | Covered Ubuntu configuration |
| --- | --- |
| OS / architecture | Ubuntu 24.04 LTS, x86-64 |
| CPU target | AVX2 and FMA |
| Compiler | GCC/G++ 14.2.0 |
| CMake | 3.31.6 |
| Boost | 1.83.0 (Ubuntu package series 1.83) |
| OpenSSL | 3.0.13 (Ubuntu package series) |
| simdjson | 3.6.4 |
| Engine build | Release; `MICROFLOW_ARCH=avx2` |

Ubuntu packaging/security revisions within those same upstream version series are included. Different upstream versions, architectures, distributions, or toolchains require written agreement to be included in this additional remedy.

The full engine was built and exercised in an Ubuntu 24.04 x86-64 GitHub Actions environment using GCC 14 and Release AVX2/FMA. Its short Python integration test passed with 42 features, a 42 × 64 matrix, advancing publication sequences, finite sampled active outputs, and a healthy snapshot with positive mid-prices for six instruments.

The recorded first full-product build used Ubuntu 24.04.5 LTS, GCC 14.2.0, CMake 3.31.6, libboost-all-dev 1.83.0.1ubuntu2, libssl-dev 3.0.13-0ubuntu3.16, and libsimdjson-dev 3.6.4-1. These identify the recorded environment, not a claim that every future package update is identical.

Ubuntu is included in the additional compilation/linking remedy defined in commercial LICENSE Section 5. This is not universal Linux compatibility, an all-formulas audit, or an endurance result. Arch has not been verified.

---

## Configuration — Full Product Only

This JSON is for the paid configurable engine. The demo and its Python examples do not read `config.json`.

`ws_host` belongs at the root, not inside a `connection` object.

The supplied connection code uses port 443.

```json
{
  "ws_host": "fstream.binance.com",
  "symbols": [
    "btcusdt",
    "ethusdt",
    "solusdt",
    "xrpusdt",
    "dogeusdt",
    "bnbusdt"
  ],
  "export_features": {
    "best_bid_price": true,
    "best_bid_qty": true,
    "best_ask_price": true,
    "best_ask_qty": true,
    "prev_bid_price": true,
    "prev_bid_qty": true,
    "prev_ask_price": true,
    "prev_ask_qty": true,
    "mid_price": true,
    "micro_price": true,
    "current_spread_bps": true,
    "avg_spread_bps": true,
    "tobi": true,
    "wobi": true,
    "prev_wobi": true,
    "depth_ratio_5": true,
    "slope_bid": true,
    "slope_ask": true,
    "slope_asymmetry": true,
    "micro_skew": true,
    "delta_wobi": true,
    "return_2s": true,
    "return_30s": true,
    "return_90s": true,
    "current_price": true,
    "recent_volume_usd": true,
    "signed_flow_usd": true,
    "fast_ofi": true,
    "slow_ofi": true,
    "delta_ofi": true,
    "idiosyncratic_ofi": true,
    "z_score_transversal": true,
    "idiosyncratic_return": true,
    "dynamic_beta": true,
    "beta_confidence": true,
    "beta_cov": true,
    "cusum_pos": true,
    "cusum_neg": true,
    "avg_volume_usd": true,
    "signed_flow_ratio": true,
    "volume_burst_ratio": true,
    "flow_toxicity": true
  }
}
```

Use unique lowercase symbol names and at most 64 symbols.

Keep engine and client configuration identical, including order.

---

## Python Client — Full Product

The paid product includes its Python shared-memory client. Its engine and reader must use an identical full-product configuration, including symbol and feature ordering. The configurable full-product client and the fixed-layout demo client are not interchangeable.

Repeated sequence numbers are normal when polling faster than publication. The layout hash checks configured ordering, not authenticity or numerical correctness. Close and recreate readers after restarting the engine or changing configuration. A healthy global heartbeat does not establish freshness of every symbol.

---

## Operational and Security Notes

- The default destination is `fstream.binance.com`, port 443, using separate `/public` and `/market` combined-stream paths.
- TLS peer and hostname verification are implemented. On Windows, certificates are imported from the Windows ROOT store.
- This is not an independent application-security audit.
- The Windows mapping name is `Local\microflow_shm`.
- The writer and Python client must use the same mapping name. Changing documentation alone does not rename an existing mapping.
- The mapping uses Windows access controls, not application authentication or encryption.
- Shared memory is not an isolation boundary against other local processes with sufficient access rights.
- Run one engine instance per mapping name. Independent instances require corresponding writer and client naming changes.
- The implementation requests CPU affinity, elevated thread priority, and increased Windows timer resolution.
- Errors and warnings are written to the console.
- The supplied ingestion/client path does not require trading credentials, a wallet connection, or remote license activation.
- A healthy global heartbeat does not establish per-symbol freshness.
- Regional restrictions, DNS/firewall failures, and exchange outages are not by themselves implementation defects.
- Applications must decide how to handle stale, incomplete, nonfinite, or unsuitable data.

A binary requiring instructions unsupported by the CPU can terminate. Use the covered AVX2/FMA build on a compatible machine.

---

## Personal License and Sharing

One purchaser entity may use the Software for internal learning, research,
development and lawful trading solely for its own account.

If the purchaser is a company, fund or other organization, its employees,
contractors and collaborators may access and use the Software solely for that
organization's internal purposes. Multiple internal Python consumer processes are
permitted.

Limited examples, charts, and derived results may be shared free of charge for genuine educational explanation, subject to third-party rights.

Not permitted:

- Redistributing the engine or modified source.
- Sharing repository access outside the purchaser's authorized internal personnel.
- Use for the benefit of another entity, client, or third party.
- Commercial feeds, signal services, or output-based products.
- Operating a recurring public data service.
- Submitting proprietary source to third-party AI training or code-generation services without written permission.

The author does not claim ownership of independently created strategies, commentary, or analysis merely because the software was used.

See the commercial license v1.0.0 in `LICENSE` for the full terms.

---

## Support, Corrections, and Contributions

Contact: microflowl2@proton.me, or private GitHub Issues.

Provide:

- Version or commit.
- Environment.
- Configuration.
- Reproduction steps.
- Actual result.
- Expected behavior and reasoning.

Support covers review of reproducible:

- Compilation and linking defects in either covered configuration.
- Crashes attributable to supplied code.
- Incorrect handling of valid supported messages.
- Incorrect publication caused by implementation defects.
- Failures of documented reconnection logic attributable to supplied code.
- Suspected mathematical or documentation errors.

Confirmed defects are addressed on a best-effort basis through available v1.x corrective releases, without an additional correction fee.

This does not promise new functions, new exchanges, different models, future major versions, indefinite maintenance, or adaptation to future Binance API changes.

No resolution deadline is promised except the compilation remedy below.

Calls, screen sharing, deployment, strategy support, and server administration are not included.

Reports and suggestions are welcome. Code and documentation contributions are incorporated only after a separate written agreement on the necessary rights.

---

## Refund Policy

No voluntary change-of-mind return is offered after access begins.

The additional compilation remedy applies when:

1. Unmodified code fails to compile or link in either covered configuration.
2. The failure is reported within seven calendar days of usable repository access.
3. Sufficient reproduction information is provided.
4. The author cannot resolve the covered defect within seven calendar days after receiving sufficient reproduction information; reasonably necessary information requests pause that resolution period as specified in LICENSE Section 5.

The license payment is then refunded under the license terms.

Mandatory remedies for defective or misdescribed content remain unaffected.

Trading losses or dissatisfaction with a strategy do not by themselves establish a software defect.

---

## Price and Purchase

USD 350, one-time.

Email microflowl2@proton.me with your GitHub username and, where applicable, the
name of the purchasing entity.

Before payment, you receive the applicable README, LICENSE, and payment instructions specifying:

- Approved token contract.
- Exact token amount.
- Arbitrum One, chain ID 42161.
- Receiving address.
- Expected access-delivery period.

USDC or USDT is accepted only if its exact contract is approved in writing.

Unless agreed otherwise before payment:

- One approved token.
- One transaction.
- Full agreed amount.
- No mixed-token or split payment.
- Buyer covers sending and withdrawal fees.

The wallet address is supplied privately.

A screenshot or transaction hash alone is not proof of receipt. Delivery follows verification of recipient, token, network, amount, and finality.

Incorrect payments must be resolved before access. Recoverable funds are handled through agreed completion or return. Recovery outside the author's control is not guaranteed.

Refund destinations are confirmed separately; exchange withdrawal addresses are not used automatically.

### Acceptance

> I have received and read the README and LICENSE v1.0.0 supplied in this email thread and agree to them. I understand the commercial entity-use and output restrictions, the prohibition on redistributing source or submitting it to third-party AI services without permission, and the corrective-only maintenance scope. No financial outcome is promised. My GitHub username is [BUYER_GITHUB_USERNAME]. Purchasing entity, if applicable: [BUYER_ENTITY_NAME].

### Immediate Digital Delivery

> I expressly request immediate supply after payment verification, before any applicable cancellation period expires. Where applicable law permits, I acknowledge that my change-of-mind cancellation right is lost once supply begins. Mandatory rights concerning defective or misdescribed content remain unaffected.

The confirmation email includes the agreed documents and acknowledgments.

### Repository Access


Keep a permitted backup. Repository hosting is not guaranteed indefinitely.

---

## Work With Me

For custom C++, Unreal Engine, ingestion, SIMD, or tooling work, email microflowl2@proton.me with your problem, environment, deliverables, timeline, and budget.

Projects are assessed against skills and availability.

Custom work requires a separate written agreement and is not included in the license or support.

---

## Changelog

### v1.0.0

- Binance USD-M Futures ingestion.
- Top-five depth and aggregate trade processing.
- C++23 feature calculations.
- Compile-time AVX2 / AVX-512 paths.
- 64-symbol capacity.
- 42 selectable feature identifiers.
- Shared-memory publication and Python client.
- Configuration-layout hash checks.
- Reconnection and gap handling.
- Included benchmark and verification material.
