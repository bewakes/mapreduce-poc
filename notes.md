## Hadoop installation and configuration
- Install hadoop from AUR: `yay -S hadoop`
- Edit `/etc/profile.d/hadoop.sh` and set the username
- Enable ssh in localhost without password.
    - start sshd: `sudo systemctl start sshd`.
    - Add public key to `authorized_keys`: `echo ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys`.
    - Now ssh should work without password.
- `HADOOP_HOME` was not set so set it to `/usr/lib/hadoop/` in `bashrc`.
- Also add `$HADOOP_HOME/sbin` to `$PATH` in `.bashrc`. This will make `start-all.sh` and `stop-all.sh` available.
- Set `HADOOP_TOOLS_DIR` to `HADOOP_TOOLS_DIR="$HADOOP_HOME/share/hadoop/tools/lib"`. This will be handy later on.
- Start all: `start-all.sh`.
- Start namenode: `hadoop namenode`.
- Now you can access hadoop portal from: `http://localhost:9870`.
- Any hadoop command assumes the directory to be `http://localhost:9000/user/<username>` by default.
- Create your user directory: `hadoop dfs -mkdir /user` and `hadoop dfs -mkdir /user/bibek`.
- Copy to hdfs: `hadoop dfs -copyFromLocal <your data directory> <hdfs directory, which need not already be present>`
- Create Custom mapper and reducer programs. In python, I've taken from [here](https://www.michael-noll.com/tutorials/writing-an-hadoop-mapreduce-program-in-python/) as example.
- Run the map reducer `hadoop jar $HADOOP_TOOLS_DIR/hadoop-streaming*.jar -file ./mapper.py -mapper ./mapper.py -file ./reducer.py -reducer ./reducer.py -input /user/bibek/cc_test/* -output /user/bibek/cc_test-output`
- The output can be viewed from portal.
