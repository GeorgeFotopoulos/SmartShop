import "./App.css";
import unorm from "unorm";
import React, { useState, useEffect } from "react";

const { ipcRenderer, shell } = window.require("electron");

const App = () => {
	const [databaseData, setDatabaseData] = useState([]);
	const [searchTerm, setSearchTerm] = useState("");

	useEffect(() => {
		ipcRenderer.on("database-data", (event, data) => {
			setDatabaseData(data);
		});

		return () => {
			ipcRenderer.removeAllListeners("database-data");
		};
	}, []);

	const handleSearch = (event) => {
		const searchTermNormalized = unorm.nfd(event.target.value.toLowerCase().trim());
		setSearchTerm(searchTermNormalized);
	};

	const filteredData = databaseData.filter((row) => unorm.nfd(row.product_name.toLowerCase()).includes(searchTerm));

	return (
		<div style={{ textAlign: "center" }}>
			<input type="text" placeholder="Search..." onChange={handleSearch} />

			<table>
				<thead>
					<tr>
						<th> Α/Α </th>
						<th> ΠΡΟΪΟΝ</th>
						<th> ΤΙΜΗ ΣΥΣΚΕΥΑΣΙΑΣ </th>
						<th> ΤΙΜΗ ΑΝΑ ΜΟΝΑΔΑ </th>
					</tr>
				</thead>
				<tbody>
					{filteredData.map((row) => (
						<tr key={row.id}>
							<td>{row.id}</td>
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
