
<template>
  <div id="app">
    <img alt="Vue logo" src="./assets/icon.svg">
    <NetworkTopology />
    <TanChuanDialog></TanChuanDialog>
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
import TanChuanDialog from './TanChuanDialog.vue';

export default {
  name: 'App',
  components: {
    NetworkTopology,
    TanChuanDialog
  }
};
</script>

