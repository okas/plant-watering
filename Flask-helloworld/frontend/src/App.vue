<template>
<main id="app">
  <router-link to="/">
    <img src="../static/logo_tk.png">
  </router-link>
  <router-view/>
</main>
</template>

<script>
export default {
    name: 'app'
}
</script>

<style>
main {
  display:block; /*IE11*/
}
body {
  background-color: #0a21880a;
}
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
  margin-top: 30px;
}
.clearfix:after {
   content: "";
   clear: both;
   display: table;
}
</style>
