import React, { useState, useEffect, useRef, Component } from 'react';
import * as ReactPlotlyFactory from 'react-plotly.js/factory';
import * as PlotlyDist from 'plotly.js-dist-min';
import { motion, useScroll, useTransform } from 'framer-motion';
import { ArrowRight, Activity, Zap, Shield, Database, TrendingUp, Globe, Leaf } from 'lucide-react';
import './index.css';

// CJS modules may export via .default when bundled by Vite
const createPlotlyComponent = ReactPlotlyFactory.default ?? ReactPlotlyFactory;
const Plotly = PlotlyDist.default ?? PlotlyDist;
const Plot = createPlotlyComponent(Plotly);

// ── Error Boundary — isolates chart crashes from the rest of the page ────────
class ErrorBoundary extends Component {
  constructor(props) { super(props); this.state = { hasError: false }; }
  static getDerivedStateFromError() { return { hasError: true }; }
  render() {
    if (this.state.hasError)
      return <div className="chart-error">⚠ Chart failed to render</div>;
    return this.props.children;
  }
}

// ── Animated counter ──────────────────────────────────────────────────────────
function Counter({ value, suffix = '', decimals = 0, duration = 1800 }) {
  const [display, setDisplay] = useState(0);
  const startRef = useRef(null);
  useEffect(() => {
    if (value == null) return;
    startRef.current = performance.now();
    const animate = (now) => {
      const elapsed = now - startRef.current;
      const progress = Math.min(elapsed / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      setDisplay(+(value * eased).toFixed(decimals));
      if (progress < 1) requestAnimationFrame(animate);
    };
    requestAnimationFrame(animate);
  }, [value, decimals, duration]);
  return <>{display.toLocaleString(undefined, { minimumFractionDigits: decimals, maximumFractionDigits: decimals })}{suffix}</>;
}

// ── Stat card ─────────────────────────────────────────────────────────────────
function StatCard({ label, value, suffix = '', delta, decimals = 1, icon: Icon }) {
  return (
    <motion.div
      className="stat-card"
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.5 }}
    >
      {Icon && <Icon size={20} color="#52525b" style={{ marginBottom: '0.75rem' }} />}
      <div className="stat-label">{label}</div>
      <div className="stat-value">
        {value != null ? <Counter value={value} suffix={suffix} decimals={decimals} /> : '—'}
      </div>
      {delta != null && (
        <div className="stat-delta" style={{ color: delta > 0 ? '#10b981' : '#f43f5e' }}>
          {delta > 0 ? '▲' : '▼'} {Math.abs(delta).toFixed(1)}
        </div>
      )}
    </motion.div>
  );
}

// ── Chart wrapper ─────────────────────────────────────────────────────────────
function ChartCard({ title, plotData, plotLayout, height = 380 }) {
  if (!plotData || !Array.isArray(plotData)) return null;
  return (
    <motion.div
      className="chart-container"
      initial={{ opacity: 0 }}
      whileInView={{ opacity: 1 }}
      viewport={{ once: true }}
      transition={{ duration: 0.7 }}
    >
      {title && (
        <h3 style={{ marginBottom: '1rem', fontSize: '0.95rem', color: '#e4e4e7', fontFamily: "'Outfit', sans-serif", fontWeight: 600 }}>
          {title}
        </h3>
      )}
      <ErrorBoundary>
        <Plot
          data={plotData}
          layout={{
            ...plotLayout,
            autosize: true,
            paper_bgcolor: 'transparent',
            plot_bgcolor: 'transparent',
            font: { ...(plotLayout?.font ?? {}), color: '#a1a1aa' },
          }}
          config={{ displayModeBar: false, responsive: true }}
          useResizeHandler
          style={{ width: '100%', height: `${height}px` }}
        />
      </ErrorBoundary>
    </motion.div>
  );
}

// ── Main App ──────────────────────────────────────────────────────────────────
export default function App() {
  const [data, setData]       = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError]     = useState(null);

  const { scrollYProgress } = useScroll();
  // Hero fades only after 25% scroll — gives time for content to appear
  const heroOpacity = useTransform(scrollYProgress, [0, 0.25], [1, 0]);
  const heroY       = useTransform(scrollYProgress, [0, 0.25], [0, -80]);

  useEffect(() => {
    fetch('http://localhost:8000/api/dashboard')
      .then((r) => { if (!r.ok) throw new Error(r.statusText); return r.json(); })
      .then((d) => { setData(d); setLoading(false); })
      .catch((e) => { setError(e.message); setLoading(false); });
  }, []);

  const m     = data?.metrics   ?? {};
  const af    = data?.af_stats  ?? {};
  const plots = data?.plots     ?? {};

  return (
    <ErrorBoundary>
      {/* ── Navbar ── */}
      <nav className="navbar">
        <div className="nav-brand">EnergyDignity</div>
        <div className="nav-links">
          <a href="#overview"  className="nav-link">Overview</a>
          <a href="#dashboard" className="nav-link">Dashboard</a>
          <a href="#analysis"  className="nav-link">Analysis</a>
          <a href="#policies"  className="nav-link">Policy</a>
        </div>
        <div className="live-badge">
          <span className="live-dot" />
          LIVE
        </div>
      </nav>

      {/* ── Hero ── */}
      <section className="section hero">
        <motion.div style={{ opacity: heroOpacity, y: heroY }} className="hero-inner">
          <motion.p
            className="hero-eyebrow"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7 }}
          >
            India's premier energy analytics platform
          </motion.p>
          <motion.h1
            className="hero-title"
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.9, delay: 0.1 }}
          >
            Energy Dignity<br />for Everyone.
          </motion.h1>
          <motion.p
            className="hero-subtitle"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.3 }}
          >
            The Alkire-Foster Capability Approach, applied in real-time across 30 states to measure, model, and advance energy dignity.
          </motion.p>
          <motion.div
            style={{ display: 'flex', gap: '1rem', justifyContent: 'center', flexWrap: 'wrap' }}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.5 }}
          >
            <button
              className="btn-primary"
              onClick={() => document.getElementById('dashboard')?.scrollIntoView({ behavior: 'smooth' })}
            >
              Explore Dashboard
              <ArrowRight size={16} />
            </button>
            <button
              className="btn-ghost"
              onClick={() => document.getElementById('analysis')?.scrollIntoView({ behavior: 'smooth' })}
            >
              View Analysis
            </button>
          </motion.div>
        </motion.div>

        <div className="hero-orb hero-orb--1" />
        <div className="hero-orb hero-orb--2" />
      </section>

      {/* ── Features ── */}
      <section className="section" id="overview">
        <motion.p className="section-eyebrow" initial={{ opacity: 0 }} whileInView={{ opacity: 1 }} viewport={{ once: true }}>
          Core Capabilities
        </motion.p>
        <motion.h2 className="section-title" initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }}>
          Built for rigorous<br />energy intelligence.
        </motion.h2>
        <div className="features-grid">
          {[
            { icon: Activity,   title: 'Real-Time Analytics',      desc: 'Sub-second latency integration with POSOCO dispatch data and live grid telemetry.' },
            { icon: Database,   title: 'Alkire-Foster Model',       desc: 'Multidimensional poverty across 6 energy dimensions and 30+ state-level indicators.' },
            { icon: Shield,     title: 'Policy Tracking',           desc: 'Automated ingestion of regulatory changes mapped to vulnerability risk scores.' },
            { icon: TrendingUp, title: 'Scenario Engine',           desc: 'Bootstrap confidence intervals and projections for future EDI trajectories.' },
            { icon: Globe,      title: 'State Coverage',            desc: 'Urban and rural decomposition across all 30+ Indian states and union territories.' },
            { icon: Leaf,       title: 'Clean Energy Mix',          desc: 'Tracks solar, wind, hydro, and thermal generation for a complete energy picture.' },
          ].map(({ icon: Icon, title, desc }, i) => (
            <motion.div
              key={title}
              className="feature-card"
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.08, duration: 0.5 }}
            >
              <Icon size={28} color="#52525b" style={{ marginBottom: '1.2rem' }} />
              <h3 className="feature-title">{title}</h3>
              <p className="feature-desc">{desc}</p>
            </motion.div>
          ))}
        </div>
      </section>

      {/* ── Live Metrics Banner ── */}
      <div className="metrics-banner" id="dashboard">
        {loading ? (
          <div className="loading-state">
            <div style={{ display: 'flex', gap: '6px' }}>
              <span className="loading-dot" /><span className="loading-dot" /><span className="loading-dot" />
            </div>
            <p>Loading intelligence…</p>
          </div>
        ) : error ? (
          <div className="error-state">⚠ API unreachable — ensure the backend is running on port 8000.</div>
        ) : (
          <div className="stat-grid">
            <StatCard icon={Zap}        label="Current Demand"        value={m.current_demand_gw}                        suffix=" GW" decimals={1} />
            <StatCard icon={Leaf}       label="Renewable Share"       value={m.renewable_share}                           suffix="%"  decimals={1} delta={2.4} />
            <StatCard icon={Globe}      label="Electrification"       value={m.electrification_rate}                      suffix="%"  decimals={1} delta={0.3} />
            <StatCard icon={Activity}   label="Clean Cooking"         value={m.clean_cooking_access}                      suffix="%"  decimals={1} delta={1.8} />
            <StatCard icon={Database}   label="Poverty Headcount"     value={af.H != null ? af.H * 100 : null}            suffix="%"  decimals={1} />
            <StatCard icon={TrendingUp} label="Solar Capacity"        value={m.solar_gw}                                  suffix=" GW" decimals={1} delta={8.5} />
          </div>
        )}
      </div>

      {/* ── Charts Dashboard ── */}
      {data && (
        <section className="section dashboard-section" id="analysis">
          <motion.p className="section-eyebrow" initial={{ opacity: 0 }} whileInView={{ opacity: 1 }} viewport={{ once: true }}>
            Live Dashboard
          </motion.p>
          <motion.h2 className="section-title" initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }}>
            National EDI intelligence<br />updated continuously.
          </motion.h2>

          <div className="dashboard-row">
            <ChartCard title="EDI Trajectory 2018–2024"         plotData={plots.trend?.data}    plotLayout={plots.trend?.layout}    height={380} />
            <ChartCard title="National Dimension Radar"         plotData={plots.radar?.data}    plotLayout={plots.radar?.layout}    height={380} />
          </div>

          <div style={{ marginTop: '2rem' }}>
            <ChartCard title="Urban–Rural EDI Surface — Top 25 States" plotData={plots.surface_3d?.data} plotLayout={plots.surface_3d?.layout} height={500} />
          </div>

          <div className="dashboard-row" style={{ marginTop: '2rem' }}>
            <ChartCard title="Generation Mix"                   plotData={plots.donut?.data}    plotLayout={plots.donut?.layout}    height={380} />
            <ChartCard title="Dimension Correlation Matrix"     plotData={plots.heatmap?.data}  plotLayout={plots.heatmap?.layout}  height={380} />
          </div>

          <div style={{ marginTop: '2rem' }}>
            <ChartCard title="State EDI Rankings (Urban)"       plotData={plots.bar?.data}      plotLayout={plots.bar?.layout}      height={Math.max(460, (data.state_data?.length ?? 30) * 11)} />
          </div>
        </section>
      )}

      {/* ── Policy Feed ── */}
      {(data?.policies?.length ?? 0) > 0 && (
        <section className="section" id="policies" style={{ background: '#0a0a0c' }}>
          <motion.p className="section-eyebrow" initial={{ opacity: 0 }} whileInView={{ opacity: 1 }} viewport={{ once: true }}>
            Policy Radar
          </motion.p>
          <motion.h2 className="section-title" initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }}>
            Regulatory intelligence,<br />mapped in real time.
          </motion.h2>
          <div className="policy-grid">
            {data.policies.map((pol, i) => (
              <motion.div
                key={i}
                className={`policy-card ${pol.impact === 'positive' ? 'positive' : pol.impact === 'negative' ? 'negative' : 'neutral'}`}
                initial={{ opacity: 0, x: -20 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.05 }}
              >
                <div className="policy-date">{pol.date}</div>
                <div className="policy-title">{pol.policy}</div>
                <div className="policy-detail">{pol.details}</div>
              </motion.div>
            ))}
          </div>
        </section>
      )}

      {/* ── Footer ── */}
      <footer className="footer">
        <div className="footer-inner">
          <span className="nav-brand">EnergyDignity</span>
          <p>Data: POSOCO · MoPNG · CEA · NFHS-5 · {new Date().getFullYear()}</p>
        </div>
      </footer>
    </ErrorBoundary>
  );
}
