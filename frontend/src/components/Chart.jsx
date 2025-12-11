import React, {useRef, useEffect} from 'react'
import * as d3 from 'd3'

export default function Chart({data, type, xKey: propX, yKey: propY}){
  const ref = useRef()

  useEffect(()=>{
    const container = ref.current
    if(!container) return
    // Clear previous
    container.innerHTML = ''

    if(!data || data.length===0) {
      container.innerHTML = '<p>No data</p>'
      return
    }

    // Select X/Y keys: prefer props (selected by user), otherwise auto-detect
    const sample = data[0]
    const keys = Object.keys(sample)
    const xKey = propX || keys.find(k=>typeof sample[k] === 'string') || keys[0]
    const yKey = propY || keys.find(k=>typeof sample[k] === 'number') || keys.find(k=>!isNaN(Number(sample[k])))
    if(!yKey){
      container.innerHTML = '<p>No numeric column found for Y-axis</p>'
      return
    }

    // Transform data to x/y
    const d = data.map(row=>({x: row[xKey], y: +row[yKey]}))

    const width = 800, height = 400, margin = {top:20,right:20,bottom:80,left:60}
    const svg = d3.select(container).append('svg').attr('width',width).attr('height',height)
    if(type === 'Bar'){
      const x = d3.scaleBand().domain(d.map(d=>d.x)).range([margin.left, width - margin.right]).padding(0.1)
      const y = d3.scaleLinear().domain([0, d3.max(d, dd=>dd.y)]).nice().range([height - margin.bottom, margin.top])

      svg.append('g').attr('fill','#4c78a8')
        .selectAll('rect').data(d).join('rect')
        .attr('x', dd=>x(dd.x))
        .attr('y', dd=>y(dd.y))
        .attr('height', dd=>y(0)-y(dd.y))
        .attr('width', x.bandwidth())

      svg.append('g').attr('transform',`translate(0,${height - margin.bottom})`)
        .call(d3.axisBottom(x)).selectAll('text').attr('transform','rotate(-45)').style('text-anchor','end')

      svg.append('g').attr('transform',`translate(${margin.left},0)`).call(d3.axisLeft(y))
    } else if(type === 'Line'){
      const x = d3.scalePoint().domain(d.map(d=>d.x)).range([margin.left, width - margin.right])
      const y = d3.scaleLinear().domain([0, d3.max(d, dd=>dd.y)]).nice().range([height - margin.bottom, margin.top])

      const line = d3.line().x(dd=>x(dd.x)).y(dd=>y(dd.y))
      svg.append('path').datum(d).attr('fill','none').attr('stroke','#ff7f0e').attr('stroke-width',2).attr('d', line)

      svg.append('g').attr('transform',`translate(0,${height - margin.bottom})`).call(d3.axisBottom(x)).selectAll('text').attr('transform','rotate(-45)').style('text-anchor','end')
      svg.append('g').attr('transform',`translate(${margin.left},0)`).call(d3.axisLeft(y))
    } else if(type === 'Pie'){
      const radius = Math.min(width, height) / 2 - 20
      const g = svg.append('g').attr('transform',`translate(${width/2},${height/2})`)
      const pie = d3.pie().value(d=>d.y)(d)
      const arc = d3.arc().innerRadius(0).outerRadius(radius)
      const color = d3.scaleOrdinal(d3.schemeTableau10)
      g.selectAll('path').data(pie).join('path').attr('d', arc).attr('fill', (d,i)=>color(i)).attr('stroke','white')
    }

  },[data, type])

  return <div ref={ref}></div>
}
