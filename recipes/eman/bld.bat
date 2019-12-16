@echo on

SET builddir=%SRC_DIR%\..\build_eman
if errorlevel 1 exit 1

mkdir %builddir% && cd %builddir%
if errorlevel 1 exit 1

set CL=/MP

cmake --version
cmake "%SRC_DIR%" -G "Visual Studio 15 2017 Win64" ^
                    -DCMAKE_BUILD_TYPE=Release    ^
                    -DENABLE_WARNINGS=OFF ^
                    -DCMAKE_VERBOSE_MAKEFILE=ON ^
                    -DENABLE_OPTIMIZE_WINDOWS_VC=ON
if errorlevel 1 exit 1

cmake --build "%builddir%" --config Release --target install
if errorlevel 1 exit 1
