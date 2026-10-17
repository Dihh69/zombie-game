Don't follow `CONTEXT.md`, that was for the base
Use `git` to add/commit locally, and then `gh` to make a PR to https://github.com/blankRiot96/zombie-game

Now the task is to take the provided base and convert it from what it is into a zombie fighting PvE game.

- The zombies are fast/aggressive not slow
- There's an Arc over the player which indicates the timer.
- As the timer goes down to the left side, the player becomes more green/zombie, the right side it becomes more yellow/human.
- Everytime you attack and hit a zombie, you gain 1 unit of time
- Everytime you try to attack and miss, you lose 1 unit of time
- Everytime you get hit by a zombie, you lose 5 units of time
- Everytime you kill a zombie, you gain 3 units of time
- Each wave is 3 zombies. After 5 waves you get a checkpoint
- After 3 checkpoints, there should be a final boss fight

4 of us are using antigravity on each of our laptops to work on this game
Create a `comms/` directory (if not already there) where you will update what changes your users have asked you to make
Check that and work accordingly. Regularly update the comms directory
