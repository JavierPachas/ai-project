# ai-project

A fantasy-football **player acquisition cost** predictor, served as a REST API, plus a **LangGraph agent** that can reason over live league/team data through a custom tool kit.

The project has two cooperating halves:

1. **Model + API** — quantile regression models (trained in scikit-learn, exported to ONNX) served behind a FastAPI app that predicts the likely *winning bid range* to acquire a player.
2. **Agent** — a LangGraph + Claude agent wired to a `SportsWorldCentral` toolkit, able to look up leagues and teams via the `swcpy` SDK.

---

## What it does

Given three features about a waiver/auction situation, the API returns a **range** of likely acquisition costs as three percentiles (10th / 50th / 90th), so you can see not just a point estimate but the spread.

**Input** (`FantasyAcquisitionFeatures`):

| Field | Type | Meaning |
|---|---|---|
| `waiver_value_tier` | int | Tier representing the player's perceived value |
| `fantasy_regular_season_weeks_remaining` | int | Weeks left in the regular season |
| `league_budget_pct_remaining` | int | Percent of auction/FAAB budget still available |

**Output** (`PredictionOutput`):

| Field | Type | Meaning |
|---|---|---|
| `winning_bid_10th_percentile` | float | Low-end estimate |
| `winning_bid_50th_percentile` | float | Median estimate |
| `winning_bid_90th_percentile` | float | High-end estimate |

Three separate ONNX models back these percentiles (`acquisition_model_10.onnx`, `acquisition_model_50.onnx`, `acquisition_model_90.onnx`).

---

## Tech stack

- **Modeling:** scikit-learn, skl2onnx, ONNX Runtime, NumPy, pandas
- **API:** FastAPI, Uvicorn, Pydantic v2
- **Agent:** LangGraph, LangChain Core, `langchain-anthropic` (Claude), a custom `BaseToolkit`
- **External SDK:** `swcpy` (SportsWorldCentral client)

---

## Repository layout

```
ai-project/
├── main.py                               # FastAPI app: /health + /predict
├── schemas.py                            # Pydantic request/response models
├── swc_toolkit.py                        # LangChain toolkit wrapping the swcpy SDK
├── models/                               # Exported ONNX models (10th/50th/90th)
├── data/                                 # Training / reference data
├── player_acquisition_model.ipynb        # Train models + export to ONNX
├── langgraph_notebook.ipynb              # Minimal LangGraph + Claude agent
├── langgraph_notebook_with_toolkit.ipynb # Agent using the SWC toolkit
├── requirements.txt
└── LICENSE                               # MIT
```

---

## Getting started

### 1. Prerequisites

- Python 3.12
- An Anthropic API key (for the agent notebooks)
- Access to a running SportsWorldCentral API (for the toolkit) and the `swcpy` SDK

### 2. Install

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

The `swcpy` SDK is not on PyPI; install it from its source repository, e.g.:

```bash
pip install "swcpy @ git+https://github.com/JavierPachas/portfolio-project.git#subdirectory=sdk"
```

### 3. Configure environment

Create a `.env` file in the project root (**do not commit it** — see Security note):

```dotenv
ANTHROPIC_API_KEY=sk-ant-...
SWC_API_BASE_URL=http://127.0.0.1:8000
```

---

## Running the API

```bash
uvicorn main:app --reload
```

Then open the interactive docs at `http://127.0.0.1:8000/docs`.

**Health check**

```bash
curl http://127.0.0.1:8000/
# {"message":"API health check successful"}
```

**Predict**

```bash
curl -X POST http://127.0.0.1:8000/predict/ \
  -H "Content-Type: application/json" \
  -d '{
    "waiver_value_tier": 3,
    "fantasy_regular_season_weeks_remaining": 8,
    "league_budget_pct_remaining": 60
  }'
```

Response:

```json
{
  "winning_bid_10th_percentile": 12.0,
  "winning_bid_50th_percentile": 24.5,
  "winning_bid_90th_percentile": 41.0
}
```

---

## The agent

`swc_toolkit.py` exposes a `SportsWorldCentralToolkit` with three tools the agent can call:

- **HealthCheck** — confirm the SWC API is up before making other calls
- **ListLeagues** — list leagues (optionally filtered by name)
- **ListTeams** — list teams (optionally filtered by team name and/or numerical league ID)

The agent itself is a standard LangGraph loop (`agent` node ↔ `tools` node) using Claude via `ChatAnthropic`. See `langgraph_notebook_with_toolkit.ipynb` for the full wiring; `langgraph_notebook.ipynb` is a simpler starting point.

```python
from swc_toolkit import SportsWorldCentralToolkit

toolkit = SportsWorldCentralToolkit()
tools = toolkit.get_tools()
# bind to a ChatAnthropic model, compile a LangGraph StateGraph, then invoke
```

---

## Retraining the models

Open `player_acquisition_model.ipynb` to retrain the quantile models and re-export them to ONNX into `models/`. The API loads those `.onnx` files at startup, so re-exporting is all that's needed to update predictions.

---

## License

MIT © 2026 Javier Pachas. See [LICENSE](LICENSE).
