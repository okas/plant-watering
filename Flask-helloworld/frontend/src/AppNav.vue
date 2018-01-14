<template>
<nav class="navbar is-fixed-top is-transparent" role="navigation" arial-label="main nvigation">
  <div class="navbar-brand">
    <router-link to="/" class="navbar-item" exact>
      <h2>Saar</h2>
      <img src="../static/logo_tk.png"/>
    </router-link>
    <div
      @click="toggleMenu"
      :class="isActiveClass"
      class="button navbar-burger"
      data-target="navMenu">
      <span/><span/><span/>
    </div>
  </div>
  <div id="navMenu" class="navbar-menu" :class="isActiveClass">
    <div class="navbar-start">
      <div class="navbar-item has-dropdown is-hoverable" aria-label="dropdown navigation">
        <router-link :to="{name: 'irrigation'}" class="navbar-link">
          Plant watcher</router-link>
        <div class="navbar-dropdown is-boxed">
          <a class="navbar-item">
            Show tank</a>
          <a class="navbar-item">
            Water statistics</a>
          <hr class="navbar-divider">
          <router-link :to="{name: 'irrigationservice'}" class="navbar-item">
            Manage service</router-link>
        </div>
      </div>
      <div class="navbar-item has-dropdown is-hoverable" aria-label="dropdown navigation">
        <a class="navbar-link">
          Windows blinds</a>
        <div class="navbar-dropdown is-boxed">
          <a class="navbar-item">
            Do something 1 </a>
          <a class="navbar-item">
            Do something 2 </a>
          <hr class="navbar-divider">
          <a class="navbar-item">
            Manager service</a>
        </div>
      </div>
    </div>
    <div class="navbar-end">
      <router-link to="/about" class="navbar-item">
        About app</router-link>
    </div>
  </div>
</nav>
</template>

<script>
export default {
    name: 'app-nav',
    data () { return { navIsActive: false } },
    computed: {
        isActiveClass () {
            return this.navIsActive ? 'is-active' : ''
        }
    },
    methods: {
        toggleMenu () {
            this.navIsActive = !this.navIsActive
        }
    },
    watch: {
        $route () {
            this.navIsActive = false
        }
    },
    beforeMount () {
        document.querySelector('html').classList.add('has-navbar-fixed-top')
    }
}
</script>

<style scoped>
img {
  height: 40px;
}
</style>
