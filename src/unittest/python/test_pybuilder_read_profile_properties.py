#   -*- coding: utf-8 -*-
#
#   Copyright 2016 Alexey Sanko
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

from mock import Mock
from pytest import fixture, raises

from pybuilder.core import Project
from pybuilder.errors import BuildFailedException
from pybuilder_read_profile_properties import (
    initialize_read_profile_properties_plugin,
    read_profile_properties_from_file,
    __add_to_prop,
    __dict_tree_to_flat,
    DEFAULT_ROOT_ELEMENT
)


@fixture()
def mock_project():
    return Project("basedir")


def create_test_project(tmpdir, name, conf_content_dict):
    project_dir = tmpdir.mkdir(name)
    test_project = Project(str(project_dir))
    config_dir = project_dir.mkdir('configs')
    test_project.set_property('read_profile_properties_dir',
                              'configs')
    for file_name, content in conf_content_dict.items():
        f = config_dir.join(file_name)
        f.write(content)
    return test_project


def test_init_should_set_dependency(mock_project):
    initialize_read_profile_properties_plugin(mock_project)
    assert 'PyYAML' in [dep.name for dep in mock_project.plugin_dependencies]


def test_init_should_set_default_properties(mock_project):
    initialize_read_profile_properties_plugin(mock_project)
    expected_default_properties = {
            'profile': 'dev',
            'read_profile_properties_dir': '',
            'read_profile_properties_file_mask': 'properties_%s.yaml'
            }
    for property_name, property_value in expected_default_properties.items():
        assert mock_project.get_property(property_name) == property_value


def test_init_should_leave_user_specified_properties_when_initializing_plugin(mock_project):
    expected_properties = {
            'profile': 'qa',
            'read_profile_properties_dir': 'any_dir',
            'read_profile_properties_file_mask': 'some_properties_%s.yaml'
            }
    for property_name, property_value in expected_properties.items():
        mock_project.set_property(property_name, property_value)

        initialize_read_profile_properties_plugin(mock_project)

    for property_name, property_value in expected_properties.items():
        assert mock_project.get_property(property_name) == property_value


def test__add_to_prop():
    assert __add_to_prop(DEFAULT_ROOT_ELEMENT, '123') == '123'
    assert __add_to_prop('456', '123') == '456_123'


def test__dict_tree_to_flat():
    d = {'a': 1, 'b': {'c': 2, 'd': 3}, 'e':4}
    assert __dict_tree_to_flat(d) == {'a':1, 'b_c': 2, 'b_d': 3, 'e': 4}


success_yaml = """
mysql:
    host: localhost
    user:
        name: root
        pwd: password
coverage:
    break_build: no
    threshold_warn: 50
"""


def test_should_read_properties_from_file(tmpdir):
    yaml_file_mask = 'props_%s.yaml'
    yaml_file_name = yaml_file_mask % 'qa'
    test_project = create_test_project(tmpdir,
                                       'rpp_success',
                                       {yaml_file_name: success_yaml}
                                       )
    test_project.set_property('read_profile_properties_file_mask', 'props_%s.yaml')
    test_project.set_property('profile', 'qa')
    read_profile_properties_from_file(test_project, Mock())
    assert test_project.get_property('mysql_host') == 'localhost'
    assert test_project.get_property('mysql_user_name') == 'root'
    assert test_project.get_property('mysql_user_pwd') == 'password'
    assert not test_project.get_property('coverage_break_build')
    assert test_project.get_property('coverage_threshold_warn') == 50


def test_fail_if_file_doesnt_exist(mock_project):
    initialize_read_profile_properties_plugin(mock_project)
    with raises(BuildFailedException) as excinfo:
        read_profile_properties_from_file(mock_project, Mock())
    assert "Properties file doesn't exists:" in str(excinfo.value)


# def test_fail_if_incorrect_name_mask

