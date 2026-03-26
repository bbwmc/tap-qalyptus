"""Module entry point for tap-qalyptus."""

from tap_qalyptus.tap import TapQalyptus


if __name__ == "__main__":
    TapQalyptus.cli()
