# Contributing

Keep the rewind core offline and standard-library-only. New classifiers should be explainable and should preserve the reason/confidence metadata. Never add a credential, Takeout export, OAuth token, or personal generated output to a commit.

Run the sample and tests before opening a change:

```bash
python3 src/main.py --history examples/watch-history-sample.json --likes examples/likes-sample.json --comments examples/comments-sample.json --years 10 --out outputs/
python3 -m pytest tests/ -q
```

Optional API changes must remain isolated from the core CLI and must default to read-only or dry-run behavior.
