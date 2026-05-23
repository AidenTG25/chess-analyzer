<template>
  <div class="board-container">
    <div class="board-controls">
      <button @click="resetToPosition" title="Reset to move position">↺ Reset</button>
      <button @click="stepBack" :disabled="history.length === 0">← Back</button>
      <button @click="playBestMove" :disabled="loading">
        {{ loading ? '...' : '▶ Best Move' }}
      </button>
      <span class="turn-indicator">{{ turnLabel }}</span>
    </div>
    <div ref="boardEl" class="board"></div>
    <div class="board-footer" v-if="lastMoveSan">
      Last move: <strong>{{ lastMoveSan }}</strong>
    </div>
    <div class="board-error" v-if="error">{{ error }}</div>
  </div>
</template>

<script>
import { Chess } from 'chess.js'
import { Chessboard, COLOR, INPUT_EVENT_TYPE } from 'cm-chessboard'
import { Markers, MARKER_TYPE } from 'cm-chessboard/src/extensions/markers/Markers.js'

export default {
  name: 'ChessBoard',
  props: {
    fen: { type: String, required: true },
    bestMove: { type: String, default: null },
    engineLine: { type: Array, default: () => [] },
    orientation: { type: String, default: 'white' }
  },
  data() {
    return {
      board: null,
      chess: null,
      history: [],
      lastMoveSan: null,
      loading: false,
      error: null
    }
  },
  computed: {
    turnLabel() {
      if (!this.chess) return ''
      return this.chess.turn() === 'w' ? "White to move" : "Black to move"
    }
  },
  mounted() {
    this.initBoard()
  },
  beforeUnmount() {
    if (this.board) this.board.destroy()
  },
  watch: {
    fen() {
      this.resetToPosition()
    }
  },
  methods: {
    initBoard() {
      this.chess = new Chess(this.fen)
      this.board = new Chessboard(this.$refs.boardEl, {
        position: this.fen,
        orientation: this.orientation === 'white' ? COLOR.white : COLOR.black,
        assetsUrl: '/cm-chessboard/',
        style: {
          cssClass: 'default',
          showCoordinates: true,
        },
        extensions: [{
          class: Markers,
          props: { autoMarkers: MARKER_TYPE.square }
        }]
      })
      this.board.enableMoveInput((event) => {
        if (event.type === INPUT_EVENT_TYPE.validateMoveInput) {
          return this.handleUserMove(event.squareFrom, event.squareTo)
        }
        return true
      }, this.orientation === 'white' ? COLOR.white : COLOR.black)
      this.markBestMove()
    },
    handleUserMove(from, to) {
      try {
        const move = this.chess.move({ from, to, promotion: 'q' })
        if (!move) return false
        this.history.push(move)
        this.lastMoveSan = move.san
        this.board.setPosition(this.chess.fen(), true)
        this.markBestMove()
        setTimeout(() => this.playBestMove(), 300)
        return true
      } catch {
        return false
      }
    },
    async playBestMove() {
      if (this.chess.isGameOver()) return
      this.loading = true
      this.error = null
      try {
        const res = await fetch('http://localhost:5000/bestmove', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ fen: this.chess.fen() })
        })
        const data = await res.json()
        if (data.error) { this.error = data.error; return }

        const move = this.chess.move(data.move_uci)
        if (move) {
          this.history.push(move)
          this.lastMoveSan = data.move_san
          this.board.setPosition(this.chess.fen(), true)
          this.markBestMove()
        }
      } catch (e) {
        this.error = 'Engine error'
      } finally {
        this.loading = false
      }
    },
    stepBack() {
      if (this.history.length === 0) return
      this.chess.undo()
      this.history.pop()
      this.lastMoveSan = this.history.length > 0
        ? this.history[this.history.length - 1].san
        : null
      this.board.setPosition(this.chess.fen(), true)
      this.markBestMove()
    },
    resetToPosition() {
      this.chess = new Chess(this.fen)
      this.history = []
      this.lastMoveSan = null
      this.error = null
      if (this.board) {
        this.board.setPosition(this.fen, true)
        this.markBestMove()
      }
    },
    markBestMove() {
      if (!this.board || !this.bestMove || this.history.length > 0) return
      try {
        const tempChess = new Chess(this.chess.fen())
        const move = tempChess.move(this.bestMove)
        if (move) {
          this.board.addMarker(MARKER_TYPE.frame, move.from)
          this.board.addMarker(MARKER_TYPE.frame, move.to)
        }
      } catch {}
    }
  }
}
</script>

<style scoped>
.board-container {
  margin-top: 12px;
  background: #0d1b2a;
  border-radius: 8px;
  padding: 12px;
  display: inline-block;
  width: 100%;
}

.board {
  width: 280px;
  height: 280px;
  margin: 0 auto;
}

.board-controls {
  display: flex;
  gap: 8px;
  align-items: center;
  margin-bottom: 10px;
  flex-wrap: wrap;
}

.board-controls button {
  background: #16213e;
  border: 1px solid #0f3460;
  color: #eee;
  padding: 4px 12px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  transition: border-color 0.2s;
}

.board-controls button:hover { border-color: #e94560; }
.board-controls button:disabled { opacity: 0.4; cursor: not-allowed; }

.turn-indicator {
  font-size: 12px;
  color: #aaa;
  margin-left: auto;
}

.board-footer {
  text-align: center;
  font-size: 12px;
  color: #aaa;
  margin-top: 8px;
}

.board-error {
  text-align: center;
  font-size: 12px;
  color: #e94560;
  margin-top: 6px;
}
</style>