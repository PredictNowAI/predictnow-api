class TrainingResult:
    def __init__(self,
                 success,
                 feat_test,
                 feat_train,
                 feature_importance,
                 lab_test,
                 lab_train,
                 performance_metrics,
                 dataframe_train_diff,
                 dataframe_train_undiff,
                 training_parameters,
                 predicted_prob_cv,
                 predicted_prob_test,
                 predicted_targets_cv,
                 predicted_targets_test,
                 ):
        self.success = success
        self.feature_importance = feature_importance
        self.feat_train = feat_train
        self.feat_test = feat_test
        self.lab_test = lab_test
        self.lab_train = lab_train
        self.performance_metrics = performance_metrics
        self.dataframe_train_diff = dataframe_train_diff
        self.dataframe_train_undiff = dataframe_train_undiff
        self.training_parameters = training_parameters
        self.predicted_prob_cv = predicted_prob_cv
        self.predicted_prob_test = predicted_prob_test
        self.predicted_targets_cv = predicted_targets_cv
        self.predicted_targets_test = predicted_targets_test

class Result:
    def __init__(self,
                 success,
                 performance_metrics,
                 predicted_prob_cv,
                 predicted_prob_test,
                 predicted_targets_cv,
                 predicted_targets_test,
                 eda_describe,
                 feature_importance,
                 lab_test,
                 ):
        self.success = success
        self.feature_importance = feature_importance
        self.lab_test = lab_test
        self.performance_metrics= performance_metrics
        self.predicted_prob_cv = predicted_prob_cv
        self.predicted_prob_test = predicted_prob_test
        self.predicted_targets_cv = predicted_targets_cv
        self.predicted_targets_test = predicted_targets_test
        self.eda_describe = eda_describe