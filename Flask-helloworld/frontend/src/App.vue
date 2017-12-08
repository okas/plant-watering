<template>
<div id="app">
  <header>
    <router-link to="/"><img src="../static/logo_tk.png"></router-link>
  </header>
  <router-view/>
  <app-footer/>
</div>
</template>

<script>
import AppFooter from './AppFooter'

export default {
    name: 'app',
    components: { AppFooter }
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
h1 {
    font-size : 3em;
    color : FF2C00;
}

h1.toptitle {
    margin-bottom : 10px;
}

h2 {
    font-size : 1.5em;
    color : #FF8500;
}

h3 {
    font-size : 1.2em;
    color : #00B945;
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
