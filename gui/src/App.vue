<template>
  <div>
    <BoincResults/>
  </div>
</template>

<script>
import BoincResults from './components/BoincResults.vue'

export default {
  name: 'App',
  components: {
    BoincResults
  }
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
</style>
