from pytest import fixture

from pybuilder.core import Project
from pybuilder_read_profile_properties import (
    initialize_read_profile_properties_plugin,
    read_profile_properties_from_file
)

@fixture()
def tmp_project():
    return Project("basedir")


def test_init_should_set_dependency(tmp_project):
    initialize_read_profile_properties_plugin(tmp_project)
    assert 'PyYAML' in [dep.name for dep in tmp_project.plugin_dependencies]


def test_init_should_set_default_properties(tmp_project):
    initialize_read_profile_properties_plugin(tmp_project)
    expected_default_properties = {
            'profile': 'dev',
            'read_profile_properties_dir': '$basedir',
            'read_profile_properties_file_mask': 'properties_%s.yaml'
            }
    for property_name, property_value in expected_default_properties.items():
        assert tmp_project.get_property(property_name) == property_value


def test_init_should_leave_user_specified_properties_when_initializing_plugin(tmp_project):
    expected_properties = {
            'profile': 'qa',
            'read_profile_properties_dir': 'any_dir',
            'read_profile_properties_file_mask': 'some_properties_%s.yaml'
            }
    for property_name, property_value in expected_properties.items():
        tmp_project.set_property(property_name, property_value)

        initialize_read_profile_properties_plugin(tmp_project)

    for property_name, property_value in expected_properties.items():
        assert tmp_project.get_property(property_name) == property_value
