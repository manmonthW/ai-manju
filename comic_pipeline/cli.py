import argparse
import json
from pathlib import Path

from .jobs import JobStore


def main() -> int:
    parser = argparse.ArgumentParser(prog="comic-pipeline")
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("show", "approve", "queue"):
        cmd = sub.add_parser(name)
        cmd.add_argument("ledger", type=Path)
        cmd.add_argument("job_id")
        if name == "approve":
            cmd.add_argument("preview_hash")
    args = parser.parse_args()
    store = JobStore(args.ledger)
    if args.command == "show":
        result = store.get(args.job_id)
    elif args.command == "approve":
        result = store.approve(args.job_id, args.preview_hash)
    else:
        result = store.queue(args.job_id)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
