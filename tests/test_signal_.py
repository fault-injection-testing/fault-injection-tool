from src.signal_ import Signal


def test_signal_value():
    assert Signal.SIGHUP.value == "HUP"
    assert Signal.SIGINT.value == "INT"
    assert Signal.SIGQUIT.value == "QUIT"
    assert Signal.SIGILL.value == "ILL"
    assert Signal.SIGTRAP.value == "TRAP"
    assert Signal.SIGABRT.value == "ABRT"
    assert Signal.SIGFPE.value == "FPE"
    assert Signal.SIGKILL.value == "KILL"
    assert Signal.SIGSEGV.value == "SEGV"
    assert Signal.SIGPIPE.value == "PIPE"
    assert Signal.SIGALRM.value == "ALRM"
    assert Signal.SIGTERM.value == "TERM"
    assert Signal.SIGUSR1.value == "USR1"
    assert Signal.SIGUSR2.value == "USR2"
