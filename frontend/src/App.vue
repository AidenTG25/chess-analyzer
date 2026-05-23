<template>
  <div id="app">
    <h1>Chess Analyzer</h1>
    <GameSearch @games-loaded="onGamesLoaded" :has-results="games.length > 0" />

    <div class="main-layout" :class="{ 'has-analysis': analysisResult || analyzing }">
      <div class="game-list-panel" :style="(analysisResult || analyzing) ? { width: listWidth + 'px', minWidth: '200px' } : { width: '100%' }">
        <GameList
          :games="games"  
          :selected-index="selectedGame?.index"
          @game-selected="onGameSelected"
        />
      </div>

      <div
        v-if="analysisResult || analyzing"
        class="divider"
        @mousedown="startResize"
      ></div>

      <div class="analysis-panel" v-if="analysisResult || analyzing">
        <div v-if="analyzing" class="analyzing">
          <p>Analyzing with Stockfish...</p>
        </div>
        <div v-if="analysisResult && !analyzing">
          <div class="analysis-header">
            <h2>vs {{ analysisResult.opponent }}</h2>
            <span class="meta">{{ analysisResult.time_class }} · playing as {{ analysisResult.user_color }} · {{ analysisResult.result }}</span>
          </div>
          <AnalysisSummary :moves="analysisResult.moves" />
          <EvalGraph :moves="analysisResult.moves" :user-color="analysisResult.user_color" />
          <MoveList :moves="analysisResult.moves" :user-color="analysisResult.user_color" />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import GameSearch from './components/GameSearch.vue'
import GameList from './components/GameList.vue'
import AnalysisSummary from './components/AnalysisSummary.vue'
import MoveList from './components/MoveList.vue'
import axios from 'axios'
import EvalGraph from './components/EvalGraph.vue'

export default {
  name: 'App',
  components: { GameSearch, GameList, MoveList, AnalysisSummary, EvalGraph},
  data() {
    return {
      games: [],
      username: '',
      year: null,
      month: null,
      selectedGame: null,
      analysisResult: null,
      analyzing: false,
      listWidth: 380,
      resizing: false,
    }
  },
  mounted() {
    const saved = sessionStorage.getItem('chessAnalyzerState')
    if (saved) {
      const { games, username, year, month } = JSON.parse(saved)
      this.games = games
      this.username = username
      this.year = year
      this.month = month
    }
    window.addEventListener('mousemove', this.onResize)
    window.addEventListener('mouseup', this.stopResize)
  },
  beforeUnmount() {
    window.removeEventListener('mousemove', this.onResize)
    window.removeEventListener('mouseup', this.stopResize)
  },
  watch: {
    username(val) {
      this.$nextTick(() => {
        const el = this.$refs.usernameInput
        if (el) {
          el.style.width = Math.max(140, val.length * 10 + 40) + 'px'
        }
      })
    }
  },
  methods: {
    onGamesLoaded({ games, username, year, month }) {
      this.games = games
      this.username = username
      this.year = year
      this.month = month
      this.selectedGame = null
      this.analysisResult = null
      sessionStorage.setItem('chessAnalyzerState', JSON.stringify({ games, username, year, month }))
    },
    async onGameSelected(game) {
      this.selectedGame = game
      this.analyzing = true
      this.analysisResult = null
      try {
        const res = await axios.post('http://localhost:5000/analyze', {
          username: this.username,
          year: this.year,
          month: this.month,
          mode: 'single',
          index: game.index
        })
        this.analysisResult = res.data.results[0]
      } catch (err) {
        console.error('Analysis failed:', err)
      } finally {
        this.analyzing = false
      }
    },
    startResize() {
      this.resizing = true
    },
    onResize(e) {
      if (!this.resizing) return
      const appLeft = document.getElementById('app').getBoundingClientRect().left
      const newWidth = e.clientX - appLeft - 40
      this.listWidth = Math.max(200, Math.min(newWidth, 700))
    },
    stopResize() {
      this.resizing = false
    }
  }
}
  
</script>

<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { background: #1a1a2e; color: #eee; font-family: sans-serif; }
#app { max-width: 100%; margin: 0 auto; padding: 24px 40px; }
h1 { font-size: 28px; margin-bottom: 24px; color: #e94560; }

.main-layout {
  display: flex;
  gap: 0;
}

.game-list-panel {
  overflow-y: auto;
  max-height: 82vh;
  flex-shrink: 0;
}

.divider {
  width: 6px;
  cursor: col-resize;
  background: #0f3460;
  margin: 0 8px;
  border-radius: 3px;
  transition: background 0.2s;
  flex-shrink: 0;
}
.divider:hover { background: #e94560; }

.analysis-panel {
  flex: 1;
  background: #16213e;
  border: 1px solid #0f3460;
  border-radius: 8px;
  padding: 28px;
  min-height: 500px;
  overflow-y: auto;
  max-height: 82vh;
}

.analyzing {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #aaa;
  font-size: 15px;
}

.analysis-header {
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid #0f3460;
}

.analysis-header h2 {
  font-size: 24px;
  color: #e94560;
  margin-bottom: 4px;
}

.meta {
  font-size: 13px;
  color: #aaa;
  text-transform: capitalize;
}
</style>