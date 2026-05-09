import { useEffect, useMemo, useState } from 'react';
import { Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { fetchBestTitles, fetchCityEngagement } from '../lib/api';
import type { AssistantSettings, BestTitleRow, CityEngagementRow } from '../types/api';

interface InsightsPanelProps {
  settings: AssistantSettings;
}

export function InsightsPanel({ settings }: InsightsPanelProps) {
  const [bestTitles, setBestTitles] = useState<BestTitleRow[]>([]);
  const [cities, setCities] = useState<CityEngagementRow[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
  // STOP if not authenticated
  if (!settings.isAuthenticated) {
    setBestTitles([]);

    setCities([]);

    return;
  }

  let ignore = false;

  async function loadInsights() {

    setIsLoading(true);

    setError(null);

    try {

      const [titles, cityRows] = await Promise.all([
        fetchBestTitles(settings),
        fetchCityEngagement(settings),
      ]);

      if (!ignore) {

        setBestTitles(titles.slice(0, 6));

        setCities(cityRows.slice(0, 6));
      }

    } catch (err) {

      if (!ignore) {

        setError(
          err instanceof Error
            ? err.message
            : String(err)
        );
      }

    } finally {

      if (!ignore) {

        setIsLoading(false);
      }
    }
  }

  loadInsights();

  return () => {
    ignore = true;
  };

}, [settings]);

  const topTitle = bestTitles[0];
  const strongestCity = cities[0];
  const titleChartData = useMemo(
    () => bestTitles.map((row) => ({ name: row.title, minutes: row.minutes, revenue: row.revenue })),
    [bestTitles]
  );
  const cityChartData = useMemo(
    () => cities.map((row) => ({ name: row.city, views: row.views, revenue: row.revenue })),
    [cities]
  );

  return (
    <section className="panel insights-panel">
      <div className="panel__header">
        <h2>Insights panel</h2>
        <span>{isLoading ? 'Refreshing...' : `${settings.year} • ${settings.month}`}</span>
      </div>

      {error && <pre className="error-box">{error}</pre>}

      <div className="kpi-grid">
        <div className="kpi-card">
          <span>Top title</span>
          <strong>{topTitle?.title ?? '—'}</strong>
          <small>{topTitle ? `${Number(topTitle.minutes ?? 0).toLocaleString()} minutes watched` : 'Load analytics to view'}</small>
        </div>
        <div className="kpi-card">
          <span>Strongest city</span>
          <strong>{strongestCity?.city ?? '—'}</strong>
          <small>{strongestCity ? `${strongestCity.views.toLocaleString()} views` : 'Load analytics to view'}</small>
        </div>
        <div className="kpi-card">
          <span>Access role</span>
          <strong>{settings.role}</strong>
        </div>
      </div>

      <div className="chart-card">

        <div className="chart-card__header">
          <div>
            <h3>Best Titles by watch minutes</h3>

            <p>
              Top performing titles ranked by audience watch time
            </p>
          </div>

          <div className="chart-badge">
            Top {titleChartData.length}
          </div>

        </div>

        <ResponsiveContainer width="100%" height={360}>

          <BarChart
            data={titleChartData}
            layout="vertical"
            margin={{
              top: 10,
              right: 30,
              left: 20,
              bottom: 10,
            }}
          >

            <CartesianGrid
              strokeDasharray="3 3"
              horizontal={false}
              opacity={0.12}
            />

            <XAxis
              type="number"
              tick={{
                fontSize: 12,
                fill: "#64748b",
              }}
              tickLine={false}
              axisLine={false}
            />

            <YAxis
              type="category"
              dataKey="name"
              width={120}
              tick={{
                fontSize: 14,
                fill: "#0f172a",
              }}
              tickLine={false}
              axisLine={false}
            />

            <Tooltip
              cursor={{
                fill: "rgba(99,102,241,0.08)",
              }}
              contentStyle={{
                borderRadius: "14px",
                border: "none",
                boxShadow: "0 8px 24px rgba(15,23,42,0.12)",
                fontSize: "13px",
              }}
               formatter={(value: number) => [
                `${value.toLocaleString()} mins`,
                "Watch time",
              ]}
            />

            <Bar
              dataKey="minutes"
              fill="#6366f1"
              radius={[0, 10, 10, 0]}
              barSize={28}
            />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="chart-card">
        <div className="chart-card__header">
          <h3>City Engagement</h3>
          <span>Views by region</span>
        </div>

        <ResponsiveContainer width="100%" height={320}>
          <BarChart
            data={cityChartData}
            margin={{
              top: 20,
              right: 20,
              left: 10,
              bottom: 60,
            }}
          >
            <CartesianGrid
              strokeDasharray="3 3"
              vertical={false}
              opacity={0.15}
            />

            <XAxis
              dataKey="name"
              tick={{
                fontSize: 13,
                fill: "#64748b",
              }}
              tickLine={false}
              axisLine={false}
              angle={-15}
              textAnchor="end"
              interval={0}
            />

            <YAxis
              tick={{
                fontSize: 12,
                fill: "#64748b",
              }}
              tickLine={false}
              axisLine={false}
            />

            <Tooltip
              cursor={{ fill: "rgba(20,184,166,0.08)" }}
              contentStyle={{
                borderRadius: "12px",
                border: "none",
                boxShadow: "0 4px 16px rgba(0,0,0,0.08)",
                fontSize: "13px",
              }}
            />

            <Bar
              dataKey="views"
              fill="#14b8a6"
              radius={[10, 10, 0, 0]}
              barSize={42}
            />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </section>
  );
}