// taken from https://github.com/ozh/github-colors/blob/master/colors.json
const colorLang = {
    css: "#563d7c",
    html: "#e34c26",
    jade: "#0298c3",
    java: "#b07219",
    js: "#f1e05a",
    jsx: "#f1e05a",
    md: "#596706",
    pm: "#0298c3",
    py: "#3572a5",
    rb: "#701516",
    sass: "#1e4aec",
    scm: "#64b970",
    scss: "#1e4aec",
    sh: "#89e051",
    tmpl: "#0298c3",
    ts: "#2b7489",
    tsx: "#2b7489",
    yaml: "#cb171e",
    yml: "#cb171e"
};

const makeChart = (ctx, logs) => new Chart(ctx, {
  type: "line",
  data: {
      labels: logs.map(_log => null),
      datasets: Object.keys(colorLang).map(lang => {
          return {
              fill: false,
              label: lang,
              borderColor: colorLang[lang],
              data: logs.map(log => log.counts).map(count => count[lang]),
              pointRadius: 0,
              spanGaps: true
          }
      })
  },
  options: {
      legend: {
          display: false
      },
      scales: {
          xAxes: [{
              display: false,
              gridLines: {
                  display: false
              }
          }],
          yAxes: [{
              display: false,
              gridLines: {
                  display: false
              },
              type: "logarithmic"
          }]
      },
      tooltips: {
          enabled: false
      }
  }
});

document.addEventListener("DOMContentLoaded", () => {
  const ddwCtx = document.getElementById("ddw").getContext("2d");
  makeChart(ddwCtx, data.ddwLog);

  const volCtx = document.getElementById("vol").getContext("2d");
  makeChart(volCtx, data.volLog);

  const swCtx = document.getElementById("sw").getContext("2d");
  makeChart(swCtx, data.swLog);

  const olCtx = document.getElementById("ol").getContext("2d");
  makeChart(olCtx, data.olLog);

  const wbCtx = document.getElementById("wb").getContext("2d");
  makeChart(wbCtx, data.wbLog);

  const gsCtx = document.getElementById("gs").getContext("2d");
  makeChart(gsCtx, data.gsLog);

  const tycsCtx = document.getElementById("tycs").getContext("2d");
  makeChart(tycsCtx, data.tycsLog);

  const dpbCtx = document.getElementById("dpb").getContext("2d");
  makeChart(dpbCtx, data.dpbLog);
});
