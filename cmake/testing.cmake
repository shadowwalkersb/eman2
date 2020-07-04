enable_testing()

add_custom_target(test-verbose
		COMMAND ${CMAKE_COMMAND} -P cmake_install.cmake
		COMMAND ${CMAKE_CTEST_COMMAND} -V -C Release
		)

add_test(NAME imports
		 COMMAND ${PYTHON_EXECUTABLE} ${CMAKE_SOURCE_DIR}/tests/test_imports.py
		 )

add_test(NAME test-EMAN2DIR
		 COMMAND ${PYTHON_EXECUTABLE} ${CMAKE_SOURCE_DIR}/tests/test_EMAN2DIR.py
		 )

add_custom_target(test-verbose-broken
		COMMAND ${NOSETESTS_EXECUTABLE} -v -m "^test_*" -a broken ${CMAKE_SOURCE_DIR}/rt/pyem/*
		)


add_test(NAME py-compile
		COMMAND ${PYTHON_EXECUTABLE} -m compileall -q -x .git ${CMAKE_SOURCE_DIR}
		)

add_custom_target(test-py-compile
		COMMAND ${CMAKE_CTEST_COMMAND} -V -C Release -R py-compile
		DEPENDS PythonFiles
		)
