<template>
<main class="content clearfix">
    <header>
        <h1>
            Plant Irrigation Module</h1>
    </header>
    <aside id="irrigation_aside">
        <section>
            <h4>
                Interests...</h4>
            <ul class="list-style-none clearfix">
                <li>
                    <span class="float-left">
                        Service:</span>
                    <span v-text="state" :class="generalStatusClass" class="float-align-right"/>
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
const { mapState } = createNamespacedHelpers('irrigation')

export default {
    name: 'IrrigationLayout',
    computed: {
        generalStatusClass () {
            switch (this.state) {
            case 'on': return 'highlight'
            case 'off': return 'highlight-warn'
            default: return 'highlight-crit'
            }
        },
        ...mapState({
            state: 'state',
            waterLevel (s) {
                return ['on', 'off'].includes(s.state) && s.waterLevel
                    ? s.waterLevel
                    : 'n/a'
            },
            waterConsum (s) {
                return this._getWaterLevelState(s)
                    ? `${Math.round(s.waterConsum)}ml`
                    : 'n/a'
            },
            waterLeveLClass (s) {
                if (s.state !== 'on') {
                    return 'highlight-disa'
                }
                switch (s.waterLevel) {
                case 'full': return 'highlight-full'
                case 'normal': return 'highlight'
                case 'low': return 'highlight-warn'
                case 'empty': return 'highlight-crit'
                default: return 'highlight-disa'
                }
            },
            waterConsumClass (s) {
                return this._getWaterLevelState(s) && s.waterConsum > 0
                    ? 'highlight'
                    : 'highlight-disa'
            }
        })
    },
    methods: {
        _getWaterLevelState: s => s.state === 'on' && this.waterConsum !== 'n/a'
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
    padding-bottom: 10px;
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
