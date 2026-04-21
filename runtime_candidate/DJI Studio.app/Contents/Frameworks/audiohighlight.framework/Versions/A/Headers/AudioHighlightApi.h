#pragma once


#import <Foundation/Foundation.h>
#if TARGET_OS_IPHONE
#import <UIKit/UIImage.h>
#else
#import <AppKit/AppKit.h>
typedef NSImage UIImage;
#endif
#include <string>




using AudioHighlightInitInfo =  struct _AudioHighlightInitInfo
{
    NSString* model_dir;      // 模型所在的目录
};

using AudioHighlightRtInfo =  struct _AudioHighlightRtInfo
{ // 算法运行时参数
    const int16_t *data_in_buff; // 输入音频数据
    size_t data_in_len;          // 输入音频数据长度(必须为 AH_FRAME_LEN)
    float *data_out_buff;        // 输出特征数据
    size_t data_out_len;         // 输出特征数据长度(必须为 AH_FEATURE_NUMS)
};




@interface AudioHighlighter:NSObject{
}


- (instancetype)init NS_UNAVAILABLE;

- (instancetype)initAudioHighlight:(AudioHighlightInitInfo*)initInfo;

- (void) AudioHighlightProcess:(AudioHighlightRtInfo*)rtInfo;

- (void) getDebugAudioHighlight:(AudioHighlightRtInfo*)rtInfo;

- (void)AudioHighlightReset;

- (NSString*)AudioHighlightGetVersion;

@end
