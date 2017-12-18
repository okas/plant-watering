<template>
<div id="app-layout" class="clearfix">
  <app-header/>
  <main>
    <router-view/>
  </main>
  <app-footer/>
</div>
</template>

<script>
import AppHeader from './AppHeader'
import AppFooter from './AppFooter'

export default {
    name: 'app-layout',
    components: { AppHeader, AppFooter }
}
</script>

<style>
main {
  display:block; /*IE11*/
}
body {
  clear: both;
  margin: 10px auto 0;
  width: 960px;
  background-color: #0a21880a;
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
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
.clearfix:after {
   content: "";
   clear: both;
   display: table;
}
a.router-link-exact-active {
   text-shadow: 0px 0px 20px #00f9ff;
}
.highlight {
  box-shadow: -1px -1px 1px 1px #52e4b585;
}
.highlight-neg {
  box-shadow: -1px -1px 1px 1px #e2181863;
}
.list-inline, .list-style-none {
    list-style-type: none;
    padding: 0;
}
.list-inline li {
  display: inline-block;
}
</style>
