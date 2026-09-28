---
max_turns: 20
allowed_tools: [Read, Glob, Grep, Skill, Write, Bash]
tags: [physical-flow, data-heavy]
---

I traced our warehouse picker's three kinds of trips with a tape measure. Coordinates are in metres, listed in walking order with every turn recorded:

trip,x,y
T1,0,0
T1,0,6.5
T1,4.2,6.5
T1,4.2,11
T1,9.8,11
T1,9.8,2.3
T1,0,2.3
T1,0,0
T2,0,0
T2,3.1,0
T2,3.1,8.4
T2,12.6,8.4
T2,12.6,14.9
T2,5,14.9
T2,0,0
T3,0,0
T3,0,6.5
T3,4.2,6.5
T3,4.2,11
T3,0,11
T3,0,0
On a typical shift she does T1 22 times, T2 9 times and T3 31 times. How far does she walk per shift, and which trip should we tackle first?
