<template>
<footer @click="quickDashRevelaed=!quickDashRevelaed">
  <section>
    <ul class="permanent list-inline">
        <li>Copyright&nbsp;©</li>
        <li v-text="years"></li>
        <li>
          Powered by
          <a href="https://vuejs.org" target="_blank">
            <img src="../static/logo_vue.png"></a>
        </li>
        <li class="about">
          <router-link to="/about">
            About app</router-link>
          </li>
      </ul>
  </section>
  <section v-if="quickDashRevelaed">
    <code>
        <b>SocketIO Client ID: </b><span v-text="ioId" :class="ioId==='n/a'?'crit':''"/>
        <b>; is new: </b><span v-text="ioIsNew" :class="ioIsNew?'high':'crit'"/>
        </code>
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
            quickDashRevelaed: true
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
            ioIsNew: s => s.ioId !== s.ioId_prev
        })
    }
}
</script>

<style>
main {
    margin-bottom: 45px;
}
</style>

<style scoped>
.about {
    position: fixed;
    right: 1.5em;
}
footer {
    font-size: 0.9em;
    text-align: center;
    position: fixed;
    bottom: 0;
    clear: both;
    width: 100%;
    left: 2px;
    right: 2px;
    border-top-left-radius: 30px;
    border-top-right-radius: 30px;
    border-top: #8c8b8b solid 1px;
    background-color: #73fbce17;
}
section {
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
}
img {
    vertical-align: middle;
    width: 17px;
}
</style>
