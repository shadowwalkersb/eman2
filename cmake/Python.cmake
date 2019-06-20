find_package(Python REQUIRED COMPONENTS Interpreter Development)

set(CMAKE_FIND_FRAMEWORK_BACK ${CMAKE_FIND_FRAMEWORK})
set(CMAKE_FIND_FRAMEWORK NEVER)
set(Python_FIND_REGISTRY NEVER)

set(CMAKE_FIND_FRAMEWORK ${CMAKE_FIND_FRAMEWORK_BACK})
unset(CMAKE_FIND_FRAMEWORK_BACK)

message("PYTHON_EXECUTABLE:   ${Python_EXECUTABLE}")
message("PYTHON_LIBRARIES:    ${Python_LIBRARIES}")
message("PYTHON_INCLUDE_DIRS: ${Python_INCLUDE_DIRS}")
message("Python site-packages: ${Python_SITELIB}")
message("Python_INTERPRETER_ID: ${Python_INTERPRETER_ID}")

# Set SP_DIR
if("$ENV{CONDA_BUILD_STATE}" STREQUAL "BUILD" )
	set(SP_DIR $ENV{SP_DIR})
else()
	if(NOT WIN32)
		set(py_sp_dir_command "import site; print(site.getsitepackages()[0])")
	else()
		set(py_sp_dir_command "import site; print(site.getsitepackages()[1])")
	endif()
	execute_process(COMMAND ${PYTHON_EXECUTABLE} -c "${py_sp_dir_command}"
			OUTPUT_VARIABLE SP_DIR
			OUTPUT_STRIP_TRAILING_WHITESPACE
			)
	message("Python site-packages: ${SP_DIR}")
endif()
