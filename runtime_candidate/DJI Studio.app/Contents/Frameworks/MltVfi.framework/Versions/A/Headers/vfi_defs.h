//
//  vfi_defs.h
//  MltVfi
//
//  Created by jasper.chen on 2026/1/8.
//

#ifndef vfi_defs_h
#define vfi_defs_h

#include <cstdint>

// MARK: - Macros

#ifdef __cplusplus
#define VFI_EXTERN extern "C"
#else
#define VFI_EXTERN extern
#endif

#define NAMESPACE_VFI_BEGIN namespace Mlt { namespace Vfi {
#define NAMESPACE_VFI_END   } }

#define USING_NAMESPACE_VFI using namespace Mlt::Vfi;

NAMESPACE_VFI_BEGIN

// MARK: - Constants

VFI_EXTERN const char* const kFilterId;

// MARK: - Enums

enum class InterpolationFactor : uint8_t
{
	None = 1,
	X2   = 2,
	X4   = 4,
	X8   = 8,
};

enum class TransitionType : uint8_t
{
	None = 0,
	DefaultOneOverThreeSeconds,
	DefaultOneOverTwoSeconds,
	DefaultOneSecond,
};

NAMESPACE_VFI_END

#endif /* vfi_defs_h */
