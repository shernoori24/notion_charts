import React, { useRef, useEffect } from 'react'
import * as d3 from 'd3'

export default function Chart({ data, type, xKey: propX, yKey: propY }) {
  const ref = useRef()

  useEffect(() => {
    const container = ref.current
    if (!container) return

    console.log('Chart re-rendering with:', { dataLen: data?.length, type, propX, propY })

    // Clear previous
    container.innerHTML = ''

    if (!data || data.length === 0) {
      container.innerHTML = '<p>No data</p>'
      return
    }

    // Select X/Y keys: prefer props (selected by user), otherwise auto-detect
    const sample = data[0]
    const keys = Object.keys(sample)
    const xKey = propX || keys.find(k => typeof sample[k] === 'string') || keys[0]
    const yKey = propY || keys.find(k => typeof sample[k] === 'number') || keys.find(k => !isNaN(Number(sample[k])))
    if (!yKey) {
      container.innerHTML = '<p>No numeric column found for Y-axis</p>'
      return
    }

    // Robust parsing for Y values which might be strings with currency/commas
    const parseY = (val) => {
      if (val === null || val === undefined) return NaN
      if (typeof val === 'number') return val
      if (typeof val !== 'string') return NaN
      // Remove currency symbols ($), commas, and spaces
      const clean = val.replace(/[$,\s]/g, '')
      return parseFloat(clean)
    }

    // Transform data to x/y and filter out invalid Y values
    const d = data
      .map(row => ({ x: row[xKey], y: parseY(row[yKey]) }))
      .filter(item => !isNaN(item.y))

    if (d.length === 0) {
      container.innerHTML = `<p>No valid numeric data found for column "${yKey}"</p>`
      console.warn(`Chart.jsx: Dropped all rows. Y-column "${yKey}" contains non-numeric data.`)
      return
    }

    const width = 800, height = 400, margin = { top: 20, right: 20, bottom: 80, left: 60 }

    console.log('D3 rendering with valid data:', d.length, d[0])

    const svg = d3.select(container).append('svg').attr('width', width).attr('height', height)
    if (type === 'Bar') {
      const x = d3.scaleBand().domain(d.map(d => d.x)).range([margin.left, width - margin.right]).padding(0.1)
      console.log('Rendering Bar chart with data sample:', d.slice(0, 3));
      const minVal = d3.min(d, dd => dd.y)
      const maxVal = d3.max(d, dd => dd.y)
      const y = d3.scaleLinear().domain([Math.min(0, minVal), Math.max(0, maxVal)]).nice().range([height - margin.bottom, margin.top])

      svg.append('g').attr('fill', '#4c78a8')
        .selectAll('rect').data(d).join('rect')
        .attr('x', dd => x(dd.x))
        .attr('y', dd => dd.y > 0 ? y(dd.y) : y(0))
        .attr('height', dd => {
          const h = Math.abs(y(dd.y) - y(0));
          return isNaN(h) ? 0 : h;
        })
        .attr('width', x.bandwidth())

      svg.append('g').attr('transform', `translate(0,${height - margin.bottom})`)
        .call(d3.axisBottom(x)).selectAll('text').attr('transform', 'rotate(-45)').style('text-anchor', 'end')

      svg.append('g').attr('transform', `translate(${margin.left},0)`).call(d3.axisLeft(y))
    } else if (type === 'Line') {
      const x = d3.scalePoint().domain(d.map(d => d.x)).range([margin.left, width - margin.right])
      const minVal = d3.min(d, dd => dd.y)
      const maxVal = d3.max(d, dd => dd.y)
      const y = d3.scaleLinear().domain([Math.min(0, minVal), Math.max(0, maxVal)]).nice().range([height - margin.bottom, margin.top])

      const line = d3.line().x(dd => x(dd.x)).y(dd => y(dd.y))
      svg.append('path').datum(d).attr('fill', 'none').attr('stroke', '#ff7f0e').attr('stroke-width', 2).attr('d', line)

      svg.append('g').attr('transform', `translate(0,${height - margin.bottom})`).call(d3.axisBottom(x)).selectAll('text').attr('transform', 'rotate(-45)').style('text-anchor', 'end')
      svg.append('g').attr('transform', `translate(${margin.left},0)`).call(d3.axisLeft(y))
    } else if (type === 'Pie') {
      const radius = Math.min(width, height) / 2 - 20
      const g = svg.append('g').attr('transform', `translate(${width / 2},${height / 2})`)
      const pie = d3.pie().value(d => d.y)(d)
      const arc = d3.arc().innerRadius(0).outerRadius(radius)
      const color = d3.scaleOrdinal(d3.schemeTableau10)
      g.selectAll('path').data(pie).join('path').attr('d', arc).attr('fill', (d, i) => color(i)).attr('stroke', 'white')
    }

    // Verify container dimensions
    const rect = container.getBoundingClientRect()
    console.log('Chart container dimensions:', rect)

  }, [data, type, propX, propY])

  return <div ref={ref} style={{ border: '2px solid red', minHeight: '400px', padding: '10px' }}></div>
}
