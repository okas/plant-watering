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
        link () { return ['16x16', '32x32'].map(this.getFaviconModel) }
    },
    methods: {
        getFaviconModel (sz) {
            return {
                rel: 'shortcut icon',
                href: require(`../static/favicon-${sz}.png`),
                sizes: sz,
                type: 'image/png',
                undo: false
            }
        }
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
    background-color: #4e111103;
}
body, .default-text-color {
    color: #3e0101;
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
a.router-link-exact-active {
    text-shadow: 0px 0px 20px #00f9ff;
}
.clearfix:after {
    content: "";
    clear: both;
    display: table;
}
.float-left {
    float: left;
}
.float-right {
    float: right;
}
.float-align-right {
    float: right;
    text-align: right;
}
.high, .info, .warn, .crit, .disa, .highlight-full, .highlight,
.highlight-warn, .highlight-crit, .default-text-color
{
    transition: 0.5s color;
}
.high {
    color: #1deca0bd;
}
.info {
    color: #52e4b585;
}
.warn {
    color: #e9ec00f0;
}
.crit {
    color: #fb6c6cbd;
}
.disa {
    color: #c5beae;
}
.highlight-full {
    box-shadow: -1px -1px 1px 1px #1717e8bd;
}
.highlight {
    box-shadow: -1px -1px 1px 1px #1deca0bd;
}
.highlight-warn {
    box-shadow: -1px -1px 1px 1px #e9ec00f0;
}
.highlight-crit {
    box-shadow: -1px -1px 1px 1px #fb6c6cbd;
}
.highlight-disa {
    box-shadow: -1px -1px 1px 1px #c5beae;
}
.list-inline, .list-style-none {
    list-style-type: none;
    padding: 0;
}
.list-inline li {
    display: inline-block;
}
.status-small {
    font-size: 0.6em;
    color: gray;
}
</style>
