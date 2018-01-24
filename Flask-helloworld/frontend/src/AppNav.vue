<template>
<nav class="navbar is-fixed-top" role="navigation" arial-label="main nvigation" :class="scroll">
  <div class="navbar-brand">
    <router-link to="/" class="navbar-item" exact>
      <h2>Saar</h2>
      <img id="app_logo" src="../static/logo_tk.png"/>
    </router-link>
    <div class="button navbar-burger" data-target="navMenu" @click="toggle" :class="activeCls">
      <span/><span/><span/>
    </div>
  </div>
  <div id="navMenu" class="navbar-menu" :class="activeCls">
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
    data () {
        return {
            isActive: false,
            lastY: 0,
            scroll: ''
        }
    },
    computed: {
        activeCls () {
            return this.isActive ? 'is-active' : ''
        }
    },
    methods: {
        toggle () {
            this.isActive = !this.isActive
        },
        handleScroll () {
            const y = window.scrollY
            this.scroll = y > this.lastY ? 'scrollUp' : ''
            this.lastY = y
        }
    },
    watch: {
        $route () {
            this.isActive = false
        }
    },
    created () {
        document.querySelector('html').classList.add('has-navbar-fixed-top')
        window.addEventListener('scroll', this.handleScroll)
    },
    destroyed () {
        window.removeEventListener('scroll', this.handleScroll)
    }
}
</script>

<style lang="scss" scoped>
nav {
    transition: all 0.5s;
    &.scrollUp {
        transform: translateY(-$navbar-height);
    }
    #app_logo {
      height: 40px;
    }
}
</style>
