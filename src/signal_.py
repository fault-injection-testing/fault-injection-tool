from enum import Enum


class Signal(Enum):
    SIGHUP = "HUP"
    SIGINT = "INT"
    SIGQUIT = "QUIT"
    SIGILL = "ILL"
    SIGTRAP = "TRAP"
    SIGABRT = "ABRT"
    SIGFPE = "FPE"
    SIGKILL = "KILL"
    SIGSEGV = "SEGV"
    SIGPIPE = "PIPE"
    SIGALRM = "ALRM"
    SIGTERM = "TERM"
    SIGUSR1 = "USR1"
    SIGUSR2 = "USR2"
