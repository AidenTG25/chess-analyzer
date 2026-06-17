<template>
  <div class="game-list" v-if="games.length">
    <div class="filters">
      <input
        v-model="search"
        placeholder="Search opponent..."
        class="filter-input"
      />
      <div class="filter-buttons">
        <button
          v-for="r in resultFilters"
          :key="r.value"
          :class="['filter-btn', r.value, { active: resultFilter === r.value }]"
          @click="resultFilter = resultFilter === r.value ? 'all' : r.value"
        >
          {{ r.label }}
        </button>
        <button
          v-for="t in timeFilters"
          :key="t"
          :class="['filter-btn', { active: timeFilter === t }]"
          @click="timeFilter = timeFilter === t ? 'all' : t"
        >
          {{ t }}
        </button>
      </div>
    </div>

    <h2>{{ filteredGames.length }} / {{ games.length }} games</h2>

    <div
      v-for="game in filteredGames"
      :key="game.index"
      class="game-card"
      :class="{ selected: game.index === selectedIndex }"
      @click="$emit('game-selected', game)"
    >
      <div class="game-info">
        <span class="opponent">vs {{ game.opponent }}</span>
        <span class="time-class">{{ game.time_class }}</span>
        <span class="opening-tag" v-if="game.opening">{{ game.opening }}</span>
      </div>
      <div class="game-meta">
        <span :class="resultClass(game.result)">{{ game.result }}</span>
        <span class="color">playing as {{ game.user_color }}</span>
        <span class="date">{{ formatDate(game.end_time) }}</span>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'GameList',
  props: {
    games: { type: Array, default: () => [] },
    selectedIndex: { type: Number, default: null }
  },
  emits: ['game-selected'],
  data() {
    return {
      search: '',
      resultFilter: 'all',
      timeFilter: 'all',
      resultFilters: [
        { value: 'win', label: 'Win' },
        { value: 'loss', label: 'Loss' },
        { value: 'draw', label: 'Draw' },
      ],
      timeFilters: ['bullet', 'blitz', 'rapid']
    }
  },
  computed: {
    filteredGames() {
      return this.games.filter(game => {
        // Opponent search
        if (this.search && !game.opponent.toLowerCase().includes(this.search.toLowerCase())) {
          return false
        }
        // Result filter
        if (this.resultFilter !== 'all') {
          const isWin = game.result === 'win'
          const isLoss = ['resigned', 'checkmated', 'timeout', 'abandoned'].includes(game.result)
          const isDraw = !isWin && !isLoss
          if (this.resultFilter === 'win' && !isWin) return false
          if (this.resultFilter === 'loss' && !isLoss) return false
          if (this.resultFilter === 'draw' && !isDraw) return false
        }
        // Time class filter
        if (this.timeFilter !== 'all' && game.time_class !== this.timeFilter) {
          return false
        }
        return true
      })
    }
  },
  methods: {
    formatDate(timestamp) {
      return new Date(timestamp * 1000).toLocaleDateString()
    },
    resultClass(result) {
      if (result === 'win') return 'result win'
      if (['resigned', 'checkmated', 'timeout', 'abandoned'].includes(result)) return 'result loss'
      return 'result draw'
    }
  }
}
</script>

<style scoped>
.game-list { margin-top: 20px; }

.filters {
  margin-bottom: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.filter-input {
  background: #16213e;
  border: 1px solid #0f3460;
  color: #eee;
  border-radius: 6px;
  padding: 7px 12px;
  font-size: 13px;
  width: 100%;
  outline: none;
}

.filter-input:focus { border-color: #e94560; }

.filter-buttons {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.filter-btn {
  background: #16213e;
  border: 1px solid #0f3460;
  color: #aaa;
  padding: 4px 12px;
  border-radius: 12px;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.2s;
}

.filter-btn:hover { border-color: #e94560; color: #eee; }
.filter-btn.active { background: #0f3460; color: #eee; border-color: #4ecca3; }
.filter-btn.win.active { border-color: #4ecca3; color: #4ecca3; }
.filter-btn.loss.active { border-color: #e94560; color: #e94560; }
.filter-btn.draw.active { border-color: #aaa; color: #aaa; }

h2 { margin-bottom: 12px; color: #aaa; font-size: 14px; }

.game-card {
  background: #16213e;
  border: 1px solid #0f3460;
  border-radius: 8px;
  padding: 10px 12px;
  margin-bottom: 8px;
  cursor: pointer;
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 4px;
  transition: border-color 0.2s;
}

.game-card:hover { border-color: #e94560; }
.game-card.selected { border-color: #e94560; background: #1a1a3e; }

.game-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.opponent {
  font-weight: 600;
  font-size: 13px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.time-class {
  color: #aaa;
  font-size: 11px;
  text-transform: capitalize;
}

.opening-tag {
  color: #4ecca3;
  font-size: 10px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.game-meta {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 2px;
  font-size: 12px;
}

.result.win { color: #4ecca3; font-weight: 600; }
.result.loss { color: #e94560; font-weight: 600; }
.result.draw { color: #aaa; font-weight: 600; }
.color { color: #aaa; text-transform: capitalize; font-size: 11px; }
.date { color: #666; font-size: 11px; }
</style>