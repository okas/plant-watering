from datetime import datetime
from threading import current_thread, BoundedSemaphore


logger_pool_sema = BoundedSemaphore(value=1)


def common_logger(act_str):
    with logger_pool_sema:
        print("At {0}, in {1}: "\
              .format(datetime.now().isoformat(), current_thread().name)
              , act_str)
