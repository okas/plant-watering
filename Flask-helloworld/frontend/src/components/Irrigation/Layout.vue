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
                <li>
                    <a href="">
                        Show tank</a></li>
                <li>
                    <a href="">
                        Water statistics</a></li>
                <li>
                    <router-link :to="{name: 'irrigationservice'}">
                        Manage service</router-link></li>
            </ul>
        </section>
        <section>
            <h4>
                Service state</h4>
            <ul class="list-style-none clearfix">
                <li>
                    <span class="float-left">
                        Service:</span>
                    <span v-text="generalStatus" :class="generalStatusClass" class="float-align-right"/>
                    </li>
                <li>
                    <span class="float-left">
                        Water level:</span>
                    <span v-text="waterLevel" :class="waterLeveLClass" class="float-align-right"/>
                    </li>
                <li>
                    <span class="float-left">
                        Water used:</span>
                    <span v-text="waterConsum" :class="waterConsumClass" class="float-align-right"/>
                    </li>
            </ul>
        </section>
    </aside>
    <slot/>
</main>
</template>

<script>
import { createNamespacedHelpers } from 'vuex'
const { mapState, mapGetters } = createNamespacedHelpers('irrigation')

export default {
    name: 'IrrigationLayout',
    computed: {
        generalStatusClass () {
            switch (this.generalStatus) {
            case 'on': return 'highlight'
            case 'off': return 'highlight-warn'
            default: return 'highlight-crit'
            }
        },
        ...mapState({
            waterLevel (s) {
                return ['on', 'off'].includes(this.generalStatus) && s.statusObj.waterLevel
                    ? s.statusObj.waterLevel
                    : 'n/a'
            },
            waterConsum (s) {
                return this._getWaterLevelState(s)
                    ? `${Math.round(s.statusObj.waterConsum)}ml`
                    : 'n/a'
            },
            waterLeveLClass (s) {
                if (this.generalStatus !== 'on') {
                    return 'highlight-disa'
                }
                switch (s.statusObj.waterLevel) {
                case 'full': return 'highlight-full'
                case 'normal': return 'highlight'
                case 'low': return 'highlight-warn'
                case 'empty': return 'highlight-crit'
                default: return 'highlight-disa'
                }
            },
            waterConsumClass (s) {
                return this._getWaterLevelState(s) && s.statusObj.waterConsum > 0
                    ? 'highlight'
                    : 'highlight-disa'
            }
        }),
        ...mapGetters(['generalStatus'])
    },
    methods: {
        _getWaterLevelState: s => s.statusObj.state && s.statusObj.waterConsum !== 'n/a'
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
