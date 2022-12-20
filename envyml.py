#!/usr/bin/env python

import os
import re
import yaml
import json


def interpolate_environmental_variables_in_yaml(data):
    """
    Load yaml configuration resolving any environment variables.
    """
    default_sep = ":"
    default_sep_pattern = r"(" + default_sep + "[^}]+)?" if default_sep else ""
    pattern = re.compile(
        r".*?\$\{([^}{" + default_sep + r"]+)" + default_sep_pattern + r"\}.*?"
    )
    loader = yaml.SafeLoader
    loader.add_implicit_resolver(None, pattern, None)

    def constructor_env_variables(loader, node):
        """
        Extract the environment variable from the yaml node's value.
        """
        value = loader.construct_scalar(node)
        match = pattern.findall(value)  # to find all env variables in line
        if match:
            full_value = value
            for g in match:
                default_value = "N/A"
                env_var_name = g
                env_var_name_with_default = g

                if default_sep and isinstance(g, tuple) and len(g) > 1:
                    env_var_name = g[0]
                    env_var_name_with_default = "".join(g)
                    found = False
                    for each in g:
                        if default_sep in each:
                            _, default_value = each.split(default_sep, 1)
                            found = True
                            break
                env_var_value = os.environ.get(env_var_name)
                if env_var_value is not None and env_var_value != "":
                    return env_var_value
            return default_value
        return value

    loader.add_constructor(None, constructor_env_variables)

    return yaml.load(data, Loader=loader)


data = """
---
#
# Base config
#
DBDefaults: &dbdefaults
  server: ${SQL_SERVER_IP:127.0.0.1}
  user: apiuser
  password: F#L@e9Xp
  provider: mssql+pyodbc
  driver: ODBC Driver 17 for SQL Server

FlexOpDb:
  <<: *dbdefaults
  database: FlexOpDb
FlexWarehouse:
  <<: *dbdefaults
  database: FlexWarehouse
FlexDemandDb:
  <<: *dbdefaults
  database: FlexDemandDB
FlexForecast:
  <<: *dbdefaults
  database: FlexForecast
"""

if __name__ == "__main__":
    # os.environ["FOO"] = "/hello/world"
    p = interpolate_environmental_variables_in_yaml(data)
    print(json.dumps(p, indent=2))  ## /home/abc/file.txt
