const fs = require('fs');
const path = require('path');
const reqText = require('require-text');
const webpack = require('webpack');
const CleanWebpackPlugin = require('clean-webpack-plugin');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const ManifestRevisionPlugin = require('manifest-revision-webpack-plugin');

const webRoot = path.resolve(__dirname, '../website');
const templatesDir = path.join(webRoot, '/templates');
const buildRootDir = path.join(webRoot, '/build');
const buildOutputDir = path.join(buildRootDir, '/public/static');
const webpackMainifest = path.join(buildRootDir, '/webpack.manifest.json');
const outputLayoutHtml = path.join(buildRootDir, '/templates/_layout.html');
const assetsRootDir = path.join(webRoot, '/assets/');
const bodyPartialHtml = path.join(templatesDir, '/_webpack_layout_content.html');

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
        filename: '[name].bundle.[hash].js',
        publicPath: '/static'
    },
    devtool: 'inline-source-map',
    devServer: {
        contentBase: buildOutputDir
    },
    module: {
        rules: [
            { test: /\.css$/, use: ['style-loader', 'css-loader'] },
            { test: /\.txt$/, use: 'raw-text-loader' }
            //{ test: /\.ico$/, use: 'file-loader' }
        ]
    },
    plugins: [
        new CleanWebpackPlugin([buildRootDir + '/*'], {
            root: webRoot
        }),
        new webpack.optimize.CommonsChunkPlugin({
            name: 'common',
            //async: true
        }),
        new HtmlWebpackPlugin({
            inject: false,
            template: require('html-webpack-template'),
            filename: outputLayoutHtml,
            lang: 'et',
            title: '{% block title %}Welcome{% endblock %} | HelloWorld app',
            meta: [{ name:'theme-color', content:'#A688FD' }],
            favicon: './assets/favicon.ico',
            mobile: true,
            bodyHtmlSnippet: bodyPartialHtml
        }),
        new ManifestRevisionPlugin(webpackMainifest, {
            rootAssetPath: assetsRootDir
        })
    ],
    parallelism: 8
};
