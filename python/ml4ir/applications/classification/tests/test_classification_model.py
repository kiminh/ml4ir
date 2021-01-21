import pytest
import numpy as np
from ml4ir.applications.classification.tests.test_base import ClassificationTestBase


class ClassificationModelTest(ClassificationTestBase):
    """
    Test end-to-end model training for classification from model retrieved with
    :func:`~ml4ir.applications.classification.pipeline.ClassificationPipeline.get_relevance_model`
    """

    def test_csv_loss_metrics(self):
        """Test the loss from CSV data"""
        # Check if the loss, accuracy and top 5 accuracy on the test set is the same
        # Note that we don't check Precision which is not useful for this test model
        # Note that these numbers are different if you run it directly vs with docker-compose up
        expected_loss = 1.6
        tol = 0.2
        self.assertTrue(np.isclose(self.metrics_dict["loss"], expected_loss, rtol=tol),
                        msg=f"Loss not in expected range."
                            f" Expected: {expected_loss} ± {tol}, Found: {self.metrics_dict['loss']}")

        expected_acc = 0.203
        tol = 0.01
        self.assertTrue(np.isclose(self.metrics_dict["categorical_accuracy"], expected_acc, rtol=tol),
                        msg=f"Categorical_accuracy not in expected range."
                            f" Expected: {expected_acc} ± {tol}, Found: {self.metrics_dict['categorical_accuracy']}")

        expected_acc = 1.0
        tol = 0.01
        _metric = "top_5_categorical_accuracy"
        self.assertTrue(np.isclose(self.metrics_dict[_metric], expected_acc, rtol=tol),
                        msg=f"Top5 Categorical_accuracy not in expected range."
                            f" Expected: {expected_acc} ± {tol}, Found: {self.metrics_dict[_metric]}")

    def test_group_metrics_df(self):
        """
        Test the dimensions of the grouped metrics
        """
        # Metrics cardinality and names
        metrics = self.classification_pipeline.metrics_keys  # Metrics during training
        df = self.grouped_metrics
        self.assertTrue(df.metric.nunique() == len(metrics))  # number of metrics
        self.assertTrue(set(df.metric.unique()) == set(metrics))  # metrics per se
        # Grouped keys cardinality and names
        group_keys = self.classification_pipeline.feature_config.get_group_metrics_keys()
        group_names = [key['name'] for key in group_keys]
        unique_group_names = set(df.group_name.unique())
        self.assertTrue(unique_group_names == set(group_names))  # group_names
        # non trainable features that are group keys
        group_names_nt = [key['name'] for key in group_keys if not key['trainable']]
        for gk in group_names_nt:
            self.assertTrue(gk in unique_group_names)  # Assert they appear in the dataframe
            unique_metrics_gk = set(df.loc[df.group_name == gk].metric.unique())
            self.assertTrue(unique_metrics_gk == set(metrics))  # Assert each metric appears for them
