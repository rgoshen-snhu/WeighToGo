# WeightToGo - Test Scenario Setup Guide

**Phase 9.6: Manual Testing Setup & Helpers**
**Purpose**: Provide commands, scripts, and helpers to efficiently execute manual testing scenarios
**Companion Document**: `Manual_Testing_Checklist.md`

---

## Table of Contents
1. [Device Setup & Management](#device-setup--management)
2. [Test Data Generation](#test-data-generation)
3. [Database Inspection](#database-inspection)
4. [App State Management](#app-state-management)
5. [Quick Test Scenarios](#quick-test-scenarios)
6. [Debugging Helpers](#debugging-helpers)

---

## Device Setup & Management

> **Post-restructure paths:** The Android project lives in the `android/` directory. Run `./gradlew` commands from there (`cd android` first). `adb` commands run from any directory. Debug APK artifacts build to `android/weightogo/build/outputs/apk/debug/weightogo-debug.apk`.

### Install & Launch App

```bash
# Build and install debug APK
./gradlew clean assembleDebug installDebug

# Launch app
adb shell am start -n com.example.weightogo/.activities.LoginActivity

# Install on specific device (if multiple connected)
adb -s <device-id> install android/weightogo/build/outputs/apk/debug/weightogo-debug.apk
```

### Device Management

```bash
# List connected devices
adb devices

# Get device info
adb shell getprop ro.build.version.sdk  # API level
adb shell wm size                        # Screen resolution
adb shell wm density                     # Screen density

# Rotate screen
adb shell settings put system user_rotation 0  # Portrait
adb shell settings put system user_rotation 1  # Landscape (90°)
adb shell settings put system user_rotation 2  # Reverse portrait (180°)
adb shell settings put system user_rotation 3  # Reverse landscape (270°)

# Enable/disable auto-rotate
adb shell settings put system accelerometer_rotation 0  # Disable
adb shell settings put system accelerometer_rotation 1  # Enable

# Simulate airplane mode
adb shell cmd connectivity airplane-mode enable
adb shell cmd connectivity airplane-mode disable

# Kill app process (simulate process death)
adb shell am kill com.example.weightogo
# Force stop app
adb shell am force-stop com.example.weightogo
# Clear app data (reset to fresh install state)
adb shell pm clear com.example.weightogo
```

### Emulator Management

```bash
# List available emulators
emulator -list-avds

# Launch specific emulator
emulator -avd <avd-name>

# Launch emulator with specific API level
emulator -avd Pixel_6_API_34
emulator -avd Pixel_4a_API_28

# Launch emulator in landscape mode
emulator -avd <avd-name> -skin 1920x1080

# Take screenshot
adb exec-out screencap -p > screenshot.png
```

---

## Test Data Generation

### Create Test Users (via ADB + SQL)

```bash
# Connect to app database
adb shell run-as com.example.weightogo
# Open SQLite database
sqlite3 /data/data/com.example.weightogo/databases/weigh_to_go.db

# Create test user manually (note: password hashing must be done in-app)
# Instead, use registration feature in app for test users:
# - testuser1 / TestPass123!
# - testuser2 / TestPass456!
# - adminuser / Admin789!

# Exit sqlite
.exit

# Exit run-as
exit
```

### Bulk Weight Entry Creation Script

Create this Python script to generate SQL for bulk weight entries:

**File: `scripts/generate_test_weight_entries.py`**

```python
#!/usr/bin/env python3
"""
Generate SQL INSERT statements for bulk weight entry testing.
Usage: python3 generate_test_weight_entries.py > test_weight_entries.sql
"""

from datetime import datetime, timedelta

def generate_weight_entries(user_id=1, count=100, start_weight=170.0, variance=5.0):
    """Generate SQL INSERT statements for weight entries."""

    entries = []
    current_date = datetime.now()
    current_weight = start_weight

    for i in range(count):
        entry_date = current_date - timedelta(days=i)
        date_str = entry_date.strftime('%Y-%m-%d')

        # Vary weight slightly (simulate realistic weight fluctuation)
        import random
        weight_change = random.uniform(-variance, variance)
        current_weight += weight_change
        current_weight = max(50.0, min(500.0, current_weight))  # Clamp to reasonable range

        unit = "lbs" if i % 3 != 0 else "kg"  # Mix of units

        sql = f"""INSERT INTO daily_weights (user_id, weight_date, weight_value, weight_unit, created_at, updated_at)
VALUES ({user_id}, '{date_str}', {current_weight:.1f}, '{unit}', datetime('now'), datetime('now'));"""

        entries.append(sql)

    return entries

if __name__ == "__main__":
    print("-- Generated test weight entries")
    print("-- Run this script in SQLite: .read test_weight_entries.sql")
    print()

    for sql in generate_weight_entries(user_id=1, count=100):
        print(sql)

    print()
    print("-- Done. Total entries: 100")
```

**Usage:**

```bash
# Generate SQL file
python3 scripts/generate_test_weight_entries.py > test_weight_entries.sql

# Apply to database
adb push test_weight_entries.sql /sdcard/
adb shell run-as com.example.weightogo
sqlite3 /data/data/com.example.weightogo/databases/weigh_to_go.db
.read /sdcard/test_weight_entries.sql
.exit
exit
```

### Quick Manual Test Data (In-App)

For faster testing without scripts:

1. **Create Test User**:
   - Launch app → Create Account tab
   - Username: `testuser1`, Password: `TestPass123!`
   - Tap "Create Account"

2. **Add Multiple Weight Entries Quickly**:
   - Use WeightEntryActivity date navigation to add entries for different dates
   - Vary weights: 170.0 → 168.5 → 169.0 → 167.5 (creates trend data)

3. **Create Goal Weight**:
   - Navigate to GoalsActivity
   - Tap FAB → Enter goal weight: 160.0 lbs
   - Set target date: 30 days from now

---

## Database Inspection

### Connect to Database

```bash
# Method 1: Via run-as (rooted device or emulator)
adb shell run-as com.example.weightogo
cd /data/data/com.example.weightogo/databases
sqlite3 weigh_to_go.db

# Method 2: Pull database to local machine
adb shell run-as com.example.weightogo
cat /data/data/com.example.weightogo/databases/weigh_to_go.db > weigh_to_go.db
sqlite3 weigh_to_go.db
```

### Useful SQL Queries

```sql
-- List all tables
.tables

-- Show table schema
.schema users
.schema daily_weights
.schema goal_weights
.schema achievements
.schema user_preferences

-- Count users
SELECT COUNT(*) FROM users;

-- List all users
SELECT user_id, username, created_at, last_login FROM users;

-- Count weight entries for a user
SELECT COUNT(*) FROM daily_weights WHERE user_id = 1 AND is_deleted = 0;

-- Show recent weight entries
SELECT weight_date, weight_value, weight_unit, created_at
FROM daily_weights
WHERE user_id = 1 AND is_deleted = 0
ORDER BY weight_date DESC
LIMIT 10;

-- Check for soft-deleted entries
SELECT weight_date, weight_value, is_deleted
FROM daily_weights
WHERE user_id = 1 AND is_deleted = 1;

-- Show active goals
SELECT goal_weight, target_date, status, created_at
FROM goal_weights
WHERE user_id = 1 AND is_active = 1;

-- Show achievements
SELECT achievement_type, earned_date, details
FROM achievements
WHERE user_id = 1
ORDER BY earned_date DESC;

-- Show user preferences
SELECT preference_key, preference_value
FROM user_preferences
WHERE user_id = 1;

-- Check for mixed units in weight entries
SELECT weight_unit, COUNT(*) as count
FROM daily_weights
WHERE user_id = 1 AND is_deleted = 0
GROUP BY weight_unit;

-- Exit SQLite
.exit
```

### Database Export/Import

```bash
# Export database to file
adb shell run-as com.example.weightogo
cat /data/data/com.example.weightogo/databases/weigh_to_go.db > backup_$(date +%Y%m%d).db

# Import database from backup
adb shell run-as com.example.weightogo
cat /sdcard/backup.db > /data/data/com.example.weightogo/databases/weigh_to_go.db
exit

# Dump database to SQL (for version control)
sqlite3 weigh_to_go.db .dump > database_dump.sql
```

---

## App State Management

### Reset App to Initial State

```bash
# Method 1: Clear app data (fastest)
adb shell pm clear com.example.weightogo
# Method 2: Uninstall and reinstall
adb uninstall com.example.weightogo
./gradlew installDebug

# Method 3: Delete database only (keep app installed)
adb shell run-as com.example.weightogo
rm /data/data/com.example.weightogo/databases/weigh_to_go.db
rm /data/data/com.example.weightogo/databases/weigh_to_go.db-shm
rm /data/data/com.example.weightogo/databases/weigh_to_go.db-wal
exit
```

### Session Management

```bash
# Check SharedPreferences (session data)
adb shell run-as com.example.weightogo
cat /data/data/com.example.weightogo/shared_prefs/SessionPrefs.xml
exit

# Clear session (force logout)
adb shell run-as com.example.weightogo
rm /data/data/com.example.weightogo/shared_prefs/SessionPrefs.xml
exit

# Restart app
adb shell am force-stop com.example.weightogo
adb shell am start -n com.example.weightogo/.activities.LoginActivity
```

### Permissions Management

```bash
# Check granted permissions
adb shell dumpsys package com.example.weightogo | grep permission

# Grant SMS permission (for testing)
adb shell pm grant com.example.weightogo android.permission.SEND_SMS

# Revoke SMS permission
adb shell pm revoke com.example.weightogo android.permission.SEND_SMS

# Grant notification permission (API 33+)
adb shell pm grant com.example.weightogo android.permission.POST_NOTIFICATIONS

# Revoke notification permission
adb shell pm revoke com.example.weightogo android.permission.POST_NOTIFICATIONS

# Reset all permissions to default
adb shell pm reset-permissions com.example.weightogo
```

---

## Quick Test Scenarios

### Scenario 1: Test Authentication Flow

```bash
# 1. Reset app
adb shell pm clear com.example.weightogo
# 2. Launch app
adb shell am start -n com.example.weightogo/.activities.LoginActivity

# 3. Register user via UI:
#    - Switch to "Create Account" tab
#    - Username: testuser1
#    - Password: TestPass123!

# 4. Verify session persistence
adb shell am force-stop com.example.weightogo
adb shell am start -n com.example.weightogo/.activities.LoginActivity
# Expected: Auto-navigate to MainActivity

# 5. Test logout
# (Tap logout in SettingsActivity via UI)

# 6. Verify session cleared
adb shell am start -n com.example.weightogo/.activities.LoginActivity
# Expected: LoginActivity displays (not auto-navigate)
```

### Scenario 2: Test Weight Entry with Mixed Units

```bash
# 1. Login as testuser1

# 2. Add entries via UI:
#    Entry 1: 100 kg (today)
#    Entry 2: 220 lbs (yesterday)
#    Entry 3: 99 kg (2 days ago)

# 3. Verify trend calculation:
#    100 kg ≈ 220 lbs → trend should be ~0 or minimal
#    99 kg < 100 kg → trend should show weight loss

# 4. Change unit preference:
#    Settings → Toggle unit to lbs

# 5. Verify all entries converted:
#    100 kg → 220 lbs
#    220 lbs → 220 lbs
#    99 kg → 218 lbs

# 6. Check database
adb shell run-as com.example.weightogo
sqlite3 /data/data/com.example.weightogo/databases/weigh_to_go.db "SELECT weight_date, weight_value, weight_unit FROM daily_weights WHERE user_id = 1 ORDER BY weight_date DESC;"
```

### Scenario 3: Test SMS Permissions

```bash
# 1. Fresh install
adb shell pm clear com.example.weightogo
./gradlew installDebug

# 2. Login as testuser1

# 3. Navigate to SettingsActivity

# 4. Tap SMS notification toggle

# 5. Deny permission in system dialog

# 6. Verify toggle remains disabled

# 7. Tap toggle again → Deny with "Don't ask again"

# 8. Tap toggle again → Verify settings prompt

# 9. Manually grant permission:
adb shell pm grant com.example.weightogo android.permission.SEND_SMS

# 10. Reopen SettingsActivity → Verify toggle enabled
```

### Scenario 4: Test Large Dataset Performance

```bash
# 1. Generate 100+ entries using Python script (see above)

# 2. Import to database
adb push test_weight_entries.sql /sdcard/
adb shell run-as com.example.weightogo
sqlite3 /data/data/com.example.weightogo/databases/weigh_to_go.db
.read /sdcard/test_weight_entries.sql
.exit
exit

# 3. Launch app
adb shell am force-stop com.example.weightogo
adb shell am start -n com.example.weightogo/.activities.MainActivity

# 4. Test scrolling performance:
#    - Open MainActivity
#    - Scroll through weight history RecyclerView
#    - Monitor logcat for frame drops

# 5. Check logcat for performance warnings
adb logcat | grep -E "Skipped|Choreographer"
```

---

## Debugging Helpers

### LogCat Filtering

```bash
# Show only app logs
adb logcat -s WeighToGo:*

# Show errors and warnings
adb logcat *:E *:W

# Filter by tag
adb logcat | grep "MainActivity"

# Clear logcat buffer
adb logcat -c

# Save logcat to file
adb logcat > logcat_$(date +%Y%m%d_%H%M%S).txt

# Monitor specific tags
adb logcat | grep -E "WeighToGo|MainActivity|LoginActivity|SessionManager"
```

### Performance Monitoring

```bash
# Monitor app memory usage
adb shell dumpsys meminfo com.example.weightogo
# Monitor CPU usage
adb shell top | grep com.example.weightogo

# Check app is running
adb shell ps | grep com.example.weightogo

# Monitor frame rendering
adb shell dumpsys gfxinfo com.example.weightogo
# Enable GPU rendering profile
adb shell setprop debug.hwui.profile true

# Disable GPU rendering profile
adb shell setprop debug.hwui.profile false
```

### Network Debugging (If Applicable)

```bash
# Enable airplane mode
adb shell cmd connectivity airplane-mode enable

# Disable airplane mode
adb shell cmd connectivity airplane-mode disable

# Check network connectivity
adb shell ping -c 3 8.8.8.8

# Monitor network traffic
adb shell dumpsys netstats | grep com.example.weightogo
```

### UI Hierarchy Inspection

```bash
# Dump UI hierarchy to file
adb shell uiautomator dump
adb pull /sdcard/window_dump.xml

# View with Android Studio Layout Inspector:
# Tools → Layout Inspector → Connect to device
```

### Activity Stack Inspection

```bash
# Show current activity stack
adb shell dumpsys activity activities | grep -E "Running|com.example.weightogo"

# Show current focused activity
adb shell dumpsys activity activities | grep mResumedActivity

# Show activity lifecycle events in real-time
adb logcat | grep -E "onCreate|onStart|onResume|onPause|onStop|onDestroy"
```

---

## Test Environment Checklist

Before starting manual testing, verify:

- [ ] **Gradle Build Success**: `./gradlew clean build` → BUILD SUCCESSFUL
- [ ] **Unit Tests Pass**: `./gradlew test` → All tests passing
- [ ] **Instrumented Tests Pass**: `./gradlew connectedAndroidTest` → All tests passing
- [ ] **Lint Clean**: `./gradlew lint` → 0 warnings/errors
- [ ] **APK Installs**: `./gradlew installDebug` → Installs without errors
- [ ] **ADB Connection**: `adb devices` → Shows connected device/emulator
- [ ] **LogCat Access**: `adb logcat` → Shows device logs
- [ ] **Database Access**: Can connect to SQLite database via `adb shell run-as`

---

## Troubleshooting Common Issues

### Issue: Cannot connect to database via run-as

**Cause**: App not debuggable or device not rooted

**Solution**:
```bash
# Verify app is debuggable
adb shell dumpsys package com.example.weightogo | grep "android:debuggable"
# Should show: android:debuggable=true

# If false, rebuild with debug variant
./gradlew clean assembleDebug installDebug
```

### Issue: Permission denied errors

**Cause**: ADB insufficient privileges

**Solution**:
```bash
# Restart ADB server with root privileges
adb kill-server
sudo adb start-server
adb devices
```

### Issue: App crashes immediately on launch

**Cause**: Database corruption or app state issue

**Solution**:
```bash
# Clear app data and reinstall
adb shell pm clear com.example.weightogo
adb uninstall com.example.weightogo
./gradlew installDebug

# Check logcat for crash details
adb logcat | grep -E "AndroidRuntime|FATAL"
```

### Issue: Cannot grant permissions via ADB

**Cause**: Permission not declared in manifest or API level restriction

**Solution**:
```bash
# Check manifest for permission declaration
grep -r "SEND_SMS" android/weightogo/src/main/AndroidManifest.xml

# For API 23+, permissions must be requested at runtime
# Use UI to grant permissions instead of ADB
```

---

## Quick Reference Commands

```bash
# Essential Test Cycle Commands
./gradlew clean build                              # Build app
./gradlew installDebug                             # Install debug APK
adb shell pm clear com.example.weightogo         # Reset app data
adb shell am start -n com.example.weightogo/.activities.LoginActivity  # Launch app
adb logcat -s WeighToGo:*                          # Monitor app logs
adb shell run-as com.example.weightogo           # Access app data
sqlite3 /data/data/com.example.weightogo/databases/weigh_to_go.db  # Open database

# Common Test Data Setup
# 1. Create testuser1 via UI (username: testuser1, password: TestPass123!)
# 2. Add 5-10 weight entries via UI
# 3. Create goal via GoalsActivity
# 4. Test all features with this baseline data
```

---

## Additional Resources

- **Manual Testing Checklist**: `docs/testing/Manual_Testing_Checklist.md`
- **Database Architecture**: `docs/architecture/WeighToGo_Database_Architecture.md`
- **Design Specifications**: `docs/design/Weight_Tracker_Figma_Design_Specifications.md`
- **Project Requirements**: `docs/requirements/CS360_Project_Three_Requirements.md`

---

**Document Version**: 1.0
**Last Updated**: Phase 9.6 (Manual Testing Setup)
**Next Steps**: Execute tests in `Manual_Testing_Checklist.md` using these setup helpers
