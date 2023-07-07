import logging

__version__ = "1.0.8"

JNEUROML_VERSION = "0.12.2"

# Define a logger for the package
logging.basicConfig(
    format="pyNeuroML >>> %(levelname)s - %(message)s",
    level=logging.WARN,
)


def print_v(msg):
    """Print message to console.

    This is to be used for printing out messages during ordinary usage of the
    tool. For status monitoring, fault investigation etc., use the logger.

    :param msg: string to print
    :type msg: str
    """
    print("pyNeuroML >>> " + msg)
