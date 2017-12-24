<template>
<article>
    <header>
        <h3>Irrigation service cofiguration</h3>
        <p>
            You can evaluate and change configuration.<br/>
            Service restart will be done only if service is started already.
        </p>
        <ul class="list-inline">
            <li v-if="status" v-text="status"></li>
        </ul>
    </header>
    <ul class="list-inline activities">
        <li>
            <a href="" @click.prevent="apiGetServiceConfig" v-text="state"></a>
        </li>
        <li v-if="hasConf">
            <a href="" @click.prevent="modify=!modify" :class="this.modify ? 'highlight': 'highlight-neg'">
                modify</a>
        </li>
        <li v-if="hasConf && wortSaving">
            <a href="" @click.prevent="apiUpdateServiceConfig">
                save and restart service</a>
        </li>
    </ul>
    <ul v-if="hasConf" class="list-inline activities">
        <li>
            <a href="" @click.prevent="addPlant">
                add new plant</a>
        </li>
        <li>
            <label for="p_r">remove plant</label>
            <select id="p_r" v-model="plantToRemove" :disabled="disableRemove" :title="selectTitle">
                <option :value="null">
                    ...chose...</option>
                <option
                    v-for="p in configData.content.plants_args_list"
                    v-text="p.name"
                    :key="p.name"/>
            </select>
        </li>
    </ul>
    <p>
        <tree-view
            v-if="hasConf"
            :data="configData.content"
            @change-data="onTreeViewDataChange"
            :options="{
                rootObjectKey: configData.filename,
                maxDepth: 3,
                modifiable: this.modify}"/>
    </p>
</article>
</template>

<script>
import Vue from 'vue'
import axios from 'axios'
Vue.use(require('vue-json-tree-view'))

const apiConf = { headers: { 'Content-Type': 'application/json' } }
var counter = 0

export default {
    name: 'IrrigationServiceConfiguration',
    props: ['serviceState'],
    data () {
        return {
            status: '',
            configData: '',
            modify: false,
            wortSaving: false
        }
    },
    methods: {
        apiGetServiceConfig () {
            this.modify = this.wortSaving = false
            axios.get('/api/irrigation/service-config')
                .then(resp => {
                    this.status = ''
                    this.configData = resp.data
                })
                .catch(console.log)
        },
        apiUpdateServiceConfig () {
            if (!this.wortSaving) {
                return
            }
            this.modify = this.wortSaving = false
            let filename = this.configData.filename || ''
            let api = `/api/irrigation/service-config/${filename}/update-restart`
            axios.put(api, this.configData.content, apiConf)
                .then(resp => {
                    this.status = resp.status !== 204 ? resp.data.message : ''
                })
                .catch((err) => {
                    this.$emit('update:serviceState', 'off')
                    if (!this.inProduction) {
                        this.status = err.response.data.message
                        console.log(err)
                    }
                })
        },
        onTreeViewDataChange (updatedDocument) {
            this.wortSaving = true
            this.configData.content = updatedDocument
        },
        addPlant () {
            var plants = this.configData.content.plants_args_list
            if (plants === undefined) {
                this.status = 'can\'t add plant, expected [plants_args_list] key in configuration'
                return
            }
            this.wortSaving = true
            // TODO: automate this schema retreival somehow :)
            plants.push({
                'name': `Lill ${++counter}`,
                'valve_pin': -1,
                'led_pin': -1,
                'moist_percent': 65,
                'pour_millilitres': 50,
                'sensor_args': {
                    'spi_device': -1,
                    'spi_channel': -1,
                    'vcc_pin': -1,
                    'wet_value': 0.44,
                    'dry_value': 0.85
                }
            })
            this.status = 'please calibrate new plant\'s sensor before usage'
        },
        removePlant (name) {
            if (name === null) {
                return
            }
            this.wortSaving = true
            var plants = this.configData.content.plants_args_list
            const index = plants.findIndex(p => p.name === name)
            if (index !== -1) {
                plants.splice(index, 1)
            } else {
                this.status = 'plant you were trying to remove do not existn in array'
            }
        }
    },
    computed: {
        selectTitle () {
            return this.disableRemove ? 'cannot remove single plant' : ''
        },
        disableRemove () {
            return this.configData.content.plants_args_list.length <= 1
        },
        plantToRemove: {
            get () { return null },
            set (name) { this.removePlant(name) }
        },
        hasConf () {
            return this.configData && Object.keys(this.configData).length > 0
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
