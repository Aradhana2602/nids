function History({ history }) {
  return (
    <div className="history">
      <h2>Recent Analyses</h2>

      <table>
        <thead>
          <tr>
            <th>File</th>
            <th>Risk</th>
            <th>Attack %</th>
          </tr>
        </thead>

        <tbody>
          {history.map((item, index) => (
            <tr key={index}>
              <td>{item.filename}</td>
              <td>{item.risk_level}</td>
              <td>{item.attack_percentage}%</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default History;