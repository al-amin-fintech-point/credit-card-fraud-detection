import { Shield, ShieldAlert } from 'lucide-react'
import { EmptyChart } from '../common/EmptyChart'

export default function PredictionResult({ prediction }) {
  return (
    <section className="card result-card"><div className="cardhead"><div><h2>Prediction result</h2><p>Risk assessment appears here</p></div></div>{prediction?<div className="result-body"><div className={`result-badge ${prediction.predicted_class?'risk':'safe'}`}>{prediction.predicted_class?<ShieldAlert size={21}/>:<Shield size={21}/>} {prediction.predicted_class?'Potential fraud':'Likely legitimate'}</div><div className="probability"><div><span>Fraud probability</span><b>{(prediction.fraud_probability*100).toFixed(2)}%</b></div><div className="progress"><i style={{width:`${prediction.fraud_probability*100}%`}}/></div><div className="risk-line"><span>Risk level</span><b>{prediction.risk_level}</b></div><div className="risk-line"><span>Model version</span><b>{prediction.model_version}</b></div><div className="risk-explain">This is a predictive signal. Use your established review workflow before making a financial decision.</div></div></div>:<EmptyChart text="Run an analysis to see the probability and risk assessment."/>}</section>
  )
}

