"""JSON Report Generator."""

from __future__ import annotations

import json
from typing import Any, Dict
from veritas_evalengine.engine.report_types import EvalReport


class JSONReportGenerator:
    @staticmethod
    def generate(report: EvalReport) -> str:
        return json.dumps(report.to_dict(), indent=2)
