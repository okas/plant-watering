<script>
export default {
    name: 'IrrigationConfiguration',
    props: ['dataObj'],
    render: function (createElement) {
        return this._getDescrList(this.dataObj, createElement)
    },
    methods: {
        _getDescrList (obj, createElement) {
            return createElement('dl', {}, [
                Object.entries(obj).map(prop => {
                    return [
                        createElement('dt', {}, prop[0]),
                        createElement('dd', {},
                            [this._getDescContent(prop[1], createElement)]
                    )]
                })])
        },
        _getDescContent (val, createElement) {
            switch (Object.prototype.toString.call(val)) {
            case '[object String]':
            case '[object Number]':
            case '[object Boolean]':
            case '[object Null]':
                return val
            case '[object Array]':
                return val.map(obj => {
                    return this._getDescrList(obj, createElement)
                })
            case '[object Object]':
                return this._getDescrList(val, createElement)
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
