# Credit Card Fraud Detection

An end-to-end transaction fraud scoring system with a leakage-conscious model training pipeline, FastAPI prediction service, PostgreSQL persistence, and a React dashboard. It is designed to run on the public Kaggle Credit Card Fraud Detection dataset. **No dataset, trained model, or metric is bundled.** Predictions remain unavailable until a model is trained from the real Kaggle CSV.

## Features

- Dataset schema, numeric value, target, missing-value, and duplicate validation.
- EDA charts written to `artifacts/eda/` from the supplied real dataset.
- Stratified train/validation/test splitting before fitting transformations or models; exact duplicate rows are removed before splitting.
- Standard scaling of `Amount`; already PCA-transformed `V1`–`V28` features pass through unchanged; `Time` remains numeric.
- Logistic Regression, Decision Tree, Random Forest, and XGBoost comparison with imbalance-aware class weighting; logistic regression also compares random undersampling and SMOTE.
- Model selection by validation PR-AUC, with validation F1 used to set the decision threshold; final metrics are computed on a held-out test set.
- FastAPI endpoints for health, statistics, single and batch predictions, model information, trends, history, and authorized retraining.
- PostgreSQL/SQLAlchemy models and Alembic migration. SQLite is the local development default.
- Responsive dashboard with overview, transaction analysis, CSV scoring/download, history, analytics, and performance views.
- Synthetic fixtures are used only in unit tests. They are never used for fitting deliverable artifacts or reporting performance.

## Architecture

```text
Browser (React + Vite + Recharts)
             │ REST / JSON + CSV
             ▼
FastAPI ─ PredictionService ─ saved sklearn/XGBoost pipeline
   │                         ▲
   └─ SQLAlchemy ─ PostgreSQL │
                             │ train.py
 Kaggle CSV → validation → EDA → stratified splits → compare → artifacts
```

The backend lives in `backend/app/`; ML workflows are in `backend/app/ml/`. The frontend is in `frontend/`. Data, model artifacts, generated charts, secrets, databases, and dependency folders are excluded from Git.

## Requirements

- Python 3.12 recommended (Docker image uses Python 3.12). The inspected host has Python 3.14; compatibility of the full scientific stack is not verified on that interpreter.
- Node.js 20+ and npm.
- PostgreSQL 15+ for persistent deployment (optional for local SQLite development).
- Docker Engine and Docker Compose plugin for containerized startup.
- Kaggle account and the `mlg-ulb/creditcardfraud` dataset.

## Dataset setup

Download `creditcard.csv` from [Kaggle: Credit Card Fraud Detection](https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud) and place it at `data/raw/creditcard.csv`:

```bash
cd /home/alamin/Ml-Project/credit-card-fraud-detection
mkdir -p data/raw
# After downloading via the Kaggle website:
cp ~/Downloads/creditcard.csv data/raw/creditcard.csv
```

Alternatively, with Kaggle CLI already configured:

```bash
kaggle datasets download -d mlg-ulb/creditcardfraud -p /tmp/credit-card-fraud
unzip /tmp/credit-card-fraud/creditcardfraud.zip -d data/raw
```

The expected CSV has `Time`, `V1` through `V28`, `Amount`, and `Class`; `Class` must be binary. The loader rejects missing/non-numeric values and negative time/amount. It reports duplicate rows; training removes exact duplicate records. Never place real data in source control.

## Local setup

Commands below assume the project root is the current directory. For a Python 3.12 virtual environment:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

On Ubuntu/Debian, install Python and venv support if needed:

```bash
sudo apt update
sudo apt install python3.12 python3.12-venv python3.12-dev build-essential
```

This project was created with a private `.venv`; it does not modify other project environments or system Python packages. If Python 3.12 is unavailable, install it alongside the system interpreter or use Docker; do not replace `/usr/bin/python3`.

## Train and inspect

Training requires the real dataset. It writes EDA images, an actual trained Joblib pipeline, its fitted preprocessing transformer, active metadata, and evaluation JSON. It never fabricates a fallback dataset or metrics.

```bash
source .venv/bin/activate
python scripts/train.py
```

Splits use stratification: 70% training, 15% validation, and 15% test (approximately; stratification preserves class proportions). Candidate models fit only on the training split. The validation set ranks PR-AUC and selects the F1-maximizing decision threshold. The selected estimator is refit on train plus validation, then evaluated once on the untouched test set. `artifacts/models/metrics.json` stores validation comparisons and the held-out test report; `artifacts/eda/` stores class balance, amount/time distributions, fraud amounts, correlation, percentage, and PCA feature plots.

All numeric inputs, including `Time`, the PCA components, and `Amount`, are standardized inside the fitted pipeline. This improves Logistic Regression convergence and makes SMOTE distance calculations meaningful; scaling is fitted on training rows only. Tree models are invariant to monotonic scaling. Class imbalance is handled using class weighting (`scale_pos_weight` for XGBoost); logistic regression additionally compares random undersampling and SMOTE. Resampling is contained in the imbalanced-learn training pipeline and occurs only after the training split is established. SMOTEENN is not added without evidence that the more complex strategy improves validation results. The saved threshold and high-risk cutoff are operational starting points and should be tuned using business review capacity, calibration, and prospective data before real decisions.

## Backend

Configure settings via `.env` (copy from `.env.example`). Defaults use local SQLite and model/data paths under the project.

```bash
cp .env.example .env
# Adjust FRAUD_DATABASE_URL as required.
export PYTHONPATH="$PWD/backend"
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

Swagger UI: <http://localhost:8000/docs> (ReDoc: `/redoc`). Health check: `/api/v1/health`. An absent model is reported clearly; scoring returns HTTP 503 until training creates artifacts.

### API endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/v1/health` | API and model availability |
| GET | `/api/v1/dashboard/stats` | Prediction counts and average probability |
| POST | `/api/v1/predict` | Score one JSON transaction (`Time`, `V1`…`V28`, `Amount`) |
| POST | `/api/v1/predict/batch` | Upload CSV; returns prediction CSV (10 MB and 10,000 rows max by default) |
| GET | `/api/v1/transactions` | Paginated prediction history |
| GET | `/api/v1/transactions/{id}` | One history record |
| GET | `/api/v1/models` | Stored model versions |
| GET | `/api/v1/models/metrics` | Training report, validation comparison, test metrics |
| GET | `/api/v1/analytics/fraud-trends` | Counts grouped by prediction date |
| GET | `/api/v1/analytics/amounts` | Transaction counts and fraud flags grouped by amount range |
| POST | `/api/v1/model/retrain` | Retrain from configured dataset; requires `X-Admin-Key` |

Example single prediction (after training):

```bash
python - <<'PY' > /tmp/transaction.json
import json
print(json.dumps({"Time": 1000, "Amount": 12.5, **{f"V{i}": 0 for i in range(1, 29)}}))
PY
curl -sS -X POST http://localhost:8000/api/v1/predict -H 'Content-Type: application/json' --data-binary @/tmp/transaction.json
```

Batch CSV headers must include the exact feature names. Results include original features and prediction class, probability, risk, model version, and generated transaction reference. Stored database records intentionally omit all PCA input values and any cardholder/card credentials; only amount, time, and score metadata are retained. Logs do not include request feature values. Set a strong `FRAUD_ADMIN_API_KEY` before enabling retraining; requests are rejected when no key is configured.

## Frontend

```bash
cd frontend
npm install
npm run dev
```

Open <http://localhost:5173>. Set `VITE_API_URL` to the API base URL when it is hosted elsewhere. `npm run build` creates a production static bundle. The dashboard adapts to narrow screens and supports light/dark themes.

## PostgreSQL

Set `FRAUD_DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST:5432/DB` in `.env`, then run `alembic upgrade head`. Tables are `transactions`, `model_versions`, and `prediction_logs`. The app calls `create_all` at startup as a convenience for local SQLite; Alembic remains the schema upgrade mechanism for deployments.

## Tests

```bash
source .venv/bin/activate
pytest -q backend/tests
```

Tests cover data loading/validation, preprocessing, training/artifact persistence, model availability/risk behavior, database persistence, and API health/stats/validation/batch behavior. Fixtures are tiny synthetic rows solely for tests and are not training data. Install all project requirements before running the suite; the API and training modules skip when their optional runtime dependencies are missing.

## Docker Compose

Install Docker Engine and the Compose plugin, then from project root:

```bash
cp .env.example .env
# In .env, set a unique POSTGRES_PASSWORD in the shell environment and a strong FRAUD_ADMIN_API_KEY.
export POSTGRES_PASSWORD='replace-with-a-long-random-value'
export FRAUD_ADMIN_API_KEY='replace-with-a-separate-long-random-value'
docker compose up --build
```

Open dashboard at <http://localhost:8080> and API docs at <http://localhost:8000/docs>. Stop with `docker compose down`; add `-v` only when intentionally deleting PostgreSQL data. Place the dataset under `data/raw/` and retrain within the API container only after authorized setup, or run `docker compose exec api python scripts/train.py`. Container images and migrations are configured for Python 3.12 and PostgreSQL 16.

## Limitations and future work

- The original dataset is not present in this workspace, so no trained artifact, EDA output, model comparison, or genuine metric exists yet. Run the commands above with the real Kaggle file to produce them.
- Kaggle data is historical and anonymized; performance does not establish suitability for live payment decisions. Validate on time-based/prospective data, calibrate probabilities, monitor drift, review false positives and false negatives, and obtain domain/compliance review.
- Current training split is stratified random rather than temporal; time-based evaluation is a recommended follow-up for deployment realism.
- Batch work is synchronous; large-scale jobs should move to a queued worker. Authentication is implemented only for model retraining; add user authentication, authorization, TLS, rate limits, and operational secret management before deployment.
- No card number, CVV, PIN, or full input feature vector is stored. This is not a guarantee of production readiness.

## Screenshots

Add deployment screenshots here after running with a trained model and representative, non-sensitive data.
