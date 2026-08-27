import json

from ml_predictor import predict_ml_risk
from hazard_engine import analyze_hazard
from cascade_engine import calculate_cascade
from priority_engine import calculate_priorities
from resource_optimizer import optimize_resources


def run_disaster_pipeline(
    rainfall_mm: float = 180.0,
    duration_hours: float = 4.0,
    water_level_m: float = 8.0,
    rainfall_1h_mm: float | None = None,
    rainfall_3h_mm: float | None = None,
    rainfall_6h_mm: float | None = None,
    rainfall_12h_mm: float | None = None,
    rainfall_24h_mm: float | None = None,
) -> dict:

    # -------------------------------------------------
    # 1. HAZARD / ML RISK
    # -------------------------------------------------

    ml_ready = all(
        value is not None
        for value in [
            rainfall_1h_mm,
            rainfall_3h_mm,
            rainfall_6h_mm,
            rainfall_12h_mm,
            rainfall_24h_mm,
        ]
    )

    if ml_ready:
        # Use the trained XGBoost model
        ml_result = predict_ml_risk(
            rainfall_1h_mm=rainfall_1h_mm,
            rainfall_3h_mm=rainfall_3h_mm,
            rainfall_6h_mm=rainfall_6h_mm,
            rainfall_12h_mm=rainfall_12h_mm,
            rainfall_24h_mm=rainfall_24h_mm,
        )

        risk_score = ml_result["risk_score"]
        hazard_level = ml_result["hazard_level"]
        confidence = ml_result["confidence"]
        hazard_type = "ML_FLOOD_RISK"

    else:
        # Fallback to the existing rule-based hazard engine
        hazard_result = analyze_hazard(
            rainfall_mm=rainfall_mm,
            duration_hours=duration_hours,
            water_level_m=water_level_m,
        )

        risk_score = hazard_result["risk_score"]
        hazard_level = hazard_result["hazard_level"]
        confidence = None
        hazard_type = hazard_result["type"]

    # -------------------------------------------------
    # 2. CASCADING IMPACT
    # -------------------------------------------------

    cascade_result = calculate_cascade(risk_score)

    # -------------------------------------------------
    # 3. PRIORITY ASSESSMENT
    # -------------------------------------------------

    priorities = calculate_priorities(cascade_result)

    # -------------------------------------------------
    # 4. RESOURCE OPTIMIZATION
    # -------------------------------------------------

    resource_result = optimize_resources(priorities)

    ambulance_unserved = (
        resource_result["ambulance_coverage"]["unserved_villages"]
    )

    rescue_unserved = (
        resource_result["rescue_team_coverage"]["unserved_villages"]
    )

    # -------------------------------------------------
    # 5. OVERALL STATUS
    # -------------------------------------------------

    if ambulance_unserved or rescue_unserved:
        overall_status = "RESOURCE_CONSTRAINED"
    elif not cascade_result["affected_villages"]:
        overall_status = "NO_AFFECTED_ZONES"
    else:
        overall_status = "FULLY_COVERED"

    # -------------------------------------------------
    # 6. FINAL RESPONSE
    # -------------------------------------------------

    return {
        "status": overall_status,
        "event": {
            "type": hazard_type,
            "risk_score": risk_score,
            "hazard_level": hazard_level,
            "confidence": confidence,
            "inputs": {
                "rainfall_mm": rainfall_mm,
                "duration_hours": duration_hours,
                "water_level_m": water_level_m,
                "rainfall_1h_mm": rainfall_1h_mm,
                "rainfall_3h_mm": rainfall_3h_mm,
                "rainfall_6h_mm": rainfall_6h_mm,
                "rainfall_12h_mm": rainfall_12h_mm,
                "rainfall_24h_mm": rainfall_24h_mm,
            },
        },
        "impact": {
            "affected_roads": cascade_result["affected_roads"],
            "affected_villages": cascade_result["affected_villages"],
            "affected_hospitals": cascade_result["affected_hospitals"],
            "population_affected": cascade_result["population_affected"],
        },
        "priority_assessment": priorities,
        "resource_optimization": resource_result,
        "resource_gaps": {
            "ambulances": ambulance_unserved,
            "rescue_teams": rescue_unserved,
        },
    }


if __name__ == "__main__":
    result = run_disaster_pipeline(
        rainfall_mm=180,
        duration_hours=4,
        water_level_m=8,
        rainfall_1h_mm=60,
        rainfall_3h_mm=120,
        rainfall_6h_mm=180,
        rainfall_12h_mm=240,
        rainfall_24h_mm=310,
    )

    print("\n==============================================")
    print("      CASCADING DISASTER INTELLIGENCE")
    print("==============================================")

    print("\n========== SYSTEM STATUS ==========")
    print("Status:", result["status"])

    print("\n========== HAZARD ANALYSIS ==========")
    print("Type:", result["event"]["type"])
    print("Risk Score:", result["event"]["risk_score"])
    print("Hazard Level:", result["event"]["hazard_level"])
    print("Confidence:", result["event"]["confidence"])

    print("\n========== INPUTS ==========")
    print("Rainfall 1h:", result["event"]["inputs"]["rainfall_1h_mm"])
    print("Rainfall 3h:", result["event"]["inputs"]["rainfall_3h_mm"])
    print("Rainfall 6h:", result["event"]["inputs"]["rainfall_6h_mm"])
    print("Rainfall 12h:", result["event"]["inputs"]["rainfall_12h_mm"])
    print("Rainfall 24h:", result["event"]["inputs"]["rainfall_24h_mm"])

    print("\n========== CASCADING IMPACT ==========")
    print("Affected Roads:", result["impact"]["affected_roads"])
    print("Affected Villages:", result["impact"]["affected_villages"])
    print("Affected Hospitals:", result["impact"]["affected_hospitals"])
    print("Population Affected:", result["impact"]["population_affected"])

    print("\n========== PRIORITY ASSESSMENT ==========")
    for priority in result["priority_assessment"]:
        print(
            f"{priority['village_id']} | "
            f"Population: {priority['population']} | "
            f"Priority: {priority['priority_score']:.2f} | "
            f"Level: {priority['priority_level']}"
        )

    print("\n========== RESOURCE ALLOCATION ==========")
    for allocation in result["resource_optimization"]["allocations"]:
        print(
            f"{allocation['resource']} "
            f"({allocation['resource_type']}) -> "
            f"{allocation['village_id']} | "
            f"Priority: {allocation['priority_score']:.2f} | "
            f"Distance: {allocation['distance_km']} km | "
            f"ETA: {allocation['estimated_travel_time_min']} min"
        )

    print("\n========== RESOURCE GAPS ==========")
    print(
        "Ambulance Gaps:",
        result["resource_gaps"]["ambulances"],
    )
    print(
        "Rescue Team Gaps:",
        result["resource_gaps"]["rescue_teams"],
    )

    print("\n========== FINAL JSON ==========")
    print(json.dumps(result, indent=4))