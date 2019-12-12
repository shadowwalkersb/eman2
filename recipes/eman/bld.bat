@echo on

SET builddir=%SRC_DIR%\..\build_eman
if errorlevel 1 exit 1

mkdir %builddir% && cd %builddir%
if errorlevel 1 exit 1

set CL=/MP

cmake --version
cmake "%SRC_DIR%" -G "%CMAKE_GENERATOR_APPVEYOR%" ^
                    -DCMAKE_BUILD_TYPE=Release    ^
                    -DENABLE_WARNINGS=OFF ^
                    -DCMAKE_VERBOSE_MAKEFILE=ON ^
                    -DENABLE_OPTIMIZE_WINDOWS_VC=ON
if errorlevel 1 exit 1

nmake
if errorlevel 1 exit 1

nmake install
if errorlevel 1 exit 1
