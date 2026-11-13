# Explicit, byte-preserving local staging; include after InstallHammondTools.
# Installed execution uses the embedded profile/glyphs and no source checkout.
if(HAMMOND_BUILD_STANDALONE AND TARGET hammond_standalone)
    hammond_require_relative_install_dir(Standalone CMAKE_INSTALL_BINDIR)
    hammond_require_relative_install_dir(Standalone CMAKE_INSTALL_DATADIR)
    find_package(Python3 3.10 REQUIRED COMPONENTS Interpreter)
    # A multi-config generator omits target-dependent install rules when no
    # configured name matches. Reject that selection before those rules: the
    # unconditional metadata copies must never produce a successful partial
    # installation. Match CMake's case-insensitive configuration selection.
    get_property(_hammond_standalone_multi_config GLOBAL PROPERTY GENERATOR_IS_MULTI_CONFIG)
    if(_hammond_standalone_multi_config)
        set(_hammond_standalone_configurations "${CMAKE_CONFIGURATION_TYPES}")
        list(TRANSFORM _hammond_standalone_configurations TOUPPER)
        set(_hammond_standalone_configuration_guard [=[
            string(TOUPPER "${CMAKE_INSTALL_CONFIG_NAME}" _hammond_standalone_selected_configuration)
            set(_hammond_standalone_allowed_configurations [==[@_hammond_standalone_configurations@]==])
            list(FIND _hammond_standalone_allowed_configurations
                "${_hammond_standalone_selected_configuration}" _hammond_standalone_configuration_index)
            if(_hammond_standalone_configuration_index EQUAL -1)
                message(FATAL_ERROR
                    "Standalone unknown configuration '${CMAKE_INSTALL_CONFIG_NAME}'; select a configured name: @_hammond_standalone_configurations@.")
            endif()
        ]=])
        string(CONFIGURE "${_hammond_standalone_configuration_guard}"
            _hammond_standalone_configuration_guard @ONLY)
        install(CODE "${_hammond_standalone_configuration_guard}" COMPONENT Standalone EXCLUDE_FROM_ALL)
    endif()
    get_filename_component(_hammond_standalone_source "${CMAKE_CURRENT_LIST_DIR}/.." ABSOLUTE)
    set(_hammond_standalone_data "${CMAKE_INSTALL_DATADIR}/hammond-b3-organ/standalone")
    set(_hammond_standalone_lock "${_hammond_standalone_source}/data/dependencies/sdl2-lock.json")
    set(_hammond_standalone_fonts "${_hammond_standalone_source}/assets/standalone/fonts")
    # Retain the configured identity, so a later source edit cannot silently
    # pair a different lock/notice with an already-built selected executable.
    file(READ "${_hammond_standalone_lock}" _hammond_standalone_lock_json)
    string(JSON _hammond_standalone_sdl_hash GET "${_hammond_standalone_lock_json}" license sha256)
    file(SHA256 "${_hammond_standalone_lock}" _hammond_standalone_lock_hash)
    file(READ "${_hammond_standalone_fonts}/source-manifest.json" _hammond_standalone_font_json)
    string(JSON _hammond_standalone_font_hash GET "${_hammond_standalone_font_json}" license sha256)
    file(SHA256 "${_hammond_standalone_fonts}/source-manifest.json" _hammond_standalone_font_manifest_hash)

    set(_hammond_standalone_preflight [=[
        if(DEFINED ENV{CMAKE_INSTALL_MODE} AND NOT "$ENV{CMAKE_INSTALL_MODE}" STREQUAL "" AND
           NOT "$ENV{CMAKE_INSTALL_MODE}" STREQUAL "COPY")
            message(FATAL_ERROR "Standalone requires CMAKE_INSTALL_MODE=COPY (or unset) for relocation.")
        endif()
        set(_hammond_standalone_inputs
            "$<TARGET_FILE:hammond_standalone>"
            "@_hammond_standalone_source@/docs/STANDALONE_INSTALL.md"
            "@_hammond_standalone_source@/docs/STANDALONE_APP.md"
            "@_hammond_standalone_source@/docs/STANDALONE_MODEL.md"
            "@_hammond_standalone_source@/THIRD_PARTY_NOTICES.md"
            "@HAMMOND_SDL2_ROOT@/LICENSE.txt"
            "@_hammond_standalone_fonts@/LICENSE-DejaVu.txt"
            "@_hammond_standalone_lock@"
            "@_hammond_standalone_fonts@/source-manifest.json")
        # lstat distinguishes ordinary files from FIFOs/devices as well as
        # directories and dangling symlinks, without opening a special file.
        # This entire read-only preflight precedes the first destination write.
        execute_process(COMMAND "@Python3_EXECUTABLE@" "-c" [==[
import hashlib
import os
from pathlib import Path
import stat
import sys

def reject(message):
    raise SystemExit("Standalone " + message)

inputs = [Path(value) for value in sys.argv[1:10]]
for path in inputs:
    try:
        info = path.lstat()
    except OSError as error:
        reject(f"missing or unreadable required input '{path}': {error}; build hammond_standalone for the selected configuration before installing.")
    if not stat.S_ISREG(info.st_mode):
        reject(f"requires a regular input without symlinks: '{path}'")
    if info.st_size == 0:
        reject(f"required input is empty: '{path}'")
for index, expected in (
    (5, "@_hammond_standalone_sdl_hash@"),
    (6, "@_hammond_standalone_font_hash@"),
    (7, "@_hammond_standalone_lock_hash@"),
    (8, "@_hammond_standalone_font_manifest_hash@"),
):
    if hashlib.sha256(inputs[index].read_bytes()).hexdigest() != expected:
        reject(f"configured notice/identity mismatch: '{inputs[index]}'")
binary, metadata = [Path(value) for value in sys.argv[10:]]
if binary == metadata or binary in metadata.parents:
    reject("executable and metadata destination paths conflict")
for destination in (binary, metadata):
    if os.path.lexists(destination):
        reject(f"destination already exists: '{destination}'; choose a fresh application destination; existing files/directories are never merged or replaced.")
    for parent in destination.parents:
        if os.path.lexists(parent) and not stat.S_ISDIR(parent.lstat().st_mode):
            reject(f"destination parent must be an ordinary directory without symlinks: '{parent}'")
]==] ${_hammond_standalone_inputs}
            "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/@CMAKE_INSTALL_BINDIR@/$<TARGET_FILE_NAME:hammond_standalone>"
            "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/@_hammond_standalone_data@"
            RESULT_VARIABLE _hammond_standalone_result
            OUTPUT_VARIABLE _hammond_standalone_output
            ERROR_VARIABLE _hammond_standalone_error)
        if(NOT "${_hammond_standalone_result}" STREQUAL "0")
            message(FATAL_ERROR "${_hammond_standalone_error}${_hammond_standalone_output}")
        endif()
    ]=])
    string(CONFIGURE "${_hammond_standalone_preflight}" _hammond_standalone_preflight @ONLY)
    install(CODE "${_hammond_standalone_preflight}" COMPONENT Standalone EXCLUDE_FROM_ALL)
    # PROGRAMS preserves the selected binary bytes instead of changing an RPATH
    # or stripping. This local payload does not collect platform runtime DLLs.
    install(PROGRAMS "$<TARGET_FILE:hammond_standalone>"
        DESTINATION "${CMAKE_INSTALL_BINDIR}" COMPONENT Standalone EXCLUDE_FROM_ALL)
    install(FILES
        "${_hammond_standalone_source}/docs/STANDALONE_INSTALL.md"
        "${_hammond_standalone_source}/docs/STANDALONE_APP.md"
        "${_hammond_standalone_source}/docs/STANDALONE_MODEL.md"
        "${_hammond_standalone_source}/THIRD_PARTY_NOTICES.md"
        "${_hammond_standalone_fonts}/LICENSE-DejaVu.txt"
        "${_hammond_standalone_lock}"
        DESTINATION "${_hammond_standalone_data}" COMPONENT Standalone EXCLUDE_FROM_ALL)
    install(FILES "${HAMMOND_SDL2_ROOT}/LICENSE.txt" RENAME LICENSE-SDL2.txt
        DESTINATION "${_hammond_standalone_data}" COMPONENT Standalone EXCLUDE_FROM_ALL)
    install(FILES "${_hammond_standalone_fonts}/source-manifest.json" RENAME font-source-manifest.json
        DESTINATION "${_hammond_standalone_data}" COMPONENT Standalone EXCLUDE_FROM_ALL)
endif()
