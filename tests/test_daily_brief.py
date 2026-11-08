"""Daily briefing behaviour: four pillars, short context, idempotence."""
import json
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

from src.daily_brief import build_daily_brief, save_daily_brief


class DailyBriefTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "config").mkdir()
        (self.root / "data").mkdir()
        config = {
            "pillars": [
                {"id": n, "title": n, "audience": "audience", "problems": ["problem"],
                 "keywords": ["keyword"], "cta": n.upper(), "styles": ["demo"]}
                for n in ("exam_automation", "web_development", "ai_agents", "social_media_ai")
            ]
        }
        (self.root / "config" / "content_strategy.json").write_text(json.dumps(config), encoding="utf-8")
        (self.root / "data" / "reels_history.json").write_text("[]", encoding="utf-8")

    def tearDown(self):
        self.temp.cleanup()

    def test_has_one_pillar_and_no_publication(self):
        brief = build_daily_brief(self.root, "2026-11-09")
        self.assertIn(brief["service_id"], {"exam_automation", "web_development", "ai_agents", "social_media_ai"})
        self.assertEqual(brief["state"], "BRIEF_READY_NOT_GENERATED")
        self.assertTrue(brief["no_automatic_publication"])
        self.assertEqual(len(brief["recent_history"]), 0)

    def test_prefers_least_used_pillar(self):
        today = date(2026, 11, 9)
        history = [
            {"tarih": (today - timedelta(days=1)).isoformat(), "service_id": p, "konu": "test"}
            for p in ("web_development", "ai_agents", "social_media_ai")
        ]
        (self.root / "data" / "reels_history.json").write_text(json.dumps(history), encoding="utf-8")
        brief = build_daily_brief(self.root, today)
        self.assertEqual(brief["service_id"], "exam_automation")

    def test_same_day_does_not_regenerate_brief(self):
        first = save_daily_brief(self.root, "2026-11-09")
        second = save_daily_brief(self.root, "2026-11-09")
        self.assertEqual(first, second)
        self.assertEqual(len(list((self.root / "runtime" / "briefs").glob("*.json"))), 1)

    def test_invalid_history_fails_closed(self):
        (self.root / "data" / "reels_history.json").write_text('{"oops":true}', encoding="utf-8")
        with self.assertRaises(ValueError):
            build_daily_brief(self.root, "2026-11-09")


if __name__ == "__main__":
    unittest.main()
