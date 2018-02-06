<template>
<main class="content is-clearfix">
    <header class="has-text-centered">
        <h1>
            Plant Irrigation Module</h1>
    </header>
    <aside id="irrigation_aside">
        <section>
            <h5>
                Overview</h5>
            <ul class="list-style-none is-clearfix">
                <li class="tags has-addons">
                    <span class="tag is-pulled-left is-white">
                        Service</span>
                    <span
                        class="tag is-rounded"
                        :class="generalStatusClass"
                        v-if="showSvcState"
                        v-text="state"/>
                    <router-link
                        class="tag is-rounded"
                        :class="generalStatusClass"
                        :to="{name: 'irrigationservice'}"
                        v-else>
                        see error info</router-link>
                </li>
                <li class="tags has-addons">
                    <span class="tag is-pulled-left is-white">
                        Water level</span>
                    <span
                        class="tag is-rounded"
                        :class="waterLeveCls"
                        v-text="waterLevel"/>
                </li>
                <li class="tags has-addons">
                    <span class="tag is-pulled-left is-white">
                        Water used</span>
                    <span
                        class="tag is-rounded"
                        :class="waterConsumCls"
                        v-text="waterConsum"/>
                </li>
            </ul>
        </section>
    </aside>
    <router-view/>
</main>
</template>

<script>
import { createNamespacedHelpers } from 'vuex'

const ns = 'irrigation'
const { mapState, mapMutations } = createNamespacedHelpers(ns)

export default {
    name: 'irrigation-layout',
    computed: {
        generalStatusClass () {
            switch (this.state) {
            case 'on': return 'is-success'
            case 'off': return 'is-warning'
            default: return 'is-danger'
            }
        },
        ...mapState({
            state: 'state',
            waterLevel (s) {
                return this.showSvcState && s.waterLevel
                    ? s.waterLevel
                    : 'n/a'
            },
            waterConsum (s) {
                return this._getWaterLevelState(s)
                    ? `${Math.round(s.waterConsum)}ml`
                    : 'n/a'
            },
            waterLeveCls (s) {
                if (s.state !== 'on') {
                    return 'is-light'
                }
                switch (s.waterLevel) {
                case 'full': return 'is-info'
                case 'normal': return 'is-success'
                case 'low': return 'is-warning'
                case 'empty': return 'is-danger'
                default: return 'is-light'
                }
            },
            waterConsumCls (s) {
                return this._getWaterLevelState(s) && s.waterConsum > 0
                    ? 'is-success'
                    : 'is-light'
            },
            showSvcState (s) {
                return ['on', 'off'].includes(s.state)
            }
        })
    },
    socket: {
        namespace: `/${ns}`,
        options: { multiplexNamespace: true },
        events: {
            connect () {
                console.info(`~ ~ [${ns}] socket connected`)
                this.setApiOnConnect(this.$socket.id)
            },
            disconnect (reason) {
                // might not work correctly or aside retains stat state based on store.
                // result is taht if browsing back to this route then aside already
                // has 'last' connected state already waiting.
                console.log(`~ ! ~ [irrigation] socket disconnected, reson: [${reason}].`)
                this.setApiOnDisconnect(this.$socket.id)
            },
            ...mapMutations({
                service_status: 'setServiceStatus',
                water_supply_state: 'setServiceStatus',
                water_consumed_changed: 'setServiceStatus'
            })
        }
    },
    methods: {
        _getWaterLevelState: s => s.state === 'on' && this.waterConsum !== 'n/a',
        ...mapMutations([
            'setApiOnConnect',
            'setApiOnDisconnect'
        ])
    }
}
</script>

<style lang="scss" scoped>
article {
    margin-bottom: 1px;
    :first-of-type {
        border-top: 1px solid lightgrey;
    }
    :not(:last-of-type) {
        border-bottom: 1px solid lightgrey;
        padding-bottom: 10px;
    }
}

.content {
    > aside {
        float: left;
        margin: 0 1.0%;
        width: 18.0%;
        background-color : #effcf8;
        border: 1px solid #A8A8A8;
        border-radius: 15px;
        padding: 10px;
        text-align: left;
        white-space: nowrap;
        h5 {
            margin: 0 auto 5% 0;
        }
        ul {
            margin: 0;
            .tags {
                margin: 0;
                .tag {
                    transition: 0.5s color;
                    transition: 0.5s background-color;
                }
            }
        }
        > section:not(:first-child) {
            margin-top: 12.5%;
            padding-top: 10px;
            border-top: 1px solid #A8A8A8;
        }
    }
    > section {
        float: right;
        width: 77.4%;
        margin: 0 1.0%;
        border: 1px solid lightgrey;
        border-radius: 15px;
        padding: 0 10px 10px;

    }
}
</style>
