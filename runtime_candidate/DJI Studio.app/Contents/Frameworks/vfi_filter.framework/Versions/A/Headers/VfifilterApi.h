
#pragma once


#import <Foundation/Foundation.h>
#if TARGET_OS_IPHONE
#import <UIKit/UIImage.h>
#else
#import <AppKit/AppKit.h>
typedef NSImage UIImage;
#endif
#import <Metal/Metal.h>
#import <simd/simd.h>
#import <Accelerate/Accelerate.h>
#include <string>
#import <MetalKit/MetalKit.h>



typedef struct _VfiSetupInfo
{
    id<MTLDevice> mtl_device;
    id<MTLCommandQueue> mtl_cmd_queue;
    MTLPixelFormat mtl_pixel_format = MTLPixelFormatBGRA8Unorm;
    int src_width;
    int src_height;
    int flow_width;
    int flow_height;
    bool use_10bit;
    bool use_fp16; //model
    const char *model_path;

}VfiSetupInfo;

typedef struct _VfiProcessInfo
{

    float timeStep;

}VfiProcessInfo;


@interface VfiFilter:NSObject{
}

- (instancetype)init NS_UNAVAILABLE;

- (instancetype)initWithVfiInfo:(VfiSetupInfo*)setup_info_ptr;

+ (bool) VfiLoadModelForAPPBoot:(const char *)model_path;

- (void) VfiFilterProcess:(id<MTLTexture>)frame00
                    src01:(id<MTLTexture>)frame01
                   output:(id<MTLTexture>)dstTex
              processinfo:(VfiProcessInfo)info;

#if TARGET_OS_IPHONE
- (UIImage*) getDebug:(id<MTLTexture>)frame00 src01:(id<MTLTexture>)frame01 processinfo:(VfiProcessInfo)info;
#else
- (NSImage*) getDebug:(id<MTLTexture>)frame00 src01:(id<MTLTexture>)frame01 processinfo:(VfiProcessInfo)info;
#endif

@end
