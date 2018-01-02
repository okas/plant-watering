<template>
<main class="content clearfix">
    <header>
        <h1 class="toptitle">
            <router-link :to="{name: 'irrigation'}">
                Plant Irrigation Module
                </router-link>
        </h1>
    </header>
    <aside id="irrigation_aside">
        <section>
            <h4>Interests...</h4>
            <ul class="list-style-none">
                <li><a href="">Show tank</a></li>
                <li><a href="">Water statistics</a></li>
                <li>
                    <router-link :to="{name: 'irrigationservice'}">
                        Manage service
                        </router-link>
                    </li>
            </ul>
        </section>
        <section>
            <h4>Service state</h4>
            <ul class="list-style-none">
                <li>Service:
                    <span v-text="irrigationState" :class="stateClass"/>
                    </li>
                <li>Water level:
                    <span v-text="waterLevel" :class="waterLeveLClass"/>
                    </li>
            </ul>
        </section>
    </aside>
    <slot/>
</main>
</template>

<script>
import { mapState } from 'vuex'

export default {
    name: 'IrrigationLayout',
    computed: {
        ...mapState('irrigation/', {
            irrigationState: s => s.statusObj.state || 'n/a',
            waterLevel: s => s.statusObj.waterLevel || 'n/a',
            stateClass: s => {
                switch (s.statusObj.state) {
                case 'on': return 'highlight'
                case 'off': return 'highlight-warn'
                default: return 'highlight-crit'
                }
            },
            waterLeveLClass: s => {
                switch (s.statusObj.waterLevel) {
                case 'full': return 'highlight-full'
                case 'normal': return 'highlight'
                case 'low': return 'highlight-warn'
                default: return 'highlight-crit'
                }
            }
        })
    }
}
</script>

<style scoped>
article {
    margin-bottom: 1px;
}
article:first-of-type {
    border-top: 1px solid lightgrey;
}
article:not(:last-of-type) {
    border-bottom: 1px solid lightgrey;
}
.content > aside {
    float: left;
    margin: 0 1.0%;
    width: 14.0%;
    background-color : #effcf8;
    border: 1px solid #A8A8A8;
    border-radius: 15px;
    padding: 10px;
    text-align: left;
    white-space: nowrap;
}
.content > aside h4 {
    margin: 0 auto 5% 0;
}
.content > aside ul {
    margin: 0;
}
aside > section:not(:first-child) {
    margin-top: 12.5%;
    padding-top: 10px;
    border-top: 1px solid #A8A8A8;
}
.content > section {
    float: right;
    width: 77.4%;
    margin: 0 1.0%;
    border: 1px solid lightgrey;
    border-radius: 15px;
    padding: 0 10px 10px;
}
</style>
