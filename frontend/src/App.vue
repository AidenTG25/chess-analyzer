<template>
  <div id="app">
    <h1>Chess Analyzer</h1>
    <GameSearch @games-loaded="onGamesLoaded" />
    <pre>{{ games }}</pre>
  </div>
</template>

<script>
import GameSearch from './components/GameSearch.vue'

export default {
  name: 'App',
  components: { GameSearch },
  data() {
    return {
      games: [],
      username: '',
      year: null,
      month: null
    }
  },
  methods: {
    onGamesLoaded({ games, username, year, month }) {
      this.games = games
      this.username = username
      this.year = year
      this.month = month
    }
  }
}
</script>