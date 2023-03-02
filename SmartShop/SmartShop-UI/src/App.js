import React, { useEffect, useState } from "react";
import ReactPaginate from "react-paginate";
import { ClipLoader } from "react-spinners";
import "./App.css";

const { ipcRenderer, shell } = window.require("electron");

const App = ({ onSearch }) => {
	const [loading, setLoading] = useState(true);
	const [databaseData, setDatabaseData] = useState([]);
	const [searchTerm, setSearchTerm] = useState("");
	const [currentPage, setCurrentPage] = useState(0);
	const [itemsPerPage, setItemsPerPage] = useState(20);

	useEffect(() => {
		ipcRenderer.on("database-data", (event, data) => {
			setDatabaseData(data);
			setLoading(false);
		});

		return () => {
			ipcRenderer.removeAllListeners("database-data");
		};
	}, []);

	const filterData = () => {
		return databaseData.filter((row) =>
			searchTerm
				.split(",")
				.map((word) => word.trim().toLowerCase())
				.every((word) => row.product_name.toLowerCase().includes(word))
		);
	};

	const handleSearch = (event) => {
		const value = event.target.value;
		setSearchTerm(value);
		setCurrentPage(0);
		const pageLinks = document.getElementsByClassName("pagination__link");
		pageLinks[0].classList.add("pagination__link--active");
		for (let i = 1; i < pageLinks.length; i++) {
			pageLinks[i].classList.remove("pagination__link--active");
		}

		// Simulate a click event on the first page that has the class name "pagination__link--active"
		const activePageLink = document.querySelector(".pagination__link--active");
		activePageLink && activePageLink.click();
	};

	const clearSearch = () => {
		setSearchTerm("");
		onSearch("");
	};

	const handlePageChange = ({ selected }) => {
		setCurrentPage(selected);
	};

	const filteredData = filterData().slice(currentPage * itemsPerPage, (currentPage + 1) * itemsPerPage);

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
						<tr key={row.code}>
							<td>{row.code}</td>
							<td>{row.store}</td>
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
							<td>{row.metric_unit}</td>
						</tr>
					))}
				</tbody>
			</table>
			{filteredData.length > 0 && (
				<ReactPaginate
					previousLabel={"← Previous"}
					nextLabel={"Next →"}
					pageCount={Math.ceil(filterData().length / itemsPerPage)}
					onPageChange={handlePageChange}
					containerClassName={"pagination"}
					pageClassName={"pagination__item"}
					pageLinkClassName={"pagination__link"}
					activeLinkClassName={"pagination__link--active"}
					previousClassName={"pagination__prev"}
					nextClassName={"pagination__next"}
					disabledClassName={"pagination__link--disabled"}
					getPageLinkClassName={({ selected }) => (selected === currentPage ? "pagination__link--active" : "pagination__link--inactive")}
				/>
			)}
		</div>
	);
};

export default App;
