from __future__ import annotations

from pathlib import Path

import click
from rich.console import Console

from . import __version__
from .new_problem import FileAlreadyExistsError, create_new_problem
from .validate import Severity, ValidationReport, discover_solution_files, validate_files

console = Console()


@click.group()
@click.version_option(__version__, prog_name="lc")
def main() -> None:
    """Tooling for managing leetcode practice solutions."""


@main.command("new")
@click.option("--topic", required=True, help="Topic directory (e.g. arrays).")
@click.option("--number", type=int, default=None, help="Leetcode problem number.")
@click.option("--title", required=True, help="Problem title.")
@click.option("--language", default="python", show_default=True, help="Solution language.")
@click.option("--dry-run", is_flag=True, help="Print what would be created without writing.")
def new_command(topic: str, number: int | None, title: str, language: str, dry_run: bool) -> None:
    """Create a new solution file with a placeholder metadata + reflection block."""
    repo_root = _find_repo_root()
    topic_dir = repo_root / topic
    if not topic_dir.exists():
        if not click.confirm(
            f"Topic directory '{topic}/' does not exist. Create it?", default=True
        ):
            console.print("[red]Aborted.[/red]")
            raise click.exceptions.Exit(1)
        if not dry_run:
            topic_dir.mkdir(parents=True, exist_ok=True)

    try:
        result = create_new_problem(
            repo_root=repo_root,
            topic=topic,
            title=title,
            number=number,
            language=language,
            dry_run=dry_run,
        )
    except FileAlreadyExistsError as exc:
        console.print(f"[red]File already exists:[/red] {exc}")
        raise click.exceptions.Exit(1) from exc

    rel = result.path.relative_to(repo_root)
    if dry_run:
        console.print(f"[yellow]Would create:[/yellow] {rel}")
        console.print("[dim]--- content ---[/dim]")
        console.print(result.content)
        return
    console.print(f"[green]Created[/green] {rel}")
    console.print(
        "[dim]Reminder: paste the chrome extension's clipboard over the placeholder "
        "metadata block.[/dim]"
    )


@main.command("validate")
@click.option(
    "--path",
    "target",
    type=click.Path(exists=True, path_type=Path),
    default=None,
    help="File or directory to validate. Defaults to the whole repo.",
)
@click.option("--strict", is_flag=True, help="Exit non-zero if any issues are found.")
def validate_command(target: Path | None, strict: bool) -> None:
    """Validate solution files against the metadata + reflection conventions."""
    repo_root = _find_repo_root()
    files = discover_solution_files(repo_root, target)
    report = validate_files(files, repo_root)
    _render_report(report)
    if strict and report.errors:
        raise click.exceptions.Exit(1)


def _render_report(report: ValidationReport) -> None:
    icons = {Severity.ERROR: "[red]✗[/red]", Severity.WARNING: "[yellow]![/yellow]"}
    issues_seen = False
    for file_report in report.files:
        if file_report.ok:
            continue
        issues_seen = True
        console.print(f"\n[bold]{file_report.path}[/bold]")
        for finding in file_report.findings:
            icon = icons[finding.severity]
            console.print(f"  {icon} [{finding.rule}] {finding.message}")
            console.print(f"     [dim]→ {finding.fix}[/dim]")

    if not issues_seen:
        console.print("[green]All files pass validation.[/green]")

    n_files = len(report.files)
    n_errors = len(report.errors)
    n_warnings = len(report.warnings)
    n_issues = n_errors + n_warnings
    console.print(
        f"\n[bold]{n_files}[/bold] file(s) validated · "
        f"[bold]{n_issues}[/bold] issue(s) "
        f"([red]{n_errors} error(s)[/red], [yellow]{n_warnings} warning(s)[/yellow])"
    )


def _find_repo_root() -> Path:
    cwd = Path.cwd().resolve()
    for candidate in (cwd, *cwd.parents):
        if (candidate / "pyproject.toml").exists() or (candidate / ".git").exists():
            return candidate
    return cwd


if __name__ == "__main__":
    main()
