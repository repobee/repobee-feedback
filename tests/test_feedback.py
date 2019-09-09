from _repobee import plugin

from repobee_feedback import feedback


def test_register():
    """Just test that there is no crash"""
    plugin.register_plugins([feedback])
