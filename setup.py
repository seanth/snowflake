#!/usr/bin/env python

from setuptools import setup

snowflake = {
    "name":"snowflake",
    "description":"snowflake generator",
    "author":"Giles Hall / Rachael Holmes",
    "packages": ["sfgen"],
    "package_dir": {
                    "sfgen": "src", 
                    },
    "py_modules":[
                    "sfgen.__init__", 
                    "sfgen.curves", 
                    "sfgen.engine",
                    "sfgen.graphics",
                    "sfgen.movie",
                    "sfgen.render",
                    "sfgen.runner",
                    "sfgen.splines",      
                ],
    "install_requires": [
        "pillow",
    ],
    "package_data": {"sfgen": ["etc/*.ini"]},
    "scripts":[
                "scripts/snowflake.py",
               ],
    "version": "0.31",
}

if __name__ == "__main__":
    setup(**snowflake)
