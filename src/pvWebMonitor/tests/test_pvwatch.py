from .. import pvwatch
from .. import read_config
import pathlib
import pytest


PROJECT_PATH = pathlib.Path(__file__).parent.parent / "project"
CONFIG_FILE = PROJECT_PATH / "config.xml"


@pytest.mark.parametrize(
    "mne, pv, desc, fmt, as_string",
    [
        ["m1_setpoint", "gp:m1.VAL", "motor1 target", "%s", False],
        ["m1", "gp:m1.RBV", "motor1 value", "%s", False],
    ]
)
def test_connect_pv(mne, pv, desc, fmt, as_string):
    configuration = read_config.read_xml(CONFIG_FILE)
    watcher = pvwatch.PvWatch(configuration)
    watcher.add_pv(mne, pv, desc, fmt, as_string)
    assert pv in watcher.pvdb


def test_pvwatch():
    configuration = read_config.read_xml(CONFIG_FILE)
    assert isinstance(configuration, dict)

    watcher = pvwatch.PvWatch(configuration)
    assert watcher is not None

    # watcher.start()  # while True loop!
    # watcher.report()
