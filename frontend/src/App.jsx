import { useEffect, useState } from 'react'
import { Activity, AlertTriangle, CreditCard, Shield, ShieldAlert, X } from 'lucide-react'
import { api, errorMessage } from './services/api'
import Sidebar from './components/layout/Sidebar'
import Topbar from './components/layout/Topbar'
import Footer from './components/layout/Footer'
import Overview from './pages/Overview'
import FraudDetection from './pages/FraudDetection'
import BatchAnalysis from './pages/BatchAnalysis'
import Transactions from './pages/Transactions'
import Analytics from './pages/Analytics'
import ModelPerformance from './pages/ModelPerformance'
import Settings from './pages/Settings'

const featureDefaults = Object.fromEntries(['Time', ...Array.from({length:28}, (_,i)=>`V${i+1}`), 'Amount'].map(x=>[x, '0']))

export default function App() {
  const [page, setPage] = useState('Overview'), [dark, setDark] = useState(true), [mobile, setMobile] = useState(false)
  const [stats, setStats] = useState(null), [history, setHistory] = useState([]), [models, setModels] = useState([]), [metrics, setMetrics] = useState(null), [trends, setTrends] = useState([]), [amounts, setAmounts] = useState([])
  const [health, setHealth] = useState(null), [busy, setBusy] = useState(false), [error, setError] = useState(''), [prediction, setPrediction] = useState(null)
  const [form, setForm] = useState(featureDefaults), [batch, setBatch] = useState(null), [search, setSearch] = useState('')
  const refresh = async () => {
    setError('')
    const results = await Promise.allSettled([api.get('/dashboard/stats'), api.get('/transactions?limit=100'), api.get('/models'), api.get('/models/metrics'), api.get('/analytics/fraud-trends'), api.get('/health'), api.get('/analytics/amounts')])
    if (results[0].status==='fulfilled') setStats(results[0].value.data)
    if (results[1].status==='fulfilled') setHistory(results[1].value.data)
    if (results[2].status==='fulfilled') setModels(results[2].value.data)
    if (results[3].status==='fulfilled') setMetrics(results[3].value.data)
    if (results[4].status==='fulfilled') setTrends(results[4].value.data)
    if (results[5].status==='fulfilled') setHealth(results[5].value.data)
    if (results[6].status==='fulfilled') setAmounts(results[6].value.data)
  }
  useEffect(()=>{refresh()},[])
  const submit = async e => { e.preventDefault(); setBusy(true); setError(''); setPrediction(null); try { const {data}=await api.post('/predict', Object.fromEntries(Object.entries(form).map(([k,v])=>[k,Number(v)]))); setPrediction(data); refresh() } catch(e){setError(errorMessage(e))} finally{setBusy(false)} }
  const upload = async e => { const file=e.target.files?.[0]; if(!file)return; setBusy(true); setError(''); try {const {data}=await api.post('/predict/batch', (()=>{const f=new FormData();f.append('file',file);return f})(),{responseType:'blob'});setBatch({blob:data,name:file.name});refresh()}catch(e){setError(e.response?.data?.detail||'Batch prediction failed. Verify CSV columns and API availability.')}finally{setBusy(false);e.target.value=''} }
  const download = () => {if(!batch)return;const url=URL.createObjectURL(batch.blob), a=document.createElement('a');a.href=url;a.download='fraud_predictions.csv';a.click();URL.revokeObjectURL(url)}
  const filtered = history.filter(t=>`${t.transaction_reference} ${t.risk_level}`.toLowerCase().includes(search.toLowerCase()))
  const pie = [{name:'Legitimate',value:stats?.legitimate_transactions||0,color:'#62e6bd'},{name:'Fraud',value:stats?.fraud_detected||0,color:'#ff6b78'}]
  const metricCards=[['Total transactions',stats?.total_transactions||0,'Across scored history',CreditCard],['Fraud detected',stats?.fraud_detected||0,'Flagged by active model',ShieldAlert],['Legitimate',stats?.legitimate_transactions||0,'Cleared transactions',Shield],['Avg. fraud probability',`${((stats?.average_fraud_probability||0)*100).toFixed(1)}%`,'Across all predictions',Activity]]
  return <div className={`shell ${dark?'dark':'light'}`}>
    <Sidebar mobile={mobile} page={page} setPage={setPage} setMobile={setMobile} health={health}/>
    {mobile&&<button className="scrim" onClick={()=>setMobile(false)} aria-label="Close menu"/>}
    <main className="main">
      <Topbar page={page} search={search} setSearch={setSearch} dark={dark} setDark={setDark} setMobile={setMobile}/>
      <div className="content">
        {error&&<div className="alert"><AlertTriangle size={17}/>{error}<button onClick={()=>setError('')}><X size={16}/></button></div>}
        {page==='Overview'&&<Overview metricCards={metricCards} refresh={refresh} trends={trends} stats={stats} pie={pie} history={history} setPage={setPage} health={health} amounts={amounts}/>}
        {page==='Fraud Detection'&&<FraudDetection form={form} setForm={setForm} busy={busy} health={health} submit={submit} prediction={prediction}/>}
        {page==='Batch Analysis'&&<BatchAnalysis busy={busy} upload={upload} batch={batch} download={download}/>}
        {page==='Transactions'&&<Transactions refresh={refresh} filtered={filtered} search={search} setSearch={setSearch}/>}
        {page==='Analytics'&&<Analytics metricCards={metricCards} trends={trends}/>}
        {page==='Model Performance'&&<ModelPerformance metrics={metrics}/>}
        {page==='Settings'&&<Settings health={health} dark={dark} setDark={setDark}/>}
        <Footer/>
      </div>
    </main>
  </div>
}

