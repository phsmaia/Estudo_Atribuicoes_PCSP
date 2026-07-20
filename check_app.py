import traceback

try:
    import app
    with open("check_success.txt", "w") as f:
        f.write("Success")
except Exception as e:
    with open("error_log.txt", "w") as f:
        f.write(traceback.format_exc())
