"""
Checks that E2E scenario allows to get desired metrics values
"""
import unittest
from pathlib import Path
from typing import Callable, Type

import pytest

from admin_utils.reference_scores import ReferenceScores
from config.lab_settings import LabSettings
from core_utils.llm.metrics import Metrics
from lab_7_llm.main import TaskEvaluator
from lab_7_llm.start import main


def run_metrics_check(
    lab_path: Path,
    pipeline_main: Callable,
    reference_file_name: str = "reference_scores.json",
    task_evaluator: Type[TaskEvaluator] = TaskEvaluator,
) -> None:
    """
    Evaluate metrics from a lab.

    Args:
         lab_path (Path): path to lab
         pipeline_main (Callable): main from this lab
         reference_file_name (str): name of the file with references
         task_evaluator (Type[TaskEvaluator]): task for evaluation
    """

    pipeline_main()

    settings = LabSettings(lab_path / "settings.json")

    predictions_path = lab_path / "dist" / "predictions.csv"
    task_evaluator = task_evaluator(data_path=predictions_path, metrics=settings.parameters.metrics)
    result = task_evaluator.run()

    references = ReferenceScores(reference_file_name)

    res = {}
    for metric in settings.parameters.metrics:
        student_result = result.get(str(metric))
        reference_result = references.get(
            settings.parameters.model, settings.parameters.dataset, str(metric)
        )
        if metric is Metrics.ROUGE:
            res[metric] = round(student_result, 2) >= round(reference_result, 2)
        else:
            res[metric] = round(student_result, 5) >= round(reference_result, 5)
    for metric, result in res.items():
        assert bool(result) is True, f"Metric {metric} has worse result than reference."


class MetricCheckTest(unittest.TestCase):
    """
    Tests e2e scenario
    """

    @pytest.mark.lab_7_llm
    @pytest.mark.mark8
    @pytest.mark.mark10
    def test_e2e_ideal(self) -> None:
        """
        Ideal metrics check scenario
        """
        self.assertIsNone(run_metrics_check(Path(__file__).parent.parent, main))
