<template>
<main>
  <h1 class="toptitle">Saar family's Smart Home</h1>
  <h2>Plant Irrigation</h2>
  <ul class="list-inline">
    <li>
      <router-link :to="{name: 'irrigation'}">
        Plant watcher system</router-link>
        </li>
    <li>
      <router-link to="/">
        Windows blinds system</router-link>
        </li>
  </ul>
</main>
</template>

<script>
export default {
    name: 'HelloWorld',
    head: { title: { inner: 'Home' } }
}
</script>

<style scoped>
li {
  margin: 0 10px;
}
</style>
