"""
Data imputation and clustering for partial data handling.

Inspired by DREAM architecture Section 4.3.3.6.6.

First Principle Analysis:
- Imputation: delta_i | X ~ N(X*beta, sigma^2_eps) where X = correlated features
- Clustering: Assign to cluster C, use cluster's delta-factors
- Fallback: Set delta = 0 if no data available
- Mathematical foundation: Bayesian inference, clustering algorithms
- Architecture: Modular imputation with multiple strategies
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from loggers.system_logger import SystemLogger
from utilities.cot_logging import ChainOfThoughtLogger, LogLevel

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
_DEFAULT_UNCERTAINTY = 1.0
_DEFAULT_CLUSTER_VARIANCE = 0.5


class ImputationStrategy(Enum):
    """Imputation strategies."""

    ZERO = "zero"
    MEAN = "mean"
    CLUSTER = "cluster"
    BAYESIAN = "bayesian"
    CORRELATION = "correlation"


@dataclass
class DataCluster:
    """Represents a data cluster."""

    cluster_id: str
    center: Dict[str, float]
    delta_factors: Dict[str, float]
    variance: Dict[str, float]
    size: int = 0
    metadata: Optional[Dict[str, Any]] = None


class DataImputation:
    """Data imputation and clustering system.

    Handles missing or partial data using various strategies.
    """

    def __init__(self) -> None:
        """Initialize data imputation system."""
        self._logger = SystemLogger()
        self.clusters: Dict[str, DataCluster] = {}
        self.correlation_matrix: Optional[np.ndarray] = None
        self.feature_names: List[str] = []

        self._logger.log("DataImputation initialized", level="INFO")

    def impute_missing(
        self,
        missing_feature: str,
        available_features: Dict[str, float],
        strategy: ImputationStrategy = ImputationStrategy.CORRELATION,
    ) -> Tuple[float, float]:
        """Impute missing feature value.

        Args:
            missing_feature: Name of missing feature.
            available_features: Dictionary of available features.
            strategy: Imputation strategy.

        Returns:
            Tuple of (imputed_value, uncertainty).
        """
        cot = ChainOfThoughtLogger()
        step_id = cot.start_step(
            action="IMPUTE_MISSING",
            input_data={"missing": missing_feature, "strategy": strategy.value},
            level=LogLevel.INFO,
        )

        try:
            value, uncertainty = self._dispatch_strategy(
                missing_feature, available_features, strategy
            )

            cot.end_step(
                step_id,
                output_data={"value": value, "uncertainty": uncertainty},
                validation_passed=True,
            )

            self._logger.log(
                f"Imputed {missing_feature}: {value:.4f} +/- {uncertainty:.4f} "
                f"(strategy={strategy.value})",
                level="INFO",
            )
            return value, uncertainty

        except Exception as e:
            cot.end_step(step_id, output_data={"error": str(e)}, validation_passed=False)
            self._logger.log(f"Error in imputation: {e}", level="ERROR")
            return 0.0, _DEFAULT_UNCERTAINTY

    def _dispatch_strategy(
        self,
        missing_feature: str,
        available_features: Dict[str, float],
        strategy: ImputationStrategy,
    ) -> Tuple[float, float]:
        """Dispatch to the appropriate imputation strategy."""
        if strategy == ImputationStrategy.ZERO:
            return 0.0, _DEFAULT_UNCERTAINTY

        if strategy == ImputationStrategy.MEAN:
            return self._mean_imputation(missing_feature)

        if strategy == ImputationStrategy.CLUSTER:
            return self._cluster_imputation(missing_feature, available_features)

        if strategy == ImputationStrategy.CORRELATION:
            return self._correlation_imputation(missing_feature, available_features)

        return 0.0, _DEFAULT_UNCERTAINTY

    def _mean_imputation(self, missing_feature: str) -> Tuple[float, float]:
        """Impute using mean value across clusters."""
        values = [
            cluster.delta_factors[missing_feature]
            for cluster in self.clusters.values()
            if missing_feature in cluster.delta_factors
        ]

        if values:
            return float(np.mean(values)), float(np.std(values))
        return 0.0, _DEFAULT_UNCERTAINTY

    def _cluster_imputation(
        self, missing_feature: str, available_features: Dict[str, float]
    ) -> Tuple[float, float]:
        """Impute using the nearest cluster."""
        best_cluster = self._find_best_cluster(available_features)
        if best_cluster and missing_feature in best_cluster.delta_factors:
            return (
                best_cluster.delta_factors[missing_feature],
                best_cluster.variance.get(missing_feature, _DEFAULT_CLUSTER_VARIANCE),
            )
        return 0.0, _DEFAULT_UNCERTAINTY

    def _find_best_cluster(self, features: Dict[str, float]) -> Optional[DataCluster]:
        """Find best matching cluster for given features."""
        if not self.clusters:
            return None

        best_cluster: Optional[DataCluster] = None
        best_distance = float("inf")

        for cluster in self.clusters.values():
            common_features = set(features.keys()) & set(cluster.center.keys())
            if not common_features:
                continue

            distance = np.sqrt(
                sum((features[f] - cluster.center[f]) ** 2 for f in common_features)
            )

            if distance < best_distance:
                best_distance = distance
                best_cluster = cluster

        return best_cluster

    def _correlation_imputation(
        self,
        missing_feature: str,
        available_features: Dict[str, float],
    ) -> Tuple[float, float]:
        """Impute using correlation with available features.

        Mathematical: delta_i | X ~ N(X*beta, sigma^2_eps)
        """
        if self.correlation_matrix is None or missing_feature not in self.feature_names:
            return 0.0, _DEFAULT_UNCERTAINTY

        missing_idx = self.feature_names.index(missing_feature)

        max_correlation = 0.0
        best_feature: Optional[str] = None

        for feature_name, value in available_features.items():
            if feature_name in self.feature_names:
                feature_idx = self.feature_names.index(feature_name)
                correlation = abs(self.correlation_matrix[missing_idx, feature_idx])

                if correlation > max_correlation:
                    max_correlation = correlation
                    best_feature = feature_name

        if best_feature:
            imputed_value = available_features[best_feature] * max_correlation
            uncertainty = 1.0 - max_correlation
            return imputed_value, uncertainty

        return 0.0, _DEFAULT_UNCERTAINTY

    def add_cluster(self, cluster: DataCluster) -> None:
        """Add a data cluster."""
        self.clusters[cluster.cluster_id] = cluster
        self._logger.log(
            f"Cluster added: {cluster.cluster_id} (size={cluster.size})", level="INFO"
        )

    def set_correlation_matrix(self, matrix: np.ndarray, feature_names: List[str]) -> None:
        """Set correlation matrix for features.

        Args:
            matrix: Square correlation matrix.
            feature_names: Feature names matching matrix dimensions.

        Raises:
            ValueError: If matrix dimensions do not match feature names.
        """
        if matrix.shape[0] != len(feature_names) or matrix.shape[1] != len(feature_names):
            raise ValueError("Correlation matrix dimensions must match feature names")

        self.correlation_matrix = matrix
        self.feature_names = feature_names
        self._logger.log(
            f"Correlation matrix set: {len(feature_names)} features", level="INFO"
        )

    def create_cluster_from_data(
        self,
        cluster_id: str,
        data_points: List[Dict[str, float]],
    ) -> DataCluster:
        """Create cluster from data points.

        Args:
            cluster_id: Cluster identifier.
            data_points: List of data point dictionaries.

        Returns:
            Created cluster.

        Raises:
            ValueError: If data_points is empty.
        """
        if not data_points:
            raise ValueError("Cannot create cluster from empty data")

        all_keys: set[str] = set()
        for point in data_points:
            all_keys.update(point.keys())

        center: Dict[str, float] = {}
        delta_factors: Dict[str, float] = {}
        variance: Dict[str, float] = {}

        for key in all_keys:
            values = [point[key] for point in data_points if key in point]
            if values:
                center[key] = float(np.mean(values))
                delta_factors[key] = float(np.mean(values))
                variance[key] = float(np.std(values)) if len(values) > 1 else _DEFAULT_CLUSTER_VARIANCE

        cluster = DataCluster(
            cluster_id=cluster_id,
            center=center,
            delta_factors=delta_factors,
            variance=variance,
            size=len(data_points),
        )

        self.add_cluster(cluster)
        return cluster
