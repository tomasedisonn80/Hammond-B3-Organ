#include "Controller.h"
#include "PluginIds.h"
#include "Processor.h"

#include "pluginterfaces/vst/ivstaudioprocessor.h"
#include "public.sdk/source/main/pluginfactory.h"

// No fabricated contact address or SDK sample identity. This factory exposes
// exactly the nominal processor and its generic host-control component.
BEGIN_FACTORY(hammond::vst3::kPluginVendor, hammond::vst3::kPluginUrl, "",
              Steinberg::PFactoryInfo::kUnicode)

DEF_CLASS2(INLINE_UID_FROM_FUID(hammond::vst3::kProcessorClassId),
           Steinberg::PClassInfo::kManyInstances, kVstAudioEffectClass,
           hammond::vst3::kPluginName, Steinberg::Vst::kDistributable,
           Steinberg::Vst::PlugType::kInstrumentSynth, hammond::vst3::kPluginVersion,
           kVstVersionString, hammond::vst3::Processor::createInstance)

DEF_CLASS2(INLINE_UID_FROM_FUID(hammond::vst3::kControllerClassId),
           Steinberg::PClassInfo::kManyInstances, kVstComponentControllerClass,
           "Hammond B3 Nominal Controller", 0, "", hammond::vst3::kPluginVersion,
           kVstVersionString, hammond::vst3::Controller::createInstance)

END_FACTORY
