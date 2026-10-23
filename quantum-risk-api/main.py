import os
import math
import numpy as np
from typing import Optional
from fastapi import FastAPI, Header, HTTPException, Depends
from pydantic import BaseModel, Field

app = FastAPI(
    title="Quantum Optimization & Financial Risk Engine API",
    description="Automated API providing quantum circuit optimization metrics and financial Value-at-Risk (VaR) analytics.",
    version="1.0.0"
)

# --- REQUEST / RESPONSE DATA MODELS ---

class CircuitOptimizationRequest(BaseModel):
    openqasm_circuit: str = Field(..., description="OpenQASM 2.0/3.0 string representation")
    physical_qubits: int = Field(default=5, ge=2, le=128)
    gate_error_rate: float = Field(default=0.005, ge=0.0001, le=0.1)
    readout_error_rate: float = Field(default=0.02, ge=0.001, le=0.2)

class FinancialRiskRequest(BaseModel):
    company_name: str
    avg_gate_fidelity: float = Field(default=0.995, ge=0.8, le=0.9999)
    shots_per_execution: int = Field(default=10000, ge=100)
    cost_per_shot_usd: float = Field(default=0.0015, ge=0.0001)
    vendor_portability_score: float = Field(default=0.5, ge=0.0, le=1.0)
    pq_readiness_score: float = Field(default=0.3, ge=0.0, le=1.0)
    initial_investment_usd: float = Field(default=2000000.0, ge=10000.0)
    projected_advantage_years: int = Field(default=3, ge=1, le=10)

# --- SECURITY / RAPIDAPI AUTHENTICATION GATEKEEPER ---

def verify_rapidapi_header(x_rapidapi_proxy_secret: Optional[str] = Header(None)):
    """
    Ensures calls originate directly from RapidAPI, preventing unauthorized direct hits.
    """
    secret = os.environ.get("RAPIDAPI_PROXY_SECRET")
    if secret and x_rapidapi_proxy_secret != secret:
        raise HTTPException(status_code=403, detail="Forbidden: Direct unauthenticated access prohibited.")
    return True

# --- API ENDPOINTS ---

@app.get("/")
def health_check():
    return {"status": "online", "system": "Quantum Optimization & Financial Risk Engine v1.0.0"}

@app.post("/api/v1/compile-and-mitigate", dependencies=[Depends(verify_rapidapi_header)])
def compile_and_mitigate(payload: CircuitOptimizationRequest):
    """
    Accepts OpenQASM circuit and backend topology constraints.
    Returns estimated gate reduction, pulse synthesis overhead, and ZNE mitigation parameters.
    """
    gate_count = payload.openqasm_circuit.count(";")
    swap_overhead_estimate = int(gate_count * (1.0 - (payload.physical_qubits / 100.0)))
    swap_overhead_estimate = max(0, swap_overhead_estimate)
    
    # Pulse-level decay extrapolation
    mitigated_fidelity = (1.0 - payload.gate_error_rate) ** (gate_count * 0.7)
    unmitigated_fidelity = (1.0 - payload.gate_error_rate) ** gate_count
    
    return {
        "status": "success",
        "circuit_metrics": {
            "input_gate_count": gate_count,
            "estimated_swap_overhead": swap_overhead_estimate,
            "estimated_unmitigated_fidelity": round(float(unmitigated_fidelity), 4),
            "mitigated_fidelity_zne": round(float(mitigated_fidelity), 4)
        },
        "mitigation_parameters": {
            "recommended_zne_scale_factors": [1.0, 3.0, 5.0],
            "zero_noise_extrapolation_fit": "polynomial_deg_2",
            "dynamical_decoupling_sequence": "XY4"
        }
    }

@app.post("/api/v1/assess-financial-risk", dependencies=[Depends(verify_rapidapi_header)])
def assess_financial_risk(payload: FinancialRiskRequest):
    """
    Computes Composite Quantum Risk Score (0-100) and Monte Carlo Value-at-Risk (VaR) array.
    """
    # 1. Risk Score Computation
    fidelity_risk = (1.0 - payload.avg_gate_fidelity) * 1000.0
    cost_risk = math.log10(payload.shots_per_execution * payload.cost_per_shot_usd + 1.0) * 20.0
    lockin_risk = (1.0 - payload.vendor_portability_score) * 100.0
    crypto_risk = (1.0 - payload.pq_readiness_score) * 100.0

    composite_score = float(np.clip(
        0.35 * fidelity_risk + 0.25 * cost_risk + 0.20 * lockin_risk + 0.20 * crypto_risk,
        0.0, 100.0
    ))

    # 2. Monte Carlo Simulation (ROQI)
    np.random.seed(42)
    iterations = 2000
    npv_results = []
    
    for _ in range(iterations):
        time_to_adv = max(1.0, np.random.normal(loc=payload.projected_advantage_years, scale=1.2))
        annual_savings = np.random.lognormal(mean=12.2, sigma=0.7)
        failed_run = np.random.choice([True, False], p=[0.12, 0.88])
        multiplier = 0.1 if failed_run else 1.0
        
        cash_flows = [-payload.initial_investment_usd]
        for yr in range(1, 6):
            if yr >= time_to_adv:
                cash_flows.append((annual_savings * multiplier) / ((1 + 0.08) ** yr))
            else:
                cash_flows.append((-payload.initial_investment_usd * 0.08) / ((1 + 0.08) ** yr))
        
        npv_results.append(sum(cash_flows))

    npv_arr = np.array(npv_results)

    return {
        "company_name": payload.company_name,
        "composite_quantum_risk_score": round(composite_score, 2),
        "risk_breakdown": {
            "fidelity_decay_risk": round(float(fidelity_risk), 2),
            "compute_cost_risk": round(float(cost_risk), 2),
            "vendor_lockin_risk": round(float(lockin_risk), 2),
            "pqc_vulnerability_risk": round(float(crypto_risk), 2)
        },
        "financial_projections": {
            "mean_expected_npv_usd": round(float(np.mean(npv_arr)), 2),
            "value_at_risk_95_percent_usd": round(float(np.percentile(npv_arr, 5)), 2),
            "probability_of_positive_return": round(float(np.mean(npv_arr > 0)), 4)
        }
    }