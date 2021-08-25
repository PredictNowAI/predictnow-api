from firebase_admin import firestore
import threading
import sched, time



class MLTrainingCompletedNotifier:
    counter = 0
    def __init__(self, username, user_logs_name):
        self.username = username

        realtime_db = firestore.client()
        cols = realtime_db.collection(u'training_logs')

        user_ref = cols.document(u'' + self.username)

        self.current_log_doc = user_ref.collection(
            "ml_train_logs").document(u'' + user_logs_name)

        self.result = None

    def wait_for_result(self):
       
        
        doc = self.current_log_doc.get()

        logs = doc.get('logs')
        if not logs:
            self.result= {'total': 6, 'current':0, 'state': 'PROGRESS', 'status': 'In Progress...'}
            return self.result
        else:

            latest = logs[-1]
            if latest['meta'] == "":
                self.result= {'total': 6, 'current':0, 'state': 'PROGRESS', 'status': 'In Progress...'}
                return self.result
            else:
                self.result = latest['meta']
                return self.result
                # print(latest)
                # print(f'{doc.id} => {doc.to_dict()}')'''

        return self.result


