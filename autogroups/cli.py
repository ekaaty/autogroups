import argparse
import logging
import sys
from .engine import AutogroupsEngine

def setup_logging(verbose=False):
    """Configures the logging level based on the verbose flag."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def main():
    """Main entry point for the Autogroups CLI."""
    parser = argparse.ArgumentParser(
        description="Autogroups: A declarative system group synchronization engine."
    )

    # Core commands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # 'sync' command
    sync_parser = subparsers.add_parser("sync", help="Synchronize system groups with YAML policies")
    sync_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be changed without applying any modifications"
    )
    sync_parser.add_argument(
        "--config-dir",
        default="/etc/autogroups/groups.d/",
        help="Path to the directory containing YAML policy files"
    )

    # Global options
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable debug logging")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    setup_logging(args.verbose)

    # Initialize the engine
    try:
        engine = AutogroupsEngine(config_dir=args.config_dir)

        if args.command == "sync":
            if args.dry_run:
                logging.info("--- DRY RUN MODE: No changes will be applied ---")
                # We'll need to pass the dry_run flag to the engine
                engine.sync(dry_run=True)
            else:
                engine.sync(dry_run=False)

    except Exception as e:
        logging.error(f"Execution failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
