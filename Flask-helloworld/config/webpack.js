const fs = require('fs');
const path = require('path');
const webpack = require('webpack');
const CleanWebpackPlugin = require('clean-webpack-plugin');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const WebpackCdnPlugin = require('webpack-cdn-plugin');
const ManifestRevisionPlugin = require('manifest-revision-webpack-plugin');

const webRoot = path.join(__dirname, '../website')
const templatesDir = path.join(webRoot, '/templates')
const buildRootDir = path.join(webRoot, '/build')
const buildOutputDir = path.join(buildRootDir, '/public/static')
const webpackMainifest = path.join(buildRootDir, '/webpack.manifest.json')
const layoutHtml = path.join(buildRootDir, '/templates/_layout.html')
const assetsRootDir = path.join(webRoot, '/assets/')

fs.mkdir(path.dirname(webpackMainifest), function(){});

module.exports = {
    context: webRoot,
    resolve: {
        extensions: ['.js']
    },
    entry: {
        site: [
            path.join(assetsRootDir, '/site/main.js'),
            path.join(assetsRootDir, '/site/main.css')
        ]
    },
    output: {
        path: buildOutputDir,
        filename: 'bundel.[name].[hash].js',
        publicPath: '/static'
    },
    devtool: 'inline-source-map',
    devServer: {
        contentBase: buildOutputDir
    },
    module: {
        rules: [
            { test: /\.css$/, use: ['style-loader', 'css-loader'] }
        ]
    },
    plugins: [
        new CleanWebpackPlugin([buildRootDir + '/*', layoutHtml], {
            root: webRoot
        }),
        new webpack.optimize.CommonsChunkPlugin({
            name: 'common'
        }),
        new HtmlWebpackPlugin({
            inject: false,
            template: './templates/_webpack_layout.html',
            filename: layoutHtml,
            favicon: './assets/favicon.ico'
        }),
        new ManifestRevisionPlugin(webpackMainifest, {
            rootAssetPath: assetsRootDir
        })
    ]
};
