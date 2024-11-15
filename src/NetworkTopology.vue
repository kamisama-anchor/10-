<template>
  <div class="container">
    <div class="topology-card">
      <h2 class="topology-title">网络拓扑展示</h2>
      <p class="topology-description">
        该图展示了网络拓扑结构的基本关系，包括控制器、交换机、端口和主机的连接。
      </p>
      <div class="svg-container">
        <svg id="topology" width="1200" height="800"></svg>
      </div>
    </div>
  </div>
</template>

<script>
import * as d3 from 'd3';

export default {
  name: "topo-logy",
  data() {
    return {
      nodes: [
        { id: 1, name: '控制器c1',x:850,y:500},
        { id: 2, name: '交换机s1',x: 700, y: 400},
        { id: 3, name: '交换机s2',x: 1000, y: 400},
        { id: 4, name: '主机h1',x:600,y:100},
        { id: 5, name: '主机h2',x:700,y:100},
        { id: 6, name: '主机h3',x:800,y:100 },
        { id: 7, name: '主机h4',x:900,y:100},
        { id: 8, name: '主机h5',x:1000,y:100},
        { id: 9, name: '主机h6',x:1100,y:100},
        { id: 10, name: '端口eh0'},
        { id: 11, name: '端口eh1' },
        { id: 12, name: '端口eh0' },
        { id: 13, name: '端口eh2'},
        { id: 14, name: '端口eh0'},
        { id: 15, name: '端口eh3' },
        { id: 16, name: '端口eh0'},
        { id: 17, name: '端口eh1' },
        { id: 18, name: '端口eh0'},
        { id: 19, name: '端口eh2' },
        { id: 20, name: '端口eh0' },
        { id: 21, name: '端口eh3' },
        { id: 22, name: '端口eh0' },
        { id: 23, name: '端口eh4' },
        { id: 24, name: '端口eh4' }
      ],
      links: [
        { source: 1, target: 2 },
        { source: 1, target: 3 },
        { source: 2, target: 23 },
        { source: 2, target: 11 },
        { source: 2, target: 13 },
        { source: 2, target: 15 },
        { source: 11, target:10 },
        { source: 10, target: 4 },
        { source: 13, target: 12 },
        { source: 12, target: 5 },
        { source: 15, target: 14 },
        { source: 14, target: 6 },
        { source: 3, target: 24},
        { source: 3, target: 17 },
        { source: 3, target: 19 },
        { source: 3, target: 21 },
        { source: 17, target: 16 },
        { source: 16, target: 7 },
        { source: 19, target: 18 },
        { source: 18, target: 8 },
        { source: 21, target: 20 },
        { source: 20, target: 9 },
        { source: 23, target: 24 }
      ],
      images: [
        require('@/assets/network/controller.light.svg'),
        require('@/assets/network/switch.light.svg'),
        require('@/assets/network/switch.light.svg'),
        require('@/assets/network/host.light.svg'),
        require('@/assets/network/host.light.svg'),
        require('@/assets/network/host.light.svg'),
        require('@/assets/network/host.light.svg'),
        require('@/assets/network/host.light.svg'),
        require('@/assets/network/host.light.svg'),
        require('@/assets/network/port.light.svg'),
        require('@/assets/network/port.light.svg'),
        require('@/assets/network/port.light.svg'),
        require('@/assets/network/port.light.svg'),
        require('@/assets/network/port.light.svg'),
        require('@/assets/network/port.light.svg'),
        require('@/assets/network/port.light.svg'),
        require('@/assets/network/port.light.svg'),
        require('@/assets/network/port.light.svg'),
        require('@/assets/network/port.light.svg'),
        require('@/assets/network/port.light.svg'),
        require('@/assets/network/port.light.svg'),
        require('@/assets/network/port.light.svg'),
        require('@/assets/network/port.light.svg'),
        require('@/assets/network/port.light.svg')

      ]
    }
  },
  mounted() {
    const svg = d3.select('#topology');

    const simulation = d3.forceSimulation(this.nodes)
      .force('link', d3.forceLink(this.links).id(d => d.id).distance(100))
      .force('charge', d3.forceManyBody().strength(-300))
      .alpha(0.2)
      .on('tick', () => {
        link
          .attr('x1', d => d.source.x)
          .attr('y1', d => d.source.y)
          .attr('x2', d => d.target.x)
          .attr('y2', d => d.target.y);

        node
          .attr('x', d => d.x - 20)
          .attr('y', d => d.y - 20);

        label
          .attr('x', d => d.x + 25)
          .attr('y', d => d.y);
      });

    const link = svg.selectAll('line')
      .data(this.links)
      .enter()
      .append('line')
      .attr('stroke', '#8aacc8')
      .attr('stroke-width', 2)
      .attr('stroke-dasharray', '5,5')
      .style("transition", "stroke-dashoffset 0.5s");

    const node = svg.selectAll('image')
      .data(this.nodes)
      .enter()
      .append('image')
      .attr('xlink:href', (d, i) => this.images[i])
      .attr('x', -20)
      .attr('y', -20)
      .attr('width', 40)
      .attr('height', 40)
      .call(d3.drag()
        .on('start', dragstarted)
        .on('drag', dragged)
        .on('end', dragended))
      .on("mouseover", function() {
        d3.select(this).transition().duration(200).attr("width", 45).attr("height", 45);
      })
      .on("mouseout", function() {
        d3.select(this).transition().duration(200).attr("width", 40).attr("height", 40);
      });

    const label = svg.selectAll('.label')
      .data(this.nodes)
      .enter()
      .append('text')
      .attr('class', "label")
      .text(d => d.name)
      .attr("dx", 12)
      .attr("dy", ".35em")
      .style("fill", "#333")
      .style("font-size", "14px");

    node.append('title')
      .text(d => d.name);

    function dragstarted(event, d) {
      if (!event.active) simulation.alphaTarget(0.3).restart();
      d.fx = d.x;
      d.fy = d.y;
    }

    function dragged(event, d) {
      d.fx = event.x;
      d.fy = event.y;
    }

    function dragended(event, d) {
      if (!event.active) simulation.alphaTarget(0);
      d.fx = null;
      d.fy = null;
    }
  }
}
</script>

<style scoped>
.container {
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #f5f7fa, #c3cfe2);
  height: 100vh;
  padding: 30px;
}

.topology-card {
  background: white;
  border-radius: 15px;
  box-shadow: 0px 6px 18px rgba(0, 0, 0, 0.1);
  padding: 25px;
  width: 90%;
  max-width: 1300px;
}

.topology-title {
  font-family: 'Arial', sans-serif;
  font-weight: 700;
  color: #333;
  font-size: 26px;
  margin-bottom: 15px;
}

.topology-description {
  font-family: 'Arial', sans-serif;
  color: #666;
  font-size: 16px;
  margin-bottom: 25px;
}

.svg-container {
  border: 2px solid #8aacc8;
  border-radius: 10px;
  overflow: hidden;
  padding: 5px;
}

line {
  transition: stroke-dashoffset 0.5s ease;
}

.label {
  font-family: 'Verdana', sans-serif;
  font-size: 12px;
  fill: #4a4a4a;
}
</style>
