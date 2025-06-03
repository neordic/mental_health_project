from prometheus_client import Histogram

age_hist = Histogram(
    'input_feature_age',
    'Distribution of Age input feature',
    buckets=[18, 25, 35, 45, 55, 65, 75, 90]
)

