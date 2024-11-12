
<template>
  <div id="app">
    <img alt="Vue logo" src="./assets/icon.svg">
    <NetworkTopology />
  </div>
</template>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
}
</style>

<script>
import NetworkTopology from './NetworkTopology.vue';

export default {
  name: 'App',
  components: {
    NetworkTopology
  }
};
</script>

