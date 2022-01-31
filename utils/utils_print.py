class bcolors:
    TITLE = "\033[95m"
    OKBLUE = "\033[94m"
    OKGREEN = "\033[92m"
    INFO = "\033[93m"
    OKRED = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    BGRED = "\033[41m"
    UNDERLINE = "\033[4m"
    FGWHITE = "\033[37m"
    FAIL = "\033[95m"


def my_print(text, message_type):
    if message_type == "INFO":
        print(bcolors.INFO + text + bcolors.ENDC)
        return
    if message_type == "PLAIN_OUTPUT_WS":
        print(bcolors.INFO + text + bcolors.ENDC)
        return
    if message_type == "INFOB":
        print(bcolors.INFO + bcolors.BOLD + text + bcolors.ENDC)
        return
    if message_type == "ERROR":
        print(bcolors.BGRED + bcolors.FGWHITE + bcolors.BOLD + text + bcolors.ENDC)
        return
    if message_type == "MESSAGE":
        print(bcolors.TITLE + bcolors.BOLD + text + bcolors.ENDC + "\n")
        return
    if message_type == "INSECURE_WS":
        print(bcolors.OKRED + bcolors.BOLD + text + bcolors.ENDC)
        return
    if message_type == "INSECURE":
        print(bcolors.OKRED + bcolors.BOLD + text + bcolors.ENDC + "\n")
        return
    if message_type == "OUTPUT":
        print(bcolors.OKBLUE + bcolors.BOLD + text + bcolors.ENDC + "\n")
        return
    if message_type == "OUTPUT_WS":
        print(bcolors.OKBLUE + bcolors.BOLD + text + bcolors.ENDC)
        return
    if message_type == "SECURE":
        print(bcolors.OKGREEN + bcolors.BOLD + text + bcolors.ENDC)


def print_list(lst, message_type="INSECURE_WS"):
    counter = 0
    for item in lst:
        counter = counter + 1
        entry = str(counter) + ". " + item
        my_print("\t" + entry, message_type)
