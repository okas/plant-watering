<template>
<div id="app-layout" class="is-clearfix">
  <app-nav/>
  <app-header/>
  <router-view/>
  <app-footer/>
</div>
</template>

<script>
import AppNav from './AppNav'
import AppHeader from './AppHeader'
import AppFooter from './AppFooter'

export default {
    name: 'app-layout',
    components: { AppNav, AppHeader, AppFooter },
    head: {
        link () { return ['16', '32'].map(this.getFaviconModel) }
    },
    methods: {
        getFaviconModel (size) {
            const sz = `${size}x${size}`
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

<style lang="scss">
@import "~bulma/sass/utilities/initial-variables";
@import "~bulma/sass/utilities/functions";
@import "~@globalsScss";
@import "~bulma/sass/utilities/derived-variables.sass";
@import "~bulma";
@import "~bulma-extensions";

body {
    clear: both;
    margin: 10px auto 0;
    width: 960px;
    font-family: 'Avenir', Helvetica, Arial, sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    text-align: center;
    background-color: rgba(#4e1111, 0.02);
    color: $default-text-color;
    main {
        display:block; /*IE11*/
    }
    .is-pulled-aligned-right {
        @extend .is-pulled-right;
        text-align: right;
    }
    .default-text-color {
        color: $default-text-color;
    }
    .router-link-active {
        text-shadow: 0px 0px 20px #269294;
    }
    .router-link-exact-active {
        text-shadow: 0px 0px 20px #00f9ff;
    }
    .list-inline, .list-style-none {
        list-style-type: none;
        padding: 0;
    }
    .list-inline > * {
        display: inline-block;
    }
    .status-small {
        font-size: 0.6em;
        color: gray;
    }
}
</style>
