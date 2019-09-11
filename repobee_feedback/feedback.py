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
    issues_dir = pathlib.Path(args.issues_dir).resolve()
    issues = _collect_issues(repo_names, issues_dir)
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
            "--id",
            "--issues-dir",
            help=(
                "Directory containing issue files. The files should be "
                "named <STUDENT_REPO_NAME>.md (for example, "
                "slarse-task-1.md). The first line is assumed to be the "
                "title, and the rest the body. Defaults to the current "
                "directory."
            ),
            dest="issues_dir",
            type=str,
            default=".",
        )
        return plug.ExtensionCommand(
            parser=parser,
            name="issue-feedback",
            help="Open issues in student repos based on local issue files.",
            description="Open issues in student repos based on local issue files.",
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
        input('Open issue "{}" in repo {}? (y/n) '.format(issue.title, repo_name))
        == "y"
    )


def _collect_issues(
    repo_names: Iterable[str], issues_dir: pathlib.Path
) -> Iterable[Tuple[str, plug.Issue]]:
    issues = []
    md_files = list(issues_dir.glob("*.md"))
    for repo_name in repo_names:
        expected_file = issues_dir / "{}.md".format(repo_name)
        if expected_file not in md_files:
            raise plug.PlugError("Expected to find issue file {}".format(expected_file))
        issues.append((repo_name, _read_issue(expected_file)))

    return issues


def _read_issue(issue_path: pathlib.Path) -> plug.Issue:
    with open(str(issue_path), "r", encoding=sys.getdefaultencoding()) as file:
        return plug.Issue(file.readline().strip(), file.read())
