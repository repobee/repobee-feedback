import pathlib
import sys

import pytest

import repobee
from repobee_feedback import feedback


class TestGenerateMultiIssueFile:
    """Tests generation of a multi-issues file"""

    def test_creates_non_empty_output_file(tmpdir):
        students = "alice bob".split()
        assignments = "task-1 task-2"
        command = [
            *feedback.GENERATE_MULTI_ISSUES_FILE_ACTION.as_name_tuple(),
            "--students",
            students,
            "--assignments",
            assignments,
        ]

        repobee.run(
            command,
            plugins=[feedback.GenerateMultiIssuesFile],
            workdir=tmpdir,
        )

        outfile = pathlib.Path(tmpdir) / feedback.MULTI_ISSUES_FILENAME
        assert outfile.is_file()
        assert len(outfile.read_text(encoding=sys.getdefaultencoding())) > 0
