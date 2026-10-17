#!/bin/sh
# Put the demo back to the start: original Brain, empty memory, empty ledger.
cd "$(dirname "$0")" && cp fixtures/brain.original.json brain.json && rm -f corrections.jsonl ledger.jsonl && echo "reset: Brain original, memory empty"
