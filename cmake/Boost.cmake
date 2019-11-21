set(Boost_USE_MULTITHREADED ON)
set(Boost_NO_BOOST_CMAKE ON)
find_package(Boost COMPONENTS python numpy REQUIRED)

message("Boost_LIBRARIES:   ${Boost_LIBRARIES}")
message("Boost_INCLUDE_DIR: ${Boost_INCLUDE_DIR}")

add_library(anaconda_compiler_include INTERFACE)
add_library(a::a ALIAS anaconda_compiler_include)
set_target_properties(anaconda_compiler_include
					PROPERTIES
					INTERFACE_INCLUDE_DIRECTORIES
					$<$<AND:$<CXX_COMPILER_ID:GNU>,$<BOOL:$ENV{CONDA_BUILD}>>:$ENV{BUILD_PREFIX}/x86_64-conda_cos6-linux-gnu/include/c++/7.3.0/>
)

#get_target_property(dd anaconda_compiler_include INTERFACE_INCLUDE_DIRECTORIES)
#cmake_print_variables(CMAKE_CXX_COMPILER_ID)
#message(FATAL_ERROR "CONDA_BUILD: $ENV{CONDA_BUILD} dd: ${dd}")
#add_custom_target(gen COMMAND ${CMAKE_COMMAND} -E echo    "$<$<AND:$<CXX_COMPILER_ID:GNU>,$<BOOL:$ENV{CONDA_BUILD}>>:YYYYYYYYYY>")
#file(GENERATE OUTPUT ${CMAKE_SOURCE_DIR}/genex.txt CONTENT "$<$<AND:$<CXX_COMPILER_ID:GNU>,$<BOOL:$ENV{CONDA_BUILD}>>:YYYYYYYYYY>")
#file(GENERATE OUTPUT ${CMAKE_SOURCE_DIR}/genex.txt CONTENT "$<$<BOOL:$ENV{CONDA_BUILD}>:YYYYYYYYYY>")
#file(GENERATE OUTPUT ${CMAKE_SOURCE_DIR}/genex.txt CONTENT "$<COMPILER_ID>")
#this definition is for boost.python > 1.35.0 
set_target_properties(Boost::python
					  PROPERTIES
					  INTERFACE_COMPILE_DEFINITIONS BOOST_PYTHON_NO_PY_SIGNATURES
					  INTERFACE_COMPILE_DEFINITIONS $<$<BOOL:WIN32>:BOOST_DISABLE_ASSERTS>
					  INTERFACE_LINK_LIBRARIES Python::Python
					  )

				  target_link_libraries(Boost::python INTERFACE a::a)

IF(CMAKE_SYSTEM MATCHES "IRIX.*")
    INCLUDE_DIRECTORIES(${Boost_INCLUDE_DIR}/boost/compatibility/cpp_c_headers)
ENDIF()
