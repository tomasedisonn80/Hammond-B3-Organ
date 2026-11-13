cmake_minimum_required(VERSION 3.21)
project(HammondB3Organ VERSION 0.1.0 LANGUAGES CXX)

if(CMAKE_SOURCE_DIR STREQUAL CMAKE_BINARY_DIR)
    message(FATAL_ERROR "Use an out-of-source build, for example: cmake -S . -B build")
endif()

option(HAMMOND_ENABLE_SANITIZERS "Enable AddressSanitizer and UndefinedBehaviorSanitizer" OFF)
option(HAMMOND_BUILD_VST3 "Build the optional pinned-SDK native VST3 instrument" OFF)
set(HAMMOND_VST3_SDK_ROOT "" CACHE PATH "Separately acquired, locked VST3 SDK checkout")
option(HAMMOND_BUILD_STANDALONE "Build the optional SDL2 native standalone instrument" OFF)
set(HAMMOND_SDL2_ROOT "" CACHE PATH "Separately acquired, locked SDL2 source checkout")
set(CMAKE_CXX_EXTENSIONS OFF)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

find_package(Python3 3.10 REQUIRED COMPONENTS Interpreter)
include(CTest)

if(HAMMOND_ENABLE_SANITIZERS)
    if(MSVC OR NOT CMAKE_CXX_COMPILER_ID MATCHES "^(GNU|Clang|AppleClang)$")
        message(FATAL_ERROR
            "HAMMOND_ENABLE_SANITIZERS requires GCC or Clang with both ASan and UBSan; "
            "MSVC/clang-cl and other compiler drivers are unsupported.")
    endif()
    include(CheckCXXSourceCompiles)
    function(hammond_check_sanitizers)
        set(CMAKE_REQUIRED_FLAGS "${CMAKE_REQUIRED_FLAGS} -fsanitize=address,undefined -fno-omit-frame-pointer")
        list(APPEND CMAKE_REQUIRED_LINK_OPTIONS "-fsanitize=address,undefined")
        check_cxx_source_compiles("int main() { return 0; }" HAMMOND_SANITIZERS_AVAILABLE)
    endfunction()
    hammond_check_sanitizers()
    if(NOT HAMMOND_SANITIZERS_AVAILABLE)
        message(FATAL_ERROR "The selected compiler cannot compile/link ASan and UBSan together.")
    endif()
endif()

function(hammond_configure_target target)
    target_compile_features(${target} PUBLIC cxx_std_20)
    if(MSVC)
        target_compile_options(${target} PRIVATE /W4 /WX /permissive- /Zc:__cplusplus)
    elseif(CMAKE_CXX_COMPILER_ID MATCHES "^(GNU|Clang|AppleClang)$")
        target_compile_options(${target} PRIVATE
            -Wall -Wextra -Wpedantic -Wconversion -Wsign-conversion -Wshadow -Werror)
    else()
        message(WARNING "No strict warning configuration is defined for ${CMAKE_CXX_COMPILER_ID}.")
    endif()
    if(HAMMOND_ENABLE_SANITIZERS)
        target_compile_options(${target} PRIVATE
            -fsanitize=address,undefined -fno-omit-frame-pointer)
        # A static core's consumers also need the sanitizer runtime at link time.
        target_link_options(${target} PUBLIC -fsanitize=address,undefined)
    endif()
endfunction()

file(GLOB HAMMOND_CORE_SOURCES CONFIGURE_DEPENDS "${CMAKE_CURRENT_SOURCE_DIR}/src/*.cpp")
if(NOT HAMMOND_CORE_SOURCES)
    message(FATAL_ERROR "No core C++ sources were found in src/.")
endif()
add_library(hammond_core STATIC ${HAMMOND_CORE_SOURCES})
target_include_directories(hammond_core PUBLIC "${CMAKE_CURRENT_SOURCE_DIR}/include")
hammond_configure_target(hammond_core)

# Documentary routing is compiled separately from the unchanged organ profile.
# Both independent CSV readings and the comparison manifest are build inputs.
set(HAMMOND_PEDAL_COMPILER "${CMAKE_CURRENT_SOURCE_DIR}/tools/compile_pedal_routing.py")
set(HAMMOND_PEDAL_MAP "${CMAKE_CURRENT_SOURCE_DIR}/data/pedal-map.json")
set(HAMMOND_PEDAL_REFERENCE "${CMAKE_CURRENT_SOURCE_DIR}/data/references/factory-table-iii.json")
set(HAMMOND_PEDAL_REVIEW_A "${CMAKE_CURRENT_SOURCE_DIR}/data/references/review-a-pedal.csv")
set(HAMMOND_PEDAL_REVIEW_B "${CMAKE_CURRENT_SOURCE_DIR}/data/references/review-b-pedal.csv")
set(HAMMOND_GENERATED_INCLUDE_DIR "${CMAKE_CURRENT_BINARY_DIR}/generated")
set(HAMMOND_PEDAL_HEADER "${HAMMOND_GENERATED_INCLUDE_DIR}/hammond/generated/PedalRoutingData.h")
add_custom_command(
    OUTPUT "${HAMMOND_PEDAL_HEADER}"
    COMMAND "${Python3_EXECUTABLE}" "${HAMMOND_PEDAL_COMPILER}"
        --input "${HAMMOND_PEDAL_MAP}" --reference "${HAMMOND_PEDAL_REFERENCE}"
        --review-a "${HAMMOND_PEDAL_REVIEW_A}" --review-b "${HAMMOND_PEDAL_REVIEW_B}"
        --output "${HAMMOND_PEDAL_HEADER}"
    DEPENDS "${HAMMOND_PEDAL_COMPILER}"
        "${CMAKE_CURRENT_SOURCE_DIR}/tools/validate_pedal_map.py"
        "${CMAKE_CURRENT_SOURCE_DIR}/tools/validate_factory_reference.py"
        "${HAMMOND_PEDAL_MAP}" "${HAMMOND_PEDAL_REFERENCE}"
        "${HAMMOND_PEDAL_REVIEW_A}" "${HAMMOND_PEDAL_REVIEW_B}"
    COMMENT "Checking both factory pedal readings and compiling native routing"
    VERBATIM)
add_custom_target(hammond_pedal_routing DEPENDS "${HAMMOND_PEDAL_HEADER}")
add_dependencies(hammond_core hammond_pedal_routing)
target_include_directories(hammond_core PRIVATE "${HAMMOND_GENERATED_INCLUDE_DIR}")

# The scanner is a separately identified documentary reconstruction. Admission
# of its full signed graph precedes generation of the native nominal constants.
set(HAMMOND_SCANNER_COMPILER "${CMAKE_CURRENT_SOURCE_DIR}/tools/compile_scanner_line.py")
set(HAMMOND_SCANNER_AUTHORING "${CMAKE_CURRENT_SOURCE_DIR}/data/scanner/atlas-late-b3-nominal-v1.json")
set(HAMMOND_SCANNER_HEADER "${HAMMOND_GENERATED_INCLUDE_DIR}/hammond/generated/ScannerLineData.h")
add_custom_command(
    OUTPUT "${HAMMOND_SCANNER_HEADER}"
    COMMAND "${CMAKE_COMMAND}" -E make_directory "${HAMMOND_GENERATED_INCLUDE_DIR}/hammond/generated"
    COMMAND "${Python3_EXECUTABLE}" "${HAMMOND_SCANNER_COMPILER}"
        --input "${HAMMOND_SCANNER_AUTHORING}"
        --output "${HAMMOND_SCANNER_HEADER}" --format header
    DEPENDS "${HAMMOND_SCANNER_COMPILER}" "${HAMMOND_SCANNER_AUTHORING}"
        "${CMAKE_CURRENT_SOURCE_DIR}/data/scanner-line.schema.json"
    COMMENT "Admitting the nominal scanner graph and compiling native constants"
    VERBATIM)
add_custom_target(hammond_scanner_data DEPENDS "${HAMMOND_SCANNER_HEADER}")
add_dependencies(hammond_core hammond_scanner_data)

set(HAMMOND_AUTHORING_PROFILE "${CMAKE_CURRENT_SOURCE_DIR}/data/profiles/nominal-unmeasured-v1.json")
set(HAMMOND_PROFILE_COMPILER "${CMAKE_CURRENT_SOURCE_DIR}/tools/compile_profile.py")
set(HAMMOND_COMPILED_PROFILE "${CMAKE_CURRENT_BINARY_DIR}/nominal.b3p")
add_custom_command(
    OUTPUT "${HAMMOND_COMPILED_PROFILE}"
    COMMAND "${Python3_EXECUTABLE}" "${HAMMOND_PROFILE_COMPILER}"
        --input "${HAMMOND_AUTHORING_PROFILE}" --output "${HAMMOND_COMPILED_PROFILE}"
    DEPENDS "${HAMMOND_PROFILE_COMPILER}" "${HAMMOND_AUTHORING_PROFILE}"
    COMMENT "Validating and compiling the nominal unmeasured profile"
    VERBATIM)
add_custom_target(hammond_profile ALL DEPENDS "${HAMMOND_COMPILED_PROFILE}")

file(GLOB HAMMOND_RENDER_SOURCE CONFIGURE_DEPENDS "${CMAKE_CURRENT_SOURCE_DIR}/tools/render.cpp")
if(HAMMOND_RENDER_SOURCE)
    add_executable(hammond_render ${HAMMOND_RENDER_SOURCE})
    target_link_libraries(hammond_render PRIVATE hammond_core)
    hammond_configure_target(hammond_render)
    add_dependencies(hammond_render hammond_profile)
endif()

add_executable(hammond_benchmark tools/benchmark.cpp)
target_link_libraries(hammond_benchmark PRIVATE hammond_core)
hammond_configure_target(hammond_benchmark)
target_compile_definitions(hammond_benchmark PRIVATE
    HAMMOND_BENCHMARK_PROFILE="${HAMMOND_COMPILED_PROFILE}"
    HAMMOND_BENCHMARK_CONFIGURATION="$<CONFIG>"
    HAMMOND_BENCHMARK_COMPILER_ID="${CMAKE_CXX_COMPILER_ID}"
    HAMMOND_BENCHMARK_COMPILER_VERSION="${CMAKE_CXX_COMPILER_VERSION}"
    HAMMOND_BENCHMARK_TARGET_SYSTEM="${CMAKE_SYSTEM_NAME}"
    HAMMOND_BENCHMARK_TARGET_PROCESSOR="${CMAKE_SYSTEM_PROCESSOR}"
    HAMMOND_BENCHMARK_SANITIZERS=$<BOOL:${HAMMOND_ENABLE_SANITIZERS}>)
add_dependencies(hammond_benchmark hammond_profile)

add_executable(hammond_model_info tools/model_info.cpp)
target_link_libraries(hammond_model_info PRIVATE hammond_core)
hammond_configure_target(hammond_model_info)

add_executable(hammond_parameter_info tools/parameter_info.cpp)
target_link_libraries(hammond_parameter_info PRIVATE hammond_core)
hammond_configure_target(hammond_parameter_info)

add_executable(hammond_console_trace tools/console_trace.cpp)
target_link_libraries(hammond_console_trace PRIVATE hammond_core)
hammond_configure_target(hammond_console_trace)
add_dependencies(hammond_console_trace hammond_profile)

add_executable(hammond_pedal_trace tools/pedal_trace.cpp)
target_link_libraries(hammond_pedal_trace PRIVATE hammond_core)
hammond_configure_target(hammond_pedal_trace)
add_dependencies(hammond_pedal_trace hammond_profile)

add_executable(hammond_scanner_line_probe tools/scanner_line_probe.cpp)
target_link_libraries(hammond_scanner_line_probe PRIVATE hammond_core)
hammond_configure_target(hammond_scanner_line_probe)

# All offline tools receive lossless Windows argv through wmain. Keep this
# executable-only startup option away from the core, tests and optional plugin.
if(MINGW)
    foreach(cli_target hammond_render hammond_benchmark hammond_model_info
                       hammond_parameter_info hammond_console_trace hammond_pedal_trace
                       hammond_scanner_line_probe)
        if(TARGET ${cli_target})
            target_link_options(${cli_target} PRIVATE -municode)
        endif()
    endforeach()
endif()

if(HAMMOND_BUILD_VST3)
    if(CMAKE_VERSION VERSION_LESS 3.25)
        message(FATAL_ERROR "The pinned optional VST3 SDK requires CMake 3.25 or newer.")
    endif()
    include(cmake/VerifyVst3Sdk.cmake)
    hammond_verify_vst3_sdk("${HAMMOND_VST3_SDK_ROOT}")
    set_target_properties(hammond_core PROPERTIES POSITION_INDEPENDENT_CODE ON)
    add_subdirectory(plugins/vst3)
endif()

add_subdirectory(apps/standalone)

if(BUILD_TESTING)
    find_package(Threads REQUIRED)
    set(HAMMOND_TEST_TARGETS ${HAMMOND_VST3_TEST_TARGETS} ${HAMMOND_STANDALONE_TEST_TARGETS})
    file(GLOB HAMMOND_CPP_TESTS CONFIGURE_DEPENDS "${CMAKE_CURRENT_SOURCE_DIR}/tests/test_*.cpp")
    foreach(test_source IN LISTS HAMMOND_CPP_TESTS)
        get_filename_component(test_name "${test_source}" NAME_WE)
        add_executable(${test_name} "${test_source}")
        target_link_libraries(${test_name} PRIVATE hammond_core)
        if(test_name STREQUAL "test_state_exchange")
            target_link_libraries(${test_name} PRIVATE Threads::Threads)
        endif()
        target_include_directories(${test_name} PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/tests")
        target_compile_definitions(${test_name} PRIVATE
            HAMMOND_TEST_PROFILE="${HAMMOND_COMPILED_PROFILE}"
            HAMMOND_SOURCE_DIR="${CMAKE_CURRENT_SOURCE_DIR}")
        hammond_configure_target(${test_name})
        add_dependencies(${test_name} hammond_profile)
        add_test(NAME ${test_name} COMMAND ${test_name})
        list(APPEND HAMMOND_TEST_TARGETS ${test_name})
    endforeach()

    file(GLOB HAMMOND_PYTHON_TESTS CONFIGURE_DEPENDS "${CMAKE_CURRENT_SOURCE_DIR}/tests/test_*.py")
    foreach(test_source IN LISTS HAMMOND_PYTHON_TESTS)
        get_filename_component(test_name "${test_source}" NAME_WE)
        add_test(NAME "python_${test_name}" COMMAND "${Python3_EXECUTABLE}" "${test_source}")
        set_tests_properties("python_${test_name}" PROPERTIES
            WORKING_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}"
            ENVIRONMENT "PYTHONDONTWRITEBYTECODE=1;HAMMOND_TEST_PROFILE=${HAMMOND_COMPILED_PROFILE};HAMMOND_SOURCE_DIR=${CMAKE_CURRENT_SOURCE_DIR}")
        set_property(TEST "python_${test_name}" APPEND PROPERTY ENVIRONMENT
            "HAMMOND_SCANNER_LINE_PROBE_EXECUTABLE=$<TARGET_FILE:hammond_scanner_line_probe>")
    endforeach()
    list(APPEND HAMMOND_TEST_TARGETS hammond_scanner_line_probe)

    foreach(build_tool_test python_test_vst3_build_tools python_test_sdl2_dependency)
        if(TEST ${build_tool_test})
            set_property(TEST ${build_tool_test} APPEND PROPERTY ENVIRONMENT
                "HAMMOND_TEST_CMAKE=${CMAKE_COMMAND}")
        endif()
    endforeach()

    if(TARGET hammond_render)
        foreach(test_source IN LISTS HAMMOND_PYTHON_TESTS)
            get_filename_component(test_name "${test_source}" NAME_WE)
            set_property(TEST "python_${test_name}" APPEND PROPERTY ENVIRONMENT
                "HAMMOND_RENDER_EXECUTABLE=$<TARGET_FILE:hammond_render>")
        endforeach()
        list(APPEND HAMMOND_TEST_TARGETS hammond_render)
    endif()

    if(TEST python_test_model_info)
        set_property(TEST python_test_model_info APPEND PROPERTY ENVIRONMENT
            "HAMMOND_MODEL_INFO_EXECUTABLE=$<TARGET_FILE:hammond_model_info>")
        list(APPEND HAMMOND_TEST_TARGETS hammond_model_info)
    endif()

    if(TEST python_test_parameter_bridge)
        set_property(TEST python_test_parameter_bridge APPEND PROPERTY ENVIRONMENT
            "HAMMOND_PARAMETER_INFO_EXECUTABLE=$<TARGET_FILE:hammond_parameter_info>")
        list(APPEND HAMMOND_TEST_TARGETS hammond_parameter_info)
    endif()

    if(TEST python_test_console_benchmark)
        set_property(TEST python_test_console_benchmark APPEND PROPERTY ENVIRONMENT
            "HAMMOND_BENCHMARK_EXECUTABLE=$<TARGET_FILE:hammond_benchmark>")
        list(APPEND HAMMOND_TEST_TARGETS hammond_benchmark)
    endif()

    if(TEST python_test_cli_unicode)
        set_property(TEST python_test_cli_unicode APPEND PROPERTY ENVIRONMENT
            "HAMMOND_BENCHMARK_EXECUTABLE=$<TARGET_FILE:hammond_benchmark>"
            "HAMMOND_MODEL_INFO_EXECUTABLE=$<TARGET_FILE:hammond_model_info>"
            "HAMMOND_PARAMETER_INFO_EXECUTABLE=$<TARGET_FILE:hammond_parameter_info>")
        list(APPEND HAMMOND_TEST_TARGETS
            hammond_benchmark hammond_model_info hammond_parameter_info)
    endif()

    foreach(test_source IN LISTS HAMMOND_PYTHON_TESTS)
        get_filename_component(test_name "${test_source}" NAME_WE)
        set_property(TEST "python_${test_name}" APPEND PROPERTY ENVIRONMENT
            "HAMMOND_CONSOLE_TRACE_EXECUTABLE=$<TARGET_FILE:hammond_console_trace>")
    endforeach()
    list(APPEND HAMMOND_TEST_TARGETS hammond_console_trace)

    foreach(test_source IN LISTS HAMMOND_PYTHON_TESTS)
        get_filename_component(test_name "${test_source}" NAME_WE)
        set_property(TEST "python_${test_name}" APPEND PROPERTY ENVIRONMENT
            "HAMMOND_PEDAL_TRACE_EXECUTABLE=$<TARGET_FILE:hammond_pedal_trace>")
    endforeach()
    list(APPEND HAMMOND_TEST_TARGETS hammond_pedal_trace)

    # Unlike invoking CTest directly, this target first builds its required inputs.
    add_custom_target(check
        COMMAND "${CMAKE_CTEST_COMMAND}" --output-on-failure --no-tests=error -C "$<CONFIG>"
        WORKING_DIRECTORY "${CMAKE_CURRENT_BINARY_DIR}"
        DEPENDS hammond_profile ${HAMMOND_TEST_TARGETS}
        USES_TERMINAL)
endif()

# Component-scoped installation is defined after all targets and tests.
include(cmake/InstallHammondTools.cmake)
include(cmake/InstallStandalone.cmake)

if(HAMMOND_BUILD_STANDALONE AND BUILD_TESTING)
    add_test(NAME test_standalone_install
        COMMAND "${Python3_EXECUTABLE}" "${PROJECT_SOURCE_DIR}/apps/standalone/native_tests/test_standalone_install.py")
    set_tests_properties(test_standalone_install PROPERTIES
        TIMEOUT 90 LABELS "standalone;native"
        ENVIRONMENT "PYTHONDONTWRITEBYTECODE=1;HAMMOND_TEST_CMAKE=${CMAKE_COMMAND};HAMMOND_TEST_BUILD_DIR=${CMAKE_BINARY_DIR};HAMMOND_TEST_CONFIG=$<CONFIG>;HAMMOND_STANDALONE_EXECUTABLE=$<TARGET_FILE:hammond_standalone>;HAMMOND_SDL2_ROOT=${HAMMOND_SDL2_ROOT};HAMMOND_INSTALL_BINDIR=${CMAKE_INSTALL_BINDIR};HAMMOND_INSTALL_DATADIR=${CMAKE_INSTALL_DATADIR}")
endif()

if(HAMMOND_BUILD_VST3 AND BUILD_TESTING)
    add_test(NAME test_native_install
        COMMAND "${Python3_EXECUTABLE}" "${PROJECT_SOURCE_DIR}/plugins/vst3/tests/test_native_install.py")
    get_target_property(HAMMOND_NATIVE_INSTALL_BUNDLE HammondB3 SMTG_PLUGIN_PACKAGE_PATH)
    set_tests_properties(test_native_install PROPERTIES
        TIMEOUT 240
        ENVIRONMENT "PYTHONDONTWRITEBYTECODE=1;HAMMOND_TEST_CMAKE=${CMAKE_COMMAND};HAMMOND_TEST_BUILD_DIR=${CMAKE_BINARY_DIR};HAMMOND_TEST_CONFIG=$<CONFIG>;HAMMOND_TEST_PROFILE=${HAMMOND_COMPILED_PROFILE};HAMMOND_TEST_VST3_BUNDLE=${HAMMOND_NATIVE_INSTALL_BUNDLE};HAMMOND_TEST_NATIVE_MODULE=$<TARGET_FILE:HammondB3>;HAMMOND_TEST_NATIVE_ABI=$<TARGET_FILE:test_native_abi>;HAMMOND_INSTALL_LIBDIR=${CMAKE_INSTALL_LIBDIR}")
endif()
