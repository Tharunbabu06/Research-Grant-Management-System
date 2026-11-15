import unittest

from graph.evidence import literature_relevance_issues


AREA = "AI-based cardiovascular monitoring"


class TestLab9LiteratureRelevance(unittest.TestCase):
    def test_relevant_cardiovascular_ai_prediction_paper_passes_topical_screen(self):
        text = (
            "Cardiovascular risk prediction using machine learning for continuous "
            "heart rate monitoring and detection."
        )
        self.assertEqual(literature_relevance_issues(AREA, text), [])

    def test_endourology_idiom_at_the_heart_is_not_cardiovascular_evidence(self):
        text = (
            "Innovation and AI in Endourology. Advancements in technology have "
            "been at the heart of endourology for decades."
        )
        issues = literature_relevance_issues(AREA, text)
        self.assertTrue(any("cardiovascular-domain" in item for item in issues))

    def test_general_ai_healthcare_paper_without_cardiovascular_terms_is_rejected(self):
        text = "Machine learning predicts complications in endourology patients."
        issues = literature_relevance_issues(AREA, text)
        self.assertTrue(any("cardiovascular-domain" in item for item in issues))

    def test_cardiometabolic_medication_review_without_ai_method_is_rejected(self):
        text = (
            "Pharmacist-led medication titration for cardiometabolic disease. "
            "This review discusses medication management across cardiometabolic conditions."
        )
        issues = literature_relevance_issues(AREA, text)
        self.assertTrue(any("cardiovascular-domain" in item for item in issues))
        self.assertTrue(any("AI/ML method" in item for item in issues))

    def test_cardiovascular_paper_without_ai_method_is_rejected(self):
        text = "Premature ventricular contractions: pathophysiology and management."
        issues = literature_relevance_issues(AREA, text)
        self.assertTrue(any("AI/ML method" in item for item in issues))

    def test_ai_cardiac_tissue_paper_without_relevant_task_is_rejected(self):
        text = "Deep learning analysis of cardiac tissue structure and anatomy."
        issues = literature_relevance_issues(AREA, text)
        self.assertTrue(any("task" in item for item in issues))

    def test_myocardial_injury_prediction_is_topically_relevant(self):
        text = (
            "Machine-learning-based prediction of myocardial injury after surgery "
            "using clinical risk factors."
        )
        self.assertEqual(literature_relevance_issues(AREA, text), [])


if __name__ == "__main__":
    unittest.main()
