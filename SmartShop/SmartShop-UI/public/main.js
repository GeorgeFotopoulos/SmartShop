const { app, BrowserWindow } = require("electron");
const sqlite3 = require("sqlite3").verbose();

function createWindow() {
	// Create the browser window.
	const win = new BrowserWindow({
		width: 1600,
		height: 1000,
		webPreferences: {
			nodeIntegration: true,
			contextIsolation: false
		}
	});

	win.maximize();

	// Load your React app.
	win.loadURL("http://localhost:3000");

	// Wait for the React app to finish loading.
	win.webContents.on("did-finish-load", () => {
		// Create a new SQLite database connection.
		const db = new sqlite3.Database("./database.db");

		// Query the database for all rows in the 'products' table.
		db.all("SELECT * FROM products", (err, rows) => {
			if (err) {
				throw err;
			}

			// Send the rows to the React app.
			win.webContents.send("database-data", rows);
		});

		// Close the database connection.
		db.close();
	});
}

// Create the window when the app is ready.
app.whenReady().then(() => {
	createWindow();

	// Quit when all windows are closed.
	app.on("window-all-closed", () => {
		if (process.platform !== "darwin") {
			app.quit();
		}
	});
});

// On macOS, recreate a window when the dock icon is clicked and no windows are open.
app.on("activate", () => {
	if (BrowserWindow.getAllWindows().length === 0) {
		createWindow();
	}
});
