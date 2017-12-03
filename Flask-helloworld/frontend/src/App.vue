<template>
  <div id="app">
    <router-link to="/">
      <img src="./assets/logo.png" width="75px">
    </router-link>
    <router-view/>
  </div>
</template>

<script>
export default {
    name: 'app'
}
</script>

<style>
h1, h2 {
  font-weight: normal;
}
a {
  color: #42b983;
}
#app {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
</style>
