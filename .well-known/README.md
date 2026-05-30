# Agent Card

This directory contains the [A2A Agent Card](https://github.com/google/A2A) for EFC.

The `agent.json` file describes EFC's capabilities in a machine-readable format so that A2A-compatible agents can discover and use EFC's fact-checking tools programmatically.

## What is A2A?

[Agent-to-Agent (A2A)](https://github.com/google/A2A) is an open protocol by Google for agent interoperability. Agents publish an Agent Card at `/.well-known/agent.json` describing their skills, interfaces, and protocols — other agents can then discover and invoke them.

## EFC's Agent Card

EFC exposes 5 skills:

| Skill | Description |
|---|---|
| `fact-check` | Full structured fact-check of a research report |
| `extract-claims` | Inventory verifiable claims with priority triage |
| `check-links` | Verify source URL resolution |
| `verify-sources` | Fetch cited pages and verify claimed content appears |
| `audit` | End-to-end audit with reliability verdict |

And 3 interface types:

| Interface | Install |
|---|---|
| CLI (`efc`) | `pip install everything-fact-checked` |
| SKILL.md (any agent) | [EFC-standalone](https://github.com/Nlai741533/EFC-standalone) |
| GitHub Action | `uses: Nlai741533/EFC-Plugin@v0.2.2` |

## Usage

A2A agents can discover EFC by fetching:
```
https://raw.githubusercontent.com/Nlai741533/EFC-Plugin/main/.well-known/agent.json
```
