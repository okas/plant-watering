var url = require('socket.io-client/lib/url');
var parser = require('socket.io-parser');
var Manager = require('socket.io-client/lib/manager');


/**
 * Module exports.
 */

module.exports = lookup;

/**
 * Managers cache.
 */

var cache = module.exports.managers = {};

/**
 * Managers index.
 */

var index = module.exports.managerIndex = {};

/**
 * Monkey patching original `connect` function.
 */

function lookup (uri, opts) {
    if (typeof uri === 'object') {
        opts = uri
        uri = undefined
    }
    opts = opts || {}

    var parsed = url(uri)
    var source = parsed.source
    var id = parsed.id
    var path = parsed.path
    var sameNamespace = cache[id] && path in cache[id].nsps

    if (sameNamespace) {
        index[source]++
    } else {
        index[source] = 1
    }

    var newConnection = opts.forceNew
        || opts['force new connection']
        || opts.multiplex === false
        || sameNamespace

    if (opts.multiplexNamespace === true && sameNamespace) {
        newConnection = false
    }
    let io

    if (newConnection) {
        io = Manager(source, opts)
    } else {
        if (!cache[id]) {
            cache[id] = Manager(source, opts)
        }
        io = cache[id]
    }
    if (parsed.query && !opts.query) {
        opts.query = parsed.query
    }
    return io.socket(parsed.path, opts)
}

/**
 * `connect`.
 *
 * @param {String} uri
 * @api public
 */
module.exports.connect = lookup

/**
 * Protocol version.
 *
 * @api public
 */

module.exports.protocol = parser.protocol

/**
 * Expose constructors for standalone build.
 *
 * @api public
 */

module.exports.Manager = Manager
module.exports.Socket = require('socket.io-client/lib//socket')
module.exports.url = url
