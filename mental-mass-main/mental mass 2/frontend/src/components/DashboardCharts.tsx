import {
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

const trendData = [
  { day: "Mon", score: 62 },
  { day: "Tue", score: 45 },
  { day: "Wed", score: 71 },
  { day: "Thu", score: 38 },
  { day: "Fri", score: 55 },
  { day: "Sat", score: 78 },
  { day: "Sun", score: 68 },
];

const emotionData = [
  { name: "Happy", value: 35, color: "#22c55e" },
  { name: "Neutral", value: 28, color: "#818cf8" },
  { name: "Sad", value: 18, color: "#60a5fa" },
  { name: "Surprised", value: 12, color: "#f59e0b" },
  { name: "Angry", value: 7, color: "#ef4444" },
];

const riskData = [
  { range: "Low (>70)", count: 12, fill: "#22c55e" },
  { range: "Medium (35-70)", count: 8, fill: "#f59e0b" },
  { range: "High (<35)", count: 4, fill: "#ef4444" },
];

const RADIAN = Math.PI / 180;

type PieLabelProps = {
  cx: number;
  cy: number;
  midAngle: number;
  innerRadius: number;
  outerRadius: number;
  percent: number;
};

const renderLabel = ({
  cx,
  cy,
  midAngle,
  innerRadius,
  outerRadius,
  percent,
}: PieLabelProps) => {
  const r = innerRadius + (outerRadius - innerRadius) * 0.5;
  const x = cx + r * Math.cos(-midAngle * RADIAN);
  const y = cy + r * Math.sin(-midAngle * RADIAN);
  return percent > 0.08 ? (
    <text
      x={x}
      y={y}
      fill="white"
      textAnchor="middle"
      dominantBaseline="central"
      fontSize={11}
      fontWeight={600}
    >
      {`${(percent * 100).toFixed(0)}%`}
    </text>
  ) : null;
};

interface MoodTrendChartProps {
  data?: Array<{ day: string; score: number }>;
}

interface EmotionPieChartProps {
  data?: Array<{ name: string; value: number; color: string }>;
}

interface RiskDistributionChartProps {
  data?: Array<{ range: string; count: number; fill: string }>;
}

export const MoodTrendChart = ({ data = trendData }: MoodTrendChartProps) => (
  <ResponsiveContainer width="100%" height={220}>
    <LineChart
      data={data}
      margin={{ top: 5, right: 10, left: -20, bottom: 5 }}
    >
      <CartesianGrid strokeDasharray="3 3" stroke="hsl(230 25% 88%)" />
      <XAxis dataKey="day" tick={{ fontSize: 12, fill: "hsl(230 15% 52%)" }} />
      <YAxis
        domain={[0, 100]}
        tick={{ fontSize: 12, fill: "hsl(230 15% 52%)" }}
      />
      <Tooltip
        contentStyle={{
          borderRadius: "8px",
          border: "1px solid hsl(230 25% 88%)",
          fontSize: 12,
        }}
      />
      <Line
        type="monotone"
        dataKey="score"
        stroke="hsl(230 65% 55%)"
        strokeWidth={2.5}
        dot={{ r: 4, fill: "hsl(230 65% 55%)" }}
        activeDot={{ r: 6 }}
        name="Mood Score"
      />
    </LineChart>
  </ResponsiveContainer>
);

export const EmotionPieChart = ({ data = emotionData }: EmotionPieChartProps) => (
  <ResponsiveContainer width="100%" height={220}>
    <PieChart>
      <Pie
        data={data}
        cx="50%"
        cy="50%"
        outerRadius={85}
        dataKey="value"
        labelLine={false}
        label={renderLabel}
      >
        {data.map((entry, index) => (
          <Cell key={index} fill={entry.color} />
        ))}
      </Pie>
      <Tooltip contentStyle={{ borderRadius: "8px", fontSize: 12 }} />
      <Legend iconType="circle" iconSize={10} wrapperStyle={{ fontSize: 12 }} />
    </PieChart>
  </ResponsiveContainer>
);

export const RiskDistributionChart = ({ data = riskData }: RiskDistributionChartProps) => (
  <ResponsiveContainer width="100%" height={180}>
    <BarChart
      data={data}
      margin={{ top: 5, right: 10, left: -20, bottom: 5 }}
    >
      <CartesianGrid strokeDasharray="3 3" stroke="hsl(230 25% 88%)" />
      <XAxis
        dataKey="range"
        tick={{ fontSize: 11, fill: "hsl(230 15% 52%)" }}
      />
      <YAxis tick={{ fontSize: 11, fill: "hsl(230 15% 52%)" }} />
      <Tooltip contentStyle={{ borderRadius: "8px", fontSize: 12 }} />
      <Bar dataKey="count" radius={[6, 6, 0, 0]} name="Sessions">
        {data.map((entry, i) => (
          <Cell key={i} fill={entry.fill} />
        ))}
      </Bar>
    </BarChart>
  </ResponsiveContainer>
);
