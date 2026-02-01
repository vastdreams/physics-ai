# utilities/
"""
Data imputation and clustering for partial data handling.

Inspired by DREAM architecture Section 4.3.3.6.6.

First Principle Analysis:
- Imputation: δ_i | X ~ N(Xβ, σ²_ε) where X = correlated features
- Clustering: Assign to cluster C, use cluster's δ-factors
- Fallback: Set δ = 0 if no data available
- Mathematical foundation: Bayesian inference, clustering algorithms
- Architecture: Modular imputation with multiple strategies
"""

from typing import Any, Dict, List, Optional, Tuple
import numpy as np
from dataclasses import dataclass
from enum import Enum
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from loggers.system_logger import SystemLogger
from utilities.cot_logging import ChainOfThoughtLogger, LogLevel


class ImputationStrategy(Enum):
    """Imputation strategies."""
    ZERO = "zero"  # Set to zero
    MEAN = "mean"  # Use mean value
    CLUSTER = "cluster"  # Use cluster-based imputation
    BAYESIAN = "bayesian"  # Bayesian imputation
    CORRELATION = "correlation"  # Use correlated features


@dataclass
class DataCluster:
    """Represents a data cluster."""
    cluster_id: str
    center: Dict[str, float]
    delta_factors: Dict[str, float]
    variance: Dict[str, float]
    size: int = 0
    metadata: Dict[str, Any] = None


class DataImputation:
    """
    Data imputation and clustering system.
    
    Handles missing or partial data using various strategies.
    """
    
    def __init__(self):
        """Initialize data imputation system."""
        self.logger = SystemLogger()
        self.clusters: Dict[str, DataCluster] = {}
        self.correlation_matrix: Optional[np.ndarray] = None
        self.feature_names: List[str] = []
        
        self.logger.log("DataImputation initialized", level="INFO")
    
    def impute_missing(self,
                      missing_feature: str,
                      available_features: Dict[str, float],
                      strategy: ImputationStrategy = ImputationStrategy.CORRELATION) -> Tuple[float, float]:
        """
        Impute missing feature value.
        
        Args:
            missing_feature: Name of missing feature
            available_features: Dictionary of available features
            strategy: Imputation strategy
            
        Returns:
            Tuple of (imputed_value, uncertainty)
        """
        cot = ChainOfThoughtLogger()
        step_id = cot.start_step(
            action="IMPUTE_MISSING",
            input_data={'missing': missing_feature, 'strategy': strategy.value},
            level=LogLevel.INFO
        )
        
        try:
            if strategy == ImputationStrategy.ZERO:
                value, uncertainty = 0.0, 1.0
            
            elif strategy == ImputationStrategy.MEAN:
                # Use mean from clusters
                values = []
                for cluster in self.clusters.values():
                    if missing_feature in cluster.delta_factors:
                        values.append(cluster.delta_factors[missing_feature])
                
                if values:
                    value = np.mean(values)
                    uncertainty = np.std(values)
                else:
                    value, uncertainty = 0.0, 1.0
            
            elif strategy == ImputationStrategy.CLUSTER:
                # Find best matching cluster
                best_cluster = self._find_best_cluster(available_features)
                if best_cluster and missing_feature in best_cluster.delta_factors:
                    value = best_cluster.delta_factors[missing_feature]
                    uncertainty = best_cluster.variance.get(missing_feature, 0.5)
                else:
                    value, uncertainty = 0.0, 1.0
            
            elif strategy == ImputationStrategy.CORRELATION:
                # Use correlation with available features
                value, uncertainty = self._correlation_imputation(missing_feature, available_features)
            
            else:
                value, uncertainty = 0.0, 1.0
            
            cot.end_step(
                step_id,
                output_data={'value': value, 'uncertainty': uncertainty},
                validation_passed=True
            )
            
            self.logger.log(
                f"Imputed {missing_feature}: {value:.4f} ± {uncertainty:.4f} (strategy={strategy.value})",
                level="INFO"
            )
            
            return value, uncertainty
        
        except Exception as e:
            cot.end_step(step_id, output_data={'error': str(e)}, validation_passed=False)
            self.logger.log(f"Error in imputation: {str(e)}", level="ERROR")
            return 0.0, 1.0
    
    def _find_best_cluster(self, features: Dict[str, float]) -> Optional[DataCluster]:
        """Find best matching cluster for given features."""
        if not self.clusters:
            return None
        
        best_cluster = None
        best_distance = float('inf')
        
        for cluster in self.clusters.values():
            # Compute distance to cluster center
            distance = 0.0
            common_features = set(features.keys()) & set(cluster.center.keys())
            
            if not common_features:
                continue
            
            for feature in common_features:
                diff = features[feature] - cluster.center[feature]
                distance += diff**2
            
            distance = np.sqrt(distance)
            
            if distance < best_distance:
                best_distance = distance
                best_cluster = cluster
        
        return best_cluster
    
    def _correlation_imputation(self,
                               missing_feature: str,
                               available_features: Dict[str, float]) -> Tuple[float, float]:
        """
        Impute using correlation with available features.
        
        Mathematical: δ_i | X ~ N(Xβ, σ²_ε)
        """
        if not self.correlation_matrix or missing_feature not in self.feature_names:
            return 0.0, 1.0
        
        # Simplified correlation-based imputation
        # In practice, would use learned correlation matrix
        missing_idx = self.feature_names.index(missing_feature)
        
        # Find most correlated available feature
        max_correlation = 0.0
        best_feature = None
        
        for feature_name, value in available_features.items():
            if feature_name in self.feature_names:
                feature_idx = self.feature_names.index(feature_name)
                correlation = abs(self.correlation_matrix[missing_idx, feature_idx])
                
                if correlation > max_correlation:
                    max_correlation = correlation
                    best_feature = feature_name
        
        if best_feature:
            # Use correlated feature value (scaled)
            imputed_value = available_features[best_feature] * max_correlation
            uncertainty = 1.0 - max_correlation  # Higher correlation = lower uncertainty
            return imputed_value, uncertainty
        
        return 0.0, 1.0
    
    def add_cluster(self, cluster: DataCluster) -> None:
        """Add a data cluster."""
        self.clusters[cluster.cluster_id] = cluster
        self.logger.log(f"Cluster added: {cluster.cluster_id} (size={cluster.size})", level="INFO")
    
    def set_correlation_matrix(self, matrix: np.ndarray, feature_names: List[str]) -> None:
        """Set correlation matrix for features."""
        if matrix.shape[0] != len(feature_names) or matrix.shape[1] != len(feature_names):
            raise ValueError("Correlation matrix dimensions must match feature names")
        
        self.correlation_matrix = matrix
        self.feature_names = feature_names
        self.logger.log(f"Correlation matrix set: {len(feature_names)} features", level="INFO")
    
    def create_cluster_from_data(self,
                                cluster_id: str,
                                data_points: List[Dict[str, float]]) -> DataCluster:
        """
        Create cluster from data points.
        
        Args:
            cluster_id: Cluster identifier
            data_points: List of data point dictionaries
            
        Returns:
            Created cluster
        """
        if not data_points:
            raise ValueError("Cannot create cluster from empty data")
        
        # Compute center (mean)
        all_keys = set()
        for point in data_points:
            all_keys.update(point.keys())
        
        center = {}
        delta_factors = {}
        variance = {}
        
        for key in all_keys:
            values = [point.get(key, 0.0) for point in data_points if key in point]
            if values:
                center[key] = np.mean(values)
                delta_factors[key] = np.mean(values)
                variance[key] = np.std(values) if len(values) > 1 else 0.5
        
        cluster = DataCluster(
            cluster_id=cluster_id,
            center=center,
            delta_factors=delta_factors,
            variance=variance,
            size=len(data_points)
        )
        
        self.add_cluster(cluster)
        return cluster

