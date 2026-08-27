"use client";

import {
    MapContainer,
    TileLayer,
    Circle,
    CircleMarker,
    Polyline,
    Popup,
    Tooltip,
} from "react-leaflet";

import "leaflet/dist/leaflet.css";

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

type Props = {
    floodActive: boolean;
    allocation: Allocation[];
    affectedVillages: string[];
    affectedRoads: string[];
    affectedHospitals: string[];
};
const villages = {
    V1: [28.4744, 77.5040] as [number, number],
    V2: [28.4820, 77.5100] as [number, number],
    V3: [28.4680, 77.5150] as [number, number],
};

const hospitals = {
    H1: [28.4760, 77.5060] as [number, number],
    H2: [28.4840, 77.5120] as [number, number],
    H3: [28.4700, 77.5170] as [number, number],
};

const shelters = {
    S1: [28.4800, 77.5000] as [number, number],
    S2: [28.4660, 77.5120] as [number, number],
};

const ambulances = {
    A1: [28.4700, 77.5000] as [number, number],
    A2: [28.4750, 77.5200] as [number, number],
    A3: [28.4650, 77.5100] as [number, number],
};

const roads = {
    R1: [
        [28.4744, 77.5040],
        [28.4780, 77.5080],
    ] as [number, number][],

    R2: [
        [28.4800, 77.5070],
        [28.4850, 77.5130],
    ] as [number, number][],

    R3: [
        [28.4680, 77.5150],
        [28.4720, 77.5200],
    ] as [number, number][],
};

export default function DisasterMap({
    floodActive,
    allocation,
    affectedVillages,
    affectedRoads,
    affectedHospitals,
}: Props) {
    const isVillageAffected = (id: string) =>
        affectedVillages.includes(id);

    const isRoadAffected = (id: string) =>
        affectedRoads.includes(id);

    const isHospitalAffected = (id: string) =>
        affectedHospitals.includes(id);
    const resourceRoutes = floodActive
        ? allocation
            .filter(
                (item) => item.resource_type === "AMBULANCE"
            )
            .map((item) => ({
                resource: item.resource,

                from:
                    ambulances[
                    item.resource as keyof typeof ambulances
                    ],

                to:
                    villages[
                    item.village_id as keyof typeof villages
                    ],

                priority: item.priority_level,
                score: item.priority_score,
                reason: item.reason,
            }))
            .filter((route) => route.from && route.to)
        : [];

    return (
        <MapContainer
            center={[28.478, 77.509]}
            zoom={14}
            scrollWheelZoom
            className="h-full w-full rounded-xl"
        >
            <TileLayer
                attribution="&copy; OpenStreetMap contributors"
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />

            {/* ROADS */}

            <Polyline
                positions={roads.R1}
                pathOptions={{
                    color: isRoadAffected("R1")
                        ? "#dc2626"
                        : "#2563eb",
                    weight: isRoadAffected("R1") ? 7 : 5,
                    dashArray: isRoadAffected("R1")
                        ? "10 10"
                        : undefined,
                }}
            >
                <Popup>
                    <strong>Road R1</strong>
                    <br />
                    Status:{" "}
                    {isRoadAffected("R1") ? "AFFECTED" : "Open"}
                </Popup>
            </Polyline>
            <Polyline
                positions={roads.R3}
                pathOptions={{
                    color: isRoadAffected("R3")
                        ? "#dc2626"
                        : "#2563eb",
                    weight: isRoadAffected("R3") ? 7 : 5,
                    dashArray: isRoadAffected("R3")
                        ? "10 10"
                        : undefined,
                }}
            >
                <Popup>
                    <strong>Road R3</strong>
                    <br />
                    Status:{" "}
                    {isRoadAffected("R3") ? "AFFECTED" : "Open"}
                </Popup>
            </Polyline>

            <Polyline
                positions={roads.R2}
                pathOptions={{
                    color: isRoadAffected("R2")
                        ? "#dc2626"
                        : "#2563eb",
                    weight: isRoadAffected("R2") ? 7 : 5,
                    dashArray: isRoadAffected("R2")
                        ? "10 10"
                        : undefined,
                }}
            >
                <Popup>
                    <strong>Road R2</strong>
                    <br />
                    Status:{" "}
                    {isRoadAffected("R2") ? "AFFECTED" : "Open"}
                </Popup>
            </Polyline>
            {/* RESOURCE DEPLOYMENT ROUTES */}

            {resourceRoutes.map((route) => (
                <Polyline
                    key={route.resource}
                    positions={[route.from, route.to]}
                    pathOptions={{
                        color: "#f59e0b",
                        weight: 5,
                        opacity: 0.9,
                        dashArray: "8 8",
                    }}
                >
                    <Popup>
                        <strong>{route.resource} Deployment</strong>
                        <br />
                        Priority: {route.priority}
                        <br />
                        Score: {route.score.toFixed(2)}
                        <br />
                        {route.reason}
                    </Popup>
                </Polyline>
            ))}

            {/* HOSPITALS */}

            <CircleMarker
                center={hospitals.H1}
                radius={8}
                pathOptions={{
                    color: "#16a34a",
                    fillColor: "#22c55e",
                    fillOpacity: 0.9,
                }}
            >
                <Tooltip permanent direction="top">
                    H1
                </Tooltip>

                <Popup>
                    <strong>Hospital H1</strong>
                    <br />
                    Capacity: 100
                    {isHospitalAffected("H1") && (
                        <>
                            <br />
                            <strong style={{ color: "#dc2626" }}>
                                ACCESS AT RISK
                            </strong>
                        </>
                    )}
                </Popup>
            </CircleMarker>

            <CircleMarker
                center={hospitals.H2}
                radius={10}
                pathOptions={{
                    color: isHospitalAffected("H2")
                        ? "#dc2626"
                        : "#16a34a",
                    fillColor: isHospitalAffected("H2")
                        ? "#ef4444"
                        : "#22c55e",
                    fillOpacity: 0.9,
                }}
            >
                <Tooltip permanent direction="top">
                    H2
                </Tooltip>

                <Popup>
                    <strong>Hospital H2</strong>
                    <br />
                    Capacity: 80
                    {isHospitalAffected("H2") && (
                        <>
                            <br />
                            <strong style={{ color: "#dc2626" }}>
                                ACCESS AT RISK
                            </strong>
                        </>
                    )}
                </Popup>
            </CircleMarker>

            <CircleMarker
                center={hospitals.H3}
                radius={8}
                pathOptions={{
                    color: isHospitalAffected("H3")
                        ? "#dc2626"
                        : "#16a34a",
                    fillColor: isHospitalAffected("H3")
                        ? "#ef4444"
                        : "#22c55e",
                    fillOpacity: 0.9,
                }}
            >
                <Tooltip permanent direction="top">
                    H3
                </Tooltip>

                <Popup>
    <strong>Hospital H3</strong>
    <br />
    Capacity: 120
    {isHospitalAffected("H3") && (
        <>
            <br />
            <strong style={{ color: "#dc2626" }}>
                ACCESS AT RISK
            </strong>
        </>
    )}
</Popup>
            </CircleMarker>

            {/* SHELTERS */}

            <CircleMarker
                center={shelters.S1}
                radius={8}
                pathOptions={{
                    color: "#9333ea",
                    fillColor: "#a855f7",
                    fillOpacity: 0.9,
                }}
            >
                <Tooltip permanent direction="top">
                    S1
                </Tooltip>

                <Popup>
                    <strong>Shelter S1</strong>
                    <br />
                    Capacity: 500
                </Popup>
            </CircleMarker>

            <CircleMarker
                center={shelters.S2}
                radius={8}
                pathOptions={{
                    color: "#9333ea",
                    fillColor: "#a855f7",
                    fillOpacity: 0.9,
                }}
            >
                <Tooltip permanent direction="top">
                    S2
                </Tooltip>

                <Popup>
                    <strong>Shelter S2</strong>
                    <br />
                    Capacity: 700
                </Popup>
            </CircleMarker>

            {/* AMBULANCES */}

            <CircleMarker
                center={ambulances.A1}
                radius={7}
                pathOptions={{
                    color: "#d97706",
                    fillColor: "#f59e0b",
                    fillOpacity: 1,
                }}
            >
                <Tooltip permanent direction="bottom">
                    A1
                </Tooltip>

                <Popup>
                    <strong>Ambulance A1</strong>
                    <br />
                    Status: Available
                    {floodActive && (
                        <>
                            <br />
                            Deployment: Optimizer Assigned
                        </>
                    )}
                </Popup>
            </CircleMarker>

            <CircleMarker
                center={ambulances.A2}
                radius={7}
                pathOptions={{
                    color: "#d97706",
                    fillColor: "#f59e0b",
                    fillOpacity: 1,
                }}
            >
                <Tooltip permanent direction="bottom">
                    A2
                </Tooltip>

                <Popup>
                    <strong>Ambulance A2</strong>
                    <br />
                    Status: Available
                    {floodActive && (
                        <>
                            <br />
                            Deployment: Optimizer Assigned
                        </>
                    )}
                </Popup>
            </CircleMarker>

            <CircleMarker
                center={ambulances.A3}
                radius={7}
                pathOptions={{
                    color: "#d97706",
                    fillColor: "#f59e0b",
                    fillOpacity: 1,
                }}
            >
                <Tooltip permanent direction="bottom">
                    A3
                </Tooltip>

                <Popup>
    <strong>Ambulance A3</strong>
    <br />
    Status: Available

    {floodActive && (
        <>
            <br />
            Deployment: Optimizer Assigned
        </>
    )}
</Popup>
            </CircleMarker>
            {/* FLOOD ZONES */}

{floodActive &&
    affectedVillages.map((villageId) => {
        const center =
            villages[
                villageId as keyof typeof villages
            ];

        if (!center) return null;

        return (
            <Circle
                key={villageId}
                center={center}
                radius={villageId === "V2" ? 700 : 500}
                pathOptions={{
                    color: "#dc2626",
                    fillColor: "#ef4444",
                    fillOpacity:
                        villageId === "V2"
                            ? 0.18
                            : 0.12,
                    weight:
                        villageId === "V2"
                            ? 3
                            : 2,
                }}
            >
                <Popup>
                    <strong>
                        Flood Risk Zone — {villageId}
                    </strong>
                    <br />
                    Affected village
                </Popup>
            </Circle>
        );
    })}

            
            
        </MapContainer>
    );
}