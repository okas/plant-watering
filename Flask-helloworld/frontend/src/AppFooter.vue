<template>
<footer @click="quickDashRevelaed=!quickDashRevelaed">
  <section class="permanent">
    <ul class="list-inline">
    <li>Copyright&nbsp;©</li>
    <li v-text="years"></li>
    <li>
      Powered by
      <a href="https://vuejs.org" target="_blank">
      <img src="../static/logo_vue.png"></a>
    </li>
    </ul>
  </section>
  <section v-if="quickDashRevelaed" class="debug tags has-addons">
    <div class="tag is-white">
      <b>SocketIO Client ID:&nbsp;</b>
      <span v-text="ioId" :class="ioIdClass"/>
    </div>
    <div :class="ioIsNewClass" class="tag is-rounded">
      <b v-text="ioIsNew"/>
    </div>
  </section>
</footer>
</template>

<script>
import { createNamespacedHelpers } from 'vuex'
const { mapState } = createNamespacedHelpers('irrigation')
// const debug = process.env.NODE_ENV !== 'production'

export default {
    name: 'app-footer',
    data () {
        return {
            quickDashRevelaed: false
        }
    },
    computed: {
        years () {
            const startYear = 2017
            const currentTear = new Date().getFullYear()
            return currentTear !== startYear
                ? `${startYear}-${currentTear}`
                : startYear
        },
        ...mapState({
            ioId: s => s.ioId || 'n/a',
            ioIdClass: s => s.ioId ? '' : 'has-text-danger',
            ioIsNew: s => s.ioId !== s.ioId_prev ? 'new' : 'old',
            ioIsNewClass: s => s.ioId !== s.ioId_prev ? 'is-success' : 'is-danger'
        })
    }
}
</script>

<style>
main {
    margin-bottom: 45px;
}
</style>

<style lang="scss" scoped>
footer {
    font-size: 0.9em;
    text-align: center;
    position: fixed;
    bottom: 0;
    clear: both;
    width: 100%;
    left: 0px;
    right: 0px;
    border-top-left-radius: 30px;
    border-top-right-radius: 30px;
    border-top: #8c8b8b solid 1px;
    background-color: rgba(#73fbce, 0.08);
    transition: 0.5s color;
    transition: 0.5s background-color;
    .permanent {
        margin: 10px 0;
        text-shadow:
            0 0 20px hsla(0, 0%, 100%, 1),
            0 0 20px hsla(0, 0%, 100%, 1),
            0 0 20px hsla(0, 0%, 100%, 1),
            0 0 20px hsla(0, 0%, 100%, 1),
            0 0 20px hsla(0, 0%, 100%, 1),
            0 0 20px hsla(0, 0%, 100%, 1),
            0 0 20px hsla(0, 0%, 100%, 1),
            0 0 20px hsla(0, 0%, 100%, 1),
            0 0 20px hsla(0, 0%, 100%, 1),
            0 0 20px hsla(0, 0%, 100%, 1),
            0 0 20px hsla(0, 0%, 100%, 1),
            0 0 19px hsla(0, 0%, 100%, 1),
            0 0 18px hsla(0, 0%, 100%, 1),
            0 0 17px hsla(0, 0%, 100%, 1),
            0 0 16px hsla(0, 0%, 100%, 1),
            0 0 15px hsla(0, 0%, 100%, 1),
            0 0 14px hsla(0, 0%, 100%, 1),
            0 0 13px hsla(0, 0%, 100%, 1),
            0 0 12px hsla(0, 0%, 100%, 1),
            0 0 11px hsla(0, 0%, 100%, 1),
            0 0 10px hsla(0, 0%, 100%, 1),
            0 0 09px hsla(0, 0%, 100%, 1),
            0 0 08px hsla(0, 0%, 100%, 1),
            0 0 07px hsla(0, 0%, 100%, 1),
            0 0 06px hsla(0, 0%, 100%, 1),
            0 0 05px hsla(0, 0%, 100%, 1),
            0 0 04px hsla(0, 0%, 100%, 1),
            0 0 03px hsla(0, 0%, 100%, 1),
            0 0 02px hsla(0, 0%, 100%, 1),
            0 0 01px hsla(0, 0%, 100%, 1);
        ul {
            margin: 0;
        }
        img {
            vertical-align: middle;
            width: 17px;
        }
    }
    .debug.tags {
        justify-content: center;
        &:last-child {margin-bottom: -3px;}
    }
}
</style>
