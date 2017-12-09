<template>
<plant-layout>
    <section>
        <header>
            <h2>Statistics for <span v-text="name"></span></h2>
            <span>Activities that irrigation system performs automatically.</span>
            <ul>
                <li v-if="status" v-text="status"></li>
                <li v-if="w_status" v-text="w_status"></li>
                <li v-if="m_status" v-text="m_status"></li>
            </ul>
        </header>
        <article>
            <table v-if="waterings.length > 0">
                <caption>
                    <span>Waterings</span>&nbsp;|&nbsp;<a href="#refresh" @click="getPlantWaterings">refresh</a>
                </caption>
                <tr>
                    <th>id</th>
                    <th>time</th>
                    <th>amount ml</th>
                </tr>
                <tr v-for="s in waterings">
                    <td v-text="s.__id"></td>
                    <td v-html="datetimeHtml(s.ts_utc)"></td>
                    <td v-text="s.mil_lit"></td>
                </tr>
            </table>
        </article>
        <article>
             <table v-if="measurings.length > 0">
                <caption>
                    <span>Measurings</span>&nbsp;|&nbsp;<a href="#refresh" @click="getPlantMeasurings">refresh</a>
                </caption>
                <tr>
                    <th>id</th>
                    <th>time</th>
                    <th>moist %</th>
                </tr>
                <tr v-for="s in measurings">
                    <td v-text="s.__id"></td>
                    <td v-html="datetimeHtml(s.ts_utc)"></td>
                    <td v-text="s.percent"></td>
                </tr>
            </table>
        </article>
    </section>
</plant-layout>
</template>

<script>
import PlantLayout from './PlantLayout'

import axios from 'axios'

export default {
    name: 'PlantStats',
    components: { PlantLayout },
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
            return localDT.toLocaleString('et-ET', {
                year: '2-digit',
                month: '2-digit',
                day: '2-digit',
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit'
            })
        }
    },
    methods: {
        datetimeHtml (val) {
            var dateTimeString = this.$options.filters.localTimeFromUtc(val)
            const match = /(\d\d.\d\d.\d\d )(\d\d:\d\d:\d\d)/
            const replace = '$1<span>$2<span>'
            return dateTimeString.replace(match, replace)
        },
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
  margin: 0 auto 1.5em;
}
caption > span {
  font-weight: bolder;
}
caption, th {
  border-bottom: 1px solid lightgrey;
}
table td:nth-last-child(n+2), th:nth-last-child(n+2) {
  border-right: 1px solid lightgrey;
}
table tr:nth-child(odd) td {
  background: #9effc657;
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
