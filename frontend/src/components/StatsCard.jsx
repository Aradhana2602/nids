function StatsCard({ title, value }) {
  let color = "#333";

  if (title === "Risk Level") {
  if (value === "High") color = "#ef4444";
  else if (value === "Medium") color = "#f59e0b";
  else color = "#22c55e";
}

  return (
    <div className="card">
      <h3>{title}</h3>
      <h2 style={{ color }}>{value}</h2>
    </div>
  );
}

export default StatsCard;