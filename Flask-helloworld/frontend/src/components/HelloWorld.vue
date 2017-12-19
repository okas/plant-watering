<template>
<section class="hello">
  <h1 class="toptitle">Welcome to Saar family's Smart Home App!</h1>
  <h2>Plant Irrigation</h2>
  <ul class="list-inline">
    <li>
      <router-link :to="{name: 'plantwatcher'}">
        Check plant watcher system
      </router-link>
    </li>
  </ul>
  <hr/>
  <h2>Essential Links</h2>
  <ul class="list-inline">
    <li><a href="https://vuejs.org" target="_blank">Core Docs</a></li>
    <li><a href="https://forum.vuejs.org" target="_blank">Forum</a></li>
    <li><a href="https://chat.vuejs.org" target="_blank">Community Chat</a></li>
    <li><a href="https://twitter.com/vuejs" target="_blank">Twitter</a></li>
    <br>
    <li><a href="http://vuejs-templates.github.io/webpack/" target="_blank">Docs for This Template</a></li>
  </ul>
  <h2>Ecosystem</h2>
  <ul class="list-inline">
    <li><a href="http://router.vuejs.org/" target="_blank">vue-router</a></li>
    <li><a href="http://vuex.vuejs.org/" target="_blank">vuex</a></li>
    <li><a href="http://vue-loader.vuejs.org/" target="_blank">vue-loader</a></li>
    <li><a href="https://github.com/vuejs/awesome-vue" target="_blank">awesome-vue</a></li>
  </ul>
</section>
</template>

<script>
export default {
    name: 'HelloWorld'
}
</script>

<style scoped>
li {
  margin: 0 10px;
}
</style>
