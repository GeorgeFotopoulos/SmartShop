import "./App.css";
import React, { useState, useEffect } from "react";
import { ClipLoader } from "react-spinners";

const { ipcRenderer, shell } = window.require("electron");

const App = ({ onSearch }) => {
	const [loading, setLoading] = useState(true); // set initial state to true to show loading animation on window load
	const [databaseData, setDatabaseData] = useState([]);
	const [searchTerm, setSearchTerm] = useState("");

	useEffect(() => {
		ipcRenderer.on("database-data", (event, data) => {
			setDatabaseData(data);
			setLoading(false); // hide loading animation after data is loaded
		});

		return () => {
			ipcRenderer.removeAllListeners("database-data");
		};
	}, []);

	const handleSearch = (event) => {
		const value = event.target.value;
		setSearchTerm(value);
		onSearch(value);
	};

	const clearSearch = () => {
		setSearchTerm("");
		onSearch("");
	};

	const filteredData = databaseData.filter((row) =>
		searchTerm
			.split(",")
			.map((word) => word.trim().toLowerCase())
			.every((word) => row.product_name.toLowerCase().includes(word))
	);

	return (
		<div style={{ textAlign: "center" }}>
			<div className="search-field">
				<input type="text" placeholder="Αναζήτηση..." value={searchTerm} onChange={handleSearch} />
				{searchTerm.length > 0 && (
					<button className="clear-search" onClick={clearSearch}>
						Καθαρισμός
					</button>
				)}
				{loading && (
					<div className="loading-overlay">
						<ClipLoader color={"#36D7B7"} size={150} />
					</div>
				)}
			</div>
			<table>
				<thead>
					<tr>
						<th> Α/Α </th>
						<th> Κατάστημα </th>
						<th> Προϊόν </th>
						<th> Τιμή Συσκευασίας </th>
						<th> Τιμή ανά μονάδα </th>
					</tr>
				</thead>
				<tbody>
					{filteredData.map((row) => (
						<tr key={row.id}>
							<td>{row.id}</td>
							<td>{row.shop}</td>
							<td>
								<a
									onClick={(event) => {
										event.preventDefault();
										shell.openExternal(row.link);
									}}
									href="#"
								>
									{" "}
									{row.product_name}{" "}
								</a>
							</td>
							<td>{row.flat_price}</td>
							<td>{row.price_per_unit}</td>
						</tr>
					))}
				</tbody>
			</table>
		</div>
	);
};

export default App;
