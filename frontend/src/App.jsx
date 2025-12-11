import React, {useState, useEffect} from 'react'
import Chart from './components/Chart'

export default function App(){
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(false)
  const [chartType, setChartType] = useState('Bar')

  const fetchData = async () =>{
    setLoading(true)
    try{
      const res = await fetch('/api/data')
      const json = await res.json()
      setData(json.results)
    }catch(err){
      console.error(err)
      alert('Failed to fetch data: ' + err.message)
    }finally{
      setLoading(false)
    }
  }

  useEffect(()=>{
    fetchData()
  },[])

  return (
    <div className="container">
      <header>
        <h1>Notion Charts (React + D3)</h1>
        <div className="controls">
          <select value={chartType} onChange={e=>setChartType(e.target.value)}>
            <option>Bar</option>
            <option>Line</option>
            <option>Pie</option>
          </select>
          <button onClick={fetchData} disabled={loading}>{loading? 'Refreshing...':'Refresh data'}</button>
        </div>
      </header>

      <main>
        <section>
          <h2>Data</h2>
          <pre style={{maxHeight:200, overflow:'auto'}}>{JSON.stringify(data.slice(0,20), null, 2)}</pre>
        </section>
        <section>
          <h2>Chart</h2>
          <Chart data={data} type={chartType} />
        </section>
      </main>
    </div>
  )
}
