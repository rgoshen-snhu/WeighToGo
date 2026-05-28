# Changelog

## [0.1.0](https://github.com/rgoshen-snhu/WeighToGo/compare/v0.1.0...v0.1.0) (2026-05-28)


### Added

* **F1:** add HSTS and path-aware CSP security headers (GH-34) ([#35](https://github.com/rgoshen-snhu/WeighToGo/issues/35)) ([364eee6](https://github.com/rgoshen-snhu/WeighToGo/commit/364eee67b1a354175551f19e7be1adf1f26c4667))
* **F2:** add CSRF Origin/Referer validation middleware (GH-34) ([#37](https://github.com/rgoshen-snhu/WeighToGo/issues/37)) ([1c8fc33](https://github.com/rgoshen-snhu/WeighToGo/commit/1c8fc33746ce3650c34c4a3407e8d927b3cfa33e))
* **F3:** coalesce concurrent 401 refresh calls via shared promise (GH-34) ([ff0450b](https://github.com/rgoshen-snhu/WeighToGo/commit/ff0450bbf26ac072b3cd5beb125ed01b6bf285f1))
* **F3:** coalesce concurrent 401 refresh calls via shared promise (GH-34) ([4b82435](https://github.com/rgoshen-snhu/WeighToGo/commit/4b824356237eaa824ffc589f63f0acd0891d26ee))
* **F5:** convert weight table actions to Button meeting 44px target (GH-34) ([c758bd9](https://github.com/rgoshen-snhu/WeighToGo/commit/c758bd9955d318081f5c75ac01a8ab9dbd666f24))
* **F5:** meet 44px target size for weight table actions (GH-34) ([0df4751](https://github.com/rgoshen-snhu/WeighToGo/commit/0df47516b072484e280224d40bf44d631edbb635))


### Fixed

* **F3:** guard against synchronous throws from interceptor.refresh() (GH-34) ([0414e98](https://github.com/rgoshen-snhu/WeighToGo/commit/0414e98fc9fcfb0ee07f4a53aec17c900ce6e13e))
* **F4:** address PR [#39](https://github.com/rgoshen-snhu/WeighToGo/issues/39) review — neutral copy + parameterized invariant test (GH-34) ([af5c37b](https://github.com/rgoshen-snhu/WeighToGo/commit/af5c37b4c76bee806f061c12008cd53b0fb09b08))
* **F4:** remove email-existence disclosure on registration (GH-34) ([9e27394](https://github.com/rgoshen-snhu/WeighToGo/commit/9e27394391dd32761b1d1b1afa7ec7086eed270c))
* **F4:** use generic creation-failure message for ApiError (GH-34) ([ff3d2bd](https://github.com/rgoshen-snhu/WeighToGo/commit/ff3d2bd2b5792faaa5dab166ec7cf6add4b32f39))
* **F5:** address PR [#40](https://github.com/rgoshen-snhu/WeighToGo/issues/40) review — move 44px floor to theme; minWidth + comment fixes (GH-34) ([5d4fc08](https://github.com/rgoshen-snhu/WeighToGo/commit/5d4fc0895f0e2c03c0f6a05125cc550666a79930))


### Changed

* **auth:** consolidate ADR-0010 auth-safe message strings into a shared module (GH-42) ([#46](https://github.com/rgoshen-snhu/WeighToGo/issues/46)) ([eacba23](https://github.com/rgoshen-snhu/WeighToGo/commit/eacba23f2855c3df04f4b9666e75621ffa5eb751))
* **F3:** address PR review comments — ix capture, auth401 helper, test hardening (GH-34) ([db45329](https://github.com/rgoshen-snhu/WeighToGo/commit/db453293cc30b65b3d4439cab5de4ec053d6750d))


### Documentation

* add design document for consolidating ADR-0010 auth-safe messag… ([424cddb](https://github.com/rgoshen-snhu/WeighToGo/commit/424cddb61981e3e4cffd5905ea3d87d6f8fdba30))
* add design document for consolidating ADR-0010 auth-safe message strings ([4fa42f2](https://github.com/rgoshen-snhu/WeighToGo/commit/4fa42f2dd389ed71cb216726e07f18bd855ecaca))
* **closeout:** record Resolution Review for issue [#34](https://github.com/rgoshen-snhu/WeighToGo/issues/34) (GH-34) ([edcac82](https://github.com/rgoshen-snhu/WeighToGo/commit/edcac82e83ff86202447af65d19512ae03fb1236))
* **closeout:** Resolution Review for issue [#34](https://github.com/rgoshen-snhu/WeighToGo/issues/34) (PR 7, GH-34) ([90e3f79](https://github.com/rgoshen-snhu/WeighToGo/commit/90e3f79dc5304b2cba91654b93ff82365e97d5c8))
* **F3:** add ADR-0018 concurrent refresh token coalescing (GH-34) ([a994e21](https://github.com/rgoshen-snhu/WeighToGo/commit/a994e219624971210c2c770f2a4e61141b96d396))
* **F4:** summary entry (GH-34) ([32c16d7](https://github.com/rgoshen-snhu/WeighToGo/commit/32c16d75d0d6a55a44617494130292c83ae80c3d))
* **F5:** add DDR-0004 weight table action button conversion (GH-34) ([1666696](https://github.com/rgoshen-snhu/WeighToGo/commit/1666696b9f68436af909325ae2995cbfc6af09c2))
* **F5:** summary entry (GH-34) ([c5ae148](https://github.com/rgoshen-snhu/WeighToGo/commit/c5ae14838cf08e992cd6f0ede3245f8619542e30))
* **F6:** address PR [#41](https://github.com/rgoshen-snhu/WeighToGo/issues/41) review — fix React/MUI version drift + FR-A mapping (GH-34) ([1af23bd](https://github.com/rgoshen-snhu/WeighToGo/commit/1af23bdc5f577c43ec2092b5aed0b1470729b0de))
* **F6:** align code comments and SRS prose with current identifiers (GH-34) ([6472a39](https://github.com/rgoshen-snhu/WeighToGo/commit/6472a3928c725d9fe0226378fcfa234167a1f330))
* **F6:** cleanup version drift in code comments and SRS (GH-34) ([eac6ccc](https://github.com/rgoshen-snhu/WeighToGo/commit/eac6ccc2b398c53778205bdfec479f2b6561fc4e))
* **F6:** SUMMARY entry for version-drift cleanup (GH-34) ([0b1ffb8](https://github.com/rgoshen-snhu/WeighToGo/commit/0b1ffb82dc71a6d002292ee106bf9ea5fd3713ce))
* **plans:** land M2 quality remediation plan (GH-34) ([067e30e](https://github.com/rgoshen-snhu/WeighToGo/commit/067e30e1bc6373e6054d490c37e41506132f32f9))
* **plans:** land M2 quality remediation plan (GH-34) ([fff372a](https://github.com/rgoshen-snhu/WeighToGo/commit/fff372a63f913d60128d01ae5027068eea803454))
* **quality:** add M2 Web App Quality Review documentation (GH-34) ([245e0ac](https://github.com/rgoshen-snhu/WeighToGo/commit/245e0acf00a43525f36d09173f5ba5d9439fc205))
* **quality:** add M2 Web App Quality Review documentation (PR 0, GH-34) ([32acab1](https://github.com/rgoshen-snhu/WeighToGo/commit/32acab16e29323a0cff640e57c2c924602c6b3aa))

## [0.1.0](https://github.com/rgoshen-snhu/WeighToGo/compare/v0.1.0...v0.1.0) (2026-05-28)


### Added

* **F1:** add HSTS and path-aware CSP security headers (GH-34) ([#35](https://github.com/rgoshen-snhu/WeighToGo/issues/35)) ([364eee6](https://github.com/rgoshen-snhu/WeighToGo/commit/364eee67b1a354175551f19e7be1adf1f26c4667))
* **F2:** add CSRF Origin/Referer validation middleware (GH-34) ([#37](https://github.com/rgoshen-snhu/WeighToGo/issues/37)) ([1c8fc33](https://github.com/rgoshen-snhu/WeighToGo/commit/1c8fc33746ce3650c34c4a3407e8d927b3cfa33e))
* **F3:** coalesce concurrent 401 refresh calls via shared promise (GH-34) ([ff0450b](https://github.com/rgoshen-snhu/WeighToGo/commit/ff0450bbf26ac072b3cd5beb125ed01b6bf285f1))
* **F3:** coalesce concurrent 401 refresh calls via shared promise (GH-34) ([4b82435](https://github.com/rgoshen-snhu/WeighToGo/commit/4b824356237eaa824ffc589f63f0acd0891d26ee))
* **F5:** convert weight table actions to Button meeting 44px target (GH-34) ([c758bd9](https://github.com/rgoshen-snhu/WeighToGo/commit/c758bd9955d318081f5c75ac01a8ab9dbd666f24))
* **F5:** meet 44px target size for weight table actions (GH-34) ([0df4751](https://github.com/rgoshen-snhu/WeighToGo/commit/0df47516b072484e280224d40bf44d631edbb635))


### Fixed

* **F3:** guard against synchronous throws from interceptor.refresh() (GH-34) ([0414e98](https://github.com/rgoshen-snhu/WeighToGo/commit/0414e98fc9fcfb0ee07f4a53aec17c900ce6e13e))
* **F4:** address PR [#39](https://github.com/rgoshen-snhu/WeighToGo/issues/39) review — neutral copy + parameterized invariant test (GH-34) ([af5c37b](https://github.com/rgoshen-snhu/WeighToGo/commit/af5c37b4c76bee806f061c12008cd53b0fb09b08))
* **F4:** remove email-existence disclosure on registration (GH-34) ([9e27394](https://github.com/rgoshen-snhu/WeighToGo/commit/9e27394391dd32761b1d1b1afa7ec7086eed270c))
* **F4:** use generic creation-failure message for ApiError (GH-34) ([ff3d2bd](https://github.com/rgoshen-snhu/WeighToGo/commit/ff3d2bd2b5792faaa5dab166ec7cf6add4b32f39))
* **F5:** address PR [#40](https://github.com/rgoshen-snhu/WeighToGo/issues/40) review — move 44px floor to theme; minWidth + comment fixes (GH-34) ([5d4fc08](https://github.com/rgoshen-snhu/WeighToGo/commit/5d4fc0895f0e2c03c0f6a05125cc550666a79930))


### Changed

* **auth:** consolidate ADR-0010 auth-safe message strings into a shared module (GH-42) ([#46](https://github.com/rgoshen-snhu/WeighToGo/issues/46)) ([eacba23](https://github.com/rgoshen-snhu/WeighToGo/commit/eacba23f2855c3df04f4b9666e75621ffa5eb751))
* **F3:** address PR review comments — ix capture, auth401 helper, test hardening (GH-34) ([db45329](https://github.com/rgoshen-snhu/WeighToGo/commit/db453293cc30b65b3d4439cab5de4ec053d6750d))


### Documentation

* **closeout:** record Resolution Review for issue [#34](https://github.com/rgoshen-snhu/WeighToGo/issues/34) (GH-34) ([edcac82](https://github.com/rgoshen-snhu/WeighToGo/commit/edcac82e83ff86202447af65d19512ae03fb1236))
* **closeout:** Resolution Review for issue [#34](https://github.com/rgoshen-snhu/WeighToGo/issues/34) (PR 7, GH-34) ([90e3f79](https://github.com/rgoshen-snhu/WeighToGo/commit/90e3f79dc5304b2cba91654b93ff82365e97d5c8))
* **F3:** add ADR-0018 concurrent refresh token coalescing (GH-34) ([a994e21](https://github.com/rgoshen-snhu/WeighToGo/commit/a994e219624971210c2c770f2a4e61141b96d396))
* **F4:** summary entry (GH-34) ([32c16d7](https://github.com/rgoshen-snhu/WeighToGo/commit/32c16d75d0d6a55a44617494130292c83ae80c3d))
* **F5:** add DDR-0004 weight table action button conversion (GH-34) ([1666696](https://github.com/rgoshen-snhu/WeighToGo/commit/1666696b9f68436af909325ae2995cbfc6af09c2))
* **F5:** summary entry (GH-34) ([c5ae148](https://github.com/rgoshen-snhu/WeighToGo/commit/c5ae14838cf08e992cd6f0ede3245f8619542e30))
* **F6:** address PR [#41](https://github.com/rgoshen-snhu/WeighToGo/issues/41) review — fix React/MUI version drift + FR-A mapping (GH-34) ([1af23bd](https://github.com/rgoshen-snhu/WeighToGo/commit/1af23bdc5f577c43ec2092b5aed0b1470729b0de))
* **F6:** align code comments and SRS prose with current identifiers (GH-34) ([6472a39](https://github.com/rgoshen-snhu/WeighToGo/commit/6472a3928c725d9fe0226378fcfa234167a1f330))
* **F6:** cleanup version drift in code comments and SRS (GH-34) ([eac6ccc](https://github.com/rgoshen-snhu/WeighToGo/commit/eac6ccc2b398c53778205bdfec479f2b6561fc4e))
* **F6:** SUMMARY entry for version-drift cleanup (GH-34) ([0b1ffb8](https://github.com/rgoshen-snhu/WeighToGo/commit/0b1ffb82dc71a6d002292ee106bf9ea5fd3713ce))
* **plans:** land M2 quality remediation plan (GH-34) ([067e30e](https://github.com/rgoshen-snhu/WeighToGo/commit/067e30e1bc6373e6054d490c37e41506132f32f9))
* **plans:** land M2 quality remediation plan (GH-34) ([fff372a](https://github.com/rgoshen-snhu/WeighToGo/commit/fff372a63f913d60128d01ae5027068eea803454))
* **quality:** add M2 Web App Quality Review documentation (GH-34) ([245e0ac](https://github.com/rgoshen-snhu/WeighToGo/commit/245e0acf00a43525f36d09173f5ba5d9439fc205))
* **quality:** add M2 Web App Quality Review documentation (PR 0, GH-34) ([32acab1](https://github.com/rgoshen-snhu/WeighToGo/commit/32acab16e29323a0cff640e57c2c924602c6b3aa))

## [0.1.0](https://github.com/rgoshen-snhu/WeighToGo/compare/v0.1.0...v0.1.0) (2026-05-28)


### Added

* **F1:** add HSTS and path-aware CSP security headers (GH-34) ([#35](https://github.com/rgoshen-snhu/WeighToGo/issues/35)) ([364eee6](https://github.com/rgoshen-snhu/WeighToGo/commit/364eee67b1a354175551f19e7be1adf1f26c4667))
* **F2:** add CSRF Origin/Referer validation middleware (GH-34) ([#37](https://github.com/rgoshen-snhu/WeighToGo/issues/37)) ([1c8fc33](https://github.com/rgoshen-snhu/WeighToGo/commit/1c8fc33746ce3650c34c4a3407e8d927b3cfa33e))
* **F3:** coalesce concurrent 401 refresh calls via shared promise (GH-34) ([ff0450b](https://github.com/rgoshen-snhu/WeighToGo/commit/ff0450bbf26ac072b3cd5beb125ed01b6bf285f1))
* **F3:** coalesce concurrent 401 refresh calls via shared promise (GH-34) ([4b82435](https://github.com/rgoshen-snhu/WeighToGo/commit/4b824356237eaa824ffc589f63f0acd0891d26ee))
* **F5:** convert weight table actions to Button meeting 44px target (GH-34) ([c758bd9](https://github.com/rgoshen-snhu/WeighToGo/commit/c758bd9955d318081f5c75ac01a8ab9dbd666f24))
* **F5:** meet 44px target size for weight table actions (GH-34) ([0df4751](https://github.com/rgoshen-snhu/WeighToGo/commit/0df47516b072484e280224d40bf44d631edbb635))


### Fixed

* **F3:** guard against synchronous throws from interceptor.refresh() (GH-34) ([0414e98](https://github.com/rgoshen-snhu/WeighToGo/commit/0414e98fc9fcfb0ee07f4a53aec17c900ce6e13e))
* **F4:** address PR [#39](https://github.com/rgoshen-snhu/WeighToGo/issues/39) review — neutral copy + parameterized invariant test (GH-34) ([af5c37b](https://github.com/rgoshen-snhu/WeighToGo/commit/af5c37b4c76bee806f061c12008cd53b0fb09b08))
* **F4:** remove email-existence disclosure on registration (GH-34) ([9e27394](https://github.com/rgoshen-snhu/WeighToGo/commit/9e27394391dd32761b1d1b1afa7ec7086eed270c))
* **F4:** use generic creation-failure message for ApiError (GH-34) ([ff3d2bd](https://github.com/rgoshen-snhu/WeighToGo/commit/ff3d2bd2b5792faaa5dab166ec7cf6add4b32f39))
* **F5:** address PR [#40](https://github.com/rgoshen-snhu/WeighToGo/issues/40) review — move 44px floor to theme; minWidth + comment fixes (GH-34) ([5d4fc08](https://github.com/rgoshen-snhu/WeighToGo/commit/5d4fc0895f0e2c03c0f6a05125cc550666a79930))


### Changed

* **F3:** address PR review comments — ix capture, auth401 helper, test hardening (GH-34) ([db45329](https://github.com/rgoshen-snhu/WeighToGo/commit/db453293cc30b65b3d4439cab5de4ec053d6750d))


### Documentation

* **closeout:** record Resolution Review for issue [#34](https://github.com/rgoshen-snhu/WeighToGo/issues/34) (GH-34) ([edcac82](https://github.com/rgoshen-snhu/WeighToGo/commit/edcac82e83ff86202447af65d19512ae03fb1236))
* **closeout:** Resolution Review for issue [#34](https://github.com/rgoshen-snhu/WeighToGo/issues/34) (PR 7, GH-34) ([90e3f79](https://github.com/rgoshen-snhu/WeighToGo/commit/90e3f79dc5304b2cba91654b93ff82365e97d5c8))
* **F3:** add ADR-0018 concurrent refresh token coalescing (GH-34) ([a994e21](https://github.com/rgoshen-snhu/WeighToGo/commit/a994e219624971210c2c770f2a4e61141b96d396))
* **F4:** summary entry (GH-34) ([32c16d7](https://github.com/rgoshen-snhu/WeighToGo/commit/32c16d75d0d6a55a44617494130292c83ae80c3d))
* **F5:** add DDR-0004 weight table action button conversion (GH-34) ([1666696](https://github.com/rgoshen-snhu/WeighToGo/commit/1666696b9f68436af909325ae2995cbfc6af09c2))
* **F5:** summary entry (GH-34) ([c5ae148](https://github.com/rgoshen-snhu/WeighToGo/commit/c5ae14838cf08e992cd6f0ede3245f8619542e30))
* **F6:** address PR [#41](https://github.com/rgoshen-snhu/WeighToGo/issues/41) review — fix React/MUI version drift + FR-A mapping (GH-34) ([1af23bd](https://github.com/rgoshen-snhu/WeighToGo/commit/1af23bdc5f577c43ec2092b5aed0b1470729b0de))
* **F6:** align code comments and SRS prose with current identifiers (GH-34) ([6472a39](https://github.com/rgoshen-snhu/WeighToGo/commit/6472a3928c725d9fe0226378fcfa234167a1f330))
* **F6:** cleanup version drift in code comments and SRS (GH-34) ([eac6ccc](https://github.com/rgoshen-snhu/WeighToGo/commit/eac6ccc2b398c53778205bdfec479f2b6561fc4e))
* **F6:** SUMMARY entry for version-drift cleanup (GH-34) ([0b1ffb8](https://github.com/rgoshen-snhu/WeighToGo/commit/0b1ffb82dc71a6d002292ee106bf9ea5fd3713ce))
* **plans:** land M2 quality remediation plan (GH-34) ([067e30e](https://github.com/rgoshen-snhu/WeighToGo/commit/067e30e1bc6373e6054d490c37e41506132f32f9))
* **plans:** land M2 quality remediation plan (GH-34) ([fff372a](https://github.com/rgoshen-snhu/WeighToGo/commit/fff372a63f913d60128d01ae5027068eea803454))
* **quality:** add M2 Web App Quality Review documentation (GH-34) ([245e0ac](https://github.com/rgoshen-snhu/WeighToGo/commit/245e0acf00a43525f36d09173f5ba5d9439fc205))
* **quality:** add M2 Web App Quality Review documentation (PR 0, GH-34) ([32acab1](https://github.com/rgoshen-snhu/WeighToGo/commit/32acab16e29323a0cff640e57c2c924602c6b3aa))

## 0.1.0 (2026-05-23)


### Added

* **api-client:** send credentials, parse RFC 7807 errors, reactive 401 refresh interceptor ([583da2e](https://github.com/rgoshen-snhu/WeighToGo/commit/583da2e6b174532b9f7bc53da9aefb97f48b4e81))
* **api:** emit RFC 7807 validation errors with field-level details (SRS §9.2) ([beef17d](https://github.com/rgoshen-snhu/WeighToGo/commit/beef17d13a43304d4ad2d1b07a813a8d02e56e32))
* **application:** add five weight use cases (FR-W-1..5) ([0755621](https://github.com/rgoshen-snhu/WeighToGo/commit/0755621bd2f8b896aaf0c6ac378485c6b4f546c5))
* **auth:** add LoginForm with zod resolver and a11y-live error region ([3bb6435](https://github.com/rgoshen-snhu/WeighToGo/commit/3bb6435babd4fcbbbb7a3c71147a1aa44680c44a))
* **auth:** add RegisterForm with complexity rules and confirm-password check ([e8fcba7](https://github.com/rgoshen-snhu/WeighToGo/commit/e8fcba7ceac2283e7a7d0d69d616f2f6d79eabb5))
* **auth:** add typed auth-client for /api/v1/auth endpoints ([3fd50c9](https://github.com/rgoshen-snhu/WeighToGo/commit/3fd50c96808a2281f77ea8ceffbda1609a151510))
* **auth:** add useLogin, useRegister, and useLogout mutations ([6e02a54](https://github.com/rgoshen-snhu/WeighToGo/commit/6e02a54de5b68251750017df8332677b3b6beaf6))
* **auth:** add user menu in AppBar with logout (DDR-0003) ([10ab16f](https://github.com/rgoshen-snhu/WeighToGo/commit/10ab16fb0a32b4e9e1f18a1f37a862abc9a7ff23))
* **auth:** add zod schemas for login and register (FR-A-1, FR-A-2) ([5eca4a7](https://github.com/rgoshen-snhu/WeighToGo/commit/5eca4a7aa247a2f046439b91c8dc5a4885eb7ec5))
* **auth:** authentication backend (Phase 6) ([feec9df](https://github.com/rgoshen-snhu/WeighToGo/commit/feec9df26f9cba07f77e1955014138d9fe21c749))
* **auth:** domain entities, use cases, and infrastructure adapters (Phase 6) ([e6db042](https://github.com/rgoshen-snhu/WeighToGo/commit/e6db042d33b7709141c931d467cf0aeab90e3a2d))
* **auth:** infrastructure adapters, FastAPI interface, and Alembic migration (Phase 6) ([17f127c](https://github.com/rgoshen-snhu/WeighToGo/commit/17f127c846f0ae9dfab6d4017e4440f822254231))
* **auth:** rebuild AuthContext on React Query and add hydration splash ([b26dc02](https://github.com/rgoshen-snhu/WeighToGo/commit/b26dc020562e03f9a2e3aadd17b59d15a3ff0acd))
* **auth:** wire LoginPage and RegisterPage to forms and mutations ([4aee3ea](https://github.com/rgoshen-snhu/WeighToGo/commit/4aee3eaa7d3d689703cd515d54194f6a0e4aeedb))
* **backend:** add Alembic migration harness ([770bc83](https://github.com/rgoshen-snhu/WeighToGo/commit/770bc832f6c765c0bea5e29baba33fdd7e022459))
* **backend:** add application settings module ([0f7f260](https://github.com/rgoshen-snhu/WeighToGo/commit/0f7f26071d17f52de6a1668fb64b0eb29c52e393))
* **backend:** add health-check endpoint ([b6c91ff](https://github.com/rgoshen-snhu/WeighToGo/commit/b6c91ffca272b86e0ce106a60c1b3c9cb9f68b16))
* **backend:** add shared logging setup and base domain exceptions ([b313ada](https://github.com/rgoshen-snhu/WeighToGo/commit/b313ada23503a696ef452ac45a8ff3814bb7627c))
* **backend:** configure import-linter contracts for clean architecture dependency rule ([824464b](https://github.com/rgoshen-snhu/WeighToGo/commit/824464bfe771d80e16734fea30bc1754bcb464d4))
* **backend:** scaffold screaming architecture domain folders ([674d357](https://github.com/rgoshen-snhu/WeighToGo/commit/674d3579c557ea3e25689e0081197a52f592613b))
* **backend:** three-pattern backend architecture scaffold (Phase 4) ([f3097a8](https://github.com/rgoshen-snhu/WeighToGo/commit/f3097a8528b5c52985781b8d989fa5090f86acf1))
* **dashboard:** add dashboard summary slice (FR-D-1) ([a7fb2b2](https://github.com/rgoshen-snhu/WeighToGo/commit/a7fb2b2594b50c7761924ae57701f48feba2d099))
* **db:** add weight_entries migration (FR-W-1..5) ([439d36c](https://github.com/rgoshen-snhu/WeighToGo/commit/439d36caea0c3aa7f621b015f3bce156331c6c8a))
* **domain:** add WeightEntry entity, port, and exceptions ([0cd69ca](https://github.com/rgoshen-snhu/WeighToGo/commit/0cd69ca99c5d9c32cfe905c5cc617bb442be935b))
* **error-mapping:** add mapValidationErrors for 422 field errors ([ed13611](https://github.com/rgoshen-snhu/WeighToGo/commit/ed13611e7e3d8a24e0067bd6b726653f2b5dc8a0))
* **frontend:** add api-client, error-mapping, and format utilities ([013ec86](https://github.com/rgoshen-snhu/WeighToGo/commit/013ec869dc5bb68b5b3381d62b64e44dc7d29c3c))
* **frontend:** add App component within the MUI theme provider ([dcca213](https://github.com/rgoshen-snhu/WeighToGo/commit/dcca213e33df548537f3d53c53680e73ee7626b4))
* **frontend:** add AuthContext and PreferencesContext providers ([aeb7566](https://github.com/rgoshen-snhu/WeighToGo/commit/aeb75665724d138641da6834c163807b7523d78d))
* **frontend:** add placeholder and stub feature pages ([951fd2c](https://github.com/rgoshen-snhu/WeighToGo/commit/951fd2c174abfa6955a4be58f31d1fd69a1e66f3))
* **frontend:** add React Router 6 route declarations ([1bfa937](https://github.com/rgoshen-snhu/WeighToGo/commit/1bfa93780f67c7c7586a068e17dffcbf172d8fe7))
* **frontend:** add shared layout and utility components ([755574e](https://github.com/rgoshen-snhu/WeighToGo/commit/755574ebc3d660bff0bd777b3f7c0c4e1128b5da))
* **frontend:** add Vitest test setup and MUI theme ([144b332](https://github.com/rgoshen-snhu/WeighToGo/commit/144b332634cdbe2b4c74d1175bb676f5e45083a7))
* **frontend:** add weight and dashboard UI components ([6a9c4f8](https://github.com/rgoshen-snhu/WeighToGo/commit/6a9c4f88f2ec4cdbc23e1d0dda264a94dbc49af0))
* **frontend:** add weight schemas, clients, format helpers, and hooks ([9f5d9a7](https://github.com/rgoshen-snhu/WeighToGo/commit/9f5d9a79f88e4d0c01feb8592dc2dbaf50dd7147))
* **frontend:** frontend architecture scaffold (Phase 5) ([f285ce2](https://github.com/rgoshen-snhu/WeighToGo/commit/f285ce2a1091af7600853ec756558cd2120cc287))
* **frontend:** replace stub pages with real weight and dashboard pages ([5ff8db2](https://github.com/rgoshen-snhu/WeighToGo/commit/5ff8db288baa5551abb38401b31ffaa2fcfbe7d8))
* **frontend:** wire BrowserRouter, QueryClient, and auth/prefs providers in App ([b12d368](https://github.com/rgoshen-snhu/WeighToGo/commit/b12d3686a8e10e422122f03a62e8354236b7c1dd))
* **infra:** add WeightEntryModel ORM and SqlAlchemy repository ([fdff822](https://github.com/rgoshen-snhu/WeighToGo/commit/fdff82246e9b1e8138fd37fa1ffb9590b9290839))
* **interface:** add weight-entries router and Pydantic schemas (FR-W-1..5) ([b736d5e](https://github.com/rgoshen-snhu/WeighToGo/commit/b736d5e1375822fb03f77385c58e6739bfbf0e29))
* **m2-phase-8:** weight entry CRUD and dashboard (FR-W-1..5, FR-D-1) ([c50a305](https://github.com/rgoshen-snhu/WeighToGo/commit/c50a305bed9aaf4403a35a03decc935a4fd98eb0))
* Phase 7 — auth frontend & vertical slice (FR-A-1..5, NFR-A-1..6) ([d0db251](https://github.com/rgoshen-snhu/WeighToGo/commit/d0db25168a7d03c17ed86eba51b605a48d10a1e9))
* **weight:** paginate weight history with Load more button ([45c228b](https://github.com/rgoshen-snhu/WeighToGo/commit/45c228b0964aa1619a9761346ca3f32c424c3bd4))


### Fixed

* **api-client:** call onLogout when post-refresh retry fails ([e8901ea](https://github.com/rgoshen-snhu/WeighToGo/commit/e8901ea53349a5f89e811e5eba56bc7b6e1b3d7b))
* **arch:** add layers contracts to import-linter for all bounded contexts ([4904154](https://github.com/rgoshen-snhu/WeighToGo/commit/490415462f5ad644b3d1b7593b906a315b8e9b90))
* **auth:** add 3/hour rate limit to /register per NFR-S-5 ([244c6dd](https://github.com/rgoshen-snhu/WeighToGo/commit/244c6dd95138a50812214977a2466e0c2932ce0d))
* **auth:** cap password length at bcrypt's 72-byte limit ([428d3aa](https://github.com/rgoshen-snhu/WeighToGo/commit/428d3aa526e66ba5bd5a8e8a8461023dd15e10e3))
* **auth:** derive dummy bcrypt hash from current cost factor ([7859b78](https://github.com/rgoshen-snhu/WeighToGo/commit/7859b783b09554b6e9c1660f680bbe534d93d8a0))
* **auth:** equalize timing for locked-account login attempts ([9022b4c](https://github.com/rgoshen-snhu/WeighToGo/commit/9022b4c023be1a6ea33d33b0e2845e105117d183))
* **auth:** include attribute parity in cookie deletion ([2b82095](https://github.com/rgoshen-snhu/WeighToGo/commit/2b8209507d7f16d0defed868139d98ccb4104af9))
* **auth:** logout revokes full token family via injected adapter ([b529213](https://github.com/rgoshen-snhu/WeighToGo/commit/b5292135b2fde3e7d5e9ee9b5058239a5b1bc857))
* **auth:** normalize email case at API boundary ([dbef642](https://github.com/rgoshen-snhu/WeighToGo/commit/dbef642aa766b7f3fac2ca6476f04c501184ed4c))
* **auth:** populate replaced_by during refresh rotation ([cc503ba](https://github.com/rgoshen-snhu/WeighToGo/commit/cc503ba2fbc1d0cf6e7752d9bfdd8870eefe99c1))
* **auth:** rate-limit logout endpoint ([eb9d2d9](https://github.com/rgoshen-snhu/WeighToGo/commit/eb9d2d9e781b4f53ead3a4077e53a3a30ecb8293))
* **auth:** revoke token family when refresh finds no user ([c494c40](https://github.com/rgoshen-snhu/WeighToGo/commit/c494c40688ac782b283df67be74ff59a41a93376))
* **auth:** scope refresh cookie to auth endpoints ([aeb6b4f](https://github.com/rgoshen-snhu/WeighToGo/commit/aeb6b4ffe6a3dafd367db823b27ffbd51ae94207))
* **auth:** validate JWT typ/aud/iss claims ([ead9e6d](https://github.com/rgoshen-snhu/WeighToGo/commit/ead9e6d16730434fad8376072248bef0c3220063))
* **backend:** construct settings lazily and harden the Alembic environment ([64e3dd4](https://github.com/rgoshen-snhu/WeighToGo/commit/64e3dd4c8984438337beeca9c8057e419ccf49b4))
* **backend:** remove users/ domain — user identity belongs in auth/ per SRS §4.2.1 ([44a8a83](https://github.com/rgoshen-snhu/WeighToGo/commit/44a8a83cfecdbb5fd95da9a8f7f19b3d737c03bc))
* **config:** require DATABASE_URL — raise ValidationError if unset ([b1c8e3d](https://github.com/rgoshen-snhu/WeighToGo/commit/b1c8e3dbcf22f5f908a125219ab29641d88c535d))
* **cors:** honor CORS_ALLOWED_ORIGINS env var ([ea09699](https://github.com/rgoshen-snhu/WeighToGo/commit/ea096996655880759d9b9d4754ceb6ab805f73a1))
* **db:** commit session exactly once per request ([0c69af0](https://github.com/rgoshen-snhu/WeighToGo/commit/0c69af0d927394fb5650619c1ea83e80b5bfbd24))
* **e2e:** bypass /register rate limit for E2E via RATE_LIMIT_ENABLED env var ([537526d](https://github.com/rgoshen-snhu/WeighToGo/commit/537526df86927d4995925b623a73a5f8ec6679de))
* **e2e:** replace __dirname with ESM-compatible import.meta.url in screenshot spec ([73a2505](https://github.com/rgoshen-snhu/WeighToGo/commit/73a25050c51d9e6d2456305893349fca194bad4b))
* **e2e:** use repo-relative path in screenshot spec ([a48b203](https://github.com/rgoshen-snhu/WeighToGo/commit/a48b20377ffa5033a48f1b3b49d17c40f106bc53))
* **e2e:** wait for post-login redirect and disambiguate delete locator ([e63dac9](https://github.com/rgoshen-snhu/WeighToGo/commit/e63dac94f67e3bff349e7fcf6a6d802f732c971c))
* **frontend:** annotate ThrowingComponent return type as never for strict TypeScript ([f961614](https://github.com/rgoshen-snhu/WeighToGo/commit/f961614c8b19f6c7af192130d6debf3c49dda9d8))
* **frontend:** declare all lint and test dependencies in the manifest ([5f1474d](https://github.com/rgoshen-snhu/WeighToGo/commit/5f1474daa310386c280117e185db13a90930a76c))
* **frontend:** type-check e2e specs and harden the Playwright config ([913fe39](https://github.com/rgoshen-snhu/WeighToGo/commit/913fe3928e3dac436cfa0d7922b6f0d51ea718bf))
* **frontend:** upgrade @mui/material to v9.0.1, add @mui/icons-material@9.0.1, remove unused placeholder install ([8437041](https://github.com/rgoshen-snhu/WeighToGo/commit/8437041e2b9466fe720021115b6d0b4ec23c71e1))
* **lint:** sort imports in test_exceptions.py ([2109cc3](https://github.com/rgoshen-snhu/WeighToGo/commit/2109cc362e041ed2e86d2a24c74c999e982a5489))
* **logging:** configure structlog centrally with automatic PII redaction ([eb43fe1](https://github.com/rgoshen-snhu/WeighToGo/commit/eb43fe1d189ab8b9b952c5e13dc16b74859d64e1))
* **schema:** align ORM types with migration (BigInt, UUID) ([36c8c2b](https://github.com/rgoshen-snhu/WeighToGo/commit/36c8c2bca801906782fd108f8b3d9b73b219f663))
* **security:** atomic refresh rotation, logout without access token, inactive-user guard ([de1bdf5](https://github.com/rgoshen-snhu/WeighToGo/commit/de1bdf56878b829be88b90eb69900b3437965bb5))
* **security:** enforce SECRET_KEY strength and derive cookie_secure from environment ([11ac999](https://github.com/rgoshen-snhu/WeighToGo/commit/11ac999ec20a927413e12d46bac1f93dde44c0e2))
* **security:** support trusted proxy headers in rate limiter ([419e139](https://github.com/rgoshen-snhu/WeighToGo/commit/419e1391c2646df6d2bd4670864966c7596a53c3))
* **types:** add full type annotations to logging module and tests ([0d4cc7f](https://github.com/rgoshen-snhu/WeighToGo/commit/0d4cc7fb9bbf06aadf263d51833b55935ea7c1e4))
* **weight:** exclude soft-deleted from get_by_id; add get_by_id_including_deleted ([ec22cf2](https://github.com/rgoshen-snhu/WeighToGo/commit/ec22cf2ddc324d817d15a118b210bdfd3b8a0f5a))
* **weight:** opaque compound cursor for list pagination (ADR-0015) ([5e84610](https://github.com/rgoshen-snhu/WeighToGo/commit/5e8461011366bb1904c958625439f3dca3cbed07))
* **weight:** render not-found state when edit-form fetch fails ([dd50dde](https://github.com/rgoshen-snhu/WeighToGo/commit/dd50dde8c92516701a1b1bf9126a0161f8396b4c))
* **weight:** validate list limit range with Query(ge=1, le=100) ([a1c7134](https://github.com/rgoshen-snhu/WeighToGo/commit/a1c71340e770cfed620c567c45e7c4ea5a804c7a))


### Changed

* relocate Android project into android/ directory ([f78cca1](https://github.com/rgoshen-snhu/WeighToGo/commit/f78cca101a773b7a0d81211aaeec607dcadc661b))
* restructure into a polyglot monorepo (Phase 2) ([601fdcd](https://github.com/rgoshen-snhu/WeighToGo/commit/601fdcd48b2b98e89dbf32fb6cb9dcf1cb9257ea))
* standardize the web database identifier on weighttogo ([63bfafb](https://github.com/rgoshen-snhu/WeighToGo/commit/63bfafb926b40ee948e8653e97e6b56a8a3db8c0))


### Documentation

* add ADR decision-log index (GH-17) ([5757d9c](https://github.com/rgoshen-snhu/WeighToGo/commit/5757d9c1360e6f3b44364fdafbed7d0706a26969))
* add ADR-0007 and ADR-0008 for the web rebuild and monorepo ([55fa5d5](https://github.com/rgoshen-snhu/WeighToGo/commit/55fa5d530a265404226543f09b78b28a499a6359))
* add ADR-0014 React Query and DDR-0003 user menu placement ([eaa155c](https://github.com/rgoshen-snhu/WeighToGo/commit/eaa155c20a54577775456993053991084c7355ee))
* add DDR decision-log index (GH-17) ([8a52d75](https://github.com/rgoshen-snhu/WeighToGo/commit/8a52d75b2fef6c134cea3ef8503e40ff1799f9d4))
* add top-level docs/README index (GH-17) ([1976961](https://github.com/rgoshen-snhu/WeighToGo/commit/1976961e9d4c8e1ff33494e4c46673feb6880a27))
* address Phase 2 review findings ([27d718f](https://github.com/rgoshen-snhu/WeighToGo/commit/27d718f4026d48c69084f0d49faea2e5870d6930))
* **adr:** add ADR-0009 email as primary user identifier ([e046e03](https://github.com/rgoshen-snhu/WeighToGo/commit/e046e03d83e1b41222a77219e7defde82421da66))
* **adr:** add ADR-0010 generic authentication error policy ([ba4603c](https://github.com/rgoshen-snhu/WeighToGo/commit/ba4603ce46a9e381f027646893d2d1801e694546))
* **adr:** add ADR-0011 PII masking strategy in logs ([83dbcf7](https://github.com/rgoshen-snhu/WeighToGo/commit/83dbcf70668313d17ebba084e699b1dffed7593d))
* **adr:** add ADR-0012 three-pattern backend architecture ([dd4d2f8](https://github.com/rgoshen-snhu/WeighToGo/commit/dd4d2f8087912c73849df7ca7be61dbf8731627e))
* **adr:** add ADR-0013 refresh token rotation with family-based revocation ([cdc3726](https://github.com/rgoshen-snhu/WeighToGo/commit/cdc3726cf2ed37face551893657a1123f5cc894d))
* **adr:** correct Author byline from 'Development Team' to Rick Goshen (GH-15) ([057cb8b](https://github.com/rgoshen-snhu/WeighToGo/commit/057cb8beef8e781a63fff91ddee4fb649f185e17))
* **api:** refresh OpenAPI snapshot and update project docs (subtasks 39-44) ([a42bf81](https://github.com/rgoshen-snhu/WeighToGo/commit/a42bf816c5280ef988773f26c35e8c70b334903d))
* **api:** refresh OpenAPI snapshot for cursor and limit changes ([6ee9d8f](https://github.com/rgoshen-snhu/WeighToGo/commit/6ee9d8fa9914d7e7034a75afda40b256a9105b84))
* **architecture:** add ARCHITECTURE.md stub deferring to SRS §4 (GH-15) ([a2eefb2](https://github.com/rgoshen-snhu/WeighToGo/commit/a2eefb22538198a4ecd1ac47d1f8121340cad4fd))
* **auth:** add auth environment variables to .env.example (SRS §12.5.1) ([d973e1c](https://github.com/rgoshen-snhu/WeighToGo/commit/d973e1c06df72f0731701e8e16891a42a5e68cba))
* complete Phase 7 SUMMARY.md entries ([2f88334](https://github.com/rgoshen-snhu/WeighToGo/commit/2f88334bfe04e8f74987f9bdafd7286ba5b26c70))
* **contributing:** add web stack contribution guidelines (GH-15) ([0483e0a](https://github.com/rgoshen-snhu/WeighToGo/commit/0483e0a1e96175da89ef687185156aa04e7c4c05))
* **contributing:** consolidate structure; expand web stack guidance (GH-15) ([e57ba19](https://github.com/rgoshen-snhu/WeighToGo/commit/e57ba19d367eac2d109f99900d1938708203e74d))
* correct a remaining restructure-stale path in the test setup guide ([32af137](https://github.com/rgoshen-snhu/WeighToGo/commit/32af1370afbf768bfaa68eeb4354721acd4e2b05))
* correct milestone tags to 0.x development versioning ([d51ff42](https://github.com/rgoshen-snhu/WeighToGo/commit/d51ff4216c624ecba3b8f783d6e888e297656c2b))
* correct retired-tracker references in the testing index ([0c3a109](https://github.com/rgoshen-snhu/WeighToGo/commit/0c3a109334318ccbe88d504c5a5acb637e9a4d1a))
* drop the intermediate restructure tag ([4001305](https://github.com/rgoshen-snhu/WeighToGo/commit/4001305a8abf9e22fac5f8845d975dd690103157))
* **history:** add preservation banner to Android-era development journal (GH-15) ([aabbcda](https://github.com/rgoshen-snhu/WeighToGo/commit/aabbcdaf0e2e24f8a79b2d62889c294494aabb13))
* **history:** adjust exploration phrasing (GH-15) ([8e146ab](https://github.com/rgoshen-snhu/WeighToGo/commit/8e146ab60093bb03464bdae0a82e960d5416380d))
* index the docs/ tree (top-level README, ADR/DDR decision logs) (GH-17) ([ccd6b75](https://github.com/rgoshen-snhu/WeighToGo/commit/ccd6b75ebaf061ffef8aedcc8cb10df95833b11e))
* **m2:** ADR-0009–0013 and milestone plan ADR timing fix ([7021d3b](https://github.com/rgoshen-snhu/WeighToGo/commit/7021d3b80f00ed146bf6fd11272f438bf627b083))
* **narrative:** add Milestone Two narrative (GH-15) ([2475839](https://github.com/rgoshen-snhu/WeighToGo/commit/24758393be66371e819ea0b8e4201a9881543d0a))
* **narrative:** align section voice (GH-15) ([b10d97d](https://github.com/rgoshen-snhu/WeighToGo/commit/b10d97daecf0272f1d5a1d14704fa4ff3332807d))
* **narrative:** apply the Outcome 3 algorithm-naming fix (GH-15) ([5dfdba6](https://github.com/rgoshen-snhu/WeighToGo/commit/5dfdba6f810ab7abafbc1961591f6fb9a3ece0e4))
* **narrative:** expand section 4 reflection from engineering log (GH-15) ([68b67a9](https://github.com/rgoshen-snhu/WeighToGo/commit/68b67a91ca2f3d9a570148e6c2a69d8408e1031b))
* **narrative:** name M3 algorithms specifically in Outcome 3 discussion (GH-15) ([09ac671](https://github.com/rgoshen-snhu/WeighToGo/commit/09ac671a167474fcd221fa73eb50fa296768da87))
* **plan:** write ADRs at decision time, not at closeout ([e73f1aa](https://github.com/rgoshen-snhu/WeighToGo/commit/e73f1aa51504144ffbd14145d34136937823859a))
* point CONTRIBUTING Android setup at the android/ directory ([f7e16a4](https://github.com/rgoshen-snhu/WeighToGo/commit/f7e16a4765506b54b774d118dd58d7fe8e6ec85f))
* **readme:** expand web stack documentation (GH-15) ([4fc454f](https://github.com/rgoshen-snhu/WeighToGo/commit/4fc454f93445c31bfdf4b38a31148627bf45e753))
* **readme:** final pass — web CI badges, M2 status, docs index link (GH-15) ([764c5df](https://github.com/rgoshen-snhu/WeighToGo/commit/764c5df9ce4eab329471a8607590f85bd38780dc))
* **readme:** restore 'in progress' status; refresh test counts (GH-15) ([4e40102](https://github.com/rgoshen-snhu/WeighToGo/commit/4e401020862412c3da97122138a0fa942ab1e218))
* **readme:** restore project tagline (GH-15) ([5e5cb02](https://github.com/rgoshen-snhu/WeighToGo/commit/5e5cb024c8286be9a3a28c4a61dcd37ea6e581b4))
* **readme:** update frontend tech stack table to reflect actual versions ([ad59231](https://github.com/rgoshen-snhu/WeighToGo/commit/ad592314c837a5cdb52e211f8be5ba9dd52d9084))
* record Phase 2 documentation-hygiene follow-up in SUMMARY ([1a1636d](https://github.com/rgoshen-snhu/WeighToGo/commit/1a1636deb27cd0013c8f4b6b1490fda59d2b77b9))
* record Phase 2 restructure in SUMMARY ([b19b9b5](https://github.com/rgoshen-snhu/WeighToGo/commit/b19b9b58f5eb8b29c2795f18227aa62c3602271f))
* record the review-driven hardening in SUMMARY ([d66824d](https://github.com/rgoshen-snhu/WeighToGo/commit/d66824d698f1b4f4a244416c738d5d42418426d8))
* remove live AI-tool references from committed documentation ([435bb1f](https://github.com/rgoshen-snhu/WeighToGo/commit/435bb1fb4959326fc2e276d1c036de0871eba23f))
* remove project instruction-file citations from documentation ([eca5577](https://github.com/rgoshen-snhu/WeighToGo/commit/eca5577c0a0e4d5cdcbd869914d14ee389d23abc))
* renumber the ADR index in the SRS for the M2 ADR set ([d697366](https://github.com/rgoshen-snhu/WeighToGo/commit/d697366b56a9010bc5ef87f5b8f136b1d02e3920))
* repair a corrupted command in the testing index README ([caa1af5](https://github.com/rgoshen-snhu/WeighToGo/commit/caa1af5611d9b3026027bf3940d2acfe4fafd9d5))
* repair corrupted manual-testing command guides ([077b765](https://github.com/rgoshen-snhu/WeighToGo/commit/077b76531849fd01bd605ba68c5f4577106025b4))
* **review:** record CS 499 checklist self-review findings (GH-15) ([2acfa18](https://github.com/rgoshen-snhu/WeighToGo/commit/2acfa185faa0b636087a1c7827e7e1eef359386b))
* rewrite the README for the polyglot monorepo ([d2ecf47](https://github.com/rgoshen-snhu/WeighToGo/commit/d2ecf472980fec343617b60b3f27c38eea5fdeff))
* **srs:** add v2 with M2 reconciliation; deprecate v1 (GH-15) ([44a1bfd](https://github.com/rgoshen-snhu/WeighToGo/commit/44a1bfd8bffee9ea1157156393ffd46cd65ebf8e))
* **srs:** consistency fixes — remove branch naming, uv commands, §5.3 cleanup ([990ed23](https://github.com/rgoshen-snhu/WeighToGo/commit/990ed23c9f5c5b7a175e00391236e0ea19ec632e))
* **srs:** reconcile Appendix A ADR index with on-disk ADRs (GH-15) ([667f36f](https://github.com/rgoshen-snhu/WeighToGo/commit/667f36fb58c5c2657931342c5cca91c98bb5be21))
* **srs:** remove branch naming, fix backend commands to use uv, correct §5.3 procedure ([92e832c](https://github.com/rgoshen-snhu/WeighToGo/commit/92e832cf775054548742812a3e2c03ca86b772c3))
* **srs:** update §4.3.1 frontend stack to actual installed versions ([776443c](https://github.com/rgoshen-snhu/WeighToGo/commit/776443c543aff64fee12cd6d8044e0b8655a1026))
* **srs:** update §4.3.1 frontend versions to reflect actual installed stack ([6d399aa](https://github.com/rgoshen-snhu/WeighToGo/commit/6d399aac9cfa1bf19d97e1fe9956cb2993124d7b))
* **summary:** Phase 9 closeout — Milestone 2 ready for release-please bootstrap (GH-15) ([c4bc17f](https://github.com/rgoshen-snhu/WeighToGo/commit/c4bc17ff552d8c331108165dbc43bb51bda12177))
* **summary:** Phase 9 closeout — Milestone 2 ready to tag v0.1.0 (GH-15) ([cb7611d](https://github.com/rgoshen-snhu/WeighToGo/commit/cb7611d257c7dddf910589f4b9d5195d11a293f3))
* **summary:** record Phase 9 documentation hardening pass (GH-15) ([e41758b](https://github.com/rgoshen-snhu/WeighToGo/commit/e41758bb1c67a84e87570ca8c16e5fd6290329a6))
* **summary:** record SRS v1-&gt;v2 process correction (GH-15) ([ae3c208](https://github.com/rgoshen-snhu/WeighToGo/commit/ae3c2081bf1eb33d418237dc80f49e2ca93fe6b6))
* tighten SUMMARY and narrative wording (GH-15) ([ea42030](https://github.com/rgoshen-snhu/WeighToGo/commit/ea42030fccf72bf402dc1a557dd17b4fb5aa1eb7))
* update README and SUMMARY for the web scaffold ([821a1c2](https://github.com/rgoshen-snhu/WeighToGo/commit/821a1c2bbd33fa0468eeb5550fc64fde169e3f77))
* update SRS cross-references from v1 to v2 (GH-15) ([bba14ab](https://github.com/rgoshen-snhu/WeighToGo/commit/bba14ab2721189e0df0c049a83760482b44be38b))
