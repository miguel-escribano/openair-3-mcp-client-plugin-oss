# Plot catalog — what to ask for

**Goal:** Pick the right MCP tool for an openair chart.

Always chain: **ingest → `prepare_series_for_openair` → one plot tool** (except wind/polar — see below).

## Time series and overview

| You want… | MCP tool | Notes |
|-----------|----------|-------|
| Trend over time | `time_plot` | One or many pollutants |
| First look + data capture % | `summary_plot` | Multi-panel summary; ggplot2 fallback if `summaryPlot` missing |
| Calendar / daily heat map | `calendar_plot` | One pollutant |
| Diurnal / weekday / monthly | `time_variation` | Auto-normalises multi-pollutant scales |
| Hour vs month heat map | `trend_level` | Two time dimensions |
| Long-term GAM trend | `smooth_trend` | Confidence bands |
| Theil–Sen trend | `theil_sen` | Non-parametric slope |
| Resample then plot | `time_average` → `time_plot` | Returns SeriesV1 |

## Relationships

| You want… | MCP tool | Notes |
|-----------|----------|-------|
| X vs Y scatter | `scatter_plot` | ≥2 series; first = x, second = y |
| Correlation matrix | `cor_plot` | ≥2 pollutants |
| Distribution (histogram / density) | `dist_plot` | `plot_options.theme` / `dist_method` (openair 3.2) |
| Summary numbers | `aq_stats` | Mean, percentiles, capture % |
| Model vs obs stats | `mod_stats` | ≥2 series; first = model, second = observed |
| Predicted vs observed quantiles | `conditional_quantile` | Model evaluation plot |
| Taylor diagram | `taylor_diagram` | Obs + multiple models |

## Wind and polar (WindSeriesV1)

**Do not** call `prepare_series_for_openair` first. Data must include `ws` and `wd`.

| You want… | MCP tool | Notes |
|-----------|----------|-------|
| Wind rose | `wind_rose` | Frequency by direction/speed |
| Pollution rose | `pollution_rose` | Concentration by wind |
| Percentile rose | `percentile_rose` | Percentiles by direction |
| Source identification | `polar_plot` | Kernel-smoothed bivariate polar |
| Polar frequency | `polar_freq` | Wind frequency + optional pollutant |
| Third variable (season, hour) | `polar_annulus` | Annulus plot |
| Two periods compared | `polar_diff` | Same pollutant, two date ranges |
| Cluster signatures | `polar_cluster` | Slow; K-means |

State wind data source before presenting polar/wind plots (guardrail O5).

## Trajectory (TrajSeriesV1)

After `import_traj`: `traj_plot`, `traj_level`, `traj_cluster`.

## Example prompts

**Overview before deep dive**
```
Load [path or import], prepare hourly [timezone].
Run summary_plot, then calendar_plot for PM10.
```

**Model evaluation**
```
Load model and observation CSV with aligned timestamps.
Prepare hourly. mod_stats (model first, obs second), then scatter_plot.
```

**Full Felisa smoke (plugin fixture)**
See [vscode-chat-felisa.md](vscode-chat-felisa.md).

## References

- [prepare-plot skill](../skills/prepare-plot/SKILL.md)
- [openair book](https://openair-project.github.io/book/)
- Server tool list: [openair-3-mcp-server-oss README](https://github.com/miguel-escribano/openair-3-mcp-server-oss#available-tools)
