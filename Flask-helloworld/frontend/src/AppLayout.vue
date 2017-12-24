<template>
<div id="app-layout" class="clearfix">
  <app-header/>
  <router-view/>
  <app-footer/>
</div>
</template>

<script>
import AppHeader from './AppHeader'
import AppFooter from './AppFooter'

export default {
    name: 'app-layout',
    components: { AppHeader, AppFooter },
    head: {
        link () {
            return ['16x16', '32x32'].map(sz => {
                return {
                    rel: 'shortcut icon',
                    href: require(`../static/favicon-${sz}.png`),
                    sizes: sz,
                    type: 'image/png',
                    undo: false
                }
            })
        },
        style: [
            {
                type: 'text/css',
                inner: 'body { background-color: #4e111103; color: #3e0101;}',
                undo: false
            }
        ]
    }
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
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
}
h1, h2 {
  font-weight: normal;
}
h1 {
    font-size : 3em;
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
  color: #7e008c;
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
