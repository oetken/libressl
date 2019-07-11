 # Copyright 2017 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
include (ExternalProject)
include_guard(GLOBAL)

set(LIBRESSL_ROOT ${CMAKE_BINARY_DIR}/thirdparty/libressl)
set(LIBRESSL_INSTALL_DIR ${LIBRESSL_ROOT}/bin/ CACHE string "")
set(LIBRESSL_INCLUDE_DIRS ${LIBRESSL_INSTALL_DIR}/include CACHE string "")
set(LIBRESSL_URL https://code.siemens.com/PLUSCONTROL/thirdparty_libressl.git)
set(LIBRESSL_TAG v2.8.2)

if(WIN32)

  if(CMAKE_C_COMPILER_ID STREQUAL "GNU")
    set(LIBRESSL_LIB_CRYPTO ${LIBRESSL_INSTALL_DIR}lib/libcrypto-44.dll.a
        CACHE string "")
    set(LIBRESSL_LIB_SSL ${LIBRESSL_INSTALL_DIR}lib/libssl-46.dll.a
        CACHE string "")    
    set(LIBRESSL_DLLS ${LIBRESSL_INSTALL_DIR}/bin/libcrypto-44.dll ${LIBRESSL_INSTALL_DIR}/bin/libssl-46.dll ${LIBRESSL_INSTALL_DIR}/bin/libtls-18.dll  CACHE            string "")
  else()
    set(LIBRESSL_STATIC_LIBRARIES
    ${LIBRESSL_INSTALL_DIR}lib/crypto-44.lib ${LIBRESSL_INSTALL_DIR}lib/tls-18.lib ${LIBRESSL_INSTALL_DIR}lib/ssl-46.lib 
    CACHE string "")
    set(LIBRESSL_LIB_CRYPTO ${LIBRESSL_INSTALL_DIR}lib/crypto-44.lib
        CACHE string "")
    set(LIBRESSL_LIB_SSL ${LIBRESSL_INSTALL_DIR}lib/ssl-46.lib 
        CACHE string "")  
  endif()
  # This section is to make sure CONFIGURE_COMMAND use the same generator settings
  set(LIBRESSL_GENERATOR_PLATFORM)
  if (CMAKE_GENERATOR_PLATFORM)
    set(LIBRESSL_GENERATOR_PLATFORM -A ${CMAKE_GENERATOR_PLATFORM})
  endif()
  set(LIBRESSL_GENERATOR_TOOLSET)
  if (CMAKE_GENERATOR_TOOLSET)
  set(LIBRESSL_GENERATOR_TOOLSET -T ${CMAKE_GENERATOR_TOOLSET})
  endif()
  set(LIBRESSL_ADDITIONAL_CMAKE_OPTIONS	
    -G${CMAKE_GENERATOR} ${LIBRESSL_GENERATOR_PLATFORM} ${LIBRESSL_GENERATOR_TOOLSET})
  # End of section
  set(LIBRESSL_DLLS ${LIBRESSL_INSTALL_DIR}/bin/crypto-44.dll ${LIBRESSL_INSTALL_DIR}/bin/ssl-46.dll ${LIBRESSL_INSTALL_DIR}/bin/tls-18.dll  CACHE string "")
  set(LIBRESSL_OPENSSL_EXECUTABLE ${LIBRESSL_INSTALL_DIR}/bin/openssl.exe CACHE string "")
else()
  file(GLOB LIBRESSL_STATIC_LIBRARIES "${LIBRESSL_INSTALL_DIR}lib/*.so.*" )
  #set(LIBRESSL_STATIC_LIBRARIES ${LIBRESSL_INSTALL_DIR}lib/libcrypto.so ${LIBRESSL_INSTALL_DIR}lib/libtls.so ${LIBRESSL_INSTALL_DIR}lib/libssl.so
    #CACHE string "")
  set(LIBRESSL_LIB_CRYPTO ${LIBRESSL_INSTALL_DIR}lib/libcrypto.so
    CACHE string "")
  set(LIBRESSL_LIB_SSL ${LIBRESSL_INSTALL_DIR}lib/libssl.so
    CACHE string "")    
  set(LIBRESSL_OPENSSL_EXECUTABLE ${LIBRESSL_INSTALL_DIR}/bin/openssl CACHE string "")
endif()
if(NOT OPT_NATIVE_LIBRARIES)
    ExternalProject_Add(thirdparty_libressl
        PREFIX libressl
        TLS_VERIFY ON
        GIT_REPOSITORY ${LIBRESSL_URL}
        GIT_TAG ${LIBRESSL_TAG}
        GIT_SUBMODULES "" #We don't need the submodules here as we dont' need to build the tests
        GIT_PROGRESS ON #Just print a little bit the progress, otherwise you are sometimes stuck with waiting 
                        #and in the end the proxy setup is wrong
        DOWNLOAD_DIR "${DOWNLOAD_LOCATION}"
        BUILD_IN_SOURCE 1
        BUILD_BYPRODUCTS ${LIBRESSL_PROTOC_EXECUTABLE} ${LIBRESSL_STATIC_LIBRARIES}
        SOURCE_DIR ${LIBRESSL_ROOT}/src/libressl
        # SOURCE_SUBDIR cmake/ # Requires CMake 3.7, this will allow removal of CONFIGURE_COMMAND
        # CONFIGURE_COMMAND resets some settings made in CMAKE_CACHE_ARGS and the generator used
        CONFIGURE_COMMAND ${CMAKE_COMMAND} .
            -DCMAKE_INSTALL_PREFIX=${LIBRESSL_INSTALL_DIR}
            -DBUILD_SHARED_LIBS:BOOL=ON
            -DCMAKE_BUILD_TYPE:STRING=Release
            -DCMAKE_RUNTIME_OUTPUT_DIRECTORY_DEBUG=${CMAKE_RUNTIME_OUTPUT_DIRECTORY_DEBUG}
            -DCMAKE_RUNTIME_OUTPUT_DIRECTORY_RELEASE=${CMAKE_RUNTIME_OUTPUT_DIRECTORY_RELEASE}
            #-DCMAKE_C_FLAGS_RELEASE=/MT 
            #-DCMAKE_C_FLAGS_DEBUG=/MTd
            -DLIBRESSL_TESTS:BOOL=OFF
            -DCMAKE_TOOLCHAIN_FILE:STRING=${CMAKE_TOOLCHAIN_FILE}
            ${LIBRESSL_ADDITIONAL_CMAKE_OPTIONS}
        INSTALL_DIR ${LIBRESSL_INSTALL_DIR}
        CMAKE_CACHE_ARGS
            -DCMAKE_BUILD_TYPE:STRING=Release

    )

    set_target_properties(thirdparty_libressl PROPERTIES FOLDER "thirdparty")
    #TARGET_INCLUDE_DIRECTORIES(thirdparty_libressl PUBLIC ${LIBRESSL_INCLUDE_DIRS})
    #target_link_libraries(thirdparty_libressl PUBLIC ${LIBRESSL_DLLS})

    # Hack to make it works, otherwise INTERFACE_INCLUDE_DIRECTORIES will not be propagated
    file(MAKE_DIRECTORY ${LIBRESSL_INCLUDE_DIRS})

    #${LIBRESSL_INSTALL_DIR}lib/crypto-44.lib ${LIBRESSL_INSTALL_DIR}lib/tls-18.lib ${LIBRESSL_INSTALL_DIR}lib/ssl-46.lib

    add_library(libressl_crypto IMPORTED STATIC GLOBAL)
    add_dependencies(libressl_crypto thirdparty_libressl)
    set_target_properties(libressl_crypto PROPERTIES
            "IMPORTED_LOCATION" ${LIBRESSL_LIB_CRYPTO}
            "INTERFACE_INCLUDE_DIRECTORIES" "${LIBRESSL_INCLUDE_DIRS}"
    )

    add_library(libressl_ssl IMPORTED STATIC GLOBAL)
    add_dependencies(libressl_ssl thirdparty_libressl)
    set_target_properties(libressl_ssl PROPERTIES
            "IMPORTED_LOCATION" ${LIBRESSL_LIB_SSL}
            "INTERFACE_INCLUDE_DIRECTORIES" "${LIBRESSL_INCLUDE_DIRS}"
    )

    file(WRITE libressl_dummy.cpp
        "//This is a dummy"
    )
    add_library(libressl STATIC libressl_dummy.cpp)
    target_link_libraries(libressl libressl_ssl libressl_crypto)
    install(FILES ${LIBRESSL_STATIC_LIBRARIES} ${LIBRESSL_OPENSSL_EXECUTABLE} ${LIBRESSL_DLLS}
		DESTINATION bin)
    install(TARGETS libressl DESTINATION lib)

    install(TARGETS libressl
        EXPORT libresslConfig
        ARCHIVE DESTINATION lib
        LIBRARY DESTINATION lib
        RUNTIME DESTINATION bin
        PUBLIC_HEADER DESTINATION include/libressl
    )
    export(TARGETS libressl
        NAMESPACE pluscontrol::
        FILE "libresslConfig.cmake"
    )
    export(PACKAGE libressl)
    install(EXPORT libresslConfig
        #DESTINATION "${CMAKE_INSTALL_DATADIR}/cmake/${libName}"
        DESTINATION "libressl/cmake"
        NAMESPACE pluscontrol::
    )

    
else()
    find_package(OpenSSL REQUIRED) 
    message(${OPENSSL_LIBRARIES})
    include_directories(${OPENSSL_INCLUDE_DIRS})
    link_directories(${OPENSSL_LIBRARIES})

    file(TOUCH libressl_dummy.cpp
        "//This is a dummy"
    )
    add_library(libressl STATIC libressl_dummy.cpp)
    target_link_libraries(libressl ${OPENSSL_LIBRARIES})
endif()

#message("asdasdojao doiawjd oiawjd ${LIBRESSL_STATIC_LIBRARIES}")
#set_target_properties(libressl PROPERTIES
#        "IMPORTED_LOCATION" ${LIBRESSL_STATIC_LIBRARIES}
#        "INTERFACE_INCLUDE_DIRECTORIES" "${LIBRESSL_INCLUDE_DIRS}"
#)
