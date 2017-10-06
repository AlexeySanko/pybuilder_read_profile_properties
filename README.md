PyBuilder Read Profile Properties Plugin [![Build Status](https://travis-ci.org/AlexeySanko/pybuilder_read_profile_properties.svg?branch=master)](https://travis-ci.org/AlexeySanko/pybuilder_read_profile_properties)
=======================

The basic way to provide build-time specific properties is usage
pyb argument `-E/--environment` and initializers marked as environment specific.
For example:

```python
@init(environments="dev")
def init_dev(project):
    # dev build initialization
    project.set_property("some_property", "some_value")
```

But sometimes  we have a lot of external properties for config files filtering and more usefull to read these additional properties from YAML tree file.

Description
----------------------------------

Plugin provides possibility to read project properties from YAML file for according profile.
The main idea - support possibility to set different properties for different profiles (like Maven) which could be used directly or for filtering.
For example, You could have two profiles "dev" and "qa" and disable coverage fail for developing purpose.

How to use pybuilder_read_profile_properties
----------------------------------

Add plugin dependency to your `build.py`
```python
use_plugin("pypi:pybuilder_read_profile_properties")
```

Configure the plugin within your `init` function:
```python
@init
def init(project):
    # dir with configs - relative path from basedir
    project.set_property('read_profile_properties_dir', '')
    # mask for file name. For mask was used old style formatting with one string specifier.
    project.set_property('read_profile_properties_file_mask', 'properties_%s.yaml')
```

Preferred way is passing profile through command arguments:
```bash
pyb clean publish -P profile=dev
```
But You can always set it directly:
```python
@init
def init(project):
    # active profile
    project.set_property('profile', 'dev')
```

Example
----------------------------------
File ext_properties_dev.yaml into directory configs into basic project directory:
```yaml
mysql:
    host: localhost
    user: root
    passwd: my secret password
    db: default
other:
    preprocessing_queue:
        - preprocessing.scale_and_center
        - preprocessing.dot_reduction
        - preprocessing.connect_lines
    use_anonymous: yes
coverage:
    break_build: no
    threshold_warn: 50
```

build.py:
```python
@init
def set_properties(project, logger):
    # read properties for profile
    project.set_property('read_profile_properties_dir', 'configs')
    project.set_property('read_profile_properties_file_mask', 'ext_properties_%s.yaml')
```

Call command:
```bash
pyb clean publish --debug -P profile=dev
```

Debug output:
```
[DEBUG] External project properties from file: 
                    coverage_break_build : False (overwritten)
                 coverage_threshold_warn : 50 (overwritten)
                                mysql_db : default
                              mysql_host : localhost
                            mysql_passwd : my secret password
                              mysql_user : root
               other_preprocessing_queue : ['preprocessing.scale_and_center', 'preprocessing.dot_reduction', 'preprocessing.connect_lines']
                     other_use_anonymous : True
```

Example of filtering
----------------------------------

/src/main/resources/myproject.yaml:
```yaml
# myproject config file
mysql:
    host: ${mysql_host}
    user_name: ${mysql_user}
    password: ${mysql_passwd}
    database: ${mysql_db}
```

build.py:
```python
@init
def add_resources(project):
    # Add config file to distribution
    config_path = 'src/main/resources/myproject.yaml'
    project.get_property('copy_resources_glob').append(config_path)
    project.set_property('copy_resources_target', '$dir_dist')
    project.install_file('myproject', config_path)
    
@init
def filter_config(project):
    # filter target files
    project.set_property('filter_resources_target', '$dir_dist')
    project.get_property('filter_resources_glob').append('src/main/resources/myproject.yaml')
```

/target/dist/test_pybuilder-0.1.1/src/main/resources/myproject.yaml
```yaml
# myproject config file
mysql:
    host: localhost
    user_name: root
    password: my secret password
    database: default
```