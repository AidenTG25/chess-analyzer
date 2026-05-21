<template>
  <div class="eval-graph">
    <h3>Evaluation Graph</h3>
    <canvas ref="chart" height="80"></canvas>
  </div>
</template>

<script>
import { Chart, LineController, LineElement, PointElement, LinearScale, CategoryScale, Filler, Tooltip } from 'chart.js'

Chart.register(LineController, LineElement, PointElement, LinearScale, CategoryScale, Filler, Tooltip)

export default {
  name: 'EvalGraph',
  props: {
    moves: { type: Array, default: () => [] },
    userColor: { type: String, default: 'white' }
  },
  data() {
    return { chartInstance: null }
  },
  computed: {
    labels() {
      return this.moves.map((m, i) => {
        if (m.is_user_move) return `${m.move_number}. ${m.move_san}`
        return `${m.move_number}... ${m.move_san}`
      })
    },
    scores() {
      return this.moves.map(m => {
        const s = m.score_after
        return Math.max(-10, Math.min(10, s / 100))
      })
    },
    pointColors() {
      return this.moves.map(m => {
        if (!m.is_user_move) return 'rgba(255,255,255,0)'
        switch (m.classification) {
          case 'best':
          case 'excellent': return '#4ecca3'
          case 'great': return '#a8e6cf'
          case 'inaccuracy': return '#f7dc6f'
          case 'mistake': return '#f0a500'
          case 'blunder': return '#e94560'
          default: return '#aaa'
        }
      })
    }
  },
  mounted() {
    this.buildChart()
  },
  watch: {
    moves() {
      if (this.chartInstance) {
        this.chartInstance.destroy()
      }
      this.$nextTick(() => this.buildChart())
    }
  },
  methods: {
    buildChart() {
      const ctx = this.$refs.chart.getContext('2d')
      this.chartInstance = new Chart(ctx, {
        type: 'line',
        data: {
          labels: this.labels,
          datasets: [{
            data: this.scores,
            borderColor: '#4ecca3',
            borderWidth: 1.5,
            pointBackgroundColor: this.pointColors,
            pointRadius: this.moves.map(m => m.is_user_move ? 4 : 2),
            pointBorderWidth: 0,
            fill: {
              target: { value: 0 },
              above: 'rgba(78, 204, 163, 0.15)',
              below: 'rgba(233, 69, 96, 0.15)'
            },
            tension: 0.3
          }]
        },
        options: {
          responsive: true,
          animation: false,
          plugins: {
            legend: { display: false },
            tooltip: {
              callbacks: {
                label: (ctx) => {
                  const move = this.moves[ctx.dataIndex]
                  const score = (ctx.raw * 100).toFixed(0)
                  const cls = move.classification || ''
                  return `${score}cp ${cls ? '· ' + cls : ''}`
                }
              }
            }
          },
          scales: {
            x: {
              ticks: { display: false },
              grid: { color: '#0f3460' }
            },
            y: {
              min: -10,
              max: 10,
              ticks: {
                color: '#aaa',
                callback: (v) => v === 0 ? '0' : v > 0 ? `+${(v * 100).toFixed(0)}` : `${(v * 100).toFixed(0)}`
              },
              grid: {
                color: (ctx) => ctx.tick.value === 0 ? '#aaa' : '#0f3460'
              }
            }
          }
        }
      })
    }
  },
  beforeUnmount() {
    if (this.chartInstance) this.chartInstance.destroy()
  }
}
</script>

<style scoped>
.eval-graph {
  margin-bottom: 24px;
  padding-bottom: 20px;
  border-bottom: 1px solid #0f3460;
}

h3 {
  font-size: 13px;
  color: #aaa;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 12px;
}
</style>