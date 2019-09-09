"""An extension command for RepoBee that looks for files called issue.md in
student repos and opens them as issues on the issue tracker.

.. module:: feedback
    :synopsis: A RepoBee plugin that finds issue files in student repos and opens them on their issue trackers

.. moduleauthor:: Simon Larsén
"""

import pathlib
import os
import sys
import argparse
from typing import Union, Iterable, Tuple

import daiquiri
import repobee_plug as plug

PLUGIN_NAME = "feedback"

LOGGER = daiquiri.getLogger(__file__)


def callback(args: argparse.Namespace, api: plug.API) -> None:
    repo_names = plug.generate_repo_names(args.students, args.master_repo_names)
    issues = _collect_issues(repo_names, args.issue_pattern)
    for repo_name, issue in issues:
        open_issue = args.batch_mode or _ask_for_open(issue, repo_name)
        if open_issue:
            api.open_issue(issue.title, issue.body, [repo_name])
        else:
            LOGGER.info("Skipping {}".format(repo_name))


class FeedbackCommand(plug.Plugin):
    def create_extension_command(self):
        parser = plug.ExtensionParser()
        parser.add_argument(
            "-b",
            "--batch-mode",
            help="Run without any yes/no promts.",
            action="store_true",
        )
        parser.add_argument(
            "-i",
            "--issue-pattern",
            help=(
                "The pattern used to find issue files. Should be a bash "
                "pattern (i.e. not regex). Default is 'issue.md'."
            ),
            type=str,
            default="issue.md",
        )
        return plug.ExtensionCommand(
            parser=parser,
            name="issue-feedback",
            help="Open issue files (issue.md) found in student repos as issues.",
            description=(
                "Search through local student repos for issue.md files, "
                "that are then opened as issues on the issue trackers of the "
                "respective repos."
            ),
            callback=callback,
            requires_api=True,
            requires_base_parsers=[
                plug.BaseParser.REPO_NAMES,
                plug.BaseParser.STUDENTS,
            ],
        )


def _ask_for_open(issue: plug.Issue, repo_name: str) -> bool:
    trunc_len = 50
    LOGGER.info(
        'Processing issue "{}" for {}: {}{}'.format(
            issue.title,
            repo_name,
            issue.body[:trunc_len],
            "[...]" if len(issue.body) > trunc_len else "",
        )
    )
    return (
        input('Open issue "{}" in repo {}? (y/n) '.format(issue.title, repo_name)) == "y"
    )


def _collect_issues(
    repo_names: Iterable[str], issue_pattern: str
) -> Iterable[Tuple[str, plug.Issue]]:
    issues = []
    local_repos = [
        dir
        for dir in pathlib.Path(".").resolve().glob("*")
        if dir.name in repo_names and dir.is_dir()
    ]
    for repo in local_repos:
        issues.append((repo.name, _find_issue(repo, issue_pattern)))

    missing_repos = set(repo_names) - set([r.name for r in local_repos])
    if missing_repos:
        LOGGER.warning("Could not find repos: {}".format(", ".join(missing_repos)))

    return issues


def _find_issue(repo: pathlib.Path, issue_pattern: str):
    matches = list(repo.rglob(issue_pattern))
    if len(matches) != 1:
        raise plug.PlugError(
            "Expected to find 1 match for pattern {} in {}"
            ", but found {}: {}".format(
                issue_pattern, repo.name, len(matches), list(map(str, matches))
            )
        )
    issue_file = matches[0]
    LOGGER.info("Found issue file at {}".format(issue_file))
    return _read_issue(issue_file)


def _read_issue(issue_path: pathlib.Path) -> plug.Issue:
    with open(str(issue_path), "r", encoding=sys.getdefaultencoding()) as file:
        return plug.Issue(file.readline().strip(), file.read())
