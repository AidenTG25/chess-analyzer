
<template>
  <div class="move-list">
    <div
      v-for="(move, i) in userMoves"
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
    </div>
  </div>
</template>

<script>
import ChessBoard from './ChessBoard.vue'
export default {
  name: 'MoveList',
  components:{ChessBoard },
  props: {
    moves: { type: Array, default: () => [] },
    userColor: { type: String, default: 'white' }
  },
  data() {
    return { expanded: {} ,boardVisible:{}}
  },
  computed: {
    userMoves() {
      return this.moves.filter(m => m.is_user_move)
    }
  },
  methods: {
    toggleBoard(i) {
      this.boardVisible[i] = !this.boardVisible[i]
    },
    toggleLine(i) {
      this.expanded[i] = !this.expanded[i]
    }
  }
}
</script>

<style scoped>
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

.best-move { font-size: 13px; color: #aaa; }
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
</style>