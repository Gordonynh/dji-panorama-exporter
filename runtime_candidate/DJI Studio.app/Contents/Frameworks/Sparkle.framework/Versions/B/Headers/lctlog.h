//
//  lctlog.h
//  Sparkle
//
//  Callback-based logging, modeled after WinSparkle's lctLog.
//  日志级别：0=调试，1=警告，2=错误，3=致命，4=信息
//

#ifndef LCTLOG_H
#define LCTLOG_H

#include <stdarg.h>

#ifdef __cplusplus
extern "C" {
#endif

// Callback type: receives level, format string, and va_list (matches WinSparkle convention).
typedef void (*lct_log_cb)(int level, const char *format, va_list args);

// Register a log callback. Pass NULL to disable logging.
void lct_set_log_callback(lct_log_cb cb) __attribute__((visibility("default")));
lct_log_cb lct_get_log_callback(void) __attribute__((visibility("hidden")));

#ifdef __cplusplus
}
#endif

#endif // LCTLOG_H
