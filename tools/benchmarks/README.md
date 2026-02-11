# Benchmarks

This directory contains performance and load benchmarking tools used to evaluate system behavior under realistic and stress conditions.

These benchmarks are engineering tools designed to measure performance characteristics, not to simulate production traffic directly.

Purpose

Benchmarking helps us:

Measure system performance under controlled scenarios

Identify bottlenecks in ingestion, search, API, or AI layers

Track performance regressions over time

Validate scaling assumptions before production changes

Support capacity planning and cost control decisions

Benchmarks should be repeatable, isolated, and measurable.

What We Benchmark

Typical benchmark targets include:

Area	Examples
API	Request latency, throughput, rate-limit behavior
Search	Index build time, query latency, reranking cost
Pipelines	Ingestion speed, backfill duration
AI Layers	Inference latency, token usage, batching performance
Database	Query latency, write throughput, index performance
Principles
Controlled Environment

Benchmarks should run in a predictable environment:

Fixed dataset sizes

Known configuration

Stable infrastructure

Reproducibility

Each benchmark should document:

Dataset used

Hardware or environment assumptions

Configuration parameters

Isolation

Benchmarks must avoid interfering with:

production systems

shared staging environments

other engineers’ workflows

Whenever possible, use local or dedicated environments.

Output Expectations

Benchmark runs should produce:

Latency metrics (avg, p95, p99 where relevant)

Throughput (requests/sec, items/sec, etc.)

Resource usage (CPU, memory, I/O when measurable)

Cost-related metrics when applicable (e.g. token usage)

Outputs should be:

human-readable in the console

optionally exportable as JSON or CSV for analysis

Running Benchmarks

Benchmarks are typically executed via scripts, for example:

pnpm benchmarks:<name>


or through a CLI entrypoint:

node tools/benchmarks/<script>.ts


Each benchmark script must document:

required environment variables

expected runtime

dataset prerequisites

When to Add a Benchmark

Add a benchmark when:

A new subsystem is performance-sensitive

A major architectural change is introduced

A known bottleneck needs measurement

Capacity planning requires real data

Benchmarks should evolve alongside the system and remain aligned with real-world usage patterns.

Not a Load Testing Platform

These benchmarks are engineering performance tools, not full-scale production load testing.
Dedicated load testing (with traffic simulation and distributed load) should live in a separate, purpose-built setup if needed.

Well-designed benchmarks give us confidence to scale — without flying blind.