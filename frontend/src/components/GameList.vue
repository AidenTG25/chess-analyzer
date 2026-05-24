<template>
  <div class="game-list" v-if="games.length">
    <h2>{{ games.length }} games found</h2>
    <div
      v-for="game in games"
      :key="game.index"
      class="game-card"
      :class="{ selected: game.index === selectedIndex }"
      @click="$emit('game-selected', game)"
    >
      <div class="game-info">
        <span class="opponent">vs {{ game.opponent }}</span>
        <span class="time-class">{{ game.time_class }}</span>
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
    games: {
      type: Array,
      default: () => []
    },
    selectedIndex: {
      type: Number,
      default: null
    }
  },
  emits: ['game-selected'],
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

.game-card.selected {
  border-color: #e94560;
  background: #1a1a3e;
}

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

.color {
  color: #aaa;
  text-transform: capitalize;
  font-size: 11px;
}

.date { color: #666; font-size: 11px; }
</style>