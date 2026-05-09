"""# vectra.configuration.core.conftest

Fixtures for `configuration.core` tests.
"""

from pytest             import fixture

from vectra.conftest    import ConcreteConfig, ConcreteConfigWithSubparser


@fixture
def config() -> ConcreteConfig:
    """# Basic ConcreteConfig Instance"""
    return ConcreteConfig()


@fixture
def config_with_args() -> ConcreteConfig:
    """# ConcreteConfig That Defines --foo Argument"""
    return ConcreteConfig(extra_args = True)


@fixture
def config_with_subparser() -> ConcreteConfigWithSubparser:
    """# COncreteConfig That Creates a Sub-Parser"""
    return ConcreteConfigWithSubparser()