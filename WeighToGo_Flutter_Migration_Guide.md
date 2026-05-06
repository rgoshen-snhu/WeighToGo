# Weigh to Go! Flutter Migration Guide

## 📱 Cross-Platform Development: Android → Flutter

**Project**: Weigh to Go! Weight Tracking Application  
**Original Platform**: Android (Java/XML)  
**Target Platform**: Flutter (Dart) - Android, iOS, Web  
**Author**: Rick Goshen  
**Date**: December 15, 2025

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Prerequisites & Environment Setup](#prerequisites--environment-setup)
3. [Project Structure Mapping](#project-structure-mapping)
4. [Architecture Translation](#architecture-translation)
5. [Database Migration](#database-migration)
6. [UI Component Mapping](#ui-component-mapping)
7. [Screen-by-Screen Implementation](#screen-by-screen-implementation)
8. [State Management](#state-management)
9. [Platform-Specific Features](#platform-specific-features)
10. [Theming & Styling](#theming--styling)
11. [Testing Strategy](#testing-strategy)
12. [Build & Deployment](#build--deployment)
13. [Migration Checklist](#migration-checklist)
14. [Resources & References](#resources--references)

---

## Executive Summary

This guide provides a comprehensive roadmap for rebuilding the Weigh to Go! Android application using Flutter, enabling deployment to Android, iOS, and web platforms from a single codebase. The migration preserves all existing functionality while leveraging Flutter's modern declarative UI paradigm and hot reload development experience.

### Key Benefits of Migration

| Benefit | Impact |
|---------|--------|
| **Single Codebase** | Maintain one codebase for Android, iOS, and Web |
| **Faster Development** | Hot reload enables instant UI changes |
| **Consistent UI** | Identical appearance across all platforms |
| **Modern Architecture** | Declarative UI with reactive state management |
| **Growing Ecosystem** | Rich package library and strong community |

### What Transfers Directly

- Database schema and CRUD logic
- Business rules and validation
- UI/UX design specifications
- Authentication flow
- Color scheme and branding

### What Requires Rewriting

- All UI code (XML → Dart widgets)
- Activity/Fragment logic (→ StatefulWidget)
- Adapters/ViewHolders (→ ListView.builder)
- Resource files (→ ThemeData and asset configuration)

---

## Prerequisites & Environment Setup

### System Requirements

**For macOS (iOS + Android development):**
- macOS 10.14 or later
- Xcode 12 or later (for iOS)
- Android Studio or VS Code
- 8GB RAM minimum (16GB recommended)

**For Windows (Android + Web only):**
- Windows 10 or later (64-bit)
- Android Studio or VS Code
- 8GB RAM minimum

**For Linux (Android + Web only):**
- 64-bit Linux distribution
- Android Studio or VS Code

### Installation Steps

#### Step 1: Install Flutter SDK

```bash
# macOS (using Homebrew)
brew install --cask flutter

# Or manual installation (all platforms)
# Download from: https://docs.flutter.dev/get-started/install
# Extract to desired location (e.g., ~/development/flutter)

# Add to PATH (add to .bashrc, .zshrc, or equivalent)
export PATH="$PATH:$HOME/development/flutter/bin"
```

#### Step 2: Verify Installation

```bash
# Run Flutter doctor to check setup
flutter doctor

# Expected output should show checkmarks for:
# ✓ Flutter (Channel stable)
# ✓ Android toolchain
# ✓ Xcode (macOS only)
# ✓ Chrome (for web development)
# ✓ Android Studio or VS Code
```

#### Step 3: Configure IDE

**VS Code (Recommended):**
```bash
# Install extensions from VS Code marketplace:
# - Flutter
# - Dart
# - Flutter Widget Snippets (optional)
```

**Android Studio:**
```
Preferences → Plugins → Marketplace
Search and install:
- Flutter
- Dart
```

#### Step 4: Create the Project

```bash
# Create new Flutter project
flutter create weigh_to_go

# Navigate to project
cd weigh_to_go

# Open in IDE
code .  # VS Code
# or
studio .  # Android Studio

# Verify project runs
flutter run
```

---

## Project Structure Mapping

### Android Project Structure → Flutter Project Structure

```
ANDROID (Current)                      FLUTTER (New)
===============                        =============

app/
├── src/main/
│   ├── java/com/example/weighttracker/
│   │   ├── MainActivity.java         → lib/main.dart
│   │   ├── LoginActivity.java        → lib/screens/login_screen.dart
│   │   ├── RegisterActivity.java     → lib/screens/register_screen.dart
│   │   ├── DashboardActivity.java    → lib/screens/dashboard_screen.dart
│   │   ├── WeightEntryActivity.java  → lib/screens/weight_entry_screen.dart
│   │   ├── SettingsActivity.java     → lib/screens/settings_screen.dart
│   │   │
│   │   ├── models/
│   │   │   ├── User.java             → lib/models/user.dart
│   │   │   └── WeightEntry.java      → lib/models/weight_entry.dart
│   │   │
│   │   ├── database/
│   │   │   ├── DatabaseHelper.java   → lib/services/database_service.dart
│   │   │   ├── UserDao.java          → lib/repositories/user_repository.dart
│   │   │   └── WeightDao.java        → lib/repositories/weight_repository.dart
│   │   │
│   │   ├── adapters/
│   │   │   └── WeightAdapter.java    → lib/widgets/weight_list_tile.dart
│   │   │
│   │   └── utils/
│   │       ├── ValidationUtils.java  → lib/utils/validators.dart
│   │       └── DateUtils.java        → lib/utils/date_helpers.dart
│   │
│   ├── res/
│   │   ├── layout/
│   │   │   ├── activity_login.xml    → (built in login_screen.dart)
│   │   │   ├── activity_main.xml     → (built in dashboard_screen.dart)
│   │   │   └── item_weight.xml       → (built in weight_list_tile.dart)
│   │   │
│   │   ├── values/
│   │   │   ├── strings.xml           → lib/constants/strings.dart
│   │   │   ├── colors.xml            → lib/theme/app_colors.dart
│   │   │   ├── styles.xml            → lib/theme/app_theme.dart
│   │   │   └── dimens.xml            → lib/theme/dimensions.dart
│   │   │
│   │   ├── drawable/                 → assets/images/
│   │   └── mipmap/                   → assets/icons/ (+ pubspec.yaml config)
│   │
│   └── AndroidManifest.xml           → android/app/src/main/AndroidManifest.xml
│                                       (auto-generated, modify for permissions)
│
└── build.gradle                      → pubspec.yaml (dependencies)
```

### Recommended Flutter Project Structure

```
weigh_to_go/
├── lib/
│   ├── main.dart                     # App entry point
│   │
│   ├── app.dart                      # MaterialApp configuration
│   │
│   ├── config/
│   │   ├── routes.dart               # Named route definitions
│   │   └── constants.dart            # App-wide constants
│   │
│   ├── models/
│   │   ├── user.dart                 # User data model
│   │   └── weight_entry.dart         # Weight entry data model
│   │
│   ├── services/
│   │   ├── database_service.dart     # SQLite database operations
│   │   ├── auth_service.dart         # Authentication logic
│   │   └── notification_service.dart # SMS/Push notifications
│   │
│   ├── repositories/
│   │   ├── user_repository.dart      # User data access
│   │   └── weight_repository.dart    # Weight data access
│   │
│   ├── providers/
│   │   ├── auth_provider.dart        # Authentication state
│   │   ├── user_provider.dart        # User data state
│   │   └── weight_provider.dart      # Weight entries state
│   │
│   ├── screens/
│   │   ├── login_screen.dart
│   │   ├── register_screen.dart
│   │   ├── dashboard_screen.dart
│   │   ├── weight_entry_screen.dart
│   │   ├── weight_history_screen.dart
│   │   └── settings_screen.dart
│   │
│   ├── widgets/
│   │   ├── common/
│   │   │   ├── app_button.dart       # Reusable button
│   │   │   ├── app_text_field.dart   # Reusable input field
│   │   │   └── loading_indicator.dart
│   │   │
│   │   ├── weight_list_tile.dart     # Weight entry list item
│   │   ├── weight_chart.dart         # Progress chart widget
│   │   └── goal_progress_card.dart   # Goal tracking card
│   │
│   ├── theme/
│   │   ├── app_theme.dart            # ThemeData configuration
│   │   ├── app_colors.dart           # Color definitions
│   │   └── text_styles.dart          # Typography
│   │
│   └── utils/
│       ├── validators.dart           # Input validation
│       ├── date_helpers.dart         # Date formatting
│       └── weight_converter.dart     # Unit conversion (lbs/kg)
│
├── assets/
│   ├── images/
│   │   └── logo.png
│   └── icons/
│       └── app_icon.png
│
├── test/
│   ├── unit/
│   ├── widget/
│   └── integration/
│
├── android/                          # Android-specific config
├── ios/                              # iOS-specific config
├── web/                              # Web-specific config
│
└── pubspec.yaml                      # Dependencies & assets
```

---

## Architecture Translation

### Android MVC → Flutter with Provider

```
ANDROID MVC                           FLUTTER + PROVIDER
===========                           ==================

┌─────────────┐                       ┌─────────────────┐
│   View      │                       │    Widgets      │
│  (XML)      │                       │   (Stateless/   │
│             │                       │    Stateful)    │
└──────┬──────┘                       └────────┬────────┘
       │                                       │
       │ findViewById()                        │ context.watch<Provider>()
       │ setOnClickListener()                  │ context.read<Provider>()
       │                                       │
┌──────▼──────┐                       ┌────────▼────────┐
│ Controller  │                       │    Provider     │
│ (Activity)  │                       │ (ChangeNotifier)│
│             │                       │                 │
└──────┬──────┘                       └────────┬────────┘
       │                                       │
       │ model.getData()                       │ repository.getData()
       │ model.saveData()                      │ repository.saveData()
       │                                       │
┌──────▼──────┐                       ┌────────▼────────┐
│   Model     │                       │   Repository    │
│ (Java POJO) │                       │   + Service     │
│ (DAO/DB)    │                       │   + Model       │
└─────────────┘                       └─────────────────┘
```

### Activity Lifecycle → StatefulWidget Lifecycle

```dart
// ANDROID LIFECYCLE              // FLUTTER LIFECYCLE
// ================              // =================

// onCreate()          →         // initState()
// onStart()           →         // (handled by framework)
// onResume()          →         // (use WidgetsBindingObserver)
// onPause()           →         // (use WidgetsBindingObserver)
// onStop()            →         // (handled by framework)
// onDestroy()         →         // dispose()
// onSaveInstanceState →         // (state preserved in Provider)

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> 
    with WidgetsBindingObserver {
  
  @override
  void initState() {
    super.initState();
    // Equivalent to onCreate()
    // Initialize data, load from database
    WidgetsBinding.instance.addObserver(this);
    _loadInitialData();
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    // Equivalent to onResume(), onPause()
    switch (state) {
      case AppLifecycleState.resumed:
        // App came to foreground
        _refreshData();
        break;
      case AppLifecycleState.paused:
        // App went to background
        _saveState();
        break;
      default:
        break;
    }
  }

  @override
  void dispose() {
    // Equivalent to onDestroy()
    // Clean up controllers, listeners
    WidgetsBinding.instance.removeObserver(this);
    super.dispose();
  }

  Future<void> _loadInitialData() async {
    // Load data on screen creation
  }

  Future<void> _refreshData() async {
    // Refresh when app resumes
  }

  void _saveState() {
    // Save state when app pauses
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      // UI implementation
    );
  }
}
```

---

## Database Migration

### Dependencies Configuration

```yaml
# pubspec.yaml
dependencies:
  flutter:
    sdk: flutter
  
  # Database
  sqflite: ^2.3.0
  path: ^1.8.3
  
  # State Management
  provider: ^6.1.1
  
  # Utilities
  intl: ^0.18.1              # Date formatting
  crypto: ^3.0.3             # Password hashing
  
  # UI Components
  fl_chart: ^0.66.0          # Charts for weight tracking
  
  # Notifications (platform-specific)
  flutter_local_notifications: ^16.3.0
  
  # Permissions
  permission_handler: ^11.1.0

dev_dependencies:
  flutter_test:
    sdk: flutter
  flutter_lints: ^3.0.1
  mockito: ^5.4.4            # Testing
```

### Database Service Implementation

```dart
// lib/services/database_service.dart

import 'package:sqflite/sqflite.dart';
import 'package:path/path.dart';

class DatabaseService {
  static final DatabaseService _instance = DatabaseService._internal();
  static Database? _database;
  
  // Database constants
  static const String _databaseName = 'weigh_to_go.db';
  static const int _databaseVersion = 1;
  
  // Table names
  static const String tableUsers = 'users';
  static const String tableWeightEntries = 'weight_entries';
  
  // Singleton pattern
  factory DatabaseService() => _instance;
  DatabaseService._internal();

  Future<Database> get database async {
    if (_database != null) return _database!;
    _database = await _initDatabase();
    return _database!;
  }

  Future<Database> _initDatabase() async {
    final String path = join(await getDatabasesPath(), _databaseName);
    
    return await openDatabase(
      path,
      version: _databaseVersion,
      onCreate: _onCreate,
      onUpgrade: _onUpgrade,
    );
  }

  Future<void> _onCreate(Database db, int version) async {
    // Create users table
    await db.execute('''
      CREATE TABLE $tableUsers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        email TEXT,
        goal_weight REAL,
        unit_preference TEXT DEFAULT 'lbs',
        notifications_enabled INTEGER DEFAULT 0,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
      )
    ''');

    // Create weight entries table
    await db.execute('''
      CREATE TABLE $tableWeightEntries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        weight REAL NOT NULL,
        entry_date TEXT NOT NULL,
        notes TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES $tableUsers(id) ON DELETE CASCADE
      )
    ''');

    // Create index for faster queries
    await db.execute('''
      CREATE INDEX idx_weight_entries_user_date 
      ON $tableWeightEntries(user_id, entry_date DESC)
    ''');
  }

  Future<void> _onUpgrade(Database db, int oldVersion, int newVersion) async {
    // Handle database migrations for future versions
    if (oldVersion < 2) {
      // Example migration
      // await db.execute('ALTER TABLE users ADD COLUMN new_field TEXT');
    }
  }

  // Close database
  Future<void> close() async {
    final db = await database;
    db.close();
    _database = null;
  }
}
```

### Model Classes

```dart
// lib/models/user.dart

class User {
  final int? id;
  final String username;
  final String passwordHash;
  final String? email;
  final double? goalWeight;
  final String unitPreference;
  final bool notificationsEnabled;
  final DateTime createdAt;
  final DateTime updatedAt;

  User({
    this.id,
    required this.username,
    required this.passwordHash,
    this.email,
    this.goalWeight,
    this.unitPreference = 'lbs',
    this.notificationsEnabled = false,
    DateTime? createdAt,
    DateTime? updatedAt,
  })  : createdAt = createdAt ?? DateTime.now(),
        updatedAt = updatedAt ?? DateTime.now();

  // Convert to Map for database insertion
  Map<String, dynamic> toMap() {
    return {
      if (id != null) 'id': id,
      'username': username,
      'password_hash': passwordHash,
      'email': email,
      'goal_weight': goalWeight,
      'unit_preference': unitPreference,
      'notifications_enabled': notificationsEnabled ? 1 : 0,
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt.toIso8601String(),
    };
  }

  // Create User from database Map
  factory User.fromMap(Map<String, dynamic> map) {
    return User(
      id: map['id'] as int?,
      username: map['username'] as String,
      passwordHash: map['password_hash'] as String,
      email: map['email'] as String?,
      goalWeight: map['goal_weight'] as double?,
      unitPreference: map['unit_preference'] as String? ?? 'lbs',
      notificationsEnabled: (map['notifications_enabled'] as int?) == 1,
      createdAt: DateTime.parse(map['created_at'] as String),
      updatedAt: DateTime.parse(map['updated_at'] as String),
    );
  }

  // Create copy with modifications
  User copyWith({
    int? id,
    String? username,
    String? passwordHash,
    String? email,
    double? goalWeight,
    String? unitPreference,
    bool? notificationsEnabled,
    DateTime? createdAt,
    DateTime? updatedAt,
  }) {
    return User(
      id: id ?? this.id,
      username: username ?? this.username,
      passwordHash: passwordHash ?? this.passwordHash,
      email: email ?? this.email,
      goalWeight: goalWeight ?? this.goalWeight,
      unitPreference: unitPreference ?? this.unitPreference,
      notificationsEnabled: notificationsEnabled ?? this.notificationsEnabled,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? DateTime.now(),
    );
  }
}
```

```dart
// lib/models/weight_entry.dart

class WeightEntry {
  final int? id;
  final int userId;
  final double weight;
  final DateTime entryDate;
  final String? notes;
  final DateTime createdAt;

  WeightEntry({
    this.id,
    required this.userId,
    required this.weight,
    required this.entryDate,
    this.notes,
    DateTime? createdAt,
  }) : createdAt = createdAt ?? DateTime.now();

  Map<String, dynamic> toMap() {
    return {
      if (id != null) 'id': id,
      'user_id': userId,
      'weight': weight,
      'entry_date': entryDate.toIso8601String().split('T')[0], // Date only
      'notes': notes,
      'created_at': createdAt.toIso8601String(),
    };
  }

  factory WeightEntry.fromMap(Map<String, dynamic> map) {
    return WeightEntry(
      id: map['id'] as int?,
      userId: map['user_id'] as int,
      weight: map['weight'] as double,
      entryDate: DateTime.parse(map['entry_date'] as String),
      notes: map['notes'] as String?,
      createdAt: DateTime.parse(map['created_at'] as String),
    );
  }

  WeightEntry copyWith({
    int? id,
    int? userId,
    double? weight,
    DateTime? entryDate,
    String? notes,
    DateTime? createdAt,
  }) {
    return WeightEntry(
      id: id ?? this.id,
      userId: userId ?? this.userId,
      weight: weight ?? this.weight,
      entryDate: entryDate ?? this.entryDate,
      notes: notes ?? this.notes,
      createdAt: createdAt ?? this.createdAt,
    );
  }
}
```

### Repository Classes

```dart
// lib/repositories/user_repository.dart

import 'package:sqflite/sqflite.dart';
import '../services/database_service.dart';
import '../models/user.dart';

class UserRepository {
  final DatabaseService _databaseService = DatabaseService();

  Future<int> createUser(User user) async {
    final db = await _databaseService.database;
    return await db.insert(
      DatabaseService.tableUsers,
      user.toMap(),
      conflictAlgorithm: ConflictAlgorithm.abort,
    );
  }

  Future<User?> getUserByUsername(String username) async {
    final db = await _databaseService.database;
    final List<Map<String, dynamic>> maps = await db.query(
      DatabaseService.tableUsers,
      where: 'username = ?',
      whereArgs: [username],
      limit: 1,
    );
    
    if (maps.isEmpty) return null;
    return User.fromMap(maps.first);
  }

  Future<User?> getUserById(int id) async {
    final db = await _databaseService.database;
    final List<Map<String, dynamic>> maps = await db.query(
      DatabaseService.tableUsers,
      where: 'id = ?',
      whereArgs: [id],
      limit: 1,
    );
    
    if (maps.isEmpty) return null;
    return User.fromMap(maps.first);
  }

  Future<int> updateUser(User user) async {
    final db = await _databaseService.database;
    return await db.update(
      DatabaseService.tableUsers,
      user.toMap(),
      where: 'id = ?',
      whereArgs: [user.id],
    );
  }

  Future<int> deleteUser(int id) async {
    final db = await _databaseService.database;
    return await db.delete(
      DatabaseService.tableUsers,
      where: 'id = ?',
      whereArgs: [id],
    );
  }

  Future<bool> usernameExists(String username) async {
    final user = await getUserByUsername(username);
    return user != null;
  }
}
```

```dart
// lib/repositories/weight_repository.dart

import 'package:sqflite/sqflite.dart';
import '../services/database_service.dart';
import '../models/weight_entry.dart';

class WeightRepository {
  final DatabaseService _databaseService = DatabaseService();

  Future<int> addWeightEntry(WeightEntry entry) async {
    final db = await _databaseService.database;
    return await db.insert(
      DatabaseService.tableWeightEntries,
      entry.toMap(),
    );
  }

  Future<List<WeightEntry>> getWeightEntries(int userId, {int? limit}) async {
    final db = await _databaseService.database;
    final List<Map<String, dynamic>> maps = await db.query(
      DatabaseService.tableWeightEntries,
      where: 'user_id = ?',
      whereArgs: [userId],
      orderBy: 'entry_date DESC',
      limit: limit,
    );
    
    return maps.map((map) => WeightEntry.fromMap(map)).toList();
  }

  Future<WeightEntry?> getLatestEntry(int userId) async {
    final entries = await getWeightEntries(userId, limit: 1);
    return entries.isNotEmpty ? entries.first : null;
  }

  Future<WeightEntry?> getEntryByDate(int userId, DateTime date) async {
    final db = await _databaseService.database;
    final dateString = date.toIso8601String().split('T')[0];
    
    final List<Map<String, dynamic>> maps = await db.query(
      DatabaseService.tableWeightEntries,
      where: 'user_id = ? AND entry_date = ?',
      whereArgs: [userId, dateString],
      limit: 1,
    );
    
    if (maps.isEmpty) return null;
    return WeightEntry.fromMap(maps.first);
  }

  Future<int> updateWeightEntry(WeightEntry entry) async {
    final db = await _databaseService.database;
    return await db.update(
      DatabaseService.tableWeightEntries,
      entry.toMap(),
      where: 'id = ?',
      whereArgs: [entry.id],
    );
  }

  Future<int> deleteWeightEntry(int id) async {
    final db = await _databaseService.database;
    return await db.delete(
      DatabaseService.tableWeightEntries,
      where: 'id = ?',
      whereArgs: [id],
    );
  }

  Future<Map<String, double>> getWeightStats(int userId) async {
    final db = await _databaseService.database;
    
    final result = await db.rawQuery('''
      SELECT 
        MIN(weight) as min_weight,
        MAX(weight) as max_weight,
        AVG(weight) as avg_weight,
        COUNT(*) as total_entries
      FROM ${DatabaseService.tableWeightEntries}
      WHERE user_id = ?
    ''', [userId]);
    
    if (result.isEmpty || result.first['total_entries'] == 0) {
      return {};
    }
    
    final row = result.first;
    return {
      'min': row['min_weight'] as double,
      'max': row['max_weight'] as double,
      'avg': row['avg_weight'] as double,
      'count': (row['total_entries'] as int).toDouble(),
    };
  }

  Future<List<WeightEntry>> getEntriesInDateRange(
    int userId,
    DateTime startDate,
    DateTime endDate,
  ) async {
    final db = await _databaseService.database;
    
    final List<Map<String, dynamic>> maps = await db.query(
      DatabaseService.tableWeightEntries,
      where: 'user_id = ? AND entry_date BETWEEN ? AND ?',
      whereArgs: [
        userId,
        startDate.toIso8601String().split('T')[0],
        endDate.toIso8601String().split('T')[0],
      ],
      orderBy: 'entry_date ASC',
    );
    
    return maps.map((map) => WeightEntry.fromMap(map)).toList();
  }
}
```

---

## UI Component Mapping

### Android XML → Flutter Widget Reference

| Android XML Element | Flutter Widget | Notes |
|---------------------|----------------|-------|
| `LinearLayout (vertical)` | `Column` | Use with `MainAxisAlignment`, `CrossAxisAlignment` |
| `LinearLayout (horizontal)` | `Row` | Use with `MainAxisAlignment`, `CrossAxisAlignment` |
| `RelativeLayout` | `Stack` | For overlapping widgets |
| `ConstraintLayout` | `Flex` / `Expanded` | Or use `LayoutBuilder` |
| `ScrollView` | `SingleChildScrollView` | Wrap Column for scrolling |
| `RecyclerView` | `ListView.builder` | Efficient list rendering |
| `CardView` | `Card` | Material card widget |
| `TextView` | `Text` | Use `TextStyle` for styling |
| `EditText` | `TextField` | With `TextEditingController` |
| `Button` | `ElevatedButton` | Or `TextButton`, `OutlinedButton` |
| `ImageView` | `Image` | `Image.asset()`, `Image.network()` |
| `ProgressBar` | `CircularProgressIndicator` | Or `LinearProgressIndicator` |
| `Switch` | `Switch` | With `onChanged` callback |
| `CheckBox` | `Checkbox` | With `onChanged` callback |
| `Spinner` | `DropdownButton` | Or `DropdownButtonFormField` |
| `FloatingActionButton` | `FloatingActionButton` | Place in `Scaffold.floatingActionButton` |
| `Toolbar/ActionBar` | `AppBar` | Place in `Scaffold.appBar` |
| `BottomNavigationView` | `BottomNavigationBar` | Place in `Scaffold.bottomNavigationBar` |
| `Snackbar` | `SnackBar` | Show via `ScaffoldMessenger` |
| `AlertDialog` | `AlertDialog` | Show via `showDialog()` |
| `Toast` | `SnackBar` | Flutter doesn't have Toast; use SnackBar |

### Layout Attribute Mapping

```dart
// ANDROID XML ATTRIBUTES → FLUTTER EQUIVALENTS

// android:layout_width="match_parent"
// android:layout_height="wrap_content"
// →
SizedBox(
  width: double.infinity,  // match_parent width
  child: Text('Content'),  // wrap_content height (default)
)

// android:padding="16dp"
// →
Padding(
  padding: EdgeInsets.all(16.0),
  child: Text('Content'),
)

// android:layout_margin="8dp"
// →
Container(
  margin: EdgeInsets.all(8.0),
  child: Text('Content'),
)

// android:gravity="center"
// →
Center(child: Text('Content'))
// or
Align(
  alignment: Alignment.center,
  child: Text('Content'),
)

// android:layout_weight="1"
// →
Expanded(
  flex: 1,
  child: Text('Content'),
)

// android:visibility="gone"
// →
Visibility(
  visible: false,
  child: Text('Content'),
)
// or conditionally build:
if (isVisible) Text('Content'),

// android:background="@color/primary"
// →
Container(
  color: AppColors.primary,
  child: Text('Content'),
)
// or with decoration:
Container(
  decoration: BoxDecoration(
    color: AppColors.primary,
    borderRadius: BorderRadius.circular(8),
  ),
  child: Text('Content'),
)
```

---

## Screen-by-Screen Implementation

### Main Entry Point

```dart
// lib/main.dart

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'app.dart';
import 'providers/auth_provider.dart';
import 'providers/weight_provider.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const WeighToGoApp());
}

class WeighToGoApp extends StatelessWidget {
  const WeighToGoApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => AuthProvider()),
        ChangeNotifierProxyProvider<AuthProvider, WeightProvider>(
          create: (_) => WeightProvider(),
          update: (_, auth, weight) => weight!..updateUserId(auth.userId),
        ),
      ],
      child: const App(),
    );
  }
}
```

```dart
// lib/app.dart

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'theme/app_theme.dart';
import 'config/routes.dart';
import 'providers/auth_provider.dart';
import 'screens/login_screen.dart';
import 'screens/dashboard_screen.dart';

class App extends StatelessWidget {
  const App({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Weigh to Go!',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.lightTheme,
      darkTheme: AppTheme.darkTheme,
      themeMode: ThemeMode.system,
      routes: AppRoutes.routes,
      home: Consumer<AuthProvider>(
        builder: (context, auth, _) {
          if (auth.isAuthenticated) {
            return const DashboardScreen();
          }
          return const LoginScreen();
        },
      ),
    );
  }
}
```

### Login Screen

```dart
// lib/screens/login_screen.dart

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/auth_provider.dart';
import '../widgets/common/app_text_field.dart';
import '../widgets/common/app_button.dart';
import '../theme/app_colors.dart';
import '../utils/validators.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _formKey = GlobalKey<FormState>();
  final _usernameController = TextEditingController();
  final _passwordController = TextEditingController();
  bool _isLoading = false;
  bool _obscurePassword = true;

  @override
  void dispose() {
    _usernameController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  Future<void> _handleLogin() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() => _isLoading = true);

    try {
      final authProvider = context.read<AuthProvider>();
      final success = await authProvider.login(
        _usernameController.text.trim(),
        _passwordController.text,
      );

      if (!success && mounted) {
        _showErrorSnackBar('Invalid username or password');
      }
    } catch (e) {
      if (mounted) {
        _showErrorSnackBar('An error occurred. Please try again.');
      }
    } finally {
      if (mounted) {
        setState(() => _isLoading = false);
      }
    }
  }

  void _showErrorSnackBar(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: AppColors.error,
        behavior: SnackBarBehavior.floating,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(24.0),
            child: Form(
              key: _formKey,
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  // Logo and title
                  _buildHeader(),
                  const SizedBox(height: 48),

                  // Username field
                  AppTextField(
                    controller: _usernameController,
                    labelText: 'Username',
                    prefixIcon: Icons.person_outline,
                    validator: Validators.username,
                    textInputAction: TextInputAction.next,
                  ),
                  const SizedBox(height: 16),

                  // Password field
                  AppTextField(
                    controller: _passwordController,
                    labelText: 'Password',
                    prefixIcon: Icons.lock_outline,
                    obscureText: _obscurePassword,
                    validator: Validators.password,
                    textInputAction: TextInputAction.done,
                    onFieldSubmitted: (_) => _handleLogin(),
                    suffixIcon: IconButton(
                      icon: Icon(
                        _obscurePassword
                            ? Icons.visibility_outlined
                            : Icons.visibility_off_outlined,
                      ),
                      onPressed: () {
                        setState(() => _obscurePassword = !_obscurePassword);
                      },
                    ),
                  ),
                  const SizedBox(height: 24),

                  // Login button
                  AppButton(
                    onPressed: _isLoading ? null : _handleLogin,
                    isLoading: _isLoading,
                    text: 'Login',
                  ),
                  const SizedBox(height: 16),

                  // Register link
                  TextButton(
                    onPressed: () {
                      Navigator.pushNamed(context, '/register');
                    },
                    child: const Text(
                      'New user? Create an account',
                      style: TextStyle(fontSize: 16),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildHeader() {
    return Column(
      children: [
        // App icon/logo
        Container(
          width: 100,
          height: 100,
          decoration: BoxDecoration(
            color: AppColors.primary.withOpacity(0.1),
            shape: BoxShape.circle,
          ),
          child: Icon(
            Icons.monitor_weight_outlined,
            size: 50,
            color: AppColors.primary,
          ),
        ),
        const SizedBox(height: 24),
        
        // App name
        Text(
          'Weigh to Go!',
          style: Theme.of(context).textTheme.headlineMedium?.copyWith(
            fontWeight: FontWeight.bold,
            color: AppColors.primary,
          ),
        ),
        const SizedBox(height: 8),
        
        // Tagline
        Text(
          "You've got this—pound for pound",
          style: Theme.of(context).textTheme.bodyLarge?.copyWith(
            color: Colors.grey[600],
            fontStyle: FontStyle.italic,
          ),
        ),
      ],
    );
  }
}
```

### Dashboard Screen

```dart
// lib/screens/dashboard_screen.dart

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/auth_provider.dart';
import '../providers/weight_provider.dart';
import '../widgets/weight_chart.dart';
import '../widgets/goal_progress_card.dart';
import '../widgets/weight_list_tile.dart';
import '../theme/app_colors.dart';

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  int _selectedIndex = 0;

  @override
  void initState() {
    super.initState();
    // Load weight entries when screen initializes
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<WeightProvider>().loadEntries();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Weigh to Go!'),
        actions: [
          IconButton(
            icon: const Icon(Icons.settings_outlined),
            onPressed: () => Navigator.pushNamed(context, '/settings'),
          ),
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: _handleLogout,
          ),
        ],
      ),
      body: _buildBody(),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () => Navigator.pushNamed(context, '/add-weight'),
        icon: const Icon(Icons.add),
        label: const Text('Add Weight'),
        backgroundColor: AppColors.primary,
      ),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _selectedIndex,
        onTap: (index) => setState(() => _selectedIndex = index),
        items: const [
          BottomNavigationBarItem(
            icon: Icon(Icons.dashboard_outlined),
            activeIcon: Icon(Icons.dashboard),
            label: 'Dashboard',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.history_outlined),
            activeIcon: Icon(Icons.history),
            label: 'History',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.insights_outlined),
            activeIcon: Icon(Icons.insights),
            label: 'Stats',
          ),
        ],
      ),
    );
  }

  Widget _buildBody() {
    switch (_selectedIndex) {
      case 0:
        return _buildDashboardView();
      case 1:
        return _buildHistoryView();
      case 2:
        return _buildStatsView();
      default:
        return _buildDashboardView();
    }
  }

  Widget _buildDashboardView() {
    return Consumer<WeightProvider>(
      builder: (context, weightProvider, _) {
        if (weightProvider.isLoading) {
          return const Center(child: CircularProgressIndicator());
        }

        final user = context.read<AuthProvider>().currentUser;
        final latestEntry = weightProvider.latestEntry;
        final recentEntries = weightProvider.entries.take(7).toList();

        return RefreshIndicator(
          onRefresh: () => weightProvider.loadEntries(),
          child: SingleChildScrollView(
            physics: const AlwaysScrollableScrollPhysics(),
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Welcome message
                Text(
                  'Welcome back, ${user?.username ?? 'User'}!',
                  style: Theme.of(context).textTheme.headlineSmall,
                ),
                const SizedBox(height: 24),

                // Goal progress card
                if (user?.goalWeight != null)
                  GoalProgressCard(
                    currentWeight: latestEntry?.weight,
                    goalWeight: user!.goalWeight!,
                    startWeight: weightProvider.entries.isNotEmpty
                        ? weightProvider.entries.last.weight
                        : null,
                  ),
                const SizedBox(height: 24),

                // Weight chart
                if (recentEntries.isNotEmpty) ...[
                  Text(
                    'Last 7 Days',
                    style: Theme.of(context).textTheme.titleMedium,
                  ),
                  const SizedBox(height: 8),
                  SizedBox(
                    height: 200,
                    child: WeightChart(entries: recentEntries),
                  ),
                ] else ...[
                  _buildEmptyState(),
                ],
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildHistoryView() {
    return Consumer<WeightProvider>(
      builder: (context, weightProvider, _) {
        if (weightProvider.isLoading) {
          return const Center(child: CircularProgressIndicator());
        }

        if (weightProvider.entries.isEmpty) {
          return _buildEmptyState();
        }

        return ListView.builder(
          padding: const EdgeInsets.all(16),
          itemCount: weightProvider.entries.length,
          itemBuilder: (context, index) {
            final entry = weightProvider.entries[index];
            return WeightListTile(
              entry: entry,
              onTap: () => _showEntryDetails(entry),
              onDelete: () => _confirmDelete(entry),
            );
          },
        );
      },
    );
  }

  Widget _buildStatsView() {
    return Consumer<WeightProvider>(
      builder: (context, weightProvider, _) {
        final stats = weightProvider.stats;
        
        if (stats.isEmpty) {
          return _buildEmptyState();
        }

        return Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            children: [
              _buildStatCard('Total Entries', stats['count']?.toInt().toString() ?? '0'),
              _buildStatCard('Lowest Weight', '${stats['min']?.toStringAsFixed(1) ?? '--'} lbs'),
              _buildStatCard('Highest Weight', '${stats['max']?.toStringAsFixed(1) ?? '--'} lbs'),
              _buildStatCard('Average Weight', '${stats['avg']?.toStringAsFixed(1) ?? '--'} lbs'),
            ],
          ),
        );
      },
    );
  }

  Widget _buildStatCard(String label, String value) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: ListTile(
        title: Text(label),
        trailing: Text(
          value,
          style: Theme.of(context).textTheme.titleLarge?.copyWith(
            fontWeight: FontWeight.bold,
            color: AppColors.primary,
          ),
        ),
      ),
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.monitor_weight_outlined,
            size: 80,
            color: Colors.grey[400],
          ),
          const SizedBox(height: 16),
          Text(
            'No weight entries yet',
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
              color: Colors.grey[600],
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'Tap the + button to add your first entry',
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
              color: Colors.grey[500],
            ),
          ),
        ],
      ),
    );
  }

  void _handleLogout() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Logout'),
        content: const Text('Are you sure you want to logout?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              context.read<AuthProvider>().logout();
            },
            child: const Text('Logout'),
          ),
        ],
      ),
    );
  }

  void _showEntryDetails(dynamic entry) {
    // Navigate to entry details
  }

  void _confirmDelete(dynamic entry) {
    // Show delete confirmation
  }
}
```

### Weight Entry Screen

```dart
// lib/screens/weight_entry_screen.dart

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:provider/provider.dart';
import 'package:intl/intl.dart';
import '../providers/weight_provider.dart';
import '../models/weight_entry.dart';
import '../widgets/common/app_button.dart';
import '../theme/app_colors.dart';

class WeightEntryScreen extends StatefulWidget {
  final WeightEntry? existingEntry; // For editing

  const WeightEntryScreen({super.key, this.existingEntry});

  @override
  State<WeightEntryScreen> createState() => _WeightEntryScreenState();
}

class _WeightEntryScreenState extends State<WeightEntryScreen> {
  final _formKey = GlobalKey<FormState>();
  final _weightController = TextEditingController();
  final _notesController = TextEditingController();
  DateTime _selectedDate = DateTime.now();
  bool _isLoading = false;

  bool get isEditing => widget.existingEntry != null;

  @override
  void initState() {
    super.initState();
    if (isEditing) {
      _weightController.text = widget.existingEntry!.weight.toString();
      _notesController.text = widget.existingEntry!.notes ?? '';
      _selectedDate = widget.existingEntry!.entryDate;
    }
  }

  @override
  void dispose() {
    _weightController.dispose();
    _notesController.dispose();
    super.dispose();
  }

  Future<void> _selectDate() async {
    final DateTime? picked = await showDatePicker(
      context: context,
      initialDate: _selectedDate,
      firstDate: DateTime(2020),
      lastDate: DateTime.now(),
    );
    if (picked != null && picked != _selectedDate) {
      setState(() => _selectedDate = picked);
    }
  }

  Future<void> _handleSave() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() => _isLoading = true);

    try {
      final weightProvider = context.read<WeightProvider>();
      final weight = double.parse(_weightController.text);
      final notes = _notesController.text.trim();

      bool success;
      if (isEditing) {
        success = await weightProvider.updateEntry(
          widget.existingEntry!.copyWith(
            weight: weight,
            entryDate: _selectedDate,
            notes: notes.isNotEmpty ? notes : null,
          ),
        );
      } else {
        success = await weightProvider.addEntry(
          weight: weight,
          date: _selectedDate,
          notes: notes.isNotEmpty ? notes : null,
        );
      }

      if (success && mounted) {
        Navigator.pop(context);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(isEditing ? 'Entry updated!' : 'Entry added!'),
            backgroundColor: AppColors.success,
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error: ${e.toString()}'),
            backgroundColor: AppColors.error,
          ),
        );
      }
    } finally {
      if (mounted) {
        setState(() => _isLoading = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(isEditing ? 'Edit Entry' : 'Add Weight'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // Weight input with large display
              _buildWeightInput(),
              const SizedBox(height: 32),

              // Date selector
              _buildDateSelector(),
              const SizedBox(height: 24),

              // Notes field
              _buildNotesField(),
              const SizedBox(height: 32),

              // Save button
              AppButton(
                onPressed: _isLoading ? null : _handleSave,
                isLoading: _isLoading,
                text: isEditing ? 'Update' : 'Save',
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildWeightInput() {
    return Column(
      children: [
        TextFormField(
          controller: _weightController,
          keyboardType: const TextInputType.numberWithOptions(decimal: true),
          textAlign: TextAlign.center,
          style: Theme.of(context).textTheme.displayMedium?.copyWith(
            fontWeight: FontWeight.bold,
            color: AppColors.primary,
          ),
          decoration: InputDecoration(
            hintText: '0.0',
            suffixText: 'lbs',
            suffixStyle: Theme.of(context).textTheme.titleLarge,
            border: InputBorder.none,
          ),
          inputFormatters: [
            FilteringTextInputFormatter.allow(RegExp(r'^\d*\.?\d{0,1}')),
          ],
          validator: (value) {
            if (value == null || value.isEmpty) {
              return 'Please enter your weight';
            }
            final weight = double.tryParse(value);
            if (weight == null || weight <= 0 || weight > 1000) {
              return 'Please enter a valid weight';
            }
            return null;
          },
        ),
        const Divider(thickness: 2),
      ],
    );
  }

  Widget _buildDateSelector() {
    return InkWell(
      onTap: _selectDate,
      borderRadius: BorderRadius.circular(12),
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          border: Border.all(color: Colors.grey[300]!),
          borderRadius: BorderRadius.circular(12),
        ),
        child: Row(
          children: [
            Icon(Icons.calendar_today, color: AppColors.primary),
            const SizedBox(width: 16),
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Date',
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: Colors.grey[600],
                  ),
                ),
                Text(
                  DateFormat('EEEE, MMMM d, yyyy').format(_selectedDate),
                  style: Theme.of(context).textTheme.titleMedium,
                ),
              ],
            ),
            const Spacer(),
            Icon(Icons.arrow_drop_down, color: Colors.grey[600]),
          ],
        ),
      ),
    );
  }

  Widget _buildNotesField() {
    return TextFormField(
      controller: _notesController,
      maxLines: 3,
      decoration: InputDecoration(
        labelText: 'Notes (optional)',
        hintText: 'How are you feeling today?',
        alignLabelWithHint: true,
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
        ),
      ),
    );
  }
}
```

---

## State Management

### Authentication Provider

```dart
// lib/providers/auth_provider.dart

import 'package:flutter/material.dart';
import 'package:crypto/crypto.dart';
import 'dart:convert';
import '../models/user.dart';
import '../repositories/user_repository.dart';

class AuthProvider extends ChangeNotifier {
  final UserRepository _userRepository = UserRepository();
  
  User? _currentUser;
  bool _isLoading = false;

  User? get currentUser => _currentUser;
  int? get userId => _currentUser?.id;
  bool get isAuthenticated => _currentUser != null;
  bool get isLoading => _isLoading;

  String _hashPassword(String password) {
    final bytes = utf8.encode(password);
    final digest = sha256.convert(bytes);
    return digest.toString();
  }

  Future<bool> login(String username, String password) async {
    _isLoading = true;
    notifyListeners();

    try {
      final user = await _userRepository.getUserByUsername(username);
      
      if (user == null) {
        return false;
      }

      final passwordHash = _hashPassword(password);
      if (user.passwordHash != passwordHash) {
        return false;
      }

      _currentUser = user;
      notifyListeners();
      return true;
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<bool> register({
    required String username,
    required String password,
    String? email,
    double? goalWeight,
  }) async {
    _isLoading = true;
    notifyListeners();

    try {
      // Check if username exists
      if (await _userRepository.usernameExists(username)) {
        return false;
      }

      final user = User(
        username: username,
        passwordHash: _hashPassword(password),
        email: email,
        goalWeight: goalWeight,
      );

      final id = await _userRepository.createUser(user);
      _currentUser = user.copyWith(id: id);
      notifyListeners();
      return true;
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> updateUser(User user) async {
    await _userRepository.updateUser(user);
    _currentUser = user;
    notifyListeners();
  }

  void logout() {
    _currentUser = null;
    notifyListeners();
  }
}
```

### Weight Provider

```dart
// lib/providers/weight_provider.dart

import 'package:flutter/material.dart';
import '../models/weight_entry.dart';
import '../repositories/weight_repository.dart';

class WeightProvider extends ChangeNotifier {
  final WeightRepository _weightRepository = WeightRepository();
  
  int? _userId;
  List<WeightEntry> _entries = [];
  Map<String, double> _stats = {};
  bool _isLoading = false;

  List<WeightEntry> get entries => _entries;
  Map<String, double> get stats => _stats;
  bool get isLoading => _isLoading;
  
  WeightEntry? get latestEntry => _entries.isNotEmpty ? _entries.first : null;

  void updateUserId(int? userId) {
    if (_userId != userId) {
      _userId = userId;
      if (userId != null) {
        loadEntries();
      } else {
        _entries = [];
        _stats = {};
        notifyListeners();
      }
    }
  }

  Future<void> loadEntries() async {
    if (_userId == null) return;

    _isLoading = true;
    notifyListeners();

    try {
      _entries = await _weightRepository.getWeightEntries(_userId!);
      _stats = await _weightRepository.getWeightStats(_userId!);
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<bool> addEntry({
    required double weight,
    required DateTime date,
    String? notes,
  }) async {
    if (_userId == null) return false;

    try {
      // Check if entry exists for this date
      final existing = await _weightRepository.getEntryByDate(_userId!, date);
      
      if (existing != null) {
        // Update existing entry
        final updated = existing.copyWith(weight: weight, notes: notes);
        await _weightRepository.updateWeightEntry(updated);
      } else {
        // Create new entry
        final entry = WeightEntry(
          userId: _userId!,
          weight: weight,
          entryDate: date,
          notes: notes,
        );
        await _weightRepository.addWeightEntry(entry);
      }

      await loadEntries();
      return true;
    } catch (e) {
      return false;
    }
  }

  Future<bool> updateEntry(WeightEntry entry) async {
    try {
      await _weightRepository.updateWeightEntry(entry);
      await loadEntries();
      return true;
    } catch (e) {
      return false;
    }
  }

  Future<bool> deleteEntry(int id) async {
    try {
      await _weightRepository.deleteWeightEntry(id);
      await loadEntries();
      return true;
    } catch (e) {
      return false;
    }
  }
}
```

---

## Platform-Specific Features

### SMS Notifications (Android Only)

Flutter doesn't have direct SMS sending capability like Android's native SMS Manager. You have two options:

#### Option 1: Use Platform Channels (Direct SMS - Android Only)

```dart
// lib/services/sms_service.dart

import 'package:flutter/services.dart';
import 'dart:io';

class SmsService {
  static const platform = MethodChannel('com.weighto.go/sms');

  static Future<bool> sendSms(String phoneNumber, String message) async {
    if (!Platform.isAndroid) {
      return false; // SMS only supported on Android
    }

    try {
      final result = await platform.invokeMethod('sendSms', {
        'phoneNumber': phoneNumber,
        'message': message,
      });
      return result == true;
    } on PlatformException catch (e) {
      print('Failed to send SMS: ${e.message}');
      return false;
    }
  }

  static Future<bool> hasPermission() async {
    if (!Platform.isAndroid) return false;
    
    try {
      final result = await platform.invokeMethod('checkSmsPermission');
      return result == true;
    } catch (e) {
      return false;
    }
  }

  static Future<bool> requestPermission() async {
    if (!Platform.isAndroid) return false;
    
    try {
      final result = await platform.invokeMethod('requestSmsPermission');
      return result == true;
    } catch (e) {
      return false;
    }
  }
}
```

```kotlin
// android/app/src/main/kotlin/.../MainActivity.kt

package com.example.weigh_to_go

import android.Manifest
import android.content.pm.PackageManager
import android.telephony.SmsManager
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import io.flutter.embedding.android.FlutterActivity
import io.flutter.embedding.engine.FlutterEngine
import io.flutter.plugin.common.MethodChannel

class MainActivity: FlutterActivity() {
    private val CHANNEL = "com.weighto.go/sms"
    private val SMS_PERMISSION_CODE = 100

    override fun configureFlutterEngine(flutterEngine: FlutterEngine) {
        super.configureFlutterEngine(flutterEngine)
        
        MethodChannel(flutterEngine.dartExecutor.binaryMessenger, CHANNEL).setMethodCallHandler { call, result ->
            when (call.method) {
                "sendSms" -> {
                    val phoneNumber = call.argument<String>("phoneNumber")
                    val message = call.argument<String>("message")
                    
                    if (phoneNumber != null && message != null) {
                        val success = sendSms(phoneNumber, message)
                        result.success(success)
                    } else {
                        result.error("INVALID_ARGS", "Phone number and message required", null)
                    }
                }
                "checkSmsPermission" -> {
                    val hasPermission = ContextCompat.checkSelfPermission(
                        this, Manifest.permission.SEND_SMS
                    ) == PackageManager.PERMISSION_GRANTED
                    result.success(hasPermission)
                }
                "requestSmsPermission" -> {
                    ActivityCompat.requestPermissions(
                        this,
                        arrayOf(Manifest.permission.SEND_SMS),
                        SMS_PERMISSION_CODE
                    )
                    result.success(true)
                }
                else -> result.notImplemented()
            }
        }
    }

    private fun sendSms(phoneNumber: String, message: String): Boolean {
        return try {
            val smsManager = SmsManager.getDefault()
            smsManager.sendTextMessage(phoneNumber, null, message, null, null)
            true
        } catch (e: Exception) {
            false
        }
    }
}
```

#### Option 2: Use Local Notifications (Cross-Platform)

```dart
// lib/services/notification_service.dart

import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:timezone/timezone.dart' as tz;
import 'package:timezone/data/latest.dart' as tz;

class NotificationService {
  static final FlutterLocalNotificationsPlugin _notifications =
      FlutterLocalNotificationsPlugin();

  static Future<void> initialize() async {
    tz.initializeTimeZones();

    const androidSettings = AndroidInitializationSettings('@mipmap/ic_launcher');
    const iosSettings = DarwinInitializationSettings(
      requestAlertPermission: true,
      requestBadgePermission: true,
      requestSoundPermission: true,
    );

    const settings = InitializationSettings(
      android: androidSettings,
      iOS: iosSettings,
    );

    await _notifications.initialize(settings);
  }

  static Future<bool> requestPermission() async {
    final android = _notifications.resolvePlatformSpecificImplementation<
        AndroidFlutterLocalNotificationsPlugin>();
    final iOS = _notifications.resolvePlatformSpecificImplementation<
        IOSFlutterLocalNotificationsPlugin>();

    if (android != null) {
      return await android.requestNotificationsPermission() ?? false;
    }
    if (iOS != null) {
      return await iOS.requestPermissions(
        alert: true,
        badge: true,
        sound: true,
      ) ?? false;
    }
    return false;
  }

  static Future<void> scheduleDailyReminder({
    required int hour,
    required int minute,
    required String title,
    required String body,
  }) async {
    await _notifications.zonedSchedule(
      0, // Notification ID
      title,
      body,
      _nextInstanceOfTime(hour, minute),
      const NotificationDetails(
        android: AndroidNotificationDetails(
          'weight_reminder',
          'Weight Reminders',
          channelDescription: 'Daily reminders to log your weight',
          importance: Importance.high,
          priority: Priority.high,
        ),
        iOS: DarwinNotificationDetails(
          presentAlert: true,
          presentBadge: true,
          presentSound: true,
        ),
      ),
      androidScheduleMode: AndroidScheduleMode.exactAllowWhileIdle,
      uiLocalNotificationDateInterpretation:
          UILocalNotificationDateInterpretation.absoluteTime,
      matchDateTimeComponents: DateTimeComponents.time,
    );
  }

  static tz.TZDateTime _nextInstanceOfTime(int hour, int minute) {
    final tz.TZDateTime now = tz.TZDateTime.now(tz.local);
    tz.TZDateTime scheduledDate =
        tz.TZDateTime(tz.local, now.year, now.month, now.day, hour, minute);
    
    if (scheduledDate.isBefore(now)) {
      scheduledDate = scheduledDate.add(const Duration(days: 1));
    }
    return scheduledDate;
  }

  static Future<void> cancelAllReminders() async {
    await _notifications.cancelAll();
  }
}
```

---

## Theming & Styling

### App Theme Configuration

```dart
// lib/theme/app_colors.dart

import 'package:flutter/material.dart';

class AppColors {
  // Primary palette - matching your Android green theme
  static const Color primary = Color(0xFF4CAF50);        // Green 500
  static const Color primaryLight = Color(0xFF81C784);   // Green 300
  static const Color primaryDark = Color(0xFF388E3C);    // Green 700
  
  // Accent colors
  static const Color secondary = Color(0xFF03DAC6);      // Teal
  static const Color accent = Color(0xFFFF9800);         // Orange
  
  // Status colors
  static const Color success = Color(0xFF4CAF50);
  static const Color warning = Color(0xFFFF9800);
  static const Color error = Color(0xFFF44336);
  static const Color info = Color(0xFF2196F3);
  
  // Neutral colors
  static const Color background = Color(0xFFFAFAFA);
  static const Color surface = Color(0xFFFFFFFF);
  static const Color textPrimary = Color(0xFF212121);
  static const Color textSecondary = Color(0xFF757575);
  static const Color divider = Color(0xFFBDBDBD);
  
  // Dark theme colors
  static const Color darkBackground = Color(0xFF121212);
  static const Color darkSurface = Color(0xFF1E1E1E);
  static const Color darkTextPrimary = Color(0xFFFFFFFF);
  static const Color darkTextSecondary = Color(0xFFB3B3B3);
}
```

```dart
// lib/theme/app_theme.dart

import 'package:flutter/material.dart';
import 'app_colors.dart';

class AppTheme {
  static ThemeData get lightTheme {
    return ThemeData(
      useMaterial3: true,
      colorScheme: ColorScheme.fromSeed(
        seedColor: AppColors.primary,
        brightness: Brightness.light,
      ),
      
      // AppBar theme
      appBarTheme: const AppBarTheme(
        centerTitle: true,
        elevation: 0,
        backgroundColor: AppColors.primary,
        foregroundColor: Colors.white,
      ),
      
      // Card theme
      cardTheme: CardTheme(
        elevation: 2,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
        ),
      ),
      
      // Input decoration theme
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: Colors.grey[100],
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: BorderSide.none,
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: BorderSide(color: Colors.grey[300]!),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: AppColors.primary, width: 2),
        ),
        errorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: AppColors.error),
        ),
        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 16),
      ),
      
      // Elevated button theme
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: AppColors.primary,
          foregroundColor: Colors.white,
          minimumSize: const Size(double.infinity, 50),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
          textStyle: const TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.w600,
          ),
        ),
      ),
      
      // Text button theme
      textButtonTheme: TextButtonThemeData(
        style: TextButton.styleFrom(
          foregroundColor: AppColors.primary,
        ),
      ),
      
      // Floating action button theme
      floatingActionButtonTheme: const FloatingActionButtonThemeData(
        backgroundColor: AppColors.primary,
        foregroundColor: Colors.white,
      ),
      
      // Bottom navigation bar theme
      bottomNavigationBarTheme: const BottomNavigationBarThemeData(
        selectedItemColor: AppColors.primary,
        unselectedItemColor: Colors.grey,
        showUnselectedLabels: true,
        type: BottomNavigationBarType.fixed,
      ),
    );
  }

  static ThemeData get darkTheme {
    return ThemeData(
      useMaterial3: true,
      colorScheme: ColorScheme.fromSeed(
        seedColor: AppColors.primary,
        brightness: Brightness.dark,
      ),
      scaffoldBackgroundColor: AppColors.darkBackground,
      
      appBarTheme: const AppBarTheme(
        centerTitle: true,
        elevation: 0,
        backgroundColor: AppColors.darkSurface,
      ),
      
      cardTheme: CardTheme(
        color: AppColors.darkSurface,
        elevation: 2,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
        ),
      ),
      
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: AppColors.darkSurface,
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: BorderSide.none,
        ),
        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 16),
      ),
      
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: AppColors.primary,
          foregroundColor: Colors.white,
          minimumSize: const Size(double.infinity, 50),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
        ),
      ),
    );
  }
}
```

### Reusable Widget Components

```dart
// lib/widgets/common/app_text_field.dart

import 'package:flutter/material.dart';

class AppTextField extends StatelessWidget {
  final TextEditingController controller;
  final String labelText;
  final String? hintText;
  final IconData? prefixIcon;
  final Widget? suffixIcon;
  final bool obscureText;
  final TextInputType? keyboardType;
  final TextInputAction? textInputAction;
  final String? Function(String?)? validator;
  final void Function(String)? onFieldSubmitted;
  final int maxLines;

  const AppTextField({
    super.key,
    required this.controller,
    required this.labelText,
    this.hintText,
    this.prefixIcon,
    this.suffixIcon,
    this.obscureText = false,
    this.keyboardType,
    this.textInputAction,
    this.validator,
    this.onFieldSubmitted,
    this.maxLines = 1,
  });

  @override
  Widget build(BuildContext context) {
    return TextFormField(
      controller: controller,
      obscureText: obscureText,
      keyboardType: keyboardType,
      textInputAction: textInputAction,
      validator: validator,
      onFieldSubmitted: onFieldSubmitted,
      maxLines: maxLines,
      decoration: InputDecoration(
        labelText: labelText,
        hintText: hintText,
        prefixIcon: prefixIcon != null ? Icon(prefixIcon) : null,
        suffixIcon: suffixIcon,
      ),
    );
  }
}
```

```dart
// lib/widgets/common/app_button.dart

import 'package:flutter/material.dart';
import '../../theme/app_colors.dart';

class AppButton extends StatelessWidget {
  final VoidCallback? onPressed;
  final String text;
  final bool isLoading;
  final bool isOutlined;
  final IconData? icon;

  const AppButton({
    super.key,
    required this.onPressed,
    required this.text,
    this.isLoading = false,
    this.isOutlined = false,
    this.icon,
  });

  @override
  Widget build(BuildContext context) {
    final child = isLoading
        ? const SizedBox(
            height: 20,
            width: 20,
            child: CircularProgressIndicator(
              strokeWidth: 2,
              valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
            ),
          )
        : Row(
            mainAxisSize: MainAxisSize.min,
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              if (icon != null) ...[
                Icon(icon, size: 20),
                const SizedBox(width: 8),
              ],
              Text(text),
            ],
          );

    if (isOutlined) {
      return OutlinedButton(
        onPressed: isLoading ? null : onPressed,
        style: OutlinedButton.styleFrom(
          minimumSize: const Size(double.infinity, 50),
          side: const BorderSide(color: AppColors.primary),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
        ),
        child: child,
      );
    }

    return ElevatedButton(
      onPressed: isLoading ? null : onPressed,
      child: child,
    );
  }
}
```

---

## Testing Strategy

### Unit Tests

```dart
// test/unit/user_repository_test.dart

import 'package:flutter_test/flutter_test.dart';
import 'package:mockito/mockito.dart';
import 'package:weigh_to_go/models/user.dart';
import 'package:weigh_to_go/repositories/user_repository.dart';

void main() {
  group('UserRepository', () {
    late UserRepository repository;

    setUp(() {
      repository = UserRepository();
    });

    test('creates user successfully', () async {
      final user = User(
        username: 'testuser',
        passwordHash: 'hashedpassword',
      );

      final id = await repository.createUser(user);
      expect(id, greaterThan(0));
    });

    test('retrieves user by username', () async {
      final user = await repository.getUserByUsername('testuser');
      expect(user, isNotNull);
      expect(user!.username, equals('testuser'));
    });

    test('returns null for non-existent user', () async {
      final user = await repository.getUserByUsername('nonexistent');
      expect(user, isNull);
    });
  });
}
```

### Widget Tests

```dart
// test/widget/login_screen_test.dart

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:provider/provider.dart';
import 'package:weigh_to_go/screens/login_screen.dart';
import 'package:weigh_to_go/providers/auth_provider.dart';

void main() {
  group('LoginScreen', () {
    testWidgets('displays login form', (WidgetTester tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: ChangeNotifierProvider(
            create: (_) => AuthProvider(),
            child: const LoginScreen(),
          ),
        ),
      );

      expect(find.text('Weigh to Go!'), findsOneWidget);
      expect(find.byType(TextField), findsNWidgets(2));
      expect(find.text('Login'), findsOneWidget);
    });

    testWidgets('validates empty fields', (WidgetTester tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: ChangeNotifierProvider(
            create: (_) => AuthProvider(),
            child: const LoginScreen(),
          ),
        ),
      );

      await tester.tap(find.text('Login'));
      await tester.pump();

      expect(find.text('Please enter your username'), findsOneWidget);
    });
  });
}
```

---

## Build & Deployment

### Building for Android

```bash
# Debug APK
flutter build apk --debug

# Release APK
flutter build apk --release

# App Bundle (recommended for Play Store)
flutter build appbundle --release

# Output locations:
# build/app/outputs/flutter-apk/app-release.apk
# build/app/outputs/bundle/release/app-release.aab
```

### Building for iOS

```bash
# Requires macOS with Xcode

# Build for iOS
flutter build ios --release

# Create IPA (requires Apple Developer account)
flutter build ipa --release

# Output location:
# build/ios/ipa/
```

### Building for Web

```bash
# Build web app
flutter build web --release

# Output location:
# build/web/

# Deploy to Firebase Hosting (example)
firebase deploy --only hosting
```

### Platform-Specific Configuration

```yaml
# android/app/build.gradle

android {
    compileSdkVersion 34
    
    defaultConfig {
        applicationId "com.example.weigh_to_go"
        minSdkVersion 21
        targetSdkVersion 34
        versionCode 1
        versionName "1.0.0"
    }
    
    buildTypes {
        release {
            signingConfig signingConfigs.release
            minifyEnabled true
            shrinkResources true
        }
    }
}
```

```xml
<!-- android/app/src/main/AndroidManifest.xml -->

<manifest xmlns:android="http://schemas.android.com/apk/res/android">
    <!-- Permissions -->
    <uses-permission android:name="android.permission.SEND_SMS" />
    <uses-permission android:name="android.permission.RECEIVE_BOOT_COMPLETED"/>
    <uses-permission android:name="android.permission.VIBRATE"/>
    <uses-permission android:name="android.permission.USE_EXACT_ALARM"/>
    
    <application
        android:label="Weigh to Go!"
        android:icon="@mipmap/ic_launcher"
        android:roundIcon="@mipmap/ic_launcher_round">
        
        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:launchMode="singleTop"
            android:theme="@style/LaunchTheme">
            <intent-filter>
                <action android:name="android.intent.action.MAIN"/>
                <category android:name="android.intent.category.LAUNCHER"/>
            </intent-filter>
        </activity>
        
        <!-- Notification receivers -->
        <receiver android:name="com.dexterous.flutterlocalnotifications.ScheduledNotificationBootReceiver"
            android:exported="false">
            <intent-filter>
                <action android:name="android.intent.action.BOOT_COMPLETED"/>
            </intent-filter>
        </receiver>
    </application>
</manifest>
```

---

## Migration Checklist

### Phase 1: Environment Setup ✅
- [ ] Install Flutter SDK
- [ ] Configure IDE (VS Code or Android Studio)
- [ ] Run `flutter doctor` successfully
- [ ] Create new Flutter project
- [ ] Set up project structure

### Phase 2: Core Infrastructure ✅
- [ ] Add dependencies to `pubspec.yaml`
- [ ] Create database service
- [ ] Create model classes (User, WeightEntry)
- [ ] Create repository classes
- [ ] Test database operations

### Phase 3: State Management ✅
- [ ] Create AuthProvider
- [ ] Create WeightProvider
- [ ] Configure Provider in main.dart
- [ ] Test authentication flow

### Phase 4: UI Implementation ✅
- [ ] Configure app theme and colors
- [ ] Create reusable widget components
- [ ] Build Login screen
- [ ] Build Registration screen
- [ ] Build Dashboard screen
- [ ] Build Weight Entry screen
- [ ] Build Settings screen

### Phase 5: Features ✅
- [ ] Implement weight chart visualization
- [ ] Implement goal progress tracking
- [ ] Implement notifications (local or SMS)
- [ ] Add unit conversion (lbs/kg)
- [ ] Implement data export

### Phase 6: Polish ✅
- [ ] Add loading states
- [ ] Add error handling
- [ ] Implement form validation
- [ ] Add animations and transitions
- [ ] Test on multiple screen sizes

### Phase 7: Testing ✅
- [ ] Write unit tests for repositories
- [ ] Write unit tests for providers
- [ ] Write widget tests for screens
- [ ] Perform manual testing on Android
- [ ] Perform manual testing on iOS
- [ ] Perform manual testing on Web

### Phase 8: Deployment ✅
- [ ] Configure Android signing
- [ ] Configure iOS signing (if applicable)
- [ ] Build release APK
- [ ] Build release IPA (if applicable)
- [ ] Build web version
- [ ] Create app store listings

---

## Resources & References

### Official Documentation
- [Flutter Documentation](https://docs.flutter.dev/)
- [Dart Language Tour](https://dart.dev/language)
- [Material Design 3](https://m3.material.io/)

### Key Packages
- [sqflite](https://pub.dev/packages/sqflite) - SQLite database
- [provider](https://pub.dev/packages/provider) - State management
- [fl_chart](https://pub.dev/packages/fl_chart) - Charts and graphs
- [flutter_local_notifications](https://pub.dev/packages/flutter_local_notifications) - Notifications
- [permission_handler](https://pub.dev/packages/permission_handler) - Runtime permissions

### Learning Resources
- [Flutter Codelabs](https://docs.flutter.dev/codelabs)
- [Flutter YouTube Channel](https://www.youtube.com/c/flutterdev)
- [Dart Packages](https://pub.dev/)

### Community
- [Flutter Discord](https://discord.gg/flutter)
- [Stack Overflow - Flutter](https://stackoverflow.com/questions/tagged/flutter)
- [r/FlutterDev](https://reddit.com/r/FlutterDev)

---

## Document History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | December 15, 2025 | Initial migration guide |

---

**Prepared for**: Rick Goshen  
**Course**: CS 360 - Mobile Architecture & Programming  
**Purpose**: Cross-platform migration of Weigh to Go! application

---

*"You've got this—pound for pound"* 🏆
