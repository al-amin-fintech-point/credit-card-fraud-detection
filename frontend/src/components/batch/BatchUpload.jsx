import { Check, Download, FileUp, Upload } from 'lucide-react'

export default function BatchUpload({ busy, upload, batch, download }) {
  return (
    <section className="card upload-card"><div className="upload-zone"><div className="upload-icon"><Upload size={22}/></div><h2>Upload transaction file</h2><p>CSV only · Maximum 10 MB · Required columns: Time, V1–V28, Amount</p><label className="btn primary file-button"><FileUp size={16}/>{busy?'Processing...':'Choose CSV file'}<input type="file" accept=".csv,text/csv" onChange={upload} disabled={busy}/></label><small>Your file is processed for predictions and not saved as an uploaded file.</small></div>{batch&&<div className="batch-success"><div><Check size={18}/><b>Batch complete</b><span>Prediction results are ready to download.</span></div><button className="btn secondary" onClick={download}><Download size={16}/> Download results</button></div>}</section>
  )
}

