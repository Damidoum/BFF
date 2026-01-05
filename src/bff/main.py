import argparse
import multiprocessing
import sys
from datetime import datetime

from bff.commands.check import check_command
from bff.commands.clean import clean_command
from bff.commands.diff import diff_command
from bff.commands.index import IndexFilters, index_command
from bff.commands.init import init_command
from bff.commands.locate import locate_command
from bff.commands.reset import reset_command
from bff.commands.stats import stats_command
from bff.commands.verify import verify_command


def parse_date(date_str: str) -> float:
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return dt.timestamp()
    except ValueError:
        print("Error: Date format must be YYYY-MM-DD")
        sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(description="BFF: Box For File - Manager")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # 1. Init
    subparsers.add_parser("init", help="Initialize repository")

    # 2. Index
    idx = subparsers.add_parser("index", help="Index files")
    idx.add_argument("--ext", nargs="+", help="Whitelist extensions")
    idx.add_argument("--after", type=str, help="Date YYYY-MM-DD")
    idx.add_argument("--min-size", type=int, default=0, help="Min bytes")

    # 3. Stats (Dashboard)
    subparsers.add_parser("stats", help="Show repository statistics")

    # 4. Clean (Deduplicate)
    clean_parser = subparsers.add_parser("clean", help="Deduplicate files")
    clean_parser.add_argument("--link", "-l", action="store_true", help="Use symlinks")
    # Add filters to clean command
    clean_parser.add_argument("--ext", nargs="+", help="Only clean specific extensions")
    clean_parser.add_argument("--min-size", type=int, default=0, help="Min size bytes")

    # 5. Check (Integrity)
    chk = subparsers.add_parser("check", help="Verify index integrity")
    chk.add_argument(
        "--prune", "-p", action="store_true", help="Remove missing files from index"
    )

    # 6. Reset (Nuke)
    rst = subparsers.add_parser("reset", help="Delete database")
    rst.add_argument("--force", "-f", action="store_true", help="Skip confirmation")

    # --- LOCATE ---
    locate_parser = subparsers.add_parser("locate", help="Find external file in index")
    locate_parser.add_argument("file", help="Path to the external file")

    # --- VERIFY ---
    subparsers.add_parser("verify", help="Check file integrity against index")

    # --- DIFF ---
    diff_parser = subparsers.add_parser(
        "diff", help="Compare local index with another repository"
    )
    diff_parser.add_argument(
        "target",
        help="Path to the target BFF repository (directory) or an index.json file",
    )

    args = parser.parse_args()

    if args.command == "init":
        init_command()
    elif args.command == "index":
        ts = parse_date(args.after) if args.after else None
        filters = IndexFilters(args.ext, args.min_size, ts)
        index_command(filters)
    elif args.command == "stats":
        stats_command()
    elif args.command == "check":
        check_command(prune=args.prune)
    elif args.command == "clean":
        filters = IndexFilters(extensions=args.ext, min_size_bytes=args.min_size)
        clean_command(use_symlinks=args.link, filters=filters)
    elif args.command == "reset":
        reset_command(force=args.force)
    elif args.command == "locate":
        locate_command(args.file)
    elif args.command == "verify":
        verify_command()
    elif args.command == "diff":
        diff_command(args.target)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
