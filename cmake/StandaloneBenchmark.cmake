# Included from apps/standalone after support and the test-target list exist.
# This target and its admission tests require no SDL or native host SDK.
include_guard(DIRECTORY)

function(hammond_add_standalone_benchmark)
    file(GLOB benchmark_core_headers CONFIGURE_DEPENDS
        "${PROJECT_SOURCE_DIR}/include/hammond/*.h")
    set(benchmark_inputs
        ${HAMMOND_CORE_SOURCES} ${benchmark_core_headers}
        "${PROJECT_SOURCE_DIR}/apps/standalone/Session.h"
        "${PROJECT_SOURCE_DIR}/apps/standalone/Session.cpp"
        "${PROJECT_SOURCE_DIR}/apps/standalone/benchmark.cpp"
        "${PROJECT_SOURCE_DIR}/tools/CliArguments.h"
        "${HAMMOND_PEDAL_COMPILER}"
        "${PROJECT_SOURCE_DIR}/tools/validate_pedal_map.py"
        "${PROJECT_SOURCE_DIR}/tools/validate_factory_reference.py"
        "${HAMMOND_PEDAL_MAP}" "${HAMMOND_PEDAL_REFERENCE}"
        "${HAMMOND_PEDAL_REVIEW_A}" "${HAMMOND_PEDAL_REVIEW_B}"
        "${HAMMOND_SCANNER_COMPILER}" "${HAMMOND_SCANNER_AUTHORING}"
        "${PROJECT_SOURCE_DIR}/data/scanner-line.schema.json"
        "${HAMMOND_PROFILE_COMPILER}" "${HAMMOND_AUTHORING_PROFILE}")
    list(REMOVE_DUPLICATES benchmark_inputs)
    set_property(DIRECTORY APPEND PROPERTY CMAKE_CONFIGURE_DEPENDS ${benchmark_inputs})

    # Relative paths make source relocation irrelevant to the fingerprint. The
    # selected repository inputs use this unambiguous ASCII path vocabulary;
    # reject unsafe names instead of emitting malformed JSON/record delimiters.
    set(benchmark_paths)
    foreach(input IN LISTS benchmark_inputs)
        if(NOT EXISTS "${input}" OR IS_DIRECTORY "${input}")
            message(FATAL_ERROR "Standalone benchmark input is not a file: ${input}")
        endif()
        file(RELATIVE_PATH relative "${PROJECT_SOURCE_DIR}" "${input}")
        if(IS_ABSOLUTE "${relative}" OR
           NOT relative MATCHES "^[A-Za-z0-9_./+-]+$" OR
           relative MATCHES "(^|/)\\.\\.?(/|$)" OR relative MATCHES "//")
            message(FATAL_ERROR "Unsafe standalone benchmark relative input: ${relative}")
        endif()
        list(APPEND benchmark_paths "${relative}")
    endforeach()
    list(REMOVE_DUPLICATES benchmark_paths)
    list(SORT benchmark_paths)
    set(benchmark_records "")
    set(benchmark_entries "")
    set(separator "")
    foreach(relative IN LISTS benchmark_paths)
        file(SHA256 "${PROJECT_SOURCE_DIR}/${relative}" digest)
        string(APPEND benchmark_records "${relative}:${digest}\n")
        string(APPEND benchmark_entries
            "${separator}    {\"path\":\"${relative}\",\"sha256\":\"${digest}\"}")
        set(separator ",\n")
    endforeach()
    string(SHA256 benchmark_source_id "${benchmark_records}")
    set(benchmark_manifest "${CMAKE_CURRENT_BINARY_DIR}/standalone-benchmark-source-manifest.json")
    file(CONFIGURE OUTPUT "${benchmark_manifest}" CONTENT
        "{\n  \"schema_version\":1,\n  \"entries\":[\n${benchmark_entries}\n  ],\n  \"source_manifest_sha256\":\"${benchmark_source_id}\"\n}\n"
        @ONLY)

    add_executable(hammond_standalone_benchmark
        "${PROJECT_SOURCE_DIR}/apps/standalone/benchmark.cpp")
    target_link_libraries(hammond_standalone_benchmark PRIVATE hammond_standalone_support)
    target_include_directories(hammond_standalone_benchmark PRIVATE "${PROJECT_SOURCE_DIR}/tools")
    hammond_configure_target(hammond_standalone_benchmark)
    add_dependencies(hammond_standalone_benchmark hammond_profile)
    set(benchmark_configuration "$<IF:$<STREQUAL:$<CONFIG>,>,Unspecified,$<CONFIG>>")
    target_compile_definitions(hammond_standalone_benchmark PRIVATE
        HAMMOND_STANDALONE_BENCHMARK_CONFIGURATION="${benchmark_configuration}"
        HAMMOND_STANDALONE_BENCHMARK_COMPILER_ID="${CMAKE_CXX_COMPILER_ID}"
        HAMMOND_STANDALONE_BENCHMARK_COMPILER_VERSION="${CMAKE_CXX_COMPILER_VERSION}"
        HAMMOND_STANDALONE_BENCHMARK_TARGET_SYSTEM="${CMAKE_SYSTEM_NAME}"
        HAMMOND_STANDALONE_BENCHMARK_TARGET_PROCESSOR="${CMAKE_SYSTEM_PROCESSOR}"
        HAMMOND_STANDALONE_BENCHMARK_SANITIZERS=$<BOOL:${HAMMOND_ENABLE_SANITIZERS}>
        HAMMOND_STANDALONE_BENCHMARK_SOURCE_ID="${benchmark_source_id}")
    if(MINGW)
        target_link_options(hammond_standalone_benchmark PRIVATE -municode)
    endif()

    if(BUILD_TESTING)
        add_test(NAME test_standalone_benchmark
            COMMAND "${CMAKE_COMMAND}" -E env
                "PYTHONDONTWRITEBYTECODE=1"
                "HAMMOND_STANDALONE_BENCHMARK_EXECUTABLE=$<TARGET_FILE:hammond_standalone_benchmark>"
                "HAMMOND_TEST_PROFILE=${HAMMOND_COMPILED_PROFILE}"
                "HAMMOND_STANDALONE_BENCHMARK_SOURCE_MANIFEST=${benchmark_manifest}"
                "HAMMOND_SOURCE_DIR=${PROJECT_SOURCE_DIR}"
                "HAMMOND_STANDALONE_BENCHMARK_EXPECTED_CONFIGURATION=${benchmark_configuration}"
                "HAMMOND_STANDALONE_BENCHMARK_EXPECTED_COMPILER_ID=${CMAKE_CXX_COMPILER_ID}"
                "HAMMOND_STANDALONE_BENCHMARK_EXPECTED_COMPILER_VERSION=${CMAKE_CXX_COMPILER_VERSION}"
                "HAMMOND_STANDALONE_BENCHMARK_EXPECTED_TARGET_SYSTEM=${CMAKE_SYSTEM_NAME}"
                "HAMMOND_STANDALONE_BENCHMARK_EXPECTED_TARGET_PROCESSOR=${CMAKE_SYSTEM_PROCESSOR}"
                "${Python3_EXECUTABLE}"
                "${PROJECT_SOURCE_DIR}/apps/standalone/tests/test_standalone_benchmark.py")
        set_tests_properties(test_standalone_benchmark PROPERTIES
            WORKING_DIRECTORY "${PROJECT_SOURCE_DIR}" TIMEOUT 90 LABELS "standalone;benchmark")
        list(APPEND HAMMOND_STANDALONE_TEST_TARGETS hammond_standalone_benchmark)
        set(HAMMOND_STANDALONE_TEST_TARGETS "${HAMMOND_STANDALONE_TEST_TARGETS}" PARENT_SCOPE)
    endif()
endfunction()

hammond_add_standalone_benchmark()
