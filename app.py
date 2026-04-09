import streamlit as st
import plotly.graph_objects as go
import anthropic

# Page config - must be the first Streamlit call
st.set_page_config(
    page_title="Material Compatibility & Production Risk Dashboard",
    page_icon=":gear:",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Design CSS
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
/* Base */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* App background */
.stApp {
    background-color: #0d0f14;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #13161e !important;
    border-right: 1px solid #1f2330;
}
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stTextInput label {
    color: #9aa0b0 !important;
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}

/* Hero header */
.hero-header {
    background: linear-gradient(135deg, #1a1d27 0%, #0f1219 60%, #1a1020 100%);
    border: 1px solid #2a2d3d;
    border-radius: 16px;
    padding: 32px 36px;
    margin-bottom: 28px;
    position: relative;
    overflow: hidden;
}
.hero-header::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, #f0a500, #ff6b6b, #7c5cbf);
}
.hero-header h1 {
    font-size: 1.7rem;
    font-weight: 700;
    color: #ffffff;
    margin: 0 0 6px 0;
    letter-spacing: -0.02em;
}
.hero-header p {
    color: #6b7280;
    font-size: 0.88rem;
    margin: 0;
}
.hero-badge {
    display: inline-block;
    background: rgba(240,165,0,0.12);
    border: 1px solid rgba(240,165,0,0.3);
    color: #f0a500;
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    padding: 3px 10px;
    border-radius: 20px;
    margin-bottom: 12px;
}

/* Metric cards */
[data-testid="stMetric"] {
    background: linear-gradient(145deg, #1a1d27, #14171f);
    border: 1px solid #1f2330;
    border-radius: 12px;
    padding: 18px 20px;
    transition: border-color 0.2s;
}
[data-testid="stMetric"]:hover {
    border-color: #2e3347;
}
[data-testid="stMetricLabel"] p {
    color: #6b7280 !important;
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.07em;
}
[data-testid="stMetricValue"] {
    color: #f0f0f0 !important;
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.4rem !important;
}

/* Pairing header */
.pairing-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 20px;
    padding: 14px 20px;
    background: #13161e;
    border: 1px solid #1f2330;
    border-radius: 10px;
}
.pairing-mat {
    background: #1f2330;
    border-radius: 6px;
    padding: 5px 12px;
    color: #e0e0e0;
    font-size: 0.88rem;
    font-weight: 500;
}
.pairing-plus {
    color: #4b5268;
    font-size: 1.1rem;
    font-weight: 600;
}

/* Banners */
.go-banner {
    background: linear-gradient(135deg, #061a0e, #0a2e1a);
    border: 1px solid #00c851;
    border-left: 4px solid #00c851;
    border-radius: 12px;
    padding: 20px 28px;
    display: flex;
    align-items: center;
    gap: 14px;
    font-size: 1.1rem;
    font-weight: 700;
    color: #00c851;
    letter-spacing: 0.02em;
}
.caution-banner {
    background: linear-gradient(135deg, #1a1200, #2e2200);
    border: 1px solid #f0a500;
    border-left: 4px solid #f0a500;
    border-radius: 12px;
    padding: 20px 28px;
    display: flex;
    align-items: center;
    gap: 14px;
    font-size: 1.1rem;
    font-weight: 700;
    color: #f0a500;
    letter-spacing: 0.02em;
}
.nogo-banner {
    background: linear-gradient(135deg, #1a0606, #2e0a0a);
    border: 1px solid #ff4444;
    border-left: 4px solid #ff4444;
    border-radius: 12px;
    padding: 20px 28px;
    display: flex;
    align-items: center;
    gap: 14px;
    font-size: 1.1rem;
    font-weight: 700;
    color: #ff4444;
    letter-spacing: 0.02em;
}
.banner-icon { font-size: 1.4rem; }
.banner-sub { font-size: 0.8rem; font-weight: 400; opacity: 0.7; margin-left: auto; }

/* Detail card */
.detail-card {
    background: linear-gradient(145deg, #1a1d27, #14171f);
    border: 1px solid #1f2330;
    border-radius: 14px;
    padding: 24px 26px;
    height: 100%;
}
.detail-card h4 {
    color: #f0a500;
    margin: 0 0 16px 0;
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    font-weight: 600;
}
.detail-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
    padding-bottom: 10px;
    border-bottom: 1px solid #1a1d27;
}
.detail-row:last-of-type { border-bottom: none; }
.detail-label { color: #6b7280; font-size: 0.82rem; }
.detail-value { color: #d1d5db; font-family: 'JetBrains Mono', monospace; font-size: 0.82rem; font-weight: 500; }
.risk-low { color: #00c851; }
.risk-med { color: #f0a500; }
.risk-high { color: #ff4444; }

.notes-box {
    background: #0d0f14;
    border: 1px solid #1f2330;
    border-radius: 8px;
    padding: 14px 16px;
    margin-top: 16px;
}
.notes-box p {
    color: #9aa0b0;
    font-size: 0.84rem;
    line-height: 1.7;
    margin: 0;
}

/* Claude answer box */
.claude-box {
    background: linear-gradient(145deg, #1a1d27, #14171f);
    border: 1px solid #1f2330;
    border-left: 3px solid #f0a500;
    border-radius: 12px;
    padding: 22px 26px;
    font-size: 0.9rem;
    line-height: 1.75;
    white-space: pre-wrap;
    color: #d1d5db;
    font-family: 'Inter', sans-serif;
}

/* Section heading */
.section-heading {
    font-size: 0.7rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: #4b5268;
    margin: 24px 0 12px 0;
}

/* Divider override */
hr { border-color: #1f2330 !important; }

/* Button */
.stButton > button {
    border-radius: 8px !important;
    font-weight: 600 !important;
    letter-spacing: 0.02em !important;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Compatibility matrix
# ---------------------------------------------------------------------------
MATERIALS = [
    "316 Stainless Steel",
    "PEEK",
    "Nitrile (NBR)",
    "Aluminum 6061",
    "Titanium Grade 5",
    "Inconel 625",
    "PTFE",
    "Carbon Steel A36",
]

# Keys: (matA, matB) - symmetric; values: dict of properties
COMPAT_MATRIX = {
    ("316 Stainless Steel", "PEEK"): {
        "chemical_compat": 9, "cte_delta": 11.0, "galvanic_risk": "Low",
        "supply_chain_risk": 3, "risk_score": 2,
        "notes": "Excellent chemical inertness. CTE mismatch (~11 um/m.C) can cause interface stress at high thermal cycles. Design for compliance.",
    },
    ("316 Stainless Steel", "Nitrile (NBR)"): {
        "chemical_compat": 8, "cte_delta": 140.0, "galvanic_risk": "Low",
        "supply_chain_risk": 2, "risk_score": 3,
        "notes": "Good chemical compatibility. Extreme CTE mismatch due to rubber elasticity. Seal geometry must accommodate large deflections.",
    },
    ("316 Stainless Steel", "Aluminum 6061"): {
        "chemical_compat": 6, "cte_delta": 7.1, "galvanic_risk": "High",
        "supply_chain_risk": 1, "risk_score": 7,
        "notes": "Active galvanic cell in the presence of electrolyte. Anodize or isolate with PTFE washers. CTE delta manageable at moderate temps.",
    },
    ("316 Stainless Steel", "Titanium Grade 5"): {
        "chemical_compat": 9, "cte_delta": 7.8, "galvanic_risk": "Low",
        "supply_chain_risk": 4, "risk_score": 2,
        "notes": "High compatibility. Titanium passivates well next to SS316. Minor CTE delta. Galling risk under high load - lubricate fasteners.",
    },
    ("316 Stainless Steel", "Inconel 625"): {
        "chemical_compat": 9, "cte_delta": 3.0, "galvanic_risk": "Low",
        "supply_chain_risk": 5, "risk_score": 2,
        "notes": "Excellent hot pairing for high-temperature service. Low CTE mismatch. Both alloys passivate; galvanic risk negligible.",
    },
    ("316 Stainless Steel", "PTFE"): {
        "chemical_compat": 10, "cte_delta": 115.0, "galvanic_risk": "Low",
        "supply_chain_risk": 2, "risk_score": 2,
        "notes": "Chemically ideal. Large CTE delta but PTFE compliance compensates. Creep under load is main concern - pre-load carefully.",
    },
    ("316 Stainless Steel", "Carbon Steel A36"): {
        "chemical_compat": 7, "cte_delta": 0.5, "galvanic_risk": "Med",
        "supply_chain_risk": 1, "risk_score": 5,
        "notes": "Moderate galvanic risk in wet environments. Near-identical CTE. Use barrier coating or isolation in corrosive service.",
    },
    ("PEEK", "Nitrile (NBR)"): {
        "chemical_compat": 7, "cte_delta": 120.0, "galvanic_risk": "Low",
        "supply_chain_risk": 3, "risk_score": 3,
        "notes": "Polymer-on-polymer; no galvanic risk. PEEK is chemically robust against most NBR service fluids. Thermal design challenge.",
    },
    ("PEEK", "Aluminum 6061"): {
        "chemical_compat": 9, "cte_delta": 14.0, "galvanic_risk": "Low",
        "supply_chain_risk": 2, "risk_score": 3,
        "notes": "Good polymer-metal pairing. CTE mismatch may loosen joints over thermal cycles - use retention features or adhesive.",
    },
    ("PEEK", "Titanium Grade 5"): {
        "chemical_compat": 9, "cte_delta": 7.4, "galvanic_risk": "Low",
        "supply_chain_risk": 5, "risk_score": 3,
        "notes": "Premium pairing for aerospace/medical. Low galvanic risk. PEEK cold flows under sustained compressive load.",
    },
    ("PEEK", "Inconel 625"): {
        "chemical_compat": 8, "cte_delta": 11.4, "galvanic_risk": "Low",
        "supply_chain_risk": 6, "risk_score": 4,
        "notes": "High-cost combination. PEEK limited to 260 C continuous - confirm temperature envelope before specifying with Inconel.",
    },
    ("PEEK", "PTFE"): {
        "chemical_compat": 10, "cte_delta": 100.0, "galvanic_risk": "Low",
        "supply_chain_risk": 2, "risk_score": 1,
        "notes": "Excellent polymer-polymer pairing. Both chemically inert. No galvanic risk. High CTE delta manageable with sliding interfaces.",
    },
    ("PEEK", "Carbon Steel A36"): {
        "chemical_compat": 8, "cte_delta": 6.3, "galvanic_risk": "Low",
        "supply_chain_risk": 1, "risk_score": 3,
        "notes": "Acceptable in dry or mild environments. PEEK chemical resistance protects the interface. Modest CTE delta.",
    },
    ("Nitrile (NBR)", "Aluminum 6061"): {
        "chemical_compat": 7, "cte_delta": 133.0, "galvanic_risk": "Low",
        "supply_chain_risk": 1, "risk_score": 3,
        "notes": "Common sealing application. NBR swells slightly with aromatic solvents - verify fluid compatibility. Extreme CTE delta expected.",
    },
    ("Nitrile (NBR)", "Titanium Grade 5"): {
        "chemical_compat": 8, "cte_delta": 140.0, "galvanic_risk": "Low",
        "supply_chain_risk": 5, "risk_score": 4,
        "notes": "No galvanic or chemical concern. Large CTE mismatch inherent to metal-elastomer pairings. Design groove to accommodate.",
    },
    ("Nitrile (NBR)", "Inconel 625"): {
        "chemical_compat": 7, "cte_delta": 150.0, "galvanic_risk": "Low",
        "supply_chain_risk": 6, "risk_score": 4,
        "notes": "Avoid if service temp exceeds NBR limit (~120 C). Consider FFKM or Viton for high-temp Inconel service.",
    },
    ("Nitrile (NBR)", "PTFE"): {
        "chemical_compat": 9, "cte_delta": 20.0, "galvanic_risk": "Low",
        "supply_chain_risk": 2, "risk_score": 2,
        "notes": "Both elastomeric/semi-elastomeric; compliance accommodates CTE differences. Common composite seal design.",
    },
    ("Nitrile (NBR)", "Carbon Steel A36"): {
        "chemical_compat": 8, "cte_delta": 137.0, "galvanic_risk": "Low",
        "supply_chain_risk": 1, "risk_score": 3,
        "notes": "Standard industrial seal application. CTE delta is inherent to metal-rubber. Ensure surface finish Rz <= 1.6 um for sealing.",
    },
    ("Aluminum 6061", "Titanium Grade 5"): {
        "chemical_compat": 7, "cte_delta": 14.9, "galvanic_risk": "Med",
        "supply_chain_risk": 4, "risk_score": 5,
        "notes": "Moderate galvanic concern in saline or acidic media. Anodize aluminum and isolate with PTFE. Ti is cathodic - Al will corrode.",
    },
    ("Aluminum 6061", "Inconel 625"): {
        "chemical_compat": 5, "cte_delta": 17.0, "galvanic_risk": "High",
        "supply_chain_risk": 5, "risk_score": 8,
        "notes": "Severe galvanic incompatibility. Inconel is strongly cathodic. Accelerated pitting on Al in any electrolyte. Avoid direct contact.",
    },
    ("Aluminum 6061", "PTFE"): {
        "chemical_compat": 9, "cte_delta": 116.0, "galvanic_risk": "Low",
        "supply_chain_risk": 2, "risk_score": 2,
        "notes": "Excellent chemical pairing. PTFE bearings on aluminum are common. Cold flow of PTFE under preload is the primary concern.",
    },
    ("Aluminum 6061", "Carbon Steel A36"): {
        "chemical_compat": 6, "cte_delta": 7.0, "galvanic_risk": "High",
        "supply_chain_risk": 1, "risk_score": 7,
        "notes": "Classic galvanic couple. Carbon steel is anodic near Al in salt spray. Heavy corrosion risk in outdoor or marine environments.",
    },
    ("Titanium Grade 5", "Inconel 625"): {
        "chemical_compat": 9, "cte_delta": 2.1, "galvanic_risk": "Low",
        "supply_chain_risk": 6, "risk_score": 3,
        "notes": "Excellent high-performance pairing. Very low CTE delta. Both alloys passivate in most environments. High material cost.",
    },
    ("Titanium Grade 5", "PTFE"): {
        "chemical_compat": 10, "cte_delta": 106.5, "galvanic_risk": "Low",
        "supply_chain_risk": 4, "risk_score": 2,
        "notes": "Biocompatible pairing, common in medical devices. No galvanic or chemical concern. High CTE delta - design for PTFE compliance.",
    },
    ("Titanium Grade 5", "Carbon Steel A36"): {
        "chemical_compat": 7, "cte_delta": 7.4, "galvanic_risk": "Med",
        "supply_chain_risk": 3, "risk_score": 5,
        "notes": "Titanium is cathodic; steel corrodes preferentially. Use isolation sleeves or barrier coating in corrosive service.",
    },
    ("Inconel 625", "PTFE"): {
        "chemical_compat": 9, "cte_delta": 118.6, "galvanic_risk": "Low",
        "supply_chain_risk": 5, "risk_score": 3,
        "notes": "Compatible for valve seats and high-temp sealing. PTFE upper temp limit (260 C) must be observed with Inconel service.",
    },
    ("Inconel 625", "Carbon Steel A36"): {
        "chemical_compat": 6, "cte_delta": 2.4, "galvanic_risk": "High",
        "supply_chain_risk": 4, "risk_score": 7,
        "notes": "Strong galvanic couple - carbon steel corrodes rapidly. Use only if fully isolated. Low CTE mismatch is the one advantage.",
    },
    ("PTFE", "Carbon Steel A36"): {
        "chemical_compat": 9, "cte_delta": 121.0, "galvanic_risk": "Low",
        "supply_chain_risk": 2, "risk_score": 2,
        "notes": "Common liner/coating application. PTFE protects steel from chemical attack. Cold flow under bolt preload must be managed.",
    },
}


def get_compat(mat_a, mat_b):
    if mat_a == mat_b:
        return None
    return COMPAT_MATRIX.get((mat_a, mat_b)) or COMPAT_MATRIX.get((mat_b, mat_a))


def risk_color(score):
    if score <= 4:
        return "#00c851"
    elif score <= 6:
        return "#f0a500"
    return "#ff4444"


def build_gauge(score):
    color = risk_color(score)
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        domain={"x": [0, 1], "y": [0, 1]},
        title={"text": "Composite Risk Score", "font": {"color": "#9aa0b0", "size": 13}},
        number={"font": {"color": color, "size": 40}, "suffix": "/10"},
        gauge={
            "axis": {"range": [0, 10], "tickcolor": "#9aa0b0",
                     "tickfont": {"color": "#9aa0b0"}},
            "bar": {"color": color},
            "bgcolor": "#1c1f26",
            "bordercolor": "#2a2d35",
            "steps": [
                {"range": [0, 4],  "color": "#0a2e1a"},
                {"range": [4, 6],  "color": "#2e2200"},
                {"range": [6, 10], "color": "#2e0a0a"},
            ],
            "threshold": {
                "line": {"color": color, "width": 3},
                "thickness": 0.8,
                "value": score,
            },
        },
    ))
    fig.update_layout(
        paper_bgcolor="#1c1f26",
        plot_bgcolor="#1c1f26",
        font={"color": "#e0e0e0"},
        height=260,
        margin={"t": 40, "b": 0, "l": 20, "r": 20},
    )
    return fig


def consult_claude(api_key, mat_a, mat_b, score, question):
    client = anthropic.Anthropic(api_key=api_key)
    system = (
        "You are a senior material science and production engineering consultant with 20+ years "
        "of industrial experience. Be precise and concise. Cite specific failure modes, use "
        "engineering units, and reference relevant standards (ASTM, ISO, NACE) where applicable."
    )
    user_msg = (
        f"Material Pairing: {mat_a} + {mat_b}  |  Composite Risk Score: {score}/10\n\n"
        f"Engineer question: {question}"
    )
    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=1024,
        thinking={"type": "adaptive"},
        system=system,
        messages=[{"role": "user", "content": user_msg}],
    )
    for block in response.content:
        if block.type == "text":
            return block.text
    return "No response received."


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### ⚙️ MatCompat Pro")
    st.caption("Material Compatibility & Production Risk")
    st.divider()

    # Load API key from Streamlit secrets (deployed) or user input (local)
    secret_key = st.secrets.get("ANTHROPIC_API_KEY", "") if hasattr(st, "secrets") else ""
    if secret_key:
        api_key = secret_key
    else:
        api_key = st.text_input(
            "Anthropic API Key",
            type="password",
            placeholder="sk-ant-...",
            help="Required for the Consult Claude feature.",
        )
    st.divider()

    st.markdown("### Material Selection")
    mat_a = st.selectbox("Material A", MATERIALS, index=0)
    mat_b = st.selectbox("Material B", MATERIALS, index=3)
    analyze = st.button("Analyze Pair", use_container_width=True, type="primary")

    st.divider()
    st.caption("MatCompat Pro v1.0 | Production Engineering Tool")

# ---------------------------------------------------------------------------
# Main panel
# ---------------------------------------------------------------------------
st.markdown("""
<div class="hero-header">
    <div class="hero-badge">Production Engineering Tool</div>
    <h1>Material Compatibility & Production Risk Dashboard</h1>
    <p>Select two materials to analyse galvanic risk, CTE mismatch, chemical compatibility, and supply chain exposure.</p>
</div>
""", unsafe_allow_html=True)

# Placeholder when no analysis yet
if not analyze and "compat_data" not in st.session_state:
    st.info("Select two materials in the sidebar and click **Analyze Pair** to begin.")

# Run analysis
if analyze:
    if mat_a == mat_b:
        st.warning("Please select two different materials.")
    else:
        data = get_compat(mat_a, mat_b)
        if data is None:
            st.error("Compatibility data not available for this pairing.")
        else:
            st.session_state["compat_data"] = data
            st.session_state["mat_a"] = mat_a
            st.session_state["mat_b"] = mat_b

# Display results
if "compat_data" in st.session_state:
    data   = st.session_state["compat_data"]
    mat_a_s = st.session_state["mat_a"]
    mat_b_s = st.session_state["mat_b"]
    score  = data["risk_score"]

    # Pairing header
    st.markdown(f"""
    <div class="pairing-header">
        <span class="pairing-mat">{mat_a_s}</span>
        <span class="pairing-plus">+</span>
        <span class="pairing-mat">{mat_b_s}</span>
    </div>
    """, unsafe_allow_html=True)

    # Metrics row
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Composite Risk",         f"{score} / 10")
    m2.metric("Chemical Compatibility", f"{data['chemical_compat']} / 10")
    m3.metric("CTE Delta",              f"{data['cte_delta']:.1f} um/m.C")
    m4.metric("Supply Chain Risk",      f"{data['supply_chain_risk']} / 10")

    st.markdown("<br>", unsafe_allow_html=True)

    # Go / No-Go banner
    if score <= 4:
        st.markdown(
            f'<div class="go-banner"><span class="banner-icon">✅</span> GO — Acceptable Pairing<span class="banner-sub">Risk Score: {score} / 10</span></div>',
            unsafe_allow_html=True,
        )
    elif score <= 6:
        st.markdown(
            f'<div class="caution-banner"><span class="banner-icon">⚠️</span> CAUTION — Engineering Review Required<span class="banner-sub">Risk Score: {score} / 10</span></div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<div class="nogo-banner"><span class="banner-icon">🚫</span> NO-GO — High Risk Pairing<span class="banner-sub">Risk Score: {score} / 10</span></div>',
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Detail card + Gauge
    col_left, col_right = st.columns(2)

    gal_map  = {"Low": "risk-low", "Med": "risk-med", "High": "risk-high"}
    gal_cls  = gal_map.get(data["galvanic_risk"], "")

    with col_left:
        st.markdown(
            f"""
            <div class="detail-card">
                <h4>Technical Details</h4>
                <div class="detail-row">
                    <span class="detail-label">Material A</span>
                    <span class="detail-value">{mat_a_s}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Material B</span>
                    <span class="detail-value">{mat_b_s}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Galvanic Risk</span>
                    <span class="detail-value {gal_cls}">{data["galvanic_risk"]}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">CTE Delta</span>
                    <span class="detail-value">{data["cte_delta"]:.1f} um/m.C</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Chemical Compat.</span>
                    <span class="detail-value">{data["chemical_compat"]}/10</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Supply Chain Risk</span>
                    <span class="detail-value">{data["supply_chain_risk"]}/10</span>
                </div>
                <div class="notes-box">
                    <h4 style="margin-bottom:8px">Engineering Notes</h4>
                    <p>{data["notes"]}</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_right:
        fig = build_gauge(score)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    # Consult Claude
    st.divider()
    st.markdown('<div class="section-heading">Consult Claude — Production AI</div>', unsafe_allow_html=True)

    suggestion = f"Will {mat_a_s} and {mat_b_s} gall under high vacuum at elevated temperature?"
    st.info(f"Suggested question: {suggestion}")

    question = st.text_area(
        "Ask a production engineering question about this material pairing:",
        placeholder=suggestion,
        height=100,
    )

    if st.button("Ask Claude", type="primary"):
        if not api_key:
            st.error("Please enter your Anthropic API Key in the sidebar.")
        elif not question.strip():
            st.warning("Please enter a question.")
        else:
            with st.spinner("Consulting Claude Opus 4.6..."):
                try:
                    answer = consult_claude(api_key, mat_a_s, mat_b_s, score, question.strip())
                    st.markdown(
                        f'<div class="claude-box">{answer}</div>',
                        unsafe_allow_html=True,
                    )
                except anthropic.AuthenticationError:
                    st.error("Invalid API key. Please check and re-enter.")
                except anthropic.RateLimitError:
                    st.error("Rate limit reached. Please wait and retry.")
                except Exception as exc:
                    st.error(f"API error: {exc}")
