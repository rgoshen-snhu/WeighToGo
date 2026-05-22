# Phase 7: SMS Notifications - Manual Testing Guide

**Version:** 1.0
**Date:** 2025-12-12
**Branch:** `feature/FR7.0-sms-notifications`
**Status:** Ready for manual testing

---

## Table of Contents

1. [Overview](#overview)
2. [Testing Prerequisites](#testing-prerequisites)
3. [Physical Device Testing (Recommended)](#physical-device-testing-recommended)
4. [Emulator Testing (Limited)](#emulator-testing-limited)
5. [Manual Testing Checklists](#manual-testing-checklists)
6. [Debugging & Troubleshooting](#debugging--troubleshooting)
7. [Known Limitations](#known-limitations)

---

## Overview

Phase 7 implements SMS notifications for the WeightToGo app, including:
- SMS permission management (SEND_SMS + POST_NOTIFICATIONS)
- Phone number validation and storage (E.164 format)
- Achievement-based SMS alerts (goal reached, milestones, streaks)
- Daily reminder SMS (scheduled via WorkManager)
- User preference controls (master toggle, alert types, reminder toggle)

**IMPORTANT:** Full SMS testing requires a **physical Android device with cellular service**. Emulator testing is limited to UI/validation/permissions only.

---

## Testing Prerequisites

### Hardware Requirements
- **Physical Android device** (Android 8.0+ / API 28+)
- **Active cellular service** with SMS capability
- **USB cable** for device connection
- **Computer** with Android Studio installed

### Software Requirements
- Android Studio Arctic Fox or later
- ADB (Android Debug Bridge) installed
- USB debugging enabled on device

### Device Setup
1. Enable Developer Options:
   ```
   Settings → About Phone → Tap "Build Number" 7 times
   ```

2. Enable USB Debugging:
   ```
   Settings → Developer Options → USB Debugging → ON
   ```

3. Connect device via USB and authorize computer

4. Verify device connection:
   ```bash
   adb devices
   # Should show: <device-id>    device
   ```

### Test Phone Number
- You'll need a phone number to receive test SMS
- Recommended: Use your own phone number during testing
- Format: 10-digit US number (e.g., 2025551234)
- App will format to E.164: +12025551234

---

## Physical Device Testing (Recommended)

This section covers complete end-to-end SMS testing on a real device.

### Step 1: Install App on Device

> **Post-restructure paths:** The Android project lives in the `android/` directory. Run `./gradlew` commands from there (`cd android` first). `adb` commands run from any directory. Debug APK artifacts build to `android/weightogo/build/outputs/apk/debug/weightogo-debug.apk`.

```bash
# Build debug APK
./gradlew assembleDebug

# Install on connected device
adb install -r android/weightogo/build/outputs/apk/debug/weightogo-debug.apk

# Or build and install in one step
./gradlew installDebug
```

### Step 2: Register and Login

1. Launch app on device
2. Register new test user:
   - Username: `smstest_<timestamp>`
   - Email: `smstest@example.com`
   - Password: `Test123!`
3. Login with test credentials

### Step 3: Navigate to Settings

1. From MainActivity, tap **Settings** button (bottom navigation or menu)
2. Verify Settings screen loads

### Step 4: Grant SMS Permissions

**Test Case 4.1: Check Initial Permission Status**
- [ ] Permission Status Badge shows "Required" (red background)
- [ ] "Grant Permissions" button is VISIBLE
- [ ] All SMS toggles are DISABLED (grayed out)

**Test Case 4.2: Request Permissions**
1. Tap "Grant Permissions" button
2. System permission dialog appears
3. Tap "Allow" for SEND_SMS
4. If Android 13+: Tap "Allow" for POST_NOTIFICATIONS

**Expected Results:**
- [ ] Permission Status Badge updates to "Granted" (green background)
- [ ] "Grant Permissions" button becomes HIDDEN
- [ ] All SMS toggles become ENABLED (active)
- [ ] Toast message: "Permissions granted"

**Test Case 4.3: Verify Permission Persistence**
1. Close app completely
2. Reopen app and navigate to Settings
3. Permission Status Badge should still show "Granted"
4. Toggles should still be enabled

### Step 5: Configure Phone Number

**Test Case 5.1: Invalid Phone Number Validation**

Test each invalid input:

| Input | Expected Error |
|-------|----------------|
| (empty) | "Phone number is required" |
| `123` | "Phone number must be at least 10 digits" |
| `12345678901234567` | "Phone number cannot exceed 15 digits" |
| `202-555-1234` | "Phone number can only contain digits and + symbol" |
| `202abc5551234` | "Invalid phone number format. Use 10 digits (e.g., 2025551234)" |

**Test Case 5.2: Valid Phone Number Entry**
1. Enter valid 10-digit phone: `2025551234` (use your actual phone number)
2. Tap keyboard "Done" button or press Enter
3. **Expected Results:**
   - [ ] Toast message: "Phone number saved"
   - [ ] No error shown
   - [ ] Phone number persists in input field

**Test Case 5.3: Phone Number Formatting**
1. Enter phone: `2025551234`
2. Close app and reopen Settings
3. Phone input should show: `2025551234` (display format)
4. Database stores: `+12025551234` (E.164 format)

### Step 6: Enable SMS Notifications

**Test Case 6.1: Master Toggle**
1. Tap "SMS Notifications" master toggle to ON
2. **Expected Results:**
   - [ ] Toggle switches to ON (teal color)
   - [ ] All child toggles (Goal Alerts, Milestone Alerts, Reminders) become ENABLED
   - [ ] Toast: "SMS notifications enabled"
   - [ ] Preference saved to database

**Test Case 6.2: Master Toggle OFF**
1. Tap master toggle to OFF
2. **Expected Results:**
   - [ ] All child toggles become DISABLED (grayed out)
   - [ ] Toast: "SMS notifications disabled"
   - [ ] No SMS should be sent even if achievements occur

**Test Case 6.3: Individual Alert Toggles**

Re-enable master toggle, then test each:

| Toggle | Action | Expected Toast |
|--------|--------|----------------|
| Goal Alerts | ON | "Goal alerts enabled" |
| Goal Alerts | OFF | "Goal alerts disabled" |
| Milestone Alerts | ON | "Milestone alerts enabled" |
| Milestone Alerts | OFF | "Milestone alerts disabled" |
| Daily Reminders | ON | "Daily reminders enabled" + WorkManager scheduled |
| Daily Reminders | OFF | "Daily reminders disabled" + WorkManager cancelled |

**Test Case 6.4: Preference Persistence**
1. Set all toggles to specific states (e.g., Master ON, Goal ON, Milestone OFF, Reminder ON)
2. Close app completely
3. Reopen and navigate to Settings
4. All toggles should retain their previous states

### Step 7: Test Message Verification

**Test Case 7.1: Send Test Message**
1. Ensure master toggle is ON
2. Ensure phone number is configured
3. Tap "Send Test Message" button
4. **Expected Results:**
   - [ ] Toast: "Test message sent!"
   - [ ] SMS received on configured phone number
   - [ ] Message text: "This is a test message from Weigh to Go! Your SMS notifications are working! ✅"

**Test Case 7.2: Test Message Without Phone**
1. Clear phone number from input
2. Tap "Send Test Message"
3. **Expected Result:**
   - [ ] Toast: "No phone number configured"
   - [ ] No SMS sent

**Test Case 7.3: Test Message Without Permission**
1. Revoke SMS permission (Settings → Apps → WeightToGo → Permissions → SMS → Deny)
2. Return to app Settings screen
3. Tap "Send Test Message"
4. **Expected Result:**
   - [ ] Toast: "Cannot send SMS. Check permissions and phone number."
   - [ ] No SMS sent

### Step 8: Achievement SMS Testing

**Prerequisites:**
- Master toggle ON
- Phone number configured
- Goal Alerts toggle ON
- Milestone Alerts toggle ON

**Test Case 8.1: First Entry Achievement**
1. Navigate to MainActivity
2. Tap "Log Weight" button
3. Enter first weight entry for user (e.g., 200.0 lbs)
4. Tap "Save"
5. **Expected Results:**
   - [ ] Entry saved successfully
   - [ ] SMS received: "Welcome to Weigh to Go! You logged your first weight entry! 📊"
   - [ ] Achievement logged in database (type: FIRST_ENTRY)

**Test Case 8.2: Goal Reached Achievement**

Setup:
1. Set goal weight (e.g., 180.0 lbs, goal type: "lose")
2. Log initial weight: 200.0 lbs
3. Log several entries approaching goal

Test:
1. Log weight entry that reaches goal: 180.0 lbs
2. Tap "Save"
3. **Expected Results:**
   - [ ] Entry saved
   - [ ] SMS received: "Congrats! You reached your goal weight of 180.0 lbs! 🎉"
   - [ ] Achievement logged (type: GOAL_REACHED)

**Test Case 8.3: 7-Day Streak Achievement**

Setup:
1. Log weight entries for 7 consecutive days (use date picker if needed)

Test:
1. On 7th consecutive day, log weight entry
2. **Expected Results:**
   - [ ] SMS received: "Amazing! You're on a 7-day logging streak! Keep it up! 🔥"
   - [ ] Achievement logged (type: STREAK_7)

**Test Case 8.4: Milestone Achievements**

Setup:
1. Start weight: 200.0 lbs
2. Goal: 150.0 lbs

Test each milestone:

| Milestone | Current Weight | Expected SMS |
|-----------|----------------|--------------|
| 5 lbs lost | 195.0 lbs | "Great progress! You've lost 5 lbs! 🎯" |
| 10 lbs lost | 190.0 lbs | "Awesome! You've lost 10 lbs! Halfway to your next milestone! 🏆" |
| 25 lbs lost | 175.0 lbs | "WOW! You've lost 25 lbs! That's a major achievement! 🌟" |

**Test Case 8.5: New Low Weight Achievement**
1. Log weight: 200.0 lbs
2. Log weight: 195.0 lbs (new low)
3. **Expected Results:**
   - [ ] SMS received: "New personal best! You hit a new low weight of 195.0 lbs! 🎊"
   - [ ] Achievement logged (type: NEW_LOW)

**Test Case 8.6: Achievement SMS with Alerts Disabled**
1. Turn OFF "Goal Alerts" toggle
2. Reach a goal
3. **Expected Results:**
   - [ ] Achievement logged in database
   - [ ] NO SMS sent
   - [ ] Toast may still show achievement in app

### Step 9: Daily Reminder Testing

**IMPORTANT:** Daily reminders require waiting 24 hours or manipulating system time.

**Test Case 9.1: Schedule Daily Reminder**
1. Navigate to Settings
2. Enable "Daily Reminders" toggle
3. **Expected Results:**
   - [ ] Toast: "Daily reminders enabled"
   - [ ] WorkManager job scheduled (check Logcat: `DailyReminderWorker`)
   - [ ] Next reminder scheduled for 9:00 AM next day

**Test Case 9.2: Reminder Sent (User Hasn't Logged)**
1. Wait until next day at 9:00 AM (or manipulate device time)
2. Ensure user has NOT logged weight today
3. **Expected Results:**
   - [ ] SMS received: "Don't forget to log your weight today! Stay on track with Weigh to Go! ⚖️"
   - [ ] Logcat: "DailyReminderWorker: Daily reminder SMS sent"

**Test Case 9.3: Reminder Skipped (User Already Logged)**
1. Log weight entry for today
2. Wait for scheduled reminder time
3. **Expected Results:**
   - [ ] NO SMS sent
   - [ ] Logcat: "DailyReminderWorker: User already logged weight today, skipping reminder"

**Test Case 9.4: Reminder Disabled**
1. Turn OFF "Daily Reminders" toggle
2. Wait for next scheduled time
3. **Expected Results:**
   - [ ] NO SMS sent
   - [ ] WorkManager job cancelled
   - [ ] Logcat: No DailyReminderWorker execution

**Test Case 9.5: Time Manipulation (Advanced)**

If you need to test without waiting 24 hours:

```bash
# Forward device time to 9:00 AM tomorrow
adb shell su root date 121309002025.00
# Format: MMDDhhmmYYYY.ss (Dec 13, 09:00, 2025)

# Trigger WorkManager to run immediately (if available)
adb shell am broadcast -a androidx.work.impl.background.systemalarm.RescheduleReceiver

# Restore correct time after testing
# Enable automatic time in Settings → Date & Time
```

### Step 10: Permission Denied Scenarios

**Test Case 10.1: Deny Permissions Initially**
1. Fresh install of app
2. Navigate to Settings
3. Tap "Grant Permissions"
4. Tap "Deny" in permission dialog
5. **Expected Results:**
   - [ ] Permission Status Badge shows "Denied" or "Required"
   - [ ] "Grant Permissions" button remains visible
   - [ ] SMS toggles remain disabled
   - [ ] Toast: "SMS permissions required for notifications"

**Test Case 10.2: Revoke Permission After Granting**
1. Grant permissions via Settings
2. Go to device Settings → Apps → WeightToGo → Permissions → SMS → Deny
3. Return to app Settings screen
4. **Expected Results:**
   - [ ] Permission Status Badge updates to "Required"
   - [ ] "Grant Permissions" button reappears
   - [ ] SMS toggles become disabled
   - [ ] Attempting to send SMS shows permission error

**Test Case 10.3: Permanently Deny Permission**
1. Tap "Grant Permissions"
2. Deny permission
3. Tap "Grant Permissions" again
4. Deny and check "Don't ask again"
5. **Expected Results:**
   - [ ] Permission Status Badge shows "Denied"
   - [ ] App should show hint to enable in device Settings
   - [ ] Toast: "Please enable SMS permissions in device Settings"

---

## Emulator Testing (Limited)

**WARNING:** Android emulators **cannot send real SMS** without complex carrier emulation. Use emulators only for UI/validation testing.

### What Can Be Tested
- ✅ Permission request UI flow
- ✅ Phone number validation and error messages
- ✅ Toggle state changes and persistence
- ✅ UI layout and accessibility
- ✅ Database operations (phone storage, preferences)
- ✅ Logcat output for SMS sending attempts

### What Cannot Be Tested
- ❌ Actual SMS delivery
- ❌ SMS receipt verification
- ❌ Carrier-specific behavior
- ❌ SMS delivery timing

### Emulator Testing Procedure

**Step 1: Launch Emulator**
```bash
# Use AVD with Google Play services
# Recommended: Pixel 6 Pro, API 34, x86_64

# Start emulator
emulator -avd Pixel_6_Pro_API_34
```

**Step 2: Install App**
```bash
./gradlew installDebug
```

**Step 3: UI Testing**
1. Follow Steps 2-6 from Physical Device Testing
2. Test permission UI flow
3. Test phone validation with all invalid/valid inputs
4. Test toggle states and persistence

**Step 4: Monitor Logcat for SMS Attempts**
```bash
# Filter for SMS-related logs
adb logcat -s SMSNotificationManager DailyReminderWorker

# Expected output when SMS would be sent:
# I/SMSNotificationManager: sendGoalAchievedSms: Sending SMS to +12025551234
# I/SMSNotificationManager: SMS sent successfully
```

**Step 5: Verify Database**
```bash
# Pull database from emulator
adb pull /data/data/com.example.weightogo/databases/weigh_to_go.db

# Open with SQLite browser to verify:
# - Phone number stored in E.164 format
# - Preferences saved correctly
# - Achievements logged (even if SMS not sent)
```

---

## Manual Testing Checklists

### Settings Screen Checklist

Permission Flow:
- [ ] Initial status shows "Required"
- [ ] Grant button visible when permissions denied
- [ ] Grant button launches system permission dialog
- [ ] Status updates to "Granted" after approval
- [ ] Grant button hidden when permissions granted
- [ ] Status persists after app restart

Phone Number:
- [ ] Empty input shows required error
- [ ] Input validates all error cases (see Test Case 5.1)
- [ ] Valid 10-digit number saves successfully
- [ ] Phone formatted to E.164 in database
- [ ] Phone persists after app restart

SMS Toggles:
- [ ] Master toggle enables/disables all child toggles
- [ ] Goal Alerts toggle saves preference
- [ ] Milestone Alerts toggle saves preference
- [ ] Daily Reminders toggle schedules/cancels WorkManager
- [ ] All toggles persist after app restart
- [ ] Toggles disabled when permissions not granted
- [ ] Toggles show appropriate toast messages

Test Message:
- [ ] Button sends SMS when conditions met
- [ ] Shows error when phone not configured
- [ ] Shows error when permissions denied
- [ ] Actual SMS received on configured number

### Achievement SMS Checklist

First Entry:
- [ ] SMS sent on very first weight entry
- [ ] Message: "Welcome to Weigh to Go! You logged your first weight entry! 📊"
- [ ] Achievement logged with correct timestamp

Goal Reached:
- [ ] SMS sent when goal weight reached
- [ ] Message includes goal weight and unit
- [ ] Not sent if Goal Alerts toggle OFF

Streaks:
- [ ] 7-day streak detected and SMS sent
- [ ] 30-day streak detected and SMS sent
- [ ] Consecutive days required (no gaps)

Milestones:
- [ ] 5 lbs lost triggers SMS
- [ ] 10 lbs lost triggers SMS
- [ ] 25 lbs lost triggers SMS
- [ ] Not sent if Milestone Alerts toggle OFF

New Low:
- [ ] SMS sent when new low weight achieved
- [ ] Message includes new weight value

General:
- [ ] SMS not sent if master toggle OFF
- [ ] SMS not sent if permissions denied
- [ ] SMS not sent if phone number not configured
- [ ] Multiple achievements in one entry send multiple SMS
- [ ] Achievements marked as notified in database

### Daily Reminder Checklist

Setup:
- [ ] Toggle ON schedules WorkManager job
- [ ] Toggle OFF cancels WorkManager job
- [ ] Scheduled for 9:00 AM daily
- [ ] Constraints: battery not low

Behavior:
- [ ] SMS sent if user hasn't logged today
- [ ] SMS NOT sent if user already logged today
- [ ] SMS NOT sent if reminder toggle OFF
- [ ] SMS NOT sent if master toggle OFF
- [ ] SMS NOT sent if permissions denied

Persistence:
- [ ] Reminder continues after app restart
- [ ] Reminder continues after device reboot
- [ ] Reminder state persists in user preferences

---

## Debugging & Troubleshooting

### Logcat Filtering

Monitor SMS activity in real-time:

```bash
# General SMS logging
adb logcat -s SMSNotificationManager

# Achievement integration
adb logcat -s AchievementManager WeightEntryActivity

# Daily reminders
adb logcat -s DailyReminderWorker

# Permission changes
adb logcat -s SettingsActivity

# All WeightToGo logs
adb logcat | grep "com.example.weightogo"
```

### Common Issues

#### Issue: SMS Not Received

**Symptoms:** App logs "SMS sent successfully" but no SMS received

**Possible Causes:**
1. **Carrier delay** - SMS can take 1-5 minutes
2. **Wrong phone number** - Verify E.164 format in database
3. **Carrier blocking** - Some carriers block app-originated SMS
4. **Device SMS limits** - Android limits SMS per hour

**Debug Steps:**
```bash
# Check phone number in database
adb shell "run-as com.example.weightogo cat databases/weigh_to_go.db" | strings | grep "+1"

# Verify SMS permission
adb shell dumpsys package com.example.weightogo | grep SEND_SMS

# Check SmsManager logs
adb logcat -s SmsManager
```

#### Issue: Permission Not Granted

**Symptoms:** Permission dialog appears but app still shows "Required"

**Debug Steps:**
1. Check Logcat for permission result:
   ```bash
   adb logcat -s SettingsActivity | grep "permission"
   ```

2. Verify permission in system:
   ```bash
   adb shell dumpsys package com.example.weightogo | grep "android.permission.SEND_SMS"
   # Should show: granted=true
   ```

3. Clear app data and retry:
   ```bash
   adb shell pm clear com.example.weightogo
   ```

#### Issue: Daily Reminder Not Firing

**Symptoms:** Reminder toggle ON but no SMS at 9:00 AM

**Debug Steps:**
1. Check WorkManager status:
   ```bash
   adb shell dumpsys jobscheduler | grep "com.example.weightogo"
   ```

2. Verify reminder preference:
   ```bash
   adb shell "run-as com.example.weightogo cat databases/weigh_to_go.db" | strings | grep "sms_reminder_enabled"
   # Should show: sms_reminder_enabled|true
   ```

3. Force WorkManager execution (requires debug build):
   ```bash
   # Trigger WorkManager test mode
   adb shell am broadcast -a androidx.work.impl.background.systemalarm.RescheduleReceiver
   ```

4. Check DailyReminderWorker logs:
   ```bash
   adb logcat -s DailyReminderWorker
   # Should see: "doWork: Daily reminder worker started"
   ```

#### Issue: Toggles Not Persisting

**Symptoms:** Toggle states reset after app restart

**Debug Steps:**
1. Verify UserPreferenceDAO saves:
   ```bash
   adb logcat -s UserPreferenceDAO | grep "setPreference"
   # Should see: "Successfully saved preference: sms_notifications_enabled"
   ```

2. Check database writes:
   ```bash
   adb shell "run-as com.example.weightogo cat databases/weigh_to_go.db" | strings | grep "sms_"
   ```

3. Verify SessionManager has valid userId:
   ```bash
   adb logcat -s SessionManager | grep "getCurrentUserId"
   # Should NOT return -1
   ```

#### Issue: Achievement SMS Not Sent

**Symptoms:** Achievement logged but no SMS received

**Debug Steps:**
1. Verify AchievementManager integration:
   ```bash
   adb logcat -s WeightEntryActivity | grep "Achievement"
   # Should see: "Achievement SMS sent: GOAL_REACHED"
   ```

2. Check SMS manager conditions:
   ```bash
   adb logcat -s SMSNotificationManager | grep "canSendSms"
   # Should return true
   ```

3. Verify preference toggles:
   ```bash
   adb shell "run-as com.example.weightogo cat databases/weigh_to_go.db" | strings | grep "sms_goal_alerts"
   # Should show: sms_goal_alerts|true
   ```

### Performance Monitoring

Check SMS sending performance:

```bash
# Monitor SMS sending time
adb logcat -v time -s SMSNotificationManager | grep "sendGoalAchievedSms"

# Expected output:
# 12-12 09:15:30.123 I/SMSNotificationManager: sendGoalAchievedSms: Sending SMS to +12025551234
# 12-12 09:15:30.456 I/SMSNotificationManager: SMS sent successfully
# Time difference should be < 500ms
```

### Database Inspection

Pull and inspect database for debugging:

```bash
# Pull database
adb pull /data/data/com.example.weightogo/databases/weigh_to_go.db

# Open with sqlite3
sqlite3 weigh_to_go.db

# Check phone numbers
SELECT user_id, phone_number FROM users WHERE phone_number IS NOT NULL;

# Check preferences
SELECT user_id, preference_key, preference_value
FROM user_preferences
WHERE preference_key LIKE 'sms%';

# Check achievements
SELECT user_id, achievement_type, notified, achieved_at
FROM achievements
ORDER BY achieved_at DESC
LIMIT 10;
```

---

## Known Limitations

### Robolectric Testing Limitations
- **Issue:** 3 SMS tests fail with Robolectric due to SmsManager mocking limitations
- **Files Affected:** `SMSNotificationManagerTest.java`, `DailyReminderWorkerTest.java`
- **Workaround:** Manual testing required for actual SMS delivery
- **Status:** Expected failures documented in test output

### Material3 Incompatibility
- **Issue:** 25 SettingsActivity tests @Ignored due to Robolectric/Material3 theme incompatibility
- **GitHub Issue:** #12
- **Resolution:** Will migrate to Espresso instrumented tests in Phase 8.4
- **Workaround:** Manual testing covers SettingsActivity functionality

### Android Version Differences
- **Android 13+ (API 33+):** Requires POST_NOTIFICATIONS permission for SMS delivery
- **Android 12 and below:** Only SEND_SMS permission required
- **Testing:** Ensure both permission types are granted on Android 13+ devices

### SMS Delivery Timing
- **Carrier delays:** SMS may take 1-5 minutes to deliver
- **Rate limiting:** Android limits SMS to prevent spam (varies by device/carrier)
- **Background restrictions:** Daily reminders may be delayed if device in battery saver mode

### Emulator Limitations
- **Cannot send real SMS:** Emulators lack cellular modem
- **SmsManager returns success:** Even though no SMS sent
- **Testing scope:** Limited to UI, validation, database operations

### WorkManager Execution Timing
- **Scheduled time:** 9:00 AM is target, but may execute ±15 minutes
- **Flex interval:** 1-hour flex interval allows Android to optimize battery
- **Constraints:** May delay if battery low or device not idle
- **Testing:** Time manipulation may not reliably trigger WorkManager

---

## Testing Sign-off

### Required Testing Completion

Before merging Phase 7 to main, complete all checklists:

**Settings Screen:**
- [ ] All permission flows tested and passing
- [ ] All phone validation scenarios tested
- [ ] All toggle behaviors tested and persisting
- [ ] Test message successfully delivered

**Achievement SMS:**
- [ ] First entry SMS verified
- [ ] Goal reached SMS verified
- [ ] At least one streak SMS verified
- [ ] At least one milestone SMS verified
- [ ] New low SMS verified
- [ ] Alert toggles correctly enable/disable SMS

**Daily Reminders:**
- [ ] Reminder successfully scheduled
- [ ] Reminder sent when user hasn't logged
- [ ] Reminder skipped when user already logged
- [ ] Reminder respects toggle state

**Edge Cases:**
- [ ] Permission denied handling verified
- [ ] Master toggle OFF prevents all SMS
- [ ] No phone number shows appropriate error
- [ ] Multiple achievements send multiple SMS

### Testing Notes

Document any issues found during manual testing:

```
Issue: [Description]
Steps to Reproduce: [1, 2, 3...]
Expected: [What should happen]
Actual: [What actually happened]
Device: [Make/Model, Android version]
Severity: [Critical | High | Medium | Low]
Status: [Fixed | Known Issue | Wont Fix]
```

---

## Additional Resources

- **Architecture Doc:** `docs/architecture/WeighToGo_Database_Architecture.md`
- **SMSNotificationManager:** `android/weightogo/src/main/java/com/example/weightogo/utils/SMSNotificationManager.java`
- **DailyReminderWorker:** `android/weightogo/src/main/java/com/example/weightogo/workers/DailyReminderWorker.java`
- **SettingsActivity:** `android/weightogo/src/main/java/com/example/weightogo/activities/SettingsActivity.java`

---

## Contact & Support

For issues or questions during testing:
1. Check Logcat output for error details
2. Verify all prerequisites are met
3. Consult troubleshooting section above
4. Document issue in Testing Notes section
5. Create GitHub issue if bug found

---

**Last Updated:** 2025-12-12
**Testing Status:** Ready for manual validation