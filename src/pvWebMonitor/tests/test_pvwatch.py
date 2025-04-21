import pathlib
import time

import epics
import pytest

from .. import pvwatch
from .. import read_config

PROJECT_PATH = pathlib.Path(__file__).parent.parent / "project"
CONFIG_FILE = PROJECT_PATH / "config.xml"


@pytest.mark.parametrize(
    "mne, pv, desc, fmt, as_string",
    [
        ["m1_setpoint", "gp:m1.VAL", "motor1 target", "%s", False],
        ["m1", "gp:m1.RBV", "motor1 value", "%s", False],
        ["tod", "gp:datetime", "date and time", "%s", True],
    ]
)
def test_PvEntry(mne, pv, desc, fmt, as_string):
    entry = pvwatch.PvEntry(mne, pv, description=desc, as_string=as_string)
    assert entry is not None
    assert str(entry) != repr(entry)

    expected = (
        f"PvEntry(pvname='{pv}'"
        f", mnemonic='{mne}'"
        f", description='{desc}'"
        f", as_string='{as_string}'"
        ")"
    )
    assert str(entry) == expected

    expected = (
        f"PvEntry(pvname='{pv}'"
        f", mnemonic='{mne}'"
        f", description='{desc}'"
        f", as_string='{as_string}'"
        f", connected='{entry.connected}'"
        ")"
    )
    assert repr(entry) == expected


@pytest.mark.parametrize(
    "mne, pv, desc, fmt, as_string, wait, min_updates",
    [
        ["m1_setpoint", "gp:m1.VAL", "motor1 target", "%s", False, 0, 0],
        ["m1", "gp:m1.RBV", "motor1 value", "%s", False, 0, 0],
        ["tod", "gp:datetime", "date and time", "%s", True, 3, 3],
    ]
)
def test_connect_pv(mne, pv, desc, fmt, as_string, wait, min_updates):
    ch = epics.PV(pv)
    assert ch is not None

    ch.connect()
    if not ch.connected:
        ch.wait_for_connection()
    assert ch.connected

    configuration = read_config.read_xml(CONFIG_FILE)
    watcher = pvwatch.PvWatch(configuration)
    watcher.add_pv(mne, pv, desc, fmt, as_string)
    assert watcher.pvdb.known(pv)

    entry = watcher.get(pv)
    assert entry is not None

    if wait > 0:
        time.sleep(wait)
    assert entry.counter >= min_updates

    assert mne in watcher.pvdb.mne_ref
    assert mne in list(watcher.pvdb.mnemonics)


def test_PvWatch():
    configuration = read_config.read_xml(CONFIG_FILE)
    assert isinstance(configuration, dict)

    watcher = pvwatch.PvWatch(configuration)
    assert watcher is not None

    # watcher.start()  # while True loop!
    watcher.report()
