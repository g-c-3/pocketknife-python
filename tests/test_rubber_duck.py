"""Unit tests for pocketknife.rubber_duck"""

import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pocketknife.rubber_duck import Duck, summon_duck, _reflect  # noqa: E402


class TestReflect(unittest.TestCase):
    def test_first_to_second_person(self):
        self.assertEqual(_reflect("my function"), "your function")

    def test_second_to_first_person(self):
        self.assertEqual(_reflect("your code"), "my code")

    def test_unmapped_words_pass_through(self):
        self.assertEqual(_reflect("the database"), "the database")

    def test_case_insensitive_matching(self):
        self.assertEqual(_reflect("My Code"), "your Code")

    def test_empty_string(self):
        self.assertEqual(_reflect(""), "")


class TestDuckRespond(unittest.TestCase):
    def setUp(self):
        self.duck = Duck(rng=random.Random(42))

    def test_empty_input_prompts_for_speech(self):
        result = self.duck.respond("")
        self.assertIn("silence", result.lower())

    def test_whitespace_only_input(self):
        result = self.duck.respond("    ")
        self.assertIn("silence", result.lower())

    def test_why_question_pattern(self):
        result = self.duck.respond("why is my loop infinite?")
        self.assertTrue(result.startswith("🦆"))
        self.assertIn("your loop", result)

    def test_i_cant_pattern(self):
        result = self.duck.respond("I can't get this test to pass")
        self.assertTrue(result.startswith("🦆"))
        self.assertIn("get this test to pass", result)

    def test_broken_pattern(self):
        result = self.duck.respond("my server is crashing")
        self.assertTrue(result.startswith("🦆"))

    def test_generic_question_fallback(self):
        result = self.duck.respond("the sky is a nice color today")
        self.assertTrue(result.startswith("🦆"))

    def test_generic_prompts_dont_immediately_repeat(self):
        duck = Duck(rng=random.Random(1))
        seen = []
        for _ in range(8):
            r = duck.respond("blah blah nonsense unrelated to any pattern")
            seen.append(r)
        # Within one full cycle (8 generic prompts) we shouldn't see
        # the exact same response twice in a row.
        for a, b in zip(seen, seen[1:]):
            self.assertNotEqual(a, b)

    def test_response_always_has_duck_prefix(self):
        inputs = [
            "why does this fail?",
            "I think the bug is in the parser",
            "it doesn't work",
            "expected 5 but got None",
            "this variable is null",
            "works on my machine",
            "is this even possible?",
            "random unmatched sentence here",
        ]
        for text in inputs:
            with self.subTest(text=text):
                result = self.duck.respond(text)
                self.assertTrue(result.startswith("🦆"))

    def test_reflection_applied_in_response(self):
        result = self.duck.respond("I can't fix my parser")
        # "my parser" should reflect to "your parser" somewhere in output
        self.assertIn("your parser", result)


class TestDuckGreetFarewell(unittest.TestCase):
    def test_greet_returns_string_with_duck_emoji(self):
        duck = Duck(rng=random.Random(0))
        self.assertIn("🦆", duck.greet())

    def test_farewell_returns_string_with_duck_emoji(self):
        duck = Duck(rng=random.Random(0))
        self.assertIn("🦆", duck.farewell())

    def test_seeded_duck_is_deterministic(self):
        duck1 = Duck(rng=random.Random(123))
        duck2 = Duck(rng=random.Random(123))
        self.assertEqual(duck1.greet(), duck2.greet())


class TestSummonDuckLoop(unittest.TestCase):
    def test_quit_word_ends_session(self):
        inputs = iter(["quit"])
        outputs = []
        summon_duck(
            input_fn=lambda _: next(inputs),
            print_fn=outputs.append,
            seed=7,
        )
        # greeting + farewell only
        self.assertEqual(len(outputs), 2)
        self.assertIn("🦆", outputs[0])
        self.assertIn("🦆", outputs[1])

    def test_quit_words_case_insensitive(self):
        inputs = iter(["BYE"])
        outputs = []
        summon_duck(
            input_fn=lambda _: next(inputs),
            print_fn=outputs.append,
            seed=1,
        )
        self.assertEqual(len(outputs), 2)

    def test_conversation_then_quit(self):
        inputs = iter(["why does my code fail?", "I think it's a typo", "exit"])
        outputs = []
        summon_duck(
            input_fn=lambda _: next(inputs),
            print_fn=outputs.append,
            seed=99,
        )
        # greeting + 2 responses + farewell
        self.assertEqual(len(outputs), 4)

    def test_eof_ends_session_gracefully(self):
        def raise_eof(_):
            raise EOFError

        outputs = []
        summon_duck(input_fn=raise_eof, print_fn=outputs.append, seed=5)
        self.assertEqual(len(outputs), 2)
        self.assertIn("🦆", outputs[1])


if __name__ == "__main__":
    unittest.main()
