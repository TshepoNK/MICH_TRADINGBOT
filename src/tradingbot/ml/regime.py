from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans


class RegimeFilter:
    """Simple market regime classifier using rolling signal features and K-means."""

    def __init__(self, n_clusters: int = 3, random_state: int = 42):
        self.n_clusters = n_clusters
        self.random_state = random_state
        self.model: KMeans | None = None
        self.labels_: pd.Index | None = None

    def _features(self, series: pd.Series) -> pd.DataFrame:
        values = pd.Series(series, copy=True).astype(float)
        returns = values.pct_change().fillna(0.0)
        volatility = returns.rolling(10, min_periods=1).std().fillna(0.0)
        trend = values.diff(5).fillna(0.0)
        z_score = (values - values.mean()) / (values.std(ddof=0) or 1.0)
        features = pd.DataFrame(
            {
                "returns": returns,
                "volatility": volatility,
                "trend": trend,
                "z_score": z_score,
            }
        )
        return features

    def classify(self, series: pd.Series) -> list[str]:
        features = self._features(series)
        self.model = KMeans(n_clusters=min(self.n_clusters, len(features)), random_state=self.random_state)
        clusters = self.model.fit_predict(features)

        cluster_stats = []
        for idx in range(self.model.n_clusters):
            mask = clusters == idx
            avg_return = features.loc[mask, "returns"].mean()
            avg_vol = features.loc[mask, "volatility"].mean()
            cluster_stats.append((idx, avg_return, avg_vol))

        regime_map = {}
        for cluster_idx, avg_return, avg_vol in cluster_stats:
            if avg_vol > features["volatility"].mean() * 1.2:
                regime = "Volatile"
            elif avg_return > 0:
                regime = "Trending"
            else:
                regime = "Ranging"
            regime_map[cluster_idx] = regime

        return [regime_map[int(cluster)] for cluster in clusters]
