# Ladybug board game simulator

Board game simulator for an overly-popular board game with my 5-year old daughter.

Having grown tired of playing this simple game (_alot_!), I thought it would be fun if I could turn the tables and *ask her* if we could play..... one million times!  >:-)

This project was also an excuse for getting familiar with Python's threading support.  Anyone familiar with Python's multithreading capabilities and limitations know where this is going (google "python threading vs. multiprocessing" for a primer).

My first threading implementation used the `threading` package.  I was shocked when 8 threads on an 8-core CPU ran significantly slower than my single-threaded pilot.  One reason for this is that all python Thread objects are sharing memory, all competing for the same GIL locks.  But what really caught my eye was the fact that all of the cores were seeinglow, sustained utilization, regardless of thread count.  Additional tests confirmed each Python thread's execution was being spread across all of the cores, the context switching adding a lot of overhead, even after factoring out GIL contention.  I found this as surprising as it was unexpected.  I was expecting was each thread to live out its existence on a single CPU core, and to be honest, remain a bit surprised that this is not the case.  Contrast with the single-threaded version which executed exclusively on a single core.  Either something funny is going on in the threaded package, or I don't understand exactly how it works.  I'm pretty sure reality is closer to a Venn diagram with a healthy overlapping component.

Once I switched to the multiprocessessing module, I could see each thread (now separate OS processes) running on a single CPU core with 100% utilization, and performance shot up to levels I was originally expecting.  This approach also happened to simplify the code close to where it was before I started adding the multithreading capability.

## Lesson One: Avoid the `threading` package for CPU-bound activities


## Results
### 10k games, 4 players
###  Timings from an Intel I7 8-core CPU, 8GB RAM

### Summary of results
We are most interested in the 'real' time field, which represents wall-clock time.

Threading model | Results | Notes
----------------|---------|--------
No threading | real    0m7.802s<br>user    0m7.788s<br>sys     0m0.008s | real: actual wall clock time<br/>user: CPU time, in user-mode<br>sys: CPU time, in kernel-mode
`thread` package, one thread | real    0m8.244s<br>user    0m8.224s<br>sys     0m0.016s | a bit elevated...
`multiprocessing` package, one ~~thread~~ process | real    0m7.894s<br>user    0m7.864s<br>sys     0m0.020s | close to the vanilla single thread model
`thread` package, 8 threads | real    0m14.711s<br>user    0m14.836s<br>sys     0m0.204s | close to double the time of the one-thread/process runs!!
`multiprocessing` package, 8 processes | real    0m1.986s<br>user    0m14.720s<br>sys     0m0.020s | Much faster than the one-thread runs, but the cost of spawning 8 processes and collecting results is noticeable.

### Detailed run results

#### No threading:
```
robb@agrippa:~/dev/ladybug$ time ./ladybug.py -p 4 -n 10000 
Number of players: 4
Number of games: 10000
Number of threads: 0
(Single-threaded)
===== Results:  {'Olivia Orange': 2561, 'Ella Yellow': 2644, 'Rickey Red': 2433, 'Tommy Teal': 2362}

real    0m7.802s
user    0m7.788s
sys     0m0.008s
```
#### `thread` package, one thread:
```
robb@agrippa:~/dev/ladybug$ time ./ladybug_threaded.py -p 4 -n 10000 -t 1
Number of players: 4
Number of games: 10000
Number of threads: 1
Thread-0 START for 10000 games
Exiting Thread-0
Threads done.  Collecting results.....
{'Mella Yellow': 2601,
 'Olivia Orange': 2572,
 'Rickey Red': 2462,
 'Tommy Teal': 2365}

real    0m8.244s
user    0m8.224s
sys     0m0.016s
```
#### `thread` package, 8 threads:
```
robb@agrippa:~/dev/ladybug$ time ./ladybug_threaded.py -p 4 -n 10000 -t 8
Number of players: 4
Number of games: 10000
Number of threads: 8
Thread-0 START for 1250 games
Thread-1 START for 1250 games
Thread-2 START for 1250 games
Thread-3 START for 1250 games
Thread-4 START for 1250 games
Thread-5 START for 1250 games
Thread-6 START for 1250 games
Thread-7 START for 1250 games
Exiting Thread-6
Exiting Thread-2
Exiting Thread-5
Exiting Thread-4
Exiting Thread-0
Exiting Thread-3
Exiting Thread-7
Exiting Thread-1
Threads done.  Collecting results.....
{'Mella Yellow': 2596,
 'Olivia Orange': 2568,
 'Rickey Red': 2459,
 'Tommy Teal': 2377}

real    0m14.711s
user    0m14.836s
sys     0m0.204s
```
#### `multiprocessing` package, one ~~thread~~ process:
```
robb@agrippa:~/dev/ladybug$ time ./ladybug.py -p 4 -n 10000 -t 1
Number of players: 4
Number of games: 10000
Number of threads: 1
Thread-0 START for 10000 games
Exiting Thread-0
Threads done.  Collecting results.....
===== Results:  {'Ella Yellow': 2665, 'Olivia Orange': 2554, 'Rickey Red': 2455, 'Tommy Teal': 2326}

real    0m7.894s
user    0m7.864s
sys     0m0.020s
```
#### `multiprocessing` package, 8 processes:
```
robb@agrippa:~/dev/ladybug$ time ./ladybug.py -p 4 -n 10000 -t 8
Number of players: 4
Number of games: 10000
Number of threads: 8
Thread-0 START for 1250 games
Thread-1 START for 1250 games
Thread-2 START for 1250 games
Thread-3 START for 1250 games
Thread-4 START for 1250 games
Thread-6 START for 1250 games
Thread-7 START for 1250 games
Thread-5 START for 1250 games
Exiting Thread-7
Exiting Thread-2
Exiting Thread-4
Exiting Thread-0
Exiting Thread-6
Exiting Thread-3
Exiting Thread-1
Exiting Thread-5
Threads done.  Collecting results.....
===== Results:  {'Ella Yellow': 2726, 'Olivia Orange': 2509, 'Rickey Red': 2456, 'Tommy Teal': 2309}

real    0m1.986s
user    0m14.720s
sys     0m0.020s
```

## Lesson Two: Player One has the best odds of winning, with odds dropping for each subsequent player.  Now you know how to play smarter than a 5-year old... but only if they let you go first!
