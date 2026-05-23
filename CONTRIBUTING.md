# Contributing to Weigh to Go! 🎉

First off, thank you for considering contributing to **Weigh to Go!** Every contribution helps make this app better for everyone trying to achieve their health goals.

> **"You've got this—pound for pound."** — And so do we, together!

---

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Code Style Guidelines](#code-style-guidelines)
- [Commit Message Guidelines](#commit-message-guidelines)
- [Pull Request Process](#pull-request-process)
- [Issue Guidelines](#issue-guidelines)
- [Recognition](#recognition)

---

## 📜 Code of Conduct

### Our Pledge

We are committed to providing a friendly, safe, and welcoming environment for all contributors regardless of experience level, gender identity, sexual orientation, disability, personal appearance, body size, race, ethnicity, age, religion, or nationality.

### Our Standards

**Examples of behavior that contributes to a positive environment:**

- ✅ Using welcoming and inclusive language
- ✅ Being respectful of differing viewpoints and experiences
- ✅ Gracefully accepting constructive criticism
- ✅ Focusing on what is best for the community
- ✅ Showing empathy towards other community members

**Examples of unacceptable behavior:**

- ❌ Trolling, insulting/derogatory comments, and personal attacks
- ❌ Public or private harassment
- ❌ Publishing others' private information without permission
- ❌ Other conduct which could reasonably be considered inappropriate

### Enforcement

Instances of abusive, harassing, or otherwise unacceptable behavior may be reported by contacting the project maintainer. All complaints will be reviewed and investigated promptly and fairly.

---

## 🚀 Getting Started

### Prerequisites

WeighToGo is a polyglot monorepo — the Android codebase lives under `android/` and
the web rebuild lives under `web/`. Install only the prerequisites for the stack
you intend to work on.

**Shared (any contribution):**

- Git installed and configured
- A GitHub account
- [pre-commit](https://pre-commit.com/) (`pip install pre-commit` or `brew install pre-commit`) — runs lint, format, type-check, and tests on staged files

**Android (`android/`):**

- [Android Studio](https://developer.android.com/studio) Ladybug (2024.2.1+)
- [JDK 21](https://adoptium.net/) or higher
- Android SDK 34 (Android 14)

**Web (`web/`):**

- [Python 3.12+](https://www.python.org/) and [uv](https://docs.astral.sh/uv/) — backend
- [Node.js 20.19+ or 22+](https://nodejs.org/) — frontend
- [Docker](https://www.docker.com/) and Docker Compose — local PostgreSQL

The full quality-gate matrix (linters, type-checkers, test runners, coverage
thresholds) is specified in the SRS §11 (Quality Engineering).

### Fork and Clone

1. **Fork** the repository on GitHub
2. **Clone** your fork locally:

```bash
git clone https://github.com/YOUR-USERNAME/WeighToGo.git
cd WeighToGo
```

3. **Add upstream** remote:

```bash
git remote add upstream https://github.com/rgoshen-snhu/WeighToGo.git
```

4. **Keep your fork synced**:

```bash
git fetch upstream
git checkout main
git merge upstream/main
```

---

## 🤝 How Can I Contribute?

### 🐛 Reporting Bugs

Found a bug? Please help us fix it!

**Before submitting a bug report:**

1. Check the [existing issues](https://github.com/rgoshen-snhu/WeighToGo/issues) to avoid duplicates
2. Ensure you're using the latest version
3. Collect information about the bug:
   - Android version and device model
   - Steps to reproduce
   - Expected vs. actual behavior
   - Screenshots or screen recordings (if applicable)
   - Logcat output (if applicable)

**Submit a bug report** using the Bug Report issue template.

### 💡 Suggesting Features

Have an idea to improve Weigh to Go!?

**Before submitting a feature request:**

1. Check the [roadmap in README.md](README.md#roadmap) to see if it's planned
2. Search existing issues for similar suggestions
3. Consider if the feature aligns with the app's simplicity-focused design

**Submit a feature request** using the Feature Request issue template.

### 📝 Improving Documentation

Documentation improvements are always welcome:

- Fix typos or clarify existing documentation
- Add examples or tutorials
- Improve code comments
- Translate documentation

### 💻 Contributing Code

Ready to write some code? Here's what we need help with:

- **Bug fixes** - Check issues labeled `bug`
- **New features** - Check issues labeled `enhancement`
- **Tests** - Improve test coverage
- **Refactoring** - Improve code quality
- **Performance** - Optimize app performance

---

## 🛠️ Development Setup

### Activate pre-commit hooks (any stack)

After cloning, install the hooks once:

```bash
pre-commit install
```

The hooks are scoped per stack — backend hooks fire only on `web/backend/*.py`,
frontend hooks fire only on `web/frontend/**` — so contributions that don't
touch a stack don't pay its cost.

### Android (`android/`)

**1. Import Project**

1. Open Android Studio
2. Select **File → Open**
3. Navigate to the `android/` directory inside your clone (the Gradle project root)
4. Wait for Gradle sync to complete

**2. Configure Code Style**

Import our code style settings:

1. **File → Settings → Editor → Code Style**
2. Click the gear icon → **Import Scheme**
3. Select `config/codestyle.xml` (if available)

Or manually configure:

- **Indentation:** 4 spaces (no tabs)
- **Line length:** 120 characters max
- **Braces:** Same line (K&R style)

**3. Run Tests**

```bash
cd android

# Unit tests
./gradlew test

# Instrumented tests
./gradlew connectedAndroidTest

# Lint
./gradlew lint
```

### Web Backend (`web/backend/`)

```bash
cd web/backend
cp .env.example .env             # adjust values as needed
docker compose up -d             # start local PostgreSQL
uv sync                          # install dependencies
uv run alembic upgrade head      # apply database migrations

# Run the dev server
uv run uvicorn weighttogo.main:app --reload

# Quality gates (also run by pre-commit and CI)
uv run ruff check .              # lint
uv run ruff format .             # format
uv run mypy                      # type-check
uv run pytest                    # tests (coverage thresholds enforced)
uv run pytest --cov              # explicit coverage report
```

The API serves at `http://localhost:8000`; `GET /health` reports service status.
The OpenAPI snapshot at `docs/api/openapi.json` is regenerated as part of
release closeout — do not edit it by hand.

### Web Frontend (`web/frontend/`)

```bash
cd web/frontend
cp .env.example .env             # adjust values as needed
npm install

# Run the dev server
npm run dev

# Quality gates (also run by pre-commit and CI)
npm run lint                     # eslint
npm run format:check             # prettier (write with `npm run format`)
npm run typecheck                # tsc
npm test                         # vitest (coverage thresholds enforced)
npm run test:e2e                 # playwright (requires backend running)
```

The frontend serves at `http://localhost:5173` and proxies API calls to the
backend dev server.

### Create a Branch

Branch names use the `feature/`, `fix/`, `docs/`, or `chore/` prefix:

```bash
git checkout -b feature/your-feature-name
git checkout -b fix/bug-description
```

---

## 🧪 Testing Strategy

### When to Use Mocks vs Real Database

**Use Mocks** (Mockito) for:
- **Unit tests** - Testing business logic in isolation
- **Activity tests** - Testing UI behavior and interactions
- **Fast feedback** - Tests that need to run quickly
- **Edge cases** - Simulating error conditions, null returns, etc.

**Example**: `MainActivityTest` uses Mockito mocks to test authentication redirect without real database.

**Use Real Database** (Integration tests) for:
- **DAO tests** - Verifying SQL queries and database constraints
- **Data integrity** - Testing transactions, foreign keys, unique constraints
- **Multi-step workflows** - Testing end-to-end data flows
- **Migration verification** - Ensuring database schema changes work correctly

**Example**: `LoginActivityIntegrationTest` uses real database to verify DAO/SessionManager integration.

### Dependency Injection for Testing

Activities use **package-private setter injection** to allow test code to inject mocks:

```java
// Production code (Activity)
private UserDAO userDAO;

void setUserDAO(UserDAO userDAO) {
    if (userDAO == null) {
        throw new IllegalArgumentException("UserDAO cannot be null");
    }
    this.userDAO = userDAO;
}

private void initDataLayer() {
    if (userDAO == null) {
        userDAO = new UserDAO(WeighToGoDBHelper.getInstance(this));
    }
}
```

```java
// Test code
@Mock private UserDAO mockUserDAO;

@Before
public void setUp() {
    MockitoAnnotations.openMocks(this);

    ActivityController<MainActivity> controller = Robolectric.buildActivity(MainActivity.class);
    activity = controller.get();

    // Inject mocks BEFORE onCreate()
    activity.setUserDAO(mockUserDAO);

    // Set default behaviors
    when(mockUserDAO.getUserById(1L)).thenReturn(testUser);

    // NOW call lifecycle methods
    controller.create().start().resume();
}
```

### Mock Stubbing Best Practices

Always stub mock method calls that return values:

```java
@Before
public void setUp() {
    // Stub DAO insert methods to return realistic IDs
    when(mockWeightEntryDAO.insertWeightEntry(any(WeightEntry.class)))
            .thenAnswer(invocation -> System.currentTimeMillis() % 1000000);

    when(mockGoalWeightDAO.insertGoal(any(GoalWeight.class)))
            .thenReturn(1L);

    // Stub getter methods
    when(mockUserDAO.getUserById(testUserId)).thenReturn(testUser);
}
```

### Verification

Use `verify()` to ensure mocked methods are called:

```java
@Test
public void test_login_callsSessionManager() {
    // ACT
    loginButton.performClick();

    // ASSERT
    verify(mockSessionManager).createSession(any(User.class));
}
```

**See Also**:
- ADR-0005: Dependency Injection for Testing
- `docs/architecture/WeighToGo_Database_Architecture.md` for DAO testing guidelines

---

## 📏 Code Style Guidelines

Code style is enforced by tooling on every commit — `pre-commit` runs the
appropriate linter/formatter per stack. The sections below describe conventions
beyond what the tools auto-fix.

### Python Style (Web Backend)

- **Formatter and linter:** `ruff` (configured in `web/backend/pyproject.toml`) — formats and lints; do not bypass.
- **Type-checker:** `mypy` strict mode — every public function annotated.
- **Imports:** `ruff` auto-sorts; never edit import order manually.
- **Domain code under `web/backend/src/weighttogo/domain/`** must not import FastAPI, SQLAlchemy, or any infrastructure framework — this is the dependency rule from ADR-0012 (Three-Pattern Backend Architecture) and is enforced by `import-linter` in CI.

### TypeScript Style (Web Frontend)

- **Formatter:** `prettier` (configured in `web/frontend/.prettierrc`).
- **Linter:** `eslint` with `@typescript-eslint`; strict rules — no `any`, no unused exports.
- **Type-checker:** `tsc --noEmit` runs in CI; `strict: true` in `tsconfig.json`.
- **Component naming:** PascalCase; one component per file when feasible.
- **Server state:** managed via TanStack Query (per ADR-0014) — no ad-hoc `useEffect` fetches.

### Java Style Guide

We follow the [Google Java Style Guide](https://google.github.io/styleguide/javaguide.html) with these specifics:

#### Naming Conventions

```java
// Classes: PascalCase
public class WeightEntryActivity { }

// Methods: camelCase (verb phrases)
public void saveWeightEntry() { }

// Variables: camelCase
private float currentWeight;

// Constants: SCREAMING_SNAKE_CASE
public static final int MAX_WEIGHT = 1000;

// Layout IDs: snake_case with type prefix
// button_save, text_weight_display, edit_password

// Resource files: snake_case
// activity_main.xml, item_weight_history.xml
```

#### Code Organization

```java
public class ExampleActivity extends AppCompatActivity {
    
    // 1. Constants
    private static final String TAG = "ExampleActivity";
    
    // 2. Static fields
    private static int instanceCount = 0;
    
    // 3. Instance fields (UI elements first, then data)
    private Button btnSave;
    private EditText etWeight;
    private WeightDAO weightDAO;
    
    // 4. Lifecycle methods (in order)
    @Override
    protected void onCreate(Bundle savedInstanceState) { }
    
    @Override
    protected void onResume() { }
    
    @Override
    protected void onPause() { }
    
    // 5. UI initialization
    private void initViews() { }
    
    private void setupListeners() { }
    
    // 6. Business logic methods
    private void saveWeight() { }
    
    private void validateInput() { }
    
    // 7. Helper/utility methods
    private String formatWeight(float weight) { }
}
```

#### Comments

```java
// Use Javadoc for public methods
/**
 * Saves the weight entry to the database.
 *
 * @param weight The weight value in the user's preferred unit
 * @param date   The date of the weight entry
 * @return true if save was successful, false otherwise
 */
public boolean saveWeightEntry(float weight, String date) { }

// Use inline comments sparingly, for complex logic
// Calculate progress percentage (avoid division by zero)
float progress = (startWeight - currentWeight) / Math.max(startWeight - goalWeight, 0.1f);
```

### XML Layout Guidelines

```xml
<!-- Use consistent attribute ordering -->
<Button
    android:id="@+id/btn_save"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:layout_marginStart="16dp"
    android:layout_marginEnd="16dp"
    android:text="@string/save"
    android:textColor="@color/white"
    android:background="@drawable/btn_primary" />

<!-- Attribute order:
     1. android:id
     2. android:layout_width, layout_height
     3. android:layout_* (margins, constraints)
     4. android:* (other android attrs)
     5. app:* (custom/library attrs)
     6. tools:* (design-time attrs)
-->
```

### Resource Naming

| Type | Convention | Example |
|------|------------|---------|
| Layout | `<type>_<description>` | `activity_login.xml` |
| Drawable | `<type>_<description>` | `ic_weight.xml`, `bg_card.xml` |
| String | `<screen>_<description>` | `login_title`, `dashboard_greeting` |
| Color | `<description>` | `primary_teal`, `text_secondary` |
| Dimen | `<type>_<description>` | `margin_standard`, `text_headline` |

---

## 💬 Commit Message Guidelines

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification.

### Format

```
<type>(<scope>): <subject>

[optional body]

[optional footer]
```

### Types

| Type | Description |
|------|-------------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation changes |
| `style` | Code style (formatting, no logic change) |
| `refactor` | Code refactoring |
| `test` | Adding/updating tests |
| `chore` | Build, config, or tooling changes |

### Examples

```bash
# Feature
feat(weight-entry): add unit toggle for lbs/kg conversion

# Bug fix
fix(database): resolve crash when saving null date

# Documentation
docs(readme): update installation instructions

# Refactoring
refactor(login): extract validation logic to utility class

# With body and footer
feat(notifications): add goal achievement celebration

Implement push notification when user reaches goal weight.
Includes custom celebration animation and sound.

Closes #42
```

### Rules

- Use **imperative mood** ("add" not "added" or "adds")
- **Don't capitalize** the subject line
- **No period** at the end of subject
- Keep subject line **under 50 characters**
- Wrap body at **72 characters**
- Reference issues in footer with `Closes #XX` or `Fixes #XX`

---

## 🔄 Pull Request Process

### Before Submitting

- [ ] Code follows style guidelines
- [ ] Self-reviewed my code
- [ ] Added comments for complex logic
- [ ] Updated documentation if needed
- [ ] All tests pass locally
- [ ] No new warnings introduced
- [ ] Branch is up-to-date with `main`

### Submitting a PR

1. **Push your branch:**

```bash
git push origin feature/your-feature-name
```

2. **Open a Pull Request** on GitHub

3. **Fill out the PR template** completely:
   - Clear title following commit conventions
   - Description of changes
   - Link to related issue(s)
   - Screenshots for UI changes
   - Testing instructions

4. **Request review** from maintainers

### PR Title Format

```
feat(scope): brief description
fix(scope): brief description
docs(scope): brief description
```

### Review Process

1. **Automated checks** must pass (build, tests, lint)
2. **Code review** by at least one maintainer
3. **Address feedback** via additional commits
4. **Squash and merge** when approved

### After Merge

- Delete your feature branch
- Update your local `main`:

```bash
git checkout main
git pull upstream main
git push origin main
```

---

## 📝 Issue Guidelines

### Bug Report Template

The canonical templates live in `.github/ISSUE_TEMPLATE/`. The skeleton below
covers the common fields; add stack-specific information based on where the bug
occurred.

```markdown
**Stack:** Android / Web (frontend / backend) / Cross-stack

**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce:
1. Go to '...'
2. Click on '...'
3. Scroll down to '...'
4. See error

**Expected behavior**
What you expected to happen.

**Screenshots**
If applicable, add screenshots.

**Environment (Android):**
 - Device: [e.g., Pixel 7]
 - Android Version: [e.g., 14]
 - App Version: [e.g., 1.0.0]

**Environment (Web):**
 - Browser and version: [e.g., Chrome 130, Firefox 132]
 - OS: [e.g., macOS 14, Windows 11]
 - Backend commit / tag (if reproducible against a specific build)
 - Console errors or backend log excerpt (redact PII)

**Additional context**
Any other context about the problem.
```

### Feature Request Template

```markdown
**Is your feature request related to a problem?**
A clear description of what the problem is.

**Describe the solution you'd like**
What you want to happen.

**Describe alternatives you've considered**
Any alternative solutions you've considered.

**Additional context**
Any other context or screenshots.
```

---

## 🏆 Recognition

Contributors will be recognized in:

- **README.md** - Listed in Contributors section
- **Release notes** - Mentioned for significant contributions
- **GitHub** - All contributors visible in repository

### All Contributors

We use the [All Contributors](https://allcontributors.org/) specification. Contributions of any kind are welcome!

| Emoji | Contribution Type |
|-------|------------------|
| 💻 | Code |
| 📖 | Documentation |
| 🐛 | Bug reports |
| 💡 | Ideas/suggestions |
| 🎨 | Design |
| 🔧 | Tools/infrastructure |
| ⚠️ | Tests |
| 🌍 | Translation |

---

## ❓ Questions?

- **General questions:** Open a [Discussion](https://github.com/rgoshen-snhu/WeighToGo/discussions)
- **Bug or feature:** Open an [Issue](https://github.com/rgoshen-snhu/WeighToGo/issues)
- **Security issues:** Email the maintainer directly (do not open a public issue)

---

## 📚 Resources

**Project-specific**

- [Software Requirements Specification](docs/specs/WeighToGo_Web_SRS_v2.md) — authoritative for the web rebuild
- [Architecture Decision Records](docs/adr/README.md) — numbered engineering decisions
- [Design Decision Records](docs/ddr/README.md) — numbered design decisions

**Web stack**

- [FastAPI](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0](https://docs.sqlalchemy.org/en/20/)
- [Pydantic v2](https://docs.pydantic.dev/)
- [React 19](https://react.dev/)
- [TanStack Query v5](https://tanstack.com/query/latest)
- [Material UI v9](https://mui.com/)
- [Playwright](https://playwright.dev/)

**Android stack**

- [Android Developer Guides](https://developer.android.com/guide)
- [Material Design Guidelines](https://material.io/design)
- [Java Style Guide](https://google.github.io/styleguide/javaguide.html)

**Workflow**

- [Git Workflow](https://www.atlassian.com/git/tutorials/comparing-workflows)
- [Conventional Commits](https://www.conventionalcommits.org/)

---

<p align="center">
  <strong>Thank you for contributing to Weigh to Go!</strong><br>
  You've got this—pound for pound. 🎉
</p>
