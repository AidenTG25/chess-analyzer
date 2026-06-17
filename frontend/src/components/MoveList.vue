<template>
  <div class="move-list">
    <div class="filter-bar">
      <button
        v-for="f in filters"
        :key="f.value"
        :class="['filter-btn', { active: activeFilter === f.value }]"
        @click="activeFilter = f.value"
      >
        {{ f.label }}
      </button>
    </div>

    <div
      v-for="(move, i) in filteredMoves"
      :key="i"
      class="move-row"
      :class="move.classification"
    >
      <div class="move-top">
        <span class="move-number">{{ move.move_number }}.</span>
        <span class="move-san">{{ move.move_san }}</span>
        <span class="classification-badge" :class="move.classification">
          {{ move.classification }}
        </span>
        <span class="cp-loss" v-if="move.cp_loss > 0">-{{ move.cp_loss }}cp</span>
        <span class="wp-loss" v-if="move.wp_loss > 0">-{{ move.wp_loss }}%</span>
      </div>

      <div class="move-details" v-if="move.patterns?.length || move.best_move">
        <div class="patterns" v-if="move.patterns?.length">
          <span v-for="(p, j) in move.patterns" :key="j" class="pattern">⚠ {{ p }}</span>
        </div>
        <div class="best-move" v-if="move.best_move">
          <span class="label">Best:</span> {{ move.best_move }}
          <button
            v-if="move.engine_line?.length"
            class="line-btn"
            @click="toggleLine(i)"
          >
            {{ expanded[i] ? 'hide line' : 'show line' }}
          </button>
          <div class="engine-line" v-if="expanded[i] && move.engine_line?.length">
            {{ move.engine_line.join(' → ') }}
          </div>
        </div>
        <div class="board-toggle">
          <button class="line-btn" @click="toggleBoard(i)">
            {{ boardVisible[i] ? 'hide board' : 'show board' }}
          </button>
          <ChessBoard
            v-if="boardVisible[i]"
            :fen="move.fen"
            :best-move="move.best_move"
            :engine-line="move.engine_line || []"
            :orientation="userColor"
          />
        </div>
      </div>
    </div>

    <p v-if="filteredMoves.length === 0" class="empty">
      No moves match the current filter.
    </p>
  </div>
</template>

<script>
import ChessBoard from './ChessBoard.vue'

export default {
  name: 'MoveList',
  components: { ChessBoard },
  props: {
    moves: { type: Array, default: () => [] },
    userColor: { type: String, default: 'white' }
  },
  data() {
    return {
      expanded: {},
      boardVisible: {},
      activeFilter: 'all',
      filters: [
        { value: 'all', label: 'All' },
        { value: 'negative', label: 'Negative' },
        { value: 'blunder', label: 'Blunders' },
        { value: 'mistake', label: 'Mistakes' },
        { value: 'inaccuracy', label: 'Inaccuracies' },
      ]
    }
  },
  computed: {
    userMoves() {
      return this.moves.filter(m => m.is_user_move)
    },
    filteredMoves() {
      if (this.activeFilter === 'all') return this.userMoves
      if (this.activeFilter === 'negative') {
        return this.userMoves.filter(m =>
          ['inaccuracy', 'mistake', 'blunder'].includes(m.classification)
        )
      }
      return this.userMoves.filter(m => m.classification === this.activeFilter)
    }
  },
  methods: {
    toggleLine(i) {
      this.expanded[i] = !this.expanded[i]
    },
    toggleBoard(i) {
      this.boardVisible[i] = !this.boardVisible[i]
    }
  }
}
</script>

<style scoped>
.filter-bar {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.filter-btn {
  background: #16213e;
  border: 1px solid #0f3460;
  color: #aaa;
  padding: 4px 14px;
  border-radius: 12px;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.2s;
}

.filter-btn:hover { border-color: #e94560; color: #eee; }
.filter-btn.active { background: #0f3460; color: #eee; border-color: #4ecca3; }

.move-list { display: flex; flex-direction: column; gap: 6px; margin-top: 16px; }

.move-row {
  background: #0d1b2a;
  border-radius: 6px;
  padding: 10px 14px;
  border-left: 3px solid #0f3460;
}
.move-row.best { border-left-color: #4ecca3; }
.move-row.excellent { border-left-color: #4ecca3; }
.move-row.great { border-left-color: #a8e6cf; }
.move-row.inaccuracy { border-left-color: #f7dc6f; }
.move-row.mistake { border-left-color: #f0a500; }
.move-row.blunder { border-left-color: #e94560; }

.move-top {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.move-number { color: #666; font-size: 12px; }
.move-san { font-weight: 600; font-size: 15px; }

.classification-badge {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 10px;
  font-weight: 600;
  text-transform: capitalize;
}
.classification-badge.best,
.classification-badge.excellent { background: #1a3a2a; color: #4ecca3; }
.classification-badge.great { background: #1a3a2a; color: #a8e6cf; }
.classification-badge.inaccuracy { background: #3a3a1a; color: #f7dc6f; }
.classification-badge.mistake { background: #3a2a1a; color: #f0a500; }
.classification-badge.blunder { background: #3a1a1a; color: #e94560; }

.cp-loss, .wp-loss { font-size: 12px; color: #aaa; }

.move-details { margin-top: 8px; padding-top: 8px; border-top: 1px solid #1a2a3a; }

.patterns { display: flex; flex-direction: column; gap: 4px; margin-bottom: 6px; }
.pattern { font-size: 12px; color: #f0a500; }

.best-move { font-size: 13px; color: #aaa; margin-bottom: 6px; }
.best-move .label { color: #4ecca3; font-weight: 600; }

.line-btn {
  background: none;
  border: 1px solid #0f3460;
  color: #aaa;
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 4px;
  cursor: pointer;
  margin-left: 8px;
}
.line-btn:hover { border-color: #e94560; color: #eee; }

.engine-line {
  margin-top: 6px;
  font-size: 12px;
  color: #888;
  font-style: italic;
}

.empty {
  color: #aaa;
  font-size: 13px;
  text-align: center;
  padding: 20px;
}
</style>