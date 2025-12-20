import React, { useState, useEffect } from 'react'
import Chart from './components/Chart'

export default function App() {
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(false)
  const [chartType, setChartType] = useState('Bar')
  const [columns, setColumns] = useState([])
  const [xKey, setXKey] = useState(null)
  const [yKey, setYKey] = useState(null)

  const fetchData = async () => {
    setLoading(true)
    try {
      const res = await fetch('/api/data')
      const json = await res.json()
      setData(json.results)
      if (json.results && json.results.length > 0) {
        const cols = Object.keys(json.results[0])
        setColumns(cols)
        setXKey(cols.find(k => typeof json.results[0][k] === 'string') || cols[0])
        setYKey(cols.find(k => typeof json.results[0][k] === 'number') || cols.find(k => !isNaN(Number(json.results[0][k]))))
      }
    } catch (err) {
      console.error(err)
      alert('Failed to fetch data: ' + err.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
  }, [])

  return (
    <div className="container">
      <header>
        <h1>Notion Charts (React + D3)</h1>
        <div className="controls">
          <select value={chartType} onChange={e => setChartType(e.target.value)}>
            <option>Bar</option>
            <option>Line</option>
            <option>Pie</option>
          </select>
          <select value={xKey || ''} onChange={e => setXKey(e.target.value)}>
            <option value="" disabled>Choose X</option>
            {columns.map(c => <option key={c} value={c}>{c}</option>)}
          </select>
          <select value={yKey || ''} onChange={e => setYKey(e.target.value)}>
            <option value="" disabled>Choose Y</option>
            {columns.map(c => <option key={c} value={c}>{c}</option>)}
          </select>
          <button onClick={() => {
            const csv = convertToCSV(data)
            const blob = new Blob([csv], { type: 'text/csv' })
            const url = URL.createObjectURL(blob)
            const a = document.createElement('a')
            a.href = url
            a.download = 'notion_data.csv'
            a.click()
            URL.revokeObjectURL(url)
          }}>Export CSV</button>
          <button onClick={fetchData} disabled={loading}>{loading ? 'Refreshing...' : 'Refresh data'}</button>
        </div>
      </header>

      <main>
        <section>
          <h2>Data</h2>
          <pre style={{ maxHeight: 200, overflow: 'auto' }}>{JSON.stringify(data.slice(0, 20), null, 2)}</pre>
        </section>
        <section>
          <h2>Chart</h2>
          <Chart data={data} type={chartType} xKey={xKey} yKey={yKey} />
        </section>
      </main>
    </div>
  )
}

function convertToCSV(arr) {
  if (!arr || arr.length === 0) return ''
  const keys = Object.keys(arr[0])
  const header = keys.join(',')
  const rows = arr.map(r => keys.map(k => escapeCSV(r[k])).join(','))
  return [header].concat(rows).join('\n')
}

function escapeCSV(v) {
  if (v === null || v === undefined) return ''
  const s = String(v).replace(/"/g, '""')
  if (s.indexOf(',') >= 0 || s.indexOf('\n') >= 0) return '"' + s + '"'
  return s
}
