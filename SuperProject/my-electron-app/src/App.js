import React, { useState, useEffect } from 'react';
import './App.css';
const { ipcRenderer } = window.require('electron');

const App = () => {
  const [databaseData, setDatabaseData] = useState([]);

  useEffect(() => {
    ipcRenderer.on('database-data', (event, data) => {
      setDatabaseData(data);
    });

    return () => {
      ipcRenderer.removeAllListeners('database-data');
    }
  }, []);

  return (
    <div>
      <table>
        <thead>
          <tr>
            <th>Id</th>
            <th>Σύνδεσμος</th>
            <th>Τιμή συσκευασίας</th>
            <th>Τιμή ανά μονάδα</th>
          </tr>
        </thead>
        <tbody>
          {databaseData.map((row) => (
            <tr key={row.id}>
              <td>{row.id}</td>
              <td><a href={row.link} target="_blank">{row.product_name}</a></td>
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
