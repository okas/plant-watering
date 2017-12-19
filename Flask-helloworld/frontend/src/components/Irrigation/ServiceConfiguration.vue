<template>
<article>
    <header>
        <h3>Irrigation service cofiguration</h3>
        <p>
            You can evaluate and change configuration.<br/>
            Service restart will be done only if service is started already.
            <br/> <code>TODO: disable save link, when no config loaded</code>
        </p>
        <ul class="list-inline">
            <li v-if="status" v-text="status"></li>
        </ul>
    </header>
    <ul class="list-inline activities">
        <li><a
            href=""
            @click.prevent="apiGetServiceConfig"
            v-text="state">
        </a></li>
        <li><a
                href=""
                @click.prevent="modify = !modify"
                :class="stateClass">
                modify
        </a></li>
        <li v-if="hasConf"><a href="" @click.prevent="apiUpdateServiceConfig">
            save and restart service
        </a></li>
    </ul>
    <tree-view
        v-if="hasConf"
        :data="configData.content"
        :options="{
            rootObjectKey: configData.filename,
            maxDepth: 3,
            modifiable: this.modify}"
        @change-data="onChangeData"/>
</article>
</template>

<script>
import Vue from 'vue'
import axios from 'axios'
import TreeView from 'vue-json-tree-view'
Vue.use(TreeView)

const apiConf = { headers: { 'Content-Type': 'application/json' } }

export default {
    name: 'IrrigationServiceConfiguration',
    data () {
        return {
            status: '',
            configData: '',
            modify: false
        }
    },
    methods: {
        onChangeData (updatedDocument) {
            this.configData.content = updatedDocument
        },
        apiGetServiceConfig () {
            this.modify = false
            axios.get('/api/irrigation/service-config')
                .then(resp => {
                    this.status = ''
                    this.configData = resp.data
                })
                .catch(console.log)
        },
        apiUpdateServiceConfig () {
            this.modify = false
            let filename = this.configData.filename || ''
            let api = `/api/irrigation/service-config/${filename}/update-restart`
            axios.put(api, this.configData.content, apiConf)
                .then(resp => {
                    this.status = resp.status !== 204 ? resp.data.message : ''
                })
                .catch((err) => {
                    if (!this.inProduction) {
                        this.status = err.response.data.message
                        console.log(err)
                    }
                })
        }
    },
    computed: {
        hasConf () {
            return this.configData
        },
        stateClass () {
            if (this.modify) {
                return 'highlight'
            } else if (!this.modify) {
                return 'highlight-neg'
            } else {
                return 'error'
            }
        },
        state () {
            return !this.hasConf ? 'load from server' : 'reload from server'
        },
        inProduction () {
            return process.env.NODE_ENV === 'production'
        }
    }
}
</script>

<style scoped>
.tree-view-wrapper, pre {
    text-align: left;
}
.activities > *:not(:first-child)::before{
    content: " | ";
}
hr {
    border-style: ridge;
}
</style>
