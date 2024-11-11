<template>
  <div>
    <svg id="topology" width="2000" height="1000"></svg>
  </div>
</template>

<script>
import * as d3 from 'd3';

export default {
  name: "topo-logy",
  data() {
    return {
      nodes: [
        {id: 1, name: '控制器c1'},
        {id: 2, name: '交换机s1'},
        {id: 3, name: '主机h1'},
        {id: 4, name: '主机h2'},
        {id: 5, name: '主机h3'},
        {id: 6, name: '端口eh0'},
        {id: 7, name: '端口eh1'},
        {id: 8, name: '端口eh2'},
        {id: 9, name: '端口eh3'},
        {id: 10, name: '端口eh4'},
        {id: 11, name: '端口eh5'}
      ],
      links: [
        {source: 1, target: 2},
        {source: 2, target: 6},
        {source: 2, target: 8},
        {source: 2, target: 10},
        {source: 6, target: 7},
        {source: 8, target: 9},
        {source: 10, target: 11},
        {source: 7, target: 3},
        {source: 9, target: 4}, 
        {source: 11, target: 5}
      ],
      // 添加图像URL数组
      images: [
      require('@/assets/network/controller.light.svg'),
      require('@/assets/network/switch.light.svg'),
      require('@/assets/network/host.light.svg'),
      require('@/assets/network/host.light.svg'),
      require('@/assets/network/host.light.svg'),
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
    const width = svg.attr('width');
    const height = svg.attr('height');

    const simulation = d3.forceSimulation(this.nodes)
        .force('link', d3.forceLink(this.links).id(d => d.id).distance(150))
        .force('charge', d3.forceManyBody())
        .force('center', d3.forceCenter(width / 2, height / 2));

    const link = svg.selectAll('line')
        .data(this.links)
        .enter()
        .append('line')
        .attr('stroke', '#ccc')
        .attr('stroke-width', 1);

    const node = svg.selectAll('image')
        .data(this.nodes)
        .enter()
        .append('image')
        .attr('xlink:href', (d, i) => this.images[i]) // 设置图像URL
        .attr('x', -15) // 图像偏移量，根据图像大小调整
        .attr('y', -15) // 图像偏移量，根据图像大小调整
        .attr('width', 30) // 图像宽度，根据实际情况调整
        .attr('height', 30) // 图像高度，根据实际情况调整
        .call(d3.drag()
            .on('start', dragstarted)
            .on('drag', dragged)
            .on('end', dragended));

    const label = svg.selectAll('.label')
        .data(this.nodes)
        .enter()
        .append('text')
        .attr('class', "label")
        .text(function (d) {return d.name;})
        .attr("dx", 12)
        .attr("dy", ".35em");

    node.append('title')
        .text(d => d.name);

    simulation.on('tick', () => {
      link
          .attr('x1', d => d.source.x)
          .attr('y1', d => d.source.y)
          .attr('x2', d => d.target.x)
          .attr('y2', d => d.target.y);

      node
          .attr('x', d => d.x - 15) // 根据图像大小调整偏移量
          .attr('y', d => d.y - 15); // 根据图像大小调整偏移量
      label
          .attr('x', function (d) {return d.x;})
          .attr('y', function (d) {return d.y;});
    });

    function dragstarted(event, d) {
      if (!event.active) simulation.alphaTarget(0.1).restart();
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