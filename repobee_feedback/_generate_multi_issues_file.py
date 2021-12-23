"""An helper command for automatic generation of a file called issue.md
with issues for multiple tasks are stored together.

.. module:: _generate_multi_issue_file
    :synopsis: An helper command for automatic generation of a multi issue file, where 
    issues for multiple tasks are stored together.

"""
import pathlib
import sys
from typing import List

import repobee_plug as plug
from repobee_plug.cli.categorization import Action

MULTI_ISSUES_FILENAME = "issue.md"

GENERATE_MULTI_ISSUES_FILE_ACTION = Action(
    name="generate-multi-issues-file",
    category=plug.cli.CoreCommand.issues,
)


class GenerateMultiIssuesFile(plug.Plugin, plug.cli.Command):
    __settings__ = plug.cli.command_settings(
        help="auto generate multi-issues file",
        description="Will generate a multi-issues file template "
        "where each pair of student and assignment (args) passed "
        "will become an issue that starts with the line "
        "#ISSUE#<STUDENT_REPO_NAME>#<ISSUE_TITLE>, followed by its "
        "body. Title and body should be filled appropriately later.",
        action=GENERATE_MULTI_ISSUES_FILE_ACTION,
        base_parsers=[plug.BaseParser.ASSIGNMENTS, plug.BaseParser.STUDENTS],
    )

    def command(
        self,
    ):
        content = _generate_multi_issues_file_content(
            self.args.students, self.args.assignments
        )

        pathlib.Path(MULTI_ISSUES_FILENAME).write_text(
            "\n\n".join(content),
            encoding=sys.getdefaultencoding(),
        )

    plug.echo(f"Created multi-issue file '{MULTI_ISSUES_FILENAME}'")


def _generate_multi_issues_file_content(
    students: List[str], assignments: List[str]
):

    issue_headers = [
        f"#ISSUE#{repo_name}#<ISSUE-TITLE>\n<ISSUE-BODY>"
        for repo_name in plug.generate_repo_names(students, assignments)
    ]

    return issue_headers
