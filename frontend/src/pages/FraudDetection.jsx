import PredictionForm from '../components/fraud/PredictionForm'
import PredictionResult from '../components/fraud/PredictionResult'

export default function FraudDetection({ form, setForm, busy, health, submit, prediction }) {
  return (
    <><div className="pagehead"><div><div className="eyebrow">TRANSACTION SCORING</div><h1>Fraud detection</h1><p>Submit anonymized transaction features for a model risk score.</p></div></div><div className="detect-layout"><PredictionForm form={form} setForm={setForm} busy={busy} health={health} submit={submit}/><PredictionResult prediction={prediction}/></div></>
  )
}

