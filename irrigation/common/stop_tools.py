from time import sleep


def stoppable_sleep(time, predicate):
    step = 0.1
    if time < step:
        return predicate()
    count_to_time = 0
    while (count_to_time + step) < time:
        #print("looping...; predicate(): %s"%predicate())
        if predicate():
            return True
        sleep(step)
        count_to_time += step
    else:
        #print("looping...; predicate(): %s"%predicate())
        if predicate():
            return True
        sleep(time - count_to_time)
    return False
