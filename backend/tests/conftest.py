import sys
import os
import tempfile
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "backend"))
os.environ["FRAUD_DATABASE_URL"] = f"sqlite:///{Path(tempfile.gettempdir()) / f'fraud-api-tests-{os.getpid()}.db'}"
