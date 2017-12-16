<script>
export default {
    name: 'IrrigationServiceConfiguration',
    props: ['dataObj'],
    render: function (ce) {
        return this._getDescrList(this.dataObj, ce)
    },
    methods: {
        _getDescrList (obj, ce) {
            return ce('dl', {},
                Object.entries(obj).map(prop => {
                    return [
                        ce('dt', {}, prop[0]),
                        ce('dd', {}, this._getDescContent(prop[1], ce))]
                }))
        },
        _getDescContent (val, ce) {
            switch (Object.prototype.toString.call(val)) {
            case '[object String]':
            case '[object Number]':
            case '[object Boolean]':
            case '[object Null]':
                return val
            case '[object Array]':
                return val.map(obj => {
                    return this._getDescrList(obj, ce)
                })
            case '[object Object]':
                return [this._getDescrList(val, ce)]
            }
        }
    }
}
</script>

<style scoped>
dl {
  display: grid;
  grid-template-columns: max-content auto;
}
dt {
  grid-column-start: 1;
}
dt::after {
  content: " : ";
}
dd::before {
  content: " ";
}
dd {
  grid-column-start: 2;
}
dt, dd {
    margin-left: 5px;
    text-align: left;
}
</style>
