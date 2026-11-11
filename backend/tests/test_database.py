from uuid import uuid4
from app.db.database import Base, SessionLocal, engine
from app.db.models import PredictionLog, Transaction

def test_transaction_and_prediction_log_persist_together():
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as session:
        record=Transaction(transaction_reference=str(uuid4()), transaction_amount=25.5, transaction_time=100,
                           predicted_class=1, fraud_probability=.91, risk_level="HIGH RISK")
        session.add(record); session.flush()
        session.add(PredictionLog(transaction_id=record.id, prediction_status="success", processing_time=.02))
        session.commit(); session.refresh(record)
        assert record.prediction_log.prediction_status=="success"
        assert record.transaction_amount==25.5
        session.delete(record); session.commit()
