class PredictResult:
    def __init__(self,
                 title,
                 filename,
                 objective,
                 eda,
                 too_many_nulls_list,
                 suffix,
                 labels,
                 probabilities,
                 prob_calib
                 ):
        self.title = title
        self.filename = filename
        self.objective = objective
        self.eda = eda
        self.too_many_nulls_list = too_many_nulls_list
        self.suffix = suffix
        self.labels = labels
        self.probabilities = probabilities
        self.prob_calib = prob_calib