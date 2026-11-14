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
    set(_hammond_standalone_reference "${_hammond_standalone_source}/assets/standalone/reference/manifest.json")
    set(_hammond_standalone_atlas "${_hammond_standalone_source}/docs/design/atlas-reference.json")
    # Retain configured identities. Installation never discovers a backend,
    # acquires an SDK, or silently substitutes changed notices for the build.
    file(READ "${_hammond_standalone_lock}" _hammond_standalone_lock_json)
    string(JSON _hammond_standalone_sdl_version GET "${_hammond_standalone_lock_json}" version)
    string(JSON _hammond_standalone_sdl_commit GET "${_hammond_standalone_lock_json}" commit)
    string(JSON _hammond_standalone_sdl_hash GET "${_hammond_standalone_lock_json}" license sha256)
    file(SHA256 "${_hammond_standalone_lock}" _hammond_standalone_lock_hash)
    file(READ "${_hammond_standalone_fonts}/source-manifest.json" _hammond_standalone_font_json)
    string(JSON _hammond_standalone_font_hash GET "${_hammond_standalone_font_json}" license sha256)
    file(SHA256 "${_hammond_standalone_fonts}/source-manifest.json" _hammond_standalone_font_manifest_hash)
    file(READ "${_hammond_standalone_reference}" _hammond_standalone_reference_json)
    string(JSON _hammond_standalone_reference_id GET "${_hammond_standalone_reference_json}" identity)
    string(JSON _hammond_standalone_reference_image_hash GET "${_hammond_standalone_reference_json}" source sha256)
    file(SHA256 "${_hammond_standalone_reference}" _hammond_standalone_reference_hash)
    file(SHA256 "${_hammond_standalone_atlas}" _hammond_standalone_atlas_hash)
    set(_hammond_standalone_metadata_sources
        "${_hammond_standalone_source}/docs/STANDALONE_INSTALL.md"
        "${_hammond_standalone_source}/docs/STANDALONE_APP.md"
        "${_hammond_standalone_source}/docs/STANDALONE_MODEL.md"
        "${_hammond_standalone_source}/docs/MIDI_UI_RUNBOOK.md"
        "${_hammond_standalone_source}/docs/PRESET_RUNBOOK.md"
        "${_hammond_standalone_source}/docs/INTERFACE_RUNBOOK.md"
        "${_hammond_standalone_source}/THIRD_PARTY_NOTICES.md"
        "${HAMMOND_SDL2_ROOT}/LICENSE.txt"
        "${_hammond_standalone_fonts}/LICENSE-DejaVu.txt"
        "${_hammond_standalone_lock}"
        "${_hammond_standalone_fonts}/source-manifest.json"
        "${_hammond_standalone_reference}"
        "${_hammond_standalone_atlas}")
    set(_hammond_standalone_metadata_names
        STANDALONE_INSTALL.md STANDALONE_APP.md STANDALONE_MODEL.md MIDI_UI_RUNBOOK.md
        PRESET_RUNBOOK.md INTERFACE_RUNBOOK.md
        THIRD_PARTY_NOTICES.md LICENSE-SDL2.txt LICENSE-DejaVu.txt sdl2-lock.json
        font-source-manifest.json reference-source-manifest.json atlas-reference.json)
    set(_hammond_standalone_midi_json [=[
    "enabled": false,
    "backend": "unavailable",
    "availability": "No physical MIDI backend was compiled. Keyboard, pointer and explicit synthetic replay remain available.",
    "rtmidi": null]=])
    if(HAMMOND_ENABLE_MIDI)
        if(NOT TARGET hammond_rtmidi)
            message(FATAL_ERROR "Standalone MIDI installation requires the configured hammond_rtmidi target.")
        endif()
        get_target_property(_hammond_standalone_rtmidi_prepared hammond_rtmidi HAMMOND_RTMIDI_PREPARED_ROOT)
        get_target_property(_hammond_standalone_midi_backend hammond_rtmidi HAMMOND_RTMIDI_BACKEND)
        if(NOT IS_DIRECTORY "${_hammond_standalone_rtmidi_prepared}" OR
           NOT _hammond_standalone_midi_backend MATCHES "^(ALSA|WinMM|CoreMIDI)$")
            message(FATAL_ERROR "Standalone MIDI installation requires the verified prepared source and explicit native backend identity.")
        endif()
        set(_hammond_standalone_rtmidi_lock "${_hammond_standalone_source}/data/dependencies/rtmidi-lock.json")
        file(READ "${_hammond_standalone_rtmidi_lock}" _hammond_standalone_rtmidi_json)
        string(JSON _hammond_standalone_rtmidi_version GET "${_hammond_standalone_rtmidi_json}" version)
        string(JSON _hammond_standalone_rtmidi_commit GET "${_hammond_standalone_rtmidi_json}" commit)
        string(JSON _hammond_standalone_rtmidi_license_hash GET "${_hammond_standalone_rtmidi_json}" license sha256)
        string(JSON _hammond_standalone_rtmidi_patch_id GET "${_hammond_standalone_rtmidi_json}" patch id)
        string(JSON _hammond_standalone_rtmidi_patch_hash GET "${_hammond_standalone_rtmidi_json}" patch sha256)
        string(JSON _hammond_standalone_rtmidi_source_hash GET "${_hammond_standalone_rtmidi_json}" patch prepared_sha256)
        file(SHA256 "${_hammond_standalone_rtmidi_lock}" _hammond_standalone_rtmidi_lock_hash)
        file(SHA256 "${_hammond_standalone_rtmidi_prepared}/prepared-source.json" _hammond_standalone_rtmidi_prepared_hash)
        list(APPEND _hammond_standalone_metadata_sources
            "${_hammond_standalone_rtmidi_prepared}/LICENSE"
            "${_hammond_standalone_rtmidi_lock}"
            "${_hammond_standalone_rtmidi_prepared}/prepared-source.json"
            "${_hammond_standalone_rtmidi_prepared}/rtmidi-coremidi-zero-init.patch")
        list(APPEND _hammond_standalone_metadata_names
            LICENSE-RtMidi.txt rtmidi-lock.json rtmidi-prepared-source.json rtmidi-coremidi-zero-init.patch)
        set(_hammond_standalone_midi_json [=[
    "enabled": true,
    "backend": "@_hammond_standalone_midi_backend@",
    "availability": "Compiled backend only; runtime service, permissions and physical input availability must be checked on the destination system.",
    "rtmidi": {
      "version": "@_hammond_standalone_rtmidi_version@",
      "commit": "@_hammond_standalone_rtmidi_commit@",
      "linkage": "static",
      "lock_sha256": "@_hammond_standalone_rtmidi_lock_hash@",
      "license_sha256": "@_hammond_standalone_rtmidi_license_hash@",
      "prepared_manifest_sha256": "@_hammond_standalone_rtmidi_prepared_hash@",
      "prepared_source_sha256": "@_hammond_standalone_rtmidi_source_hash@",
      "patch_id": "@_hammond_standalone_rtmidi_patch_id@",
      "patch_sha256": "@_hammond_standalone_rtmidi_patch_hash@"
    }]=])
        string(CONFIGURE "${_hammond_standalone_midi_json}" _hammond_standalone_midi_json @ONLY)
    endif()
    # Config-independent metadata records compile-time capability, never a
    # successful device probe. Its contents contain no build/checkout paths.
    set(HAMMOND_STANDALONE_CAPABILITIES "${CMAKE_CURRENT_BINARY_DIR}/generated/standalone-capabilities.json")
    set(_hammond_standalone_capabilities [=[{
  "schema_version": 1,
  "component": "Standalone",
  "midi": {
@_hammond_standalone_midi_json@
  },
  "sdl2": {
    "version": "@_hammond_standalone_sdl_version@",
    "commit": "@_hammond_standalone_sdl_commit@",
    "linkage": "static",
    "lock_sha256": "@_hammond_standalone_lock_hash@",
    "license_sha256": "@_hammond_standalone_sdl_hash@"
  },
  "fonts": {
    "embedded": true,
    "manifest_sha256": "@_hammond_standalone_font_manifest_hash@",
    "license_sha256": "@_hammond_standalone_font_hash@"
  },
  "reference_art": {
    "embedded": true,
    "identity": "@_hammond_standalone_reference_id@",
    "manifest_sha256": "@_hammond_standalone_reference_hash@",
    "provenance_sha256": "@_hammond_standalone_atlas_hash@",
    "source_image_sha256": "@_hammond_standalone_reference_image_hash@",
    "rights_notice": "THIRD_PARTY_NOTICES.md#embedded-reference-decoration"
  },
  "profile": "embedded nominal-unmeasured-v1",
  "qualification": "Local staging metadata; no physical-device, timing, fidelity or release-distribution claim."
}
]=])
    file(CONFIGURE OUTPUT "${HAMMOND_STANDALONE_CAPABILITIES}"
        CONTENT "${_hammond_standalone_capabilities}" @ONLY NEWLINE_STYLE UNIX)
    list(APPEND _hammond_standalone_metadata_sources "${HAMMOND_STANDALONE_CAPABILITIES}")
    list(APPEND _hammond_standalone_metadata_names standalone-capabilities.json)
    set(_hammond_standalone_metadata_hashes)
    list(LENGTH _hammond_standalone_metadata_sources _hammond_standalone_metadata_count)
    math(EXPR _hammond_standalone_metadata_last "${_hammond_standalone_metadata_count} - 1")
    foreach(_hammond_standalone_index RANGE ${_hammond_standalone_metadata_last})
        list(GET _hammond_standalone_metadata_sources ${_hammond_standalone_index} _hammond_standalone_input)
        list(GET _hammond_standalone_metadata_names ${_hammond_standalone_index} _hammond_standalone_name)
        file(SHA256 "${_hammond_standalone_input}" _hammond_standalone_hash)
        # License/correction bytes must satisfy their reviewed identities even
        # if an inconsistent source copy was present at configure time.
        if(_hammond_standalone_name STREQUAL "LICENSE-SDL2.txt")
            set(_hammond_standalone_hash "${_hammond_standalone_sdl_hash}")
        elseif(_hammond_standalone_name STREQUAL "LICENSE-DejaVu.txt")
            set(_hammond_standalone_hash "${_hammond_standalone_font_hash}")
        elseif(_hammond_standalone_name STREQUAL "LICENSE-RtMidi.txt")
            set(_hammond_standalone_hash "${_hammond_standalone_rtmidi_license_hash}")
        elseif(_hammond_standalone_name STREQUAL "rtmidi-coremidi-zero-init.patch")
            set(_hammond_standalone_hash "${_hammond_standalone_rtmidi_patch_hash}")
        endif()
        list(APPEND _hammond_standalone_metadata_hashes "${_hammond_standalone_hash}")
    endforeach()
    set_property(DIRECTORY APPEND PROPERTY CMAKE_CONFIGURE_DEPENDS ${_hammond_standalone_metadata_sources})

    set(_hammond_standalone_preflight [=[
        if(DEFINED ENV{CMAKE_INSTALL_MODE} AND NOT "$ENV{CMAKE_INSTALL_MODE}" STREQUAL "" AND
           NOT "$ENV{CMAKE_INSTALL_MODE}" STREQUAL "COPY")
            message(FATAL_ERROR "Standalone requires CMAKE_INSTALL_MODE=COPY (or unset) for relocation.")
        endif()
        set(_hammond_standalone_inputs
            "$<TARGET_FILE:hammond_standalone>"
            @_hammond_standalone_preflight_sources@)
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

inputs = [Path(value) for value in sys.argv[1:-2]]
expected_hashes = "@_hammond_standalone_metadata_hashes@".split(";")
if len(inputs) != len(expected_hashes) + 1:
    reject("invalid configured input inventory")
for index, path in enumerate(inputs):
    try:
        info = path.lstat()
    except OSError as error:
        reject(f"missing or unreadable required input '{path}': {error}; build hammond_standalone for the selected configuration before installing.")
    if not stat.S_ISREG(info.st_mode):
        reject(f"requires a regular input without symlinks: '{path}'")
    if info.st_size == 0:
        reject(f"required input is empty: '{path}'")
    digest = hashlib.sha256()
    try:
        with path.open("rb") as stream:
            while chunk := stream.read(1024 * 1024):
                digest.update(chunk)
    except OSError as error:
        reject(f"missing or unreadable required input '{path}': {error}")
    if index and digest.hexdigest() != expected_hashes[index - 1]:
        reject(f"configured notice/identity mismatch: '{path}'; reconfigure after an intentional input change.")
binary, metadata = [Path(value) for value in sys.argv[-2:]]
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
    set(_hammond_standalone_preflight_sources "")
    foreach(_hammond_standalone_input IN LISTS _hammond_standalone_metadata_sources)
        string(APPEND _hammond_standalone_preflight_sources "\"${_hammond_standalone_input}\"\n            ")
    endforeach()
    string(CONFIGURE "${_hammond_standalone_preflight}" _hammond_standalone_preflight @ONLY)
    install(CODE "${_hammond_standalone_preflight}" COMPONENT Standalone EXCLUDE_FROM_ALL)
    # PROGRAMS preserves the selected binary bytes instead of changing an RPATH
    # or stripping. This local payload does not collect platform runtime DLLs.
    install(PROGRAMS "$<TARGET_FILE:hammond_standalone>"
        DESTINATION "${CMAKE_INSTALL_BINDIR}" COMPONENT Standalone EXCLUDE_FROM_ALL)
    foreach(_hammond_standalone_index RANGE ${_hammond_standalone_metadata_last})
        list(GET _hammond_standalone_metadata_sources ${_hammond_standalone_index} _hammond_standalone_input)
        list(GET _hammond_standalone_metadata_names ${_hammond_standalone_index} _hammond_standalone_name)
        install(FILES "${_hammond_standalone_input}" RENAME "${_hammond_standalone_name}"
            DESTINATION "${_hammond_standalone_data}" COMPONENT Standalone EXCLUDE_FROM_ALL)
    endforeach()
endif()
