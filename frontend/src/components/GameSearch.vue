<template>
  <div class="search" :class="{ compact: hasResults }">
    <h2 v-if="!hasResults">Find Your Games</h2>
    <div class="form">
      <input ref="usernameInput" v-model="username" placeholder="Chess.com username" />
      <input v-model.number="year" type="number" placeholder="Year" />
      <input v-model.number="month" type="number" placeholder="Month" />
      <button @click="search" :disabled="loading">
        {{ loading ? 'Loading...' : 'Search' }}
      </button>
    </div>
    <p v-if="error" class="error">{{ error }}</p>
  </div>
</template>

<script>
import axios from 'axios'

const API = 'http://localhost:5000'

export default {
  name: 'GameSearch',
  emits: ['games-loaded'],
  props: {
    hasResults: { type: Boolean, default: false }
  },
  data() {
    return {
      username: '',
      year: new Date().getFullYear(),
      month: new Date().getMonth() + 1,
      loading: false,
      error: null
    }
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
    async search() {
      if (!this.username) return
      this.loading = true
      this.error = null
      try {
        const res = await axios.post(`${API}/games`, {
          username: this.username,
          year: this.year,
          month: this.month
        })
        this.$emit('games-loaded', {
          games: res.data.games,
          username: this.username,
          year: this.year,
          month: this.month
        })
      } catch (err) {
        this.error = err.response?.data?.error || 'Something went wrong'
      } finally {
        this.loading = false
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
}

h2 {
  font-size: 22px;
  color: #aaa;
  margin-bottom: 20px;
}

.form {
  display: flex;
  gap: 10px;
  transition: all 0.4s ease;
}

.search:not(.compact) input {
  padding: 14px 18px;
  font-size: 16px;
  width: 220px;
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
</style>