FILE(GLOB tbxprograms "${CMAKE_CURRENT_SOURCE_DIR}/*.py")
INSTALL(FILES ${tbxprograms}
  DESTINATION    ${SP_DIR}/pyemtbx
)

install_develop_mode(${SP_DIR}/pyemtbx)
