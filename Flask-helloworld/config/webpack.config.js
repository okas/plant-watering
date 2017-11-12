const path = require('path');
const webpack = require('webpack');
const CleanWebpackPlugin = require('clean-webpack-plugin');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const ManifestRevisionPlugin = require('manifest-revision-webpack-plugin');

var projectRoot = path.join(__dirname, '../website')

module.exports = {
    context: projectRoot,
    resolve: {
        extensions: ['.js']
    },
    entry: {
        site_js: './assets/site.js',
        site_css: './assets/site.css'
    },
    output: {
        path: path.join(projectRoot, './static'),
        filename: '[name].[hash].bdl.js'
    },
    devtool: 'inline-source-map',
    devServer: {
        contentBase: './static'
    },
    module: {
        rules: [
            {
                test: /\.css$/,
                use: ['style-loader', 'css-loader']
            }
        ]
    },
    plugins: [
        new CleanWebpackPlugin(['./static/*'], {
            root: projectRoot
        }),
        new webpack.optimize.CommonsChunkPlugin({
            name: 'common'
        }),
        new HtmlWebpackPlugin({
            template: './templates/_webpack/empty.html',
            filename: '../templates/_webpack/injected_scripts.html',
        }),
        new ManifestRevisionPlugin(
            path.join('build', 'webpack.manifest.json'), {
                rootAssetPath: projectRoot + '/assets'
        })
    ]
};
