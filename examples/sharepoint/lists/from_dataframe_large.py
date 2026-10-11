"""Stream a large CSV into a SharePoint list — memory-bounded, resumable, idempotent.

The chunk iterator goes to ``List.from_dataframe``: the typed columns are
provisioned once, each chunk is flushed through server-side OData batches
(``--concurrency`` parallel, per-sub-request retries honoring ``Retry-After``),
and queued items are discarded after every chunk — so memory stays flat no matter
the file size.

**Idempotent** — ``key=["Name", "date"]`` hashes the natural key into a
``MigrationKey`` column (created automatically), so a re-run skips rows that are
already present — on a fresh run **and** when resuming. **Resumable** — the
committed cursor is checkpointed after each chunk, so an interrupted run
continues where it stopped; changing ``--chunk`` invalidates the checkpoint and
triggers a full re-scan (the key keeps it duplicate-free). Use
``--reset-checkpoint`` to start over — the checkpoint is also ignored
automatically when the target list is empty (a deleted/recreated list).

    python from_dataframe_large.py --rows 40000 --concurrency 5

A live progress bar is shown by default (``--no-progress`` disables it; tqdm is
used when installed, otherwise a plain per-second counter).

Requires: pip install office365-rest-python-client[pandas]
"""

from __future__ import annotations

import argparse
import tempfile
import time
from pathlib import Path

from office365.runtime.operations import Progress
from office365.sharepoint.client_context import ClientContext
from tests.settings import client_id, password, team_site_url, tenant, username

CSV_URL = "https://raw.githubusercontent.com/plotly/datasets/master/all_stocks_5yr.csv"


def _is_empty(lst) -> bool:
    """Whether the target list has no items (a fresh or recreated list)."""
    lst.ensure_property("ItemCount").execute_query()
    return (lst.item_count or 0) == 0


class _Progress:
    """Live progress reporter: a tqdm bar, or a plain throttled counter."""

    def __init__(self, total: int | None, initial: int) -> None:
        self._bar = None
        self._last = 0.0
        try:
            from tqdm import tqdm
        except ImportError:
            return
        self._bar = tqdm(
            total=total,
            initial=initial,
            unit="row",
            unit_scale=True,
            desc="Importing",
            dynamic_ncols=True,
        )

    def __call__(self, p: Progress) -> None:
        if self._bar is not None:
            self._bar.update(p.done - self._bar.n)
            return
        now = time.monotonic()
        if now - self._last < 1.0 and (not p.total or p.done < p.total):
            return
        self._last = now
        pct = f" ({p.percent:.0f}%)" if p.total else ""
        print(f"  {p.done:,} rows{pct}", flush=True)

    def close(self) -> None:
        if self._bar is not None:
            self._bar.close()
        else:
            print(flush=True)


def main():
    import pandas as pd  # type: ignore[import-not-found]

    p = argparse.ArgumentParser(description="Stream a large CSV into a SharePoint list")
    p.add_argument("--list-title", default="Stocks_5yr_Large")
    p.add_argument("--rows", type=int, default=40000, help="rows to import (0 = all)")
    p.add_argument("--chunk", type=int, default=2000, help="rows per memory slice")
    p.add_argument("--concurrency", type=int, default=5, help="parallel batch requests")
    p.add_argument(
        "--checkpoint", default=str(Path(tempfile.gettempdir()) / "stocks.checkpoint.json"), help="'' disables resume"
    )
    p.add_argument("--reset-checkpoint", action="store_true", help="delete the checkpoint and start fresh")
    p.add_argument("--no-progress", action="store_true", help="disable the live progress bar")
    args = p.parse_args()

    ckpt_path = Path(args.checkpoint) if args.checkpoint else None
    if ckpt_path is not None and args.reset_checkpoint:
        ckpt_path.unlink(missing_ok=True)

    ctx = ClientContext(team_site_url).with_username_and_password(
        tenant=tenant, client_id=client_id, username=username, password=password
    )
    lst = ctx.web.lists.ensure_list(args.list_title).execute_query()

    # A checkpoint only makes sense while its target still holds the committed
    # rows. If the list is empty (e.g. it was deleted and recreated), the cursor
    # is stale — ignore it and start from scratch.
    if ckpt_path is not None and ckpt_path.exists() and _is_empty(lst):
        print(f"Target list is empty; ignoring the stale checkpoint ({args.checkpoint})")
        ckpt_path.unlink()

    chunks = pd.read_csv(CSV_URL, chunksize=args.chunk, nrows=args.rows or None)

    resumed = 0
    if args.checkpoint:
        from office365.runtime.imports import FileCheckpointStore

        resumed = FileCheckpointStore(args.checkpoint).load().cursor
    if resumed and args.rows and resumed >= args.rows:
        print(
            f"Nothing to do: checkpoint is already at {resumed:,}/{args.rows:,} rows (use --reset-checkpoint to re-scan)"
        )
    reporter = None if args.no_progress else _Progress(args.rows or None, resumed)

    driver = lst.from_dataframe(
        chunks,
        checkpoint=args.checkpoint or None,
        key=["Name", "date"],
        progress=reporter,
        total=args.rows or None,
    )
    if driver.resumed_from:
        print(f"Resuming from {driver.resumed_from:,} committed row(s)")

    try:
        stats = driver.execute_batch(concurrency=args.concurrency).value
    except KeyboardInterrupt:
        if reporter is not None:
            reporter.close()
        print(f"Interrupted at {driver.checkpoint.cursor:,} row(s) — re-run to resume")
        raise SystemExit(130) from None
    if reporter is not None:
        reporter.close()

    print(f"{stats.summary()} into '{lst.title}'")


if __name__ == "__main__":
    main()
