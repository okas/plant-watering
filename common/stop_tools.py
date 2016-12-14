from time import sleep


def stoppable_sleep(time, predicate):
    if time == 0: return False
    elif time < 1:
        if predicate(): return True
        sleep(time)
        return False
    count_to_time = 0
    step = 0.2
    while (count_to_time + step) < time:
        #print("looping...; predicate(): %s"%predicate())
        if predicate(): return True
        sleep(step)
        count_to_time += step
    else:
        #print("looping...; predicate(): %s"%predicate())
        if predicate(): return True
        sleep(time - count_to_time)
    return False
