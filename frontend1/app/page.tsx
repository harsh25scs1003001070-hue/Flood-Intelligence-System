"use client";

import dynamic from "next/dynamic";
import { useState } from "react";

const DisasterMap = dynamic(
  () => import("../components/DisasterMap"),
  {
    ssr: false,
    loading: () => (
      <div className="h-full flex items-center justify-center text-slate-400">
        Loading map...
      </div>
    ),
  }
);


type Allocation = {
  resource: string;
  resource_type: string;
  village_id: string;
  priority_score: number;
  priority_level: string;
  population: number;
  distance_km: number;
  estimated_travel_time_min: number;
  assignment_score: number;
  reason: string;
};

type DisasterResult = {
  status: string;

  event: {
    type: string;
    risk_score: number;
    hazard_level: string;

    inputs: {
      rainfall_mm: number;
      duration_hours: number;
      water_level_m: number;
    };
  };

  impact: {
    affected_roads: string[];
    affected_villages: string[];
    affected_hospitals: string[];
    population_affected: number;
  };

  priority_assessment: {
    village_id: string;
    population: number;
    priority_score: number;
    priority_level: string;
    road_impact: boolean;
    hospital_impact: boolean;
  }[];

  resource_optimization: {
    status: string;

    allocations: Allocation[];

    ambulance_coverage: {
      served_villages: string[];
      unserved_villages: string[];
      total_resources: number;
      resources_used: number;
    };

    rescue_team_coverage: {
      served_villages: string[];
      unserved_villages: string[];
      total_resources: number;
      resources_used: number;
    };
  };

  resource_gaps: {
    ambulances: string[];
    rescue_teams: string[];
  };
};

type Mode = "live" | "simulation";

export default function Home() {
  const [mode, setMode] = useState<Mode>("live");

  const [rainfall, setRainfall] = useState(180);
  const [duration, setDuration] = useState(4);
  const [waterLevel, setWaterLevel] = useState(8);

  const [data, setData] = useState<DisasterResult | null>(null);
  const [loading, setLoading] = useState(false);
  async function analyzeScenario() {
    try {
      setLoading(true);
      setData(null);

      const payload =
        mode === "live"
          ? {
            mode: "live",
          }
          : {
            mode: "simulation",
            rainfall_mm: rainfall,
            duration_hours: duration,
            water_level_m: waterLevel,
          };

      const response = await fetch(
        "http://127.0.0.1:8000/api/disaster/analyze",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(payload),
        }
      );

      if (!response.ok) {
        const errorText = await response.text();
        console.error("Backend response:", errorText);
        throw new Error("Backend request failed");
      }

      const result: DisasterResult =
        await response.json();

      console.log("DISASTER RESULT:", result);

      setData(result);
    } catch (error) {
      console.error(error);
      alert("Could not connect to the disaster engine.");
    } finally {
      setLoading(false);
    }
  }



  return (
    <main className="min-h-screen bg-slate-950 text-white p-8">
      <div className="mx-auto max-w-7xl">

        {/* HEADER */}
        <div className="flex items-start justify-between mb-8">
          <div>
            <p className="text-yellow-400 font-semibold tracking-wider">
              DISASTER MANAGEMENT
            </p>

            <h1 className="text-4xl font-bold mt-2">
              Disaster Command Center
            </h1>

            <p className="text-slate-400 mt-2">
              Cascading Disaster Intelligence & Resource Allocation Platform
            </p>
          </div>

          <div className="text-right">

  <div className="flex rounded-lg border border-slate-700 bg-slate-900 p-1 mb-3">
    <button
      onClick={() => setMode("live")}
      className={`px-4 py-2 rounded-md text-sm font-semibold transition ${
        mode === "live"
          ? "bg-green-600 text-white"
          : "text-slate-400 hover:text-white"
      }`}
    >
      LIVE INTELLIGENCE
    </button>

    <button
      onClick={() => setMode("simulation")}
      className={`px-4 py-2 rounded-md text-sm font-semibold transition ${
        mode === "simulation"
          ? "bg-yellow-500 text-black"
          : "text-slate-400 hover:text-white"
      }`}
    >
      SIMULATION
    </button>
  </div>

  <button
    onClick={analyzeScenario}
    disabled={loading}
    className="rounded-lg bg-red-600 px-6 py-3 font-semibold hover:bg-red-500 disabled:opacity-50 transition-all"
  >
    {loading ? "ANALYZING..." : "ANALYZE DISASTER"}
  </button>

  {data && !loading && (
    <p className="mt-3 text-sm text-red-400">
      ● Disaster analysis active
    </p>
  )}

</div>
        </div>
        {mode === "simulation" && (
          <div className="mb-8 rounded-2xl border border-slate-800 bg-slate-900 p-6">
            <h2 className="text-lg font-semibold mb-4">
              Simulation Parameters
            </h2>

            <div className="grid md:grid-cols-3 gap-6">
              <div>
                <label className="text-sm text-slate-400">
                  Rainfall (mm)
                </label>

                <input
                  type="number"
                  min="0"
                  value={rainfall}
                  onChange={(e) =>
                    setRainfall(Number(e.target.value))
                  }
                  className="mt-2 w-full rounded-lg bg-slate-800 border border-slate-700 px-4 py-3 text-white"
                />
              </div>

              <div>
                <label className="text-sm text-slate-400">
                  Duration (hours)
                </label>

                <input
                  type="number"
                  min="0"
                  value={duration}
                  onChange={(e) =>
                    setDuration(Number(e.target.value))
                  }
                  className="mt-2 w-full rounded-lg bg-slate-800 border border-slate-700 px-4 py-3 text-white"
                />
              </div>

              <div>
                <label className="text-sm text-slate-400">
                  Water Level (m)
                </label>

                <input
                  type="number"
                  min="0"
                  value={waterLevel}
                  onChange={(e) =>
                    setWaterLevel(Number(e.target.value))
                  }
                  className="mt-2 w-full rounded-lg bg-slate-800 border border-slate-700 px-4 py-3 text-white"
                />
              </div>
            </div>
          </div>
        )}
        {/* STATS */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">

          <StatCard
            title="Risk Score"
            value={
              data
                ? data.event.risk_score.toFixed(2)
                : "—"
            }
          />

          <StatCard
            title="Hazard Level"
            value={
              data
                ? data.event.hazard_level
                : "NORMAL"
            }
          />

          <StatCard
            title="Affected Villages"
            value={
              data
                ? String(
                  data?.impact?.affected_villages?.length ?? 0
                )
                : "0"
            }
          />

          <StatCard
            title="Population Affected"
            value={
              data
                ? data?.impact?.population_affected?.toLocaleString() ?? "0"
                : "0"
            }
          />
        </div>

        {/* MAIN CONTENT */}
        <div className="grid lg:grid-cols-3 gap-6">

          {/* MAP */}
          <div className="lg:col-span-2 rounded-2xl border border-slate-800 bg-slate-900 p-6">
            <h2 className="text-xl font-semibold mb-4">
              Disaster Map
            </h2>

            <div className="h-[500px] rounded-xl overflow-hidden">
              <DisasterMap
                floodActive={!!data}
                allocation={
                  data?.resource_optimization?.allocations ?? []
                }
                affectedVillages={
                  data?.impact?.affected_villages ?? []
                }
                affectedRoads={
                  data?.impact?.affected_roads ?? []
                }
                affectedHospitals={
                  data?.impact?.affected_hospitals ?? []
                }
              />
            </div>
          </div>

          {/* CASCADING IMPACT */}
          <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
            <h2 className="text-xl font-semibold mb-6">
              Cascading Impact
            </h2>

            <div className="space-y-4 text-center">

              <FlowItem
                text={
                  data
                    ? `${data.event.type} — ${data.event.hazard_level}`
                    : "Extreme Rainfall"
                }
              />

              <Arrow />

              <FlowItem
                text={
                  data
                    ? `Flood Risk ${data.event.risk_score.toFixed(2)}`
                    : "Flood"
                }
              />

              <Arrow />

              <FlowItem
                text={
                  data
                    ? `${data?.impact?.affected_roads?.length ?? 0} Roads Affected`
                    : "Road Blockage"
                }
              />

              <Arrow />

              <FlowItem
                text={
                  data
                    ? `${data?.impact?.affected_villages?.length ?? 0} Villages Affected`
                    : "Village Isolation"
                }
              />

              <Arrow />

              <FlowItem
                text={
                  data
                    ? `${data?.impact?.affected_hospitals?.length ?? 0} Hospitals at Risk`
                    : "Hospital Access Risk"
                }
              />
            </div>
          </div>
        </div>

        {/* RECOMMENDED ACTIONS */}
        <div className="mt-6 rounded-2xl border border-slate-800 bg-slate-900 p-6">
          <div className="flex items-center justify-between mb-5">
            <h2 className="text-xl font-semibold">
              Recommended Actions
            </h2>

            {data && (
              <span className="text-sm text-green-400">
                Optimization:{" "}
                {data.resource_optimization.status}
              </span>
            )}
          </div>

          {!data ? (
            <p className="text-slate-400">
              Run a disaster analysis to generate recommendations.
            </p>
          ) : (
            <>
              <div className="grid md:grid-cols-3 gap-4">

                {data.resource_optimization.allocations
                  .filter(
                    (item) =>
                      item.resource_type === "AMBULANCE"
                  )
                  .map((item) => (
                    <div
                      key={item.resource}
                      className="rounded-xl border border-slate-700 bg-slate-800 p-4"
                    >
                      <div className="flex items-center justify-between">
                        <p className="text-yellow-400 font-semibold">
                          {item.resource}
                        </p>

                        <span className="text-xs rounded-full bg-red-500/20 px-2 py-1 text-red-300">
                          {item.priority_level}
                        </span>
                      </div>

                      <p className="mt-3 text-lg font-semibold">
                        Deploy → {item.village_id}
                      </p>

                      <p className="text-sm text-slate-400 mt-2">
                        Priority:{" "}
                        {item.priority_score.toFixed(2)}
                      </p>

                      <p className="text-sm text-slate-400">
                        Population:{" "}
                        {item.population.toLocaleString()}
                      </p>

                      <p className="text-sm text-slate-400">
                        Distance:{" "}
                        {item.distance_km.toFixed(2)} km
                      </p>

                      <p className="text-sm text-slate-400">
                        ETA:{" "}
                        {item.estimated_travel_time_min.toFixed(2)} min
                      </p>

                      <p className="text-xs text-slate-500 mt-3">
                        {item.reason}
                      </p>
                    </div>
                  ))}
              </div>

              {/* RESOURCE GAPS */}
              <div className="mt-6 grid md:grid-cols-2 gap-4">

                <div className="rounded-xl border border-slate-700 bg-slate-800 p-4">
                  <p className="text-yellow-400 font-semibold">
                    Ambulance Coverage
                  </p>

                  <p className="mt-2 text-sm text-slate-300">
                    Served:{" "}
                    {data.resource_optimization
                      .ambulance_coverage
                      .served_villages.join(", ") || "None"}
                  </p>

                  <p className="text-sm text-slate-400">
                    Unserved:{" "}
                    {data.resource_optimization
                      .ambulance_coverage
                      .unserved_villages.join(", ") || "None"}
                  </p>
                </div>

                <div className="rounded-xl border border-slate-700 bg-slate-800 p-4">
                  <p className="text-red-400 font-semibold">
                    Resource Gaps
                  </p>

                  <p className="mt-2 text-sm text-slate-300">
                    Rescue teams needed at:{" "}
                    {data?.resource_gaps?.rescue_teams?.join(", ") || "None"}
                  </p>
                </div>

              </div>
            </>
          )}
        </div>
      </div>
    </main>
  );
}

function StatCard({
  title,
  value,
}: {
  title: string;
  value: string;
}) {
  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
      <p className="text-sm text-slate-400">
        {title}
      </p>

      <p className="text-3xl font-bold mt-2">
        {value}
      </p>
    </div>
  );
}

function FlowItem({ text }: { text: string }) {
  return (
    <div className="rounded-lg bg-slate-800 border border-slate-700 p-3 font-medium">
      {text}
    </div>
  );
}

function Arrow() {
  return (
    <div className="text-yellow-400 text-xl">
      ↓
    </div>
  );
}