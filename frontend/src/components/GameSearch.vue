<template>
  <div class="search">
    <h2>Find Your Games</h2>
    <div class="form">
      <input v-model="username" placeholder="Chess.com username" />
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
  data() {
    return {
      username: '',
      year: new Date().getFullYear(),
      month: new Date().getMonth() + 1,
      loading: false,
      error: null
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