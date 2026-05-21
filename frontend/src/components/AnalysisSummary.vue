<template>
  <div class="summary">
    <div class="stat-row">
      <div class="stat">
        <span class="stat-value accuracy">{{ accuracy }}%</span>
        <span class="stat-label">Accuracy</span>
      </div>
      <div class="stat">
        <span class="stat-value best">{{ counts.best + counts.excellent }}</span>
        <span class="stat-label">Best/Excellent</span>
      </div>
      <div class="stat">
        <span class="stat-value great">{{ counts.great }}</span>
        <span class="stat-label">Good</span>
      </div>
      <div class="stat">
        <span class="stat-value inaccuracy">{{ counts.inaccuracy }}</span>
        <span class="stat-label">Inaccuracies</span>
      </div>
      <div class="stat">
        <span class="stat-value mistake">{{ counts.mistake }}</span>
        <span class="stat-label">Mistakes</span>
      </div>
      <div class="stat">
        <span class="stat-value blunder">{{ counts.blunder }}</span>
        <span class="stat-label">Blunders</span>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AnalysisSummary',
  props: {
    moves: { type: Array, default: () => [] }
  },
  computed: {
    userMoves() {
      return this.moves.filter(m => m.is_user_move)
    },
    counts() {
      const c = { best: 0, excellent: 0, great: 0, inaccuracy: 0, mistake: 0, blunder: 0 }
      for (const m of this.userMoves) {
        if (m.classification && c[m.classification] !== undefined) {
          c[m.classification]++
        }
      }
      return c
    },
    accuracy() {
      if (!this.userMoves.length) return 0
      // Accuracy = average (100 - wp_loss) across all moves, clamped to 0-100
      const total = this.userMoves.reduce((sum, m) => {
        const loss = Math.max(0, m.wp_loss || 0)
        return sum + Math.max(0, 100 - loss * 3)
      }, 0)
      return Math.min(100, Math.round(total / this.userMoves.length))
    }
  }
}
</script>

<style scoped>
.summary {
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid #0f3460;
}

.stat-row {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.stat {
  display: flex;
  flex-direction: column;
  align-items: center;
  background: #0d1b2a;
  border-radius: 8px;
  padding: 12px 20px;
  min-width: 80px;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 11px;
  color: #aaa;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.accuracy { color: #4ecca3; }
.best { color: #4ecca3; }
.great { color: #a8e6cf; }
.inaccuracy { color: #f7dc6f; }
.mistake { color: #f0a500; }
.blunder { color: #e94560; }
</style>