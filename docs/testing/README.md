# WeightToGo Testing Documentation

This directory contains comprehensive manual testing documentation and setup helpers for Phase 9.6 of the WeightToGo project.

## Contents

### 1. Manual_Testing_Checklist.md
**Purpose**: Comprehensive checklist for executing manual device and scenario testing

**Covers**:
- Device testing (API levels, orientations, screen sizes)
- Authentication scenarios (registration, login, logout, session persistence)
- Weight entry workflows (add, edit, delete, unit conversion)
- SMS permissions scenarios (grant, deny, "don't ask again")
- Edge cases (special characters, screen rotation, app kill/restart, boundaries)

**Use This When**:
- Performing manual validation before release
- Testing on physical devices
- Verifying app behavior across different configurations
- Documenting test results for stakeholders

**Total Test Steps**: 145+ documented test cases

---

### 2. Test_Scenario_Setup_Guide.md
**Purpose**: Commands, scripts, and helpers to efficiently set up and execute manual test scenarios

**Provides**:
- ADB commands for device management (install, rotation, airplane mode, etc.)
- Database inspection queries (SQLite commands for verification)
- App state management (reset, session clearing, permissions)
- Quick test scenario walkthroughs (authentication, weight entry, SMS)
- Debugging helpers (LogCat filtering, performance monitoring, UI inspection)
- Troubleshooting common issues

**Use This When**:
- Setting up test environments
- Inspecting app database during testing
- Debugging test failures
- Generating bulk test data
- Resetting app state between tests

**Contains**: 50+ ADB commands, 15+ SQL queries, 20+ debugging commands

---

### 3. Python Test Data Generator
**Location**: `../../scripts/generate_test_weight_entries.py`

**Purpose**: Generate bulk weight entry test data for performance and scenario testing

**Features**:
- Configurable entry count (default: 100)
- Configurable weight variance (default: ±2.0)
- Mixed units support (lbs, kg, or both)
- SQL transaction wrapping
- Command-line interface

**Usage**:
```bash
# Generate 100 mixed-unit entries
python3 scripts/generate_test_weight_entries.py > test_data.sql

# Generate 200 lbs-only entries starting at 180 lbs
python3 scripts/generate_test_weight_entries.py --count 200 --start-weight 180 --unit lbs

# Apply to database
adb push test_data.sql /sdcard/
adb shell run-as weightogosqlite3 /data/data/weightogodatabases/WeighToGo.db
.read /sdcard/test_data.sql
.exit
exit
```

---

## How to Use This Documentation

### For Manual Testing:

1. **Before Testing**:
   - Read both documents to understand scope and setup
   - Prepare 2-3 test environments (different devices/emulators)
   - Review `Test_Scenario_Setup_Guide.md` for ADB commands

2. **During Testing**:
   - Follow `Manual_Testing_Checklist.md` step-by-step
   - Mark each test: ✅ Pass | ❌ Fail | ⚠️ Issue | ⏭️ Skipped
   - Document unexpected behavior in "Actual Result / Notes" column
   - Take screenshots for failures
   - Use `Test_Scenario_Setup_Guide.md` for setup commands

3. **After Testing**:
   - Complete Test Summary section in checklist
   - Update `project_summary.md` with findings
   - Create GitHub issues for bugs found
   - Attach checklist to final documentation

### For Test Data Setup:

1. **Small Dataset** (for quick testing):
   - Use UI to manually create 5-10 weight entries
   - Vary weights to create trend data

2. **Large Dataset** (for performance testing):
   - Use Python script to generate 100+ entries
   - Import to database using SQL commands from Setup Guide
   - Test scrolling performance, edit/delete operations

### For Debugging:

1. **App Crashes**:
   - Check LogCat for crash details (see Setup Guide section)
   - Inspect database for data corruption
   - Clear app data and retry

2. **Permission Issues**:
   - Use ADB commands to manually grant/revoke permissions
   - Check permission state with `dumpsys package` command
   - Reset permissions to default if needed

3. **Database Issues**:
   - Use SQL queries to inspect database state
   - Export database for offline analysis
   - Compare with expected schema

---

## Quick Start

**New to manual testing this app?** Start here:

1. **Read**: `Manual_Testing_Checklist.md` introduction
2. **Set Up**: Use `Test_Scenario_Setup_Guide.md` to install app and prepare test environments
3. **Test**: Execute Section 9.6.2 (Authentication Scenarios) first - these are quick and foundational
4. **Document**: Mark results in checklist as you go
5. **Expand**: Continue with other sections based on priority

**Estimated Time**:
- Full checklist execution: 4-6 hours (across all configurations)
- Critical path only (authentication + weight entry): 1-2 hours
- Per-device configuration: ~30 minutes setup + 2-3 hours testing

---

## Integration with Automated Tests

These manual tests **complement** (not replace) automated tests:

- **Automated Tests** (Unit + Espresso):
  - Run on every commit (CI/CD)
  - Test isolated logic and critical UI flows
  - Fast feedback (minutes)
  - High coverage (450+ tests)

- **Manual Tests** (This Documentation):
  - Run before major releases
  - Test full user experiences across devices
  - Validate visual design, usability, accessibility
  - Catch integration issues that automated tests miss

**Both are required** for comprehensive quality assurance.

---

## Maintenance

**When to Update This Documentation**:
- New features added to the app
- New edge cases discovered during testing
- Test scenarios need clarification
- Setup procedures change (new ADB commands, database schema changes)

**How to Update**:
1. Edit markdown files directly
2. Increment version numbers in document headers
3. Update this README if new documents added
4. Commit changes with descriptive message

---

## Related Documentation

- **Android Development Journal**: `../history/android_summary.md`
- **TODO**: `../../TODO.md` - Phase 9.6 completion tracking
- **Database Architecture**: `../architecture/WeighToGo_Database_Architecture.md`
- **Design Specifications**: `../design/Weight_Tracker_Figma_Design_Specifications.md`
- **Requirements**: `../requirements/CS360_Project_Three_Requirements.md`

---

## Support

**Questions or Issues?**
- Check `Test_Scenario_Setup_Guide.md` troubleshooting section
- Review LogCat output for error details
- Consult database architecture docs for schema questions
- Create GitHub issue for documentation improvements

---

**Last Updated**: 2025-12-14 (Phase 9.6 - Manual Testing Documentation)
**Document Version**: 1.0
**Status**: Complete - Ready for manual test execution
