<template>
<article>
    <header>
        <h3>Irrigation service cofiguration</h3>
        <p>
            You can evaluate and change configuration.
        </p>
        <ul class="list-inline">
            <li v-if="status" v-text="status"></li>
        </ul>
    </header>
    <ul class="list-inline activities">
        <li><a href="#" @click.prevent="reload" v-text="state"></a></li>
        <li><a
                href="#"
                @click.prevent="modify = !modify"
                :class="stateClass">
                modify
            </a></li>
        <li><a href="#" @click.prevent="reload">save and restart service</a></li>
    </ul>
    <tree-view
        v-if="configData !== ''"
        :data="configData.content"
        :options="{
            rootObjectKey: configData.filename,
            maxDepth: 3,
            modifiable: this.modify}"
        @change-data="onChangeData"/>
    <hr/>
    <pre v-text="configData"></pre>
</article>
</template>

<script>
import axios from 'axios'
import Vue from 'vue'
import TreeView from 'vue-json-tree-view'
Vue.use(TreeView)

export default {
    name: 'ServiceConfiguration',
    data () {
        return {
            status: '',
            configData: '',
            modify: false
        }
    },
    methods: {
        reload () {
            this.modify = false
            this.apiGetServiceConfig()
        },
        onChangeData (updatedDocument) {
            this.configData.content = updatedDocument
        },
        apiGetServiceConfig () {
            axios.get('/api/irrigation/service-config')
                .then(resp => {
                    this.status = ''
                    this.configData = resp.data
                })
                .catch(console.log)
        }
    },
    computed: {
        stateClass: function () {
            if (this.modify) {
                return 'highlight'
            } else if (!this.modify) {
                return 'highlight-neg'
            } else {
                return 'error'
            }
        },
        state: function () {
            return !this.configData
                ? 'load from server'
                : 'reload from server'
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
