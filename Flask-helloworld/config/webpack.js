const fs = require('fs');
const path = require('path');
const webpack = require('webpack');
const CleanWebpackPlugin = require('clean-webpack-plugin');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const ManifestRevisionPlugin = require('manifest-revision-webpack-plugin');

const projectRoot = path.join(__dirname, '../website')
const buildRootDir = path.join(projectRoot, '/build')
const buildOutputDir = path.join(buildRootDir, '/static')
const webpackMainifest = path.join(buildRootDir, '/webpack.manifest.json')
const assetsRootDir = path.join(projectRoot, '/assets')

fs.mkdir(path.dirname(webpackMainifest), function(){});

module.exports = {
    context: projectRoot,
    resolve: {
        extensions: ['.js']
    },
    entry: {
        site: [
            path.join(assetsRootDir, '/site.js'),
            path.join(assetsRootDir, '/site.css')
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
            {
                test: /\.css$/,
                use: ['style-loader', 'css-loader']
            }
        ]
    },
    plugins: [
        new CleanWebpackPlugin([buildRootDir + '/*'], {
            root: projectRoot
        }),
        new webpack.optimize.CommonsChunkPlugin({
            name: 'common'
        }),
        new HtmlWebpackPlugin({
            template: './templates/_webpack/empty.html',
            filename: projectRoot + '/templates/_webpack/injected_scripts.html',
        }),
        new ManifestRevisionPlugin(webpackMainifest, {
            rootAssetPath: assetsRootDir
        })
    ]
};
