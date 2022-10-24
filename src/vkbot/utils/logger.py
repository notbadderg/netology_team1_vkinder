def logger(log_filename='running.log'):
    import datetime
    import os

    def get_log_path():
        log_path = os.path.join(os.getcwd(), log_filename)
        return log_path

    def write_log_line(line):
        with open(get_log_path(), "a") as f:
            f.write(f'{line}\n')
        return None

    def decorator(func):
        def wrapper(*args, **kwargs):
            f_start_date = datetime.datetime.now()
            f_name = func.__name__
            f_return = func(*args, **kwargs)
            log_line = f'{f_start_date} - Func: {f_name} - Args: {args} {kwargs} - Return: {f_return}'
            print(log_line)
            print()
            # write_log_line(log_line)
            return f_return
        return wrapper
    return decorator
