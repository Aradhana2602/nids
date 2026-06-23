import { useState } from "react";
import { useEffect } from "react";
import Charts from "./components/Charts.jsx";
import StatsCard from "./components/StatsCard";
import History from "./components/History";
import axios from "axios";
import "./App.css";



function App() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const API_URL = "https://nids-9si4.onrender.com";
  const [history, setHistory] = useState([]);



const fetchHistory = async () => {
  try {
    const response = await axios.get(
      `${API_URL}/history`
    );

    setHistory(response.data);
  } catch (error) {
    console.error(error);
  }
};

useEffect(() => {
  fetchHistory();
}, []);

  const handleUpload = async () => {
    if (!file) {
      alert("Please select a file");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await axios.post(
        `${API_URL}/upload-csv`,
        formData
      );

      setResult(response.data);
      fetchHistory();
    } catch (error) {
      console.error(error);
      alert("Upload failed");
    }
  };

  const downloadPDF = async () => {
  try {
    const response = await axios.post(
      `${API_URL}/generate-report`,
      result,
      {
        responseType: "blob",
      }
    );

    const url = window.URL.createObjectURL(
      new Blob([response.data])
    );

    const link = document.createElement("a");

    link.href = url;
    link.download = "nids_report.pdf";

    document.body.appendChild(link);

    link.click();

    link.remove();
  } catch (error) {
    console.error(error);
    alert("PDF download failed");
  }
};

  return (
    <div className="container">
      <h1>AI Powered Network Intrusion Detection <hr></hr>System</h1>

      <input
        type="file"
        onChange={(e) => setFile(e.target.files[0])}
      />

      <br />
      <br />

      <button onClick={handleUpload}>
        Analyze Traffic
      </button>

      {result && (
  <div className="cards">
    <StatsCard
      title="Attacks"
      value={result.attacks}
    />

    <StatsCard
      title="Normal"
      value={result.normal}
    />

    <StatsCard
      title="Risk Level"
      value={result.risk_level}
    />
  </div>
)}


      {result && (
        
        <div className="results">
          <h2>Analysis Results</h2>

          <p>
            <strong>Total Records:</strong> {result.total_records}
          </p>

          <p>
            <strong>Attacks:</strong> {result.attacks}
          </p>

          <p>
            <strong>Normal:</strong> {result.normal}
          </p>

          <p>
            <strong>Attack Percentage:</strong>{" "}
            {result.attack_percentage}%
          </p>

          <p>
            <strong>Risk Level:</strong> {result.risk_level}
          </p>
        </div>
      )}

      {result && (
  <>
    <Charts
      attacks={result.attacks}
      normal={result.normal}
      attackPercentage={result.attack_percentage}
    />

    <br />

    <button onClick={downloadPDF}>
      Download PDF Report
    </button>
  </>
)}
 <History history={history} />
 
    </div>
  );
}

export default App;