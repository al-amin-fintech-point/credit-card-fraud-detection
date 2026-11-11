import { CircleHelp, Fingerprint } from 'lucide-react'

export default function PredictionForm({ form, setForm, busy, health, submit }) {
  return (
    <section className="card form-card"><div className="cardhead"><div><h2>Transaction details</h2><p>Enter Time, Amount, and PCA features V1–V28.</p></div><span className="required">30 FEATURES</span></div><form onSubmit={submit}><div className="basic-fields"><label>Transaction time (seconds)<input type="number" min="0" step="any" value={form.Time} onChange={e=>setForm({...form,Time:e.target.value})}/></label><label>Transaction amount<input type="number" min="0" step="any" value={form.Amount} onChange={e=>setForm({...form,Amount:e.target.value})}/></label></div><details className="feature-details"><summary>Advanced PCA features <span>V1 to V28</span></summary><div className="feature-grid">{Array.from({length:28},(_,i)=>`V${i+1}`).map(k=><label key={k}>{k}<input type="number" step="any" value={form[k]} onChange={e=>setForm({...form,[k]:e.target.value})}/></label>)}</div></details><div className="form-foot"><small><CircleHelp size={14}/> Prediction is a model estimate, not a guaranteed financial decision.</small><button className="btn primary" disabled={busy||!health?.model_available}><Fingerprint size={16}/>{busy?'Scoring...':'Analyze transaction'}</button></div>{!health?.model_available&&<p className="muted-callout">Train and load a model before scoring. See the README dataset and training steps.</p>}</form></section>
  )
}

