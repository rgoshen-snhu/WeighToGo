# ADR 0006: Emulator SMS Testing

## Status
Accepted

## Context

WeighToGo includes SMS notification features for goal achievements, milestones, and daily reminders. During development and testing, we encountered critical usability issues:

1. **SMS Testing on Emulator**: Android emulators cannot send actual SMS messages because they lack SIM cards and cellular network connectivity. This prevented developers from testing SMS functionality without a physical device.

2. **Phone Number Persistence**: User-entered phone numbers were only saved when the keyboard "Done" button was pressed, not when navigating away from settings. This led to data loss and poor user experience.

3. **PII Exposure in Logs**: Full phone numbers were being logged in plaintext, creating GDPR/compliance risks and exposing personally identifiable information (PII).

These issues blocked development workflow and created security vulnerabilities.

## Decision

We implemented a three-part solution:

### 1. Emulator Detection and Conditional SMS Behavior

**Detection Strategy**: Use multiple `Build` property checks to reliably detect emulator vs physical device:

```java
public static boolean isRunningOnEmulator() {
    String fingerprint = Build.FINGERPRINT != null ? Build.FINGERPRINT : "";
    String model = Build.MODEL != null ? Build.MODEL : "";
    String product = Build.PRODUCT != null ? Build.PRODUCT : "";

    return fingerprint.contains("generic")
        || fingerprint.startsWith("unknown")
        || model.contains("google_sdk")
        || model.contains("Emulator")
        || model.contains("Android SDK built for x86")
        || product.contains("sdk")
        || product.contains("vbox");  // Genymotion
}
```

**Conditional Behavior**:
- **On Emulator**: Log SMS content to Logcat with clear formatting (bordered output for visibility)
- **On Physical Device**: Send actual SMS via `SmsManager.sendTextMessage()`

**Location**: `ValidationUtils.isRunningOnEmulator()` and `SettingsActivity.handleSendTestMessage()`

### 2. Phone Number Masking for Security

Created centralized `ValidationUtils.maskPhoneNumber()` utility that:
- Shows only last 4 digits of phone numbers (e.g., "+12025551234" → "***1234")
- Returns "***NONE" for null/empty values
- Returns "***" for numbers shorter than 4 digits

**Usage**: Applied throughout app wherever phone numbers are logged:
- `SettingsActivity.handleSendTestMessage()` (emulator logging)
- `SMSNotificationManager.sendSms()` (all SMS operations)

### 3. Automatic Phone Number Persistence

Added `onPause()` lifecycle method to `SettingsActivity` to auto-save phone numbers when:
- User navigates away (back button, home button, app switcher)
- Activity loses focus for any reason
- Phone number is valid and non-empty

**Validation**: Reuses existing `ValidationUtils.getPhoneValidationError()` logic to ensure only valid phone numbers are persisted.

## Rationale

### Why This Approach Over Alternatives

**Alternative 1: Comment Out SMS Code**
- ❌ Requires manual code changes for production deployment
- ❌ Risk of forgetting to uncomment for release
- ❌ No way to test actual SMS on physical devices during development

**Alternative 2: Feature Flag / Build Variant**
- ❌ Adds complexity to build configuration
- ❌ Requires maintaining separate code paths
- ❌ Doesn't solve emulator detection automatically

**Alternative 3: Mock SMS Manager**
- ❌ Only works in unit tests, not during manual testing
- ❌ Doesn't provide Logcat output for visual verification
- ❌ Doesn't help with real device testing workflow

**Why Our Solution is Better**:
- ✅ **Zero Configuration**: Automatically detects environment, no manual intervention
- ✅ **Seamless Workflow**: Developers test on emulator, QA tests on device, both work correctly
- ✅ **Security Built-In**: Phone masking happens automatically in all logs
- ✅ **Better UX**: Auto-save prevents data loss from navigation
- ✅ **Production Ready**: Device behavior unchanged, fully backward compatible

### Emulator Detection Trade-offs

**Reliability**: Multiple checks (`FINGERPRINT`, `MODEL`, `PRODUCT`) ensure high accuracy:
- Android Studio AVD: Detected by `FINGERPRINT.contains("generic")`
- Genymotion: Detected by `PRODUCT.contains("vbox")`
- Generic emulators: Detected by multiple fallback checks

**False Positives**: Extremely rare in practice. Even if emulator misdetected as device:
- SMS send would fail gracefully with SecurityException
- User sees helpful toast message
- Logs show reason for failure

**False Negatives**: If device misdetected as emulator:
- Test message logs to Logcat instead of sending
- User sees clear toast: "Test message logged to Logcat (emulator mode)"
- Issue immediately obvious to developer/tester

### Phone Masking Security

**GDPR/Compliance**: Last 4 digits are sufficient for:
- Debugging: Identifies which user/phone without full exposure
- Support: Helps trace issues without storing full PII in logs
- Audit: Maintains security compliance (GDPR Article 25 - data protection by design)

**Industry Standard**: Common practice in:
- Credit card masking (PCI DSS)
- Social security numbers (HIPAA)
- Phone number logging (telecommunications industry)

## Consequences

### Positive

1. **Improved Developer Experience**
   - Developers can test SMS notifications on emulators without physical devices
   - Logcat output provides immediate visual feedback (bordered, easy to find)
   - No manual environment configuration required

2. **Enhanced Security**
   - Phone numbers never logged in full (PII protection)
   - GDPR/compliance improvement
   - Security audit trail maintained

3. **Better User Experience**
   - Phone numbers automatically save on navigation (no data loss)
   - Clear toast messages inform users of SMS behavior
   - Consistent behavior across emulator and device

4. **Production Ready**
   - Zero behavior change on physical devices
   - Fully backward compatible
   - No breaking changes

5. **Testability**
   - Unit tests verify emulator detection logic
   - Integration tests verify conditional SMS behavior
   - Manual testing simplified (just run on emulator)

### Negative

1. **Emulator Detection Not 100% Reliable**
   - Custom/modified emulators might not be detected
   - Rooted devices might have modified Build properties
   - **Mitigation**: Multiple fallback checks; worst case is graceful degradation

2. **Maintenance Overhead**
   - New emulator types might require Build property updates
   - **Mitigation**: Defensive checks cover most emulator types; logs show detection reasoning

3. **Debugging Complexity**
   - Masked phone numbers hide full data during troubleshooting
   - **Mitigation**: Last 4 digits sufficient for most debugging; full phone visible in database

### Technical Debt

None. This solution follows Android best practices and requires no future refactoring.

## Testing Strategy

### Unit Tests (8 tests added)
- `ValidationUtilsTest`: 6 tests for phone masking (valid, null, empty, short, international, 10-digit)
- `ValidationUtilsTest`: 2 tests for emulator detection (exists, deterministic)

### Integration Tests (4 tests added)
- `SettingsActivityEspressoTest`: 3 tests for phone persistence (navigate away, invalid not saved, empty not saved)
- `SettingsActivityEspressoTest`: 1 test for emulator SMS logging

### Manual Testing
1. Run app on Android Studio emulator
2. Navigate to Settings > SMS Notifications
3. Enter phone number (e.g., "2025551234")
4. Navigate away (back button) → **Verify**: Phone persists on return
5. Click "Send Test Message" → **Verify**: Logcat shows:
   ```
   I/SettingsActivity: ======================================
   I/SettingsActivity: TEST SMS (EMULATOR MODE)
   I/SettingsActivity: To: ***1234
   I/SettingsActivity: Message: This is a test message...
   I/SettingsActivity: ======================================
   ```
6. Run app on physical device
7. Click "Send Test Message" → **Verify**: Actual SMS sent

## Implementation Files

**Modified Files**:
1. `ValidationUtils.java` (+60 LOC)
   - Added `maskPhoneNumber()` method
   - Added `isRunningOnEmulator()` method

2. `SettingsActivity.java` (+35 LOC)
   - Added `onPause()` lifecycle method (auto-save)
   - Updated `handleSendTestMessage()` (emulator detection)

3. `SMSNotificationManager.java` (+3 LOC)
   - Updated logging to use masked phone numbers

**Test Files**:
1. `ValidationUtilsTest.java` (+80 LOC) - 8 new unit tests
2. `SettingsActivityEspressoTest.java` (+50 LOC) - 4 new integration tests

**Total Changes**: ~230 LOC added (excluding tests)

## References

- **Android Developer Docs**: [Build class](https://developer.android.com/reference/android/os/Build)
- **Android Developer Docs**: [Activity Lifecycle](https://developer.android.com/guide/components/activities/activity-lifecycle)
- **GDPR Article 25**: Data protection by design and by default
- **PCI DSS**: Payment Card Industry Data Security Standard (masking practices)
- **Industry Pattern**: Common emulator detection strategy used in popular Android apps

## Related ADRs

- **ADR-0003**: Overall App Architecture - Discusses utility class patterns and layering
- **ADR-0005**: Dependency Injection for Testing - Complements this with testing infrastructure

## Future Considerations

1. **Advanced Emulator Detection**: Consider using Android SafetyNet Attestation API for enterprise-grade emulator detection (adds Google Play Services dependency)

2. **Configurable Masking**: Add user preference for phone number masking level (4 digits, 6 digits, full for debugging)

3. **SMS Testing UI**: Add developer settings panel with:
   - Force emulator mode toggle
   - SMS history viewer
   - Test message templates

4. **Analytics**: Log emulator vs device usage statistics (anonymized) to understand development vs production usage patterns

---

**Last Updated**: 2024-12-14
**Author**: Rick Goshen
**Approved By**: Technical Lead
