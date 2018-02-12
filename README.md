![Example Snowflakes](https://raw.githubusercontent.com/vishnubob/snowflake/master/media/collage_medium.jpg)

This is a snowflake simulator written in python by Rachael Holmes and Giles
Hall.  It builds realistic looking snowflakes by modeling the phase
transistions between water molecules at a mesoscopic scale.  The model is
lifted (verbatim) from "MODELING SNOW CRYSTAL GROWTH II: A mesoscopic lattice
map with plausible dynamics" by Janko Gravner and David Griffeath.

Requirements:
    - PyPy (for fast execution of the simulations)
    - PIL for exporting graphics (PyPy accesible)

Requirements for Laser Cutting:
    - Python only (no PyPy support)
    - PIL (Python accessible)
    - potrace (For translating SVG)
    - scipy/numpy (For clustering)

Requirements for 3D Printing:
    - PyPy or Python
    - PIL (PyPy/Python accessible)
    - potrace (For translating SVG) (http://potrace.sourceforge.net/#downloading)
    - pstoedit
    - ghostscript (must be v9.2) (brew install https://raw.githubusercontent.com/Homebrew/homebrew-core/79e814b80c470c894d24e5b37108c5bacaf45a80/Formula/ghostscript.rb)
    - matplotlib
    - CURA version 15.04.6 (https://ultimaker.com/en/products/cura-software/list)

![Example Snowflake](https://raw.githubusercontent.com/vishnubob/snowflake/master/media/example.png)
