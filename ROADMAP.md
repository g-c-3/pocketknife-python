# ðŸ—ºï¸„1¤7 ROADMAP â€„1¤7 pocketknife-python 

> **For Claude:** Always read this file at the start of a new conversation using:
> ```
> curl https://raw.githubusercontent.com/GokulChandar/pocketknife-python/main/ROADMAP.md
> ```
> Check which boxes are ticked âœ„1¤7 to know where we left off, then continue from the first unchecked item.

---

## Legend
- âœ„1¤7 Complete â€„1¤7 code written, tested, merged
- ðŸ”¨ In Progress â€„1¤7 currently being built
- ðŸ“‹ Planned â€„1¤7 not started yet

---

## ðŸ—ï¸„1¤7 PHASE 1: THE FOUNDATION (Modules 1â€„1¤710)

### ðŸŽ­ The "Just for Fun" Wing

- [x] **1. `pocketknife.text_flair`**
  - `spongecase()` â€„1¤7 alternating CaPs LiKe ThIs
  - `leetspeak()` â€„1¤7 converts text to l33t 5p34k
  - `clapy()` â€„1¤7 inserts ðŸ‘ clap ðŸ‘ emojis ðŸ‘ between ðŸ‘ words

- [x] **2. `pocketknife.drama`**
  - `dramatic_progress()` â€„1¤7 stressed loading bar with anxiety messages
  - `excuse_generator()` â€„1¤7 generates fake but plausible crash log excuses

- [x] **3. `pocketknife.absurd_units`**
  - `to_bananas(meters)` â€„1¤7 converts meters to banana lengths
  - `to_coffees(joules)` â€„1¤7 converts energy to cups of coffee
  - `to_jiffies(seconds)` â€„1¤7 converts seconds to actual jiffies (1/100th of a second)

- [x] **4. `pocketknife.dev_oracle`**
  - `should_i_deploy()` â€„1¤7 warns if it's Friday afternoon; blesses deploys otherwise
  - `code_review_roulette()` â€„1¤7 returns a random passive-aggressive PR review comment

### ðŸ› ï¸„1¤7 The "Pure Utility" Wing

- [x] **5. `pocketknife.fuzzy_time`**
  - `around_noon(dt)` â€„1¤7 humanizes datetimes ("about 3 hours ago", "just now")
  - `relative_age(dt)` â€„1¤7 returns a human-readable age string for any datetime

- [x] **6. `pocketknife.corporate_lorem`**
  - `buzzwords(n)` â€„1¤7 generates n corporate buzzword sentences
  - `pirate(n)` â€„1¤7 generates pirate-themed filler text

- [x] **7. `pocketknife.flatpack`**
  - `flatten(d, sep=".")` â€„1¤7 collapses nested dicts into dot-notation keys
  - `unflatten(d, sep=".")` â€„1¤7 rebuilds a nested dict from dot-notation keys

- [x] **8. `pocketknife.resilience`**
  - `@stubborn(retries=3, delay=1)` â€„1¤7 decorator that retries a failing function
  - `fallback(fn, default)` â€„1¤7 calls fn, returns default if it raises any exception

- [x] **9. `pocketknife.sandbox`**
  - `temp_workspace()` â€„1¤7 context manager creating a temp dir, cleaned up on exit

- [x] **10. `pocketknife.inspector`**
  - `snoop(var)` â€„1¤7 rich print of type, value, length, and memory size
  - `stopwatch()` â€„1¤7 context manager that prints exact execution time on exit

---

## ðŸš€ PHASE 2: THE EXPANSION (Modules 11â€„1¤730)

### ðŸŽ­ The "Just for Fun" Wing

- [x] **11. `pocketknife.blame`**
  - `git_roulette()` â€„1¤7 on crash, blames a random name from git log

- [x] **12. `pocketknife.nostalgia`**
  - `dial_up_print(text)` â€„1¤7 prints text character by character with modem sounds
  - `matrix_rain()` â€„1¤7 renders a Matrix-style green character rain in the terminal

- [x] **13. `pocketknife.overengineer`**
  - `@enterprise_edition` â€„1¤7 wraps simple functions with verbose Java-style XML logs

- [x] **14. `pocketknife.hype`**
  - `hype_man(iterable)` â€„1¤7 wraps an iterable, shouting motivation every N iterations

- [x] **15. `pocketknife.schrodinger`**
  - `quantum_bool()` â€„1¤7 returns `True` exactly 50% of the time (the real 50/50)

- [x] **16. `pocketknife.fortune`**
  - `zen_crash()` â€„1¤7 exception hook that appends a peaceful proverb to any traceback

- [x] **17. `pocketknife.soundtrack`**
  - `run_with_music(fn, url)` â€„1¤7 prints a music link timed to the function's duration

- [x] **18. `pocketknife.conspiracy`**
  - `generate_theory(vars)` â€„1¤7 links your variable names to the Illuminati via GPT-style text

- [x] **19. `pocketknife.pet`**
  - `feed_the_bird()` â€„1¤7 terminal Tamagotchi; mood degrades if not run daily

- [x] **20. `pocketknife.snark`**
  - `judge_type(x)` â€„1¤7 passive-aggressive alternative to `type()` with commentary

### ðŸ› ï¸„1¤7 The "Pure Utility" Wing

- [x] **21. `pocketknife.env_police`**
  - `require_env(*keys)` â€„1¤7 raises clear error early if env vars are missing

- [x] **22. `pocketknife.diet_pandas`**
  - `groupby_key(records, key)` â€„1¤7 groups list of dicts by a field, no Pandas needed

- [x] **23. `pocketknife.chunker`**
  - `paginate(iterable, size)` â€„1¤7 safely splits any iterable into chunks of `size`

- [x] **24. `pocketknife.lazy_logger`**
  - `@log_to_file(path)` â€„1¤7 decorator logging function inputs/outputs to a file

- [x] **25. `pocketknife.dict_diff`**
  - `compare(a, b)` â€„1¤7 returns added, removed, and modified keys between two dicts

- [x] **26. `pocketknife.file_scout`**
  - `find_first(pattern, root=".")` â€„1¤7 finds first file matching a regex in a dir tree

- [x] **27. `pocketknife.safe_math`**
  - `divide(a, b, default=None)` â€„1¤7 safe division with a fallback on zero/type errors

- [x] **28. `pocketknife.clean_strings`**
  - `normalize_text(s)` â€„1¤7 strips weird Unicode, normalizes whitespace for DB input

- [x] **29. `pocketknife.secret_keeper`**
  - `mask_secrets(d, keys)` â€„1¤7 recursively hides sensitive values in nested dicts/logs

- [x] **30. `pocketknife.gossip`**
  - `tell_me_about(obj)` â€„1¤7 upgraded `dir()` printing markdown tables of methods + docs

---

## ðŸ›ï¸„1¤7 PHASE 3: THE MICRO-ARCHITECTURES (Modules 31â€„1¤750)

### ðŸŽ­ The "Just for Fun" Wing

- [ ] **31. `pocketknife.rubber_duck`**
  - `summon_duck()` â€„1¤7 ELIZA-style debug chatbot that asks Socratic questions

- [ ] **32. `pocketknife.xp_tracker`**
  - `@award_xp(points)` â€„1¤7 saves XP to hidden file on test pass; prints level-ups

- [ ] **33. `pocketknife.chaos_monkey`**
  - `unleash_monkey(rate=0.05)` â€„1¤7 randomly fails 5% of local HTTP requests

- [ ] **34. `pocketknife.bouncing_dvd`**
  - `standby_screen(text)` â€„1¤7 bounces text around the terminal on script completion

- [ ] **35. `pocketknife.narrator`**
  - `@narrate` â€„1¤7 uses OS TTS to read function start/finish/crash states aloud

### ðŸ› ï¸„1¤7 The "Pure Utility" Wing

- [ ] **36. `pocketknife.memoize_disk`**
  - `@cache_to(path)` â€„1¤7 caches slow function results to a JSON file on disk

- [ ] **37. `pocketknife.fast_map`**
  - `multithread(fn, items)` â€„1¤7 one-line concurrent.futures wrapper for I/O tasks

- [ ] **38. `pocketknife.easy_env`**
  - `generate_env_template(filepath)` â€„1¤7 reads Python file, extracts all `os.environ` keys to `.env.template`

- [ ] **39. `pocketknife.fake_server`**
  - `WebhookReceiver()` â€„1¤7 context manager spinning up a local HTTP server to catch POSTs

- [ ] **40. `pocketknife.auto_cli`**
  - `turn_into_cli(fn)` â€„1¤7 parses type hints to auto-generate an `argparse` CLI

- [ ] **41. `pocketknife.shape_check`**
  - `validate(data, schema)` â€„1¤7 pure-Python dict validator (lightweight Pydantic alternative)

- [ ] **42. `pocketknife.watchdog`**
  - `on_file_change(path, callback)` â€„1¤7 background loop triggering callback on file save

- [ ] **43. `pocketknife.tiny_orm`**
  - `dict_to_sqlite(d, db_path)` â€„1¤7 auto-creates SQLite DB and schema from a dict

- [ ] **44. `pocketknife.stealth_get`**
  - `fetch_page(url)` â€„1¤7 scraping wrapper with User-Agent rotation and human-like delays

- [ ] **45. `pocketknife.stream_csv`**
  - `read_huge_csv(path)` â€„1¤7 generator yielding rows from multi-GB CSVs without RAM bloat

- [ ] **46. `pocketknife.git_snapshot`**
  - `zip_working_state(output)` â€„1¤7 respects `.gitignore` to create a clean ZIP backup

- [ ] **47. `pocketknife.regex_presets`**
  - `extract.emails(text)` â€„1¤7 extracts all emails from a string
  - `extract.urls(text)` â€„1¤7 extracts all URLs from a string

- [ ] **48. `pocketknife.file_hash`**
  - `hash_directory(path)` â€„1¤7 recursive SHA-256 master hash of an entire directory

- [ ] **49. `pocketknife.token_bucket`**
  - `@rate_limit(calls, period)` â€„1¤7 pure-Python rate limiter decorator

- [ ] **50. `pocketknife.memory_leak`**
  - `memory_watch()` â€„1¤7 context manager warning of RAM growth inside a block

---

## ðŸ“¦ Project Infrastructure

- [ ] `setup.py` / `pyproject.toml` â€„1¤7 pip-installable package config
- [ ] `pocketknife/__init__.py` â€„1¤7 package init with version
- [ ] `tests/` directory with base test structure
- [ ] `LICENSE` (MIT)
- [ ] `README.md` â€„1¤7 complete with examples and contributor credits
- [ ] PyPI publish (after Phase 1 complete)

---

*Last updated: Phase 1 not yet started. Begin with Module 1: `pocketknife.text_flair`.*
