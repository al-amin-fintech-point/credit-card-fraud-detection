import BatchUpload from '../components/batch/BatchUpload'

export default function BatchAnalysis({ busy, upload, batch, download }) {
  return (
    <><div className="pagehead"><div><div className="eyebrow">BULK SCREENING</div><h1>Batch analysis</h1><p>Score up to 10,000 anonymized transactions from a CSV.</p></div></div><BatchUpload busy={busy} upload={upload} batch={batch} download={download}/><section className="card guide-card"><h2>CSV format</h2><p>The header must include the Kaggle feature names exactly. Each row must contain finite numeric values; transaction time and amount must be non-negative.</p><code>Time,V1,V2,...,V28,Amount</code></section></>
  )
}

