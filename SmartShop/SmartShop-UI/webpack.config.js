// webpack.config.js
const path = require("path");

module.exports = {
	target: "electron-renderer",
	node: {
		__dirname: false,
		__filename: false,
		fs: "empty" // Include this line to include the fs module
	},
	entry: "./src/index.js",
	output: {
		filename: "bundle.js",
		path: path.resolve(__dirname, "dist")
	},
	module: {
		rules: [
			// Add any necessary rules for your project
		]
	},
	resolve: {
		extensions: [".js", ".jsx"]
	},
	devtool: "source-map"
};
