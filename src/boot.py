# This file is executed on every boot (including wake-boot from deepsleep)

import gc

gc.collect()

import main

# start main routine here
main.main()
