import { EmptyChart } from '../common/EmptyChart'

const money = n => new Intl.NumberFormat('en-US',{maximumFractionDigits:2}).format(n || 0)

export function TransactionTable({items}){return <div className="table-wrap">{items.length?<table><thead><tr><th>REFERENCE</th><th>AMOUNT</th><th>DECISION</th><th>PROBABILITY</th><th>RISK</th><th>TIME</th></tr></thead><tbody>{items.map(t=><tr key={t.id}><td className="ref">{t.transaction_reference.slice(0,13)}…</td><td>{money(t.transaction_amount)}</td><td><span className={`decision ${t.predicted_class?'fraud':'legit'}`}><i/>{t.predicted_class?'Fraud flagged':'Legitimate'}</span></td><td>{(t.fraud_probability*100).toFixed(2)}%</td><td><span className={`risk-pill ${t.risk_level.toLowerCase().replace(' ','-')}`}>{t.risk_level}</span></td><td className="muted">{new Date(t.created_at).toLocaleString()}</td></tr>)}</tbody></table>:<EmptyChart text="No transactions saved yet. Run a prediction to populate history."/>}</div>}
