{
  metric_name: 'pageserver_send_flushes_total',
  type: 'counter',
  help: 'Number of flushes to the pageserver connection',
  values: [
    'pageserver_send_flushes_total',
  ],
  query_ref: 'serendb_perf_counters',
}
