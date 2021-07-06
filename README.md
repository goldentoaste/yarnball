# yarnball
A python program for organizing ideas, planning, brain storming etc.  
All requirements and the program itself are packaged with pyinstaller and can be downloaded ./dist or the Releases section. 

![demo](./demo.png)

## Controls
- Middle click or left click and drag background to move camera/move background.
- Double left click background to make new post.
- Double left click to edit existing posts.
- Single left click to select post or connection.
- Left click and drag to move post.
- Right click and drag to another post to make connection.
- Double left click a connection for prompt to edit label and color for a connection. (empty label text hides the label)
- Ctrl + W or del to remove select connection or post.
- Ctrl + Z to undo deleting a post.
- Ctrl + N to make new file in a new window.
- Ctrl + O to open a file.
- Space bar to open a menu with file controls(save, save as, open, new file).

Save files follows the following format for each post: ``` id|#hexColor|title|content|x|y|sizeX|sizeY  ``` and 
connections should have this format: ```id1|id2|#hexcolor|labelText```
the save file for the image above looks something like this: 
```
0|#37A0D2|Demo post|whats the largest integer?\n\nmultiline text!...\n\n\n\nand scrollable........|-498|-240|300|300
1|#41ff61|No largest integer exist.|proof is trivial and is left for reader as excercise.\n|187|-184|320|177
2|#55ff00|This one:|I mean...\n232135698374124905123124819571242194812488912 is pretty big, and I can't think of a bigger one.|-639|281|210|327
3|#aa00ff|probably?|dont really care.|-165|80|184|127
4|#aa00ff|Some other one.|??\n|169|211|298|145
5|#aa00ff|||512|204|143|142
6|#aa00ff|||310|472|242|159
0|1|#37A0D2|No such integer exist
0|2|#ff5500|Yes
0|3|#37A0D2|
5|6|#55aaff|
6|4|#ff0000|
4|5|#55aa00|
```
The id may be any integer, but must be unique. The connection list should have unique ids that exists. badly formatted save file results exceptions thrown at the moment :v

Also, you can set the program as the default way to open .yarnball files, to open save files more conviniently. 
## Requirements:
PyQt5 for ui, pyinstaller for packaging. 
  
