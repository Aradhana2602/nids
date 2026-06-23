import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid
} from "recharts";

function Charts({ attacks, normal, attackPercentage }) {
  const pieData = [
    { name: "Attacks", value: attacks },
    { name: "Normal", value: normal }
  ];

  const barData = [
    {
      name: "Attack %",
      percentage: attackPercentage
    }
  ];

  const COLORS = ["#ff4d4f", "#52c41a"];

  return (
    <>
      <h2>Traffic Distribution</h2>

      <PieChart width={400} height={300}>
        <Pie
          data={pieData}
          dataKey="value"
          cx="50%"
          cy="50%"
          outerRadius={100}
          label
        >
          {pieData.map((entry, index) => (
            <Cell
              key={index}
              fill={COLORS[index]}
            />
          ))}
        </Pie>

        <Tooltip />
        <Legend />
      </PieChart>

      <h2>Attack Percentage</h2>

      <BarChart
        width={500}
        height={300}
        data={barData}
      >
        <CartesianGrid strokeDasharray="3 3" />

        <XAxis dataKey="name" />

        <YAxis />

        <Tooltip />

        <Bar
          dataKey="percentage"
        />
      </BarChart>
    </>
  );
}

export default Charts;