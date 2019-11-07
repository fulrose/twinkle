def load_config():
    f = open('threshold_config.txt', 'r')
    t = float(f.readline())
    f.close()
    return t


# file write
def save_config(t):
    f = open("threshold_config.txt", "w")

    f.write(str(t))
    f.close()
