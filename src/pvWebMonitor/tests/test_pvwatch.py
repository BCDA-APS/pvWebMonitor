from .. import pvwatch
from .. import read_config
import pathlib


PROJECT_PATH = pathlib.Path(__file__).parent.parent / "project"
CONFIG_FILE = PROJECT_PATH / "config.xml"


def test_pvwatch():
    configuration = read_config.read_xml(CONFIG_FILE)
    assert isinstance(configuration, dict)

    watcher = pvwatch.PvWatch(configuration)
    assert watcher is not None

    # watcher.start()  # while True loop!
    watcher.report()
