FUNCTION(message_var var)
	message("${var}: ${${var}}")
endfunction()

function(set_cache_var var val)
	if(val AND NOT ${var})
		set(${var} ${val} CACHE PATH "" FORCE)
	else()
		set(${var} ${var}-NOTFOUND CACHE PATH "")
	endif()
endfunction()

function(set_cache_var_to_var var val)
	if(${val} AND NOT ${var})
		set(${var} ${${val}} CACHE PATH "" FORCE)
	else()
		set(${var} ${var}-NOTFOUND CACHE PATH "")
	endif()
endfunction()

function(EMAN_CHECK_FUNCTION FUNCTION VARIABLE)
	CHECK_FUNCTION_EXISTS(${FUNCTION} ${VARIABLE})
	IF(${VARIABLE})
		ADD_DEFINITIONS(-D${VARIABLE})
	ENDIF()
endfunction()

OPTION(DEBUG_CHECK_REQUIRED_LIB "enable debug output for function CHECK_REQUIRED_LIB" OFF)
function(CHECK_REQUIRED_LIB upper lower header lower2 header2)
	if(DEBUG_CHECK_REQUIRED_LIB)
		message("\n### BEGIN ### CHECK_REQUIRED_LIB ${upper} ${lower} ${header} ${lower2} ${header2}")
		message_var(${upper}_INCLUDE_PATH)
		message_var(${upper}_LIBRARY)
		
		message("Searching in ${EMAN_PREFIX_INC} for ${header} and ${header2} ...")
	endif()
		
	FIND_PATH(${upper}_INCLUDE_PATH
			NAMES ${header} ${header2}
			PATHS $ENV{${upper}DIR}/include ${EMAN_PREFIX_INC}
			NO_DEFAULT_PATH
			)
	
	IF(${upper}_INCLUDE_PATH)
		FIND_LIBRARY(${upper}_LIBRARY NAMES ${lower} ${lower2} PATHS $ENV{${upper}DIR}/lib ${EMAN_PREFIX_LIB})
		
		if(DEBUG_CHECK_REQUIRED_LIB)
			message("FIND_LIBRARY: ${upper}_LIBRARY NAMES ${lower} ${lower2} PATHS $ENV{${upper}DIR}/lib ${EMAN_PREFIX_LIB}")
		endif()
	ENDIF()
	
	IF(NOT ${upper}_INCLUDE_PATH OR NOT ${upper}_LIBRARY)
		MESSAGE(SEND_ERROR "ERROR: ${upper} not found. please install ${upper} first!")
	ENDIF()

	if(DEBUG_CHECK_REQUIRED_LIB)
		message("### END ### CHECK_REQUIRED_LIB ${upper} ${lower} ${header} ${lower2} ${header2}")
		message_var(${upper}_INCLUDE_PATH)
		message_var(${upper}_LIBRARY)
	endif()
endfunction()

function(CHECK_LIB_ONLY upper lower)
	FIND_LIBRARY(${upper}_LIBRARY NAMES ${lower} PATHS $ENV{${upper}DIR}/lib ${EMAN_PREFIX_LIB} NO_DEFAULT_PATH)
	message(STATUS "CHECK_LIB_ONLY upper lower")
	message_var(${upper}_LIBRARY)
endfunction()

function(install_develop_mode dest_dir)
	FILE(GLOB files RELATIVE ${CMAKE_CURRENT_SOURCE_DIR} "${CMAKE_CURRENT_SOURCE_DIR}/*.py")
	
	foreach(p ${files})
		set(source_file "${CMAKE_CURRENT_SOURCE_DIR}/${p}")
		set(dest_file   "${dest_dir}/${p}")
#		message_var(p)
#		message("${source_file} ${dest_file}")
		INSTALL(CODE "execute_process(
					COMMAND ${CMAKE_COMMAND} -E create_symlink
					${source_file} ${dest_file}
					)"
				COMPONENT develop
				EXCLUDE_FROM_ALL
				)
	endforeach()
endfunction()
