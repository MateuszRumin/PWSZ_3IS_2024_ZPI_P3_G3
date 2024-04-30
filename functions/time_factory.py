import time

def timer_factory():
    class MyTimer(object):
        total_count = 0

        def __init__(self, msg='', count=True):
            self.msg = msg
            self.count = count

        def __enter__(self):
            self.start = time.time()
            if self.msg:
                print(f'started: {self.msg}')
            return self

        def __exit__(self, typ, value, traceback):
            self.duration = time.time() - self.start
            if self.count:
                MyTimer.total_count += self.duration
            if self.msg:
                print(f'finished: {self.msg}. duration: {MyTimer.convert_to_time_format(self.duration)}')

        @staticmethod
        def print_total_time():
            print('\n ----- \n')
            print(f'total time: {MyTimer.convert_to_time_format(MyTimer.total_count)}')

        @staticmethod
        def convert_to_time_format(sec):
            sec = round(sec, 2)
            if sec < 60:
                return f'{sec} [sec]'

            minutes = int(sec / 60)
            remaining_seconds = sec - (minutes * 60)
            remaining_seconds = round(remaining_seconds, 2)
            return f'{minutes}:{remaining_seconds} [min:sec]'

    return MyTimer