<template>
  <div class="search" :class="{ compact: hasResults }">
    <h2 v-if="!hasResults">Find Your Games</h2>

    <div class="mode-select" >
      <button
        v-for="m in modes"
        :key="m.value"
        :class="{ active: mode === m.value }"
        @click="mode = m.value"
      >
        {{ m.label }}
      </button>
    </div>

    <div class="form">
      <input
        ref="usernameInput"
        v-model="username"
        placeholder="Chess.com username"
      />
      <template v-if="mode === 'month'">
        <input v-model.number="year" type="number" placeholder="Year" />
        <input v-model.number="month" type="number" placeholder="Month" />
      </template>
      <template v-if="mode === 'last_n'">
        <input v-model.number="n" type="number" placeholder="Last N games" />
      </template>
      <template v-if="mode === 'last_n_month'">
        <input v-model.number="year" type="number" placeholder="Year" min="2005" :max="new Date().getFullYear()" />
        <input v-model.number="month" type="number" placeholder="Month" min="1" max="12" />
        <input v-model.number="n" type="number" placeholder="Last N games" min="1" max="500" />
      </template>
      <input
        ref="usernameInput"
        v-model="username"
        placeholder="Chess.com username"
      />
      <template v-if="mode === 'month'">
        <input v-model.number="year" type="number" placeholder="Year" />
        <input v-model.number="month" type="number" placeholder="Month" />
      </template>
      <template v-if="mode === 'last_n'">
        <input v-model.number="n" type="number" placeholder="Last N games" />
      </template>
      <template v-if="mode === 'last_n_month'">
        <input v-model.number="year" type="number" placeholder="Year" min="2005" :max="new Date().getFullYear()" />
        <input v-model.number="month" type="number" placeholder="Month" min="1" max="12" />
        <input v-model.number="n" type="number" placeholder="Last N games" min="1" max="500" />
      </template>
      <button @click="search" :disabled="loading">
        {{ loading ? loadingText : 'Search' }}
        {{ loading ? loadingText : 'Search' }}
      </button>
    </div>
    <p v-if="error" class="error">{{ error }}</p>
    <p v-if="progressText" class="progress">{{ progressText }}</p>
    <p v-if="progressText" class="progress">{{ progressText }}</p>
  </div>
</template>

<script>
import axios from 'axios'

const API = 'http://localhost:5000'

export default {
  name: 'GameSearch',
  emits: ['games-loaded'],
  props: {
    hasResults: { type: Boolean, default: false },
    savedUsername: { type: String, default: '' },
    savedYear: { type: Number, default: null },
    savedMonth: { type: Number, default: null },
  },
  data() {
    return {
      username: this.savedUsername || '',
      year: this.savedYear || new Date().getFullYear(),
      month: this.savedMonth ||new Date().getMonth() + 1,
      n: 10,
      mode: 'month',
      loading: false,
      loadingText: 'Loading...',
      progressText: '',
      error: null,
      modes: [
        { value: 'month', label: 'By Month' },
        { value: 'last_n', label: 'Last N Games' },
        { value: 'last_n_month', label: 'Last N of Month' },
      ]
    }
  },
  mounted() {
    const savedSearch = sessionStorage.getItem('chessSearchState')
    if (savedSearch) {
      const { mode, n } = JSON.parse(savedSearch)
      if (mode) this.mode = mode
      if (n) this.n = n
    }
    if (this.username) {
      this.$nextTick(() => {
        const el = this.$refs.usernameInput
        if (el) {
          el.style.width = Math.max(140, this.username.length * 10 + 40) + 'px'
        }
      })
    }
  },
  watch: {
    savedUsername(val) {
      if (val && !this.username) {
        this.username = val
        this.$nextTick(() => {
          const el = this.$refs.usernameInput
          if (el) {
            el.style.width = Math.max(140, val.length * 10 + 40) + 'px'
          }
        })
      }
    },
    savedYear(val) {
      if (val && !this.year) this.year = val
    },
    savedMonth(val) {
      if (val && !this.month) this.month = val
    },
    username(val) {
      this.$nextTick(() => {
        const el = this.$refs.usernameInput
        if (el) {
          el.style.width = Math.max(140, val.length * 10 + 40) + 'px'
        }
      })
    },
    month(val) {
      if (!val) return
      if (val > 12) {
        this.month = 1
        this.year++
      } else if (val < 1) {
        this.month = 12
        this.year--
      }
    },
    year(val) {
      const currentYear = new Date().getFullYear()
      const currentMonth = new Date().getMonth() + 1
      if (!val) return
      if (val < 2005) {
        this.year = 2005
        this.month = 1
      }
      if (val > currentYear) {
        this.year = currentYear
        this.month = currentMonth
      }
    }
    
    },
    month(val) {
      if (!val) return
      if (val > 12) {
        this.month = 1
        this.year++
      } else if (val < 1) {
        this.month = 12
        this.year--
      }
    },
    year(val) {
      const currentYear = new Date().getFullYear()
      const currentMonth = new Date().getMonth() + 1
      if (!val) return
      if (val < 2005) {
        this.year = 2005
        this.month = 1
      }
      if (val > currentYear) {
        this.year = currentYear
        this.month = currentMonth
      }
    }
    
  },
  methods: {
    prevMonth(year, month) {
      if (month === 1) return { year: year - 1, month: 12 }
      return { year, month: month - 1 }
    },

    async fetchMonth(username, year, month) {
      const res = await axios.post(`${API}/games`, { username, year, month })
      const games = res.data.games || []
      return games.map(g => ({ ...g, fetchYear: year, fetchMonth: month }))
    },

    async search() {
      if (!this.username) return
      sessionStorage.setItem('chessSearchState', JSON.stringify({ mode: this.mode, n: this.n }))
      this.loading = true
      this.error = null
      this.progressText = ''

      this.progressText = ''

      try {
        if (this.mode === 'month') {
          const games = await this.fetchMonth(this.username, this.year, this.month)
          this.$emit('games-loaded', {
            games,
            username: this.username,
            year: this.year,
            month: this.month
          })

        } else if (this.mode === 'last_n_month') {
          const games = await this.fetchMonth(this.username, this.year, this.month)
          const sliced = games.slice(-Math.min(this.n, games.length))
          this.$emit('games-loaded', {
            games: sliced,
            username: this.username,
            year: this.year,
            month: this.month
          })

        } else if (this.mode === 'last_n') {
          // Progressive multi-month fetch
          let collected = []
          let { year, month } = { year: new Date().getFullYear(), month: new Date().getMonth() + 1 }
          const target = this.n
          let attempts = 0
          const maxAttempts = 24 // go back up to 2 years

          while (collected.length < target && attempts < maxAttempts) {
            this.progressText = `Found ${collected.length} / ${target} games, loading ${year}/${month}...`
            const games = await this.fetchMonth(this.username, year, month)
            collected = [...games, ...collected]
            if (games.length === 0 && attempts > 2) break // no more games
            const prev = this.prevMonth(year, month)
            year = prev.year
            month = prev.month
            attempts++
          }

          const sliced = collected.slice(-target)
          this.progressText = ''
          this.$emit('games-loaded', {
            games: sliced,
            username: this.username,
            year: new Date().getFullYear(),
            month: new Date().getMonth() + 1
          })
        }

        if (this.mode === 'month') {
          const games = await this.fetchMonth(this.username, this.year, this.month)
          this.$emit('games-loaded', {
            games,
            username: this.username,
            year: this.year,
            month: this.month
          })

        } else if (this.mode === 'last_n_month') {
          const games = await this.fetchMonth(this.username, this.year, this.month)
          const sliced = games.slice(-Math.min(this.n, games.length))
          this.$emit('games-loaded', {
            games: sliced,
            username: this.username,
            year: this.year,
            month: this.month
          })

        } else if (this.mode === 'last_n') {
          // Progressive multi-month fetch
          let collected = []
          let { year, month } = { year: new Date().getFullYear(), month: new Date().getMonth() + 1 }
          const target = this.n
          let attempts = 0
          const maxAttempts = 24 // go back up to 2 years

          while (collected.length < target && attempts < maxAttempts) {
            this.progressText = `Found ${collected.length} / ${target} games, loading ${year}/${month}...`
            const games = await this.fetchMonth(this.username, year, month)
            collected = [...games, ...collected]
            if (games.length === 0 && attempts > 2) break // no more games
            const prev = this.prevMonth(year, month)
            year = prev.year
            month = prev.month
            attempts++
          }

          const sliced = collected.slice(-target)
          this.progressText = ''
          this.$emit('games-loaded', {
            games: sliced,
            username: this.username,
            year: new Date().getFullYear(),
            month: new Date().getMonth() + 1
          })
        }

      } catch (err) {
        this.error = err.response?.data?.error || 'Something went wrong'
      } finally {
        this.loading = false
        this.progressText = ''
        this.progressText = ''
      }
    }
  }
}
</script>

<style scoped>
.search {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px 20px;
  transition: all 0.4s ease;
}

.search.compact {
  padding: 12px 0;
  align-items: flex-start;
  flex-wrap: wrap;
  gap: 8px;
}

h2 {
  font-size: 22px;
  color: #aaa;
  margin-bottom: 20px;
}

.mode-select {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}

.mode-select button {
  background: #16213e;
  border: 1px solid #0f3460;
  color: #aaa;
  padding: 6px 16px;
  border-radius: 20px;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.2s;
}

.mode-select button.active {
  background: #e94560;
  border-color: #e94560;
  color: white;
}

.mode-select button:hover:not(.active) {
  border-color: #e94560;
  color: #eee;
}
.search.compact .form {
  justify-content: flex-start;
}
.search.compact .mode-select {
  margin-bottom: 8px;
  flex-wrap: wrap;
}

.search.compact .mode-select button {
  padding: 3px 10px;
  font-size: 11px;
}
.form {
  display: flex;
  gap: 10px;
  transition: all 0.4s ease;
  flex-wrap: wrap;
  justify-content: center;
  flex-wrap: wrap;
  justify-content: center;
}

.search:not(.compact) input {
  padding: 14px 18px;
  font-size: 16px;
}

.search:not(.compact) button {
  padding: 14px 28px;
  font-size: 16px;
}

input {
  background: #16213e;
  border: 1px solid #0f3460;
  color: #eee;
  border-radius: 6px;
  padding: 8px 12px;
  font-size: 14px;
  width: 140px;
  transition: all 0.4s ease;
  outline: none;
  color-scheme: dark;
}

input:focus { border-color: #e94560; }

input[type="number"] { color-scheme: dark; }

button {
  background: #e94560;
  border: none;
  color: white;
  padding: 8px 18px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.4s ease;
}

button:hover { background: #c73652; }
button:disabled { opacity: 0.5; cursor: not-allowed; }

.error { color: #e94560; font-size: 13px; margin-top: 8px; }
.progress { color: #4ecca3; font-size: 13px; margin-top: 8px; }
.progress { color: #4ecca3; font-size: 13px; margin-top: 8px; }
</style>