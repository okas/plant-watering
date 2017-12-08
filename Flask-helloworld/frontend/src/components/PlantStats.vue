<template>
<div>
    <h1>Statistics for <span v-text="name"></span></h1>
    <span>These are currently activities which ara automatically performed.</span>
    <ul>
        <li v-if="status" v-text="status"></li>
        <li v-if="w_status" v-text="w_status"></li>
        <li v-if="m_status" v-text="m_status"></li>
    </ul>
    <table v-if="waterings.length > 0">
        <caption>
            Waterings&nbsp;|&nbsp;<a href="#refresh" @click="getPlantWaterings">refresh</a>
        </caption>
        <tr>
            <th>id</th>
            <th>time</th>
            <th>amount ml</th>
        </tr>
        <tr v-for="s in waterings">
            <td v-text="s.__id"></td>
            <td>{{ s.ts_utc | localTimeFromUtc }}</td>
            <td v-text="s.mil_lit"></td>
        </tr>
    </table>
    <table v-if="measurings.length > 0">
        <caption>
            Measurings&nbsp;|&nbsp;<a href="#refresh" @click="getPlantMeasurings">refresh</a>
        </caption>
        <tr>
            <th>id</th>
            <th>time</th>
            <th>moist %</th>
        </tr>
        <tr v-for="s in measurings">
            <td v-text="s.__id"></td>
            <td>{{ s.ts_utc | localTimeFromUtc }}</td>
            <td v-text="s.percent"></td>
        </tr>
    </table>
</div>
</template>

<script>
import axios from 'axios'

export default {
    name: 'PlantStats',
    props: {
        name: {
            type: String,
            required: true
        }
    },
    data () {
        return {
            status: 'loading statistic from database...',
            w_status: '',
            m_status: '',
            waterings: [],
            measurings: []
        }
    },
    filters: {
        localTimeFromUtc (val) {
            var localDT = new Date(val * 1000)
            localDT.setMinutes(localDT.getMinutes() - localDT.getTimezoneOffset())
            return localDT.toLocaleString('et-ET', {})
        }
    },
    methods: {
        _handleResponse (resp, statsType) {
            var msg = ''
            if (Array.isArray(resp.data) && resp.data.length > 0) {
                this[statsType] = resp.data
                this.status = ''
            } else {
                msg = `didn't get any ${statsType}, check what's wrong`
            }
            if (statsType === 'waterings') {
                this.w_status = msg
            } else {
                this.m_status = msg
            }
        },
        getPlantWaterings () {
            axios.get(`/api/plant/${this.name}/statistics/watering`)
                .then(resp => this._handleResponse(resp, 'waterings'))
                .catch(console.log)
        },
        getPlantMeasurings () {
            axios.get(`/api/plant/${this.name}/statistics/measuring`)
                .then(resp => this._handleResponse(resp, 'measurings'))
                .catch(console.log)
        }
    },
    beforeMount () {
        this.getPlantMeasurings()
        this.getPlantWaterings()
    }
}
</script>

<style scoped>
h1 > span {
  box-shadow: -1px -1px 1px 1px #52e4b585;
}
ul {
  list-style-type: none;
  padding: 0;
}
table {
  margin: 0 auto 1.5em
}
</style>

<docs>
{
    "__id": <int>,
    "ts_utc": "timestamp()",
    "mil_lit": <float>
},
{
    "__id": <int>,
    "ts_utc": "timestamp()",
    "percent": <float>
}
</docs>
