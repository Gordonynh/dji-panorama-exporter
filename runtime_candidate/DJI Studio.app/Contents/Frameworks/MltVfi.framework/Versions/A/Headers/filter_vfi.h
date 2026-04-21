//
//  filter_vfi.h
//  MltVfi
//
//  Created by jasper.chen on 2026/1/8.
//

#ifndef filter_vfi_h
#define filter_vfi_h

#ifdef __cplusplus
extern "C" {
#endif
#include <MKMediaEditor/MltTypes.h>
#ifdef __cplusplus
}
#endif

#include <MltVfi/vfi_defs.h>

VFI_EXTERN void mlt_vfi_register(void);

VFI_EXTERN int mlt_vfi_load_model_for_app_boot(void);

// MARK: -

NAMESPACE_VFI_BEGIN

constexpr double InterpolationFactorToSpeed(InterpolationFactor interpolation_factor) {
    return 1.0 / static_cast<double>(interpolation_factor);
}

constexpr double CalculateVfiTransitionOutputDuration(TransitionType transition_type) {
    double output_duration = 0.0;
    switch (transition_type) {
        case TransitionType::DefaultOneOverThreeSeconds:
            output_duration = 1.0 / 3;
            break;
        case TransitionType::DefaultOneOverTwoSeconds:
            output_duration = 1.0 / 2;
            break;
        case TransitionType::DefaultOneSecond:
            output_duration = 1.0;
            break;
        default:
            break;
    }
    return output_duration;
}

mlt_position CalculateVfiTransitionOriginalLength(mlt_producer producer, InterpolationFactor interpolation_factor, TransitionType transition_type);

NAMESPACE_VFI_END

#endif /* filter_vfi_h */
