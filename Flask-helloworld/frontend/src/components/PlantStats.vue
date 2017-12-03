<template>
<div>
    <h1>Statistics for <span v-text="name"></span></h1>
    <span v-if="statistics.length == 0" v-text="status"></span>
    <table v-else>
        <tr>
            <th>id</th>
            <th>garderer__id</th>
            <th>plant_uuid1</th>
            <th>timestamp utc</th>
            <th>measure %</th>
        </tr>
        <tr v-for="s in statistics">
            <td v-text="s.__id"></td>
            <td v-text="s.gardener__id"></td>
            <td v-text="s.plant_uuid1"></td>
            <td v-text="s.ts_utc"></td>
            <td v-text="s.percent"></td>
        </tr>
    </table>
</div>
</template>

<script>
import axios from 'axios'

const apiBase = 'http://saarmas-rp3-1.saared.eu:4999/api/plant'

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
            statistics: []
        }
    },
    methods: {
        _handleResponse (resp) {
            if (Array.isArray(resp.data) && resp.data.length > 0) {
                this.statistics = resp.data
            } else {
                this.status = "didn't get any statistics, check what's wrong'"
            }
        },
        getPlantStatistics () {
            axios.get(`${apiBase}/${this.name}/statistics`)
                .then(this._handleResponse)
                .catch(console.log)
        }
    },
    beforeMount () { this.getPlantStatistics() }
}
</script>

<style scoped>
h1 > span {
    box-shadow: -1px -1px 4px 2px #52e4b585;
}
</style>

<doc>
{
    "__id": <int>,
    "gardener__id": <gardener_instances__id>,
    "plant_uuid1": <parent plant>,
    "ts_utc": "timestamp()",
    "mil_lit": <float>
}
</doc>
