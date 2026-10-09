# Round 47 native runtime workloads

The Round 46 runtime A/B harness is reused in `tools/r47_runtime_benchmark.py`;
only its workload list and generated-disassembly hotspot window are modified.
No additional compiler or runtime implementation.

- `r47_pankti_reads.sm`: 12M fixed-array checked reads
- `r47_kosh_reads.sm`: 10M growable-array checked reads
- `r47_array_mix.sm`: 5M compound indexed reads
- `r46_hotcall_array.sm`: existing call + array workload
- `examples/126_numeric_pipeline.sm`: existing realistic numerical pipeline

The runner compares output and exit exactly for before vs after and records
CPU pinned process runtimes with interleaved order, 40 measured pairs and six
discarded warm-ups. Python is test harness only, not the Sutram compiler.

Native original golden suite is never regenerated.
