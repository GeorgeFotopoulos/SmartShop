import React, { useState, useEffect } from 'react';
import './App.css';

const fetchDatabaseData = () => {
  const sqlite3 = require('sqlite3').verbose();
  const db = new sqlite3.Database('../database.db');

  db.serialize(() => {
    const query = `SELECT * FROM products`;

    db.all(query, [], (err, rows) => {
      if (err) {
        throw err;
      }
      db.close();
      return rows;
    });
  });
};

const App = () => {
  const [databaseData, setDatabaseData] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      const data = await fetchDatabaseData();
      setDatabaseData(data);
    };

    fetchData();
  }, []);

  return (
    <div>
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Link</th>
            <th>Product Name</th>
            <th>Flat Price</th>
            <th>Price per Unit</th>
          </tr>
        </thead>
        <tbody>
          {databaseData.map((row) => (
            <tr key={row.id}>
              <td>{row.id}</td>
              <td>{row.link}</td>
              <td>{row.product_name}</td>
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