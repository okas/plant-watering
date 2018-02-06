<template>
<section>
<header>
  <h2 class="has-text-centered">
    Control blinds</h2>
</header>
<article class="is-fluid container has-text-centered">
  <h3>
    Mom&amp;Dad's room</h3>
  <section class="box is-fluid container has-text-centered">
    <div class="columns is-vcentered">
      <div class="column has-text-centered">
        <button class="button" @click="wsUp">
          <f-a icon="chevron-up"/>
        </button>
      </div>
    </div>
    <div class="columns is-vcentered">
      <div class="column has-text-centered">
        <button class="button" @click="wsStop">
          <f-a :icon="['far', 'square']"/>
        </button>
      </div>
    </div>
    <div class="columns is-vcentered">
      <div class="column has-text-centered">
        <button class="button" @click="wsDown">
          <f-a icon="chevron-down"/>
        </button>
      </div>
    </div>
  </section>
</article>
</section>
</template>

<script>
const ns = 'windowblind'
export default {
    name: 'windowblind-layout',
    head: { title: { inner: 'Window blinds' } },
    socket: {
        namespace: `/${ns}`,
        options: { multiplexNamespace: true },
        events: {
            connect (msg) {
                console.log(`connected to ns [${ns}]`)
            }
        }
    },
    methods: {
        wsUp () {
            this.$socket.emit('up')
        },
        wsStop () {
            this.$socket.emit('stop')
        },
        wsDown () {
            this.$socket.emit('down')
        }
    }
}
</script>

<style lang="scss" scoped>
.box {
    width: 5rem;
}
</style>
