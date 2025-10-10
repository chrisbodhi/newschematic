const {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ReferenceDot,
} = Recharts;

const SkyhookVisualization = () => {
  const v_e = 3.5;

  const generateData = () => {
    const data = [];
    for (let deltaV = 0; deltaV <= 12; deltaV += 0.1) {
      const massRatio = Math.exp(deltaV / v_e);
      data.push({
        deltaV: deltaV,
        massRatio: massRatio,
      });
    }
    return data;
  };

  const data = generateData();

  const skyhookIntercept = {
    deltaV: 5.27,
    massRatio: Math.exp(5.27 / v_e),
    label: "Skyhook Intercept",
  };

  const directToOrbit = {
    deltaV: 7.8,
    massRatio: Math.exp(7.8 / v_e),
    label: "Direct to Orbit",
  };

  const skyhookRelease = {
    deltaV: 10.07,
    massRatio: Math.exp(10.07 / v_e),
    label: "Skyhook Release",
  };

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      return (
        <div
          style={{
            backgroundColor: "white",
            padding: "10px",
            border: "1px solid #ccc",
            borderRadius: "4px",
          }}
        >
          <p style={{ margin: 0 }}>
            <strong>Δv:</strong> {payload[0].payload.deltaV.toFixed(2)} km/s
          </p>
          <p style={{ margin: 0 }}>
            <strong>Mass Ratio:</strong> {payload[0].value.toFixed(2)}
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <div style={{ padding: "20px", fontFamily: "Arial, sans-serif" }}>
      <h2 style={{ textAlign: "center", marginBottom: "10px" }}>
        The Tyranny of the Rocket Equation
      </h2>
      <h3
        style={{
          textAlign: "center",
          color: "#666",
          fontWeight: "normal",
          marginTop: "0",
        }}
      >
        How Skyhooks Reduce Delta-v Requirements
      </h3>

      <div
        style={{
          display: "flex",
          justifyContent: "center",
          marginTop: "20px",
        }}
      >
        <LineChart
          width={800}
          height={500}
          data={data}
          margin={{ top: 20, right: 30, left: 60, bottom: 60 }}
        >
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis
            dataKey="deltaV"
            type="number"
            domain={[0, 12]}
            label={{
              value: "Delta-v Required (km/s)",
              position: "bottom",
              offset: 40,
            }}
          />
          <YAxis
            label={{
              value: "Mass Ratio (m₀/mf)",
              angle: -90,
              position: "left",
              offset: 40,
            }}
            domain={[0, 25]}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend
            verticalAlign="top"
            height={36}
            wrapperStyle={{ paddingBottom: "20px" }}
          />
          <Line
            type="monotone"
            dataKey="massRatio"
            stroke="#2563eb"
            strokeWidth={3}
            dot={false}
            name="Mass Ratio (vₑ = 3.5 km/s)"
          />

          <ReferenceDot
            x={skyhookIntercept.deltaV}
            y={skyhookIntercept.massRatio}
            r={8}
            fill="#10b981"
            stroke="#059669"
            strokeWidth={2}
          />

          <ReferenceDot
            x={directToOrbit.deltaV}
            y={directToOrbit.massRatio}
            r={8}
            fill="#ef4444"
            stroke="#dc2626"
            strokeWidth={2}
          />

          <ReferenceDot
            x={skyhookRelease.deltaV}
            y={skyhookRelease.massRatio}
            r={6}
            fill="#8b5cf6"
            stroke="#7c3aed"
            strokeWidth={2}
          />
        </LineChart>
      </div>

      <div
        style={{
          marginTop: "30px",
          maxWidth: "800px",
          margin: "30px auto",
        }}
      >
        <h3>Key Points:</h3>
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "1fr 1fr 1fr",
            gap: "20px",
          }}
        >
          <div
            style={{
              padding: "15px",
              backgroundColor: "#d1fae5",
              borderRadius: "8px",
              border: "2px solid #10b981",
            }}
          >
            <div
              style={{
                display: "flex",
                alignItems: "center",
                marginBottom: "8px",
              }}
            >
              <div
                style={{
                  width: "12px",
                  height: "12px",
                  backgroundColor: "#10b981",
                  borderRadius: "50%",
                  marginRight: "8px",
                }}
              ></div>
              <strong>Skyhook Intercept</strong>
            </div>
            <p style={{ margin: "4px 0" }}>
              Δv: {skyhookIntercept.deltaV} km/s
            </p>
            <p style={{ margin: "4px 0" }}>Altitude: 200 km</p>
            <p style={{ margin: "4px 0" }}>
              Mass Ratio: {skyhookIntercept.massRatio.toFixed(2)}
            </p>
          </div>

          <div
            style={{
              padding: "15px",
              backgroundColor: "#fee2e2",
              borderRadius: "8px",
              border: "2px solid #ef4444",
            }}
          >
            <div
              style={{
                display: "flex",
                alignItems: "center",
                marginBottom: "8px",
              }}
            >
              <div
                style={{
                  width: "12px",
                  height: "12px",
                  backgroundColor: "#ef4444",
                  borderRadius: "50%",
                  marginRight: "8px",
                }}
              ></div>
              <strong>Direct to Orbit</strong>
            </div>
            <p style={{ margin: "4px 0" }}>Δv: {directToOrbit.deltaV} km/s</p>
            <p style={{ margin: "4px 0" }}>Altitude: ~400 km</p>
            <p style={{ margin: "4px 0" }}>
              Mass Ratio: {directToOrbit.massRatio.toFixed(2)}
            </p>
          </div>

          <div
            style={{
              padding: "15px",
              backgroundColor: "#ede9fe",
              borderRadius: "8px",
              border: "2px solid #8b5cf6",
            }}
          >
            <div
              style={{
                display: "flex",
                alignItems: "center",
                marginBottom: "8px",
              }}
            >
              <div
                style={{
                  width: "12px",
                  height: "12px",
                  backgroundColor: "#8b5cf6",
                  borderRadius: "50%",
                  marginRight: "8px",
                }}
              ></div>
              <strong>Skyhook Release</strong>
            </div>
            <p style={{ margin: "4px 0" }}>Δv: {skyhookRelease.deltaV} km/s</p>
            <p style={{ margin: "4px 0" }}>Altitude: 600 km</p>
            <p style={{ margin: "4px 0" }}>
              Mass Ratio: {skyhookRelease.massRatio.toFixed(2)}
            </p>
          </div>
        </div>

        <div
          style={{
            marginTop: "20px",
            padding: "15px",
            backgroundColor: "#f3f4f6",
            borderRadius: "8px",
          }}
        >
          <p style={{ margin: "0" }}>
            <strong>The Skyhook Advantage:</strong> By catching a spacecraft at
            the lower tip (5.27 km/s instead of 7.8 km/s), the required mass
            ratio drops from {directToOrbit.massRatio.toFixed(2)} to{" "}
            {skyhookIntercept.massRatio.toFixed(2)} — that's{" "}
            <strong>
              {(
                (1 - skyhookIntercept.massRatio / directToOrbit.massRatio) *
                100
              ).toFixed(0)}
              % less mass needed!
            </strong>
          </p>
        </div>
      </div>
    </div>
  );
};

const root = ReactDOM.createRoot(document.getElementById("skyhook-root"));
root.render(<SkyhookVisualization />);
